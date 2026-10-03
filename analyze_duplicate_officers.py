import sys
import json
import re
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'window\.OFFICERS_MASTER\s*=\s*(\[.*?\]);', text, re.DOTALL)
officers = json.loads(m.group(1))

print(f"Total officers: {len(officers)}")
print(f"Sample officer: {json.dumps(officers[0], ensure_ascii=False, indent=2)}")

# 1. Check duplicate IDs
ids = [o.get('id') for o in officers]
id_counts = Counter(ids)
dup_ids = {k: v for k, v in id_counts.items() if v > 1}
print(f"\nDuplicate IDs count: {len(dup_ids)}")
for k, v in dup_ids.items():
    print(f"  ID '{k}': {v} times")

# 2. Check duplicate names
name_map = defaultdict(list)
for idx, o in enumerate(officers):
    name_map[o.get('name')].append((idx, o))

dup_names = {k: v for k, v in name_map.items() if len(v) > 1}
print(f"\nDuplicate names count: {len(dup_names)}")
for name, list_officers in dup_names.items():
    print(f"\n=== Name: {name} ({len(list_officers)} entries) ===")
    for idx, o in list_officers:
        print(f"  [{idx}] ID: {o.get('id')}, Clan: {o.get('clan')}, Birth: {o.get('birthYear')}, Death: {o.get('deathYear')}, Lead: {o.get('lead')}, Bra: {o.get('bra')}, Int: {o.get('int')}, Pol: {o.get('pol')}")

