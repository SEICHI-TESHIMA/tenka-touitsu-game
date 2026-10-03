import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Load scenarios
start_idx = text.find('window.SCENARIOS_DATA = [')
end_idx = text.find('\n];', start_idx) + 2
scenarios = json.loads(text[start_idx + len('window.SCENARIOS_DATA = '):end_idx])

# Load historical governors table if present
hist_govs = {}
h_idx = text.find('window.SCENARIO_HISTORICAL_GOVERNORS = {')
if h_idx != -1:
    h_end = text.find('\n};', h_idx) + 3
    # let's parse or extract
    sub = text[h_idx + len('window.SCENARIO_HISTORICAL_GOVERNORS = '):h_end]
    try:
        hist_govs = json.loads(sub)
    except:
        pass

out = []
for scen in scenarios:
    sid = str(scen['id'])
    year = scen['year']
    title = scen['title']
    owners = scen.get('owners', {})
    govs = scen.get('governors', {})
    scen_hist = hist_govs.get(sid, {})
    
    empty_provs = []
    for prov_id, owner_id in owners.items():
        if not owner_id:
            continue
        # Is there a governor in scen.governors or scen_hist?
        has_gov = False
        if prov_id in govs and govs[prov_id]:
            has_gov = True
        elif prov_id in scen_hist and scen_hist[prov_id]:
            has_gov = True
            
        if not has_gov:
            empty_provs.append((prov_id, owner_id))
            
    out.append(f"Scenario {sid} ({year} {title}) | Owned Provs: {len(owners)} | Empty/Jodai: {len(empty_provs)}")
    if empty_provs:
        for p, o in empty_provs:
            out.append(f"    - prov:{p:<16} owner:{o}")

with open('scenarios_empty_govs_utf8.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(out))

print("Saved scenarios_empty_govs_utf8.txt")
