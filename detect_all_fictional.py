# -*- coding: utf-8 -*-
"""
実在しない総称武将（蝦夷アイヌ首長、蝦夷族長など）を全て検出する。
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

officers = extract_js_var('window.OFFICERS_MASTER', text)

generic_keywords = [
    '首長', '族長', '酋長', '豪族', '郡司', '国司', '商人', '忍者',
    '真田十勇士', '架空', '名代', '一族', '門徒', '海賊', '土豪'
]

fictional_officers = []
for o in officers:
    name = o.get('name', '')
    lore = o.get('lore', '')
    oid = o.get('id', '')
    hit = False
    for kw in generic_keywords:
        if kw in name or (kw in lore and any(w in name for w in ['アイヌ', '首長', '族長', '酋長', '豪族', '郡司'])):
            hit = True
            break
    if hit:
        fictional_officers.append(o)

# Also check 真田十勇士
sanada_ten = ['猿飛佐助', '霧隠才蔵', '三好清海入道', '三好伊三入道', '穴山小助', '由利鎌之助', '筧十蔵', '海野六郎', '根津甚八', '望月六郎']
for o in officers:
    if o['name'] in sanada_ten and o not in fictional_officers:
        fictional_officers.append(o)

with open('all_fictional_and_generic.txt', 'w', encoding='utf-8') as out:
    out.write(f"Total detected generic / fictional officers: {len(fictional_officers)}\n\n")
    for o in fictional_officers:
        out.write(f"[{o['id']}] {o['name']} ({o.get('clanId')}, {o.get('birthYear')}-{o.get('deathYear')}): {o.get('lore')}\n")

print(f"Total generic / fictional: {len(fictional_officers)}")
