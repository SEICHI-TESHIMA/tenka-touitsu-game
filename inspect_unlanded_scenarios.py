import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Officers
idx_off = text.find('window.OFFICERS_MASTER = [')
end_off = text.find('];', idx_off)
officers = json.loads(text[idx_off + len('window.OFFICERS_MASTER = '): end_off + 1])

# Scenarios
idx_scen = text.find('window.SCENARIOS_DATA = [')
end_scen = text.find('];\n\nwindow.CLAN_MASTER_DATA', idx_scen)
if end_scen == -1:
    end_scen = text.find('];', idx_scen)

scenarios = json.loads(text[idx_scen + len('window.SCENARIOS_DATA = '): end_scen + 1])

# Let's inspect unlanded officers for 1866, 1860, 1853, 1837, 1789, 1721, 1702, 1651, 1637, 1614, 1600, 1582, 1560
target_scen_ids = ['1866', '1860', '1853', '1837', '1789', '1702', '1651', '1614', '1600', '1582', '1560']

court_clans = set(['heian_court', 'kamakura_shogunate', 'muromachi_shogunate', 'imperial', 'meiji_court'])

for sid in target_scen_ids:
    scen = next(s for s in scenarios if str(s['id']) == sid)
    year = scen['year']
    owners = set(scen.get('owners', {}).values())
    alive = [o for o in officers if (o.get('birthYear', 9999) <= year <= o.get('deathYear', -9999))]
    
    unlanded = [o for o in alive if o.get('clanId') not in owners and o.get('clanId') not in court_clans and o.get('id') not in ['off_meiji_tenno', 'off_dm_meiji_1868']]
    
    print(f"\n=== SCENARIO {sid} ({year} {scen.get('title')}) - Unlanded count: {len(unlanded)} ===")
    for o in unlanded:
        print(f"  {o['id']:<28} {o['name']:<12} clan:{o.get('clanId',''):<15} {o.get('birthYear')}-{o.get('deathYear')} prov:{o.get('defaultProv')}")
