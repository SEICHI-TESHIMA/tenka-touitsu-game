import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('window.SCENARIOS_DATA = [')
end_idx = text.find('\n];', start_idx) + 2
scenarios = json.loads(text[start_idx + len('window.SCENARIOS_DATA = '):end_idx])

out = []
for s in scenarios:
    sid = s.get('id')
    title = s.get('title')
    year = s.get('year')
    
    daimyo = s.get('daimyo', {})
    for clan_id, dinfo in daimyo.items():
        if '真田幸村' in str(dinfo):
            out.append(f"Scenario {sid} ({year} {title}) daimyo: {clan_id} -> {dinfo}")
            
    govs = s.get('governors', {})
    for prov, gname in govs.items():
        if '真田幸村' in str(gname):
            out.append(f"Scenario {sid} ({year} {title}) governor in {prov}: {gname}")
            
    officers = s.get('officers', {})
    for clan_id, oflist in officers.items():
        if '真田幸村' in str(oflist):
            out.append(f"Scenario {sid} ({year} {title}) officers of {clan_id}: {oflist}")
            
    ronin = s.get('ronin', {})
    for prov, rlist in ronin.items():
        if '真田幸村' in str(rlist):
            out.append(f"Scenario {sid} ({year} {title}) ronin in {prov}: {rlist}")

out.append(f"\nTotal scenario matches for 真田幸村: {len(out)}")

lines = text.splitlines()
out.append("\nLines in data.js with 真田幸村:")
for i, line in enumerate(lines):
    if "真田幸村" in line:
        out.append(f"Line {i+1}: {line.strip()[:140]}")

with open('yukimura_results_utf8.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(out))
