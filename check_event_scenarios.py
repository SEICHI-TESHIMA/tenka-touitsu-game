import json
import re

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

scen_match = re.search(r'window\.SCENARIOS_DATA\s*=\s*(\[.*?\]);\s*window\.CLAN_MASTER_DATA', text, re.DOTALL)
scens = {str(s['id']): s for s in json.loads(scen_match.group(1))}

evt_match = re.search(r'window\.HISTORICAL_EVENTS_DATA\s*=\s*(\[.*?\]);\s*window\.HISTORICAL_CASTLE_CHANGES', text, re.DOTALL)
evts = json.loads(evt_match.group(1))

print("Checking each event against its scenario's playables and existing owners...")

for ev in evts:
    eid = ev.get('id')
    scen_id = str(ev.get('scenarioId', ''))
    terr = ev.get('changes', {}).get('territory', {})
    year = ev.get('year')
    title = ev.get('title')
    
    # Target scenarios
    target_scens = []
    if scen_id != '*':
        if scen_id in scens:
            target_scens = [scens[scen_id]]
    else:
        # All scenarios that start <= year
        # Especially scenarios where this event would actually fire
        target_scens = [s for s in scens.values() if s.get('year', 0) <= year]
    
    for s in target_scens:
        # check if owners in terr match playables or owners of s
        sc_playables = {p['id']: p['name'] for p in s.get('playables', [])}
        sc_owners = set(s.get('owners', {}).values())
        
        for p, o in terr.items():
            if o not in sc_playables and o not in sc_owners:
                # Is there a playable whose name appears in the title or event?
                # e.g., 源頼朝 in title, but playable id is genji_yoritomo, and event owner is minamoto_yoritomo
                print(f"[POTENTIAL MISMATCH] Event {eid} ({title}) year {year} in scenario {s['id']} ({s.get('title')}, {s.get('year')}):")
                print(f"   Territory {p} -> {o}")
                print(f"   Playables in {s['id']}: {sc_playables}")
