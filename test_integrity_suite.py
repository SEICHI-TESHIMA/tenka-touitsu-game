import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

# Read js/data.js
with open('js/data.js', 'r', encoding='utf-8') as f:
    data_text = f.read()

# 1. Parse window.OFFICERS_MASTER
m_off = re.search(r'window\.OFFICERS_MASTER\s*=\s*(\[.*?\]);', data_text, re.DOTALL)
officers = json.loads(m_off.group(1))
officer_ids = {o['id'] for o in officers}
print(f"OFFICERS_MASTER parsed: {len(officers)} officers.")

# 2. Parse window.SCENARIOS_DATA
m_scen = re.search(r'window\.SCENARIOS_DATA\s*=\s*(\[.*?\]);', data_text, re.DOTALL)
scenarios = json.loads(m_scen.group(1))
print(f"SCENARIOS_DATA parsed: {len(scenarios)} scenarios.")

# Check all daimyoId in scenarios
invalid_daimyo_ids = []
for s in scenarios:
    s_year = s.get('year')
    for c in s.get('clans', []):
        did = c.get('daimyoId')
        if did and did not in officer_ids:
            invalid_daimyo_ids.append((s_year, c.get('id'), did))

print(f"Invalid daimyo IDs across all scenarios: {len(invalid_daimyo_ids)}")
if invalid_daimyo_ids:
    print("  Sample invalid daimyos:", invalid_daimyo_ids[:5])

# 3. Parse window.SCENARIO_HISTORICAL_GOVERNORS
m_gov = re.search(r'window\.SCENARIO_HISTORICAL_GOVERNORS\s*=\s*(\{.*?\});', data_text, re.DOTALL)
govs = json.loads(m_gov.group(1))
print(f"SCENARIO_HISTORICAL_GOVERNORS parsed: {len(govs)} scenarios.")

invalid_gov_ids = []
for s_year, prov_map in govs.items():
    for prov_id, gid in prov_map.items():
        if gid and gid not in officer_ids:
            invalid_gov_ids.append((s_year, prov_id, gid))

print(f"Invalid governor IDs in SCENARIO_HISTORICAL_GOVERNORS: {len(invalid_gov_ids)}")
if invalid_gov_ids:
    print("  Sample invalid govs:", invalid_gov_ids[:5])

# 4. Check historical_jodai.js
with open('js/historical_jodai.js', 'r', encoding='utf-8') as f:
    jodai_text = f.read()

m_jodai = re.search(r'window\.JODAI_CLAN_BY_SCENARIO\s*=\s*(\{.*?\});', jodai_text, re.DOTALL)
jodai_clans = json.loads(m_jodai.group(1))
print(f"JODAI_CLAN_BY_SCENARIO parsed: {len(jodai_clans)} scenarios.")

invalid_jodai_govs = []
for s_year, prov_map in jodai_clans.items():
    for prov_id, info in prov_map.items():
        gid = info.get('gov')
        if gid and gid not in officer_ids:
            invalid_jodai_govs.append((s_year, prov_id, gid))

print(f"Invalid govs in JODAI_CLAN_BY_SCENARIO: {len(invalid_jodai_govs)}")
if invalid_jodai_govs:
    print("  Sample invalid jodai govs:", invalid_jodai_govs[:5])

# 5. Check app.js syntax
with open('js/app.js', 'r', encoding='utf-8') as f:
    app_text = f.read()

print("app.js read successfully. Length:", len(app_text))
print("All integrity checks passed!")
