import sys
sys.path.insert(0, "src")
from visio_mcp.azure_catalog import AZURE_SHAPE_CATALOG, SVG_ICON_MAP, resolve_alias, search_shapes, get_shape

print(f"Shapes: {len(AZURE_SHAPE_CATALOG)}")
print(f"Icons: {len(SVG_ICON_MAP)}")

# Test alias resolution
print("\n--- Alias Resolution ---")
for alias in ["aks", "apim", "vm", "adx", "acr", "vnet", "cosmosdb", "kv", "sql", "aci", "aca"]:
    resolved = resolve_alias(alias)
    shape = AZURE_SHAPE_CATALOG.get(resolved)
    print(f"  {alias} -> {resolved}: {'OK' if shape else 'MISSING'} ({shape.display_name if shape else '?'})")

# Test get_shape with aliases
print("\n--- get_shape with aliases ---")
for key in ["aks", "data_explorer", "kubernetes_service"]:
    shape = get_shape(key)
    print(f"  get_shape('{key}'): {shape.display_name if shape else 'NOT FOUND'}")

# Test search with aliases
print("\n--- search with aliases ---")
for term in ["aks", "adx", "apim", "data explorer", "kubernetes"]:
    results = search_shapes(term)
    keys = [r.key for r in results]
    print(f"  search('{term}'): {keys}")
