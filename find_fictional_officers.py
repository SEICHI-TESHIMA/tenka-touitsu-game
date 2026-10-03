# -*- coding: utf-8 -*-
"""
OFFICERS_MASTER 内の全武将について、実在・非実在・架空・総称の可能性を徹底調査するスクリプト。
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

officers = extract_js_var('window.OFFICERS_MASTER', text)
scenarios = extract_js_var('window.SCENARIOS_DATA', text)
hist_govs = extract_js_var('window.SCENARIO_HISTORICAL_GOVERNORS', text) or {}

# Check which officers actually appear in scenarios
# For each scenario, an officer appears if:
# (scen.year - birthYear >= 15) and (scen.year <= deathYear)
appeared_officers = set()
for s in scenarios:
    y = int(s['year'])
    for o in officers:
        b = o.get('birthYear')
        d = o.get('deathYear')
        if b is not None and d is not None:
            if (y - b >= 15) and (y <= d):
                appeared_officers.add(o['id'])

with open('fictional_investigation.txt', 'w', encoding='utf-8') as out:
    out.write(f"Total officers: {len(officers)}\n")
    out.write(f"Officers appearing in at least one scenario: {len(appeared_officers)}\n\n")

    # Check suspicious patterns in name
    # 1. Generic names like '酋長', '豪族', '郡司', '国司', etc.
    # 2. Names with parentheses like '島津忠久(祖)', '大隅豪族(三代)'
    # 3. Known fictional ninja/characters (猿飛佐助, 霧隠才蔵, 望月六郎, 筧十蔵, 穴山小助, 三好清海入道, 三好伊三入道, 根津甚八, 由利鎌之助, 海野六郎 etc.)
    # 4. Successor placeholders with generic generated names
    suspicious = []
    sanada_ten = ['猿飛佐助', '霧隠才蔵', '三好清海', '三好伊三', '筧十蔵', '由利鎌之助', '穴山小助'] # check if in game
    
    for o in officers:
        name = o.get('name', '')
        oid = o.get('id', '')
        reasons = []
        
        # Check generic titles
        if any(w in name for w in ['酋長', '豪族', '郡司', '国司', '商人', '忍者', '代官', '海賊', '土豪', '一族', '家臣', '門徒', '農民']):
            reasons.append("総称・役職・身分名")
        if name.endswith('氏') and len(name) > 3:
            reasons.append("氏族名のみ（個人名でない）")
        if '(' in name or '（' in name or '祖' in name or '三代' in name or '初代' in name or '二代' in name:
            reasons.append("世代記号・祖・代名")
        for st in sanada_ten:
            if st in name:
                reasons.append("架空の真田十勇士")
        if any(w in oid for w in ['dummy', 'fake', 'temp', 'placeholder']):
            reasons.append("IDにダミー表記")
            
        if reasons:
            suspicious.append((o, reasons, o['id'] in appeared_officers))

    out.write(f"Suspicious officers count: {len(suspicious)}\n\n")
    for o, reasons, in_scen in suspicious:
        out.write(f"[{o['id']}] {o['name']} ({o.get('clanId')}, {o.get('birthYear')}-{o.get('deathYear')}) - 配置シナリオあり: {in_scen}\n")
        out.write(f"   理由: {', '.join(reasons)}\n")
        out.write(f"   列伝: {o.get('lore')}\n\n")

print("Done fictional investigation.")
