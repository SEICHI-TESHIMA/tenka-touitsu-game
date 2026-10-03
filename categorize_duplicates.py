import sys
import json
import re
from collections import defaultdict

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'window\.OFFICERS_MASTER\s*=\s*(\[.*?\]);', text, re.DOTALL)
officers = json.loads(m.group(1))

# Group by name
name_map = defaultdict(list)
for idx, o in enumerate(officers):
    name_map[o.get('name')].append(o)

dup_names = {k: v for k, v in name_map.items() if len(v) > 1}

same_person_candidates = []
different_person_candidates = []

for name, offs in dup_names.items():
    births = [o.get('birthYear') for o in offs if o.get('birthYear') is not None]
    if len(births) >= 2:
        diff = max(births) - min(births)
        if diff <= 80:
            same_person_candidates.append((name, offs, diff))
        else:
            different_person_candidates.append((name, offs, diff))
    else:
        same_person_candidates.append((name, offs, 0))

lines = []
lines.append(f"Total duplicate name groups: {len(dup_names)}")
lines.append(f"Likely duplicate (birth diff <= 80): {len(same_person_candidates)}")
lines.append(f"Likely different era (birth diff > 80): {len(different_person_candidates)}")

lines.append("\n=== LIKELY DUPLICATES (birth diff <= 80) ===")
for name, offs, diff in same_person_candidates:
    lines.append(f"\n{name} (diff={diff}y):")
    for o in offs:
        lines.append(f"  id: {o.get('id')}, birth: {o.get('birthYear')}-{o.get('deathYear')}, "
                     f"stats: L{o.get('lead')}/B{o.get('bra')}/I{o.get('int')}/P{o.get('pol')}")

lines.append("\n=== LIKELY DIFFERENT ERA (birth diff > 80) ===")
for name, offs, diff in different_person_candidates:
    lines.append(f"\n{name} (diff={diff}y):")
    for o in offs:
        lines.append(f"  id: {o.get('id')}, birth: {o.get('birthYear')}-{o.get('deathYear')}, "
                     f"stats: L{o.get('lead')}/B{o.get('bra')}/I{o.get('int')}/P{o.get('pol')}")

with open('categorize_duplicates_utf8.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("Saved categorize_duplicates_utf8.txt successfully.")
