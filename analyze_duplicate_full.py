import sys
import json
import re
from collections import defaultdict, Counter

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'window\.OFFICERS_MASTER\s*=\s*(\[.*?\]);', text, re.DOTALL)
officers = json.loads(m.group(1))

output = []
output.append(f"Total officers: {len(officers)}")

# 1. Duplicate IDs
ids = [o.get('id') for o in officers]
id_counts = Counter(ids)
dup_ids = {k: v for k, v in id_counts.items() if v > 1}
output.append(f"\nDuplicate IDs count: {len(dup_ids)}")
for k, v in dup_ids.items():
    output.append(f"  ID '{k}': {v} times")

# 2. Duplicate Names
name_map = defaultdict(list)
for idx, o in enumerate(officers):
    name_map[o.get('name')].append((idx, o))

dup_names = {k: v for k, v in name_map.items() if len(v) > 1}
output.append(f"\nDuplicate names count: {len(dup_names)}")
for name, list_officers in dup_names.items():
    output.append(f"\n=== Name: '{name}' ({len(list_officers)} entries) ===")
    for idx, o in list_officers:
        output.append(f"  [{idx}] ID: {o.get('id')}, Birth: {o.get('birthYear')}, Death: {o.get('deathYear')}, "
                      f"lead: {o.get('lead')}, bra: {o.get('bra')}, int: {o.get('int')}, pol: {o.get('pol')}, "
                      f"alias: {o.get('alias')}, skills: {o.get('skills')}")

with open('duplicate_analysis_full.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("Analysis written to duplicate_analysis_full.txt")
