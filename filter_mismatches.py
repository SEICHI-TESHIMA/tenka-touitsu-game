import json
import re

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

scen_match = re.search(r'window\.SCENARIOS_DATA\s*=\s*(\[.*?\]);\s*window\.CLAN_MASTER_DATA', text, re.DOTALL)
scens = {str(s['id']): s for s in json.loads(scen_match.group(1))}

evt_match = re.search(r'window\.HISTORICAL_EVENTS_DATA\s*=\s*(\[.*?\]);\s*window\.HISTORICAL_CASTLE_CHANGES', text, re.DOTALL)
evts = json.loads(evt_match.group(1))

# For global events, find the most relevant scenario (e.g. closest start year <= event.year)
results = []
for ev in evts:
    eid = ev.get('id')
    scen_id = str(ev.get('scenarioId', ''))
    terr = ev.get('changes', {}).get('territory', {})
    year = ev.get('year', 0)
    title = ev.get('title', '')
    desc = ev.get('desc', '')
    msg = ev.get('changes', {}).get('message', '')
    
    if scen_id != '*':
        relevant = [scens[scen_id]] if scen_id in scens else []
    else:
        # find closest scenario with year <= ev.year
        valid_scens = [s for s in scens.values() if s.get('year', 0) <= year]
        if valid_scens:
            closest = max(valid_scens, key=lambda s: s.get('year', 0))
            relevant = [closest]
        else:
            relevant = []

    for s in relevant:
        sc_playables = {p['id']: p['name'] for p in s.get('playables', [])}
        sc_owners = set(s.get('owners', {}).values())
        
        for p, o in terr.items():
            # Check if this owner is NOT in the scenario
            if o not in sc_playables and o not in sc_owners:
                # Check if someone with a similar name is in playables
                matched = []
                for pid, pname in sc_playables.items():
                    if pname in title or pname in desc or pname in msg:
                        matched.append((pid, pname))
                results.append({
                    'event_id': eid,
                    'title': title,
                    'scenario': f"{s['id']} ({s.get('title')})",
                    'prov': p,
                    'event_owner': o,
                    'matched_playables': matched
                })

print(f"Total potential mismatches: {len(results)}")
for r in results:
    if r['matched_playables']:
        print(f"[DIRECT NAME MISMATCH!] Event {r['event_id']} ({r['title']}) in Scen {r['scenario']}")
        print(f"   Territory {r['prov']} -> Event gives '{r['event_owner']}', but Scenario has {r['matched_playables']}")
    else:
        print(f"[New/Rebel clan created] Event {r['event_id']} ({r['title']}) creates '{r['event_owner']}' in {r['prov']}")
