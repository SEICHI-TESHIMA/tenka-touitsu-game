# -*- coding: utf-8 -*-
"""
短い列伝（一言コメント）の全パターンを分類し、
それぞれの歴史的事実に基づく充実した列伝（100〜160文字）を生成するエンジン。
"""
import json
import re

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

officers = extract_js_var('window.OFFICERS_MASTER', text)
provinces = extract_js_var('window.PROVINCES_DATA', text) or []
prov_map = {p['id']: p['name'] for p in provinces}

short_officers = [o for o in officers if len(o.get('lore', '')) < 60]

print(f"Total short lore officers: {len(short_officers)}")

# Let's inspect common short lore patterns
patterns = {}
for o in short_officers:
    lore = o.get('lore', '').strip()
    if '藩主' in lore:
        patterns.setdefault('藩主系', []).append(o)
    elif '城主' in lore:
        patterns.setdefault('城主系', []).append(o)
    elif '守護' in lore or '守' in lore:
        patterns.setdefault('守護・受領系', []).append(o)
    elif '継いだ' in lore or '受けた' in lore or '後を' in lore:
        patterns.setdefault('後継・継承系', []).append(o)
    elif '家臣' in lore or '仕えた' in lore or '従い' in lore:
        patterns.setdefault('家臣・従軍系', []).append(o)
    elif '子。' in lore or '弟。' in lore or '父。' in lore:
        patterns.setdefault('血縁・一族系', []).append(o)
    else:
        patterns.setdefault('その他', []).append(o)

for p, olist in patterns.items():
    print(f"  {p}: {len(olist)} 名 (例: {olist[0]['name']} -> \"{olist[0]['lore']}\")")
