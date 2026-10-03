import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

def parse_section(prefix, next_prefix):
    start = text.find(prefix) + len(prefix)
    end = text.find(next_prefix, start) if next_prefix else len(text)
    body = text[start:end].strip()
    last_b = max(body.rfind(']'), body.rfind('}'))
    return json.loads(body[:last_b+1])

hist_govs = parse_section('window.SCENARIO_HISTORICAL_GOVERNORS =', 'window.CLAN_CAPITAL_PROVINCES =')
scenarios = parse_section('window.SCENARIOS_DATA =', 'window.CLAN_MASTER_DATA =')

print("=== SCENARIO_HISTORICAL_GOVERNORS for Tsugaru Tamenobu ===")
for sid, govs in hist_govs.items():
    for pid, gid in govs.items():
        if gid == 'off_tsugaru_tamenobu' or gid == '津軽為信':
            scen = next((s for s in scenarios if str(s['id']) == sid), None)
            year = scen['year'] if scen else '?'
            owner = scen.get('owners', {}).get(pid) if scen else '?'
            print(f"  Scen [{sid}] ({year}): {pid} = {gid} (province owner: {owner})")

