import json
import re

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

prov_match = re.search(r'window\.PROVINCES_DATA\s*=\s*(\[.*?\]);', text, re.DOTALL)
provs = set(p['id'] for p in json.loads(prov_match.group(1)))

scen_match = re.search(r'window\.SCENARIOS_DATA\s*=\s*(\[.*?\]);\s*window\.CLAN_MASTER_DATA', text, re.DOTALL)
scens = {str(s['id']): s for s in json.loads(scen_match.group(1))}

clan_match = re.search(r'window\.CLAN_MASTER_DATA\s*=\s*(\{.*?\});\s*window\.CLAN_ABILITIES', text, re.DOTALL)
clans = json.loads(clan_match.group(1))

evt_match = re.search(r'window\.HISTORICAL_EVENTS_DATA\s*=\s*(\[.*?\]);\s*window\.HISTORICAL_CASTLE_CHANGES', text, re.DOTALL)
evts = json.loads(evt_match.group(1))

out = []
out.append(f"Loaded {len(scens)} scenarios, {len(evts)} historical events in data.js.\n")

for i, ev in enumerate(evts):
    eid = ev.get('id')
    title = ev.get('title')
    scen_id = str(ev.get('scenarioId', ''))
    year = ev.get('year')
    season = ev.get('season')
    changes = ev.get('changes', {})
    terr = changes.get('territory', {})
    
    out.append(f"[{i+1}] {eid} | {title} (scen: {scen_id}, year: {year}, season: {season})")
    out.append(f"    desc: {ev.get('desc')}")
    out.append(f"    territory: {terr}")
    
    # Check provinces
    for pid in terr.keys():
        if pid not in provs:
            out.append(f"    *** ERROR: invalid province id '{pid}'")
            
    # Check owners
    for pid, oid in terr.items():
        if oid not in clans:
            out.append(f"    *** CRITICAL: owner '{oid}' is NOT in CLAN_MASTER_DATA! This will cause English name or crash!")
        
        # Check against scenario
        if scen_id != '*':
            scen = scens.get(scen_id)
            if not scen:
                out.append(f"    *** ERROR: Scenario {scen_id} not found!")
            else:
                p_ids = [p['id'] for p in scen.get('playables', [])]
                if oid not in p_ids:
                    # check if playables have someone who corresponds to this
                    names = {p['name']: p['id'] for p in scen.get('playables', [])}
                    out.append(f"    *** WARNING: owner '{oid}' is not in scenario {scen_id} playables {p_ids}. Playable names: {names}")
        else:
            # global event (*): check which scenario could be active in this year
            active_scens = [s for s in scens.values() if s.get('year', 0) <= year]
            # Find the closest scenario before or at year
            if active_scens:
                closest = max(active_scens, key=lambda s: s.get('year', 0))
                p_ids = [p['id'] for p in closest.get('playables', [])]
                if oid not in p_ids and oid not in closest.get('owners', {}).values():
                    out.append(f"    (Global evt at {year}: closest scen is {closest['id']} ({closest['year']}), owner '{oid}' in its playables? {oid in p_ids}, in owners? {oid in closest.get('owners', {}).values()})")
    out.append("")

with open('dump_historical_events_audit.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))

print("Wrote dump_historical_events_audit.txt successfully.")
