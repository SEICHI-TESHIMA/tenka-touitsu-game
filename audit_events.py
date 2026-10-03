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

print(f"Loaded {len(scens)} scenarios, {len(evts)} historical events.")

issues = []

for ev in evts:
    eid = ev.get('id')
    title = ev.get('title')
    scen_id = str(ev.get('scenarioId', ''))
    scen = scens.get(scen_id)
    if not scen:
        issues.append(f"Event {eid} ({title}) references unknown scenario {scen_id}")
        continue
    
    scen_year = scen.get('year', 0)
    ev_year = ev.get('year', 0)
    if ev_year < scen_year:
        issues.append(f"Event {eid} ({title}) year {ev_year} is before scenario {scen_id} year {scen_year}")

    changes = ev.get('changes', {})
    terr = changes.get('territory', {})
    
    playables = {p['id']: p for p in scen.get('playables', [])}
    playable_names = {p['name']: p['id'] for p in scen.get('playables', [])}
    owners_in_scen = set(scen.get('owners', {}).values())

    for p_id, owner in terr.items():
        if p_id not in provs:
            issues.append(f"Event {eid} ({title}) invalid province: {p_id}")
        
        # Check if owner exists in scenario playables or owners
        owner_in_playables = owner in playables
        owner_in_owners = owner in owners_in_scen
        owner_in_clan_master = owner in clans
        
        # Check if any playable daimyo has a name that matches something in event or title
        # e.g., 源頼信 vs minamoto_yorinobu
        suspect = False
        if not owner_in_playables and not owner_in_owners:
            suspect = True
        
        # Also check if owner is not even in clan_master
        if not owner_in_clan_master:
            issues.append(f"[UNKNOWN_CLAN] Event {eid} ({title}) scenario {scen_id}: owner '{owner}' is NOT in CLAN_MASTER_DATA! (prov: {p_id})")
        
        if suspect:
            # Let's inspect playable names
            matched_playables = []
            for pname, pid in playable_names.items():
                if pname in title or pname in ev.get('desc', '') or pname in changes.get('message', ''):
                    matched_playables.append((pname, pid))
            issues.append(f"[CLAN_MISMATCH] Event {eid} ({title}) scenario {scen_id}: terr {p_id} -> '{owner}' (in_playables={owner_in_playables}, in_owners={owner_in_owners}, in_clans={owner_in_clan_master}). Mentioned playables: {matched_playables}")

print(f"\n--- Issues found in HISTORICAL_EVENTS_DATA: {len(issues)} ---")
for iss in issues:
    print(iss)
