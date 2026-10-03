import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Clans
clan_idx = text.find('window.CLAN_MASTER_DATA =')
abilities_idx = text.find('window.CLAN_ABILITIES =')
clans = json.loads(text[clan_idx + len('window.CLAN_MASTER_DATA ='):abilities_idx].strip().rstrip(';'))

print("=== CHECK CLANS ===")
search_clans = ['kunohe', 'yui', 'oshio', 'amakusa', 'tengu', 'tenchu', 'nanbu', 'mito']
for k, v in clans.items():
    if any(sc in k for sc in search_clans):
        print(f"Clan: {k} -> {v.get('name')} (leader: {v.get('leader')}, color: {v.get('color')})")

# Check 1590, 1592, 1637, 1651, 1837 scenarios
scen_idx = text.find('window.SCENARIOS_DATA =')
scenarios = json.loads(text[scen_idx + len('window.SCENARIOS_DATA ='):clan_idx].strip().rstrip(';'))

for sid in ['1590', '1592', '1637', '1651', '1837', '1860', '1866']:
    s = next((sc for sc in scenarios if str(sc.get('id')) == sid), None)
    if s:
        print(f"\nScenario {sid}: {s.get('name')}")
        print("  Owners mutsu/rikuchu/mutsu_center:", {k: s.get('owners', {}).get(k) for k in ['mutsu', 'rikuchu', 'rikuzen', 'ugo', 'uzen'] if k in s.get('owners', {})})
        print("  Playables count:", len(s.get('playables', [])))
