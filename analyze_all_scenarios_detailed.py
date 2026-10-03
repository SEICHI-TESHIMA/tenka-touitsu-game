import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

scenarios = json.loads(text[text.find('window.SCENARIOS_DATA =') + len('window.SCENARIOS_DATA ='):text.find('window.CLAN_MASTER_DATA =')].strip().rstrip(';'))
clans = json.loads(text[text.find('window.CLAN_MASTER_DATA =') + len('window.CLAN_MASTER_DATA ='):text.find('window.CLAN_ABILITIES =')].strip().rstrip(';'))
hist_govs = json.loads(text[text.find('window.SCENARIO_HISTORICAL_GOVERNORS =') + len('window.SCENARIO_HISTORICAL_GOVERNORS ='):text.find('window.CLAN_CAPITAL_PROVINCES =')].strip().rstrip(';'))
capitals = json.loads(text[text.find('window.CLAN_CAPITAL_PROVINCES =') + len('window.CLAN_CAPITAL_PROVINCES ='):].strip().rstrip(';'))
officers = json.loads(text[text.find('window.OFFICERS_MASTER =') + len('window.OFFICERS_MASTER ='):text.find('window.SCENARIOS_DATA =')].strip().rstrip(';'))

with open('js/historical_jodai.js', 'r', encoding='utf-8') as f:
    jodai_code = f.read()

officers_dict = {o['id']: o for o in officers}
officers_by_name = {}
for o in officers:
    officers_by_name.setdefault(o['name'], []).append(o)

print("=== CHECKING ALL 30 SCENARIOS: CLANS, CAPITAL, GOVERNORS, AND DATES ===")

for scen in scenarios:
    sid = str(scen['id'])
    year = scen['year']
    title = scen.get('title')
    owners = scen.get('owners', {})
    playables = {p['id']: p for p in scen.get('playables', [])}
    
    clan_provs = {}
    for pid, cid in owners.items():
        clan_provs.setdefault(cid, []).append(pid)
        
    scen_govs = hist_govs.get(sid, {})
    
    # Check each clan in this scenario
    clan_reports = []
    for cid, plist in clan_provs.items():
        cname = clans.get(cid, {}).get('name', cid)
        cap = capitals.get(cid)
        if not cap or cap not in plist:
            cap = plist[0]
            
        # check playable leader name
        p_info = playables.get(cid)
        leader_name = p_info['name'] if p_info else None
        
        # Check officers belonging to this clan alive in this year
        clan_offs = [o for o in officers if o.get('clanId') == cid and o.get('birthYear') and o.get('deathYear') and (year - o['birthYear'] >= 15) and (year <= o['deathYear'])]
        
        # Find which provinces have governors
        branch_provinces = [p for p in plist if p != cap]
        gov_details = []
        missing_govs = []
        for bp in branch_provinces:
            if bp in scen_govs:
                gid = scen_govs[bp]
                g_off = officers_dict.get(gid)
                g_name = g_off['name'] if g_off else gid
                gov_details.append(f"{bp}:{g_name}")
            else:
                missing_govs.append(bp)
                
        clan_reports.append({
            'cid': cid,
            'cname': cname,
            'provs_count': len(plist),
            'cap': cap,
            'leader_name': leader_name,
            'alive_offs_count': len(clan_offs),
            'missing_govs': missing_govs,
            'gov_details': gov_details
        })
        
    # Summarize scenario
    total_missing = sum(len(cr['missing_govs']) for cr in clan_reports)
    total_branch = sum(max(0, cr['provs_count'] - 1) for cr in clan_reports)
    assigned_count = total_branch - total_missing
    print(f"\n[{sid}] ({year}年) {title}: Branch Castles={total_branch}, Assigned={assigned_count}, Missing={total_missing}")
    for cr in clan_reports:
        if cr['missing_govs']:
            print(f"  * {cr['cname']} ({cr['cid']}) [Total={cr['provs_count']}, Cap={cr['cap']}]: Missing {len(cr['missing_govs'])} -> {cr['missing_govs']}")
