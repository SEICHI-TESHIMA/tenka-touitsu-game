import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('window.OFFICERS_MASTER = [')
end_idx = text.find('\n];', start_idx) + 2
officers = json.loads(text[start_idx + len('window.OFFICERS_MASTER = '):end_idx])

names = ['島津久光', '毛利敬親', '山内容堂', '片倉重長', '阿部正弘', '島津斉彬', '小早川秀包', '浅野幸長', '山名祐豊', '平忠常']
for n in names:
    matches = [o for o in officers if n in o.get('name', '')]
    if matches:
        print(f"Name {n}: {[m['id'] + ':' + m['name'] for m in matches]}")
    else:
        print(f"Name {n}: NOT FOUND")
