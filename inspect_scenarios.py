import json
import re

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

scen_match = re.search(r'window\.SCENARIOS_DATA\s*=\s*(\[.*?\]);\s*window\.CLAN_MASTER_DATA', text, re.DOTALL)
scens = {str(s['id']): s for s in json.loads(scen_match.group(1))}

for s_id in ['939', '1028', '1051', '1087', '1180', '1183', '1184', '1185']:
    if s_id in scens:
        s = scens[s_id]
        print(f"Scenario {s_id}: {s.get('title')} ({s.get('year')} {s.get('season')})")
        print("  playables:")
        for p in s.get('playables', []):
            print(f"    id: {p['id']}, name: {p['name']}, clan: {p.get('clan')}")
        print()
