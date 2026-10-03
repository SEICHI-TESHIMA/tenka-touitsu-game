import json
import re

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Load SCENARIO_HISTORICAL_GOVERNORS
idx = text.find('window.SCENARIO_HISTORICAL_GOVERNORS = {')
end_idx = text.find('\n};', idx) + 3
hist_govs = json.loads(text[idx + len('window.SCENARIO_HISTORICAL_GOVERNORS = '):end_idx-1])

# Load SCENARIOS_DATA
start_idx = text.find('window.SCENARIOS_DATA = [')
end_idx = text.find('\n];', start_idx) + 2
scenarios = json.loads(text[start_idx + len('window.SCENARIOS_DATA = '):end_idx])

# Load OFFICERS_MASTER
start_idx = text.find('window.OFFICERS_MASTER = [')
end_idx = text.find('\n];', start_idx) + 2
officers = json.loads(text[start_idx + len('window.OFFICERS_MASTER = '):end_idx])
officer_ids = set(o['id'] for o in officers)
officer_names = set(o['name'] for o in officers)

# Check coverage for each scenario
out = []
total_empty = 0

for scen in scenarios:
    sid = str(scen['id'])
    year = scen['year']
    title = scen['title']
    owners = scen.get('owners', {})
    scen_hist = hist_govs.get(sid, {})
    
    empty_provs = []
    invalid_govs = []
    
    for prov_id, owner_id in owners.items():
        if not owner_id:
            continue
        gov = scen_hist.get(prov_id)
        if not gov:
            empty_provs.append((prov_id, owner_id))
        else:
            # check if gov exists in officers
            if gov not in officer_ids and gov not in officer_names:
                invalid_govs.append((prov_id, owner_id, gov))
                
    total_empty += len(empty_provs)
    out.append(f"Scenario {sid} ({year} {title}) | Provinces: {len(owners)} | Unassigned/Jodai: {len(empty_provs)} | InvalidGovs: {len(invalid_govs)}")
    if empty_provs:
        for p, o in empty_provs:
            out.append(f"   [EMPTY] prov: {p:<16} (owner: {o})")
    if invalid_govs:
        for p, o, g in invalid_govs:
            out.append(f"   [INVALID] prov: {p:<16} (owner: {o}) -> gov: {g} NOT FOUND")

out.append(f"\nTOTAL EMPTY PROVINCES ACROSS ALL SCENARIOS: {total_empty}")

with open('gov_coverage_utf8.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(out))

print(f"Done. Total empty provinces: {total_empty}")
