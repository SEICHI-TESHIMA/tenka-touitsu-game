import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

events_idx = text.find('window.HISTORICAL_EVENTS_DATA =')
castle_idx = text.find('window.HISTORICAL_CASTLE_CHANGES =')
events = json.loads(text[events_idx + len('window.HISTORICAL_EVENTS_DATA ='):castle_idx].strip().rstrip(';'))

print("=== ALL HISTORICAL_EVENTS_DATA ===")
for i, e in enumerate(events):
    print(f"[{i}] id: {e.get('id')}, year: {e.get('year')} {e.get('season','')}, title: {e.get('title')}, scen: {e.get('scenarioId')}")

# Check specific scenarios
scen_idx = text.find('window.SCENARIOS_DATA =')
clan_idx = text.find('window.CLAN_MASTER_DATA =')
scenarios = json.loads(text[scen_idx + len('window.SCENARIOS_DATA ='):clan_idx].strip().rstrip(';'))

print("\n=== SPECIFIC SCENARIOS ===")
for s in scenarios:
    sid = str(s.get('id'))
    if sid in ['1590', '1592', '1637', '1651', '1837', '1860', '1866']:
        print(f"\nScenario {sid}: {s.get('name')} ({s.get('year')})")
        print("  Playables:", [p.get('id') + ':' + p.get('name') for p in s.get('playables', [])[:8]])
        # check owners
        owners = s.get('owners', {})
        print(f"  Total owned provs: {len(owners)}")
        # Check if kunohe, yui, oshio, tengu are present
        for p, c in owners.items():
            if any(k in c for k in ['kunohe', 'yui', 'shosetsu', 'oshio', 'tengu', 'mitotengu', 'takeda']):
                print(f"    Special owner: prov {p} -> {c}")
