import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

provs = json.loads(text[text.find('window.PROVINCES_DATA =') + len('window.PROVINCES_DATA ='):text.find('window.OFFICERS_MASTER =')].strip().rstrip(';'))
officers = json.loads(text[text.find('window.OFFICERS_MASTER =') + len('window.OFFICERS_MASTER ='):text.find('window.SCENARIOS_DATA =')].strip().rstrip(';'))
scenarios = json.loads(text[text.find('window.SCENARIOS_DATA =') + len('window.SCENARIOS_DATA ='):text.find('window.CLAN_MASTER_DATA =')].strip().rstrip(';'))
hist_govs = json.loads(text[text.find('window.SCENARIO_HISTORICAL_GOVERNORS =') + len('window.SCENARIO_HISTORICAL_GOVERNORS ='):text.find('window.CLAN_CAPITAL_PROVINCES =')].strip().rstrip(';'))
capitals = json.loads(text[text.find('window.CLAN_CAPITAL_PROVINCES =') + len('window.CLAN_CAPITAL_PROVINCES ='):].strip().rstrip(';'))

print("=== SCENARIOS & TSUGARU / NANBU ===")
for s in scenarios:
    s_id = str(s['id'])
    year = s['year']
    title = s['title']
    owners = s.get('provinceOwners', {})
    tsugaru_owner = owners.get('tsugaru')
    mutsu_owner = owners.get('mutsu')
    govs = hist_govs.get(s_id, {})
    tsugaru_gov = govs.get('tsugaru')
    print(f"[{s_id}] {year} {title}: tsugaru owner={tsugaru_owner}, gov={tsugaru_gov} | mutsu owner={mutsu_owner}")

print("\n=== TSUGARU TAMENOBU OFFICER ===")
for o in officers:
    if '津軽為信' in o['name'] or o['id'] == 'off_tsugaru_tamenobu':
        print(o)

