import sys
import json
import re
import shutil
from officer_merge_definitions import OFFICER_MERGES, OFFICER_RENAMES

sys.stdout.reconfigure(encoding='utf-8')

# 1. Back up files
shutil.copyfile('js/data.js', 'js/data.js.before_officer_dedup_bak')
shutil.copyfile('js/historical_jodai.js', 'js/historical_jodai.js.before_officer_dedup_bak')
shutil.copyfile('js/app.js', 'js/app.js.before_officer_dedup_bak')
print("Backed up data.js, historical_jodai.js, app.js")

# 2. Build ID replacement map: merged_id -> canonical_id
merge_id_map = {}
for canon_id, merged_list, _, desc in OFFICER_MERGES:
    for mid in merged_list:
        merge_id_map[mid] = canon_id

print(f"Total merged IDs to replace: {len(merge_id_map)}")

# 3. Read and process js/data.js
with open('js/data.js', 'r', encoding='utf-8') as f:
    data_content = f.read()

# Extract OFFICERS_MASTER
prefix = 'window.OFFICERS_MASTER ='
next_prefix = 'window.SCENARIOS_DATA ='
start_idx = data_content.find(prefix) + len(prefix)
end_idx = data_content.find(next_prefix, start_idx)

body = data_content[start_idx:end_idx].strip()
last_bracket = max(body.rfind(']'), body.rfind('}'))
officers_json_str = body[:last_bracket+1]

officers = json.loads(officers_json_str)
print(f"Original OFFICERS_MASTER length: {len(officers)}")

officer_by_id = {o['id']: o for o in officers}

# Perform merge
merged_officers_dict = {}
for o in officers:
    oid = o['id']
    if oid in merge_id_map:
        continue # remove merged duplicate
    merged_officers_dict[oid] = dict(o)

for canon_id, merged_list, _, desc in OFFICER_MERGES:
    target = merged_officers_dict[canon_id]
    for mid in merged_list:
        src = officer_by_id[mid]
        # Stat merge (max of both)
        target['military'] = max(target.get('military', 0), src.get('military', 0))
        target['politic'] = max(target.get('politic', 0), src.get('politic', 0))
        target['intel'] = max(target.get('intel', 0), src.get('intel', 0))
        
        # isDaimyo flag
        if src.get('isDaimyo'):
            target['isDaimyo'] = True
            
        # lore: prefer more detailed / longer description
        if len(src.get('lore', '')) > len(target.get('lore', '')):
            target['lore'] = src['lore']
            
        # skill: preserve if target doesn't have one
        if not target.get('skill') and src.get('skill'):
            target['skill'] = src['skill']

# Apply renames for dummy successors
for oid, (new_name, new_lore) in OFFICER_RENAMES.items():
    if oid in merged_officers_dict:
        merged_officers_dict[oid]['name'] = new_name
        merged_officers_dict[oid]['lore'] = new_lore
        print(f"Renamed {oid} to '{new_name}'")

new_officers_list = list(merged_officers_dict.values())
print(f"New OFFICERS_MASTER length: {len(new_officers_list)}")
print(f"Eliminated duplicates count: {len(officers) - len(new_officers_list)}")

# Format new OFFICERS_MASTER
new_officers_json = json.dumps(new_officers_list, ensure_ascii=False, indent=2)

# Reconstruct data.js with updated OFFICERS_MASTER
new_data_content = data_content[:start_idx] + ' ' + new_officers_json + ';\n\n' + data_content[end_idx:]

# Replace all merged IDs in the entire data.js (especially in SCENARIO_HISTORICAL_GOVERNORS, etc.)
replaced_in_data = 0
for mid, canon_id in merge_id_map.items():
    count = new_data_content.count(mid)
    if count > 0:
        new_data_content = new_data_content.replace(f'"{mid}"', f'"{canon_id}"')
        new_data_content = new_data_content.replace(f"'{mid}'", f"'{canon_id}'")
        replaced_in_data += count

print(f"Replaced {replaced_in_data} references of merged IDs in data.js")

with open('js/data.js', 'w', encoding='utf-8') as f:
    f.write(new_data_content)
print("Updated js/data.js successfully.")

# 4. Update js/historical_jodai.js
with open('js/historical_jodai.js', 'r', encoding='utf-8') as f:
    jodai_content = f.read()

replaced_in_jodai = 0
for mid, canon_id in merge_id_map.items():
    count = jodai_content.count(mid)
    if count > 0:
        jodai_content = jodai_content.replace(f'"{mid}"', f'"{canon_id}"')
        jodai_content = jodai_content.replace(f"'{mid}'", f"'{canon_id}'")
        replaced_in_jodai += count

print(f"Replaced {replaced_in_jodai} references in js/historical_jodai.js")
with open('js/historical_jodai.js', 'w', encoding='utf-8') as f:
    f.write(jodai_content)
print("Updated js/historical_jodai.js successfully.")

print("Step 1 execution finished.")
