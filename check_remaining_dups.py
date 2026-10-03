import sys
import json
import re
from collections import defaultdict
from verify_merges import merges

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'window\.OFFICERS_MASTER\s*=\s*(\[.*?\]);', text, re.DOTALL)
officers = json.loads(m.group(1))

merged_ids_set = set()
for canon, m_list, desc in merges:
    for mid in m_list:
        merged_ids_set.add(mid)

name_map = defaultdict(list)
for o in officers:
    if o['id'] not in merged_ids_set:
        name_map[o['name']].append(o)

remaining_dups = {k: v for k, v in name_map.items() if len(v) > 1}

print(f"Remaining duplicate name groups: {len(remaining_dups)}")
for k, v in remaining_dups.items():
    print(f"\nName: '{k}' ({len(v)} entries):")
    for o in v:
        print(f"  id: {o['id']}, birth: {o['birthYear']}-{o['deathYear']}, clan: {o.get('clanId')}, prov: {o.get('defaultProv')}")
        print(f"    lore: {o.get('lore')}")
