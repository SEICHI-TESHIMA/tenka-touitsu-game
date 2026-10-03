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
capitals = parse_section('window.CLAN_CAPITAL_PROVINCES =', None)

# Simulate full officer affiliation for a given scenario
def simulate_scenario(scen_id):
    scen = next(s for s in scenarios if str(s['id']) == scen_id)
    year = scen['year']
    owners = scen.get('owners', {})
    owners_set = set(owners.values()) - {None, '', 'null'}
    gov_map = hist_govs.get(scen_id, {})
    
    # Active officers (age >= 15 and year <= deathYear)
    active = []
    for o in json.loads(json.dumps(officers_master)):
        b = o.get('birthYear')
        d = o.get('deathYear')
        if b is not None and d is not None and (year >= b + 15) and (year <= d):
            o['isDead'] = False
            active.append(o)
            
    # Step 1: Historical Governors assignment (like switchScenario step 2-A)
    # in switchScenario:
    # let histOff = active.find(...)
    # if (!histOff) histOff = active.find(o => ... && !provs.some(pp => pp.ownerId === o.clanId));
    # if (histOff) { p.governorId = histOff.id; histOff.assignedProvId = p.id; histOff.clanId = p.ownerId; }
    for pid, gid in gov_map.items():
        p_owner = owners.get(pid)
        if not p_owner: continue
        # match officer
        off = next((o for o in active if (o['id'] == gid or o['name'] == gid) and not o.get('assignedProvId')), None)
        if off:
            off['assignedProvId'] = pid
            off['clanId'] = p_owner

    # Step 2: resolveOfficerAffiliations simulation (current app.js logic)
    # Check what remains ronin
    ronins = []
    for off in active:
        # If assigned to a prov, not ronin
        if off.get('assignedProvId'):
            continue
        # If clanId in owners_set, not ronin
        if off.get('clanId') in owners_set:
            continue
        ronins.append(off)
        
    return scen, active, ronins

print("=== CURRENT IN-GAME SIMULATION ===")
for sid in ['1560', '1570', '1582', '1584', '1587', '1590', '1592', '1600', '1614', '1637', '1853', '1860', '1866', '1868']:
    scen, active, ronins = simulate_scenario(sid)
    # Filter ronins to notable historical figures
    notable_ronins = [o for o in ronins if not o['id'].startswith('off_succ_') and not o['id'].startswith('off_succ2_') and not o['id'].startswith('off_dm_')]
    print(f"[{sid}] {scen['year']} {scen['title']} | Active: {len(active)} | Total Ronin: {len(ronins)} | Notable Ronin: {len(notable_ronins)}")
    # Print notable ronin names
    names = [f"{o['name']}({o.get('clanId')})" for o in notable_ronins[:12]]
    print("   Notable:", ", ".join(names))

