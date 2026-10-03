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

clan_name_map = {cid: cdata.get('name', cid) for cid, cdata in clans.items()}

# Also read historical_jodai.js to see what jodai exist
with open('js/historical_jodai.js', 'r', encoding='utf-8') as f:
    jodai_text = f.read()

print("=== CHECKING ALL SCENARIOS FOR MISSING GOVERNORS ===")

for scen in scenarios:
    sid = str(scen['id'])
    year = scen['year']
    title = scen.get('title')
    owners = scen.get('owners', {})
    
    clan_provs = {}
    for pid, cid in owners.items():
        clan_provs.setdefault(cid, []).append(pid)
        
    scen_govs = hist_govs.get(sid, {})
    
    missing_by_clan = {}
    for pid, cid in owners.items():
        # A province needs a governor if it's NOT the capital
        # Capital is capitals.get(cid) or if clan only has 1 prov
        clan_p_list = clan_provs.get(cid, [])
        is_cap = (capitals.get(cid) == pid) if len(clan_p_list) > 1 else True
        if not is_cap:
            if pid not in scen_govs:
                missing_by_clan.setdefault(cid, []).append(pid)
                
    if missing_by_clan:
        total_missing = sum(len(v) for v in missing_by_clan.values())
        print(f"\n[{sid}] ({year}) {title} - Missing Govs: {total_missing}")
        for cid, m_provs in missing_by_clan.items():
            cname = clan_name_map.get(cid, cid)
            print(f"  Clan {cname} ({cid}) [Total Provs={len(clan_provs[cid])}]: Missing {len(m_provs)} -> {m_provs}")
