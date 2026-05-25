"""Get all browseable architecture entries from GitHub repo tree."""
import urllib.request
import json
import re

# Get full repo tree
print("Fetching GitHub repo tree...")
url = "https://api.github.com/repos/MicrosoftDocs/architecture-center/git/trees/main?recursive=1"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
data = json.loads(urllib.request.urlopen(req).read().decode())

all_files = [item['path'] for item in data['tree'] if item['type'] == 'blob']

# Find all .yml files under architecture paths
arch_patterns = [
    r'^docs/ai-ml/(architecture|idea)/',
    r'^docs/example-scenario/',
    r'^docs/reference-architectures/',
    r'^docs/solution-ideas/articles/',
    r'^docs/databases/(architecture|idea)/',
    r'^docs/hybrid/',
    r'^docs/virtual-machines/',
    r'^docs/high-availability/',
    r'^docs/mainframe/',
    r'^docs/industries/',
    r'^docs/analytics/architecture/',
    r'^docs/microservices/',
    r'^docs/serverless/',
    r'^docs/landing-zones/',
    r'^docs/networking/',
    r'^docs/web-apps/',
    r'^docs/best-practices/',
    r'^docs/guide/(aks|sas|devsecops|security|iot|hadoop|spot|compute)/',
]

# Find all .yml files matching architecture patterns
yml_files = [f for f in all_files if f.endswith('.yml')]
print(f"Total .yml files in repo: {len(yml_files)}")

matched = set()
for pattern_str in arch_patterns:
    for f in yml_files:
        if re.match(pattern_str, f):
            matched.add(f)

print(f"Architecture .yml files matching patterns: {len(matched)}")

# Also count by prefix
prefixes = {}
for f in matched:
    parts = f.split('/')
    key = '/'.join(parts[:3]) if len(parts) > 3 else '/'.join(parts[:2])
    prefixes[key] = prefixes.get(key, 0) + 1

for k in sorted(prefixes.keys()):
    print(f"  {k}: {prefixes[k]}")

# AI+ML specific 
ai_ml = [f for f in yml_files if f.startswith('docs/ai-ml/')]
print(f"\nAll AI+ML .yml files: {len(ai_ml)}")
for f in sorted(ai_ml):
    print(f"  {f}")
