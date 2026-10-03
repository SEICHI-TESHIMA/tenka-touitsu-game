import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

events = json.loads(text[text.find('window.HISTORICAL_EVENTS_DATA =') + len('window.HISTORICAL_EVENTS_DATA ='):text.find('window.HISTORICAL_CASTLE_CHANGES =')].strip().rstrip(';'))

print(f"Total events in HISTORICAL_EVENTS_DATA: {len(events)}")
for ev in events:
    changes = ev.get('changes')
    territory = changes.get('territory') if changes else None
    appoint = changes.get('appoint') if changes else None
    t_keys = list(territory.keys()) if territory else []
    print(f"[{ev.get('id')}] {ev.get('title')} ({ev.get('year')} {ev.get('season')}) - scen: {ev.get('scenarioId')} - terr_count: {len(t_keys)} - appoint: {appoint}")
