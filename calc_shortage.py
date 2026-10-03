# -*- coding: utf-8 -*-
"""
各シナリオで城代になっている国数と、各大名家の領国数、
および重複なしで必要な固有武将の数を算出するスクリプト。
"""
import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

def extract_js_var(var_name, t):
    start = t.find(var_name + ' = [')
    open_char, close_char = '[', ']'
    if start == -1:
        start = t.find(var_name + ' = {')
        open_char, close_char = '{', '}'
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

with open('scenarios_prov_counts.txt', 'w', encoding='utf-8') as out:
    for scen in scenarios:
        scen_id = str(scen['id'])
        year = int(scen.get('year', 1560))
        owners = scen.get('owners', {})
        # count how many provinces each owner has
        counts = {}
        for pid, cid in owners.items():
            if cid:
                counts[cid] = counts.get(cid, 0) + 1
        
        # count how many active officers each owner has
        active_counts = {}
        for o in officers:
            b, d = o.get('birthYear'), o.get('deathYear')
            if b is not None and d is not None:
                if (year - b >= 15) and (year <= d):
                    cid = o.get('clanId')
                    active_counts[cid] = active_counts.get(cid, 0) + 1
                    
        out.write(f"=== Scenario {scen_id} ({year}年 {scen.get('title')}) ===\n")
        for cid, count in sorted(counts.items(), key=lambda x: -x[1]):
            if count > 1:
                active_num = active_counts.get(cid, 0)
                out.write(f"  Clan {cid:20}: {count:2} 領国 (生存武将: {active_num} 名, 不足: {max(0, count - active_num)} 名)\n")

print("Calculated province and officer counts per scenario.")
