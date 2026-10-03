import json
import re

with open('js/data.js', 'r', encoding='utf-8') as f:
    data_text = f.read()

# Parse OFFICERS_MASTER
start_idx = data_text.find('window.OFFICERS_MASTER = [')
end_idx = data_text.find('\n];', start_idx) + 2
officers_master = json.loads(data_text[start_idx + len('window.OFFICERS_MASTER = '):end_idx])

# Parse SCENARIOS_DATA
start_idx = data_text.find('window.SCENARIOS_DATA = [')
end_idx = data_text.find('\n];', start_idx) + 2
scenarios = json.loads(data_text[start_idx + len('window.SCENARIOS_DATA = '):end_idx])

scen_1866 = [s for s in scenarios if str(s['id']) == '1866'][0]

print("Scenario 1866 year:", scen_1866['year'])
print("Scenario 1866 owners:", json.dumps(scen_1866.get('owners', {}), ensure_ascii=False, indent=2)[:300])

# Check who is alive in 1866 from OFFICERS_MASTER:
alive_1866 = []
for o in officers_master:
    by = o.get('birthYear')
    dy = o.get('deathYear')
    if by is not None and dy is not None:
        age = 1866 - by
        if age >= 15 and 1866 <= dy:
            alive_1866.append(o)

print(f"Alive officers in 1866 from OFFICERS_MASTER: {len(alive_1866)}")
for o in alive_1866:
    if '真田' in o.get('name', ''):
        print("Sanada in 1866:", o)
    if '大塩' in o.get('name', ''):
        print("Oshio in 1866:", o)
