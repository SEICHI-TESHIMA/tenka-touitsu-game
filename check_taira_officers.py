import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx_off = text.find('window.OFFICERS_MASTER = [')
end_off = text.find('];', idx_off)
officers = json.loads(text[idx_off + len('window.OFFICERS_MASTER = '): end_off + 1])
officers_dict = {o['id']: o for o in officers}

# Check for Taira officers
taira_officers = [o for o in officers if 'taira' in o['id'] or '平' in o['name']]
print(f"Total Taira officers: {len(taira_officers)}")
for o in taira_officers[:25]:
    print(f"  {o['id']:<25} {o['name']:<12} {o.get('birthYear')}-{o.get('deathYear')}")
