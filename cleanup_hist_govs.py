import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('window.OFFICERS_MASTER = [')
end_idx = text.find('\n];', start_idx) + 2
officers = json.loads(text[start_idx + len('window.OFFICERS_MASTER = '):end_idx])

start_idx = text.find('window.SCENARIOS_DATA = [')
end_idx = text.find('\n];', start_idx) + 2
scenarios = json.loads(text[start_idx + len('window.SCENARIOS_DATA = '):end_idx])

idx = text.find('window.SCENARIO_HISTORICAL_GOVERNORS = {')
end_idx = text.find('\n};', idx) + 3
hist_govs = json.loads(text[idx + len('window.SCENARIO_HISTORICAL_GOVERNORS = '):end_idx-1])

idx = text.find('window.CLAN_MASTER_DATA = {')
end_idx = text.find('\n};', idx) + 3
clan_master = json.loads(text[idx + len('window.CLAN_MASTER_DATA = '):end_idx-1])

def is_capital(p, o, s):
    cm = clan_master.get(o)
    if cm and cm.get('capital') == p: return True
    owned = [k for k, v in s.get('owners', {}).items() if v == o]
    return owned and owned[0] == p

# Build pool of alive officers per scenario
for scen in scenarios:
    sid = str(scen['id'])
    year = scen['year']
    title = scen['title']
    owners = scen.get('owners', {})
    scen_h = hist_govs.setdefault(sid, {})
    
    # Alive officers
    alive = [o for o in officers if o.get('birthYear') is not None and o.get('deathYear') is not None and (year - o['birthYear'] >= 15) and (year <= o['deathYear'])]
    
    # Find which officers are already assigned as daimyo (capital) or governor
    used_officer_ids = set()
    
    # Daimyos
    for p, o in owners.items():
        if not o: continue
        if is_capital(p, o, scen):
            # find daimyo
            d_cand = next((al for al in alive if al.get('clanId') == o and al['id'] not in used_officer_ids), None)
            if d_cand:
                used_officer_ids.add(d_cand['id'])
                
    # Valid existing governors in hist_govs
    for p, target in list(scen_h.items()):
        if target:
            # check if target is alive and valid
            match = next((al for al in alive if (al['id'] == target or al['name'] == target) and al['id'] not in used_officer_ids), None)
            if match:
                used_officer_ids.add(match['id'])
            else:
                # invalid or dead! remove to reassign
                del scen_h[p]

print("Cleaned up dead/invalid targets in hist_govs.")
