import json
import re

# Load data.js
with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Parse officers
idx = text.find('window.OFFICERS_MASTER = [')
end_idx = text.find('];', idx)
officers = json.loads(text[idx + len('window.OFFICERS_MASTER = '): end_idx + 1])

# Parse scenarios
idx_scen = text.find('window.SCENARIOS = [')
end_scen = text.find('];', idx_scen)
# Scenarios might have comments or js objects, let's parse safely or extract 1866
scen_text = text[idx_scen + len('window.SCENARIOS = '): end_scen + 1]

# Let's extract scenario 1866 province owners
# Find id: '1866'
p_1866 = re.search(r'id:\s*[\'"]1866[\'"].*?provinces:\s*(\{.*?\})', text, re.DOTALL)
if p_1866:
    prov_str = p_1866.group(1)
    # convert js object to json (quote keys)
    prov_json_str = re.sub(r'([a-zA-Z0-9_]+):', r'"\1":', prov_str)
    prov_1866 = json.loads(prov_json_str)
    print(f"Scenario 1866 has {len(prov_1866)} provinces defined.")
    owners_1866 = set(prov_1866.values())
    print("Owners in 1866:", sorted(list(owners_1866)))
else:
    print("Could not parse 1866 provinces")
    prov_1866 = {}
    owners_1866 = set()

# Check active officers in 1866
alive_1866 = [o for o in officers if (o.get('birthYear', 9999) <= 1866 <= o.get('deathYear', -9999))]
print(f"\nAlive officers in 1866: {len(alive_1866)}")

# Simulate affiliations logic
ronin_list = []
assigned = {}
for o in alive_1866:
    clan = o.get('clanId')
    name = o.get('name')
    oid = o.get('id')
    prov = o.get('defaultProv')
    
    # Check if clan in owners_1866
    if clan in owners_1866:
        assigned[oid] = (clan, 'in owners')
    elif clan == 'matsudaira' and 'tokugawa' in owners_1866:
        assigned[oid] = ('tokugawa', 'matsudaira -> tokugawa')
    elif clan == 'shogunate' and 'tokugawa' in owners_1866:
        assigned[oid] = ('tokugawa', 'shogunate -> tokugawa')
    elif clan == 'shonai' and 'tokugawa' in owners_1866:
        assigned[oid] = ('tokugawa', 'shonai -> tokugawa')
    elif clan == 'kuwana' and 'tokugawa' in owners_1866:
        assigned[oid] = ('tokugawa', 'kuwana -> tokugawa')
    elif clan == 'makino' and 'tokugawa' in owners_1866:
        assigned[oid] = ('tokugawa', 'makino -> tokugawa')
    elif clan == 'fukuoka_kuroda' and 'kuroda' in owners_1866:
        assigned[oid] = ('kuroda', 'alias')
    elif clan == 'kumamoto_hosokawa' and 'hosokawa' in owners_1866:
        assigned[oid] = ('hosokawa', 'alias')
    else:
        # Check special rules in app.js
        satsumaMembers = ['西郷隆盛', '大久保利通', '小松帯刀', '黒田清隆', '桐野利秋', '大山巌', '伊地知正治']
        choshuMembers = ['木戸孝允', '桂小五郎', '高杉晋作', '大村益次郎', '伊藤博文', '井上馨', '山田顕義', '山縣有朋', '品川弥二郎', '世良修蔵']
        tosaMembers = ['坂本龍馬', '中岡慎太郎', '板垣退助', '後藤象二郎']
        bakufuNames = ['榎本武揚', '大鳥圭介', '人見勝太郎', '春日左衛門']
        shinsengumiNames = ['近藤勇', '土方歳三', '沖田総司', '斎藤一', '永倉新八', '中島登', '島田魁']
        
        if name in satsumaMembers and 'shimazu' in owners_1866:
            assigned[oid] = ('shimazu', 'satsuma member')
        elif name in choshuMembers and 'mori' in owners_1866:
            assigned[oid] = ('mori', 'choshu member')
        elif name in tosaMembers and 'tosa' in owners_1866:
            assigned[oid] = ('tosa', 'tosa member')
        elif (name in bakufuNames or name in shinsengumiNames) and 'tokugawa' in owners_1866:
            assigned[oid] = ('tokugawa', 'bakufu/shinsengumi')
        elif name == '立見鑑三郎' and 'tokugawa' in owners_1866:
            assigned[oid] = ('tokugawa', 'kuwana')
        elif name == '河井継之助' and 'tokugawa' in owners_1866:
            assigned[oid] = ('tokugawa', 'makino')
        else:
            ronin_list.append(o)

print(f"\nResulting Ronin count in 1866: {len(ronin_list)}")
for r in ronin_list:
    print(f"  RONIN: {r['id']:<30} {r['name']:<15} origClan:{r.get('clanId',''):<15} prov:{r.get('defaultProv')}")
