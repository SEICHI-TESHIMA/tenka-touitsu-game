import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'window\.OFFICERS_MASTER\s*=\s*(\[.*?\]);', text, re.DOTALL)
officers = json.loads(m.group(1))
officer_by_id = {o['id']: o for o in officers}

from verify_merges import merges

# Add the two newly found ones:
merges_extended = list(merges)
merges_extended.append(('off_edo_matsudaira_harusato', ['off_edo_matsue_1743_167'], '松平治郷 (1751-1818)'))
merges_extended.append(('off_edo_matsudaira_yorizane', ['off_matsudaira_yoritaka'], '松平頼真 (1743-1800)'))

print(f"Total merge groups: {len(merges_extended)}")

# Build merge map: merged_id -> canonical_id
merge_id_map = {}
for canon_id, merged_list, desc in merges_extended:
    for mid in merged_list:
        merge_id_map[mid] = canon_id

print(f"Total merged IDs to eliminate: {len(merge_id_map)}")

# Perform merge simulation
merged_officers_dict = {}
for o in officers:
    oid = o['id']
    if oid in merge_id_map:
        continue # will be merged into canonical
    merged_officers_dict[oid] = dict(o)

# Now apply properties from merged into canonical
for canon_id, merged_list, desc in merges_extended:
    target = merged_officers_dict[canon_id]
    for mid in merged_list:
        src = officer_by_id[mid]
        # max stats
        target['military'] = max(target.get('military', 0), src.get('military', 0))
        target['politic'] = max(target.get('politic', 0), src.get('politic', 0))
        target['intel'] = max(target.get('intel', 0), src.get('intel', 0))
        # isDaimyo
        if src.get('isDaimyo'):
            target['isDaimyo'] = True
        # lore: take the longer / more informative one
        if len(src.get('lore', '')) > len(target.get('lore', '')):
            target['lore'] = src['lore']
        # skill
        if not target.get('skill') and src.get('skill'):
            target['skill'] = src['skill']

print(f"Original officers count: {len(officers)}")
print(f"New officers count: {len(merged_officers_dict)}")
print(f"Difference: {len(officers) - len(merged_officers_dict)} officers merged!")
