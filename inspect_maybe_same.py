import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

with open('all_parsed_pairs.json', 'r', encoding='utf-8') as f:
    pairs = json.load(f)

# Inspect all 175 pairs
definite_same = []
maybe_same = []

for item in pairs:
    n1, id1, n2, id2, y1, y2, p1, p2, l1, l2, is_tenno = item
    
    # Check exact same name
    if n1 == n2:
        definite_same.append(item)
        continue
        
    # Check if names are variations
    if (n1 == '佐々木広綱' and n2 == '佐佐木広綱') or (n1 == '片倉小十郎' and n2 == '片倉景綱') or \
       (n1 == '武田信正' and n2 == '武田信政') or (n1 == '後白河天皇' and n2 == '後白河院') or \
       (n1 == '後鳥羽上皇' and n2 == '後鳥羽天皇') or (n1 == '後嵯峨上皇' and n2 == '後嵯峨天皇'):
        definite_same.append(item)
        continue

    # Let's check other possible aliases:
    # Are there any other pairs where given name or family name indicates same person?
    maybe_same.append(item)

print(f"Definite same from 175: {len(definite_same)}")
print(f"Others to inspect: {len(maybe_same)}")

with open('maybe_same.txt', 'w', encoding='utf-8') as f:
    for item in maybe_same:
        f.write(f"{item[0]} ({item[1]}) vs {item[2]} ({item[3]}) | {item[4]} vs {item[5]} | {item[6]} vs {item[7]}\n")
        f.write(f"  {item[8]}\n")
        f.write(f"  {item[9]}\n\n")

print("Saved maybe_same.txt")
