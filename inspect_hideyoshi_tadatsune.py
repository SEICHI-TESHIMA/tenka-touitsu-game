import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

officers = json.loads(text[text.find('window.OFFICERS_MASTER =') + len('window.OFFICERS_MASTER ='):text.find('window.SCENARIOS_DATA =')].strip().rstrip(';'))

print("Matching 秀吉:")
for o in officers:
    if '秀吉' in o['name'] or 'hideyoshi' in o['id']:
        print(f"  {o['id']}: name={o['name']}, birth={o.get('birthYear')}, death={o.get('deathYear')}, clanId={o.get('clanId')}")

print("\nMatching 忠恒 / 家久:")
for o in officers:
    if '忠恒' in o['name'] or '家久' in o['name'] or 'tadatsune' in o['id']:
        print(f"  {o['id']}: name={o['name']}, birth={o.get('birthYear')}, death={o.get('deathYear')}, clanId={o.get('clanId')}")
