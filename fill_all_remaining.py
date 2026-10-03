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

idx_cm = text.find('window.CLAN_CAPITAL_PROVINCES = {')
end_idx_cm = text.find('\n};', idx_cm) + 3
caps = json.loads(text[idx_cm + len('window.CLAN_CAPITAL_PROVINCES = '):end_idx_cm-1])

officers_map = {o['id']: o for o in officers}

# Apply corrected IDs
corrected = {
    ("1868", "hyuga"): "off_edo_shimazu_1817_184",
    ("1866", "hyuga"): "off_edo_shimazu_1817_184",
    ("1860", "hyuga"): "off_edo_shimazu_1817_184",
    ("1853", "hyuga"): "off_edo_shimazu_1817_184",
    ("1590", "rikuchu"): "off_dm_nanbu_1582",
    ("1587", "rikuchu"): "off_dm_nanbu_1582",
    ("1546", "awa_boshu"): "off_dm_satomi_1546",
    ("1546", "izumo"): "off_dm_amago_1546",
    ("1651", "mutsu"): "off_nanbu_shigenao",
    ("1637", "mutsu"): "off_nanbu_shigenao",
    ("1614", "mutsu"): "off_nanbu_toshinao",
}

for (sid, prov), off_id in corrected.items():
    if off_id in officers_map:
        hist_govs.setdefault(sid, {})[prov] = off_id

def is_capital_correct(p, o, owners):
    registered = caps.get(o)
    owned = [k for k, v in owners.items() if v == o]
    if registered and registered in owned:
        return p == registered
    return owned and owned[0] == p

# Full auto-filler for all remaining scenarios
filled_total = 0
for scen in scenarios:
    sid = str(scen['id'])
    year = scen['year']
    owners = scen.get('owners', {})
    scen_h = hist_govs.setdefault(sid, {})
    
    alive = [o for o in officers if o.get('birthYear') is not None and o.get('deathYear') is not None and (year - o['birthYear'] >= 15) and (year <= o['deathYear'])]
    alive_by_prov = {}
    alive_by_clan = {}
    for al in alive:
        dp = al.get('defaultProv')
        c = al.get('clanId')
        if dp: alive_by_prov.setdefault(dp, []).append(al)
        if c: alive_by_clan.setdefault(c, []).append(al)
        
    used_ids = set()
    # capital daimyos
    for p, o in owners.items():
        if not o: continue
        if is_capital_correct(p, o, owners):
            c_cand = next((al for al in alive if al.get('clanId') == o and al['id'] not in used_ids), None)
            if c_cand: used_ids.add(c_cand['id'])
            
    # existing govs
    for p, g in scen_h.items():
        if g in officers_map: used_ids.add(g)
        
    # fill empty branches
    for p, o in owners.items():
        if not o: continue
        if is_capital_correct(p, o, owners): continue
        if scen_h.get(p) and scen_h[p] in officers_map: continue
        
        # 1. same prov + same clan
        cand = next((al for al in alive_by_prov.get(p, []) if al.get('clanId') == o and al['id'] not in used_ids), None)
        # 2. same prov
        if not cand:
            cand = next((al for al in alive_by_prov.get(p, []) if al['id'] not in used_ids), None)
        # 3. same clan
        if not cand:
            cand = next((al for al in alive_by_clan.get(o, []) if al['id'] not in used_ids), None)
        # 4. any alive officer not used
        if not cand:
            cand = next((al for al in alive if al['id'] not in used_ids and not al.get('isDaimyo')), None)
            
        if cand:
            scen_h[p] = cand['id']
            used_ids.add(cand['id'])
            filled_total += 1

print(f"Auto-filled {filled_total} remaining governors across all scenarios!")

# Write to js/data.js
new_gov_json = json.dumps(hist_govs, ensure_ascii=False, indent=2)
new_text = text[:idx_gov + len('window.SCENARIO_HISTORICAL_GOVERNORS = ')] + new_gov_json + text[end_idx_gov-1:]

with open('js/data.js', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Saved js/data.js successfully.")
