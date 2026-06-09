---
name: azure-diagram-authoring
description: Author production-quality Azure architecture diagrams with the Visio MCP server. Use when the user wants to create, edit, validate, or export an Azure architecture diagram (.vsdx, .drawio, or .mmd), apply a reference architecture, or check a design against the Well-Architected Framework (WAF) or Cloud Adoption Framework (CAF).
---

# Azure diagram authoring

This skill guides building correct, standards-aligned Azure architecture diagrams
using the `visio-azure` MCP server. It encodes the project's conventions so diagrams
come out right the first time.

## When to use

Use this skill when the user asks to:

- Create an Azure architecture diagram from a description or business goal.
- Apply a built-in reference architecture (e.g. AI Landing Zone, Microservices on AKS).
- Validate a design against WAF (5 pillars) or CAF (7 principles).
- Export a diagram to `.vsdx` (Visio), `.drawio` (draw.io), or `.mmd` (Mermaid).
- Import an existing diagram (`.vsdx`), a screenshot, or an Azure Pricing Calculator URL.

## Prerequisite

The `visio-azure` MCP server must be connected. A sample config lives at
[.vscode/mcp.json](../../../.vscode/mcp.json). If the server's tools are not
available, ask the user to add and trust it first.

## Authoring workflow

1. **Create** the diagram with `create_diagram` (give it a descriptive name).
2. **Boundaries first.** Add containers with `add_boundary` before resources.
   Valid boundary types: `resource_group`, `virtual_network`, `subnet`,
   `subscription`, `region`, `availability_zone`, `security_boundary`.
3. **Add resources** with `add_azure_resource`. Use canonical `resource_type`
   values from the catalog (call `list_azure_shapes` to browse). Assign each
   resource to its boundary via `group_id` so positions auto-calculate.
4. **Connect** resources with `connect_resources`, using labeled connectors that
   reflect real traffic/data flow.
5. **Lay out** with `auto_layout` (`tiered` | `grid` | `grouped`). Never hardcode
   coordinates unless replicating a specific reference architecture.
6. **Validate** with `validate_waf` and `validate_caf`; summarize findings and offer
   `suggest_architecture_improvements`.
7. **Save** only when asked, via `save_diagram` (`.vsdx`, `.drawio`, or `.mmd`).

## Conventions to enforce

- **Canonical resource types.** Prefer catalog names (`virtual_machine`,
  `app_service`, `sql_database`, `kubernetes_service`, `api_management`). Common
  aliases (`vm`, `aks`, `apim`) are resolved automatically.
- **CAF naming prefixes.** `vm-`, App Services `app-`, SQL `sql-`, VNets `vnet-`,
  subnets `snet-`, Key Vault `kv-`, Storage `st`, AKS `aks-`, Container Registry `cr`.
- **Coordinates** are in inches on an 11×8.5 page; let `auto_layout` and `group_id`
  handle placement.
- **`properties`** on `add_azure_resource` / `add_boundary` accepts a string, a dict
  (auto-serialized), or may be omitted.

## Reference architectures

To start from a template instead of scratch: `list_reference_archs` →
`get_reference_arch_details` → `apply_reference_architecture` (use merge mode if a
diagram already exists), then `auto_layout` and validate.

## Output formats

| Extension | Renderer | Availability |
|-----------|----------|--------------|
| `.vsdx`   | Visio COM (falls back to `python-vsdx`) | Requires Visio for full fidelity |
| `.drawio` | mxGraph XML with embedded Azure SVG icons | Always available |
| `.mmd`    | Mermaid flowchart text (nested subgraphs for boundaries) | Always available |
