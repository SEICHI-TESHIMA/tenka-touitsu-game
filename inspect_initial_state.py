import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Load sections
provs = json.loads(text[text.find('window.PROVINCES_DATA =') + len('window.PROVINCES_DATA ='):text.find('window.OFFICERS_MASTER =')].strip().rstrip(';'))
officers = json.loads(text[text.find('window.OFFICERS_MASTER =') + len('window.OFFICERS_MASTER ='):text.find('window.SCENARIOS_DATA =')].strip().rstrip(';'))
scenarios = json.loads(text[text.find('window.SCENARIOS_DATA =') + len('window.SCENARIOS_DATA ='):text.find('window.CLAN_MASTER_DATA =')].strip().rstrip(';'))
clans = json.loads(text[text.find('window.CLAN_MASTER_DATA =') + len('window.CLAN_MASTER_DATA ='):text.find('window.CLAN_ABILITIES =')].strip().rstrip(';'))
events = json.loads(text[text.find('window.HISTORICAL_EVENTS_DATA =') + len('window.HISTORICAL_EVENTS_DATA ='):text.find('window.HISTORICAL_CASTLE_CHANGES =')].strip().rstrip(';'))
hist_govs = json.loads(text[text.find('window.SCENARIO_HISTORICAL_GOVERNORS =') + len('window.SCENARIO_HISTORICAL_GOVERNORS ='):text.find('window.CLAN_CAPITAL_PROVINCES =')].strip().rstrip(';'))
capitals = json.loads(text[text.find('window.CLAN_CAPITAL_PROVINCES =') + len('window.CLAN_CAPITAL_PROVINCES ='):].strip().rstrip(';'))

print("=== SCENARIOS & GOVERNOR / PROVINCE STATS ===")
for scen in scenarios:
    sid = str(scen['id'])
    year = scen['year']
    title = scen.get('title')
    owners = scen.get('owners', {})
    
    # Count provinces per clan
    clan_provs = {}
    for pid, cid in owners.items():
        clan_provs.setdefault(cid, []).append(pid)
        
    # Count how many provinces are NOT capital for their owner
    total_provs = len(owners)
    branch_provs = 0
    assigned_govs = 0
    scen_govs = hist_govs.get(sid, {})
    
    for pid, cid in owners.items():
        is_cap = (capitals.get(cid) == pid)
        # Check if clan has only 1 prov
        if len(clan_provs.get(cid, [])) == 1:
            is_cap = True
        if not is_cap:
            branch_provs += 1
            if pid in scen_govs:
                assigned_govs += 1
                
    print(f"[{sid}] ({year}) {title}: Total Provs={total_provs}, Branch Provs={branch_provs}, Assigned Govs={assigned_govs}, Gov Entries In Data={len(scen_govs)}")

print("\n=== HISTORICAL EVENTS ANALYSIS ===")
print(f"Total events: {len(events)}")
transfer_events = 0
for ev in events:
    changes = ev.get('changes', {})
    territory = changes.get('territory', {}) if isinstance(changes, dict) else {}
    if territory:
        transfer_events += 1
        print(f"Event with territory change: {ev.get('id')} - {ev.get('title')} ({ev.get('year')} {ev.get('season')}): {len(territory)} provinces")

print(f"Total events with territory change: {transfer_events} / {len(events)}")
