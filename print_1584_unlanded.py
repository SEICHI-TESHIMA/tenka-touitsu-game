import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('unlanded_analysis.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

scen = data['1584']
print(f"=== 1584 Unlanded ({len(scen['unlanded'])}) ===")
for o in scen['unlanded']:
    print(f"  {o['id']}: {o['name']} (clan:{o['clanId']}, defProv:{o['defaultProv']}, isDaimyo:{o['isDaimyo']})")

