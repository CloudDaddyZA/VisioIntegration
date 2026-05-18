# tests/ — Test Suite

Integration and unit tests for the Visio Azure MCP server.

---

## Test Files

### `test_reference_arch.py`

Tests the 12 built-in reference architecture templates:

- Validates that `apply_reference_architecture` produces the expected resource count,
  boundary count, and connection count for each template
- Checks resource type correctness and CAF-aligned naming
- Verifies boundary nesting (e.g., subnets inside VNets inside resource groups)
- Tests workflow step ordering and connection labels
- Tests merge mode (`merge=True`) to combine architectures

### `test_ai_landing_zone.py`

Focused tests for the `ai_landing_zone` reference architecture:

- Verifies AI-specific resources: Azure OpenAI, AI Search, Cognitive Services
- Validates hub-spoke network topology with correct boundary hierarchy
- Checks security components: Key Vault, managed identity, private endpoints
- Validates WAF and CAF scores are above threshold after template application

### `test_sku_grounding.py`

Tests the Azure SKU grounding module:

- Verifies Azure Retail Prices API connectivity and response parsing
- Tests SKU price comparison (sorted cheapest-first with monthly estimates)
- Validates VM family recommendation logic (workload → family mapping)
- Tests App Service / AKS / database reference data retrieval

---

## Running Tests

```powershell
# All tests:
.\.venv\Scripts\python.exe -m pytest tests/ -v

# Specific test file:
.\.venv\Scripts\python.exe -m pytest tests/test_reference_arch.py -v

# With coverage:
.\.venv\Scripts\python.exe -m pytest tests/ --cov=src/visio_mcp --cov-report=term-missing
```

---

## Adding Tests

1. Create a new file `tests/test_<feature>.py`
2. Import from `src/visio_mcp/`:
   ```python
   from visio_mcp.diagram_state import DiagramManager
   from visio_mcp.waf_validator import WafValidator
   from visio_mcp.caf_validator import CafValidator
   from visio_mcp.layout_engine import LayoutEngine
   from visio_mcp.azure_catalog import AZURE_SHAPE_CATALOG, resolve_alias
   ```
3. Use `DiagramManager()` to build diagrams programmatically:
   ```python
   def test_example():
       mgr = DiagramManager()
       mgr.new_diagram("Test")
       mgr.add_resource("app_service", "app-web-prod-001")
       mgr.add_resource("sql_database", "sqldb-app-prod-001")
       mgr.add_connection("res-...", "res-...", label="SQL")

       # Validate
       waf = WafValidator().validate(mgr.state)
       assert waf.score >= 0
   ```

Tests do **not** require Microsoft Visio to be installed — they validate
the in-memory diagram state, layout, and validation logic. Only `save_diagram`
with `format="vsdx"` requires a Windows machine with Visio. The `format="drawio"`
output works on any platform without Visio.
