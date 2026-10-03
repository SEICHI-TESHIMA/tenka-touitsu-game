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

def is_capital(p, o, s):
    cm = clan_master.get(o)
    if cm and cm.get('capital') == p: return True
    owned = [k for k, v in s.get('owners', {}).items() if v == o]
    return owned and owned[0] == p

officers_by_id = {o['id']: o for o in officers}
officers_by_name = {o['name']: o for o in officers}

# Intelligent assignment algorithm
total_reassigned = 0

for scen in scenarios:
    sid = str(scen['id'])
    year = scen['year']
    title = scen['title']
    owners = scen.get('owners', {})
    scen_h = hist_govs.setdefault(sid, {})
    
    # alive pool
    alive = [o for o in officers if o.get('birthYear') is not None and o.get('deathYear') is not None and (year - o['birthYear'] >= 15) and (year <= o['deathYear'])]
    
    assigned_officers = set()
    
    # 1. First, reserve daimyos at capitals
    for p, o in owners.items():
        if not o: continue
        if is_capital(p, o, scen):
            d_cand = next((al for al in alive if al.get('clanId') == o and al['id'] not in assigned_officers), None)
            if d_cand:
                assigned_officers.add(d_cand['id'])
                
    # 2. Check existing hist_govs entries: keep if alive and available
    for p, target in list(scen_h.items()):
        if not target: continue
        match = next((al for al in alive if (al['id'] == target or al['name'] == target) and al['id'] not in assigned_officers), None)
        if match:
            scen_h[p] = match['id']
            assigned_officers.add(match['id'])
        else:
            del scen_h[p] # dead or invalid in this year!
            
    # 3. For any branch province without a governor, find the best alive historical officer!
    for p, o in owners.items():
        if not o: continue
        if is_capital(p, o, scen): continue
        if p in scen_h: continue # already has valid governor
        
        # Candidate selection priority:
        # Priority 1: same owner clan + same defaultProv
        cand = next((al for al in alive if al.get('clanId') == o and al.get('defaultProv') == p and al['id'] not in assigned_officers), None)
        
        # Priority 2: same defaultProv (historical ruler/clan of this province)
        if not cand:
            cand = next((al for al in alive if al.get('defaultProv') == p and al['id'] not in assigned_officers), None)
            
        # Priority 3: same owner clan
        if not cand:
            cand = next((al for al in alive if al.get('clanId') == o and al['id'] not in assigned_officers), None)
            
        if cand:
            scen_h[p] = cand['id']
            assigned_officers.add(cand['id'])
            total_reassigned += 1

print(f"Intelligently assigned {total_reassigned} missing/dead historical governors across scenarios!")

# Write updated hist_govs back to js/data.js
new_gov_json = json.dumps(hist_govs, ensure_ascii=False, indent=2)
new_text = text[:idx_gov + len('window.SCENARIO_HISTORICAL_GOVERNORS = ')] + new_gov_json + text[end_idx_gov-1:]

with open('js/data.js', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Saved updated SCENARIO_HISTORICAL_GOVERNORS to js/data.js successfully.")
