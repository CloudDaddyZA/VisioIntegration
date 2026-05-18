"""Import Azure Pricing Calculator estimates and convert to architecture diagrams.

Supports two input modes:
1. Direct service list - the AI agent reads the pricing calculator URL (which is
   a JavaScript SPA) and provides the extracted service names directly.
2. URL reference - stores the estimate URL as metadata on the diagram.

The tool maps Azure Pricing Calculator service names to resource_type keys in the
shape catalog and generates a starter architecture diagram with appropriate
grouping, positioning, and logical connections.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# ── Mapping from Pricing Calculator service names to catalog resource_type keys ──

PRICING_SERVICE_MAP: dict[str, str] = {
    # Compute
    "Virtual Machines": "virtual_machine",
    "Virtual Machine": "virtual_machine",
    "Azure Virtual Machines": "virtual_machine",
    "Virtual Machine Scale Sets": "vm_scale_set",
    "App Service": "app_service",
    "Azure App Service": "app_service",
    "Azure Functions": "azure_functions",
    "Functions": "azure_functions",
    "Container Instances": "container_instances",
    "Azure Container Instances": "container_instances",
    "Azure Kubernetes Service (AKS)": "kubernetes_service",
    "Azure Kubernetes Service": "kubernetes_service",
    "Container Apps": "container_apps",
    "Azure Container Apps": "container_apps",
    "Azure Spring Apps": "spring_apps",
    "Azure Batch": "batch",
    # Networking
    "Load Balancer": "load_balancer",
    "Azure Load Balancer": "load_balancer",
    "Application Gateway": "application_gateway",
    "Azure Application Gateway": "application_gateway",
    "Azure Front Door": "front_door",
    "Front Door": "front_door",
    "Azure Front Door and CDN profiles": "front_door",
    "Azure Firewall": "azure_firewall",
    "Firewall": "azure_firewall",
    "VPN Gateway": "vpn_gateway",
    "Azure VPN Gateway": "vpn_gateway",
    "ExpressRoute": "express_route",
    "Azure ExpressRoute": "express_route",
    "Azure DNS": "dns",
    "DNS": "dns",
    "Traffic Manager": "traffic_manager",
    "Azure Traffic Manager": "traffic_manager",
    "Virtual Network": "virtual_network",
    "Azure Virtual Network": "virtual_network",
    "Azure Bastion": "bastion",
    "Bastion": "bastion",
    "Azure DDoS Protection": "ddos_protection",
    "Content Delivery Network": "cdn",
    "Azure CDN": "cdn",
    "NAT Gateway": "nat_gateway",
    "Private Link": "private_link_service",
    # Storage
    "Storage Accounts": "storage_account",
    "Azure Blob Storage": "blob_storage",
    "Blob Storage": "blob_storage",
    "Managed Disks": "managed_disk",
    "Azure Managed Disks": "managed_disk",
    "Azure NetApp Files": "netapp_files",
    "Azure Data Lake Storage": "data_lake",
    # Databases
    "Azure SQL Database": "sql_database",
    "SQL Database": "sql_database",
    "Azure SQL Managed Instance": "sql_managed_instance",
    "Azure Cosmos DB": "cosmos_db",
    "Cosmos DB": "cosmos_db",
    "Azure Database for PostgreSQL": "postgresql_database",
    "Azure Database for MySQL": "mysql_database",
    "Azure Database for MariaDB": "mariadb_database",
    "Azure Cache for Redis": "redis_cache",
    "Redis Cache": "redis_cache",
    "Azure Synapse Analytics": "synapse",
    "Synapse Analytics": "synapse",
    # Integration / Messaging
    "Event Hubs": "event_hub",
    "Azure Event Hubs": "event_hub",
    "Service Bus": "service_bus",
    "Azure Service Bus": "service_bus",
    "Event Grid": "event_grid",
    "Azure Event Grid": "event_grid",
    "API Management": "api_management",
    "Azure API Management": "api_management",
    "Logic Apps": "logic_apps",
    "Azure Logic Apps": "logic_apps",
    # AI / ML
    "Azure OpenAI Service": "openai_service",
    "Azure AI Search": "ai_search",
    "Cognitive Services": "cognitive_services",
    "Azure Cognitive Services": "cognitive_services",
    "Azure Machine Learning": "machine_learning",
    "Azure Bot Service": "bot_service",
    "Azure AI Services": "cognitive_services",
    # Analytics
    "Azure Databricks": "databricks",
    "Databricks": "databricks",
    "Azure Data Factory": "data_factory",
    "Data Factory": "data_factory",
    "Azure Stream Analytics": "stream_analytics",
    "HDInsight": "hdinsight",
    "Azure Data Explorer": "data_explorer",
    "Power BI Embedded": "power_bi_embedded",
    # Security / Identity
    "Azure Active Directory": "active_directory",
    "Microsoft Entra ID": "active_directory",
    "Key Vault": "key_vault",
    "Azure Key Vault": "key_vault",
    "Azure Sentinel": "sentinel",
    "Microsoft Sentinel": "sentinel",
    # Monitoring / Management
    "Azure Monitor": "monitor",
    "Log Analytics": "log_analytics",
    "Application Insights": "application_insights",
    # IoT
    "Azure IoT Hub": "iot_hub",
    "IoT Hub": "iot_hub",
    "Azure Digital Twins": "digital_twins",
    # DevOps
    "Azure DevOps": "devops",
    # Web
    "Azure SignalR Service": "signalr",
    "SignalR Service": "signalr",
    "Azure Static Web Apps": "static_web_app",
    # Containers
    "Container Registry": "container_registry",
    "Azure Container Registry": "container_registry",
    # Other
    "Foundry Tools": "openai_service",
    "Microsoft Cost Management": "monitor",
    "Bandwidth": "virtual_network",
    "Azure Backup": "backup",
    "Azure Site Recovery": "site_recovery",
}

# Categories for grouping services into boundaries
SERVICE_CATEGORY: dict[str, str] = {
    "virtual_machine": "compute",
    "vm_scale_set": "compute",
    "app_service": "compute",
    "azure_functions": "compute",
    "container_instances": "compute",
    "kubernetes_service": "compute",
    "container_apps": "compute",
    "spring_apps": "compute",
    "batch": "compute",
    "load_balancer": "networking",
    "application_gateway": "networking",
    "front_door": "networking",
    "azure_firewall": "networking",
    "vpn_gateway": "networking",
    "express_route": "networking",
    "dns": "networking",
    "traffic_manager": "networking",
    "virtual_network": "networking",
    "bastion": "networking",
    "ddos_protection": "networking",
    "cdn": "networking",
    "nat_gateway": "networking",
    "private_link_service": "networking",
    "storage_account": "storage",
    "blob_storage": "storage",
    "managed_disk": "storage",
    "netapp_files": "storage",
    "data_lake": "storage",
    "sql_database": "data",
    "sql_managed_instance": "data",
    "cosmos_db": "data",
    "postgresql_database": "data",
    "mysql_database": "data",
    "mariadb_database": "data",
    "redis_cache": "data",
    "synapse": "data",
    "event_hub": "integration",
    "service_bus": "integration",
    "event_grid": "integration",
    "api_management": "integration",
    "logic_apps": "integration",
    "openai_service": "ai",
    "ai_search": "ai",
    "cognitive_services": "ai",
    "machine_learning": "ai",
    "bot_service": "ai",
    "databricks": "analytics",
    "data_factory": "analytics",
    "stream_analytics": "analytics",
    "hdinsight": "analytics",
    "data_explorer": "analytics",
    "power_bi_embedded": "analytics",
    "active_directory": "security",
    "key_vault": "security",
    "sentinel": "security",
    "monitor": "monitoring",
    "log_analytics": "monitoring",
    "application_insights": "monitoring",
    "iot_hub": "iot",
    "digital_twins": "iot",
    "signalr": "web",
    "static_web_app": "web",
    "container_registry": "containers",
    "devops": "devops",
    "backup": "management",
    "site_recovery": "management",
}

CATEGORY_DISPLAY: dict[str, str] = {
    "compute": "Compute",
    "networking": "Networking",
    "storage": "Storage",
    "data": "Data Services",
    "integration": "Integration",
    "ai": "AI & Machine Learning",
    "analytics": "Analytics",
    "security": "Security & Identity",
    "monitoring": "Monitoring",
    "iot": "IoT",
    "web": "Web",
    "containers": "Containers",
    "devops": "DevOps",
    "management": "Management",
}


@dataclass
class EstimateService:
    """A service parsed from an Azure Pricing Calculator estimate."""
    name: str
    resource_type: str
    description: str = ""
    monthly_cost: float = 0.0
    tier: str = ""
    count: int = 1


@dataclass
class EstimateResult:
    """Result of parsing an Azure Pricing Calculator estimate."""
    url: str
    services: list[EstimateService] = field(default_factory=list)
    monthly_total: float = 0.0
    annual_total: float = 0.0
    error: str | None = None


def parse_services_from_list(
    service_names: list[str],
    *,
    monthly_cost: float = 0.0,
    annual_cost: float = 0.0,
    url: str = "",
) -> EstimateResult:
    """Parse a list of service names into an EstimateResult.

    This is the primary entry point. The AI agent extracts service names from the
    pricing calculator page (via its web browsing capability) and passes them here.

    Each entry in service_names should be the display name as shown in the pricing
    calculator (e.g. "Load Balancer", "Azure Front Door", "Azure Cache for Redis").
    Duplicates are counted (e.g. two "Load Balancer" entries become count=2).

    Args:
        service_names: List of service display names from the pricing calculator.
        monthly_cost: Total monthly cost (if known).
        annual_cost: Total annual cost (if known).
        url: The original pricing calculator URL (stored as metadata).

    Returns:
        EstimateResult with parsed services.
    """
    services: list[EstimateService] = []
    type_counts: dict[str, int] = {}
    unrecognized: list[str] = []

    for name in service_names:
        name = name.strip()
        if not name:
            continue

        resource_type = _resolve_service_name(name)
        if not resource_type:
            unrecognized.append(name)
            continue

        type_counts[resource_type] = type_counts.get(resource_type, 0) + 1
        services.append(EstimateService(
            name=name,
            resource_type=resource_type,
            count=type_counts[resource_type],
        ))

    error = None
    if unrecognized:
        error = f"Unrecognized services (not mapped): {', '.join(unrecognized)}"

    return EstimateResult(
        url=url,
        services=services,
        monthly_total=monthly_cost,
        annual_total=annual_cost,
        error=error,
    )


def _resolve_service_name(name: str) -> str | None:
    """Resolve a service display name to a resource_type key.

    Tries exact match first, then case-insensitive, then partial match.
    """
    # Exact match
    if name in PRICING_SERVICE_MAP:
        return PRICING_SERVICE_MAP[name]

    # Case-insensitive match
    name_lower = name.lower()
    for known_name, rtype in PRICING_SERVICE_MAP.items():
        if known_name.lower() == name_lower:
            return rtype

    # Partial match (name contains or is contained in a known name)
    for known_name, rtype in PRICING_SERVICE_MAP.items():
        if known_name.lower() in name_lower or name_lower in known_name.lower():
            return rtype

    return None


async def fetch_estimate_from_url(url: str) -> EstimateResult:
    """Fetch services from an Azure Pricing Calculator shared estimate URL.

    Uses Playwright (headless Chromium) to render the JavaScript SPA and extract
    the services from the rendered page content.

    Args:
        url: Shared estimate URL (e.g. https://azure.com/e/<id>) or estimate ID.

    Returns:
        EstimateResult with extracted services and cost totals.
    """
    import re

    # Normalize URL
    normalized_url = _normalize_estimate_url(url)

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        return EstimateResult(
            url=normalized_url,
            error="Playwright is not installed. Run: pip install playwright && playwright install chromium",
        )

    service_names: list[str] = []
    monthly_total = 0.0
    annual_total = 0.0

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(normalized_url, wait_until="networkidle", timeout=60000)

            # Wait for the estimate section to render
            try:
                await page.wait_for_selector("text=Your Estimate", timeout=15000)
            except Exception:
                pass  # Continue anyway — content may still be available

            # Extract service names from h3 headings within the estimate section
            # The pricing calculator renders services as h3 elements
            headings = await page.query_selector_all("h3")
            skip_headings = {
                "support", "select your program/offer", "estimated upfront cost",
                "estimated monthly cost", "estimated annual cost", "your estimate",
                "products", "find the next step", "start using azure",
                "contact sales", "find an azure partner", "try azure for free",
            }

            for h in headings:
                text = await h.inner_text()
                text = text.strip()
                if text and text.lower() not in skip_headings:
                    # Only include if it maps to a known service
                    if _resolve_service_name(text):
                        service_names.append(text)

            # Extract cost totals from the page
            # The header bar shows costs like "$3,873 / Estimated monthly cost"
            # Individual services show "Monthly: $23.25" and "Annual: $279.00"
            costs = await page.evaluate(
                """() => {
                    const text = document.body.innerText;
                    const dollars = text.match(/\\$[\\d,]+\\.?\\d*/g) || [];
                    let monthly = 0, annual = 0;
                    // Look for "Estimated monthly cost" preceded by a dollar amount in the header
                    const monthlyMatch = text.match(/\\$(\\d[\\d,]*\\.?\\d*)\\s*(?:\\/\\s*)?Estimated monthly cost/);
                    if (monthlyMatch) monthly = parseFloat(monthlyMatch[1].replace(/,/g, ''));
                    // Sum individual monthly costs as a more accurate approach
                    const monthlyLines = text.match(/Monthly:\\s*\\$(\\d[\\d,]*\\.?\\d*)/g) || [];
                    if (monthlyLines.length > 0) {
                        monthly = monthlyLines.reduce((sum, m) => {
                            const v = m.match(/\\$(\\d[\\d,]*\\.?\\d*)/);
                            return sum + (v ? parseFloat(v[1].replace(/,/g, '')) : 0);
                        }, 0);
                    }
                    const annualLines = text.match(/Annual:\\s*\\$(\\d[\\d,]*\\.?\\d*)/g) || [];
                    if (annualLines.length > 0) {
                        annual = annualLines.reduce((sum, m) => {
                            const v = m.match(/\\$(\\d[\\d,]*\\.?\\d*)/);
                            return sum + (v ? parseFloat(v[1].replace(/,/g, '')) : 0);
                        }, 0);
                    }
                    return {monthly, annual};
                }"""
            )
            monthly_total = costs.get("monthly", 0.0)
            annual_total = costs.get("annual", 0.0)

            await browser.close()

    except Exception as e:
        return EstimateResult(
            url=normalized_url,
            error=f"Failed to fetch estimate: {e}",
        )

    if not service_names:
        return EstimateResult(
            url=normalized_url,
            error="No services found in the estimate. The page may not have loaded correctly.",
        )

    # Parse the extracted service names
    return parse_services_from_list(
        service_names,
        monthly_cost=monthly_total,
        annual_cost=annual_total,
        url=normalized_url,
    )


def _normalize_estimate_url(url: str) -> str:
    """Normalize and validate pricing calculator URL."""
    import re as _re

    url = url.strip()

    # Already a full URL
    if url.startswith("https://azure.com/e/") or url.startswith("https://azure.microsoft.com"):
        return url

    # Extract ID from various URL formats
    match = _re.search(r'(?:shared-estimate=|/e/)([a-f0-9]{32})', url)
    if match:
        return f"https://azure.com/e/{match.group(1)}"

    # Just the ID
    if _re.match(r'^[a-f0-9]{32}$', url):
        return f"https://azure.com/e/{url}"

    # Return as-is if it looks like a URL
    if url.startswith("http"):
        return url

    raise ValueError(f"Could not parse estimate URL or ID: {url}")


def generate_diagram_plan(services: list[EstimateService]) -> dict[str, Any]:
    """Generate a diagram layout plan from parsed estimate services.

    Groups services by category and generates positions for a clean layout.

    Returns:
        Dict with boundaries, resources, connections, and layout metadata.
    """
    # Group services by category
    categories: dict[str, list[EstimateService]] = {}
    for svc in services:
        cat = SERVICE_CATEGORY.get(svc.resource_type, "other")
        categories.setdefault(cat, []).append(svc)

    # Layout: arrange categories in a grid
    boundaries: list[dict[str, Any]] = []
    resources: list[dict[str, Any]] = []
    connections: list[dict[str, Any]] = []

    # Position categories in rows
    col_width = 7.0
    row_height = 5.0
    max_cols = 3
    col = 0
    row = 0

    category_order = [
        "networking", "security", "compute", "web", "containers",
        "data", "integration", "ai", "analytics", "storage",
        "monitoring", "iot", "devops", "management",
    ]

    # Only include categories that have services
    active_categories = [c for c in category_order if c in categories]
    # Add any remaining categories not in the predefined order
    for c in categories:
        if c not in active_categories and c != "other":
            active_categories.append(c)

    for cat in active_categories:
        cat_services = categories[cat]
        display_name = CATEGORY_DISPLAY.get(cat, cat.title())

        x = 1.0 + col * col_width
        y = 1.0 + row * row_height

        boundary_id = f"boundary_{cat}"
        boundaries.append({
            "boundary_type": "resource_group",
            "display_name": display_name,
            "boundary_id": boundary_id,
            "x": x,
            "y": y,
            "width": 6.0,
            "height": max(3.5, len(cat_services) * 1.5 + 1.0),
        })

        # Position resources within the boundary
        for i, svc in enumerate(cat_services):
            suffix = f"-{svc.count}" if svc.count > 1 else ""
            resource_id = f"{svc.resource_type}{suffix}"
            res_x = x + 1.5 + (i % 2) * 2.5
            res_y = y + 1.0 + (i // 2) * 1.5

            resources.append({
                "resource_type": svc.resource_type,
                "display_name": svc.name,
                "resource_id": resource_id,
                "x": res_x,
                "y": res_y,
                "group_id": boundary_id,
            })

        col += 1
        if col >= max_cols:
            col = 0
            row += 1

    # Generate logical connections between tiers
    _add_logical_connections(resources, connections)

    return {
        "boundaries": boundaries,
        "resources": resources,
        "connections": connections,
        "layout": {
            "columns": min(len(active_categories), max_cols),
            "rows": row + 1,
            "page_width": min(len(active_categories), max_cols) * col_width + 2,
            "page_height": (row + 1) * row_height + 2,
        },
    }


def _add_logical_connections(
    resources: list[dict[str, Any]],
    connections: list[dict[str, Any]],
) -> None:
    """Add logical connections between resources based on common patterns."""
    resource_types = {r["resource_type"]: r["resource_id"] for r in resources}

    # Common connection patterns: (from_type, to_type, label)
    patterns = [
        ("front_door", "application_gateway", "routes to"),
        ("front_door", "app_service", "routes to"),
        ("front_door", "load_balancer", "routes to"),
        ("application_gateway", "app_service", "routes to"),
        ("application_gateway", "kubernetes_service", "routes to"),
        ("application_gateway", "container_apps", "routes to"),
        ("load_balancer", "virtual_machine", "distributes to"),
        ("load_balancer", "vm_scale_set", "distributes to"),
        ("load_balancer", "kubernetes_service", "distributes to"),
        ("app_service", "sql_database", "reads/writes"),
        ("app_service", "cosmos_db", "reads/writes"),
        ("app_service", "redis_cache", "caches"),
        ("app_service", "storage_account", "stores"),
        ("app_service", "key_vault", "secrets"),
        ("app_service", "event_hub", "publishes"),
        ("app_service", "service_bus", "messages"),
        ("kubernetes_service", "sql_database", "reads/writes"),
        ("kubernetes_service", "cosmos_db", "reads/writes"),
        ("kubernetes_service", "redis_cache", "caches"),
        ("kubernetes_service", "key_vault", "secrets"),
        ("container_apps", "sql_database", "reads/writes"),
        ("container_apps", "cosmos_db", "reads/writes"),
        ("container_apps", "redis_cache", "caches"),
        ("azure_functions", "event_hub", "triggered by"),
        ("azure_functions", "service_bus", "triggered by"),
        ("azure_functions", "storage_account", "reads/writes"),
        ("azure_functions", "cosmos_db", "reads/writes"),
        ("event_hub", "stream_analytics", "streams to"),
        ("event_hub", "azure_functions", "triggers"),
        ("api_management", "app_service", "proxies"),
        ("api_management", "azure_functions", "proxies"),
        ("api_management", "kubernetes_service", "proxies"),
        ("virtual_machine", "sql_database", "reads/writes"),
        ("virtual_machine", "storage_account", "stores"),
        ("openai_service", "ai_search", "retrieves from"),
        ("machine_learning", "storage_account", "reads data"),
        ("data_factory", "sql_database", "ETL"),
        ("data_factory", "data_lake", "loads"),
        ("data_factory", "synapse", "loads"),
        ("application_insights", "app_service", "monitors"),
        ("application_insights", "azure_functions", "monitors"),
        ("log_analytics", "monitor", "aggregates"),
    ]

    for from_type, to_type, label in patterns:
        if from_type in resource_types and to_type in resource_types:
            connections.append({
                "from_id": resource_types[from_type],
                "to_id": resource_types[to_type],
                "label": label,
            })
