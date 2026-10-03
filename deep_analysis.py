# -*- coding: utf-8 -*-
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

scenarios = extract_js_var('window.SCENARIOS_DATA', text)
officers = extract_js_var('window.OFFICERS_MASTER', text)
jodai_govs = extract_js_var('window.SCENARIO_HISTORICAL_GOVERNORS', text)

with open('deep_analysis.txt', 'w', encoding='utf-8') as out:
    out.write("=== SCENARIOS SAMPLE ===\n")
    if scenarios:
        out.write(f"Count: {len(scenarios)}\n")
        out.write(f"First scenario keys: {list(scenarios[0].keys())}\n")
        for s in scenarios:
            title = s.get('title') or s.get('name') or s.get('label')
            out.write(f"ID: {s.get('id')}, Year: {s.get('year')}, Title: {title}, Clans: {len(s.get('clans', [])) if 'clans' in s else 'no clans key'}\n")
            if 'provinces' in s:
                out.write(f"  Provinces count: {len(s['provinces'])}\n")

    out.write("\n=== OFFICERS LORE & NAMES ===\n")
    if officers:
        out.write(f"Total officers: {len(officers)}\n")
        out.write(f"Sample officer: {json.dumps(officers[0], ensure_ascii=False, indent=2)}\n")
        
        # Check lore lengths
        empty_lore = [o for o in officers if not o.get('lore')]
        short_lore = [o for o in officers if o.get('lore') and len(o.get('lore')) < 30]
        long_lore = [o for o in officers if o.get('lore') and len(o.get('lore')) >= 30]
        out.write(f"Empty lore: {len(empty_lore)}\n")
        out.write(f"Short lore (<30): {len(short_lore)}\n")
        out.write(f"Long lore (>=30): {len(long_lore)}\n")

        # Sample short lores
        out.write("\nSample short lores (first 20):\n")
        for o in short_lore[:20]:
            out.write(f"  [{o.get('id')}] {o.get('name')}: \"{o.get('lore')}\"\n")

    out.write("\n=== SCENARIO_HISTORICAL_GOVERNORS ===\n")
    if jodai_govs:
        out.write(f"Jodai Govs keys: {list(jodai_govs.keys())}\n")
        sample_k = list(jodai_govs.keys())[0]
        out.write(f"Sample [{sample_k}]: {jodai_govs[sample_k]}\n")

print('Deep analysis done.')
