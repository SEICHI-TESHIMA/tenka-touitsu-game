import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('window.OFFICERS_MASTER = [')
end_idx = text.find('\n];', start_idx) + 2
officers = json.loads(text[start_idx + len('window.OFFICERS_MASTER = '):end_idx])

start_idx = text.find('window.SCENARIOS_DATA = [')
end_idx = text.find('\n];', start_idx) + 2
scenarios = json.loads(text[start_idx + len('window.SCENARIOS_DATA = '):end_idx])

idx = text.find('window.SCENARIO_HISTORICAL_GOVERNORS = {')
end_idx = text.find('\n};', idx) + 3
hist_govs = json.loads(text[idx + len('window.SCENARIO_HISTORICAL_GOVERNORS = '):end_idx-1])

idx = text.find('window.CLAN_MASTER_DATA = {')
end_idx = text.find('\n};', idx) + 3
clan_master = json.loads(text[idx + len('window.CLAN_MASTER_DATA = '):end_idx-1])

def is_cap(p, o, s):
    cm = clan_master.get(o)
    if cm and cm.get('capital') == p: return True
    owned = [k for k, v in s.get('owners', {}).items() if v == o]
    return owned and owned[0] == p

# Check unassigned per scenario and find matching candidates in OFFICERS_MASTER
report = []

for s in scenarios:
    sid = str(s['id'])
    year = s['year']
    title = s['title']
    owners = s.get('owners', {})
    scen_h = hist_govs.get(sid, {})
    
    # get alive officers
    alive = []
    for o in officers:
        by = o.get('birthYear')
        dy = o.get('deathYear')
        if by is not None and dy is not None:
            if year - by >= 15 and year <= dy:
                alive.append(o)
                
    # find empty branches
    empty_branches = []
    for p, o in owners.items():
        if not o: continue
        target = scen_h.get(p)
        # Check if target is valid alive officer
        target_valid = False
        if target:
            for al in alive:
                if al['id'] == target or al['name'] == target:
                    target_valid = True
                    break
        if not target_valid and not is_cap(p, o, s):
            empty_branches.append((p, o, target))
            
    if empty_branches:
        report.append(f"Scenario {sid} ({year} {title}) - Missing Govs: {len(empty_branches)}")
        for p, o, t in empty_branches:
            # find candidates in alive officers who have matching defaultProv or clanId
            cands = [al['name'] for al in alive if al.get('defaultProv') == p]
            if not cands:
                cands = [al['name'] for al in alive if al.get('clanId') == o]
            report.append(f"   {p:<16} (owner: {o:<16}, currentTarget: {str(t):<24}) -> cands: {', '.join(cands[:4])}")

with open('missing_govs_analysis_utf8.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(report))

print(f"Saved missing_govs_analysis_utf8.txt. Total scenarios with missing govs: {len(report)}")
