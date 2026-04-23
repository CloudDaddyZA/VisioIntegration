# src/visio_mcp/ — MCP Server Package

The core MCP (Model Context Protocol) server that exposes Azure architecture diagram
capabilities as tools, resources, and prompts for AI agents and direct tool calling.

---

## Capabilities

| Type | Count | Description |
|------|------:|-------------|
| **Tools** | 28 | Diagram CRUD, layout, validation, reference architectures, rendering, import |
| **Resources** | 8 | Diagram state, catalog browsing, shape listings |
| **Prompts** | 7 | Architecture creation, validation, import, style guidance, business requirements, getting started |
| **Azure Shapes** | 151 | Full catalog in `AZURE_SHAPE_CATALOG` with stencil + SVG mappings |
| **SVG Icons** | 97+ | Azure Public Service, Entra (7), and Fabric (28) icon sets |
| **Resource Aliases** | 40+ | Common abbreviations (`aks` → `kubernetes_service`, `apim` → `api_management`) |
| **Architecture Catalog** | 206 | Reference architectures from Azure Architecture Center |
| **Design Patterns** | 40 | Cloud design patterns with diagram implications |
| **Architecture Styles** | 6 | N-Tier, Web-Queue-Worker, Microservices, Event-Driven, Big Data, Big Compute |
| **Reference Architectures** | 12 | Hand-tuned templates with position hints and workflow steps |
| **Output Formats** | 2 | Visio `.vsdx` (COM / python-vsdx) and draw.io `.drawio` (mxGraph XML) |

---

## Module Reference

### `server.py` (~2,570 lines)

FastMCP server entry point. Registers all 28 tools, 8 resources, and 7 prompts.

Key responsibilities:
- Tool registration with parameter schemas and docstrings
- Request routing to `DiagramManager`, `VisioEngine`, `DrawioEngine`, `WafValidator`, `CafValidator`
- Alias resolution via `resolve_alias()` before resource type lookups
- Category-aware shape metadata injection on add_resource
- Architecture catalog search and browsing endpoints
- Image import with OpenAI vision API integration
- Business-to-architecture prompt with 7-step structured workflow

### `models.py` (~109 lines)

Pydantic data models shared across all modules:
- `DiagramState` — Top-level state container (resources, connections, boundaries, page dimensions, properties dict for page metadata)
- `DiagramResource` — Azure resource with position, size, properties, group assignment
- `Connection` — Labeled typed connector between two resources
- `BoundaryGroup` — Visual container (VNet, subnet, resource group, etc.)
- `ValidationFinding` / `ValidationReport` — WAF/CAF validation results (with page/page_name fields)
- `AzureShapeInfo` — Shape catalog entry metadata
- Enums: `AzureServiceCategory` (19), `WafPillar` (5), `CafPrinciple` (7)

### `diagram_state.py` (~209 lines)

In-memory diagram state management:
- `DiagramManager` class with CRUD operations for resources, connections, boundaries
- Automatic cleanup: removing a resource also removes its connections
- Boundary assignment/unassignment with cascading parent cleanup
- Query helpers: `get_resources_in_boundary()`, `get_connections_for_resource()`
- `summary()` — Compact serialization for MCP tool responses (includes page metadata per resource/boundary)

### `azure_catalog.py` (~1,490 lines)

Comprehensive Azure resource catalog:
- **`SVG_ICON_MAP`** (97 entries) — Maps resource type keys to SVG file paths in the Azure Public Service Icons pack
- **`ENTRA_ICON_MAP`** (7 entries) — Microsoft Entra icon paths
- **`FABRIC_ICON_MAP`** (28 entries) — Microsoft Fabric icon paths (item + color variants)
- **`ALL_ICON_MAPS`** — Merged lookup with cross-root path resolution
- **`RESOURCE_ALIASES`** (40+ entries) — Common abbreviations resolved by `resolve_alias()`
- **`AZURE_SHAPE_CATALOG`** (151 entries) — Full shape metadata (`AzureShapeInfo`) with stencil names, SVG paths, icon colors, WAF considerations
- **`BOUNDARY_STYLES`** / **`CONNECTOR_STYLES`** — Visual style definitions
- **`resolve_svg_path()`** — Resolves resource type → SVG file path (checks filesystem existence)
- **`get_icons_root()`** — Returns the path to the Azure Public Service Icons directory

### `layout_engine.py` (355 lines)

Automatic diagram layout:
- `LayoutEngine.layout()` — Main entry point, applies tiered or grid layout
- Boundary-aware positioning: groups resources within their parent boundaries
- Connection-aware: positions connected resources near each other
- Preserves reference architecture position hints when available
- Page size auto-calculation with margins

### `drawio_engine.py` (~275 lines)

Draw.io (mxGraph XML) rendering engine — **no Visio or Windows required**:
- **`DrawioEngine.render()`** — Converts `DiagramState` to a `.drawio` file
- **`DRAWIO_AZURE_STYLES`** (97+ entries) — Maps resource type keys to draw.io style strings using the built-in `img/lib/azure2/` Azure icon library
- Boundaries rendered as styled rounded rectangles with fill/stroke from `BOUNDARY_STYLES`
- Connectors rendered as orthogonal edges with colors/patterns from `CONNECTOR_STYLES`
- Labels positioned below icons, matching the Visio rendering layout
- Nested boundary support via mxGraph's `parent` cell relationships
- Output readable by draw.io Desktop, VS Code draw.io extension, and diagrams.net

### `visio_engine.py` (~715 lines)

Microsoft Visio COM automation + python-vsdx fallback:
- **COM rendering** (primary): `_render_com()` creates a Visio document via `win32com.client`
  - SVG icon import at 1:1 aspect with label positioning
  - Boundary drawing per Microsoft Architecture Center CSS conventions
  - Dynamic connector routing with right-angle style and arrow endpoints
  - Numbered workflow step circles (green #107C10 with white bold text)
  - White background page, auto page sizing, theme stripping
- **python-vsdx fallback**: `_render_vsdx()` for headless environments without Visio
- **Critical rules**:
  - Always use named cells (never `CellsSRC` indices)
  - Never call `AutoSizeDrawing()` — manual page sizing
  - Always call `RemoveTheme()` after document creation
  - Y-axis flip: Visio uses bottom-up, layout uses top-down

### `waf_validator.py` (~530 lines)

Azure Well-Architected Framework validation:
- Checks against all 5 WAF pillars plus reference architecture alignment
- Severity levels: `critical` (−15), `warning` (−8), `info` (−3)
- **Smart multi-region detection**: Scans resource/boundary names for Azure region keywords (eastus, westeurope, etc.), recognizes Traffic Manager/Front Door as multi-region intent
- **Intelligent DB failover detection**: Detects paired databases of the same type, DB-to-DB connections (geo-replication), and boundary notes mentioning replication/failover
- **AZ detection**: Boundary types + name-based scanning for availability zone keywords
- **CI/CD detection**: Multiple resource types (`devops`, `github_actions`, `data_factory`) plus name-based detection ("pipeline", "ci/cd")
- Checks include: load balancer presence, Key Vault, managed identity, NSG/Firewall, private endpoints, DDoS, WAF on ingress, monitoring, caching, CDN
- Reference architecture alignment: private endpoints per PaaS, subnet segmentation, egress control
- Page annotation: findings are tagged with page number/name from affected resources
- Score: 100 minus severity-weighted deductions

### `caf_validator.py` (~383 lines)

Azure Cloud Adoption Framework validation:
- Checks against 7 CAF principles
- Severity levels: `critical` (−15), `warning` (−8), `info` (−2)
- **Naming Convention** — Validates against CAF prefix table (50+ resource types)
- **Resource Organization** — Resource group boundaries, subscription hierarchy
- **Network Topology** — Hub-spoke pattern, subnet segmentation, Bastion
- **Identity** — Entra ID, managed identity presence
- **Governance** — Azure Policy, tagging strategy
- **Security Baseline** — Defender for Cloud, Sentinel
- **Management** — Monitoring, Log Analytics

### `reference_architectures.py` (~3,750 lines)

Built-in reference architecture definitions:
- 5 hand-crafted architecture templates with position hints and workflow steps
- Microsoft Architecture Center visual standards (`MICROSOFT_STANDARDS` dataclass)
- `AZURE_DIAGRAM_COLORS` — Color palette constants per published Architecture Center SVGs
- 206-entry architecture catalog from Azure Architecture Center browse page
- 40 cloud design patterns and 6 architecture styles with metadata

---

## Stencils

The `stencils/` directory contains Azure icon packs (~81 MB, excluded from git):

- **Azure Public Service Icons** — `stencils/Azure_Public_Service_Icons/Icons/` (97+ SVGs across 28 categories)
- **Entra Icons** — `stencils/Entra_Icons/` (7 SVGs)
- **Fabric Icons** — `stencils/Fabric_Icons/` (28 SVGs)

Download instructions in the root [README.md](../../README.md).

---

## Running Standalone

```powershell
# As MCP server (stdio transport):
.\.venv\Scripts\python.exe -m visio_mcp.server

# The Streamlit app spawns this automatically via mcp_client.py
```
