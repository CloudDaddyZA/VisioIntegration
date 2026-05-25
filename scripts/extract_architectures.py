"""Extract all reference architectures from Azure Architecture Center TOC."""
import urllib.request
import json
import os

BASE_URL = "https://learn.microsoft.com/en-us/azure/architecture/"

# Paths that indicate browsable architectures / solution ideas
ARCH_PATH_PREFIXES = (
    'example-scenario/', 'reference-architectures/', 'solution-ideas/',
    'hybrid/', 'ai-ml/', 'databases/architecture/', 'databases/idea/',
    'microservices/', 'virtual-machines/', 'high-availability/',
    'analytics/', 'industries/', 'mainframe/', 'landing-zones/',
    'guide/sas/', 'guide/aks/', 'guide/devsecops/',
    'serverless/', 'networking/', 'web-apps/',
)

# Explicitly skip non-architecture docs (guides, overview pages, etc.)
SKIP_SUFFIXES = (
    '-start-here', '-get-started', 'get-started', '/index',
    'start-here', 'container-get-started', 'database-get-started',
)

def find_node(items, title_match):
    for item in items:
        if item.get('toc_title', '') == title_match:
            return item
        if 'children' in item:
            r = find_node(item['children'], title_match)
            if r:
                return r
    return None

def find_all_nodes(items, title_match):
    """Find ALL nodes matching the title (not just first)."""
    results = []
    for item in items:
        if item.get('toc_title', '') == title_match:
            results.append(item)
        if 'children' in item:
            results.extend(find_all_nodes(item['children'], title_match))
    return results

def extract_all_leaf(node, category, section_type, results):
    href = node.get('href', '')
    has_children = bool(node.get('children'))
    
    if href and not has_children:
        # Skip external links outside architecture center
        if href.startswith('/azure/') and '/architecture/' not in href:
            return
        if href.startswith('/security/'):
            return
        results.append({
            'title': node.get('toc_title', ''),
            'href': href,
            'category': category,
            'type': section_type,
            'display_name': node.get('displayName', '')
        })
    
    if has_children:
        for child in node['children']:
            extract_all_leaf(child, category, section_type, results)

def extract_all_from_tree(node, category, results, depth=0):
    """Extract ALL architecture-like entries from entire category tree."""
    href = node.get('href', '')
    has_children = bool(node.get('children'))
    title = node.get('toc_title', '')
    
    if href and not has_children:
        # Skip external links
        if href.startswith('/azure/') and '/architecture/' not in href:
            pass
        elif href.startswith('/security/'):
            pass
        elif any(href.endswith(s) for s in SKIP_SUFFIXES):
            pass
        else:
            # Determine type from path
            if 'solution-ideas/' in href:
                entry_type = 'Solution Idea'
            elif any(href.startswith(p) for p in ('example-scenario/', 'reference-architectures/',
                'hybrid/', 'databases/architecture/', 'virtual-machines/', 'high-availability/',
                'mainframe/', 'industries/', 'analytics/architecture/')):
                entry_type = 'Architecture'
            elif 'guide/' in href or 'best-practices/' in href:
                entry_type = 'Guide'
            else:
                entry_type = 'Architecture'
            
            results.append({
                'title': title,
                'href': href,
                'category': category,
                'type': entry_type,
                'display_name': node.get('displayName', '')
            })
    
    if has_children:
        for child in node['children']:
            extract_all_from_tree(child, category, results, depth + 1)

def main():
    url = 'https://learn.microsoft.com/en-us/azure/architecture/toc.json'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    data = json.loads(urllib.request.urlopen(req).read().decode())
    
    cats_node = find_node(data['items'], 'Azure categories')
    all_entries = []
    
    for cat in cats_node.get('children', []):
        cat_name = cat.get('toc_title', '')
        # Extract from the ENTIRE category tree
        extract_all_from_tree(cat, cat_name, all_entries)
    
    # Also extract from "Application architecture fundamentals" > Best practices
    best_practices = find_node(data['items'], 'Best practices for cloud applications')
    if best_practices:
        extract_all_from_tree(best_practices, 'Best Practices', all_entries)
    
    # Also get from Design patterns (already have these but for completeness)
    patterns = find_node(data['items'], 'Design patterns')
    if patterns:
        extract_all_from_tree(patterns, 'Design Patterns', all_entries)
    
    # Deduplicate by href
    seen = set()
    unique = []
    for e in all_entries:
        if e['href'] not in seen:
            seen.add(e['href'])
            unique.append(e)
    
    # Filter to only Architecture and Solution Idea types for the browse catalog
    browseable = [e for e in unique if e['type'] in ('Architecture', 'Solution Idea')]
    
    print(f"Total unique entries: {len(unique)}")
    print(f"Architecture + Solution Idea: {len(browseable)}")
    print(f"Guides: {len([e for e in unique if e['type'] == 'Guide'])}")
    print()
    
    for cat_name in sorted(set(e['category'] for e in browseable)):
        cat_entries = [e for e in browseable if e['category'] == cat_name]
        archs = [e for e in cat_entries if e['type'] == 'Architecture']
        sols = [e for e in cat_entries if e['type'] == 'Solution Idea']
        print(f"  {cat_name}: {len(archs)} archs, {len(sols)} solutions")
    
    print()
    for i, e in enumerate(browseable[:20]):
        print(f"  {i+1}. [{e['type']}] {e['title']}")
        print(f"     Category: {e['category']}, href: {e['href']}")
    
    # Save full list to JSON (all entries including guides)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'architectures_from_toc.json')
    with open(out_path, 'w') as f:
        json.dump(unique, f, indent=2)
    print(f"\nSaved {len(unique)} entries to {out_path}")

if __name__ == '__main__':
    main()
