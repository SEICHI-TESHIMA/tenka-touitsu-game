import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('window.SCENARIO_HISTORICAL_GOVERNORS = {')
end_idx = text.find('\n};', idx) + 3
hist_govs = json.loads(text[idx + len('window.SCENARIO_HISTORICAL_GOVERNORS = '):end_idx-1])

start_idx = text.find('window.SCENARIOS_DATA = [')
end_idx = text.find('\n];', start_idx) + 2
scenarios = json.loads(text[start_idx + len('window.SCENARIOS_DATA = '):end_idx])

# Group scenarios into eras:
# 1. Ancient / Heian / Kamakura: 939 - 1350
# 2. Muromachi / Sengoku: 1438 - 1614
# 3. Edo / Bakumatsu: 1637 - 1868

def analyze_era(scen_ids, filename):
    out = []
    for s in scenarios:
        sid = str(s['id'])
        if sid not in scen_ids:
            continue
        year = s['year']
        title = s['title']
        owners = s.get('owners', {})
        scen_h = hist_govs.get(sid, {})
        
        empty = []
        for p, o in owners.items():
            if not o: continue
            if not scen_h.get(p):
                empty.append((p, o))
        out.append(f"### Scenario {sid} ({year} {title}) - Empty: {len(empty)} ###")
        for p, o in empty:
            out.append(f"  {p:<16} | owner: {o}")
        out.append("")
        
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("\n".join(out))
    print(f"Saved {filename}")

analyze_era(['939', '1028', '1056', '1087', '1156', '1180', '1221', '1331', '1333', '1336', '1350'], 'empty_ancient.txt')
analyze_era(['1438', '1467', '1495', '1546', '1560', '1570', '1582', '1584', '1587', '1590', '1592', '1600', '1614'], 'empty_sengoku.txt')
analyze_era(['1637', '1651', '1702', '1721', '1789', '1837', '1853', '1860', '1866', '1868'], 'empty_edo.txt')
