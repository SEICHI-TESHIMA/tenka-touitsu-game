# -*- coding: utf-8 -*-
"""
平安時代シナリオ（939, 1028, 1056, 1087, 1156）の城代国を抽出し、
必要な史実武将・国司・受領を調査するスクリプト。
"""
import json

with open('scenarios_jodai_scan.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Already extracted in jodai_detailed_analysis.txt!
# Let's inspect which officers already exist in OFFICERS_MASTER for ancient / heian era!
with open('js/data.js', 'r', encoding='utf-8') as f:
    data_text = f.read()

def extract_js_var(var_name, t):
    start = t.find(var_name + ' = [')
    if start == -1: return None
    start_content = start + len(var_name + ' = ')
    count, end = 0, -1
    for i in range(start_content, len(t)):
        if t[i] == '[': count += 1
        elif t[i] == ']':
            count -= 1
            if count == 0:
                end = i + 1
                break
    return json.loads(t[start_content:end])

officers = extract_js_var('window.OFFICERS_MASTER', data_text)

ancient_heian = [o for o in officers if (o.get('birthYear') or 2000) <= 1180]

with open('ancient_heian_officers.txt', 'w', encoding='utf-8') as out:
    out.write(f"Total ancient/heian officers (birth <= 1180): {len(ancient_heian)}\n\n")
    for o in ancient_heian:
        out.write(f"[{o['id']}] {o['name']} ({o.get('clanId')}, {o.get('birthYear')}-{o.get('deathYear')}, prov:{o.get('defaultProv')}): {o.get('lore')}\n")

print(f"Total ancient/heian officers: {len(ancient_heian)}")
