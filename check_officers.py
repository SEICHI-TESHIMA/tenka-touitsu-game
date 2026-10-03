import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

off_idx = text.find('window.OFFICERS_MASTER =')
scen_idx = text.find('window.SCENARIOS_DATA =')
officers = json.loads(text[off_idx + len('window.OFFICERS_MASTER ='):scen_idx].strip().rstrip(';'))

print(f"Total officers in OFFICERS_MASTER: {len(officers)}")

search_terms = ['九戸', '由比', '由井', '丸橋', '大塩', '武田耕雲斎', '藤田小四郎', '天狗', '生田', '平野国臣', '吉村寅太郎', '中山忠光', '松倉', '板倉重昌', '保科正之', '大塩格之助']
found = []
for o in officers:
    name = o.get('name', '')
    for t in search_terms:
        if t in name:
            found.append(o)
            break

for o in found:
    print(f"  {o.get('id')}: {o.get('name')} (birth:{o.get('birth')}, death:{o.get('death')}, clan:{o.get('clanId')}, prov:{o.get('provinceId', o.get('location'))}) [統:{o.get('leadership')}, 武:{o.get('valor')}, 知:{o.get('intelligence')}, 政:{o.get('politics')}]")
