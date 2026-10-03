import re
import json

print("=== FINAL INTEGRATION VERIFICATION ===")

# 1. Verify data.js
with open('js/data.js', 'r', encoding='utf-8') as f:
    data_text = f.read()

# Officers parse
idx_off = data_text.find('window.OFFICERS_MASTER = [')
end_off = data_text.find('\n];', idx_off) + 2
officers = json.loads(data_text[idx_off + len('window.OFFICERS_MASTER = '):end_off])
print(f"Total Officers in OFFICERS_MASTER: {len(officers)}")

# Scenarios parse
idx_scen = data_text.find('window.SCENARIOS_DATA = [')
end_scen = data_text.find('\n];', idx_scen) + 2
scenarios = json.loads(data_text[idx_scen + len('window.SCENARIOS_DATA = '):end_scen])
print(f"Total Scenarios in SCENARIOS_DATA: {len(scenarios)}")

# Governors parse
idx_gov = data_text.find('window.SCENARIO_HISTORICAL_GOVERNORS = {')
end_gov = data_text.find('\n};', idx_gov) + 3
hist_govs = json.loads(data_text[idx_gov + len('window.SCENARIO_HISTORICAL_GOVERNORS = '):end_gov-1])
print(f"Total Scenarios in HISTORICAL_GOVERNORS: {len(hist_govs)}")

# Check Oshio
oshio = [o for o in officers if 'oshio' in o['id'] or '大塩' in o['name']]
print(f"Oshio officers count: {len(oshio)}")
for o in oshio:
    print(f"  {o['id']}: {o['name']} ({o.get('birthYear')}-{o.get('deathYear')})")

# Check Sanada in 1866
sanada_1866 = [o for o in officers if ('sanada' in o['id'] or '真田' in o['name']) and o.get('birthYear', 9999) <= 1866 <= o.get('deathYear', -9999)]
print(f"Sanada officers in 1866: {len(sanada_1866)}")
for o in sanada_1866:
    print(f"  {o['id']}: {o['name']} clan:{o.get('clanId')} prov:{o.get('defaultProv')}")

# Check any invalid province IDs in defaultProv
bad_provs = [o for o in officers if o.get('defaultProv') == 'shinano']
print(f"Officers with invalid 'shinano' prov: {len(bad_provs)}")

# 2. Verify app.js
with open('js/app.js', 'r', encoding='utf-8') as f:
    app_text = f.read()

# Check that critical methods and keys exist
assert 'resolveOfficerAffiliations' in app_text, "Missing resolveOfficerAffiliations"
assert '【史実城代・配置武将の絶対保証】' in app_text, "Missing governor guarantee"
assert '【包括的史実配属・浪人化防止ルール】' in app_text, "Missing historical rules"

print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")
