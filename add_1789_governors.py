import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Parse OFFICERS_MASTER
idx_off = text.find('window.OFFICERS_MASTER = [')
end_off = text.find('];', idx_off)
officers = json.loads(text[idx_off + len('window.OFFICERS_MASTER = '): end_off + 1])
existing_ids = set(o['id'] for o in officers)

# Officers for 1789 (Kansei era)
kansei_officers = [
    {
        "id": "off_edo_ota_sukeyoshi",
        "name": "太田資愛",
        "clanId": "tokugawa",
        "defaultProv": "settsu",
        "military": 68, "politic": 85, "intel": 82,
        "era": "edo",
        "skill": "大坂城代",
        "lore": "遠江掛川藩主。大坂城代を経て老中首座となり、松平定信失脚後の幕政を主導した。",
        "birthYear": 1745, "deathYear": 1805, "isDaimyo": False
    },
    {
        "id": "off_edo_okabe_nagakuni",
        "name": "岡部長邦",
        "clanId": "tokugawa",
        "defaultProv": "izumi",
        "military": 62, "politic": 75, "intel": 70,
        "era": "edo",
        "skill": "和泉守護",
        "lore": "和泉岸和田藩第8代藩主。藩政改革と海防の強化に尽力した譜代大名。",
        "birthYear": 1763, "deathYear": 1818, "isDaimyo": False
    },
    {
        "id": "off_edo_aoyama_tadahiro",
        "name": "青山忠裕",
        "clanId": "tokugawa",
        "defaultProv": "tamba",
        "military": 65, "politic": 88, "intel": 83,
        "era": "edo",
        "skill": "老中首座",
        "lore": "丹波篠山藩主。寺社奉行、大坂城代を経て老中首座を20年以上務めた幕閣の重鎮。",
        "birthYear": 1768, "deathYear": 1836, "isDaimyo": False
    },
    {
        "id": "off_edo_matsudaira_suketsugu",
        "name": "松平資承",
        "clanId": "tokugawa",
        "defaultProv": "tango",
        "military": 60, "politic": 78, "intel": 76,
        "era": "edo",
        "skill": "丹後宮津",
        "lore": "丹後宮津藩第3代藩主。寺社奉行、若年寄を務め、寛政の改革を支えた。",
        "birthYear": 1749, "deathYear": 1800, "isDaimyo": False
    },
    {
        "id": "off_edo_sengoku_hisayuki",
        "name": "仙石久行",
        "clanId": "tokugawa",
        "defaultProv": "tajima",
        "military": 64, "politic": 74, "intel": 72,
        "era": "edo",
        "skill": "但馬出石",
        "lore": "但馬出石藩第4代藩主。仙石権兵衛秀久の子孫。藩財政の再建と文教政策を推進。",
        "birthYear": 1753, "deathYear": 1817, "isDaimyo": False
    },
    {
        "id": "off_edo_matsudaira_yasusada",
        "name": "松平康定",
        "clanId": "tokugawa",
        "defaultProv": "iwami",
        "military": 66, "politic": 84, "intel": 80,
        "era": "edo",
        "skill": "石見浜田",
        "lore": "石見浜田藩主。老中。松平定信の寛政の改革に参画し幕政の引き締めを行った。",
        "birthYear": 1748, "deathYear": 1806, "isDaimyo": False
    },
    {
        "id": "off_edo_matsudaira_yasuchika",
        "name": "松平康哉",
        "clanId": "tokugawa",
        "defaultProv": "mimasaka",
        "military": 60, "politic": 82, "intel": 80,
        "era": "edo",
        "skill": "美作津山",
        "lore": "美作津山藩第5代藩主。越前松平家。民政に心を砕き名君として称えられた。",
        "birthYear": 1758, "deathYear": 1794, "isDaimyo": False
    },
    {
        "id": "off_edo_itakura_katsumasa",
        "name": "板倉勝政",
        "clanId": "tokugawa",
        "defaultProv": "bicchu",
        "military": 63, "politic": 79, "intel": 77,
        "era": "edo",
        "skill": "備中松山",
        "lore": "備中松山藩第4代藩主。板倉勝静の祖父。学問を奨励し藩校を開設した。",
        "birthYear": 1759, "deathYear": 1821, "isDaimyo": False
    },
    {
        "id": "off_edo_matsudaira_yorizane",
        "name": "松平頼真",
        "clanId": "tokugawa",
        "defaultProv": "sanuki",
        "military": 62, "politic": 76, "intel": 74,
        "era": "edo",
        "skill": "讃岐高松",
        "lore": "讃岐高松藩第6代藩主。水戸徳川家連枝。学問・武芸を重んじ、藩校講道館を振興した。",
        "birthYear": 1743, "deathYear": 1800, "isDaimyo": False
    },
    {
        "id": "off_edo_nakagawa_hisayoshi",
        "name": "中川久持",
        "clanId": "tokugawa",
        "defaultProv": "bungo",
        "military": 61, "politic": 74, "intel": 73,
        "era": "edo",
        "skill": "豊後岡城",
        "lore": "豊後岡藩第9代藩主。中川清秀の子孫。名城・岡城を維持し質素倹約を奨励。",
        "birthYear": 1776, "deathYear": 1798, "isDaimyo": False
    },
    {
        "id": "off_edo_matsudaira_harusato",
        "name": "松平治郷",
        "clanId": "tokugawa",
        "defaultProv": "oki",
        "military": 58, "politic": 92, "intel": 89,
        "era": "edo",
        "skill": "不昧流茶道",
        "lore": "出雲松江藩第7代藩主。号は不昧。大名茶人として名高いが、莫大な借金を返済し財政再建を成し遂げた名君。",
        "birthYear": 1751, "deathYear": 1818, "isDaimyo": False
    },
    {
        "id": "off_edo_inada_tanesuke",
        "name": "稲田植資",
        "clanId": "tokugawa",
        "defaultProv": "awaji",
        "military": 70, "politic": 76, "intel": 74,
        "era": "edo",
        "skill": "洲本城代",
        "lore": "淡路洲本城代・蜂須賀家筆頭家老。淡路一国を差配した実質的な淡路領主。",
        "birthYear": 1752, "deathYear": 1816, "isDaimyo": False
    },
    {
        "id": "off_edo_arao_narinao",
        "name": "荒尾成直",
        "clanId": "tottori",
        "defaultProv": "hoki",
        "military": 67, "politic": 78, "intel": 75,
        "era": "edo",
        "skill": "米子城代",
        "lore": "伯耆米子城代・鳥取藩筆頭家老。伯耆国一帯の支配と治安維持を管掌した。",
        "birthYear": 1750, "deathYear": 1813, "isDaimyo": False
    },
    {
        "id": "off_edo_ito_sukeyoshi_1789",
        "name": "伊東祐福",
        "clanId": "shimazu",
        "defaultProv": "hyuga",
        "military": 65, "politic": 77, "intel": 74,
        "era": "edo",
        "skill": "日向飫肥",
        "lore": "日向飫肥藩第10代藩主。杉林の植林事業（飫肥杉）を推進し藩財政を立て直した。",
        "birthYear": 1743, "deathYear": 1804, "isDaimyo": False
    },
    {
        "id": "off_edo_shimazu_tadahiro",
        "name": "島津忠厚",
        "clanId": "shimazu",
        "defaultProv": "osumi",
        "military": 68, "politic": 76, "intel": 75,
        "era": "edo",
        "skill": "加治木島津",
        "lore": "大隅加治木島津家第4代当主。薩摩藩主・島津重豪の補佐として藩政に重きをなした。",
        "birthYear": 1750, "deathYear": 1819, "isDaimyo": False
    }
]

added_count = 0
for off in kansei_officers:
    if off['id'] not in existing_ids:
        officers.append(off)
        existing_ids.add(off['id'])
        added_count += 1

print(f"Added {added_count} officers for Kansei era (1789).")

# Update window.OFFICERS_MASTER
new_off_json = json.dumps(officers, ensure_ascii=False, indent=2)
text = text[:idx_off + len('window.OFFICERS_MASTER = ')] + new_off_json + text[end_off + 1:]

# 2. Update SCENARIO_HISTORICAL_GOVERNORS for 1789
idx_gov = text.find('window.SCENARIO_HISTORICAL_GOVERNORS = {')
end_gov = text.find('};\n\n', idx_gov)
if end_gov == -1:
    end_gov = text.find('};', idx_gov)

gov_str = text[idx_gov + len('window.SCENARIO_HISTORICAL_GOVERNORS = '): end_gov + 1]
# clean regex for json
import re
cleaned_gov = re.sub(r'([a-zA-Z0-9_]+):', r'"\1":', gov_str)
hist_govs = json.loads(cleaned_gov)

if '1789' not in hist_govs:
    hist_govs['1789'] = {}

# Set the 15 empty provinces
hist_govs['1789']['settsu'] = 'off_edo_ota_sukeyoshi'
hist_govs['1789']['izumi'] = 'off_edo_okabe_nagakuni'
hist_govs['1789']['tamba'] = 'off_edo_aoyama_tadahiro'
hist_govs['1789']['tango'] = 'off_edo_matsudaira_suketsugu'
hist_govs['1789']['tajima'] = 'off_edo_sengoku_hisayuki'
hist_govs['1789']['iwami'] = 'off_edo_matsudaira_yasusada'
hist_govs['1789']['mimasaka'] = 'off_edo_matsudaira_yasuchika'
hist_govs['1789']['bicchu'] = 'off_edo_itakura_katsumasa'
hist_govs['1789']['sanuki'] = 'off_edo_matsudaira_yorizane'
hist_govs['1789']['bungo'] = 'off_edo_nakagawa_hisayoshi'
hist_govs['1789']['oki'] = 'off_edo_matsudaira_harusato'
hist_govs['1789']['awaji'] = 'off_edo_inada_tanesuke'
hist_govs['1789']['hoki'] = 'off_edo_arao_narinao'
hist_govs['1789']['hyuga'] = 'off_edo_ito_sukeyoshi_1789'
hist_govs['1789']['osumi'] = 'off_edo_shimazu_tadahiro'

new_gov_json = json.dumps(hist_govs, ensure_ascii=False, indent=2)
text = text[:idx_gov + len('window.SCENARIO_HISTORICAL_GOVERNORS = ')] + new_gov_json + text[end_gov + 1:]

with open('js/data.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Successfully updated js/data.js with 1789 governors!")
