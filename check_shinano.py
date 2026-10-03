import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Check all references to 'shinano' vs 'north_shinano'
print("Checking shinano occurrences:")
import re
prov_shinano = re.findall(r'"defaultProv":\s*"(?:north_shinano|south_shinano|shinano)"', text)
from collections import Counter
print(Counter(prov_shinano))

# Let's check which officers have defaultProv "shinano"
officers_with_shinano = []
# Find in text
matches = re.finditer(r'\{\s*"id":\s*"([^"]+)",\s*"name":\s*"([^"]+)"[^}]+?"defaultProv":\s*"shinano"', text)
for m in matches:
    officers_with_shinano.append((m.group(1), m.group(2)))
print(f"Officers with defaultProv 'shinano': {len(officers_with_shinano)}")
for off in officers_with_shinano[:20]:
    print(off)

# Also let's check all provinces in INITIAL_PROVINCES
m_prov = re.search(r'const\s+INITIAL_PROVINCES\s*=\s*(\[.*?\]);', text, re.DOTALL)
if m_prov:
    provs = json.loads(m_prov.group(1))
    p_ids = [p['id'] for p in provs]
    print("Shinano provinces in INITIAL_PROVINCES:", [p for p in p_ids if 'shinano' in p])
