import json
import re

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Load all data
start_idx = text.find('window.OFFICERS_MASTER = [')
end_idx = text.find('\n];', start_idx) + 2
officers_master = json.loads(text[start_idx + len('window.OFFICERS_MASTER = '):end_idx])

start_idx = text.find('window.SCENARIOS_DATA = [')
end_idx = text.find('\n];', start_idx) + 2
scenarios = json.loads(text[start_idx + len('window.SCENARIOS_DATA = '):end_idx])

start_idx = text.find('window.PROVINCES_DATA = [')
end_idx = text.find('\n];', start_idx) + 2
provinces_data = json.loads(text[start_idx + len('window.PROVINCES_DATA = '):end_idx])

idx = text.find('window.SCENARIO_HISTORICAL_GOVERNORS = {')
end_idx = text.find('\n};', idx) + 3
hist_govs = json.loads(text[idx + len('window.SCENARIO_HISTORICAL_GOVERNORS = '):end_idx-1])

# Load CLAN_MASTER_DATA
idx = text.find('window.CLAN_MASTER_DATA = {')
end_idx = text.find('\n};', idx) + 3
clan_master = json.loads(text[idx + len('window.CLAN_MASTER_DATA = '):end_idx-1])

# Load historical_jodai.js roster if any
with open('js/historical_jodai.js', 'r', encoding='utf-8') as f:
    jodai_text = f.read()

# Let's see if historical_jodai adds officers to window.OFFICERS_MASTER
# We can parse roster in historical_jodai.js
# But let's first simulate standard switchScenario without jodai, or with jodai

def is_capital_province(prov_id, clan_id, scen):
    # Check clan_master capital
    cm = clan_master.get(clan_id)
    if cm and cm.get('capital') == prov_id:
        return True
    # If not specified, default to first province owned
    owners = scen.get('owners', {})
    owned = [p for p, o in owners.items() if o == clan_id]
    if owned and owned[0] == prov_id:
        return True
    return False

# Simulate for each scenario
out = []
total_real_empty = 0

for scen in scenarios:
    sid = str(scen['id'])
    year = scen['year']
    title = scen['title']
    owners = scen.get('owners', {})
    
    # 1. alive officers
    active_officers = []
    for m in officers_master:
        by = m.get('birthYear')
        dy = m.get('deathYear')
        if by is not None and dy is not None:
            age = year - by
            if age >= 15 and year <= dy:
                o = dict(m)
                o['isDaimyo'] = False
                o['assignedProvId'] = None
                active_officers.append(o)
                
    # 2. leader identification
    active_owners = set(owners.values())
    for owner_id in active_owners:
        if not owner_id: continue
        # playable or clan leader
        playable = None
        for d in scen.get('playables', []):
            if d.get('id') == owner_id:
                playable = d
                break
        leader_name = playable.get('name') if playable else None
        
        leader_officer = None
        clan_officers = [o for o in active_officers if o.get('clanId') == owner_id]
        if leader_name:
            for o in clan_officers:
                if o.get('name') == leader_name:
                    leader_officer = o
                    break
            if not leader_officer:
                for o in active_officers:
                    if o.get('name') == leader_name:
                        leader_officer = o
                        o['clanId'] = owner_id
                        break
        if not leader_officer and clan_officers:
            leader_officer = clan_officers[0]
            
        if leader_officer:
            leader_officer['isDaimyo'] = True
            
    # Step 1: Assign Daimyo to Capital
    prov_gov = {}
    for prov_id, owner_id in owners.items():
        if not owner_id: continue
        if is_capital_province(prov_id, owner_id, scen):
            d_off = None
            for o in active_officers:
                if o.get('clanId') == owner_id and o.get('isDaimyo') and not o.get('assignedProvId'):
                    d_off = o
                    break
            if d_off:
                prov_gov[prov_id] = d_off['id']
                d_off['assignedProvId'] = prov_id
                
    # Step 2: Historical Governors
    scen_hist = hist_govs.get(sid, {})
    for prov_id, owner_id in owners.items():
        if not owner_id: continue
        if prov_id not in prov_gov and not is_capital_province(prov_id, owner_id, scen):
            target = scen_hist.get(prov_id)
            if target:
                hist_off = None
                for o in active_officers:
                    if (o.get('id') == target or o.get('name') == target) and not o.get('assignedProvId') and not o.get('isDaimyo'):
                        if o.get('clanId') == owner_id:
                            hist_off = o
                            break
                if not hist_off:
                    for o in active_officers:
                        if (o.get('id') == target or o.get('name') == target) and not o.get('assignedProvId') and not o.get('isDaimyo'):
                            hist_off = o
                            o['clanId'] = owner_id
                            break
                if hist_off:
                    prov_gov[prov_id] = hist_off['id']
                    hist_off['assignedProvId'] = prov_id
                    
    # Remaining unassigned provinces (truly jodai!)
    unassigned = []
    for prov_id, owner_id in owners.items():
        if not owner_id: continue
        if prov_id not in prov_gov:
            target = scen_hist.get(prov_id)
            unassigned.append((prov_id, owner_id, target))
            
    total_real_empty += len(unassigned)
    out.append(f"Scenario {sid} ({year} {title}) | Owners: {len(owners)} | Truly JODAI (no governor): {len(unassigned)}")
    for p, o, t in unassigned:
        out.append(f"   [JODAI] prov: {p:<16} owner: {o:<18} (histGov target was: {t})")

out.append(f"\nTOTAL TRULY JODAI PROVINCES: {total_real_empty}")

with open('truly_jodai_scenarios_utf8.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(out))

print(f"Simulation done! Total truly jodai: {total_real_empty}")
