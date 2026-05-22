# Copilot Instructions — Azure Visio MCP

## Project Overview

This is an **MCP (Model Context Protocol) server** for creating production-quality Azure architecture diagrams. It exposes 31 tools, 8 resources, and 7 prompts via FastMCP (Python) and is consumed by:
- A **Streamlit web app** (`app/`)
- A **VS Code extension** with GitHub Copilot Chat participant `@azureVisio` (`vscode-extension/`)
- A **PyInstaller desktop app** (`desktop.spec`)

## Architecture

- **MCP Server**: `src/visio_mcp/server.py` — central tool hub
- **Data Models**: `src/visio_mcp/models.py` — Pydantic models (DiagramState, DiagramResource, Connection, BoundaryGroup)
- **State Manager**: `src/visio_mcp/diagram_state.py` — DiagramManager class
- **Renderers**: `visio_engine.py` (.vsdx via COM) and `drawio_engine.py` (.drawio XML)
- **Validators**: `waf_validator.py` (5 WAF pillars) and `caf_validator.py` (7 CAF principles)
- **Layout**: `layout_engine.py` — tiered/grid/grouped auto-layout
- **Catalog**: `azure_catalog.py` — 151 Azure resource shapes with SVG icon paths
- **References**: `reference_architectures.py` — 16 templates, 14 styles, 50 design patterns
- **Pricing**: `azure_sku_grounding.py` — live Azure Retail Prices API

## Key Conventions

### Resource Types
Always use the canonical `resource_type` from `AZURE_SHAPE_CATALOG` (e.g., `virtual_machine`, `app_service`, `sql_database`). Common aliases are resolved automatically (`aks` → `kubernetes_service`, `apim` → `api_management`, `vm` → `virtual_machine`).

### CAF Naming
Resources should follow Cloud Adoption Framework naming prefixes:
- VMs: `vm-`, App Services: `app-`, SQL: `sql-`, VNets: `vnet-`, Subnets: `snet-`
- Key Vault: `kv-`, Storage: `st`, AKS: `aks-`, Container Registry: `cr`

### Boundary Types
Use: `resource_group`, `virtual_network`, `subnet`, `subscription`, `region`, `availability_zone`, `security_boundary`

### Positions & Layout
- Coordinates are in inches (Visio page units). Default page: 11×8.5 inches.
- Let `auto_layout` handle positioning — don't hardcode unless replicating a reference architecture.
- When adding resources to a boundary with `group_id`, positions auto-calculate.

### Properties Parameter
The `properties` parameter in `add_azure_resource` and `add_boundary` accepts `str | dict | None`. If passing a dict, it will be auto-serialized. When None/omitted, no custom properties are set.

### Output Formats
- `.vsdx` — requires Microsoft Visio installed (COM automation) or falls back to `python-vsdx`
- `.drawio` — always available, generates mxGraph XML with embedded Azure SVG icons

## Build & Run

```powershell
# Activate virtualenv
.\.venv\Scripts\Activate.ps1

# Run MCP server standalone
python -m visio_mcp.server

# Run Streamlit app
streamlit run app/streamlit_app.py

# Compile VS Code extension
cd vscode-extension && npm run compile

# Run tests
python -m pytest tests/ -v
```

## MCP Tools (31)

### Diagram CRUD
- `create_diagram` — Initialize a new diagram
- `add_azure_resource` — Add a resource (type, name, position, group_id, properties)
- `add_boundary` — Add a boundary group (type, name, parent_id)
- `connect_resources` — Connect two resources with a labeled connector
- `assign_resource_to_boundary` — Move a resource into a boundary
- `remove_resource` / `remove_boundary` — Delete elements

### Layout & State
- `auto_layout` — Apply tiered/grid/grouped layout
- `get_diagram_state` — Return full diagram JSON
- `get_diagram_standards` — Visual standards reference

### Validation
- `validate_waf` — Score against Well-Architected Framework pillars
- `validate_caf` — Check Cloud Adoption Framework naming
- `suggest_architecture_improvements` — AI-powered recommendations
- `get_waf_tips` — Per-resource-type WAF guidance

### Reference Architectures
- `list_reference_archs` — List 16 available templates
- `apply_reference_architecture` — Apply a template (with merge mode)
- `get_reference_arch_details` — Get template metadata

### Architecture Knowledge
- `suggest_architecture_style` — Recommend style from description
- `get_architecture_style_detail` — Style deep-dive
- `suggest_design_patterns` — Pattern recommendations
- `get_design_pattern_detail` — Pattern deep-dive
- `browse_architecture_catalog` — Browse 206 architectures
- `search_arch_catalog` / `get_arch_catalog_entry` — Search/get catalog entries

### SKU & Pricing
- `query_azure_pricing` — Live Azure Retail Prices API query
- `compare_azure_skus` — Side-by-side SKU comparison
- `get_sku_recommendations` — Workload-based tier guidance

### Rendering
- `save_diagram` — Render to .vsdx or .drawio
- `list_azure_shapes` — Browse shape catalog with filters

### Import
- `import_vsdx` — Import existing Visio files
- `import_image` — AI-powered image-to-architecture conversion
- `import_pricing_estimate` — Import Azure Pricing Calculator URL

## File Locations

| What | Where |
|------|-------|
| MCP Server entry | `src/visio_mcp/__main__.py` |
| All tools | `src/visio_mcp/server.py` |
| Data models | `src/visio_mcp/models.py` |
| Azure shapes (151) | `src/visio_mcp/azure_catalog.py` |
| SVG icons | `src/visio_mcp/stencils/` |
| Streamlit app | `app/streamlit_app.py` |
| VS Code extension | `vscode-extension/src/extension.ts` |
| Chat participant | `vscode-extension/src/chatParticipant.ts` |
| Tests | `tests/` |
| PyInstaller spec | `desktop.spec` |
