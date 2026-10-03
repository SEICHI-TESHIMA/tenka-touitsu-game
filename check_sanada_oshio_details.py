import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('window.OFFICERS_MASTER = [')
end_idx = text.find('\n];', start_idx) + 2
officers = json.loads(text[start_idx + len('window.OFFICERS_MASTER = '):end_idx])

# Check Sanada Yukinori vs Yukimoto
for o in officers:
    if '真田幸教' in o.get('name', ''):
        print("Sanada Yukinori/Yukimoto:", o)

# Check Oshio officers to delete
oshio_to_delete = []
for o in officers:
    oid = o['id']
    name = o.get('name', '')
    if name == '大塩門人(残党)':
        oshio_to_delete.append(o)
    elif oid in ['off_edo_oshio_1855_12', 'off_edo_oshio_1890_13', 'off_edo_oshio_1925_14', 'off_oshio_succ_3']:
        oshio_to_delete.append(o)
    elif name == '大塩格之助' and oid == 'off_oshio_succ_1':
        oshio_to_delete.append(o)

print(f"\nOshio officers to delete: {len(oshio_to_delete)}")
for o in oshio_to_delete:
    print(f"  Delete: {o['id']} ({o.get('name')}, born {o.get('birthYear')}, died {o.get('deathYear')})")
