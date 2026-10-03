import sys
import json
import re
from collections import defaultdict

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'window\.OFFICERS_MASTER\s*=\s*(\[.*?\]);', text, re.DOTALL)
officers = json.loads(m.group(1))

# Group by name
name_map = defaultdict(list)
for idx, o in enumerate(officers):
    name_map[o.get('name')].append((idx, o))

dup_names = {k: v for k, v in name_map.items() if len(v) > 1}

lines = []
lines.append(f"Total duplicate groups: {len(dup_names)}")

for i, (name, list_offs) in enumerate(dup_names.items(), 1):
    lines.append(f"\n[{i}] Name: '{name}' ({len(list_offs)} entries)")
    for idx, o in list_offs:
        lines.append(f"    - idx: {idx}, id: {o.get('id')}, clan: {o.get('clanId')}, prov: {o.get('defaultProv')}, "
                     f"years: {o.get('birthYear')}-{o.get('deathYear')}, "
                     f"mil: {o.get('military')}, pol: {o.get('politic')}, int: {o.get('intel')}, "
                     f"isDaimyo: {o.get('isDaimyo')}")
        lines.append(f"      lore: {o.get('lore')}")

with open('all_90_duplicates_detailed.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("Wrote all_90_duplicates_detailed.txt")
