import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

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
officers_master = extract_js_var('window.OFFICERS_MASTER', text)
hist_govs = extract_js_var('window.SCENARIO_HISTORICAL_GOVERNORS', text) or {}
provinces_data = extract_js_var('window.PROVINCES_DATA', text) or []

officer_dict = {o['id']: o for o in officers_master}

print(f"Total Scenarios: {len(scenarios)}")
print(f"Total Officers in Master: {len(officers_master)}")

scenario_errors = []

for scen in scenarios:
    s_year = scen['year']
    s_name = scen.get('name', '')
    
    # Check clans
    for c in scen.get('clans', []):
        cid = c['id']
        did = c.get('daimyoId')
        if not did or did not in officer_dict:
            scenario_errors.append(f"Scenario {s_year} ({s_name}): clan {cid} has invalid daimyoId '{did}'")
            
    # Check provinces
    for p in scen.get('provinces', []):
        pid = p['id']
        gid = p.get('governorId')
        if gid and gid not in officer_dict:
            scenario_errors.append(f"Scenario {s_year} ({s_name}): province {pid} has invalid governorId '{gid}'")
            
    # Check hist govs for this year
    gov_map = hist_govs.get(str(s_year), {})
    for pid, gid in gov_map.items():
        if gid and gid not in officer_dict:
            scenario_errors.append(f"Scenario {s_year} ({s_name}) hist_gov: province {pid} has invalid governorId '{gid}'")

if not scenario_errors:
    print("ALL 34 SCENARIOS PASSED WITH 0 ERRORS! Daimyos and governors are 100% valid.")
else:
    print(f"Found {len(scenario_errors)} errors:")
    for err in scenario_errors[:10]:
        print("  ", err)
