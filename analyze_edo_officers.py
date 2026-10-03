import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('window.OFFICERS_MASTER = [')
end_idx = text.find('\n];', start_idx) + 2
officers = json.loads(text[start_idx + len('window.OFFICERS_MASTER = '):end_idx])

edo_bakumatsu = [o for o in officers if o.get('era') in ['edo', 'bakumatsu']]
print(f"Total Edo/Bakumatsu officers in OFFICERS_MASTER: {len(edo_bakumatsu)}")

# group by era
by_era = {}
for o in edo_bakumatsu:
    e = o.get('era')
    by_era.setdefault(e, []).append(o)

print("Edo count:", len(by_era.get('edo', [])))
print("Bakumatsu count:", len(by_era.get('bakumatsu', [])))

# Let's see some notable names
print("\nSample Edo names:")
for o in by_era.get('edo', [])[:20]:
    print(f"  {o['id']}: {o['name']} ({o.get('birthYear')}-{o.get('deathYear')}) prov:{o.get('defaultProv')}")

print("\nSample Bakumatsu names:")
for o in by_era.get('bakumatsu', [])[:20]:
    print(f"  {o['id']}: {o['name']} ({o.get('birthYear')}-{o.get('deathYear')}) prov:{o.get('defaultProv')}")
