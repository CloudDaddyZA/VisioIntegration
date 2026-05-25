"""
Fetch all browseable architecture YAML files from MicrosoftDocs/architecture-center
and extract metadata (title, summary, categories, products) into a single JSON catalog.
"""
import urllib.request
import json
import re
import sys
import time

BASE_RAW = "https://raw.githubusercontent.com/MicrosoftDocs/architecture-center/main/"
LEARN_BASE = "https://learn.microsoft.com/en-us/azure/architecture/"

def get_repo_tree():
    """Get the full file tree from GitHub."""
    url = "https://api.github.com/repos/MicrosoftDocs/architecture-center/git/trees/main?recursive=1"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    data = json.loads(urllib.request.urlopen(req).read().decode())
    return [item['path'] for item in data['tree'] if item['type'] == 'blob']

def get_toc_data():
    """Get the TOC JSON for title/path mapping."""
    url = 'https://learn.microsoft.com/en-us/azure/architecture/toc.json'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return json.loads(urllib.request.urlopen(req).read().decode())

def extract_toc_entries(data):
    """Recursively extract all leaf entries from the TOC."""
    entries = {}
    
    def walk(node, category=""):
        href = node.get('href', '')
        title = node.get('toc_title', '')
        
        if href and not node.get('children'):
            entries[href.rstrip('/')] = {
                'title': title,
                'href': href,
                'toc_category': category,
            }
        
        if node.get('children'):
            cat = title if title else category
            for child in node['children']:
                walk(child, cat)
    
    for item in data['items']:
        walk(item)
    
    return entries

def parse_yml_frontmatter(content):
    """Parse YAML architecture file metadata using regex (no PyYAML needed)."""
    result = {}
    
    # Extract name
    name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
    result['name'] = name_match.group(1).strip().strip('"\'') if name_match else ''
    
    # Extract summary (may be multiline)
    summary_match = re.search(r'^summary:\s*(.+?)(?:\n\S|\nthumbnail|\ncontent:)', content, re.MULTILINE | re.DOTALL)
    if summary_match:
        result['summary'] = ' '.join(summary_match.group(1).strip().split())
    else:
        summary_match = re.search(r'^summary:\s*(.+)$', content, re.MULTILINE)
        result['summary'] = summary_match.group(1).strip() if summary_match else ''
    
    # Extract title from metadata
    title_match = re.search(r'^\s+title:\s*(.+)$', content, re.MULTILINE)
    result['title'] = title_match.group(1).strip().strip('"\'') if title_match else result['name']
    
    # Extract description from metadata
    desc_match = re.search(r'^\s+description:\s*(.+)$', content, re.MULTILINE)
    result['description'] = desc_match.group(1).strip() if desc_match else result['summary']
    
    # Extract ms.topic
    topic_match = re.search(r'ms\.topic:\s*(.+)$', content, re.MULTILINE)
    result['topic_type'] = topic_match.group(1).strip() if topic_match else ''
    
    # Extract azureCategories list
    cats = []
    cats_match = re.search(r'azureCategories:\s*\n((?:\s+-\s+.+\n)+)', content)
    if cats_match:
        cats = [line.strip().lstrip('- ').strip().strip('"').strip("'") for line in cats_match.group(1).strip().split('\n')]
    result['categories'] = [c for c in cats if c]
    
    # Extract products list
    prods = []
    prods_match = re.search(r'products:\s*\n((?:\s+-\s+.+\n)+)', content)
    if prods_match:
        prods = [line.strip().lstrip('- ').strip().strip('"').strip("'") for line in prods_match.group(1).strip().split('\n')]
    result['products'] = [p for p in prods if p]
    
    return result

def main():
    print("Step 1: Fetching GitHub repo tree...", flush=True)
    all_files = get_repo_tree()
    
    # Architecture file patterns
    arch_dirs = [
        'docs/ai-ml/architecture/', 'docs/ai-ml/idea/', 'docs/ai-ml/openai/architecture/',
        'docs/example-scenario/', 'docs/reference-architectures/',
        'docs/solution-ideas/articles/',
        'docs/databases/architecture/', 'docs/databases/idea/',
        'docs/hybrid/', 'docs/virtual-machines/', 'docs/high-availability/',
        'docs/mainframe/', 'docs/industries/',
        'docs/analytics/architecture/',
        'docs/microservices/',
        'docs/serverless/', 'docs/landing-zones/',
        'docs/networking/architecture/', 'docs/networking/guide/',
        'docs/web-apps/',
        'docs/best-practices/',
        'docs/guide/aks/', 'docs/guide/sas/', 'docs/guide/devsecops/',
        'docs/guide/security/', 'docs/guide/iot/',
        'docs/guide/hadoop/', 'docs/guide/spot/', 'docs/guide/compute/',
        'docs/guide/data/',
    ]
    
    yml_files = []
    for f in all_files:
        if not f.endswith('.yml'):
            continue
        if f.endswith('toc.yml'):
            continue
        if any(f.startswith(d) for d in arch_dirs):
            yml_files.append(f)
    
    print(f"  Found {len(yml_files)} architecture .yml files", flush=True)
    
    print("\nStep 2: Fetching TOC for title mapping...", flush=True)
    toc_data = get_toc_data()
    toc_entries = extract_toc_entries(toc_data)
    print(f"  TOC has {len(toc_entries)} leaf entries", flush=True)
    
    print(f"\nStep 3: Fetching {len(yml_files)} YAML files from GitHub...", flush=True)
    
    catalog = []
    errors = []
    
    for i, filepath in enumerate(yml_files):
        if (i + 1) % 20 == 0 or i == 0:
            print(f"  Fetching {i+1}/{len(yml_files)}...", flush=True)
        
        url = BASE_RAW + filepath
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            content = urllib.request.urlopen(req).read().decode('utf-8')
            
            meta = parse_yml_frontmatter(content)
            
            # Build href (relative path for learn.microsoft.com)
            rel_path = filepath.replace('docs/', '').replace('.yml', '')
            learn_url = LEARN_BASE + rel_path
            
            # Determine type from metadata or path
            topic_type = meta.get('topic_type', '')
            if 'solution-idea' in topic_type or '/idea/' in filepath or 'solution-ideas/' in filepath:
                entry_type = 'Solution Idea'
            elif 'reference-architecture' in topic_type:
                entry_type = 'Reference Architecture'
            elif 'best-practice' in topic_type:
                entry_type = 'Best Practice'
            else:
                entry_type = 'Architecture'
            
            # Determine category from metadata
            categories = meta.get('categories', [])
            if not categories:
                # Derive from path
                if 'ai-ml/' in filepath:
                    categories = ['ai-machine-learning']
                elif 'networking/' in filepath:
                    categories = ['networking']
                elif 'databases/' in filepath:
                    categories = ['databases']
                elif 'hybrid/' in filepath:
                    categories = ['hybrid-multicloud']
                elif 'web-apps/' in filepath:
                    categories = ['web']
            
            # Map category codes to display names
            cat_map = {
                'ai-machine-learning': 'AI + Machine Learning',
                'analytics': 'Analytics',
                'compute': 'Compute',
                'containers': 'Containers',
                'databases': 'Databases',
                'developer-tools': 'Developer Tools',
                'devops': 'DevOps',
                'hybrid-multicloud': 'Hybrid + Multicloud',
                'identity': 'Identity',
                'integration': 'Integration',
                'iot': 'Internet of Things',
                'management-governance': 'Management + Governance',
                'media': 'Media',
                'migration': 'Migration',
                'mobile': 'Mobile',
                'networking': 'Networking',
                'security': 'Security',
                'storage': 'Storage',
                'virtual-desktop-infrastructure': 'Virtual Desktop',
                'web': 'Web',
                'featured': 'Featured',
            }
            
            display_categories = [cat_map.get(c, c) for c in categories]
            
            # Generate key from filename
            filename = filepath.split('/')[-1].replace('.yml', '')
            key = re.sub(r'[^a-z0-9]+', '_', filename.lower()).strip('_')
            
            entry = {
                'key': key,
                'name': meta.get('name', '') or meta.get('title', '') or filename,
                'summary': meta.get('summary', '') or meta.get('description', ''),
                'source_url': learn_url,
                'type': entry_type,
                'categories': display_categories,
                'category_codes': categories,
                'products': meta.get('products', []),
                'file_path': filepath,
            }
            
            catalog.append(entry)
            
        except Exception as e:
            errors.append((filepath, str(e)))
        
        # Brief delay to avoid rate limiting
        if (i + 1) % 50 == 0:
            time.sleep(1)
    
    # Deduplicate by key
    seen_keys = set()
    unique_catalog = []
    for entry in catalog:
        if entry['key'] not in seen_keys:
            seen_keys.add(entry['key'])
            unique_catalog.append(entry)
    
    # Sort by category then name
    unique_catalog.sort(key=lambda e: (e['categories'][0] if e['categories'] else 'zzz', e['name']))
    
    print(f"\nStep 4: Results", flush=True)
    print(f"  Total entries: {len(unique_catalog)}", flush=True)
    print(f"  Errors: {len(errors)}", flush=True)
    
    # Stats by category
    cat_counts = {}
    for e in unique_catalog:
        for c in e['categories']:
            cat_counts[c] = cat_counts.get(c, 0) + 1
    for c in sorted(cat_counts.keys()):
        print(f"    {c}: {cat_counts[c]}", flush=True)
    
    # Stats by type
    type_counts = {}
    for e in unique_catalog:
        type_counts[e['type']] = type_counts.get(e['type'], 0) + 1
    print(f"\n  By type:", flush=True)
    for t, c in sorted(type_counts.items()):
        print(f"    {t}: {c}", flush=True)
    
    if errors:
        print(f"\n  Errors:", flush=True)
        for fp, err in errors[:10]:
            print(f"    {fp}: {err}", flush=True)
    
    # Save catalog
    out_path = 'output/azure_architecture_catalog.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(unique_catalog, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved to {out_path}", flush=True)

if __name__ == '__main__':
    main()
