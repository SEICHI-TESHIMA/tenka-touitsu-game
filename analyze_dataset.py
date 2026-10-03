# -*- coding: utf-8 -*-
import json
import re

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# SCENARIOS_DATA
scenarios_match = re.search(r'window\.SCENARIOS_DATA\s*=\s*(\[.*?\]);\s*\n\s*(?:window|const|let|var)', text, re.DOTALL)
if not scenarios_match:
    # try finding matching brackets
    start = text.find('window.SCENARIOS_DATA = [')
    if start != -1:
        # find matching bracket
        count = 0
        end = -1
        for i in range(start + len('window.SCENARIOS_DATA = '), len(text)):
            if text[i] == '[':
                count += 1
            elif text[i] == ']':
                count -= 1
                if count == 0:
                    end = i + 1
                    break
        scenarios_json = text[start + len('window.SCENARIOS_DATA = '):end]
        scenarios = json.loads(scenarios_json)
else:
    scenarios = json.loads(scenarios_match.group(1))

with open('scenarios_info.txt', 'w', encoding='utf-8') as out:
    for s in scenarios:
        out.write(f"id: {s.get('id')}, name: {s.get('name')}, year: {s.get('year')}, daimyoCount: {len(s.get('daimyos', []))}\n")

# OFFICERS_MASTER
start_officers = text.find('window.OFFICERS_MASTER = [')
if start_officers != -1:
    count = 0
    end = -1
    for i in range(start_officers + len('window.OFFICERS_MASTER = '), len(text)):
        if text[i] == '[':
            count += 1
        elif text[i] == ']':
            count -= 1
            if count == 0:
                end = i + 1
                break
    officers_json = text[start_officers + len('window.OFFICERS_MASTER = '):end]
    officers = json.loads(officers_json)
    with open('officers_summary.txt', 'w', encoding='utf-8') as out:
        out.write(f'Total officers in OFFICERS_MASTER: {len(officers)}\n')
        if officers:
            out.write(f'Sample keys: {list(officers[0].keys())}\n')
            short_descs = []
            for o in officers:
                desc = o.get('description', '')
                if len(desc) < 40:
                    short_descs.append((o.get('id'), o.get('name'), desc))
            out.write(f'Short descs (< 40 chars): {len(short_descs)} / {len(officers)}\n')
            out.write('Sample short descs:\n')
            for oid, name, desc in short_descs[:30]:
                out.write(f'  [{oid}] {name}: {desc}\n')

print('Done analysis script.')
