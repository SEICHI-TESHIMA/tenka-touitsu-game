import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('window.OFFICERS_MASTER = [')
end_idx = text.find('\n];', start_idx) + 2
officers = json.loads(text[start_idx + len('window.OFFICERS_MASTER = '):end_idx])

names = ['島津久光', '前田利政', '香川親和', '花房正成', '小早川秀包', '南部信直', '里見義堯', '尼子晴久', '南部重直', '南部利直']
for n in names:
    matches = [o for o in officers if n in o.get('name', '')]
    if matches:
        print(f"{n}: {[m['id'] for m in matches]}")
    else:
        print(f"{n}: NOT FOUND")
