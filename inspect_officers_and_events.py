import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

events_idx = text.find('window.HISTORICAL_EVENTS_DATA =')
castle_idx = text.find('window.HISTORICAL_CASTLE_CHANGES =')
events = json.loads(text[events_idx + len('window.HISTORICAL_EVENTS_DATA ='):castle_idx].strip().rstrip(';'))

for e in events:
    if any(k in e.get('id', '') or k in e.get('title', '') for k in ['1651', '1837', 'kunohe', 'tengu', 'yui', 'oshio', 'keian']):
        print(f"--- Event: {e.get('id')} ---")
        print(json.dumps(e, ensure_ascii=False, indent=2))

# Check officers: kunohe, yui, oshio, tengu
officers_idx = text.find('window.OFFICERS_DATA =')
# find end of officers
officers_end = text.find('window.SCENARIO_OFFICERS =') if 'window.SCENARIO_OFFICERS =' in text else len(text)
officers_text = text[officers_idx + len('window.OFFICERS_DATA ='):officers_end].strip().rstrip(';')
officers = json.loads(officers_text)

print(f"\nTotal officers: {len(officers)}")
search_names = ['九戸', '由比', '丸橋', '大塩', '武田耕雲斎', '藤田小四郎', '天狗', '生田万', '平野国臣', '吉村寅太郎']
for o in officers:
    name = o.get('name', '')
    if any(s in name for s in search_names):
        print(f"  Officer: {o.get('id')} - {name} ({o.get('birth', '?')}-{o.get('death', '?')}), clan: {o.get('clanId')}, lead: {o.get('leadership')}, val: {o.get('valor')}, int: {o.get('intelligence')}, pol: {o.get('politics')}")
