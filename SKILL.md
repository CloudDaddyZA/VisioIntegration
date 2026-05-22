# Azure Visio MCP — Skill Definition

## Metadata

- **Name**: azure-visio-mcp
- **Version**: 0.2.0
- **Description**: Create, validate, and export production-quality Azure architecture diagrams using natural language via MCP tools.

## When to Use

Use this skill when the user asks to:
- Create or draw an Azure architecture diagram
- Generate a Visio (.vsdx) or Draw.io (.drawio) architecture file
- Validate an architecture against WAF (Well-Architected Framework) or CAF (Cloud Adoption Framework)
- Apply a reference architecture template (hub-spoke, 3-tier, microservices, etc.)
- Get Azure SKU recommendations or live pricing for resources
- Import an existing Visio file or architecture image
- Browse Azure architecture patterns, styles, or the service catalog
- Compare Azure service tiers or get FinOps guidance

### Trigger Phrases

**Diagram Creation**
- "draw an Azure architecture"
- "create a Visio diagram"
- "create a drawio diagram"
- "architecture diagram for..."
- "diagram my Azure environment"
- "visualize my infrastructure"
- "generate architecture diagram"

**Reference Architectures**
- "hub-spoke network diagram"
- "3-tier web app diagram"
- "microservices architecture"
- "serverless event-driven architecture"
- "data analytics lakehouse"
- "IoT solution architecture"
- "AI/ML platform diagram"
- "disaster recovery architecture"
- "hybrid connectivity diagram"
- "zero trust network architecture"
- "API management platform"
- "container apps microservices"
- "enterprise data pipeline"
- "AI/ML pipeline diagram"
- "RAG GenAI app architecture"
- "streaming analytics architecture"
- "apply reference architecture"
- "load a template"

**Architecture Styles**
- "N-tier architecture"
- "web-queue-worker architecture"
- "microservices architecture"
- "event-driven architecture"
- "big data architecture"
- "big compute architecture"
- "dataflow architecture"
- "data analytics pipeline"
- "database flow diagram"
- "AI/ML pipeline"
- "RAG AI application"
- "streaming analytics"
- "integration workflow"
- "IoT edge architecture"
- "suggest architecture style for..."
- "what architecture style should I use"

**Design Patterns**
- "design pattern for..."
- "CQRS pattern"
- "event sourcing pattern"
- "saga pattern"
- "circuit breaker pattern"
- "retry pattern"
- "bulkhead pattern"
- "gateway aggregation"
- "gateway routing"
- "sidecar pattern"
- "ambassador pattern"
- "strangler fig pattern"
- "backends for frontends"
- "cache-aside pattern"
- "claim check pattern"
- "competing consumers"
- "priority queue pattern"
- "publisher-subscriber"
- "queue-based load leveling"
- "throttling pattern"
- "valet key pattern"
- "data lake pattern"
- "ETL/ELT pattern"
- "lambda architecture"
- "kappa architecture"
- "feature store pattern"
- "MLOps CI/CD pattern"
- "RAG pattern"
- "data mesh pattern"
- "stream processing pattern"
- "polyglot persistence"

**Validation**
- "validate my architecture"
- "WAF validation"
- "Well-Architected Framework check"
- "CAF naming check"
- "Cloud Adoption Framework validation"
- "check reliability"
- "check security posture"
- "check cost optimization"
- "check operational excellence"
- "check performance efficiency"
- "suggest improvements"
- "architecture recommendations"

**SKU & Pricing**
- "Azure pricing for..."
- "compare VM SKUs"
- "compare Azure SKUs"
- "VM family recommendation"
- "what VM size should I use"
- "App Service tier recommendation"
- "AKS sizing guidance"
- "SQL database tier comparison"
- "Cosmos DB pricing"
- "reserved instance savings"
- "FinOps guidance"
- "cost optimize my architecture"

**Azure Services (by category)**
- "virtual machine diagram"
- "App Service architecture"
- "Azure Functions serverless"
- "AKS Kubernetes cluster"
- "Container Apps deployment"
- "Azure SQL database"
- "Cosmos DB architecture"
- "PostgreSQL Flexible Server"
- "Azure Storage account"
- "Blob storage architecture"
- "Virtual Network diagram"
- "Application Gateway"
- "Azure Front Door"
- "Azure Firewall"
- "Load Balancer architecture"
- "VPN Gateway"
- "ExpressRoute connection"
- "Azure API Management"
- "Service Bus messaging"
- "Event Hub streaming"
- "Event Grid pub/sub"
- "Logic Apps workflow"
- "Azure OpenAI service"
- "Azure AI Search"
- "Cognitive Services"
- "Azure Machine Learning"
- "Key Vault security"
- "Azure Monitor"
- "Log Analytics workspace"
- "Application Insights"
- "Azure DevOps pipeline"
- "Container Registry"
- "Redis Cache"
- "CDN architecture"
- "DNS architecture"
- "Traffic Manager"
- "Azure Bastion"
- "Network Security Group"
- "Private Endpoint"
- "Azure IoT Hub"
- "Azure Digital Twins"
- "Azure Synapse Analytics"
- "Azure Data Factory"
- "Azure Databricks"
- "Azure Data Explorer"
- "Power BI architecture"
- "Azure Purview"
- "Azure Active Directory"
- "Managed Identity"

**Import & Export**
- "save as drawio"
- "save as Visio"
- "export to vsdx"
- "import Visio file"
- "import existing diagram"
- "import architecture image"
- "import pricing estimate"
- "convert image to architecture"

**Browsing & Discovery**
- "browse Azure shapes"
- "list available resources"
- "search architecture catalog"
- "browse architecture catalog"
- "what Azure services are available"
- "show me compute services"
- "show me networking services"
- "show me database services"

## Capabilities

### 31 MCP Tools

| Category | Tools |
|----------|-------|
| Diagram CRUD | `create_diagram`, `add_azure_resource`, `add_boundary`, `connect_resources`, `assign_resource_to_boundary`, `remove_resource`, `remove_boundary` |
| Layout | `auto_layout` |
| State | `get_diagram_state`, `get_diagram_standards` |
| Validation | `validate_waf`, `validate_caf`, `suggest_architecture_improvements`, `get_waf_tips` |
| Reference Architectures | `list_reference_archs`, `apply_reference_architecture`, `get_reference_arch_details` |
| Architecture Knowledge | `suggest_architecture_style`, `get_architecture_style_detail`, `suggest_design_patterns`, `get_design_pattern_detail`, `browse_architecture_catalog`, `search_arch_catalog`, `get_arch_catalog_entry` |
| SKU & Pricing | `query_azure_pricing`, `compare_azure_skus`, `get_sku_recommendations` |
| Rendering | `save_diagram`, `list_azure_shapes` |
| Import | `import_vsdx`, `import_image`, `import_pricing_estimate` |

### 8 MCP Resources

| URI | Description |
|-----|-------------|
| `azure://shape-catalog` | Full 151-shape catalog with categories and icon paths |
| `azure://connector-styles` | Standard connector styling (black, 1pt, right-angle) |
| `azure://boundary-styles` | Boundary visual standards (dashed borders, fills) |
| `azure://reference-architectures` | List of 16 available templates |
| `azure://diagram-standards` | Microsoft Architecture Center visual conventions |
| `azure://architecture-styles` | 14 architecture style definitions |
| `azure://design-patterns` | 50 cloud design patterns |
| `azure://architecture-catalog` | 206 curated Azure architectures |

### 7 MCP Prompts

| Prompt | Description |
|--------|-------------|
| `getting_started` | Onboarding guide with example prompts |
| `hub_spoke_architecture` | Hub-spoke network diagram workflow |
| `three_tier_web_app` | 3-tier web application workflow |
| `microservices_architecture` | Microservices diagram workflow |
| `validate_existing` | Import and validate existing architecture |
| `business_requirements` | Business need → architecture diagram workflow |
| `architecture_style_guide` | Style selection guidance |

## Workflow Patterns

### Standard Diagram Creation Flow

```
1. create_diagram(name)
2. add_boundary(type, name)         — boundaries first
3. add_azure_resource(type, name, group_id)  — resources into boundaries
4. connect_resources(from, to, label)
5. auto_layout()                    — positions everything
6. validate_waf() + validate_caf()  — check compliance
7. save_diagram(path, format)       — render to file
```

### Reference Architecture Flow

```
1. list_reference_archs()           — see available templates
2. apply_reference_architecture(key) — creates full diagram
3. validate_waf()                   — confirm alignment
4. save_diagram(path, format)       — export
```

### Validation Flow

```
1. validate_waf()       — scores 5 pillars (reliability, security, cost, ops, performance)
2. validate_caf()       — checks naming conventions against 7 principles
3. suggest_architecture_improvements() — AI recommendations
```

## Key Domain Knowledge

### Azure Service Categories (19)
Compute, Networking, Storage, Databases, Security, Identity, Integration, Analytics, AI + Machine Learning, DevOps, Management + Governance, Web, Containers, IoT, Messaging, Migration, Mixed Reality, Media, General

### Resource Type Aliases
| Alias | Canonical Type |
|-------|---------------|
| `vm` | `virtual_machine` |
| `aks` | `kubernetes_service` |
| `apim` | `api_management` |
| `sql` | `sql_database` |
| `cosmos` | `cosmos_db` |
| `kv` | `key_vault` |
| `nsg` | `network_security_group` |
| `pip` | `public_ip` |
| `agw` | `application_gateway` |
| `afd` | `front_door` |

### CAF Naming Prefixes
| Resource | Prefix |
|----------|--------|
| Virtual Machine | `vm-` |
| App Service | `app-` |
| SQL Database | `sql-` |
| Virtual Network | `vnet-` |
| Subnet | `snet-` |
| Key Vault | `kv-` |
| Storage Account | `st` |
| AKS Cluster | `aks-` |
| Container Registry | `cr` |
| Resource Group | `rg-` |
| Network Security Group | `nsg-` |
| Public IP | `pip-` |

### Reference Architecture Templates (16)
`hub_spoke_network`, `three_tier_web_app`, `microservices_aks`, `serverless_event_driven`, `data_analytics_lakehouse`, `iot_solution`, `ai_ml_platform`, `disaster_recovery`, `hybrid_connectivity`, `zero_trust_network`, `api_management_platform`, `container_apps_microservices`, `enterprise_data_pipeline`, `ai_ml_pipeline`, `rag_genai_app`, `streaming_analytics`

### WAF Pillars (5)
1. **Reliability** — redundancy, failover, availability zones
2. **Security** — network isolation, encryption, identity, key management
3. **Cost Optimization** — right-sizing, reserved instances, serverless
4. **Operational Excellence** — monitoring, automation, IaC
5. **Performance Efficiency** — caching, CDN, scaling, load balancing

## Runtime Requirements

- Python 3.12+ with `.venv` (managed by `uv`)
- Microsoft Visio (optional — for `.vsdx` COM rendering)
- Node.js 18+ (for VS Code extension build)
- OpenAI API key or Azure OpenAI (for AI agent features)

## Transport

- **Protocol**: MCP (Model Context Protocol) over JSON-RPC 2.0
- **Transport**: stdio (stdin/stdout)
- **Launch**: `python -m visio_mcp.server`
