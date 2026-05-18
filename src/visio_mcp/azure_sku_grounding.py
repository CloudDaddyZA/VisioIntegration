"""Azure SKU grounding module — queries live Azure APIs for pricing and capability data.

Provides:
- Azure Retail Prices API queries (no auth required)
- SKU capability reference data (VM families, DB tiers, etc.)
- Architecture guidance references (WAF, Advisor, FinOps)
- Regional availability lookups

Used by the MCP server to ground AI SKU recommendations in real data.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# ── Azure Retail Prices API (public, no auth) ──────────────────────────────────

RETAIL_PRICES_BASE = "https://prices.azure.com/api/retail/prices"


@dataclass
class PriceResult:
    """Single price entry from Azure Retail Prices API."""

    sku_name: str
    service_name: str
    product_name: str
    meter_name: str
    region: str
    retail_price: float
    unit_of_measure: str
    type: str  # "Consumption", "Reservation", etc.
    currency: str = "USD"
    tier: str = ""
    savings_plan_price: float | None = None
    reservation_term: str = ""


async def query_retail_prices(
    service_name: str,
    region: str | None = None,
    sku_name: str | None = None,
    price_type: str | None = None,
    currency: str = "USD",
    max_results: int = 20,
) -> list[dict[str, Any]]:
    """Query Azure Retail Prices API for live pricing data.

    Args:
        service_name: Azure service (e.g., "Virtual Machines", "Azure App Service")
        region: Azure region (e.g., "eastus", "westeurope"). None = all regions.
        sku_name: Specific SKU filter (e.g., "Standard_D4s_v5")
        price_type: "Consumption", "Reservation", or "SavingsPlan"
        currency: Currency code (default USD)
        max_results: Max results to return

    Returns:
        List of price entries as dicts
    """
    filters = [f"serviceName eq '{service_name}'"]
    if region:
        filters.append(f"armRegionName eq '{region}'")
    if sku_name:
        filters.append(f"armSkuName eq '{sku_name}'")
    if price_type:
        filters.append(f"priceType eq '{price_type}'")

    filter_str = " and ".join(filters)
    params = {
        "$filter": filter_str,
        "currencyCode": currency,
    }

    results: list[dict[str, Any]] = []
    url = RETAIL_PRICES_BASE

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            while url and len(results) < max_results:
                resp = await client.get(url, params=params if url == RETAIL_PRICES_BASE else None)
                resp.raise_for_status()
                data = resp.json()

                for item in data.get("Items", []):
                    if len(results) >= max_results:
                        break
                    results.append({
                        "skuName": item.get("armSkuName", ""),
                        "serviceName": item.get("serviceName", ""),
                        "productName": item.get("productName", ""),
                        "meterName": item.get("meterName", ""),
                        "region": item.get("armRegionName", ""),
                        "retailPrice": item.get("retailPrice", 0),
                        "unitOfMeasure": item.get("unitOfMeasure", ""),
                        "priceType": item.get("type", ""),
                        "currency": item.get("currencyCode", "USD"),
                        "tier": item.get("tier", ""),
                        "savingsPlanPrice": item.get("savingsPlan", [{}])[0].get("retailPrice") if item.get("savingsPlan") else None,
                    })

                url = data.get("NextPageLink")
                params = None  # NextPageLink includes params

    except httpx.HTTPError as e:
        logger.warning("Azure Retail Prices API error: %s", e)
        return [{"error": f"API request failed: {e}"}]

    return results


async def compare_sku_pricing(
    service_name: str,
    sku_names: list[str],
    region: str = "eastus",
    currency: str = "USD",
) -> list[dict[str, Any]]:
    """Compare pricing for multiple SKUs of the same service.

    Returns a sorted list (cheapest first) with monthly estimates.
    """
    results: list[dict[str, Any]] = []

    for sku in sku_names:
        prices = await query_retail_prices(
            service_name=service_name,
            region=region,
            sku_name=sku,
            price_type="Consumption",
            currency=currency,
            max_results=5,
        )
        # Find the compute/base price (filter out OS, disk, etc.)
        base = next(
            (p for p in prices if not p.get("error") and "Spot" not in p.get("meterName", "")),
            None,
        )
        if base:
            hourly = base["retailPrice"]
            results.append({
                "skuName": sku,
                "region": region,
                "hourlyPrice": hourly,
                "monthlyEstimate": round(hourly * 730, 2),  # 730 hrs/month
                "unitOfMeasure": base.get("unitOfMeasure", ""),
                "priceType": "PayAsYouGo",
            })

    results.sort(key=lambda x: x.get("monthlyEstimate", float("inf")))
    return results


# ── VM Family Reference Data ───────────────────────────────────────────────────

VM_FAMILIES: dict[str, dict[str, Any]] = {
    "B-series": {
        "description": "Burstable, economical for dev/test and low-traffic workloads",
        "use_cases": ["dev/test", "small websites", "micro-services", "CI/CD agents"],
        "cpu_memory_ratio": "variable (burst credits)",
        "examples": ["Standard_B1s", "Standard_B2s", "Standard_B4ms"],
        "cost_tier": "low",
    },
    "D-series": {
        "description": "General-purpose, balanced CPU-to-memory for production",
        "use_cases": ["web servers", "app servers", "databases (medium)", "enterprise apps"],
        "cpu_memory_ratio": "1:4",
        "examples": ["Standard_D4s_v5", "Standard_D8s_v5", "Standard_D16s_v5"],
        "cost_tier": "medium",
    },
    "E-series": {
        "description": "Memory-optimized for in-memory databases and analytics",
        "use_cases": ["SAP HANA", "Redis", "SQL Server", "data warehousing", "analytics"],
        "cpu_memory_ratio": "1:8",
        "examples": ["Standard_E4s_v5", "Standard_E16s_v5", "Standard_E32s_v5"],
        "cost_tier": "medium-high",
    },
    "F-series": {
        "description": "Compute-optimized for CPU-intensive workloads",
        "use_cases": ["batch processing", "gaming servers", "ML inference", "scientific"],
        "cpu_memory_ratio": "1:2",
        "examples": ["Standard_F4s_v2", "Standard_F8s_v2", "Standard_F16s_v2"],
        "cost_tier": "medium",
    },
    "L-series": {
        "description": "Storage-optimized for high throughput and IO-intensive workloads",
        "use_cases": ["big data", "NoSQL databases", "data warehousing", "log analytics"],
        "cpu_memory_ratio": "1:8 (high local SSD)",
        "examples": ["Standard_L8s_v3", "Standard_L16s_v3", "Standard_L32s_v3"],
        "cost_tier": "high",
    },
    "N-series": {
        "description": "GPU-accelerated for AI/ML training, rendering, and HPC",
        "use_cases": ["ML training", "deep learning", "video rendering", "simulation"],
        "cpu_memory_ratio": "varies (GPU-focused)",
        "examples": ["Standard_NC6s_v3", "Standard_NC24ads_A100_v4", "Standard_ND96asr_v4"],
        "cost_tier": "very high",
    },
    "M-series": {
        "description": "Ultra memory-optimized for largest in-memory workloads",
        "use_cases": ["SAP HANA (large)", "SQL Server in-memory OLTP"],
        "cpu_memory_ratio": "1:16+",
        "examples": ["Standard_M128s", "Standard_M208s_v2"],
        "cost_tier": "very high",
    },
}


# ── Database Tier Reference Data ───────────────────────────────────────────────

DB_TIERS: dict[str, dict[str, Any]] = {
    "azure_sql": {
        "models": {
            "DTU": {
                "tiers": ["Basic (5 DTU)", "Standard (S0-S12)", "Premium (P1-P15)"],
                "best_for": "Predictable workloads, simpler management",
                "guidance": "Start S1 for small apps, S3+ for production",
            },
            "vCore": {
                "tiers": ["General Purpose", "Business Critical", "Hyperscale"],
                "best_for": "Flexible scaling, familiar SQL Server licensing",
                "guidance": "GP for most workloads; BC for <1ms latency; Hyperscale for >4TB or rapid scale",
            },
        },
    },
    "cosmos_db": {
        "models": {
            "Serverless": {
                "best_for": "Dev/test, infrequent/sporadic traffic",
                "guidance": "Max 1 million RU/s burst, no SLA guarantee",
            },
            "Provisioned": {
                "best_for": "Steady production workloads",
                "guidance": "Start 400 RU/s, autoscale for variable; 4000+ RU/s for multi-partition",
            },
        },
    },
    "postgresql_flexible": {
        "models": {
            "Burstable": {
                "best_for": "Dev/test, low-traffic apps",
                "guidance": "B1ms (1 vCore/2GB), B2s for small prod",
            },
            "General Purpose": {
                "best_for": "Most production workloads",
                "guidance": "D2s_v3+ (2-64 vCores), good balance",
            },
            "Memory Optimized": {
                "best_for": "Large datasets, real-time analytics",
                "guidance": "E2s_v3+ for memory-heavy queries",
            },
        },
    },
}


# ── App Service Tier Reference Data ────────────────────────────────────────────

APP_SERVICE_TIERS: dict[str, dict[str, Any]] = {
    "Free/Shared": {
        "use_cases": ["testing", "PoC"],
        "limits": "No custom domain (Free), no always-on, shared compute",
        "cost": "$0-10/month",
    },
    "Basic (B1-B3)": {
        "use_cases": ["dev/test", "low-traffic sites"],
        "limits": "No auto-scale, no slots, no VNet integration",
        "cost": "$13-52/month",
    },
    "Standard (S1-S3)": {
        "use_cases": ["production sites", "moderate traffic"],
        "limits": "Up to 10 instances, 5 slots, VNet integration",
        "cost": "$73-292/month",
    },
    "Premium v3 (P1v3-P3v3)": {
        "use_cases": ["high-traffic production", "enterprise"],
        "limits": "Up to 30 instances, 20 slots, enhanced networking",
        "cost": "$108-432/month",
    },
    "Isolated v2 (I1v2-I3v2)": {
        "use_cases": ["high security", "compliance", "dedicated network"],
        "limits": "ASE-based, fully isolated, up to 100 instances",
        "cost": "$350+/month",
    },
}


# ── AKS Node Pool Guidance ─────────────────────────────────────────────────────

AKS_GUIDANCE: dict[str, Any] = {
    "system_pool": {
        "recommended_sku": "Standard_D4s_v5",
        "min_nodes": 2,
        "note": "System pool runs CoreDNS, metrics-server; needs reliability not performance",
    },
    "general_workload": {
        "recommended_skus": ["Standard_D4s_v5", "Standard_D8s_v5"],
        "autoscale": "1-10 nodes typical",
        "note": "General purpose for web/API workloads",
    },
    "memory_intensive": {
        "recommended_skus": ["Standard_E4s_v5", "Standard_E8s_v5"],
        "note": "For data processing, caching, Java apps with large heaps",
    },
    "gpu_workloads": {
        "recommended_skus": ["Standard_NC6s_v3", "Standard_NC24ads_A100_v4"],
        "note": "For ML inference/training; use spot for training, on-demand for inference",
    },
    "spot_pools": {
        "use_cases": ["batch processing", "ML training", "CI/CD"],
        "savings": "Up to 90% discount vs on-demand",
        "note": "Can be evicted; use for fault-tolerant workloads only",
    },
}


# ── Grounding Reference URLs ──────────────────────────────────────────────────

GROUNDING_REFERENCES: dict[str, dict[str, str]] = {
    "pricing": {
        "name": "Azure Retail Prices API",
        "url": "https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices",
        "purpose": "Live SKU pricing, reservations, savings plans, unit economics",
    },
    "sku_capabilities": {
        "name": "Azure Compute Resource SKUs API",
        "url": "https://learn.microsoft.com/en-us/rest/api/compute/resource-skus/list",
        "purpose": "VM capabilities (vCPU, memory, accelerated networking, zones)",
    },
    "pricing_calculator": {
        "name": "Azure Pricing Calculator",
        "url": "https://azure.microsoft.com/en-us/pricing/calculator/",
        "purpose": "Multi-service estimation and configuration",
    },
    "waf": {
        "name": "Azure Well-Architected Framework",
        "url": "https://learn.microsoft.com/en-us/azure/well-architected/",
        "purpose": "SKU patterns, HA/DR guidance, performance tradeoffs",
    },
    "architecture_center": {
        "name": "Azure Architecture Center",
        "url": "https://learn.microsoft.com/en-us/azure/architecture/",
        "purpose": "Reference architectures, proven SKU combinations",
    },
    "service_limits": {
        "name": "Azure Subscription and Service Limits",
        "url": "https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits",
        "purpose": "SKU constraints, scaling ceilings, throughput limits",
    },
    "advisor": {
        "name": "Azure Advisor Documentation",
        "url": "https://learn.microsoft.com/en-us/azure/advisor/",
        "purpose": "Optimization heuristics, reserved instance guidance",
    },
    "finops": {
        "name": "Azure FinOps Documentation",
        "url": "https://learn.microsoft.com/en-us/azure/cost-management-billing/finops/",
        "purpose": "Cost governance, reservation guidance, savings plans",
    },
    "vm_sizes": {
        "name": "Azure VM Sizes Documentation",
        "url": "https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/overview",
        "purpose": "VM family explanations, GPU recommendations, workload alignment",
    },
    "sql_purchasing": {
        "name": "Azure SQL Purchasing Models",
        "url": "https://learn.microsoft.com/en-us/azure/azure-sql/database/purchasing-models",
        "purpose": "DTU vs vCore, Hyperscale vs Business Critical logic",
    },
    "aks_best_practices": {
        "name": "AKS Best Practices",
        "url": "https://learn.microsoft.com/en-us/azure/aks/best-practices",
        "purpose": "Node pool sizing, autoscaling, SKU alignment",
    },
    "openai_quotas": {
        "name": "Azure OpenAI Quotas and Limits",
        "url": "https://learn.microsoft.com/en-us/azure/ai-services/openai/quotas-limits",
        "purpose": "TPM/RPM quotas, model availability, regional support",
    },
    "products_by_region": {
        "name": "Azure Products by Region",
        "url": "https://azure.microsoft.com/en-us/explore/global-infrastructure/products-by-region/",
        "purpose": "Regional availability, SKU/service rollout validation",
    },
    "monitor_metrics": {
        "name": "Azure Monitor Metrics Reference",
        "url": "https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/metrics-supported",
        "purpose": "Performance baselines, throughput indicators, scaling signals",
    },
    "rest_api_specs": {
        "name": "Azure REST API Specs",
        "url": "https://github.com/Azure/azure-rest-api-specs",
        "purpose": "Full API schema, Swagger/OpenAPI definitions, automation",
    },
}


# ── Service Name Mapping for Prices API ────────────────────────────────────────

SERVICE_NAMES_FOR_PRICING: dict[str, str] = {
    "virtual_machine": "Virtual Machines",
    "vm_scale_set": "Virtual Machine Scale Sets",
    "app_service": "Azure App Service",
    "app_service_plan": "Azure App Service",
    "function_app": "Functions",
    "container_app": "Azure Container Apps",
    "aks": "Azure Kubernetes Service",
    "sql_database": "SQL Database",
    "sql_managed_instance": "SQL Managed Instance",
    "cosmos_db": "Azure Cosmos DB",
    "postgresql": "Azure Database for PostgreSQL",
    "mysql": "Azure Database for MySQL",
    "redis_cache": "Azure Cache for Redis",
    "storage_account": "Storage",
    "key_vault": "Key Vault",
    "application_gateway": "Application Gateway",
    "load_balancer": "Load Balancer",
    "firewall": "Azure Firewall",
    "front_door": "Azure Front Door Service",
    "cognitive_services": "Cognitive Services",
    "openai": "Azure OpenAI Service",
    "databricks": "Azure Databricks",
    "data_factory": "Azure Data Factory v2",
    "synapse": "Azure Synapse Analytics",
    "event_hub": "Event Hubs",
    "service_bus": "Service Bus",
    "logic_app": "Logic Apps",
    "api_management": "API Management",
    "signalr": "SignalR Service",
    "cdn": "Content Delivery Network",
}


def get_pricing_service_name(resource_type: str) -> str | None:
    """Map a catalog resource_type to the Azure Retail Prices API serviceName."""
    return SERVICE_NAMES_FOR_PRICING.get(resource_type)


def get_vm_family_recommendation(
    workload_type: str,
    environment: str = "production",
) -> dict[str, Any]:
    """Get VM family recommendation based on workload type and environment.

    Args:
        workload_type: One of "general", "memory", "compute", "storage", "gpu", "burstable"
        environment: "dev/test" or "production"

    Returns:
        Dict with recommended family, SKUs, and rationale.
    """
    mapping = {
        "general": "D-series",
        "memory": "E-series",
        "compute": "F-series",
        "storage": "L-series",
        "gpu": "N-series",
        "burstable": "B-series",
        "sap": "M-series",
    }

    # For dev/test, default to burstable regardless
    if environment.lower() in ("dev", "test", "dev/test", "development"):
        family_key = "B-series"
    else:
        family_key = mapping.get(workload_type.lower(), "D-series")

    family = VM_FAMILIES.get(family_key, VM_FAMILIES["D-series"])
    return {
        "family": family_key,
        "description": family["description"],
        "use_cases": family["use_cases"],
        "examples": family["examples"],
        "cost_tier": family["cost_tier"],
        "environment": environment,
    }


def get_sku_reference_data(resource_type: str) -> dict[str, Any]:
    """Get reference data for a given resource type (tiers, guidance, etc.)."""
    if resource_type in ("virtual_machine", "vm_scale_set"):
        return {"vm_families": VM_FAMILIES}
    elif resource_type in ("sql_database", "sql_managed_instance"):
        return {"tiers": DB_TIERS["azure_sql"]}
    elif resource_type == "cosmos_db":
        return {"tiers": DB_TIERS["cosmos_db"]}
    elif resource_type in ("postgresql", "postgresql_flexible"):
        return {"tiers": DB_TIERS["postgresql_flexible"]}
    elif resource_type in ("app_service", "app_service_plan"):
        return {"tiers": APP_SERVICE_TIERS}
    elif resource_type == "aks":
        return {"guidance": AKS_GUIDANCE}
    else:
        return {"note": f"No detailed SKU reference for '{resource_type}'. Use query_azure_pricing tool for live data."}
