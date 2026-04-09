# tests/ — Integration Tests

Integration tests that exercise the MCP server tools end-to-end without needing a running server process. Tests call the tool functions directly from `visio_mcp.server`.

## Test Files

| File | Lines | Description |
|------|------:|-------------|
| [`test_reference_arch.py`](test_reference_arch.py) | 39 | Applies **all 5 reference architectures** in sequence and validates each with WAF + CAF |
| [`test_ai_landing_zone.py`](test_ai_landing_zone.py) | 344 | Full end-to-end test that builds an enterprise AI Landing Zone from scratch using individual MCP tools |

## Running

```powershell
cd d:\.github\VisioIntegration
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

Or run a specific test directly:
```powershell
.\.venv\Scripts\python.exe tests/test_ai_landing_zone.py
```

## test_reference_arch.py

Iterates over all reference architectures returned by `list_reference_archs()` and for each:
1. Calls `apply_reference_architecture(key)` — verifies resources, connections, and boundaries are created
2. Runs `validate_waf()` — prints score and finding count
3. Runs `validate_caf()` — prints score and finding count
4. Calls `get_diagram_state()` to verify state consistency

Validates: `baseline_foundry_chat`, `azure_landing_zone`, `baseline_web_app`, `ai_landing_zone`, `microservices_aks`

## test_ai_landing_zone.py

A comprehensive 12-step integration test that exercises 11 MCP tools:

| Step | Tools Used | What It Tests |
|------|-----------|---------------|
| 1. Create Diagram | `create_diagram` | New diagram initialization |
| 2. Shape Catalog | `list_azure_shapes` | Category filtering, search |
| 3. Boundaries | `add_boundary` | Management group → subscription → RGs → VNets → subnets (nested hierarchy) |
| 4. Resources | `add_azure_resource` | 36 resources across 4 tiers: networking, AI/ML, data, shared services + external actors |
| 5. Connections | `connect_resources` | 32 connections with typed flows: `data_flow`, `network`, `dependency`, `vpn_tunnel`, `reference` |
| 6. WAF Tips | `get_waf_tips` | Per-resource-type WAF considerations |
| 7. Auto-Layout | `auto_layout` | Tiered layout strategy |
| 8. State | `get_diagram_state` | Diagram summary verification |
| 9. WAF Validation | `validate_waf` | Full WAF audit with severity breakdown |
| 10. CAF Validation | `validate_caf` | Full CAF audit (naming, organization, governance) |
| 11. Improvements | `suggest_architecture_improvements` | AI improvement suggestions, critical issues, missing resources |
| 12. Save | `save_diagram` | Visio COM rendering to `.vsdx` (with timeout guard for CI environments) |

### Architecture Built

- **Boundaries**: Management group → Subscription → 4 resource groups → VNet → 3 subnets (6 nesting levels)
- **Resources**: 36 total including Firewall, App Gateway, Bastion, OpenAI, AI Search, Cognitive Services, Machine Learning, Cosmos DB, SQL Database, Redis, Key Vault, Defender for Cloud, Sentinel, and more
- **Connections**: 32 typed connections modeling data flows, network paths, dependencies, and monitoring
- **Naming**: All resources use CAF-aligned naming conventions

## Notes

- Tests import directly from `visio_mcp.server` — no running server process required
- The save step in `test_ai_landing_zone.py` requires Visio COM (Windows + Microsoft Visio installed)
- A 60-second timeout guard wraps the save operation to prevent CI hangs if Visio shows a dialog
- Tests use `sys.path.insert(0, ...)` to locate the `src/` package
