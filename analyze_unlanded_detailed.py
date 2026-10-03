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

# Also check resolveOfficerAffiliations in app.js
with open('js/app.js', 'r', encoding='utf-8') as f:
    app_text = f.read()

print("Analyzing unlanded officers for each scenario...")

results = {}
for scen in scenarios:
    s_id = str(scen['id'])
    year = scen['year']
    title = scen['title']
    owners = scen.get('owners', {})
    landed_clans = set(owners.values()) - {None, '', 'null'}
    govs = govs_map.get(s_id, {})
    gov_officer_ids = set(govs.values())
    
    active = []
    for o in officers_master:
        b = o.get('birthYear')
        d = o.get('deathYear')
        if b is not None and d is not None and (year >= b + 15) and (year <= d):
            active.append(o)
            
    unlanded = []
    for o in active:
        cid = o.get('clanId')
        # check if clan is landed or if officer is a governor
        if cid not in landed_clans and o['id'] not in gov_officer_ids and o['name'] not in gov_officer_ids:
            unlanded.append(o)
            
    results[s_id] = {
        'year': year,
        'title': title,
        'landed_clans': list(landed_clans),
        'unlanded': [{'id': o['id'], 'name': o['name'], 'clanId': o.get('clanId'), 'defaultProv': o.get('defaultProv'), 'isDaimyo': o.get('isDaimyo')} for o in unlanded]
    }

with open('unlanded_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Saved to unlanded_analysis.json")
