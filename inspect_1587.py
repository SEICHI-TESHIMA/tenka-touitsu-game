import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1587 scenario object search
pos = text.find('"id": "1587"')
if pos != -1:
    # find next scenario or end of SCENARIOS
    next_pos = text.find('\n  {\n    "id":', pos)
    if next_pos == -1:
        next_pos = text.find('\n];', pos)
    scen_str = text[pos:next_pos]
    print("Found scenario 1587 snippet length:", len(scen_str))
    
    # check if there is officers, playables, governors
    for key in ['governors', 'officers', 'playables']:
        matches = re.findall(rf'"{key}":', scen_str)
        print(f"Key {key} count: {len(matches)}")

# Also check HISTORICAL_SCENARIO_OFFICERS or similar in data.js
for key in ['HISTORICAL_SCENARIO_OFFICERS', 'SCENARIO_OFFICERS', 'SCENARIOS_OFFICERS', 'INITIAL_GOVERNORS', 'HISTORICAL_JODAI']:
    matches = re.findall(rf'\b{key}\b', text)
    print(f"Global key {key}: {len(matches)}")
