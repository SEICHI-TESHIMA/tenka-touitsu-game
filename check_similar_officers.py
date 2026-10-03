import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'window\.OFFICERS_MASTER\s*=\s*(\[.*?\]);', text, re.DOTALL)
officers = json.loads(m.group(1))

# Check for parentheses in officer names
parens = [o for o in officers if '(' in o.get('name', '') or '（' in o.get('name', '')]
print(f"Officers with parentheses: {len(parens)}")
for o in parens:
    print(f"  {o['id']}: {o['name']}")

# Check for officers with similar birth/death years and similar clans/provinces
# E.g., birthYear == birthYear and deathYear == deathYear in same province
by_birth_prov = {}
potential_similar = []
for o in officers:
    b = o.get('birthYear')
    d = o.get('deathYear')
    prov = o.get('defaultProv')
    clan = o.get('clanId')
    name = o.get('name')
    if b is not None and d is not None:
        key = (b, d, prov)
        if key in by_birth_prov:
            potential_similar.append((by_birth_prov[key], o))
        else:
            by_birth_prov[key] = o

print(f"\nPotential duplicate candidates by same (birthYear, deathYear, defaultProv): {len(potential_similar)}")
for o1, o2 in potential_similar:
    print(f"  Match: [{o1['id']}] '{o1['name']}' vs [{o2['id']}] '{o2['name']}' (birth: {o1['birthYear']}-{o1['deathYear']}, prov: {o1['defaultProv']})")
