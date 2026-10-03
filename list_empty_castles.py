import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Officers
idx_off = text.find('window.OFFICERS_MASTER = [')
end_off = text.find('];', idx_off)
officers = json.loads(text[idx_off + len('window.OFFICERS_MASTER = '): end_off + 1])
officers_dict = {o['id']: o for o in officers}

# Scenarios
idx_scen = text.find('window.SCENARIOS_DATA = [')
end_scen = text.find('];\n\nwindow.CLAN_MASTER_DATA', idx_scen)
if end_scen == -1:
    end_scen = text.find('];', idx_scen)
scenarios = json.loads(text[idx_scen + len('window.SCENARIOS_DATA = '): end_scen + 1])

# Historical governors
idx_gov = text.find('window.SCENARIO_HISTORICAL_GOVERNORS = {')
end_gov = text.find('};\n\n', idx_gov)
if end_gov == -1:
    end_gov = text.find('};', idx_gov)
gov_text = text[idx_gov + len('window.SCENARIO_HISTORICAL_GOVERNORS = '): end_gov + 1]
# Note: gov_text is a JS object, let's load using python regex or json if formatted as json
import re
# check if it's json parsable
try:
    hist_govs = json.loads(gov_text)
except Exception:
    # replace unquoted keys
    cleaned = re.sub(r'([a-zA-Z0-9_]+):', r'"\1":', gov_text)
    hist_govs = json.loads(cleaned)

print(f"Loaded {len(hist_govs)} scenario governor entries.")

check_scenarios = ['1789', '1467', '1438', '1221', '1156']

for sid in check_scenarios:
    scen = next(s for s in scenarios if str(s['id']) == sid)
    year = scen['year']
    prov_owners = scen.get('owners', {})
    gov_map = hist_govs.get(sid, {})
    
    empty_provs = []
    for prov_id, owner_id in prov_owners.items():
        gov_id = gov_map.get(prov_id)
        if not gov_id:
            empty_provs.append((prov_id, owner_id, 'NoGovInMap'))
        else:
            gov_off = officers_dict.get(gov_id)
            if not gov_off:
                empty_provs.append((prov_id, owner_id, f'InvalidGovId({gov_id})'))
            elif not (gov_off.get('birthYear', 9999) <= year <= gov_off.get('deathYear', -9999)):
                empty_provs.append((prov_id, owner_id, f"DeadGov({gov_off['name']},{gov_off.get('birthYear')}-{gov_off.get('deathYear')})"))
                
    print(f"\nScenario {sid} ({year} {scen.get('title')}) - Empty count: {len(empty_provs)} / {len(prov_owners)}")
    for ep in empty_provs:
        print(f"  prov:{ep[0]:<15} owner:{ep[1]:<20} reason:{ep[2]}")
