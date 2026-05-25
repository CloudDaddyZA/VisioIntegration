"""Azure SKU and pricing tools."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from visio_mcp._state import mcp, _diagram, _layout, _waf, _caf
from visio_mcp.azure_sku_grounding import (
    query_retail_prices,
    compare_sku_pricing,
    get_vm_family_recommendation,
    get_sku_reference_data,
    get_pricing_service_name,
    VM_FAMILIES,
    DB_TIERS,
    APP_SERVICE_TIERS,
    AKS_GUIDANCE,
    GROUNDING_REFERENCES,
    SERVICE_NAMES_FOR_PRICING,
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════
# TOOL: import_pricing_estimate
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
async def import_pricing_estimate(
    estimate_url: str = "",
    services: list[str] | None = None,
    diagram_name: str = "Architecture from Pricing Estimate",
    auto_connect: bool = True,
    monthly_cost: float = 0.0,
    annual_cost: float = 0.0,
) -> dict[str, Any]:
    """Import an Azure Pricing Calculator estimate and generate a starter architecture diagram.

    Provide EITHER estimate_url (auto-fetches services via headless browser) OR a
    services list. Creates a diagram with resources grouped by category (Compute,
    Networking, Data, etc.) with logical connections between them.

    Args:
        estimate_url: Shared estimate URL from the Azure Pricing Calculator.
                      Formats: https://azure.com/e/<id>, or the 32-char estimate ID.
                      The tool will fetch the page and extract services automatically.
        services: Optional explicit list of Azure service names (overrides URL fetch).
                  Include duplicates for multiple instances (e.g. ["Load Balancer",
                  "Load Balancer", "Azure Front Door"]).
        diagram_name: Name for the created diagram.
        auto_connect: Add logical connections between resources (default: True).
        monthly_cost: Optional total monthly cost (used if services list provided).
        annual_cost: Optional total annual cost (used if services list provided).

    Returns:
        Summary of the imported estimate including services found, diagram created,
        and estimated costs.
    """
    from .pricing_import import (
        parse_services_from_list,
        fetch_estimate_from_url,
        generate_diagram_plan,
        PRICING_SERVICE_MAP,
    )

    # Determine source: explicit service list or URL fetch
    if services:
        result = parse_services_from_list(
            services,
            monthly_cost=monthly_cost,
            annual_cost=annual_cost,
            url=estimate_url,
        )
    elif estimate_url:
        result = await fetch_estimate_from_url(estimate_url)
    else:
        return {
            "status": "error",
            "message": "Provide either estimate_url or services list.",
        }

    if result.error and not result.services:
        return {
            "status": "error",
            "message": result.error,
            "url": result.url,
            "hint": (
                "Provide the shared estimate URL (https://azure.com/e/<id>) or an "
                "explicit services list. "
                f"Supported services: {len(PRICING_SERVICE_MAP)} mapped names."
            ),
        }

    # Generate diagram plan
    plan = generate_diagram_plan(result.services)

    # Create the diagram
    state = _diagram.new_diagram(diagram_name)

    # Add boundaries (category groups)
    boundary_results = []
    for b in plan["boundaries"]:
        boundary = _diagram.add_boundary(
            boundary_type=b["boundary_type"],
            display_name=b["display_name"],
            boundary_id=b["boundary_id"],
            x=b["x"],
            y=b["y"],
            width=b["width"],
            height=b["height"],
        )
        boundary_results.append({
            "id": boundary.id,
            "name": b["display_name"],
        })

    # Add resources
    resource_results = []
    for r in plan["resources"]:
        try:
            resource = _diagram.add_resource(
                resource_type=r["resource_type"],
                display_name=r["display_name"],
                resource_id=r["resource_id"],
                x=r["x"],
                y=r["y"],
                group_id=r.get("group_id"),
            )
            resource_results.append({
                "id": resource.id,
                "type": r["resource_type"],
                "name": r["display_name"],
            })
        except Exception as e:
            logger.warning(f"Failed to add resource {r['display_name']}: {e}")

    # Add connections
    connection_results = []
    if auto_connect:
        for c in plan["connections"]:
            try:
                conn = _diagram.add_connection(
                    source_id=c["from_id"],
                    target_id=c["to_id"],
                    label=c.get("label", ""),
                )
                connection_results.append({
                    "from": c["from_id"],
                    "to": c["to_id"],
                    "label": c.get("label", ""),
                })
            except Exception as e:
                logger.debug(f"Connection skipped: {e}")

    return {
        "status": "created",
        "diagram_name": diagram_name,
        "estimate_url": result.url,
        "services_found": len(result.services),
        "services": [
            {"name": s.name, "type": s.resource_type}
            for s in result.services
        ],
        "diagram": {
            "boundaries": len(boundary_results),
            "resources": len(resource_results),
            "connections": len(connection_results),
        },
        "cost_estimate": {
            "monthly": f"${result.monthly_total:,.2f}" if result.monthly_total else None,
            "annual": f"${result.annual_total:,.2f}" if result.annual_total else None,
        },
        "warnings": result.error if result.error else None,
        "message": (
            f"Created diagram '{diagram_name}' with {len(resource_results)} resources "
            f"in {len(boundary_results)} groups, {len(connection_results)} auto-connections. "
            f"ASK the user about: (1) subscription/resource group layout, "
            f"(2) VNet/subnet topology, (3) data flow direction, "
            f"(4) environment (prod/dev), (5) naming convention. "
            f"Use answers to restructure boundaries before layout. "
            f"If user provides a dataflow image, use that instead."
        ),
    }


# ═══════════════════════════════════════════════════════════════════
# TOOL: query_azure_pricing
# ═══════════════════════════════════════════════════════════════════


@mcp.tool()
async def query_azure_pricing(
    service_name: str,
    region: str = "eastus",
    sku_name: str = "",
    price_type: str = "Consumption",
    currency: str = "USD",
    max_results: int = 10,
) -> dict[str, Any]:
    """Query live Azure Retail Prices API for SKU pricing data.

    Use this tool to get real pricing data when making SKU recommendations.
    No authentication required — queries the public Azure Retail Prices endpoint.

    Args:
        service_name: Azure service name exactly as the API expects it
            (e.g., "Virtual Machines", "Azure App Service", "SQL Database",
            "Azure Cosmos DB", "Azure Kubernetes Service", "Storage",
            "Azure Cache for Redis", "Azure Firewall", "Application Gateway").
            Use get_sku_recommendations to discover the correct service name.
        region: Azure region (e.g., "eastus", "westeurope", "southeastasia")
        sku_name: Optional specific SKU (e.g., "Standard_D4s_v5")
        price_type: "Consumption" (pay-as-you-go), "Reservation", or "SavingsPlan"
        currency: Currency code (default "USD")
        max_results: Maximum results to return (default 10)

    Returns:
        Dict with pricing results including SKU names, hourly/unit prices, and regions.
    """
    results = await query_retail_prices(
        service_name=service_name,
        region=region if region else None,
        sku_name=sku_name if sku_name else None,
        price_type=price_type if price_type else None,
        currency=currency,
        max_results=max_results,
    )
    return {
        "status": "success",
        "service": service_name,
        "region": region,
        "price_type": price_type,
        "currency": currency,
        "results_count": len(results),
        "prices": results,
        "note": "Prices are retail (list) prices. Monthly estimate = hourly × 730 hours.",
        "source": "Azure Retail Prices API (https://prices.azure.com)",
    }


# ═══════════════════════════════════════════════════════════════════
# TOOL: compare_azure_skus
# ═══════════════════════════════════════════════════════════════════


@mcp.tool()
async def compare_azure_skus(
    service_name: str,
    sku_names: list[str],
    region: str = "eastus",
    currency: str = "USD",
) -> dict[str, Any]:
    """Compare pricing for multiple SKUs of the same Azure service.

    Returns a sorted comparison (cheapest first) with monthly estimates.
    Useful for right-sizing decisions and presenting cost trade-offs.

    Args:
        service_name: Azure service name (e.g., "Virtual Machines", "Azure App Service")
        sku_names: List of SKU names to compare (e.g., ["Standard_B2s", "Standard_D2s_v5", "Standard_D4s_v5"])
        region: Azure region for pricing (default "eastus")
        currency: Currency code (default "USD")

    Returns:
        Sorted comparison with hourly and monthly pricing for each SKU.
    """
    results = await compare_sku_pricing(
        service_name=service_name,
        sku_names=sku_names,
        region=region,
        currency=currency,
    )
    return {
        "status": "success",
        "service": service_name,
        "region": region,
        "comparison": results,
        "note": "Sorted cheapest-first. Monthly = hourly × 730 hours.",
        "source": "Azure Retail Prices API",
    }


# ═══════════════════════════════════════════════════════════════════
# TOOL: get_sku_recommendations
# ═══════════════════════════════════════════════════════════════════


@mcp.tool()
async def get_sku_recommendations(
    resource_type: str,
    workload_type: str = "general",
    environment: str = "production",
) -> dict[str, Any]:
    """Get SKU/tier recommendations for an Azure resource type.

    Provides curated guidance based on Azure Well-Architected Framework,
    Architecture Center patterns, and best practices. Includes VM family
    selection, database tier guidance, App Service plan selection, and
    AKS node pool sizing.

    Args:
        resource_type: The resource type (e.g., "virtual_machine", "sql_database",
            "app_service", "cosmos_db", "aks", "postgresql")
        workload_type: Workload category — "general", "memory", "compute",
            "storage", "gpu", or "burstable" (mainly for VMs)
        environment: "production", "dev/test", "staging"

    Returns:
        Structured recommendations with tier options, use cases, and pricing service name.
    """
    reference = get_sku_reference_data(resource_type)
    pricing_name = get_pricing_service_name(resource_type)

    result: dict[str, Any] = {
        "status": "success",
        "resource_type": resource_type,
        "environment": environment,
        "reference_data": reference,
        "pricing_service_name": pricing_name,
    }

    # Add VM-specific recommendation
    if resource_type in ("virtual_machine", "vm_scale_set"):
        vm_rec = get_vm_family_recommendation(workload_type, environment)
        result["vm_recommendation"] = vm_rec

    result["grounding_sources"] = {
        "pricing_api": "Use query_azure_pricing with service_name='{}'".format(pricing_name) if pricing_name else None,
        "documentation": [
            ref["url"] for key, ref in GROUNDING_REFERENCES.items()
            if key in ("waf", "advisor", "finops", "vm_sizes", "sql_purchasing", "aks_best_practices")
        ],
    }

    return result


# ═══════════════════════════════════════════════════════════════════
