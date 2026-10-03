import json
import re

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

scen_match = re.search(r'window\.SCENARIOS_DATA\s*=\s*(\[.*?\]);\s*window\.CLAN_MASTER_DATA', text, re.DOTALL)
scens = {str(s['id']): s for s in json.loads(scen_match.group(1))}

for sid in ['1582', '1584']:
    if sid in scens:
        s = scens[sid]
        print(f"Scenario {sid}:")
        for p in s.get('playables', []):
            if '織田' in p.get('name', '') or 'oda' in p.get('id', ''):
                print(f"  {p['id']}: {p['name']} ({p.get('clan')})")

clan_match = re.search(r'window\.CLAN_MASTER_DATA\s*=\s*(\{.*?\});\s*window\.CLAN_ABILITIES', text, re.DOTALL)
clans = json.loads(clan_match.group(1))

for cid in ['oda', 'oda_nobuo', 'oda_nobutaka']:
    print(f"Clan {cid} in CLAN_MASTER_DATA: {cid in clans}")
