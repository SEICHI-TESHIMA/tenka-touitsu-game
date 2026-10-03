import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'window\.OFFICERS_MASTER\s*=\s*(\[.*?\]);', text, re.DOTALL)
officers = json.loads(m.group(1))

print(f"Total officers: {len(officers)}")

# Let's inspect officers from index 1800 to end
for i in range(1800, min(1830, len(officers))):
    o = officers[i]
    print(f"[{i}] {o['id']}: {o['name']} ({o['birthYear']}-{o['deathYear']}) clan:{o.get('clanId')}")

print("...")
for i in range(1930, min(1960, len(officers))):
    o = officers[i]
    print(f"[{i}] {o['id']}: {o['name']} ({o['birthYear']}-{o['deathYear']}) clan:{o.get('clanId')}")
