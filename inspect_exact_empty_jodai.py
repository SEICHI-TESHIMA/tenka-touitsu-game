import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('window.OFFICERS_MASTER = [')
end_idx = text.find('\n];', start_idx) + 2
officers = json.loads(text[start_idx + len('window.OFFICERS_MASTER = '):end_idx])

start_idx_scen = text.find('window.SCENARIOS_DATA = [')
end_idx_scen = text.find('\n];', start_idx_scen) + 2
scenarios = json.loads(text[start_idx_scen + len('window.SCENARIOS_DATA = '):end_idx_scen])

idx_gov = text.find('window.SCENARIO_HISTORICAL_GOVERNORS = {')
end_idx_gov = text.find('\n};', idx_gov) + 3
hist_govs = json.loads(text[idx_gov + len('window.SCENARIO_HISTORICAL_GOVERNORS = '):end_idx_gov-1])

idx_cm = text.find('window.CLAN_CAPITAL_PROVINCES = {')
end_idx_cm = text.find('\n};', idx_cm) + 3
caps = json.loads(text[idx_cm + len('window.CLAN_CAPITAL_PROVINCES = '):end_idx_cm-1])

# Parse historical_jodai.js
with open('js/historical_jodai.js', 'r', encoding='utf-8') as f:
    jodai_text = f.read()

m_roster = re.search(r'const roster = (\[.*?\]);\s*const reuse =', jodai_text, re.DOTALL)
if m_roster:
    js_obj_str = m_roster.group(1)
    clean_json = re.sub(r'(\b[a-zA-Z_]\w*\b)\s*:', r'"\1":', js_obj_str)
    clean_json = re.sub(r',\s*([\]}])', r'\1', clean_json)
    try:
        roster = json.loads(clean_json)
        seq = 0
        for r in roster:
            alive_posts = [p for p in r['posts'] if int(p['year']) - r['birth'] >= 15 and int(p['year']) <= r['death']]
            if not alive_posts: continue
            seq += 1
            oid = f"off_jd_{str(seq).zfill(3)}"
            first = alive_posts[0]
            officers.append({
                "id": oid,
                "name": r['name'],
                "clanId": first['clan'],
                "defaultProv": first['prov'],
                "birthYear": r['birth'],
                "deathYear": r['death'],
                "isDaimyo": False
            })
            for p in alive_posts:
                key = str(p['year'])
                hist_govs.setdefault(key, {})[p['prov']] = oid
    except Exception as e:
        print("Roster parse failed:", e)

m_reuse = re.search(r'const reuse = (\[.*?\]);', jodai_text, re.DOTALL)
if m_reuse:
    clean_reuse = re.sub(r'(\b[a-zA-Z_]\w*\b)\s*:', r'"\1":', m_reuse.group(1))
    clean_reuse = re.sub(r',\s*([\]}])', r'\1', clean_reuse)
    try:
        reuse = json.loads(clean_reuse)
        for row in reuse:
            key = str(row['year'])
            hist_govs.setdefault(key, {})[row['prov']] = row['id']
    except Exception as e:
        print("Reuse parse failed:", e)

officers_map = {o['id']: o for o in officers}

def is_capital_correct(p, o, owners):
    registered = caps.get(o)
    owned = [k for k, v in owners.items() if v == o]
    if registered and registered in owned:
        return p == registered
    return owned and owned[0] == p

target_sids = ['1789', '1467', '1438', '1221', '1156', '939', '1028', '1056', '1087']

for scen in scenarios:
    sid = str(scen['id'])
    if sid not in target_sids: continue
    year = scen['year']
    title = scen['title']
    owners = scen.get('owners', {})
    govs = hist_govs.get(sid, {})
    
    empty_list = []
    for p, o in owners.items():
        if not o: continue
        is_cap = is_capital_correct(p, o, owners)
        target = govs.get(p)
        off = officers_map.get(target)
        if not is_cap and not off:
            empty_list.append((p, o, target))
            
    print(f"\nScenario {sid} ({year} {title}) | Empty: {len(empty_list)}")
    for p, o, target in empty_list:
        print(f"  prov:{p:<15} owner:{o:<20} assignedTarget:{target}")
