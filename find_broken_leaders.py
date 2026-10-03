import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

scenarios = json.loads(text[text.find('window.SCENARIOS_DATA =') + len('window.SCENARIOS_DATA ='):text.find('window.CLAN_MASTER_DATA =')].strip().rstrip(';'))
officers = json.loads(text[text.find('window.OFFICERS_MASTER =') + len('window.OFFICERS_MASTER ='):text.find('window.SCENARIOS_DATA =')].strip().rstrip(';'))

print("=== EXACT PLAYABLES WITH ISSUES ===")
for s in scenarios:
    sid = str(s['id'])
    year = s['year']
    title = s['title']
    playables = s.get('playables', [])
    for p in playables:
        pid = p['id']
        pname = p['name']
        exact_alive = [o for o in officers if o['name'] == pname and o.get('birthYear') and o.get('deathYear') and (year - o['birthYear'] >= 15) and (year <= o['deathYear'])]
        if not exact_alive:
            # Look for officers with same name
            same_name = [o for o in officers if o['name'] == pname]
            print(f"[{sid}] ({year}) Clan '{pid}' - Playable Leader '{pname}':")
            if same_name:
                for so in same_name:
                    print(f"   Name match: id={so['id']}, clan={so.get('clanId')}, birth={so.get('birthYear')}, death={so.get('deathYear')}, age in scen={year - so.get('birthYear', 0)}")
            else:
                print(f"   Name '{pname}' NOT in OFFICERS_MASTER at all!")
