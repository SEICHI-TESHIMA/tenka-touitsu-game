import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

scen_idx = text.find('window.SCENARIOS_DATA =')
clan_idx = text.find('window.CLAN_MASTER_DATA =')
events_idx = text.find('window.HISTORICAL_EVENTS_DATA =')
castle_idx = text.find('window.HISTORICAL_CASTLE_CHANGES =')

scenarios = json.loads(text[scen_idx + len('window.SCENARIOS_DATA ='):clan_idx].strip().rstrip(';'))
print(f'Total scenarios: {len(scenarios)}')
for s in scenarios:
    sid = s.get('id')
    sname = s.get('name')
    syear = s.get('year')
    print(f'  Scenario: {sid} - {sname} ({syear}年)')

events = json.loads(text[events_idx + len('window.HISTORICAL_EVENTS_DATA ='):castle_idx].strip().rstrip(';'))
print(f'\nTotal HISTORICAL_EVENTS_DATA: {len(events)}')
for e in events[:30]:
    print(f"  [{e.get('id')}] {e.get('title')} ({e.get('year')})")
