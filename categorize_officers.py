# -*- coding: utf-8 -*-
"""
OFFICERS_MASTER の全武将について、実在性の詳細調査。
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

# Let's inspect officers by era or by clan to spot any weird ones
by_era = {}
for o in officers:
    era = o.get('era', 'unknown')
    by_era.setdefault(era, []).append(o)

with open('officers_by_era.txt', 'w', encoding='utf-8') as out:
    for era, olist in by_era.items():
        out.write(f"=== ERA: {era} (Count: {len(olist)}) ===\n")
        for o in olist:
            out.write(f"  [{o['id']}] {o['name']} ({o.get('clanId')}, {o.get('birthYear')}-{o.get('deathYear')})\n")

print("Wrote officers_by_era.txt")
