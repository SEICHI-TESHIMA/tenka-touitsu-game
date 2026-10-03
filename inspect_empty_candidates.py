import json

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

off_by_id = {o['id']: o for o in officers_master}

for scen_id in ['1584', '1587', '1592', '1614', '1637', '1651', '1702', '1721', '1789', '1837', '1853', '1860', '1866', '1056']:
    scen = next(s for s in scenarios if str(s['id']) == scen_id)
    year = scen['year']
    title = scen['title']
    owners = scen.get('owners', {})
    govs = hist_govs.get(scen_id, {})
    
    # Active officers
    active = [o for o in officers_master if o.get('birthYear') and o.get('deathYear') and o['birthYear'] + 15 <= year <= o['deathYear']]
    
    empty_provs = []
    for p in provs:
        pid = p['id']
        owner = owners.get(pid)
        if not owner: continue
        is_cap = (capitals.get(owner) == pid)
        gov = govs.get(pid)
        if not gov and not is_cap:
            empty_provs.append((pid, p['name'], owner))
            
    print(f"\n=======================================================")
    print(f"Scenario [{scen_id}] {year} {title} - Empty branch castles: {len(empty_provs)}")
    for pid, pname, owner in empty_provs:
        # Find candidates: active officers whose defaultProv == pid, or clanId == owner
        cands_prov = [o for o in active if o.get('defaultProv') == pid]
        cands_clan = [o for o in active if o.get('clanId') == owner and o.get('defaultProv') != pid]
        cand_str = ", ".join([f"{o['name']}({o['id']})" for o in cands_prov[:3]])
        if not cand_str and cands_clan:
            cand_str = "Clan: " + ", ".join([f"{o['name']}({o['id']})" for o in cands_clan[:2]])
        print(f"  {pid:14s} ({pname:4s}, owner:{owner:12s}): {cand_str}")

