import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('unlanded_analysis.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for s_id, scen in data.items():
    year = scen['year']
    unlanded = scen['unlanded']
    if not unlanded:
        continue
    print(f"\n==================================================")
    print(f"[{s_id}] {year} {scen['title']} (Unlanded: {len(unlanded)})")
    print(f"Landed Clans: {sorted(scen['landed_clans'])}")
    for o in unlanded:
        print(f"  {o['id']}: {o['name']} (clan:{o['clanId']}, defProv:{o['defaultProv']}, isDaimyo:{o['isDaimyo']})")

