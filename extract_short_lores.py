# -*- coding: utf-8 -*-
"""
OFFICERS_MASTER 内の武将で、列伝が短い（手抜き感のある）武将を抽出するスクリプト。
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

short_officers = []
for o in officers:
    lore = o.get('lore', '')
    if len(lore) < 60:
        short_officers.append((o['id'], o['name'], o.get('clanId'), o.get('birthYear'), o.get('deathYear'), lore, len(lore)))

short_officers.sort(key=lambda x: x[6])

with open('short_lore_officers.txt', 'w', encoding='utf-8') as out:
    out.write(f"Total short lore officers (< 60 chars): {len(short_officers)} / {len(officers)}\n\n")
    for oid, name, clan, b, d, lore, length in short_officers:
        out.write(f"[{oid}] {name} ({clan}, {b}-{d}) [文字数: {length}]\n  現行: {lore}\n\n")

print(f"Total short lore officers (< 60 chars): {len(short_officers)}")
