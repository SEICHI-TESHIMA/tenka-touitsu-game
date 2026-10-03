import json
import re

with open('js/data.js', 'r', encoding='utf-8') as f:
    data_text = f.read()

start_idx = data_text.find('window.OFFICERS_MASTER = [')
end_idx = data_text.find('\n];', start_idx) + 2
officers_master = json.loads(data_text[start_idx + len('window.OFFICERS_MASTER = '):end_idx])

start_idx = data_text.find('window.SCENARIOS_DATA = [')
end_idx = data_text.find('\n];', start_idx) + 2
scenarios = json.loads(data_text[start_idx + len('window.SCENARIOS_DATA = '):end_idx])

scen = [s for s in scenarios if str(s['id']) == '1866'][0]
year = scen['year']
owners_set = set(scen.get('owners', {}).values())

alive = []
for m in officers_master:
    by = m.get('birthYear')
    dy = m.get('deathYear')
    if by is not None and dy is not None:
        age = year - by
        if age >= 15 and year <= dy:
            o = dict(m)
            o['isDaimyo'] = False
            o['isDead'] = False
            alive.append(o)

for off in alive:
    if 'meiji' not in owners_set:
        satsumaMembers = ['西郷隆盛', '大久保利通', '小松帯刀', '黒田清隆', '桐野利秋', '大山巌', '伊地知正治']
        if off['name'] in satsumaMembers:
            if 'shimazu' in owners_set:
                off['clanId'] = 'shimazu'
                continue
        choshuMembers = ['木戸孝允', '桂小五郎', '高杉晋作', '大村益次郎', '伊藤博文', '井上馨', '山田顕義', '山縣有朋', '品川弥二郎', '世良修蔵']
        if off['name'] in choshuMembers:
            if 'mori' in owners_set:
                off['clanId'] = 'mori'
                continue
        tosaMembers = ['坂本龍馬', '中岡慎太郎', '板垣退助', '後藤象二郎']
        if off['name'] in tosaMembers:
            if 'tosa' in owners_set:
                off['clanId'] = 'tosa'
                continue
        shonaiMembers = ['酒井吉之丞', '伴百悦']
        if off['name'] in shonaiMembers:
            if 'shonai' in owners_set:
                off['clanId'] = 'shonai'
                continue
            if 'tokugawa' in owners_set:
                off['clanId'] = 'tokugawa'
                continue
        if off['name'] == '立見鑑三郎':
            if 'kuwana' in owners_set:
                off['clanId'] = 'kuwana'
                continue
            if 'tokugawa' in owners_set:
                off['clanId'] = 'tokugawa'
                continue
        if off['name'] == '河井継之助':
            if 'makino' in owners_set:
                off['clanId'] = 'makino'
                continue
            if 'tokugawa' in owners_set:
                off['clanId'] = 'tokugawa'
                continue

    exactName = lambda names: off['name'] in names
    stillUnplaced = not off.get('clanId') or off['clanId'] in ['ronin', 'goryokaku', 'shogunate', 'tokugawa'] or off['clanId'] not in owners_set
    ezoNames = ['榎本武揚', '大鳥圭介', '土方歳三', '人見勝太郎', '中島登', '春日左衛門', '島田魁']
    shinsengumiNames = ['近藤勇', '土方歳三', '沖田総司', '斎藤一', '永倉新八', '中島登', '島田魁']
    bakufuNames = ['榎本武揚', '大鳥圭介', '人見勝太郎', '春日左衛門']

    if exactName(ezoNames) and 'goryokaku' in owners_set and stillUnplaced:
        off['clanId'] = 'goryokaku'
        continue
    if exactName(shinsengumiNames) and year < 1863 and 'goryokaku' not in owners_set and stillUnplaced:
        off['clanId'] = 'ronin'
        continue
    if (exactName(bakufuNames) or (exactName(shinsengumiNames) and year >= 1863)) and stillUnplaced and 'tokugawa' in owners_set:
        off['clanId'] = 'tokugawa'
        continue

    clanAlias = {
        'kuroda': 'fukuoka_kuroda', 'fukuoka_kuroda': 'kuroda',
        'hosokawa': 'kumamoto_hosokawa', 'kumamoto_hosokawa': 'hosokawa',
        'shogunate': 'tokugawa', 'shonai': 'tokugawa', 'kuwana': 'tokugawa', 'makino': 'tokugawa', 'ii': 'meiji'
    }
    aliased = clanAlias.get(off['clanId'])
    if aliased and aliased in owners_set:
        off['clanId'] = aliased
        continue

    if off['clanId'] not in owners_set:
        if off.get('id') == 'off_dm_meiji_1868':
            continue
        off['clanId'] = 'ronin'

ronins_1866 = [o for o in alive if o['clanId'] == 'ronin']
out = []
out.append(f"=== ACTUAL RONIN IN 1866: {len(ronins_1866)} ===")
for r in ronins_1866:
    out.append(f"  {r['id']:<26} | {r['name']:<12} | defProv:{r.get('defaultProv'):<14} | masterClan:{r.get('clanId')}")

with open('actual_ronin_1866_utf8.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(out))
print("Saved actual_ronin_1866_utf8.txt")
