# -*- coding: utf-8 -*-
"""
OFFICERS_MASTER 内の全2098武将を一覧化し、
真田十勇士、架空人物、怪しい人物を徹底網羅する。
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

with open('all_officers_names.txt', 'w', encoding='utf-8') as out:
    for i, o in enumerate(officers):
        out.write(f"{i+1}\t{o['id']}\t{o['name']}\t{o.get('clanId')}\t{o.get('birthYear')}\t{o.get('deathYear')}\n")

# Check for specific famous fictional or legendary figures
fictional_patterns = [
    '佐助', '才蔵', '清海', '伊三', '小助', '鎌之助', '十蔵', '甚八', '六郎',
    '弁慶', '牛若丸', '義経', '静御前', '巴御前', '木曽義高',
    '風魔小太郎', '服部半蔵', '百地三太夫', '石川五右衛門', '果心居士',
    '児雷也', '自来也', '自来也', '水戸黄門', '助さん', '格さん',
    '国定忠治', '大前田英五郎', '清水次郎長', '森の石松',
    '酋長', '豪族', '郡司', '国司', '先祖'
]

hits = []
for o in officers:
    for fp in fictional_patterns:
        if fp in o['name']:
            hits.append((o, fp))

with open('fictional_pattern_hits.txt', 'w', encoding='utf-8') as out:
    for o, fp in hits:
        out.write(f"[{fp}] {o['id']}: {o['name']} ({o.get('clanId')}, {o.get('birthYear')}-{o.get('deathYear')}) -> {o.get('lore')}\n")

print(f"Total pattern hits: {len(hits)}")
