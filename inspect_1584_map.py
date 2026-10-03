import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

def parse_section(prefix, next_prefix):
    start = text.find(prefix) + len(prefix)
    end = text.find(next_prefix, start) if next_prefix else len(text)
    body = text[start:end].strip()
    last_b = max(body.rfind(']'), body.rfind('}'))
    return json.loads(body[:last_b+1])

provs = parse_section('window.PROVINCES_DATA =', 'window.OFFICERS_MASTER =')
scenarios = parse_section('window.SCENARIOS_DATA =', 'window.CLAN_MASTER_DATA =')
hist_govs = parse_section('window.SCENARIO_HISTORICAL_GOVERNORS =', 'window.CLAN_CAPITAL_PROVINCES =')

scen_1584 = next(s for s in scenarios if str(s['id']) == '1584')
govs_1584 = hist_govs.get('1584', {})

print("=== 1584 PROVINCE OWNERS & GOVERNORS ===")
for p in provs:
    pid = p['id']
    pname = p['name']
    owner = scen_1584['owners'].get(pid)
    gov = govs_1584.get(pid)
    print(f"{pid:15s} ({pname:4s}): owner={str(owner):12s} | gov={str(gov)}")

