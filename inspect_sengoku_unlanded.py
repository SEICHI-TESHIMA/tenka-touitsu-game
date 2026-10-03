import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('unlanded_analysis.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for sid in ['1560', '1570', '1582', '1584', '1587', '1590', '1592', '1600', '1614']:
    scen = data[sid]
    print(f"\n=== [{sid}] {scen['year']} {scen['title']} (Unlanded: {len(scen['unlanded'])}) ===")
    print(f"Landed clans: {scen['landed_clans']}")
    for o in scen['unlanded']:
        print(f"  {o['id']}: {o['name']} (clan:{o['clanId']}, defProv:{o['defaultProv']})")

