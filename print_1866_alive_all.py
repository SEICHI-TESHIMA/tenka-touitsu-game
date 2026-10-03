import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('window.OFFICERS_MASTER = [')
end_idx = text.find('\n];', start_idx) + 2
officers = json.loads(text[start_idx + len('window.OFFICERS_MASTER = '):end_idx])

alive_1866 = []
for o in officers:
    by = o.get('birthYear')
    dy = o.get('deathYear')
    if by is not None and dy is not None:
        if 1866 - by >= 15 and 1866 <= dy:
            alive_1866.append(o)

out = [f"Total alive officers in 1866: {len(alive_1866)}"]
for o in alive_1866:
    out.append(f"  {o['id']:<30} | {o['name']:<12} | clan:{str(o.get('clanId')):<14} | prov:{str(o.get('defaultProv'))}")

with open('alive_1866_utf8.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(out))

print("Saved alive_1866_utf8.txt")
