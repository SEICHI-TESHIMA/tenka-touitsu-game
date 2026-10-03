# -*- coding: utf-8 -*-
import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

def extract_js_var(var_name, t):
    start = t.find(var_name + ' = [')
    if start == -1:
        start = t.find(var_name + ' = {')
        open_char, close_char = '{', '}'
    else:
        open_char, close_char = '[', ']'
    if start == -1: return None
    start_content = start + len(var_name + ' = ')
    count, end = 0, -1
    for i in range(start_content, len(t)):
        if t[i] == open_char: count += 1
        elif t[i] == close_char:
            count -= 1
            if count == 0:
                end = i + 1
                break
    return json.loads(t[start_content:end])

scenarios = extract_js_var('window.SCENARIOS_DATA', text)
officers = extract_js_var('window.OFFICERS_MASTER', text)
hist_govs = extract_js_var('window.SCENARIO_HISTORICAL_GOVERNORS', text) or {}
clan_capitals = extract_js_var('window.CLAN_CAPITAL_PROVINCES', text) or {}
provinces = extract_js_var('window.PROVINCES_DATA', text) or []

prov_names = {p['id']: p['name'] for p in provinces}
officers_by_id = {o['id']: o for o in officers}

with open('diagnose_vacant_results.txt', 'w', encoding='utf-8') as out:
    for scen in scenarios:
        scen_id = str(scen['id'])
        year = int(scen.get('year', 1560))
        title = scen.get('title', scen_id)
        owners = scen.get('owners', {})
        hmap = hist_govs.get(scen_id, {})
        
        # active officers
        active = []
        for o in officers:
            b, d = o.get('birthYear'), o.get('deathYear')
            if b is not None and d is not None:
                if (year - b >= 15) and (year <= d):
                    active.append(dict(o))
        active_ids = {o['id'] for o in active}
        active_names = {o['name'] for o in active}

        # check capitals
        owners_set = set(owners.values())
        capitals = {}
        for cid in owners_set:
            if not cid: continue
            owned_pids = [pid for pid, o in owners.items() if o == cid]
            pref = clan_capitals.get(cid)
            if pref and pref in owned_pids:
                capitals[cid] = pref
            elif owned_pids:
                capitals[cid] = owned_pids[0]

        vacant_reasons = []
        # check each province
        for pid, cid in owners.items():
            if not cid: continue
            if capitals.get(cid) == pid:
                # capital -> has daimyo?
                d_off = next((o for o in active if o.get('clanId') == cid and o.get('isDaimyo')), None)
                if not d_off:
                    # direct daimyo rule, not jodai
                    pass
                continue
            
            # branch castle
            target = hmap.get(pid)
            if not target:
                vacant_reasons.append((pid, prov_names.get(pid, pid), cid, "histGovMapに未登録"))
            else:
                # check if target exists and is active
                if target not in active_ids and target not in active_names:
                    # check if exists in master at all
                    m_off = officers_by_id.get(target)
                    if not m_off:
                        vacant_reasons.append((pid, prov_names.get(pid, pid), cid, f"Target '{target}' がOFFICERS_MASTERに不在"))
                    else:
                        b, d = m_off.get('birthYear'), m_off.get('deathYear')
                        vacant_reasons.append((pid, prov_names.get(pid, pid), cid, f"Target '{target}' がシナリオ年({year}年)に生存・元服していない (生没: {b}-{d})"))
                else:
                    # check if target isDaimyo
                    cand = next((o for o in active if o.get('id') == target or o.get('name') == target), None)
                    if cand and cand.get('isDaimyo'):
                        vacant_reasons.append((pid, prov_names.get(pid, pid), cid, f"Target '{target}' が大名フラグ(isDaimyo:true)のため弾かれた"))

        if vacant_reasons:
            out.write(f"=== シナリオ {scen_id} ({year}年 {title}) 城代原因: {len(vacant_reasons)} 件 ===\n")
            for pid, pname, cid, reason in vacant_reasons:
                out.write(f"   {pid:14} {pname:6} (勢力: {cid:15}): {reason}\n")
            out.write("\n")

print("Diagnosis done.")
