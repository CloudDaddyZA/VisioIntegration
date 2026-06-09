---
name: generate-azure-diagram
description: Generate an Azure architecture diagram from a natural-language description using the Visio MCP tools.
argument-hint: describe the workload (services, tiers, boundaries, connections)
agent: agent
tools: ['visio-azure/*']
---

# Generate an Azure architecture diagram

Build a production-quality Azure architecture diagram for the workload described below.

Workload: ${input:workload:e.g. a 3-tier web app with App Service, SQL Database, and Key Vault inside a VNet}

Follow this process:

1. Call `create_diagram` with a descriptive name.
2. Choose canonical Azure `resource_type` values from the shape catalog (use
   `list_azure_shapes` if unsure). Apply Cloud Adoption Framework naming prefixes
   (`vm-`, `app-`, `sql-`, `vnet-`, `snet-`, `kv-`, `st`, `aks-`, `cr`).
3. Add boundaries first (`add_boundary` for `resource_group`, `virtual_network`,
   `subnet`, etc.), then add resources with `add_azure_resource`, assigning each to
   its boundary via `group_id`.
4. Connect resources with `connect_resources`, using clear, labeled connectors that
   reflect real traffic/data flow.
5. Run `auto_layout` (tiered by default) so positions are computed for you.
6. Call `validate_waf` and briefly summarize the score and top findings.
7. Show the final `get_diagram_state` summary (resource, connection, and boundary
   counts) and ask whether to save.

Do not hardcode coordinates — let `auto_layout` and `group_id` placement handle
positioning. Prefer canonical resource types; common aliases (`aks`, `apim`, `vm`)
are resolved automatically.
