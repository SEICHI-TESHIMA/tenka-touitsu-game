import sys
import json
import re
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'window\.OFFICERS_MASTER\s*=\s*(\[.*?\]);', text, re.DOTALL)
officers = json.loads(m.group(1))

print(f"Total officers: {len(officers)}")

# Search for any officers with birth diff <= 5, death diff <= 5
pairs = []
n = len(officers)
for i in range(n):
    o1 = officers[i]
    b1, d1 = o1.get('birthYear'), o1.get('deathYear')
    if b1 is None or d1 is None:
        continue
    for j in range(i + 1, n):
        o2 = officers[j]
        b2, d2 = o2.get('birthYear'), o2.get('deathYear')
        if b2 is None or d2 is None:
            continue
        
        # Check if birth and death are within 5 years of each other
        if abs(b1 - b2) <= 5 and abs(d1 - d2) <= 5:
            n1 = o1.get('name', '')
            n2 = o2.get('name', '')
            # If names are identical
            if n1 == n2:
                pairs.append(('exact_name', o1, o2))
            else:
                # Check character overlap or substring or famous alias
                set1 = set(n1)
                set2 = set(n2)
                overlap = len(set1 & set2)
                if overlap >= 2 or n1 in n2 or n2 in n1:
                    pairs.append(('similar_name', o1, o2))
                elif o1.get('clanId') == o2.get('clanId') or o1.get('defaultProv') == o2.get('defaultProv'):
                    # Same clan or prov with close birth/death
                    pairs.append(('same_context', o1, o2))

print(f"Found {len(pairs)} candidate pairs.")

with open('similar_pairs_candidates.txt', 'w', encoding='utf-8') as f:
    for cat, o1, o2 in pairs:
        f.write(f"[{cat}] '{o1['name']}' ({o1['id']}, {o1.get('clanId')}, {o1['birthYear']}-{o1['deathYear']}, {o1.get('defaultProv')}) vs "
                f"'{o2['name']}' ({o2['id']}, {o2.get('clanId')}, {o2['birthYear']}-{o2['deathYear']}, {o2.get('defaultProv')})\n")
        f.write(f"    Lore1: {o1.get('lore')}\n")
        f.write(f"    Lore2: {o2.get('lore')}\n\n")

print("Saved to similar_pairs_candidates.txt")
