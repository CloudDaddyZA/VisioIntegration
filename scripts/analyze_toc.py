"""Show top-level TOC structure and find all architecture entries."""
import urllib.request
import json

url = 'https://learn.microsoft.com/en-us/azure/architecture/toc.json'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
data = json.loads(urllib.request.urlopen(req).read().decode())

# Show top-level items
print("=== TOP-LEVEL TOC ITEMS ===")
for i, item in enumerate(data['items']):
    title = item.get('toc_title', '(no title)')
    href = item.get('href', '')
    children_count = len(item.get('children', []))
    print(f"  {i}. {title} [href={href}] children={children_count}")

# Now do a comprehensive extraction of ALL items in the entire TOC
# that look like architecture entries (based on file path patterns)
all_entries = []

ARCH_PATTERNS = [
    'example-scenario/', 'reference-architectures/', 'solution-ideas/',
    'ai-ml/architecture/', 'ai-ml/idea/', 'databases/architecture/',
    'databases/idea/', 'hybrid/', 'virtual-machines/', 'high-availability/',
    'mainframe/', 'industries/', 'analytics/architecture/',
    'microservices/', 'serverless/', 'landing-zones/',
    'guide/sas/', 'guide/aks/', 'guide/devsecops/',
    'guide/hadoop/', 'guide/iot/', 'guide/security/',
    'web-apps/', 'networking/guide/',
]

def extract_all(node, path="", results=None):
    if results is None:
        results = []
    
    href = node.get('href', '')
    title = node.get('toc_title', '')
    has_children = bool(node.get('children'))
    
    if href and not has_children:
        # Skip external links
        if not (href.startswith('/azure/') and '/architecture/' not in href):
            if not href.startswith('/security/'):
                results.append({
                    'title': title,
                    'href': href,
                    'display_name': node.get('displayName', ''),
                    'path': path,
                })
    
    if has_children:
        for child in node['children']:
            child_title = child.get('toc_title', '')
            extract_all(child, f"{path} > {child_title}" if path else child_title, results)
    
    return results

all_items = []
for item in data['items']:
    extract_all(item, item.get('toc_title', ''), all_items)

# Deduplicate
seen = set()
unique = []
for e in all_items:
    if e['href'] not in seen:
        seen.add(e['href'])
        unique.append(e)

print(f"\nTotal unique leaf nodes in TOC: {len(unique)}")

# Classify
architectures = [e for e in unique if any(p in e['href'] for p in [
    'example-scenario/', 'reference-architectures/', 'ai-ml/architecture/',
    'hybrid/', 'virtual-machines/', 'high-availability/',
    'mainframe/', 'industries/', 'analytics/architecture/',
    'databases/architecture/', 'microservices/',
])]
solutions = [e for e in unique if 'solution-ideas/' in e['href'] or 'ai-ml/idea/' in e['href'] or 'databases/idea/' in e['href']]
best_practices = [e for e in unique if 'best-practices/' in e['href']]
patterns = [e for e in unique if 'patterns/' in e['href']]
guides = [e for e in unique if 'guide/' in e['href']]

print(f"  Architectures: {len(architectures)}")
print(f"  Solution Ideas: {len(solutions)}")
print(f"  Best Practices: {len(best_practices)}")
print(f"  Design Patterns: {len(patterns)}")
print(f"  Guides: {len(guides)}")

# Show AI+ML entries
ai_entries = [e for e in unique if 'ai-ml/' in e['href']]
print(f"\n=== AI+ML entries ({len(ai_entries)}) ===")
for e in ai_entries:
    print(f"  {e['title']}: {e['href']}")

# Browse-like entries (architectures + solutions, excluding patterns)
browse = architectures + solutions
browse_unique = list({e['href']: e for e in browse}.values())
print(f"\n=== BROWSE-LIKE (arch + solution, no patterns): {len(browse_unique)} ===")
