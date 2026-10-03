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

provs = parse_section('window.PROVINCES_DATA =', 'window.OFFICERS_MASTER =')
officers_master = parse_section('window.OFFICERS_MASTER =', 'window.SCENARIOS_DATA =')
scenarios = parse_section('window.SCENARIOS_DATA =', 'window.CLAN_MASTER_DATA =')
clans = parse_section('window.CLAN_MASTER_DATA =', 'window.CLAN_ABILITIES =')
govs_map = parse_section('window.SCENARIO_HISTORICAL_GOVERNORS =', 'window.CLAN_CAPITAL_PROVINCES =')
capitals = parse_section('window.CLAN_CAPITAL_PROVINCES =', None)

for scen in scenarios:
    s_id = str(scen['id'])
    year = scen['year']
    title = scen['title']
    owners = scen.get('owners', {})
    landed_clans = set(owners.values()) - {None, '', 'null'}
    govs = govs_map.get(s_id, {})
    
    # Active officers: year >= b+15 and year <= d
    active = []
    for o in officers_master:
        b = o.get('birthYear')
        d = o.get('deathYear')
        if b is not None and d is not None and (year >= b + 15) and (year <= d):
            active.append(o)
            
    # Count how many are landed vs unlanded
    unlanded = [o for o in active if o.get('clanId') not in landed_clans]
    # Check if unlanded officer is assigned as a governor
    gov_ids = set(govs.values())
    unlanded_not_gov = [o for o in unlanded if o['id'] not in gov_ids and o['name'] not in gov_ids]
    
    print(f"[{s_id}] {year} {title} | Landed Clans: {len(landed_clans)} | Active: {len(active)} | Unlanded: {len(unlanded)} (NotGov: {len(unlanded_not_gov)})")

