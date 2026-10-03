import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('window.OFFICERS_MASTER = [')
end_idx = text.find('\n];', start_idx) + 2
officers = json.loads(text[start_idx + len('window.OFFICERS_MASTER = '):end_idx])

keys = ['hachisuka', 'kuki', 'tsutsui', 'katagiri', 'wakisaka', 'ikoma', 'nanjo', 'miyabe', 'maeno']
for k in keys:
    matches = [o for o in officers if k in o['id'].lower() or k in o.get('name', '').lower()]
    print(f"Key {k}: {[m['id'] + ':' + m['name'] for m in matches]}")
