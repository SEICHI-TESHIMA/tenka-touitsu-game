import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

scenarios = json.loads(text[text.find('window.SCENARIOS_DATA =') + len('window.SCENARIOS_DATA ='):text.find('window.CLAN_MASTER_DATA =')].strip().rstrip(';'))
officers = json.loads(text[text.find('window.OFFICERS_MASTER =') + len('window.OFFICERS_MASTER ='):text.find('window.SCENARIOS_DATA =')].strip().rstrip(';'))
clans = json.loads(text[text.find('window.CLAN_MASTER_DATA =') + len('window.CLAN_MASTER_DATA ='):text.find('window.CLAN_ABILITIES =')].strip().rstrip(';'))
capitals = json.loads(text[text.find('window.CLAN_CAPITAL_PROVINCES =') + len('window.CLAN_CAPITAL_PROVINCES ='):].strip().rstrip(';'))

officers_dict = {o['id']: o for o in officers}

print("=== CHECKING ALL PLAYABLES AND CLAN LEADERS ===")
for s in scenarios:
    sid = str(s['id'])
    year = s['year']
    title = s['title']
    owners = s.get('owners', {})
    playables = s.get('playables', [])
    
    print(f"\n--- Scenario [{sid}] ({year}) {title} ---")
    active_clans = sorted(list(set(owners.values())))
    for cid in active_clans:
        c_provs = [p for p, c in owners.items() if c == cid]
        p_match = next((p for p in playables if p['id'] == cid), None)
        leader_name = p_match['name'] if p_match else "N/A"
        
        # Check matching alive officer
        alive_offs = [o for o in officers if (o.get('clanId') == cid or o.get('name') == leader_name) 
                      and o.get('birthYear') and o.get('deathYear') 
                      and (year - o['birthYear'] >= 15) and (year <= o['deathYear'])]
        
        has_exact_leader = any(o['name'] == leader_name for o in alive_offs)
        cap = capitals.get(cid, c_provs[0])
        
        print(f"Clan {cid} ({clans.get(cid, {}).get('name', cid)}): Leader='{leader_name}' (exact alive: {has_exact_leader}), Provs={len(c_provs)}, Cap={cap}")
        if not has_exact_leader:
            # show potential matching officers
            name_offs = [o for o in officers if o['name'] == leader_name]
            if name_offs:
                for no in name_offs:
                    print(f"   Officer found by name: {no['id']} (clan: {no.get('clanId')}, birth: {no.get('birthYear')}, death: {no.get('deathYear')}, age: {year - no.get('birthYear', 0)})")
            else:
                print(f"   NO officer found with name '{leader_name}'!")
