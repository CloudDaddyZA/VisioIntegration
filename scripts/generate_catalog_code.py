"""Generate Python code for AZURE_ARCHITECTURE_CATALOG from JSON catalog."""
import json
import textwrap
import re

with open('output/azure_architecture_catalog.json', encoding='utf-8') as f:
    catalog = json.load(f)

# Category normalization map
CAT_NORMALIZE = {
    'analytics': 'Analytics',
    'databases': 'Databases', 
    'hybrid': 'Hybrid + Multicloud',
    'identity': 'Identity',
    'iot': 'Internet of Things',
    'mobile': 'Mobile',
    'security': 'Security',
    'web': 'Web',
    'azure-virtual-desktop': 'Virtual Desktop',
    'management-and-governance': 'Management + Governance',
    'ai-machine-learning': 'AI + Machine Learning',
    'compute': 'Compute',
    'containers': 'Containers',
    'devops': 'DevOps',
    'developer-tools': 'Developer Tools',
    'integration': 'Integration',
    'migration': 'Migration',
    'networking': 'Networking',
    'media': 'Media',
    'featured': 'Featured',
    'storage': 'Storage',
    'hybrid-multicloud': 'Hybrid + Multicloud',
}

lines = []
lines.append('''
# ═══════════════════════════════════════════════════════════════════
# AZURE ARCHITECTURE CATALOG — 206 reference architectures & solutions
# ═══════════════════════════════════════════════════════════════════
# Extracted from https://learn.microsoft.com/en-us/azure/architecture/browse/
# Each entry has: key, name, summary, source_url, type, categories, products

@dataclass
class AzureArchitectureEntry:
    """A reference architecture or solution idea from Azure Architecture Center."""
    key: str
    name: str
    summary: str
    source_url: str
    entry_type: str   # Architecture, Reference Architecture, Solution Idea, Best Practice
    categories: list[str]
    products: list[str]


AZURE_ARCHITECTURE_CATALOG: dict[str, AzureArchitectureEntry] = {''')

for entry in catalog:
    key = entry['key']
    name = entry['name'].replace("'", "\\'").replace('"', '\\"')
    summary = entry['summary'].replace("'", "\\'").replace('"', '\\"')
    # Truncate very long summaries
    if len(summary) > 200:
        summary = summary[:197] + '...'
    source_url = entry['source_url']
    entry_type = entry['type']
    
    # Normalize categories
    cats = []
    for c in entry.get('categories', []):
        c = c.strip('"').strip("'")
        if c in CAT_NORMALIZE:
            cats.append(CAT_NORMALIZE[c])
        else:
            cats.append(c)
    cats = list(dict.fromkeys(cats))  # dedupe preserving order
    
    # Limit products to top 5, strip quotes
    products = [p.strip('"').strip("'") for p in entry.get('products', [])[:5]]
    
    lines.append(f'    "{key}": AzureArchitectureEntry(')
    lines.append(f'        key="{key}",')
    lines.append(f'        name="{name}",')
    lines.append(f'        summary="{summary}",')
    lines.append(f'        source_url="{source_url}",')
    lines.append(f'        entry_type="{entry_type}",')
    lines.append(f'        categories={cats},')
    lines.append(f'        products={products},')
    lines.append(f'    ),')

lines.append('}')
lines.append('')

# Add helper functions
lines.append('''
def list_architecture_catalog(category: str = "", entry_type: str = "") -> list[dict[str, Any]]:
    """List architectures from the Azure Architecture Catalog, optionally filtered."""
    results = []
    for entry in AZURE_ARCHITECTURE_CATALOG.values():
        if category and not any(category.lower() in c.lower() for c in entry.categories):
            continue
        if entry_type and entry_type.lower() not in entry.entry_type.lower():
            continue
        results.append({
            "key": entry.key,
            "name": entry.name,
            "summary": entry.summary,
            "source_url": entry.source_url,
            "type": entry.entry_type,
            "categories": entry.categories,
        })
    return results


def search_architecture_catalog(query: str) -> list[dict[str, Any]]:
    """Search the architecture catalog by name, summary, category, or products."""
    q = query.lower()
    scored: list[tuple[int, AzureArchitectureEntry]] = []

    for entry in AZURE_ARCHITECTURE_CATALOG.values():
        score = 0
        name_lower = entry.name.lower()
        summary_lower = entry.summary.lower()

        # Exact name match
        if q in name_lower:
            score += 10
        # Key match
        if q.replace(" ", "_") in entry.key:
            score += 8
        # Word matches in name
        for word in q.split():
            if len(word) > 2 and word in name_lower:
                score += 3
            if len(word) > 3 and word in summary_lower:
                score += 1
        # Category match
        for cat in entry.categories:
            if q in cat.lower():
                score += 5
        # Product match
        for prod in entry.products:
            prod_name = prod.replace("-", " ")
            if q in prod_name:
                score += 3

        if score > 0:
            scored.append((score, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {
            "key": entry.key,
            "name": entry.name,
            "score": score,
            "summary": entry.summary,
            "source_url": entry.source_url,
            "type": entry.entry_type,
            "categories": entry.categories,
            "products": entry.products,
        }
        for score, entry in scored[:15]
    ]


def get_architecture_catalog_entry(key: str) -> dict[str, Any] | None:
    """Get full details for an architecture catalog entry."""
    entry = AZURE_ARCHITECTURE_CATALOG.get(key)
    if not entry:
        return None
    return {
        "key": entry.key,
        "name": entry.name,
        "summary": entry.summary,
        "source_url": entry.source_url,
        "type": entry.entry_type,
        "categories": entry.categories,
        "products": entry.products,
    }
''')

output = '\n'.join(lines)
with open('output/catalog_code.py', 'w', encoding='utf-8') as f:
    f.write(output)

print(f"Generated {len(catalog)} entries")
print(f"Output: output/catalog_code.py ({len(output)} chars)")
