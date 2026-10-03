import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx_off = text.find('window.OFFICERS_MASTER = [')
end_off = text.find('];', idx_off)
officers = json.loads(text[idx_off + len('window.OFFICERS_MASTER = '): end_off + 1])

alive_1156 = [o for o in officers if (o.get('birthYear', 9999) <= 1156 <= o.get('deathYear', -9999))]
print(f"Alive in 1156: {len(alive_1156)}")
for o in alive_1156:
    if 'taira' in o['clanId'] or 'taira' in o['id']:
        print(f"  {o['id']:<26} {o['name']:<12} {o.get('birthYear')}-{o.get('deathYear')} prov:{o.get('defaultProv')}")
