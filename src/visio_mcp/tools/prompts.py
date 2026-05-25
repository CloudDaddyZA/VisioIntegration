"""MCP prompt handlers."""

from __future__ import annotations

from visio_mcp._state import mcp
from visio_mcp.azure_catalog import AZURE_SHAPE_CATALOG, list_categories
from visio_mcp.caf_validator import CAF_NAMING_PREFIXES
from visio_mcp.reference_architectures import (
    list_reference_architectures,
    list_architecture_styles,
    list_design_patterns,
)

# PROMPTS
# ═══════════════════════════════════════════════════════════════════

@mcp.prompt()
def getting_started() -> str:
    """How-to guide for first-time users of the Azure Visio MCP server."""
    return """# Getting Started with Azure Visio MCP Server

## Quick Start (3 steps)

1. **Create a diagram** — call `create_diagram` with a name, e.g.:
   `create_diagram(name="My Azure Architecture")`

2. **Add resources** — use `add_azure_resource` with a shape key from the catalog:
   `add_azure_resource(resource_type="app_service", display_name="Web App")`
   Use `list_azure_shapes()` to see all 151 available Azure resource types.

3. **Save** — call `save_diagram` with a path and format:
   `save_diagram(output_path="diagram.vsdx", format="vsdx")`
   Supported formats: `vsdx` (Microsoft Visio) or `drawio` (draw.io XML).

## Common Workflows

### Build from a reference architecture template
```
list_reference_archs()                        # See 5 available templates
apply_reference_architecture("baseline_web_app")  # Creates full diagram
```
Templates: baseline_foundry_chat, azure_landing_zone, baseline_web_app, ai_landing_zone, microservices_aks

### Add resources and connect them
```
add_azure_resource(resource_type="app_service", display_name="web-app-prod")
add_azure_resource(resource_type="sql_database", display_name="sqldb-prod")
connect_resources(source_id="web-app-prod", target_id="sqldb-prod", label="SQL")
```

### Group resources inside boundaries
```
add_boundary(boundary_type="virtual_network", display_name="vnet-prod")
add_azure_resource(resource_type="app_service", display_name="app-01", group_id="vnet-prod")
```

### Validate architecture quality
```
validate_waf()   # Well-Architected Framework (6 pillars: Reliability, Security, Cost, etc.)
validate_caf()   # Cloud Adoption Framework (naming, tagging, structure)
```

### Browse the architecture catalog (206 entries)
```
browse_architecture_catalog(category="AI + Machine Learning")
search_arch_catalog(query="kubernetes")
```

## Available Resources (read with resources/read)
- `azure://shape-catalog` — All 151 Azure shapes with icons & WAF tips
- `azure://reference-architectures` — 5 buildable architecture templates
- `azure://architecture-catalog` — 206 Architecture Center entries
- `azure://architecture-styles` — 6 architecture styles (microservices, event-driven, etc.)
- `azure://design-patterns` — 40 cloud design patterns
- `azure://connector-styles` — Connection line types and styles
- `azure://boundary-styles` — Boundary grouping types (VNet, subnet, etc.)
- `azure://diagram-standards` — Microsoft visual standards and color palette

## 28 Tools Summary
| Tool | Purpose |
|------|---------|
| create_diagram | Create new empty diagram |
| list_azure_shapes | Browse 151 Azure resource types |
| add_azure_resource | Place a resource on the diagram |
| add_boundary | Add a grouping boundary (VNet, subnet, RG, etc.) |
| connect_resources | Connect two resources with a line/arrow |
| assign_resource_to_boundary | Move a resource into a boundary |
| remove_resource / remove_boundary | Remove elements |
| auto_layout | Auto-arrange the diagram layout |
| get_diagram_state | Get current diagram contents |
| save_diagram | Save as .vsdx or .drawio |
| validate_waf / validate_caf | Architecture validation |
| get_waf_tips | WAF tips for a specific resource type |
| suggest_architecture_improvements | AI-powered improvement suggestions |
| list_reference_archs | List 16 reference architecture templates |
| apply_reference_architecture | Build a full diagram from a template |
| suggest_architecture_style | Recommend a style for your workload |
| suggest_design_patterns | Recommend design patterns |
| browse_architecture_catalog | Browse 206 Architecture Center entries |
| search_arch_catalog | Search the catalog by keyword |
| import_vsdx | Import an existing Visio file |
| import_image | Convert an image/screenshot to a diagram |
"""


@mcp.prompt()
def hub_spoke_architecture() -> str:
    """Prompt template for Azure Landing Zone hub-spoke architecture per Azure Architecture Center."""
    return """Create an Azure hub-spoke architecture aligned with the Azure Architecture Center
landing zone reference architecture.

Use `apply_reference_architecture("azure_landing_zone")` to start from the official template,
or build manually following these Microsoft standards:

1. Management Group hierarchy (per CAF):
   - Root MG → Platform MG (Identity, Management, Connectivity subscriptions)
   - Root MG → Landing Zones MG (Corp, Online sub-groups)

2. Hub VNet (Connectivity subscription):
   - AzureFirewallSubnet with Azure Firewall Premium
   - GatewaySubnet with VPN Gateway / ExpressRoute
   - AzureBastionSubnet with Azure Bastion
   - snet-dns-inbound for Private DNS

3. Spoke VNets (one per workload landing zone):
   - Peered to Hub, forced tunneling through Firewall
   - Dedicated subnets per function (compute, PE, integration)

4. Platform shared services (Management subscription):
   - Log Analytics, Azure Monitor, Azure Policy
   - Defender for Cloud, Microsoft Sentinel

Visual standards: Use `get_diagram_standards()` for Microsoft color palette and conventions.
Source: https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/

Validate with WAF and CAF after creation."""


@mcp.prompt()
def three_tier_web_app() -> str:
    """Prompt template for baseline zone-redundant web app per Azure Architecture Center."""
    return """Create a baseline zone-redundant web application architecture aligned
with the Azure Architecture Center reference pattern.

Use `apply_reference_architecture("baseline_web_app")` to start from the official template,
or build manually following these Microsoft standards:

1. Ingress (snet-appGateway subnet):
   - Application Gateway with WAF v2 in Prevention mode
   - DDoS Protection Plan on public IP

2. Compute (snet-appServiceIntegration subnet):
   - App Service with VNet integration, zone-redundant P1v3
   - Deployment slots for zero-downtime deploys

3. Private endpoint subnet (snet-privateEndpoints):
   - PE: SQL Database, PE: Key Vault, PE: Storage
   - All PaaS accessed only through private endpoints

4. Data tier (separate resource group):
   - Azure SQL Database (BusinessCritical, zone-redundant)
   - Azure Storage (ZRS)

5. Shared services (separate resource group):
   - Key Vault, Managed Identity, Entra ID
   - Application Insights + Log Analytics

Visual standards: Use `get_diagram_standards()` for Microsoft color palette and conventions.
Source: https://learn.microsoft.com/en-us/azure/architecture/web-apps/app-service/architectures/baseline-zone-redundant

Validate with WAF and CAF after creation."""


@mcp.prompt()
def microservices_architecture() -> str:
    """Prompt template for microservices on AKS per Azure Architecture Center."""
    return """Create a microservices architecture on AKS aligned with the
Azure Architecture Center reference pattern.

Use `apply_reference_architecture("microservices_aks")` to start from the official template,
or build manually following these Microsoft standards:

1. Global ingress:
   - Azure Front Door for global load balancing
   - Application Gateway with AGIC for regional ingress

2. Compute (snet-aks-nodes subnet):
   - AKS private cluster (Standard SKU)
   - System + user node pools across availability zones
   - Workload Identity for pod authentication

3. Container Registry (private endpoint):
   - Image pull via private endpoint in PE subnet

4. Per-service databases (private endpoints):
   - Cosmos DB for Service A
   - Azure SQL for Service B
   - Redis Cache for shared caching

5. Async messaging:
   - Service Bus for inter-service communication
   - Event Grid for event-driven patterns

6. Observability:
   - Container Insights + Application Insights
   - Log Analytics workspace + Azure Monitor

Visual standards: Use `get_diagram_standards()` for Microsoft color palette and conventions.
Source: https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/containers/aks-microservices/aks-microservices

Validate with WAF and CAF after creation."""


@mcp.prompt()
def ai_chat_architecture() -> str:
    """Prompt template for baseline AI/Foundry chat per Azure Architecture Center."""
    return """Create a baseline end-to-end AI chat architecture aligned with the
Azure Architecture Center Foundry reference pattern.

Use `apply_reference_architecture("baseline_foundry_chat")` to start from the official template,
or build manually following these Microsoft standards:

1. Ingress (snet-appGateway subnet):
   - Application Gateway with WAF v2
   - DDoS Protection Plan

2. App tier (snet-appServicePlan subnet):
   - App Service (Chat UI) with VNet integration
   - Zone-redundant P1v3 plan

3. AI tier:
   - Foundry Agent Service (prompt-based agent)
   - Azure OpenAI (GPT-4o, data-zone provisioned)
   - Azure AI Search (Standard, 3 replicas)
   - snet-foundryIntegration and snet-agentsEgress subnets

4. Data tier:
   - Cosmos DB (NoSQL, continuous backup, zone-redundant)
   - Azure Storage (ZRS)

5. Network security:
   - Private endpoints for ALL PaaS services in snet-privateEndpoints
   - Azure Firewall for egress control
   - Azure Bastion + jump box for portal access
   - Private DNS Zones, NSGs per subnet

6. Shared services:
   - Key Vault, Managed Identities (per App + per Foundry project)
   - Entra ID, Log Analytics, Application Insights
   - Defender for Cloud

Workflow steps (numbered on diagram):
  1. User → App Gateway (WAF) → App Service
  2. App Service → Foundry Agent (via private endpoint)
  3. Agent processes request per system prompt
  4. Agent → AI Search (RAG retrieval)
  5. Agent → Azure Firewall (external tool calls)
  6. Agent → OpenAI model (inference)
  7. Agent → Cosmos DB (persist conversation)

Visual standards: Use `get_diagram_standards()` for Microsoft color palette and conventions.
Source: https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/baseline-microsoft-foundry-chat

Validate with WAF and CAF after creation."""


@mcp.prompt()
def ai_landing_zone_architecture() -> str:
    """Prompt template for AI workload in Azure Landing Zone per CAF guidance."""
    return """Create an AI workload deployed within the Azure Landing Zone architecture,
following Microsoft CAF guidance that 'AI is just another workload — no separate
AI landing zone is needed.'

Use `apply_reference_architecture("ai_landing_zone")` to start from the official template,
or build manually following these Microsoft standards:

1. Platform Landing Zone (shared):
   - Connectivity sub: Hub VNet with Azure Firewall, VPN Gateway
   - Management sub: Log Analytics, Azure Policy, Defender, Sentinel

2. Application Landing Zone (AI workload under Corp MG):
   - Spoke VNet peered to Hub, forced tunneling through Firewall
   - snet-appGateway: Application Gateway + WAF v2
   - snet-compute: Container Apps (inference API), App Service (Chat UI)
   - snet-privateEndpoints: PEs for OpenAI, AI Search, Cosmos DB, Storage
   - snet-foundryIntegration: Foundry agent delegation

3. AI Services (rg-ai-services):
   - Azure OpenAI, AI Search (3 replicas), Azure AI Services
   - ML Workspace, Container Registry

4. Data (rg-ai-data):
   - Cosmos DB (zone-redundant, continuous backup)
   - Storage Account (GRS), Redis Cache

5. Shared (rg-ai-shared):
   - Key Vault, Managed Identity, Entra ID
   - Log Analytics (workload) → feeds Platform Log Analytics
   - Application Insights, Azure Monitor

6. Governance:
   - Azure Policy at Management Group scope
   - Defender for Cloud monitoring across subscriptions
   - Sentinel SIEM integration

Visual standards: Use `get_diagram_standards()` for Microsoft color palette and conventions.
Source: https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/scenarios/ai/

Validate with WAF and CAF after creation."""


@mcp.prompt()
def business_to_architecture() -> str:
    """Translate a business case or business requirement into an Azure architecture diagram — analyze workload characteristics, select architecture style, build resources, and validate."""
    return """\
You are an Azure Solutions Architect. The user will describe a **business case** or \
**business requirement** (not a technical architecture). Your job is to translate their \
business needs into an Azure architecture diagram.

Follow this structured workflow:

## 1. Analyse the Business Requirement
Break the requirement into these dimensions:
- **Workload type** — Web app, API, batch processing, real-time analytics, AI/ML, IoT, etc.
- **Users & scale** — Expected concurrent users, requests/sec, data volume, growth trajectory
- **Data requirements** — Relational, NoSQL, files/blobs, search, caching, data lake
- **Integration** — Third-party APIs, on-premises connectivity, messaging/events
- **Security & compliance** — Authentication (B2C, B2B, internal), regulatory (PCI, HIPAA, SOC2), data residency
- **Availability & DR** — SLA target, RPO/RTO, multi-region needs
- **Budget sensitivity** — Cost-optimised vs. performance-first

## 2. Select Architecture Style
Use `suggest_architecture_style` with a description of the workload to pick the best-fit \
pattern (N-Tier, Web-Queue-Worker, Microservices, Event-Driven, Big Data, Big Compute). \
Use `get_architecture_style_detail` for deeper guidance.

## 3. Check the Architecture Catalog
Use `search_arch_catalog` with keywords from the business domain to find matching reference \
architectures or solution ideas from the 206-entry Azure Architecture Center catalog. \
If a good match exists, prefer using `apply_reference_architecture` or the catalog entry \
as a blueprint.

## 4. Identify Design Patterns
Use `suggest_design_patterns` for any cross-cutting concerns (caching, resilience, \
async processing, CQRS, etc.). Apply the returned diagram_implications when placing resources.

## 5. Build the Diagram Step-by-Step
1. `create_diagram` with a descriptive name derived from the business case
2. Add **boundaries** first (resource groups, VNets, subnets) using CAF naming: \
   `rg-<app>-<env>-<region>`, `vnet-<app>-<env>-<region>`
3. Add **resources** one by one inside boundaries, choosing the right Azure service \
   for each requirement (e.g., App Service for web, Azure SQL for relational data, \
   Redis Cache for caching, Service Bus for messaging)
4. Add **connections** with descriptive labels (e.g., "HTTPS", "Private Endpoint", \
   "Service Bus Queue")
5. `auto_layout` for clean arrangement

## 6. Validate & Iterate
Run `validate_waf` and `validate_caf` to check compliance. Fix any findings, \
then re-validate until scores are acceptable.

## 7. Explain Your Decisions
After building, provide a brief summary:
- Why you chose each Azure service
- Key architecture decisions and trade-offs
- Estimated cost tier (Dev/Test, Production, Enterprise)
- Recommendations for next steps (monitoring, CI/CD, disaster recovery)

**Important rules:**
- Always explain your reasoning *before* making tool calls
- Use CAF-compliant naming conventions throughout
- Prefer managed PaaS services over IaaS unless the requirement demands it
- Include security (NSGs, Private Endpoints, Managed Identity) by default
- Add monitoring (Application Insights, Log Analytics) unless explicitly out of scope"""


