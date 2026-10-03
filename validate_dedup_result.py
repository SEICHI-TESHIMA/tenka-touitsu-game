import sys
import json
import re
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'window\.OFFICERS_MASTER\s*=\s*(\[.*?\]);', text, re.DOTALL)
officers = json.loads(m.group(1))

print(f"OFFICERS_MASTER is valid JSON! Count: {len(officers)}")

ids = [o['id'] for o in officers]
id_c = Counter(ids)
dup_ids = {k: v for k, v in id_c.items() if v > 1}
print(f"Duplicate IDs: {len(dup_ids)}")

name_map = Counter([o['name'] for o in officers])
dup_names = {k: v for k, v in name_map.items() if v > 1}
print(f"Duplicate Names: {len(dup_names)}")
for k, v in dup_names.items():
    entries = [o for o in officers if o['name'] == k]
    years = [f"{o.get('id')} ({o.get('birthYear')}-{o.get('deathYear')})" for o in entries]
    print(f"  '{k}' ({v} entries): {', '.join(years)}")
