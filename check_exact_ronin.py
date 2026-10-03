import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('window.OFFICERS_MASTER = [')
end_idx = text.find('\n];', start_idx) + 2
officers = json.loads(text[start_idx + len('window.OFFICERS_MASTER = '):end_idx])

start_idx_scen = text.find('window.SCENARIOS_DATA = [')
end_idx_scen = text.find('\n];', start_idx_scen) + 2
scenarios = json.loads(text[start_idx_scen + len('window.SCENARIOS_DATA = '):end_idx_scen])

# Let's inspect which officers become ronin in 1866, 1860, 1853, 1837, 1789, 1702, 1651, 1614, 1600, 1582, 1560
def check_scenario_ronin(sid):
    scen = next(s for s in scenarios if str(s['id']) == sid)
    year = scen['year']
    owners = set(scen.get('owners', {}).values())
    alive = [o for o in officers if (o.get('birthYear', 9999) <= year <= o.get('deathYear', -9999))]
    
    # We want to identify officers whose historical lord or affiliation EXISTS on the map
    # but they become ronin because of clanId mismatch or missing affiliation rule
    print(f"\n=======================================================")
    print(f"Scenario {sid} ({year} {scen.get('title')}) - Alive: {len(alive)}")
    print(f"Map Owners: {sorted(list(owners))}")
    print(f"=======================================================")
    
    # Check each unlanded
    for o in alive:
        c = o.get('clanId')
        if c in owners: continue
        # Print who they are
        print(f"  {o['id']:<28} {o['name']:<14} origClan:{c:<16} prov:{o.get('defaultProv'):<14} {o.get('birthYear')}-{o.get('deathYear')}")

for sid in ['1866', '1868', '1860', '1853', '1837', '1789', '1702', '1651', '1614', '1600']:
    check_scenario_ronin(sid)
