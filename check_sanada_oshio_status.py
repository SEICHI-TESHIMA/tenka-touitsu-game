import re
import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract window.OFFICERS_MASTER
idx = text.find('window.OFFICERS_MASTER = [')
if idx != -1:
    end_idx = text.find('];', idx)
    json_str = text[idx + len('window.OFFICERS_MASTER = '): end_idx + 1]
    officers = json.loads(json_str)
    print(f"Loaded {len(officers)} officers from OFFICERS_MASTER.")
else:
    print("Could not find OFFICERS_MASTER")
    officers = []

# Check Oshio
oshio_list = [o for o in officers if 'oshio' in o.get('id', '') or '大塩' in o.get('name', '')]
print(f"\nOshio officers ({len(oshio_list)}):")
for o in oshio_list:
    print(f"  {o['id']}: {o['name']} ({o.get('birthYear')}-{o.get('deathYear')}) clan:{o.get('clanId')} prov:{o.get('defaultProv')}")

# Check Sanada
sanada_list = [o for o in officers if 'sanada' in o.get('id', '') or '真田' in o.get('name', '')]
print(f"\nSanada officers ({len(sanada_list)}):")
for o in sanada_list:
    print(f"  {o['id']:<25} {o['name']:<10} clan:{o.get('clanId',''):<15} {o.get('birthYear')}-{o.get('deathYear')} prov:{o.get('defaultProv')}")

# Check any invalid defaultProv
for o in officers:
    prov = o.get('defaultProv')
    if prov == 'shinano':
        print(f"ERROR: officer {o['id']} ({o['name']}) has defaultProv 'shinano'!")

# Check 1866 alive officers
alive_1866 = [o for o in officers if (o.get('birthYear', 9999) <= 1866 <= o.get('deathYear', -9999))]
print(f"\nTotal alive in 1866: {len(alive_1866)}")
for o in alive_1866:
    if 'sanada' in o['id'] or '真田' in o['name']:
        print(f"  1866 Sanada alive: {o['id']} {o['name']} clan:{o.get('clanId')} prov:{o.get('defaultProv')}")
