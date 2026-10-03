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

print("=== CHECKING ALL HISTORICAL_EVENTS_DATA ===")
report = []

for idx, ev in enumerate(evts):
    eid = ev.get('id')
    scen_id = str(ev.get('scenarioId', ''))
    title = ev.get('title', '')
    desc = ev.get('desc', '')
    year = ev.get('year', 0)
    season = ev.get('season', '')
    changes = ev.get('changes', {})
    terr = changes.get('territory', {})
    msg = changes.get('message', '')

    # Determine which scenarios this event applies to
    applicable_scens = []
    if scen_id == '*':
        # Finds scenarios where this event could happen (scenario.year <= year)
        # Specifically the scenario whose year is closest <= year
        cands = [s for s in scens.values() if s.get('year', 0) <= year]
        if cands:
            closest_scen = max(cands, key=lambda s: s.get('year', 0))
            applicable_scens.append(closest_scen)
    else:
        if scen_id in scens:
            applicable_scens.append(scens[scen_id])
        else:
            report.append(f"[{eid}] Unknown scenarioId: {scen_id}")

    # Check territory changes
    for pid, oid in terr.items():
        if pid not in provs:
            report.append(f"[{eid}] Invalid province: '{pid}' in {title}")

        if oid not in clans:
            report.append(f"[{eid}] Owner '{oid}' is NOT in CLAN_MASTER_DATA! Title: {title}")

        for sc in applicable_scens:
            sc_playables = {p['id']: p for p in sc.get('playables', [])}
            sc_owners = set(sc.get('owners', {}).values())
            
            # If owner is not among playables or owners in this scenario
            if oid not in sc_playables and oid not in sc_owners:
                # Check if there is an existing playable with matching name/clan
                # Look through playable names
                potential_matches = []
                for p_id, p_obj in sc_playables.items():
                    p_name = p_obj.get('name', '')
                    p_clan = p_obj.get('clan', '')
                    if p_name in title or p_name in desc or p_name in msg or p_clan in title or p_clan in desc or p_clan in msg:
                        potential_matches.append(f"{p_name}({p_id})")
                
                report.append(f"[{eid}] In scen {sc['id']} ({sc.get('title')}), territory '{pid}' -> '{oid}'. But '{oid}' is not in scenario! Matching playables in scenario: {potential_matches}")

with open('full_event_audit_report.txt', 'w', encoding='utf-8') as f:
    for line in report:
        f.write(line + '\n')

print(f"Audit completed. Found {len(report)} issues.")
