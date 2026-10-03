import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('similar_name_only.txt', 'r', encoding='utf-8') as f:
    text = f.read()

blocks = text.split('\n\n')
print(f"Total blocks: {len(blocks)}")

# Let's inspect all blocks to find candidates that refer to the same historical figure
# Usually they share same family or same given name or title
candidates = []
for b in blocks:
    lines = b.strip().split('\n')
    if not lines or not lines[0].startswith('[similar_name]'):
        continue
    header = lines[0]
    # parse: [similar_name] 'name1' (id1, clan1, y1, p1) vs 'name2' (id2, clan2, y2, p2)
    m = re.match(r"\[similar_name\] '([^']+)' \(([^,]+), ([^,]+), ([^,]+), ([^)]+)\) vs '([^']+)' \(([^,]+), ([^,]+), ([^,]+), ([^)]+)\)", header)
    if m:
        n1, id1, c1, y1, p1, n2, id2, c2, y2, p2 = m.groups()
        l1 = lines[1] if len(lines) > 1 else ''
        l2 = lines[2] if len(lines) > 2 else ''
        candidates.append((n1, id1, c1, y1, p1, n2, id2, c2, y2, p2, l1, l2))

with open('candidates_parsed.txt', 'w', encoding='utf-8') as f:
    for item in candidates:
        f.write(f"{item[0]} ({item[1]}) vs {item[5]} ({item[6]}) | {item[3]} vs {item[8]} | {item[4]} vs {item[9]}\n")
        f.write(f"  {item[10]}\n")
        f.write(f"  {item[11]}\n\n")

print("Saved candidates_parsed.txt")
