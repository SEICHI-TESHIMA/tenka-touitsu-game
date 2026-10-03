# -*- coding: utf-8 -*-
"""
全34シナリオにおいて、各国の領主・本拠地・城主（governorId）をシミュレーションし、
「城代（城主不在）」となっている国をすべて洗い出すスクリプト。
"""
import json
import re

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

def extract_js_var(var_name, text):
    start = text.find(var_name + ' = [')
    if start == -1:
        start = text.find(var_name + ' = {')
        open_char, close_char = '{', '}'
    else:
        open_char, close_char = '[', ']'
    if start == -1:
        return None
    
    start_content = start + len(var_name + ' = ')
    count = 0
    end = -1
    for i in range(start_content, len(text)):
        if text[i] == open_char:
            count += 1
        elif text[i] == close_char:
            count -= 1
            if count == 0:
                end = i + 1
                break
    if end != -1:
        return json.loads(text[start_content:end])
    return None

scenarios = extract_js_var('window.SCENARIOS_DATA', text)
officers_master = extract_js_var('window.OFFICERS_MASTER', text)
hist_govs = extract_js_var('window.SCENARIO_HISTORICAL_GOVERNORS', text) or {}
provinces_data = extract_js_var('window.PROVINCES_DATA', text) or []
clan_master = extract_js_var('window.CLAN_MASTER_DATA', text) or {}
clan_capitals = extract_js_var('window.CLAN_CAPITAL_PROVINCES', text) or {}

prov_names = {p['id']: p['name'] for p in provinces_data}

# also read historical_jodai.js if it exists to see what it injects
try:
    with open('js/historical_jodai.js', 'r', encoding='utf-8') as f:
        jodai_code = f.read()
except Exception:
    jodai_code = ""

results = []

for scen in scenarios:
    scen_id = str(scen['id'])
    year = int(scen.get('year', 1560))
    scen_title = scen.get('title', scen_id)
    owners = scen.get('owners', {})
    
    # 1. filter active officers
    # age >= 15 and alive
    active = []
    for m in officers_master:
        b = m.get('birthYear')
        d = m.get('deathYear')
        if b is not None and d is not None:
            age = year - int(b)
            if age >= 15 and year <= int(d):
                o = dict(m)
                o['assignedProvId'] = None
                active.append(o)
    
    # identify owners present on map
    owners_set = set(owners.values())
    
    # identify capital for each clan
    # app.js rule:
    # 1) CLAN_CAPITAL_PROVINCES if owned
    # 2) playables home/capital
    # 3) largest kokudaka among owned
    capital_by_clan = {}
    for cid in owners_set:
        if not cid: continue
        # candidates
        owned_pids = [pid for pid, o in owners.items() if o == cid]
        if not owned_pids: continue
        pref = clan_capitals.get(cid)
        if pref and pref in owned_pids:
            capital_by_clan[cid] = pref
        else:
            capital_by_clan[cid] = owned_pids[0]

    # histGovMap
    hist_gov_map = hist_govs.get(scen_id, {})

    # simulate assignment
    gov_by_prov = {} # pid -> officer_id or None
    
    # Step 1: capital gets daimyo
    for pid, cid in owners.items():
        if not cid: continue
        if capital_by_clan.get(cid) == pid:
            # find daimyo officer
            daimyo_off = next((o for o in active if o.get('clanId') == cid and o.get('isDaimyo') and not o.get('assignedProvId')), None)
            if daimyo_off:
                gov_by_prov[pid] = daimyo_off['id']
                daimyo_off['assignedProvId'] = pid
            else:
                gov_by_prov[pid] = 'daimyo_direct' # direct daimyo rule

    # Step 2: branch castles
    # 2-A: histGovMap
    for pid, cid in owners.items():
        if not cid or pid in gov_by_prov: continue
        target_name_or_id = hist_gov_map.get(pid)
        if target_name_or_id:
            # find matching officer
            matched = next((o for o in active if (o.get('id') == target_name_or_id or o.get('name') == target_name_or_id) and not o.get('assignedProvId')), None)
            if matched:
                gov_by_prov[pid] = matched['id']
                matched['assignedProvId'] = pid

    # 2-B: matching defaultProv and clanId
    for pid, cid in owners.items():
        if not cid or pid in gov_by_prov: continue
        matched = next((o for o in active if o.get('clanId') == cid and o.get('defaultProv') == pid and not o.get('assignedProvId') and not o.get('isDaimyo')), None)
        if matched:
            gov_by_prov[pid] = matched['id']
            matched['assignedProvId'] = pid

    # 2-C: highest ability remaining officer of clan
    no_auto = scen.get('noAutoCastellan', False)
    if not no_auto:
        for pid, cid in owners.items():
            if not cid or pid in gov_by_prov: continue
            cands = [o for o in active if o.get('clanId') == cid and not o.get('assignedProvId') and not o.get('isDaimyo')]
            if cands:
                cands.sort(key=lambda o: (o.get('military',0) + o.get('politic',0) + o.get('intel',0)), reverse=True)
                best = cands[0]
                gov_by_prov[pid] = best['id']
                best['assignedProvId'] = pid

    # check which provinces are still vacant / Jodai
    jodai_list = []
    for pid, cid in owners.items():
        if not cid: continue
        if pid not in gov_by_prov:
            jodai_list.append((pid, prov_names.get(pid, pid), cid))

    results.append({
        'scen_id': scen_id,
        'year': year,
        'title': scen_title,
        'jodai_count': len(jodai_list),
        'jodai_provs': jodai_list
    })

with open('scenarios_jodai_scan.txt', 'w', encoding='utf-8') as out:
    total_jodai = sum(r['jodai_count'] for r in results)
    out.write(f"Total jodai (vacant) castle instances across all scenarios: {total_jodai}\n\n")
    for r in results:
        out.write(f"Scenario [{r['scen_id']}] {r['year']}年 {r['title']}: {r['jodai_count']} 城代\n")
        if r['jodai_provs']:
            for pid, pname, cid in r['jodai_provs']:
                out.write(f"   - {pid} ({pname}) [勢力: {cid}]\n")

print(f"Total jodai instances: {total_jodai}")
