import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

def parse_section(prefix, next_prefix):
    start = text.find(prefix) + len(prefix)
    end = text.find(next_prefix, start) if next_prefix else len(text)
    body = text[start:end].strip()
    last_b = max(body.rfind(']'), body.rfind('}'))
    return json.loads(body[:last_b+1])

provs = parse_section('window.PROVINCES_DATA =', 'window.OFFICERS_MASTER =')
officers_master = parse_section('window.OFFICERS_MASTER =', 'window.SCENARIOS_DATA =')
scenarios = parse_section('window.SCENARIOS_DATA =', 'window.CLAN_MASTER_DATA =')
clans = parse_section('window.CLAN_MASTER_DATA =', 'window.CLAN_ABILITIES =')
hist_govs = parse_section('window.SCENARIO_HISTORICAL_GOVERNORS =', 'window.CLAN_CAPITAL_PROVINCES =')
capitals = parse_section('window.CLAN_CAPITAL_PROVINCES =', None)

# Map province id to prov object
prov_map = {p['id']: p for p in provs}
officer_map = {o['id']: o for o in officers_master}

print("=== CHECKING ALL SCENARIOS FOR EMPTY GOVERNORS & UNLANDED OFFICERS ===")

# For each scenario, find provinces where owner exists but gov is None (and not capital)
for scen in scenarios:
    sid = str(scen['id'])
    y = scen['year']
    t = scen['title']
    owners = scen.get('owners', {})
    govs = hist_govs.get(sid, {})
    
    # Active officers in this year
    active = [o for o in officers_master if o.get('birthYear') and o.get('deathYear') and o['birthYear'] + 15 <= y <= o['deathYear']]
    active_ids = set(o['id'] for o in active)
    
    # Find provinces with owner but no governor
    empty_provs = []
    for pid, owner in owners.items():
        if not owner: continue
        # Check if capital
        is_cap = (capitals.get(owner) == pid)
        gov = govs.get(pid)
        if not gov and not is_cap:
            empty_provs.append((pid, owner))
            
    # Also find unlanded officers whose defaultProv is an empty_prov or owned by that clan
    unlanded = [o for o in active if o.get('clanId') not in owners.values() and o['id'] not in govs.values() and o['name'] not in govs.values()]
    
    # Matches: unlanded officer whose defaultProv is owned by some landed clan!
    matches = []
    for o in unlanded:
        def_p = o.get('defaultProv')
        if def_p and def_p in owners and owners[def_p]:
            matches.append((o, def_p, owners[def_p], govs.get(def_p)))
            
    if empty_provs or matches:
        print(f"\n[{sid}] {y} {t}: Empty non-cap branch provinces: {len(empty_provs)}, Unlanded matching prov owner: {len(matches)}")
        if matches:
            print("  --- Unlanded officers matching province owner ---")
            for o, def_p, p_owner, current_gov in matches:
                print(f"    {o['id']}: {o['name']} (clan:{o.get('clanId')}) -> defaultProv:{def_p} (owner:{p_owner}, current_gov:{current_gov})")

