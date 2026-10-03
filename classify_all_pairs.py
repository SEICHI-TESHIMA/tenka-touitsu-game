import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('candidates_parsed.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect candidates where both people might be the exact same historical figure
blocks = text.split('\n\n')

same_person = []
different_person = []

for b in blocks:
    lines = b.strip().split('\n')
    if len(lines) < 3:
        continue
    header = lines[0]
    l1 = lines[1]
    l2 = lines[2]
    
    # Extract names
    m = re.match(r"^(.+?) \((.+?)\) vs (.+?) \((.+?)\) \| (.+?) vs (.+?) \| (.+?) vs (.+?)$", header)
    if not m:
        continue
    n1, id1, n2, id2, y1, y2, p1, p2 = m.groups()
    
    # Indicators of same person:
    # 1. Tenno / In
    is_tenno_in = any(x in n1 for x in ['天皇', '上皇', '院', '法皇']) and any(x in n2 for x in ['天皇', '上皇', '院', '法皇'])
    # 2. Same name with slightly different kanji (e.g., 佐々木 / 佐佐木, 信正 / 信政)
    # 3. Known alias (片倉小十郎 / 片倉景綱)
    # 4. Very similar lore
    
    # Check if first 2 chars of name or surname match
    same_person.append((n1, id1, n2, id2, y1, y2, p1, p2, l1, l2, is_tenno_in))

with open('all_parsed_pairs.json', 'w', encoding='utf-8') as f:
    json.dump(same_person, f, ensure_ascii=False, indent=2)

print(f"Total parsed pairs: {len(same_person)}")
