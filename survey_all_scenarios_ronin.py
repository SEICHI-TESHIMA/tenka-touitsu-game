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

print(f"Loaded {len(officers)} officers and {len(scenarios)} scenarios.")

court_clans = set(['heian_court', 'kamakura_shogunate', 'muromachi_shogunate', 'imperial', 'meiji_court'])

for s in scenarios:
    sid = str(s['id'])
    year = s['year']
    title = s.get('title', '')
    owners = set(s.get('owners', {}).values())
    
    # Alive officers
    alive = [o for o in officers if (o.get('birthYear', 9999) <= year <= o.get('deathYear', -9999))]
    
    # Check who has clan not in owners
    unlanded = []
    for o in alive:
        clan = o.get('clanId')
        name = o.get('name')
        # Skip court figures if not in owners
        if clan in court_clans and clan not in owners:
            continue
        if o.get('id') in ['off_meiji_tenno', 'off_dm_meiji_1868']:
            continue
        if clan not in owners:
            unlanded.append(o)
            
    print(f"Scenario {sid:>4} ({year} {title:<16}) | Alive: {len(alive):>4} | Unlanded clan: {len(unlanded):>3}")
    if len(unlanded) > 0 and len(unlanded) <= 15:
        names = [f"{o['name']}({o['clanId']})" for o in unlanded]
        print(f"    -> {', '.join(names[:10])}")
