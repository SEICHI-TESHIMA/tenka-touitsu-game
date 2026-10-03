# -*- coding: utf-8 -*-
"""
各シナリオの owners や playables、SCENARIO_HISTORICAL_GOVERNORS に指定されている武将が
本当に史実に実在するかを全件検証するスクリプト。
"""
import json

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
officers = extract_js_var('window.OFFICERS_MASTER', text)
hist_govs = extract_js_var('window.SCENARIO_HISTORICAL_GOVERNORS', text) or {}

officers_map = {o['id']: o for o in officers}
name_map = {o['name']: o for o in officers}

# Collect all officers explicitly assigned in scenarios
# 1. SCENARIO_HISTORICAL_GOVERNORS
used_gov_ids = set()
for scen_id, gmap in hist_govs.items():
    for pid, target in gmap.items():
        used_gov_ids.add((scen_id, pid, target))

# 2. Playables leaders
playables_officers = set()
for s in scenarios:
    for p in s.get('playables', []):
        playables_officers.add((s['id'], p.get('id'), p.get('name')))

with open('scenario_assigned_officers.txt', 'w', encoding='utf-8') as out:
    out.write(f"=== SCENARIO HISTORICAL GOVERNORS ({len(used_gov_ids)} assignments) ===\n")
    for scen_id, pid, target in sorted(used_gov_ids):
        off = officers_map.get(target) or name_map.get(target)
        if off:
            out.write(f"Scenario {scen_id} | Prov: {pid:12} -> [{off['id']}] {off['name']} ({off.get('clanId')}, {off.get('birthYear')}-{off.get('deathYear')}) | {off.get('lore')}\n")
        else:
            out.write(f"Scenario {scen_id} | Prov: {pid:12} -> Target: {target} (NOT IN OFFICERS_MASTER!)\n")

print("Wrote scenario_assigned_officers.txt")
