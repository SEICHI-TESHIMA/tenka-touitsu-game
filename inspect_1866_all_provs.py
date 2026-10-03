import json

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

idx_cm = text.find('window.CLAN_MASTER_DATA = {')
end_idx_cm = text.find('\n};', idx_cm) + 3
clan_master = json.loads(text[idx_cm + len('window.CLAN_MASTER_DATA = '):end_idx_cm-1])

officers_map = {o['id']: o for o in officers}
scen_1866 = [s for s in scenarios if str(s['id']) == '1866'][0]
owners_1866 = scen_1866['owners']
govs_1866 = hist_govs.get('1866', {})

def is_capital(p, o):
    cm = clan_master.get(o)
    if cm and cm.get('capital') == p: return True
    owned = [k for k, v in owners_1866.items() if v == o]
    return owned and owned[0] == p

out = []
empty_count = 0
for p, o in owners_1866.items():
    if not o: continue
    is_cap = is_capital(p, o)
    target = govs_1866.get(p)
    off = officers_map.get(target)
    
    if is_cap:
        out.append(f"{p:<16} | owner:{o:<16} | [CAPITAL DAIMYO]")
    elif off:
        out.append(f"{p:<16} | owner:{o:<16} | [GOVERNOR] {off['name']} ({off['id']})")
    else:
        empty_count += 1
        out.append(f"{p:<16} | owner:{o:<16} | [EMPTY JODAI!]")

print(f"Scenario 1866: Total empty/jodai remaining: {empty_count}")
with open('scenario_1866_all_provs_utf8.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(out))
