import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('window.OFFICERS_MASTER = [')
end_idx = text.find('\n];', start_idx) + 2
officers = json.loads(text[start_idx + len('window.OFFICERS_MASTER = '):end_idx])
officers_map = {o['id']: o for o in officers}

start_idx_scen = text.find('window.SCENARIOS_DATA = [')
end_idx_scen = text.find('\n];', start_idx_scen) + 2
scenarios = json.loads(text[start_idx_scen + len('window.SCENARIOS_DATA = '):end_idx_scen])

idx_gov = text.find('window.SCENARIO_HISTORICAL_GOVERNORS = {')
end_idx_gov = text.find('\n};', idx_gov) + 3
hist_govs = json.loads(text[idx_gov + len('window.SCENARIO_HISTORICAL_GOVERNORS = '):end_idx_gov-1])

idx_cm = text.find('window.CLAN_CAPITAL_PROVINCES = {')
end_idx_cm = text.find('\n};', idx_cm) + 3
caps = json.loads(text[idx_cm + len('window.CLAN_CAPITAL_PROVINCES = '):end_idx_cm-1])

with open('js/historical_jodai.js', 'r', encoding='utf-8') as f:
    jodai_text = f.read()

m_reuse = re.search(r'const reuse = (\[.*?\]);', jodai_text, re.DOTALL)
if m_reuse:
    clean_reuse = re.sub(r'(\b[a-zA-Z_]\w*\b)\s*:', r'"\1":', m_reuse.group(1))
    clean_reuse = re.sub(r',\s*([\]}])', r'\1', clean_reuse)
    reuse = json.loads(clean_reuse)
    for row in reuse:
        hist_govs.setdefault(str(row['year']), {})[row['prov']] = row['id']

def is_capital_correct(p, o, owners):
    registered = caps.get(o)
    owned = [k for k, v in owners.items() if v == o]
    if registered and registered in owned:
        return p == registered
    return owned and owned[0] == p

scen_939 = next(s for s in scenarios if str(s['id']) == '939')
owners_939 = scen_939.get('owners', {})
govs_939 = hist_govs.get('939', {})

print("Empty provinces in 939:")
for p, o in owners_939.items():
    if not o: continue
    if not is_capital_correct(p, o, owners_939) and not officers_map.get(govs_939.get(p)):
        print(f"  prov:{p:<15} owner:{o:<20}")
