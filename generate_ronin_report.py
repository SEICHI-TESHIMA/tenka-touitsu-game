import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

def parse_section(prefix, next_prefix):
    start = text.find(prefix) + len(prefix)
    end = text.find(next_prefix, start) if next_prefix else len(text)
    body = text[start:end].strip()
    last_b = max(body.rfind(']'), body.rfind('}'))
    return json.loads(body[:last_b+1])

provs = parse_section('window.PROVINCES_DATA =', 'window.OFFICERS_MASTER =')
officers_master = parse_section('window.OFFICERS_MASTER =', 'window.SCENARIOS_DATA =')
scenarios = parse_section('window.SCENARIOS_DATA =', 'window.CLAN_MASTER_DATA =')
clans = parse_section('window.CLAN_MASTER_DATA =', 'window.CLAN_ABILITIES =')
hist_govs = parse_section('window.SCENARIO_HISTORICAL_GOVERNORS =', 'window.CLAN_CAPITAL_PROVINCES =')
capitals = parse_section('window.CLAN_CAPITAL_PROVINCES =', None)

with open('detailed_ronin_report.txt', 'w', encoding='utf-8') as out:
    for scen in scenarios:
        sid = str(scen['id'])
        y = scen['year']
        t = scen['title']
        owners = scen.get('owners', {})
        landed_clans = set(owners.values()) - {None, '', 'null'}
        govs = hist_govs.get(sid, {})
        gov_ids = set(govs.values())
        
        active = [o for o in officers_master if o.get('birthYear') and o.get('deathYear') and o['birthYear'] + 15 <= y <= o['deathYear']]
        
        # Check officers who become ronin
        # An officer is landed if their clanId is in landed_clans OR they are assigned to a gov in govs
        unlanded = []
        for o in active:
            cid = o.get('clanId')
            if cid not in landed_clans and o['id'] not in gov_ids and o['name'] not in gov_ids:
                unlanded.append(o)
                
        out.write(f"\n=======================================================\n")
        out.write(f"Scenario [{sid}] {y} {t} | Landed Clans: {len(landed_clans)} | Total Active: {len(active)} | Unlanded/Ronin: {len(unlanded)}\n")
        out.write(f"Landed Clans: {sorted(list(landed_clans))}\n")
        out.write(f"-------------------------------------------------------\n")
        
        # Group unlanded by:
        # 1. Has historical name (not generic succ/event)
        # 2. Check if their defaultProv is owned by a landed clan
        for o in unlanded:
            is_generic = o['id'].startswith('off_succ_') or o['id'].startswith('off_succ2_') or o['id'].startswith('off_dm_')
            def_p = o.get('defaultProv')
            p_owner = owners.get(def_p) if def_p else None
            out.write(f"  {o['id']:32s} | {o['name']:15s} | clan:{str(o.get('clanId')):15s} | defProv:{str(def_p):12s} (owner:{str(p_owner):12s}) | {o.get('lore', '')[:40]}\n")

print("Generated detailed_ronin_report.txt")

