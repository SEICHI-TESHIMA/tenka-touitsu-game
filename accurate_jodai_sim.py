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

# Parse historical_jodai.js accurately
with open('js/historical_jodai.js', 'r', encoding='utf-8') as f:
    jodai_text = f.read()

# Find roster string between 'const roster = [' and '];'
idx_r_start = jodai_text.find('const roster = [')
idx_r_end = jodai_text.find('\n  ];\n\n  const reuse =', idx_r_start)
if idx_r_end == -1:
    idx_r_end = jodai_text.find('];\n\n  const reuse =', idx_r_start)
if idx_r_end == -1:
    idx_r_end = jodai_text.find('const reuse =', idx_r_start)
    idx_r_end = jodai_text.rfind('];', 0, idx_r_end)

roster_str = jodai_text[idx_r_start + len('const roster = '): idx_r_end + 1]

# Convert JS array of objects to Python objects
# Use regex to extract each object
pattern = r'\{\s*name:\s*"([^"]+)",\s*birth:\s*(\d+),\s*death:\s*(\d+).*?posts:\s*(\[[^\]]+\])\s*\}'
matches = re.findall(pattern, roster_str, re.DOTALL)
print(f"Parsed {len(matches)} officers from historical_jodai.js roster.")

existing = set(o['name'] for o in officers)
seq = 0
for name, birth, death, posts_str in matches:
    if name in existing: continue
    birth = int(birth)
    death = int(death)
    # Parse posts
    post_matches = re.findall(r'\{\s*year:\s*"([^"]+)",\s*prov:\s*"([^"]+)",\s*clan:\s*"([^"]+)"\s*\}', posts_str)
    alive_posts = [p for p in post_matches if int(p[0]) - birth >= 15 and int(p[0]) <= death]
    if not alive_posts: continue
    seq += 1
    oid = f"off_jd_{str(seq).zfill(3)}"
    first = alive_posts[0]
    officers.append({
        "id": oid,
        "name": name,
        "clanId": first[2],
        "defaultProv": first[1],
        "birthYear": birth,
        "deathYear": death,
        "isDaimyo": False
    })
    existing.add(name)
    for p in alive_posts:
        key = str(p[0])
        hist_govs.setdefault(key, {})[p[1]] = oid

# Reuse
idx_reuse_start = jodai_text.find('const reuse = [')
idx_reuse_end = jodai_text.find('];', idx_reuse_start)
reuse_str = jodai_text[idx_reuse_start + len('const reuse = '): idx_reuse_end + 1]
reuse_matches = re.findall(r'\{\s*year:\s*"([^"]+)",\s*prov:\s*"([^"]+)",\s*id:\s*"([^"]+)"', reuse_str)
print(f"Parsed {len(reuse_matches)} reuse entries.")
for y, p, oid in reuse_matches:
    hist_govs.setdefault(y, {})[p] = oid

officers_map = {o['id']: o for o in officers}

def is_capital_correct(p, o, owners):
    registered = caps.get(o)
    owned = [k for k, v in owners.items() if v == o]
    if registered and registered in owned:
        return p == registered
    return owned and owned[0] == p

total_empty = 0
for scen in scenarios:
    sid = str(scen['id'])
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
            empty_list.append((p, o))
            
    total_empty += len(empty_list)
    print(f"Scenario {sid:<5} ({year:<4} {title:<16}) | Empty/Jodai: {len(empty_list):<2}")

print(f"\nREAL-WORLD TOTAL EMPTY ACROSS ALL SCENARIOS: {total_empty}")
