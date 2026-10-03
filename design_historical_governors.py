# -*- coding: utf-8 -*-
"""
全233箇所の城代に対して、史実武将をマッピングする設計スクリプト。
"""
import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    data_text = f.read()

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

scenarios = extract_js_var('window.SCENARIOS_DATA', data_text)
officers = extract_js_var('window.OFFICERS_MASTER', data_text)
hist_govs = extract_js_var('window.SCENARIO_HISTORICAL_GOVERNORS', data_text) or {}
provinces = extract_js_var('window.PROVINCES_DATA', data_text) or []

# Read jodai detailed analysis
with open('jodai_detailed_analysis.txt', 'r', encoding='utf-8') as f:
    jodai_raw = f.read()

print("Analyzing governor assignment...")
