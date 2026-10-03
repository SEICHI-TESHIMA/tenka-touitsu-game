import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. OFFICERS_MASTER
idx_off = text.find('window.OFFICERS_MASTER = [')
end_off = text.find('];', idx_off)
officers = json.loads(text[idx_off + len('window.OFFICERS_MASTER = '): end_off + 1])
existing_ids = set(o['id'] for o in officers)

medieval_officers = [
    # 1156
    {
        "id": "off_ata_tadakage",
        "name": "阿多忠景",
        "clanId": "minamoto_tametomo",
        "defaultProv": "satsuma",
        "military": 72, "politic": 64, "intel": 66,
        "era": "ancient",
        "skill": "薩摩豪族",
        "lore": "薩摩国の有力豪族。源為朝の九州進出に同調し、保元の乱の前後で南九州に勢威を振るった。",
        "birthYear": 1115, "deathYear": 1175, "isDaimyo": False
    },
    {
        "id": "off_fujiwara_motohira",
        "name": "藤原基衡",
        "clanId": "fujiwara_hiraizumi",
        "defaultProv": "tsugaru",
        "military": 70, "politic": 85, "intel": 82,
        "era": "ancient",
        "skill": "毛越寺建立",
        "lore": "奥州藤原氏第2代当主。清衡の次男。毛越寺を建立し、北東北一帯を統括して平泉文化の基礎を築いた。",
        "birthYear": 1105, "deathYear": 1157, "isDaimyo": False
    },
    # 1221
    {
        "id": "off_ooe_chikahiro",
        "name": "大江親広",
        "clanId": "gotoba_in",
        "defaultProv": "awaji",
        "military": 74, "politic": 82, "intel": 80,
        "era": "ancient",
        "skill": "院宣奉行",
        "lore": "大江広元の長男。京都守護・院判官代。承久の乱では父と袂を分かち後鳥羽上皇方として挙兵した。",
        "birthYear": 1180, "deathYear": 1242, "isDaimyo": False
    },
    {
        "id": "off_sasaki_munetsuna",
        "name": "佐々木宗綱",
        "clanId": "gotoba_in",
        "defaultProv": "oki",
        "military": 71, "politic": 70, "intel": 68,
        "era": "ancient",
        "skill": "隠岐守護",
        "lore": "近江源氏佐々木一族。承久の乱に際し山陰・隠岐方面の抑えとして配備された。",
        "birthYear": 1190, "deathYear": 1250, "isDaimyo": False
    },
    # 1438
    {
        "id": "off_ouchi_sugi_shigeaki",
        "name": "杉重明",
        "clanId": "ouchi",
        "defaultProv": "chikuzen",
        "military": 75, "politic": 72, "intel": 70,
        "era": "sengoku",
        "skill": "筑前守護代",
        "lore": "大内家重臣。大内持世の命を受けて筑前守護代を務め、少弐氏との戦いを主導した。",
        "birthYear": 1400, "deathYear": 1455, "isDaimyo": False
    },
    {
        "id": "off_hosokawa_mochiharu",
        "name": "細川持春",
        "clanId": "hosokawa",
        "defaultProv": "awaji",
        "military": 68, "politic": 76, "intel": 74,
        "era": "sengoku",
        "skill": "淡路守護",
        "lore": "室町中期の武将。細川持之の弟。淡路分郡守護として紀淡海峡の警固と海運を掌握した。",
        "birthYear": 1400, "deathYear": 1466, "isDaimyo": False
    },
    # 1467
    {
        "id": "off_ouchi_toida_hirotane",
        "name": "問田弘胤",
        "clanId": "ouchi",
        "defaultProv": "buzen",
        "military": 76, "politic": 74, "intel": 73,
        "era": "sengoku",
        "skill": "豊前守護代",
        "lore": "大内家重臣。問田氏当主。応仁の乱では大内政弘の上洛に従軍し、豊前・西国の守備を固めた。",
        "birthYear": 1435, "deathYear": 1492, "isDaimyo": False
    },
    {
        "id": "off_ouchi_aso_ieshige",
        "name": "麻生家重",
        "clanId": "ouchi",
        "defaultProv": "chikuzen",
        "military": 73, "politic": 69, "intel": 68,
        "era": "sengoku",
        "skill": "遠賀郡司",
        "lore": "筑前遠賀郡の有力領主・麻生氏当主。大内方として筑前防衛と博多警護にあたった。",
        "birthYear": 1420, "deathYear": 1480, "isDaimyo": False
    },
    {
        "id": "off_otomo_kamachi_akihisa",
        "name": "蒲池鑑久",
        "clanId": "otomo",
        "defaultProv": "chikugo",
        "military": 75, "politic": 72, "intel": 71,
        "era": "sengoku",
        "skill": "筑後旗頭",
        "lore": "筑後柳川城主・蒲池氏当主。大友親繁に従い筑後守護代として筑後国人を統括した。",
        "birthYear": 1430, "deathYear": 1490, "isDaimyo": False
    },
    {
        "id": "off_nanbu_namioka_akiyasu",
        "name": "浪岡顕保",
        "clanId": "nanbu",
        "defaultProv": "tsugaru",
        "military": 72, "politic": 78, "intel": 75,
        "era": "sengoku",
        "skill": "浪岡御所",
        "lore": "津軽浪岡城主。北畠氏の流れを汲み、南部氏と同盟関係を結んで津軽平野を支配した。",
        "birthYear": 1435, "deathYear": 1504, "isDaimyo": False
    },
    {
        "id": "off_hosokawa_shigeharu",
        "name": "細川成春",
        "clanId": "hosokawa",
        "defaultProv": "awaji",
        "military": 70, "politic": 75, "intel": 73,
        "era": "sengoku",
        "skill": "淡路守護代",
        "lore": "細川持春の子。淡路守護。応仁の乱では東軍・細川勝元方に属し、四国・淡路の軍勢を率いた。",
        "birthYear": 1435, "deathYear": 1485, "isDaimyo": False
    },
    {
        "id": "off_kyogoku_oki_kiyomasa",
        "name": "隠岐清政",
        "clanId": "kyogoku",
        "defaultProv": "oki",
        "military": 69, "politic": 73, "intel": 71,
        "era": "sengoku",
        "skill": "隠岐守護代",
        "lore": "京極家家臣。隠岐守護代。出雲・隠岐の海上防衛と内政を支えた。",
        "birthYear": 1430, "deathYear": 1490, "isDaimyo": False
    }
]

added_count = 0
for off in medieval_officers:
    if off['id'] not in existing_ids:
        officers.append(off)
        existing_ids.add(off['id'])
        added_count += 1

print(f"Added {added_count} medieval officers.")

# Update OFFICERS_MASTER
new_off_json = json.dumps(officers, ensure_ascii=False, indent=2)
text = text[:idx_off + len('window.OFFICERS_MASTER = ')] + new_off_json + text[end_off + 1:]

# 2. Update SCENARIO_HISTORICAL_GOVERNORS
idx_gov = text.find('window.SCENARIO_HISTORICAL_GOVERNORS = {')
end_gov = text.find('};\n\n', idx_gov)
if end_gov == -1: end_gov = text.find('};', idx_gov)

gov_str = text[idx_gov + len('window.SCENARIO_HISTORICAL_GOVERNORS = '): end_gov + 1]
import re
cleaned_gov = re.sub(r'([a-zA-Z0-9_]+):', r'"\1":', gov_str)
hist_govs = json.loads(cleaned_gov)

# 1156
if '1156' not in hist_govs: hist_govs['1156'] = {}
hist_govs['1156']['iwami'] = 'off_taira_yorimori'
hist_govs['1156']['mimasaka'] = 'off_taira_tadanori'
hist_govs['1156']['bicchu'] = 'off_senoo_kaneyasu'
hist_govs['1156']['bingo'] = 'off_taira_norimori'
hist_govs['1156']['aki'] = 'off_taira_kiyomori'
hist_govs['1156']['suo'] = 'off_taira_tsunemori'
hist_govs['1156']['nagato'] = 'off_taira_tomomori'
hist_govs['1156']['tosa'] = 'off_namba_tsuneto'
hist_govs['1156']['hyuga'] = 'off_taira_munemori'
hist_govs['1156']['shima'] = 'off_taira_iesada'
hist_govs['1156']['awaji'] = 'off_sadamori_tokitada'
hist_govs['1156']['oki'] = 'off_taira_morikuni'
hist_govs['1156']['satsuma'] = 'off_ata_tadakage'
hist_govs['1156']['tsugaru'] = 'off_fujiwara_motohira'

# 1221
if '1221' not in hist_govs: hist_govs['1221'] = {}
hist_govs['1221']['awaji'] = 'off_ooe_chikahiro'
hist_govs['1221']['oki'] = 'off_sasaki_munetsuna'

# 1438
if '1438' not in hist_govs: hist_govs['1438'] = {}
hist_govs['1438']['chikuzen'] = 'off_ouchi_sugi_shigeaki'
hist_govs['1438']['awaji'] = 'off_hosokawa_mochiharu'

# 1467
if '1467' not in hist_govs: hist_govs['1467'] = {}
hist_govs['1467']['buzen'] = 'off_ouchi_toida_hirotane'
hist_govs['1467']['chikuzen'] = 'off_ouchi_aso_ieshige'
hist_govs['1467']['chikugo'] = 'off_otomo_kamachi_akihisa'
hist_govs['1467']['tsugaru'] = 'off_nanbu_namioka_akiyasu'
hist_govs['1467']['awaji'] = 'off_hosokawa_shigeharu'
hist_govs['1467']['oki'] = 'off_kyogoku_oki_kiyomasa'

new_gov_json = json.dumps(hist_govs, ensure_ascii=False, indent=2)
text = text[:idx_gov + len('window.SCENARIO_HISTORICAL_GOVERNORS = ')] + new_gov_json + text[end_gov + 1:]

with open('js/data.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Successfully updated 1156, 1221, 1438, 1467 governors in js/data.js!")
