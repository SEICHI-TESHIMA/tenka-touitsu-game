import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('window.OFFICERS_MASTER = [')
end_idx = text.find('\n];', start_idx) + 2
officers = json.loads(text[start_idx + len('window.OFFICERS_MASTER = '):end_idx])

start_idx_scen = text.find('window.SCENARIOS_DATA = [')
end_idx_scen = text.find('\n];', start_idx_scen) + 2
scenarios = json.loads(text[start_idx_scen + len('window.SCENARIOS_DATA = '):end_idx_scen])

idx_gov = text.find('window.SCENARIO_HISTORICAL_GOVERNORS = {')
end_idx_gov = text.find('\n};', idx_gov) + 3
hist_govs = json.loads(text[idx_gov + len('window.SCENARIO_HISTORICAL_GOVERNORS = '):end_idx_gov-1])

idx_cm = text.find('window.CLAN_MASTER_DATA = {')
end_idx_cm = text.find('\n};', idx_cm) + 3
clan_master = json.loads(text[idx_cm + len('window.CLAN_MASTER_DATA = '):end_idx_cm-1])

officers_map = {o['id']: o for o in officers}

def is_capital(p, o, owners):
    cm = clan_master.get(o)
    if cm and cm.get('capital') == p: return True
    owned = [k for k, v in owners.items() if v == o]
    return owned and owned[0] == p

out = []
for scen in scenarios:
    sid = str(scen['id'])
    year = scen['year']
    title = scen['title']
    owners = scen.get('owners', {})
    govs = hist_govs.get(sid, {})
    
    empty_list = []
    for p, o in owners.items():
        if not o: continue
        is_cap = is_capital(p, o, owners)
        target = govs.get(p)
        off = officers_map.get(target)
        if not is_cap and not off:
            empty_list.append((p, o))
            
    out.append(f"Scenario {sid:<5} ({year:<4} {title:<16}) | Owned: {len(owners):<2} | Truly Empty/Jodai: {len(empty_list):<2}")
    if empty_list:
        for p, o in empty_list[:5]:
            out.append(f"   - {p:<14} (owner: {o})")

with open('all_scenarios_empty_report_utf8.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(out))

print("Saved all_scenarios_empty_report_utf8.txt")
