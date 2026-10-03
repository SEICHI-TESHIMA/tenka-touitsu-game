import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('window.OFFICERS_MASTER = [')
end_idx = text.find('\n];', start_idx) + 2
officers = json.loads(text[start_idx + len('window.OFFICERS_MASTER = '):end_idx])

start_idx = text.find('window.SCENARIOS_DATA = [')
end_idx = text.find('\n];', start_idx) + 2
scenarios = json.loads(text[start_idx + len('window.SCENARIOS_DATA = '):end_idx])

idx = text.find('window.SCENARIO_HISTORICAL_GOVERNORS = {')
end_idx = text.find('\n};', idx) + 3
hist_govs = json.loads(text[idx + len('window.SCENARIO_HISTORICAL_GOVERNORS = '):end_idx-1])

officer_by_id = {o['id']: o for o in officers}
officer_by_name = {o['name']: o for o in officers}

print(f"Total scenarios in hist_govs: {len(hist_govs)}")
