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
scenarios = parse_section('window.SCENARIOS_DATA =', 'window.CLAN_MASTER_DATA =')
hist_govs = parse_section('window.SCENARIO_HISTORICAL_GOVERNORS =', 'window.CLAN_CAPITAL_PROVINCES =')
capitals = parse_section('window.CLAN_CAPITAL_PROVINCES =', None)
officers_master = parse_section('window.OFFICERS_MASTER =', 'window.SCENARIOS_DATA =')
off_dict = {o['id']: o for o in officers_master}

with open('scenarios_governors_summary.txt', 'w', encoding='utf-8') as f:
    for scen in scenarios:
        sid = str(scen['id'])
        y = scen['year']
        t = scen['title']
        owners = scen.get('owners', {})
        govs = hist_govs.get(sid, {})
        f.write(f"\n=======================================================\n")
        f.write(f"Scenario [{sid}] {y} {t} (Owners: {len(owners)}, Govs: {len(govs)})\n")
        f.write(f"-------------------------------------------------------\n")
        
        # List all provinces in order
        for p in provs:
            pid = p['id']
            pname = p['name']
            owner = owners.get(pid)
            if not owner:
                continue
            is_cap = (capitals.get(owner) == pid)
            gov_id = govs.get(pid)
            gov_name = off_dict.get(gov_id, {}).get('name', gov_id) if gov_id else ('(CAPITAL/DAIMYO)' if is_cap else '(EMPTY/NONE)')
            f.write(f"  {pid:14s} ({pname:4s}): owner={owner:15s} | gov={str(gov_name):20s} [id:{str(gov_id)}]\n")

print("Written scenarios_governors_summary.txt")

