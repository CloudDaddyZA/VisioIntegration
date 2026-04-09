# visio_mcp — MCP Server Package

The core MCP server that exposes 21 tools for Azure architecture diagram creation, validation, and Visio rendering.

## Module Overview

| Module | Lines | Purpose |
|--------|------:|---------|
| [`server.py`](server.py) | 1,582 | FastMCP server — 21 tools, 5 resources, 5 prompt templates |
| [`reference_architectures.py`](reference_architectures.py) | 929 | 5 Azure Architecture Center templates with hand-tuned position/boundary hints |
| [`azure_catalog.py`](azure_catalog.py) | 882 | 70+ Azure resource types, 709 SVG icon path mappings, boundary/connector style defs |
| [`visio_engine.py`](visio_engine.py) | 613 | Visio COM automation — SVG import, connectors, MS visual standards, python-vsdx fallback |
| [`waf_validator.py`](waf_validator.py) | 430 | Well-Architected Framework validator (5 pillars, 6 check methods) |
| [`caf_validator.py`](caf_validator.py) | 350 | Cloud Adoption Framework validator (7 principles, 7 check methods) |
| [`layout_engine.py`](layout_engine.py) | 229 | Auto-layout engine (tiered, grid, grouped) with position hint support |
| [`diagram_state.py`](diagram_state.py) | 172 | `DiagramManager` — in-memory CRUD for resources, connections, boundaries |
| [`models.py`](models.py) | 106 | Pydantic data models — `DiagramState`, `DiagramResource`, `Connection`, `BoundaryGroup`, validators |

## Server Tools (21)

### Diagram CRUD

| Tool | Args | Description |
|------|------|-------------|
| `create_diagram` | `name` | Creates a new empty diagram, resets state |
| `add_azure_resource` | `resource_type`, `display_name`, `resource_id?`, `x?`, `y?`, `group_id?`, `properties?` | Adds a resource (validates against catalog) |
| `add_boundary` | `boundary_type`, `display_name`, `boundary_id?`, `x?`, `y?`, `width?`, `height?`, `parent_id?` | Adds a boundary container |
| `connect_resources` | `source_id`, `target_id`, `label?`, `connection_type?`, `style?` | Creates a labeled connection |
| `assign_resource_to_boundary` | `resource_id`, `boundary_id` | Moves a resource into a boundary |
| `remove_resource` | `resource_id` | Removes resource and its connections |
| `remove_boundary` | `boundary_id` | Removes boundary, unlinks children |

### Layout & Rendering

| Tool | Args | Description |
|------|------|-------------|
| `auto_layout` | `strategy` (tiered/grid/grouped) | Applies automatic layout, re-uses stored hints if available |
| `save_diagram` | `output_path`, `stencil_dir?`, `icons_root?` | Renders to `.vsdx` via Visio COM |

### Reference Architectures

| Tool | Args | Description |
|------|------|-------------|
| `apply_reference_architecture` | `architecture_key`, `name_override?` | Builds a complete diagram from a template |
| `list_reference_archs` | `category?` | Lists available templates |
| `get_reference_arch_details` | `architecture_key` | Full template inspection (resources, boundaries, connections, workflow steps) |

### Validation

| Tool | Args | Description |
|------|------|-------------|
| `validate_waf` | `pillar?` | WAF 5-pillar validation, returns score 0-100 |
| `validate_caf` | `principle?` | CAF 7-principle validation, returns score 0-100 |
| `suggest_architecture_improvements` | — | Combined WAF+CAF analysis with missing resource suggestions |
| `get_waf_tips` | `resource_type` | Per-resource WAF considerations |

### Import

| Tool | Args | Description |
|------|------|-------------|
| `import_vsdx` | `file_path`, `assess_waf?`, `assess_caf?` | Parses existing `.vsdx` via Visio COM, fuzzy-matches shapes to catalog |
| `import_image` | `file_path` | Converts image to Azure diagram. Raster (PNG/JPG/BMP/GIF/WEBP/TIFF) → GPT-4o Vision; SVG → text analysis |

### Reference

| Tool | Args | Description |
|------|------|-------------|
| `list_azure_shapes` | `category?`, `search?` | Browse/search the resource catalog |
| `get_diagram_state` | — | Returns current diagram summary (counts, resource list) |
| `get_diagram_standards` | — | Returns MS color palette, icon rules, layout conventions |

## Data Models (models.py)

```
DiagramState
├── name: str
├── resources: dict[str, DiagramResource]
│   ├── id, resource_type, display_name
│   ├── position: Position (x, y)
│   ├── size: Size (width, height)
│   ├── properties: dict
│   └── group_id: Optional[str]  → boundary reference
├── connections: dict[str, Connection]
│   ├── id, source_id, target_id
│   ├── label, connection_type, style
├── boundaries: dict[str, BoundaryGroup]
│   ├── id, boundary_type, display_name
│   ├── position, size
│   ├── parent_id: Optional[str]  → parent boundary
│   └── properties: dict
├── page_width, page_height
└── _layout_hints, _boundary_hints  (private, from reference architectures)
```

## DiagramManager API (diagram_state.py)

| Method | Returns | Description |
|--------|---------|-------------|
| `new_diagram(name)` | `DiagramState` | Resets to fresh state |
| `add_resource(resource_type, display_name, ...)` | `DiagramResource` | Auto-generates ID if not given |
| `remove_resource(resource_id)` | `bool` | Also removes related connections |
| `move_resource(resource_id, x, y)` | `bool` | Updates position |
| `add_connection(source_id, target_id, ...)` | `Connection` | Raises `ValueError` if endpoints missing |
| `remove_connection(connection_id)` | `bool` | — |
| `add_boundary(boundary_type, display_name, ...)` | `BoundaryGroup` | Auto-generates ID if not given |
| `remove_boundary(boundary_id)` | `bool` | Unlinks children |
| `assign_to_boundary(resource_id, boundary_id)` | `bool` | Sets `resource.group_id` |
| `get_resources_in_boundary(boundary_id)` | `list` | Query helper |
| `get_connections_for_resource(resource_id)` | `list` | Query helper |
| `summary()` | `dict` | Name, counts, resource/connection/boundary lists |

## Visio Engine (visio_engine.py)

The `VisioEngine` class renders a `DiagramState` to `.vsdx` via Visio COM automation.

### Rendering Pipeline

1. **Kill orphaned VISIO.EXE** — `taskkill /F /IM VISIO.EXE`
2. **Create document** — `Dispatch("Visio.Application")`, new doc, set `AlertResponse=6`
3. **Remove theme** — `doc.RemoveTheme()` (prevents style overrides)
4. **Calculate page size** — Bounding box of all elements + margins
5. **White background** — Separate background page (`VisioBG`)
6. **Enable right-angle routing** — `RouteStyle=1` on page sheet
7. **Draw boundaries** — Sorted by area (largest first) for correct z-ordering
8. **Draw resources** — Strategy: (1) `.vssx` stencil master → (2) SVG import → (3) colored rectangle
9. **Draw connections** — Dynamic connectors with named-cell gluing, arrows, step circles
10. **Add title** — Top of page
11. **Save** — `doc.SaveAs(path)` (never call `AutoSizeDrawing`)

### Visual Standards (from actual MS Architecture Center SVGs)

```
Boundaries:  fill #FFFFFF/#F2F2F2, opacity 55-79%, border #7F7F7F dashed 0.5pt
Connectors:  #000000, 1pt, right-angle, arrow endpoints
Step circles: #107C10 (green) fill, white bold Segoe UI number, no stroke
Labels:      #000000 Segoe UI 9pt, boundary labels #5B9BD5 bold
```

### Critical COM Rules

- **Named cells only**: `shape.Cells("PinX")` — never `CellsSRC` indices
- **Never `AutoSizeDrawing()`** — corrupts page geometry
- **Always `RemoveTheme()`** — themes override explicit colors
- **Y-flip**: `page_height - y` for all coordinates (Visio Y is bottom-up)

## Azure Catalog (azure_catalog.py)

- `AZURE_SHAPE_CATALOG`: 70+ `AzureShapeInfo` entries with stencil names, SVG paths, icon colors, WAF tips
- `SVG_ICON_MAP`: 74 resource type → SVG file path mappings
- `BOUNDARY_STYLES`: 8 boundary types with default colors/patterns
- `CONNECTOR_STYLES`: 6 connection types with colors/patterns/weights
- `resolve_svg_path(resource_type, icons_root)`: Resolves the SVG file path for a resource type
- `get_icons_root()`: Returns the stencils icons directory path

## Validators

### WAF Validator (waf_validator.py)

Checks 6 areas: Reliability, Security, Cost Optimization, Operational Excellence, Performance Efficiency, Reference Architecture Alignment. Scoring: critical = -15, warning = -8, info = -3, from 100.

### CAF Validator (caf_validator.py)

Checks 7 principles: Naming, Resource Organization, Network Topology, Identity, Governance, Security Baseline, Management. Includes `CAF_NAMING_PREFIXES` dict with ~40 expected prefixes. Scoring: critical = -15, warning = -8, info = -2, from 100.

## Reference Architectures (reference_architectures.py)

Each `ReferenceArchitecture` dataclass contains:
- **Boundary templates** — hierarchy with parent/child relationships
- **Resource templates** — typed resources with group assignments
- **Connection templates** — labeled connections with workflow step numbers
- **Layout hints** — `dict[str, tuple[float, float]]` — exact (x, y) per resource
- **Boundary hints** — `dict[str, tuple[float, float, float, float]]` — exact (x, y, w, h) per boundary
- **WAF/CAF notes** — per-pillar/principle commentary
- **Workflow steps** — numbered descriptions

## Stencils

The `stencils/Azure_Public_Service_Icons/` directory contains **709 official Azure SVG icons** across 28 categories, sourced from [Microsoft Azure architecture icons](https://learn.microsoft.com/en-us/azure/architecture/icons/).

See [`stencils/Azure_Public_Service_Icons/README.md`](stencils/Azure_Public_Service_Icons/README.md) for details.
