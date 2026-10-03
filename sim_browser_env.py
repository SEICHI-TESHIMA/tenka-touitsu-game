# -*- coding: utf-8 -*-
"""
js/data.js と js/historical_jodai.js の両方を読み込み、
ブラウザ上と同じ状態で全34シナリオの城代（governorIdがnullになる国）を精密にシミュレートする。
"""
import json
import re

with open('js/data.js', 'r', encoding='utf-8') as f:
    data_text = f.read()

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

scenarios = extract_js_var('window.SCENARIOS_DATA', data_text)
officers_master = extract_js_var('window.OFFICERS_MASTER', data_text)
hist_govs = extract_js_var('window.SCENARIO_HISTORICAL_GOVERNORS', data_text) or {}
provinces_data = extract_js_var('window.PROVINCES_DATA', data_text) or []
clan_capitals = extract_js_var('window.CLAN_CAPITAL_PROVINCES', data_text) or {}

prov_names = {p['id']: p['name'] for p in provinces_data}

# historical_jodai.js を解析して、OFFICERS_MASTERとSCENARIO_HISTORICAL_GOVERNORSに反映
with open('js/historical_jodai.js', 'r', encoding='utf-8') as f:
    jodai_text = f.read()

# roster を抽出
roster_match = re.search(r'const roster = (\[.*?\]);\s*\n\s*const', jodai_text, re.DOTALL)
if roster_match:
    roster_json_str = roster_match.group(1)
    # roster is in JS object syntax (might not have quotes on keys)
    # let's parse via regex or node
    pass

# safer: use node.js to run both files and inspect window directly!
