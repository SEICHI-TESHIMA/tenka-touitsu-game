import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

from accurate_jodai_sim import scenarios, hist_govs, officers_map, is_capital_correct

print("Remaining Empty Provinces across all scenarios:")
for scen in scenarios:
    sid = str(scen['id'])
    year = scen['year']
    title = scen['title']
    owners = scen.get('owners', {})
    govs = hist_govs.get(sid, {})
    
    empty_list = []
    for p, o in owners.items():
        if not o: continue
        is_cap = is_capital_correct(p, o, owners)
        target = govs.get(p)
        off = officers_map.get(target)
        if not is_cap and not off:
            empty_list.append((p, o, target))
            
    if empty_list:
        print(f"Scenario {sid} ({year} {title}) - Empty: {len(empty_list)}")
        for p, o, target in empty_list:
            print(f"  prov:{p:<15} owner:{o:<20} assignedTarget:{target}")
