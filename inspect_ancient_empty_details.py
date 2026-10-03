import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

from accurate_jodai_sim import scenarios, hist_govs, officers_map, is_capital_correct

for sid in ['1028', '1056', '1087']:
    scen = next(s for s in scenarios if str(s['id']) == sid)
    year = scen['year']
    owners = scen.get('owners', {})
    govs = hist_govs.get(sid, {})
    
    empty_list = []
    for p, o in owners.items():
        if not o: continue
        is_cap = is_capital_correct(p, o, owners)
        target = govs.get(p)
        off = officers_map.get(target)
        if not is_cap and not off:
            empty_list.append((p, o))
            
    print(f"\nScenario {sid} ({year}) Empty count: {len(empty_list)}")
    owners_counts = {}
    for p, o in empty_list:
        owners_counts[o] = owners_counts.get(o, 0) + 1
    print("  Owners:", owners_counts)
