import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

def parse_section(prefix, next_prefix):
    start = text.find(prefix) + len(prefix)
    end = text.find(next_prefix, start) if next_prefix else len(text)
    body = text[start:end].strip()
    last_b = max(body.rfind(']'), body.rfind('}'))
    return json.loads(body[:last_b+1])

scenarios = parse_section('window.SCENARIOS_DATA =', 'window.CLAN_MASTER_DATA =')
officers_master = parse_section('window.OFFICERS_MASTER =', 'window.SCENARIOS_DATA =')

for s in scenarios:
    scen_id = str(s['id'])
    year = s['year']
    title = s['title']
    owners = s.get('owners', {})
    playables = s.get('playables', [])

    print(f"\n==========================================")
    print(f"Scenario {scen_id} ({year}): {title}")
    
    # Check all playables in this scenario
    for p in playables:
        pid = p['id']
        pname = p['name']
        owned_provs = [prov_id for prov_id, cl in owners.items() if cl == pid]
        
        # find officer with this name in officers_master
        def matches_name(o, pname):
            if o['name'] == pname: return True
            if pname in ['豊臣秀吉', '羽柴秀吉'] and o['id'] == 'off_toyotomi_hideyoshi': return True
            if pname in ['徳川家康', '松平元康'] and o['id'] == 'off_tokugawa_ieyasu': return True
            return False

        exact_off = [o for o in officers_master if matches_name(o, pname)]
        alive_exact = [o for o in exact_off if (o.get('birthYear') and o.get('deathYear') and year - o['birthYear'] >= 15 and year <= o['deathYear'])]
        
        status = "OK"
        if len(owned_provs) == 0:
            status = "NO_PROV_IN_OWNERS"
        elif not alive_exact:
            status = f"NO_ALIVE_OFFICER (exact found: {len(exact_off)})"
            
        if status != "OK":
            print(f"  [PLAYABLE ISSUE] {pname} ({pid}): status={status}, owned_provs={owned_provs}")
            if exact_off:
                for eo in exact_off:
                    print(f"      Officer {eo['id']}: birth={eo.get('birthYear')}, death={eo.get('deathYear')}, clan={eo.get('clanId')}")

