# Visio Azure MCP — AI-Powered Azure Architecture Diagrams

An MCP (Model Context Protocol) server and interactive Streamlit app that creates **production-quality Microsoft Visio architecture diagrams** aligned with [Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/) standards.

Combines AI-driven natural language understanding with Visio COM automation to go from *"build me a 3-tier web app"* to a fully rendered `.vsdx` file — with official Azure SVG icons, Microsoft-standard boundary styling, numbered workflow steps, and WAF/CAF validation.

---

## Features

### MCP Server (21 tools)

| Category | Tools | Description |
|----------|-------|-------------|
| **Diagram CRUD** | `create_diagram`, `add_azure_resource`, `add_boundary`, `connect_resources`, `assign_resource_to_boundary`, `remove_resource`, `remove_boundary` | Build diagrams programmatically with 70+ Azure resource types |
| **Layout** | `auto_layout` | Automatic tiered/grid/grouped layout following Architecture Center conventions |
| **Reference Architectures** | `apply_reference_architecture`, `list_reference_archs`, `get_reference_arch_details` | 5 built-in templates from Azure Architecture Center with hand-tuned position hints |
| **Validation** | `validate_waf`, `validate_caf`, `suggest_architecture_improvements`, `get_waf_tips` | Well-Architected Framework (5 pillars) and Cloud Adoption Framework (7 principles) |
| **Rendering** | `save_diagram` | Renders to `.vsdx` via Visio COM with official Azure SVG icons |
| **Import** | `import_vsdx`, `import_image` | Import existing `.vsdx` files or convert screenshots/whiteboard photos/SVGs to diagrams |
| **Reference** | `list_azure_shapes`, `get_diagram_state`, `get_diagram_standards` | Catalog browsing and diagram inspection |

### Interactive Streamlit App

- **AI Chat Interface** — Describe your architecture in natural language; the AI agent translates to MCP tool calls
- **Live Diagram Preview** — SVG preview updates in real-time as you build
- **Multiple AI Providers** — GitHub Copilot (GitHub Models), OpenAI, Azure OpenAI
- **Reference Architecture Templates** — One-click apply for 5 Azure Architecture Center patterns
- **Import & Assess** — Upload existing `.vsdx` for WAF/CAF assessment, or upload an image for AI-powered conversion
- **Save to Visio** — Export as `.vsdx` with browse dialog

### Visual Standards (from actual Microsoft Architecture Center SVGs)

Every diagram follows the exact visual conventions extracted from published Azure Architecture Center SVGs:

- **Boundaries**: White/light gray fills (#FFFFFF/#F2F2F2), gray dashed borders (#7F7F7F), 0.5pt weight
- **Connectors**: All black (#000000), 1pt, right-angle routed with arrow endpoints
- **Step Circles**: Green (#107C10) with white bold numbers (Segoe UI)
- **Labels**: Black (#000000) Segoe UI, boundary labels in blue-gray (#5B9BD5) bold
- **Icons**: Official Azure SVG icons imported at 1:1 aspect ratio — never cropped, flipped, or rotated

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit App (UI)                    │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ AI Agent │→ │  MCP Client  │→ │ Diagram Preview   │  │
│  │ (OpenAI) │  │ (stdio)      │  │ (SVG renderer)    │  │
│  └──────────┘  └──────┬───────┘  └───────────────────┘  │
└─────────────────────────┬───────────────────────────────┘
                          │ stdio (JSON-RPC)
┌─────────────────────────▼───────────────────────────────┐
│                  MCP Server (FastMCP)                    │
│  ┌────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
│  │ Diagram    │ │ Layout      │ │ Reference           │ │
│  │ State      │ │ Engine      │ │ Architectures (×5)  │ │
│  ├────────────┤ ├─────────────┤ ├─────────────────────┤ │
│  │ WAF        │ │ CAF         │ │ Azure Catalog       │ │
│  │ Validator  │ │ Validator   │ │ (70+ types, 709 SVGs│ │
│  ├────────────┤ ├─────────────┤ ├─────────────────────┤ │
│  │ Visio COM  │ │ VSDX Import │ │ Image Import        │ │
│  │ Engine     │ │ (COM parse) │ │ (GPT-4o Vision)     │ │
│  └────────────┘ └─────────────┘ └─────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| **Python** | ≥ 3.11 | Tested on 3.14 |
| **Microsoft Visio** | 2019+ / Microsoft 365 | Required for `.vsdx` rendering (COM automation) |
| **Windows** | 10/11 | Visio COM is Windows-only |
| **GitHub CLI** (optional) | Any | For GitHub Copilot auto-auth (`gh auth login`) |

---

## Installation

### 1. Clone and create virtual environment

```powershell
git clone https://github.com/CloudDaddyZA/VisioIntegration.git
cd VisioIntegration
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
# Core MCP server
pip install -e .

# Interactive app (Streamlit + OpenAI)
pip install -e ".[app]"

# Development (tests)
pip install -e ".[dev]"
```

### 3. Configure AI provider

Choose **one** provider. GitHub Copilot requires the least setup:

#### GitHub Copilot (recommended)

```powershell
# Install GitHub CLI: https://cli.github.com
gh auth login
# The app auto-detects `gh auth token` — no manual config needed
```

#### OpenAI

```powershell
$env:OPENAI_API_KEY = "sk-..."
$env:OPENAI_MODEL = "gpt-4o"         # optional, defaults to gpt-4o
```

#### Azure OpenAI

```powershell
$env:AZURE_OPENAI_ENDPOINT = "https://your-instance.openai.azure.com/"
$env:AZURE_OPENAI_API_KEY = "..."
$env:AZURE_OPENAI_DEPLOYMENT = "gpt-4o"
```

See [`app/.env.example`](app/.env.example) for all options.

---

## Quick Start

### Option A: Interactive App (recommended)

```powershell
# Start the MCP server (background)
.\.venv\Scripts\python.exe -m src.visio_mcp.server &

# Start the Streamlit app
$env:GITHUB_TOKEN = (gh auth token)
.\.venv\Scripts\streamlit.exe run app/streamlit_app.py --server.port 8501
```

Open http://localhost:8501 and try:
- *"Create a 3-tier web application architecture"*
- *"Apply the baseline Foundry chat reference architecture"*
- *"Validate my architecture against WAF"*
- *"Save as production-web-app.vsdx"*

### Option B: VS Code MCP Integration

The project includes [`.vscode/mcp.json`](.vscode/mcp.json) for direct VS Code Copilot integration. Open the project in VS Code and the MCP server registers automatically.

### Option C: CLI

```powershell
# Run the MCP server directly
visio-mcp

# Or launch the full app
visio-app
```

---

## Reference Architectures

Five production-ready templates from Azure Architecture Center, each with hand-tuned position hints:

| Key | Architecture | Resources | Source |
|-----|-------------|-----------|--------|
| `baseline_foundry_chat` | Baseline E2E Chat with Microsoft Foundry | 27 resources, 15 boundaries | [Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/baseline-microsoft-foundry-chat) |
| `azure_landing_zone` | CAF Landing Zone with Hub-Spoke | 24 resources, 19 boundaries | [Architecture Center](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/) |
| `baseline_web_app` | Baseline Zone-Redundant Web App | 16 resources, 9 boundaries | [Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/web-apps/app-service/architectures/baseline-zone-redundant) |
| `ai_landing_zone` | AI Workload in Azure Landing Zone | 30 resources, 18 boundaries | [Architecture Center](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/scenarios/ai/) |
| `microservices_aks` | Microservices on AKS | 23 resources, 8 boundaries | [Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/microservices/aks) |

Apply via chat: *"Apply the baseline web app reference architecture"*
Or sidebar: **Reference Architectures** → select template → **Apply Template**

---

## Import Features

### Import Existing .vsdx

Upload an existing Visio diagram to parse its shapes, match them to Azure resource types, and optionally run WAF/CAF assessment:

1. **Sidebar** → **Import** → **📄 Visio (.vsdx)** tab
2. Upload your `.vsdx` file
3. Check "Run WAF/CAF assessment" (optional)
4. Click **Import .vsdx**

The parser:
- Opens the file via Visio COM and extracts all shapes from Page 1
- Matches shape text and master names to 70+ Azure resource types using fuzzy matching
- Identifies large rectangles as boundaries (VNets, subnets, resource groups)
- Detects connectors and their endpoints
- Auto-assigns resources to containing boundaries by position
- Skips step number circles, title shapes, and decorative elements
- Runs WAF (5 pillars) and CAF (7 principles) validation

### Import Image → Diagram

Upload a screenshot, whiteboard photo, block diagram, or SVG and AI converts it to a proper Azure architecture diagram:

1. **Sidebar** → **Import** → **🖼️ Image** tab
2. Upload a PNG/JPG/BMP/GIF/WEBP/TIFF/SVG image
3. Preview the image (SVGs render inline)
4. Click **Convert to Diagram**

The converter:
- **Raster images** (PNG, JPG, BMP, GIF, WEBP, TIFF) → encoded and sent to GPT-4o Vision
- **SVG files** → parsed as structured XML text (no vision model needed; the LLM reads labels and structure directly)
- The prompt includes the full Azure resource catalog (70+ types) for accurate matching
- Returns structured JSON with resources, boundaries, and connections
- Positions are approximated from the spatial layout in the image
- Auto-layouts the result

---

## Validation

### WAF — Well-Architected Framework

Validates against all 5 pillars:

| Pillar | Checks |
|--------|--------|
| **Reliability** | Load balancers, multi-region, availability zones, geo-replication, storage redundancy |
| **Security** | Key Vault, managed identity, NSG/Firewall, private endpoints, DDoS, WAF, Defender |
| **Cost Optimization** | Autoscale, premium SKU justification, standalone VM count |
| **Operational Excellence** | Monitoring, CI/CD, Azure Policy |
| **Performance Efficiency** | Caching, CDN, async messaging |

Additionally checks Architecture Center reference alignment: private endpoints for PaaS, dedicated subnets, WAF on ingress, egress firewall.

### CAF — Cloud Adoption Framework

Validates against 7 principles:

| Principle | Checks |
|-----------|--------|
| **Naming Convention** | CAF prefixes (e.g., `vm-`, `rg-`, `vnet-`), environment indicators |
| **Resource Organization** | Boundary grouping, subscription/management group hierarchy |
| **Network Topology** | VNets, hub-spoke pattern, subnet segmentation, Bastion |
| **Identity and Access** | Entra ID, managed identities |
| **Governance** | Azure Policy, resource tagging |
| **Security Baseline** | Defender for Cloud, Sentinel |
| **Management and Monitoring** | Monitor, Log Analytics |

Scoring: starts at 100, critical findings deduct 15, warnings deduct 8, info deducts 2–3.

---

## Project Structure

```
VisioIntegration/
├── README.md                          # This file
├── pyproject.toml                     # Package config (hatchling)
├── .vscode/
│   ├── mcp.json                       # VS Code MCP server registration
│   └── settings.json                  # Python interpreter config
│
├── src/visio_mcp/                     # MCP Server package
│   ├── server.py                      # FastMCP server — 21 tools, 5 resources, 5 prompts
│   ├── models.py                      # Pydantic data models (DiagramState, resources, etc.)
│   ├── diagram_state.py               # In-memory diagram state manager (DiagramManager)
│   ├── azure_catalog.py               # 70+ Azure resource types, 709 SVG icon mappings
│   ├── visio_engine.py                # Visio COM rendering engine (SVG import, connectors)
│   ├── layout_engine.py               # Auto-layout (tiered, grid, grouped strategies)
│   ├── reference_architectures.py     # 5 Architecture Center templates with position hints
│   ├── waf_validator.py               # WAF 5-pillar validation engine
│   ├── caf_validator.py               # CAF 7-principle validation engine
│   └── stencils/                      # Official Azure icon SVGs (709 files, 28 categories)
│
├── app/                               # Streamlit interactive UI
│   ├── streamlit_app.py               # Main app (chat, preview, sidebar, import UI)
│   ├── ai_agent.py                    # AI agent (OpenAI function calling, token management)
│   ├── mcp_client.py                  # Thread-safe MCP client (stdio, background event loop)
│   ├── diagram_preview.py             # Browser-side SVG diagram renderer
│   ├── run.py                         # CLI launcher
│   └── .env.example                   # Environment variable template
│
├── tests/                             # Test suite
│   ├── test_reference_arch.py         # Reference architecture template tests
│   └── test_ai_landing_zone.py        # AI Landing Zone integration tests
│
└── output/                            # Generated diagrams (git-ignored)
```

---

## Azure Resource Catalog

The server includes 70+ Azure resource types with full SVG icon mappings:

<details>
<summary>All resource types (click to expand)</summary>

`ai_search` · `api_management` · `app_registration` · `app_service` · `app_service_plan` · `application_gateway` · `application_insights` · `bastion` · `blob_storage` · `bot_service` · `cdn_profile` · `cognitive_services` · `container_apps` · `container_instances` · `container_registry` · `cosmos_db` · `data_factory` · `data_lake_storage` · `databricks` · `ddos_protection` · `defender_for_cloud` · `devops` · `dns_zone` · `entra_id` · `event_grid` · `event_hub` · `expressroute` · `file_share` · `firewall` · `front_door` · `function_app` · `internet` · `iot_central` · `iot_hub` · `key_vault` · `kubernetes_service` · `load_balancer` · `log_analytics` · `logic_app` · `machine_learning` · `managed_disk` · `managed_identity` · `management_group` · `monitor` · `mysql_database` · `nat_gateway` · `nsg` · `on_premises` · `openai_service` · `policy` · `postgresql_database` · `private_endpoint` · `private_link` · `redis_cache` · `resource_group` · `sentinel` · `service_bus` · `signalr` · `sql_database` · `sql_managed_instance` · `static_web_app` · `storage_account` · `stream_analytics` · `subnet` · `subscription` · `synapse_analytics` · `traffic_manager` · `user` · `virtual_machine` · `virtual_network` · `vm_scale_set` · `vpn_gateway`

</details>

Icons are sourced from the official [Azure architecture icons](https://learn.microsoft.com/en-us/azure/architecture/icons/) pack (709 SVGs across 28 categories).

---

## Visio COM Technical Notes

The rendering engine uses Visio COM automation with specific constraints discovered through extensive testing:

- **Named cells only** — Always use `shape.Cells("PinX")`, never `shape.CellsSRC(section, row, col)`. Index-based access fails silently on SVG-imported group shapes.
- **Never call `AutoSizeDrawing()`** — This corrupts page sizing. The engine calculates the bounding box manually.
- **Always call `RemoveTheme()`** — Visio themes override explicit fill/line colors.
- **SVG import** — Uses `Page.Import(svg_path)` with named cell positioning and `LockAspect=1`.
- **Dynamic connectors** — Uses `ConnectorToolDataObject` with `Cells("BeginX").GlueTo(shape.Cells("PinX"))` for proper routing.
- **Page-level routing** — `RouteStyle=1` (right-angle) set on the page sheet for Architecture Center-style orthogonal connectors.
- **Y-axis flip** — Layout coordinates are top-down but Visio's Y-axis is bottom-up, requiring `page_height - y` conversion.

---

## Development

### Running Tests

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

### Adding a New Resource Type

1. Add the shape info to `AZURE_SHAPE_CATALOG` in [`azure_catalog.py`](src/visio_mcp/azure_catalog.py)
2. Add the SVG icon mapping to `SVG_ICON_MAP`
3. Place the SVG file in the appropriate `stencils/Azure_Public_Service_Icons/Icons/<category>/` folder
4. (Optional) Add WAF considerations to the shape's `waf_considerations` dict

### Adding a New Reference Architecture

1. Add a new `ReferenceArchitecture` dataclass instance in [`reference_architectures.py`](src/visio_mcp/reference_architectures.py)
2. Include `layout_hints` (resource positions) and `boundary_hints` (boundary positions/sizes)
3. Register in the `REFERENCE_ARCHITECTURES` dict
4. Add a corresponding `@mcp.prompt()` in [`server.py`](src/visio_mcp/server.py)

---

## License

Azure icons are subject to [Microsoft Terms of Use](src/visio_mcp/stencils/Azure_Public_Service_Icons/Microsoft_Terms_of_Use.pdf). See the included FAQ for icon usage guidelines.
