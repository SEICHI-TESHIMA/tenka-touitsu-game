import json
import re

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

evt_match = re.search(r'window\.HISTORICAL_EVENTS_DATA\s*=\s*(\[.*?\]);\s*window\.HISTORICAL_CASTLE_CHANGES', text, re.DOTALL)
evts = json.loads(evt_match.group(1))

targets = ['evt_1585_shikoku_surrender', 'evt_1600_sekigahara', 'evt_1868_enomoto_ezo', 'evt_1591_kunohe_rebellion', 'evt_1591_kunohe_victory_if', 'evt_1863_ikuno_success_if']

for ev in evts:
    if ev.get('id') in targets:
        print("=== " + ev.get('id') + " ===")
        print(json.dumps(ev, ensure_ascii=False, indent=2))
