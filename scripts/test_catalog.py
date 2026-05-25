"""Quick test of the architecture catalog integration."""
import sys
sys.path.insert(0, "src")

from visio_mcp.reference_architectures import (
    AZURE_ARCHITECTURE_CATALOG,
    list_architecture_catalog,
    search_architecture_catalog,
    get_architecture_catalog_entry,
    DESIGN_PATTERNS,
    ARCHITECTURE_STYLES,
    REFERENCE_ARCHITECTURES,
)

print(f"Catalog: {len(AZURE_ARCHITECTURE_CATALOG)} entries")
print(f"Patterns: {len(DESIGN_PATTERNS)}, Styles: {len(ARCHITECTURE_STYLES)}, RefArchs: {len(REFERENCE_ARCHITECTURES)}")

# Test browse by category
ai = list_architecture_catalog(category="AI")
print(f"AI category: {len(ai)} entries")
assert len(ai) > 10, f"Expected >10 AI entries, got {len(ai)}"

# Test browse by type
sols = list_architecture_catalog(entry_type="Solution Idea")
print(f"Solution Ideas: {len(sols)} entries")
assert len(sols) > 20, f"Expected >20 Solution Ideas, got {len(sols)}"

# Test combined filter
ai_sols = list_architecture_catalog(category="AI", entry_type="Solution Idea")
print(f"AI Solution Ideas: {len(ai_sols)} entries")

# Test search
r = search_architecture_catalog("kubernetes")
print(f"Search 'kubernetes': {len(r)} results")
assert len(r) > 0, "Expected kubernetes results"
print(f"  Top result: {r[0]['name']}")

r2 = search_architecture_catalog("machine learning")
print(f"Search 'machine learning': {len(r2)} results")

# Test get entry
first_key = list(AZURE_ARCHITECTURE_CATALOG.keys())[0]
e = get_architecture_catalog_entry(first_key)
assert e is not None, f"Expected entry for key '{first_key}'"
print(f"Entry '{first_key}': {e['name']}")
print(f"  Products: {e['products']}")
print(f"  Categories: {e['categories']}")

# Verify no quoted products
for key, entry in AZURE_ARCHITECTURE_CATALOG.items():
    for p in entry.products:
        assert '"' not in p, f"Product has inner quotes: {p} in {key}"
        assert "'" not in p, f"Product has inner quotes: {p} in {key}"

# Count by type
from collections import Counter
types = Counter(e.entry_type for e in AZURE_ARCHITECTURE_CATALOG.values())
print(f"\nBy type: {dict(types)}")

cats = Counter()
for e in AZURE_ARCHITECTURE_CATALOG.values():
    for c in e.categories:
        cats[c] += 1
print(f"Top categories: {cats.most_common(5)}")

# Test missing entry
missing = get_architecture_catalog_entry("nonexistent_key_xyz")
assert missing is None, "Expected None for missing key"

print("\nALL TESTS PASSED")
