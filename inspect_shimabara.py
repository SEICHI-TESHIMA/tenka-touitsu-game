import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

scenarios = json.loads(text[text.find('window.SCENARIOS_DATA =') + len('window.SCENARIOS_DATA ='):text.find('window.CLAN_MASTER_DATA =')].strip().rstrip(';'))
events = json.loads(text[text.find('window.HISTORICAL_EVENTS_DATA =') + len('window.HISTORICAL_EVENTS_DATA ='):text.find('window.HISTORICAL_CASTLE_CHANGES =')].strip().rstrip(';'))

s1637 = next((s for s in scenarios if str(s['id']) == '1637'), None)
if s1637:
    print('1637 scenario owners for hizen and higo:')
    print('hizen:', s1637.get('owners', {}).get('hizen'))
    print('higo:', s1637.get('owners', {}).get('higo'))
    print('playables in 1637:')
    for p in s1637.get('playables', []):
        print('  ', p['id'], p['name'])

print('\nShimabara events in HISTORICAL_EVENTS_DATA:')
for e in events:
    if '島原' in e['title'] or 'shimabara' in e['id'] or '天草' in e['title']:
        print(f"[{e['id']}] {e['title']} ({e.get('year')} {e.get('season')}) scen:{e.get('scenarioId')}")
        print(f"  changes: {e.get('changes')}")

with open('js/app.js', 'r', encoding='utf-8') as f:
    app_text = f.read()

print('\nShimabara in app.js:')
for line in app_text.splitlines():
    if 'shimabara' in line.lower() or '島原' in line:
        print('  ', line[:100])
