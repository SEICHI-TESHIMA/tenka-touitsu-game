import json
import re

with open('js/data.js', 'r', encoding='utf-8') as f:
    data_text = f.read()

start_idx = data_text.find('window.OFFICERS_MASTER = [')
end_idx = data_text.find('\n];', start_idx) + 2
officers_master = json.loads(data_text[start_idx + len('window.OFFICERS_MASTER = '):end_idx])

start_idx = data_text.find('window.SCENARIOS_DATA = [')
end_idx = data_text.find('\n];', start_idx) + 2
scenarios = json.loads(data_text[start_idx + len('window.SCENARIOS_DATA = '):end_idx])

# Read app.js logic for resolveOfficerAffiliations simulation
out = []

for scen in scenarios:
    sid = str(scen['id'])
    year = scen['year']
    title = scen.get('title', '')
    owners = set(scen.get('owners', {}).values())
    
    # filter alive officers
    alive = []
    for m in officers_master:
        by = m.get('birthYear')
        dy = m.get('deathYear')
        if by is not None and dy is not None:
            age = year - by
            if age >= 15 and year <= dy:
                alive.append(dict(m))
                
    # Check who does not have clan in owners
    unlanded = []
    for o in alive:
        c = o.get('clanId')
        # check if clan is in owners
        if c not in owners:
            unlanded.append((o['id'], o['name'], c, o.get('defaultProv')))
            
    out.append(f"=== Scenario {sid} ({year} {title}) | Owners: {len(owners)} | Unlanded/Ronin: {len(unlanded)} ===")
    for u in unlanded:
        out.append(f"  {u[0]:<28} | {u[1]:<12} | origClan:{u[2]:<16} | defProv:{u[3]}")

with open('all_scenarios_unlanded_utf8.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(out))

print("Saved all_scenarios_unlanded_utf8.txt successfully.")
