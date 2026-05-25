import sys
sys.path.insert(0, "src")
from visio_mcp.azure_catalog import AZURE_SHAPE_CATALOG, SVG_ICON_MAP

print(f"Shapes: {len(AZURE_SHAPE_CATALOG)}")
print(f"Icons: {len(SVG_ICON_MAP)}")

# Check critical user-scenario resources
for key in ["data_explorer", "storage_account", "aks", "api_management",
            "cosmos_db", "sql_database", "virtual_machine", "app_service"]:
    shape = AZURE_SHAPE_CATALOG.get(key)
    icon = SVG_ICON_MAP.get(key)
    status = "OK" if shape and icon else ("NO SHAPE" if not shape else "NO ICON")
    name = shape.display_name if shape else "?"
    print(f"  {key}: {status} ({name})")

# Search test  
from visio_mcp.azure_catalog import search_shapes
for term in ["data explorer", "cosmos", "sql", "kubernetes", "api management"]:
    results = search_shapes(term)
    keys = [r.key for r in results]
    print(f"  search('{term}'): {keys}")
