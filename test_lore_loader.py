# -*- coding: utf-8 -*-
"""
全武将の列伝を史実リサーチに基づき、手抜き感のない本格的な歴史列伝（100〜160文字）に拡充するエンジン。
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

print(f"Total officers loaded for lore expansion: {len(officers)}")
