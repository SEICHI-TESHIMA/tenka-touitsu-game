import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    data_text = f.read()

start_idx = data_text.find('window.OFFICERS_MASTER = [')
end_idx = data_text.find('\n];', start_idx) + 2
officers_master = json.loads(data_text[start_idx + len('window.OFFICERS_MASTER = '):end_idx])

out = []
for o in officers_master:
    if '真田' in o.get('name', ''):
        out.append(f"{o.get('id')}: {o.get('name')} (born {o.get('birthYear')}, died {o.get('deathYear')}, clan: {o.get('clanId')}, prov: {o.get('defaultProv')})")

with open('sanada_officers_list.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(out))

print("Saved sanada_officers_list.txt")
