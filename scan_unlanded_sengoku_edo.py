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
hist_govs = parse_section('window.SCENARIO_HISTORICAL_GOVERNORS =', 'window.CLAN_CAPITAL_PROVINCES =')

# Check which unlanded officers have clear historical masters or home provinces owned by other clans
# Let's inspect officers who are unlanded in each scenario from 1546 to 1868
target_scenarios = [s for s in scenarios if s['year'] >= 1546]

for scen in target_scenarios:
    s_id = str(scen['id'])
    year = scen['year']
    title = scen['title']
    owners = scen.get('owners', {})
    govs = hist_govs.get(s_id, {})
    landed_clans = set(owners.values()) - {None, '', 'null'}
    
    active = [o for o in officers_master if o.get('birthYear') and o.get('deathYear') and o['birthYear'] + 15 <= year <= o['deathYear']]
    
    # Unlanded officers who are not assigned as governor in this scenario
    unlanded = [o for o in active if o.get('clanId') not in landed_clans and o['id'] not in govs.values() and o['name'] not in govs.values()]
    
    # Filter for non-generic or notable officers
    notable = []
    for o in unlanded:
        # Check if their defaultProv is owned by some landed clan
        def_prov = o.get('defaultProv')
        prov_owner = owners.get(def_prov) if def_prov else None
        notable.append((o['id'], o['name'], o.get('clanId'), def_prov, prov_owner))
        
    print(f"\n=======================================================")
    print(f"[{s_id}] {year} {title} (Total unlanded: {len(unlanded)})")
    # Show officers who have a matching prov_owner or well-known names
    for oid, name, cid, def_p, p_owner in notable:
        print(f"  {oid:28s} {name:10s} (clan:{str(cid):12s}, defProv:{str(def_p):12s} -> owner:{str(p_owner)})")

