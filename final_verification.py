import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

# Verify data.js
with open('js/data.js', 'r', encoding='utf-8') as f:
    d_text = f.read()

off_idx = d_text.find('window.OFFICERS_MASTER =')
scen_idx = d_text.find('window.SCENARIOS_DATA =')
clan_idx = d_text.find('window.CLAN_MASTER_DATA =')
ab_idx = d_text.find('window.CLAN_ABILITIES =')
ev_idx = d_text.find('window.HISTORICAL_EVENTS_DATA =')
cast_idx = d_text.find('window.HISTORICAL_CASTLE_CHANGES =')

officers = json.loads(d_text[off_idx + len('window.OFFICERS_MASTER ='):scen_idx].strip().rstrip(';'))
scenarios = json.loads(d_text[scen_idx + len('window.SCENARIOS_DATA ='):clan_idx].strip().rstrip(';'))
clans = json.loads(d_text[clan_idx + len('window.CLAN_MASTER_DATA ='):ab_idx].strip().rstrip(';'))
abilities = json.loads(d_text[ab_idx + len('window.CLAN_ABILITIES ='):ev_idx].strip().rstrip(';'))
events = json.loads(d_text[ev_idx + len('window.HISTORICAL_EVENTS_DATA ='):cast_idx].strip().rstrip(';'))

print('=== DATA.JS STATUS ===')
print(f'Officers: {len(officers)}')
print(f'Scenarios: {len(scenarios)}')
print(f'Clans: {len(clans)}')
print(f'Abilities: {len(abilities)}')
print(f'Events: {len(events)}')

# Check new rebellions in events
print('\n=== HISTORICAL REBELLION EVENTS IN DATA.JS ===')
for e in events:
    if any(k in e['id'] for k in ['kunohe', 'yui', 'oshio', 'tengu', 'tenchu', 'ikuno', 'sanhei', 'ikuta', 'shimabara', 'keian']):
        print(f"[{e['id']}] {e.get('year')} {e.get('season','')} - {e.get('title')}")

# Verify app.js
with open('js/app.js', 'r', encoding='utf-8') as f:
    a_text = f.read()

pattern = re.compile(r'id:\s*[\x27\x22]([^\x27\x22]+)[\x27\x22],\s*scenarioId:\s*[\x27\x22]([^\x27\x22]+)[\x27\x22],\s*title:\s*[\x27\x22]([^\x27\x22]+)[\x27\x22]')
app_events = list(pattern.finditer(a_text))
print(f'\n=== APP.JS INTERACTIVE EVENTS ({len(app_events)}) ===')
for m in app_events:
    print(f"{m.group(1):<25} ({m.group(2)}): {m.group(3)}")
