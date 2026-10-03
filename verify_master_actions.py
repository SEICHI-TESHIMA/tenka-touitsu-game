with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re

m = re.search(r'getHistoricalEventsMaster\(\)\s*\{(.*?)\n\s*\}\s*\n\s*checkHistoricalEvents', text, re.DOTALL)
body = m.group(1)

# Check all ownerId assignments: ownerId = '...'
owner_assigns = re.findall(r"ownerId\s*=\s*'([^']+)'", body)
print("ownerId assignments in getHistoricalEventsMaster:", set(owner_assigns))

# Check province references: find(p => p.id === '...')
prov_finds = re.findall(r"p\.id\s*===\s*'([^']+)'", body)
print("prov finds:", set(prov_finds))

# Verify prov finds against PROVINCES_DATA
with open('js/data.js', 'r', encoding='utf-8') as f:
    dtext = f.read()
import json
prov_match = re.search(r'window\.PROVINCES_DATA\s*=\s*(\[.*?\]);', dtext, re.DOTALL)
provs = set(p['id'] for p in json.loads(prov_match.group(1)))
clan_match = re.search(r'window\.CLAN_MASTER_DATA\s*=\s*(\{.*?\});\s*window\.CLAN_ABILITIES', dtext, re.DOTALL)
clans = json.loads(clan_match.group(1))

for pf in set(prov_finds):
    if pf not in provs:
        print(f"INVALID PROVINCE in getHistoricalEventsMaster: {pf}")

for oa in set(owner_assigns):
    if oa not in clans:
        print(f"INVALID CLAN in getHistoricalEventsMaster: {oa}")
