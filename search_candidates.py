# -*- coding: utf-8 -*-
"""
中世・戦国・江戸シナリオの城代に対して、既存武将で充当できるかを調べるスクリプト。
"""
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

officers = extract_js_var('window.OFFICERS_MASTER', text)

# search for candidates for medieval / sengoku / edo jodai
queries = [
    '内藤隆春', '市川経好', '内藤元盛', '福原貞俊', '福原広俊', '熊谷信直', '口羽通良',
    '益田藤兼', '益田元祥', '吉川広家', '吉川元長', '隠岐為清', '隠岐清政', '正木頼忠', '正木時茂',
    '佐々木経高', '佐々木重清', '大内教幸', '細川持賢', '黒川春成', '麻生家春', '問註所', '安東政季',
    '浪岡', '隠岐清忠', '青山忠裕', '京極高備', '仙石久道', '亀井矩貞', '三浦前次', '板倉勝政',
    '松平頼謙', '松平親貞', '樺山久言', '松平直恒', '稲田敏植'
]

with open('candidate_search_results.txt', 'w', encoding='utf-8') as out:
    for q in queries:
        found = [o for o in officers if q in o.get('name', '') or q in o.get('lore', '')]
        out.write(f"Query [{q}]: {len(found)} hits\n")
        for f in found:
            out.write(f"   [{f['id']}] {f['name']} ({f.get('clanId')}, {f.get('birthYear')}-{f.get('deathYear')}): {f.get('lore')}\n")

print("Wrote candidate_search_results.txt")
