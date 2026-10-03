import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

def parse_section(prefix, next_prefix):
    start = text.find(prefix) + len(prefix)
    end = text.find(next_prefix, start) if next_prefix else len(text)
    body = text[start:end].strip()
    last_b = max(body.rfind(']'), body.rfind('}'))
    return json.loads(body[:last_b+1])

officers_master = parse_section('window.OFFICERS_MASTER =', 'window.SCENARIOS_DATA =')
scenarios = parse_section('window.SCENARIOS_DATA =', 'window.CLAN_MASTER_DATA =')
hist_govs = parse_section('window.SCENARIO_HISTORICAL_GOVERNORS =', 'window.CLAN_CAPITAL_PROVINCES =')

scen_1584 = next(s for s in scenarios if str(s['id']) == '1584')
print("=== 1584 Scenario ===")
print("Title:", scen_1584['title'])
print("Owners of Tohoku:")
for p in ['tsugaru', 'mutsu', 'rikuchu', 'rikuzen', 'ugo', 'uzen', 'iwashiro', 'iwaki', 'ezo']:
    print(f"  {p}: {scen_1584['owners'].get(p)}")

print("Govs of Tohoku in 1584:")
govs_1584 = hist_govs.get('1584', {})
for p in ['tsugaru', 'mutsu', 'rikuchu', 'rikuzen', 'ugo', 'uzen', 'iwashiro', 'iwaki', 'ezo']:
    print(f"  {p}: {govs_1584.get(p)}")

# Find Nanbu officers and Tsugaru officers
print("\nOfficers with clan nanbu or tsugaru in 1584:")
for o in officers_master:
    b = o.get('birthYear', 0)
    d = o.get('deathYear', 9999)
    if b <= 1584 - 15 <= d and (o.get('clanId') in ['nanbu', 'tsugaru'] or '津軽' in o['name'] or '南部' in o['name']):
        print(f"  {o['id']}: {o['name']} (clan:{o['clanId']}, defProv:{o.get('defaultProv')}, isDaimyo:{o.get('isDaimyo')})")

