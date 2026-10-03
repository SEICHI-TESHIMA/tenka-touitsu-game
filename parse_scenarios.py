import re
import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract window.SCENARIOS_DATA
start_idx = text.find('window.SCENARIOS_DATA = [')
# Find matching closing bracket
# Let's use bracket counter or just find '\n];'
end_idx = text.find('\n];', start_idx) + 2
scen_json_str = text[start_idx + len('window.SCENARIOS_DATA = '):end_idx]

try:
    scenarios = json.loads(scen_json_str)
    print(f"Successfully loaded {len(scenarios)} scenarios.")
    for s in scenarios:
        print(f"ID: {s.get('id')}, Year: {s.get('year')}, Title: {s.get('title')}")
except Exception as e:
    print("JSON load failed:", e)
    # let's write out first 500 chars of scen_json_str
    print(scen_json_str[:500])
