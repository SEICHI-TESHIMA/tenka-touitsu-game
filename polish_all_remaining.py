# -*- coding: utf-8 -*-
"""
Polish all remaining governor gaps across ancient, medieval and late scenarios.
"""

import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Helper to slice sections
provs_str = text[text.find('window.PROVINCES_DATA =') + len('window.PROVINCES_DATA ='):text.find('window.OFFICERS_MASTER =')].strip().rstrip(';')
officers_str = text[text.find('window.OFFICERS_MASTER =') + len('window.OFFICERS_MASTER ='):text.find('window.SCENARIOS_DATA =')].strip().rstrip(';')
scenarios_str = text[text.find('window.SCENARIOS_DATA =') + len('window.SCENARIOS_DATA ='):text.find('window.CLAN_MASTER_DATA =')].strip().rstrip(';')
clans_str = text[text.find('window.CLAN_MASTER_DATA =') + len('window.CLAN_MASTER_DATA ='):text.find('window.CLAN_ABILITIES =')].strip().rstrip(';')
clan_ab_str = text[text.find('window.CLAN_ABILITIES =') + len('window.CLAN_ABILITIES ='):text.find('window.HISTORICAL_EVENTS_DATA =')].strip().rstrip(';')
events_str = text[text.find('window.HISTORICAL_EVENTS_DATA =') + len('window.HISTORICAL_EVENTS_DATA ='):text.find('window.HISTORICAL_CASTLE_CHANGES =')].strip().rstrip(';')
castle_str = text[text.find('window.HISTORICAL_CASTLE_CHANGES =') + len('window.HISTORICAL_CASTLE_CHANGES ='):text.find('window.DAIMYO_LIFESPAN_DATA =')].strip().rstrip(';')

s_idx = text.find('window.DAIMYO_LIFESPAN_DATA =') + len('window.DAIMYO_LIFESPAN_DATA =')
e_idx = text.find('window.SCENARIO_HISTORICAL_GOVERNORS =')
lifespan_str = text[s_idx:e_idx].strip()
last_b = lifespan_str.rfind('}')
lifespan_str = lifespan_str[:last_b+1]

hist_govs_str = text[text.find('window.SCENARIO_HISTORICAL_GOVERNORS =') + len('window.SCENARIO_HISTORICAL_GOVERNORS ='):text.find('window.CLAN_CAPITAL_PROVINCES =')].strip().rstrip(';')
capitals_str = text[text.find('window.CLAN_CAPITAL_PROVINCES =') + len('window.CLAN_CAPITAL_PROVINCES ='):].strip().rstrip(';')

officers = json.loads(officers_str)
scenarios = json.loads(scenarios_str)
clans = json.loads(clans_str)
events = json.loads(events_str)
hist_govs = json.loads(hist_govs_str)
capitals = json.loads(capitals_str)

# Ensure Uesugi capital in 1582 is echigo (Kasugayama Castle)
capitals['uesugi'] = 'echigo'

# Extra officers for Hojo, Nanbu, Shiba, Hatakeyama, etc.
EXTRA_MEDIEVAL = [
    # 後北条
    {"id": "off_hojo_ujiteru", "name": "北条氏照", "clanId": "hojo", "defaultProv": "shimousa",
     "military": 88, "politic": 82, "intel": 85, "era": "sengoku", "skill": "八王子城の勇将",
     "lore": "北条氏康の三男。武蔵八王子城主。外交・軍事の両面で後北条家を支えた屈指の猛将。小田原開城時に切腹した。",
     "birthYear": 1540, "deathYear": 1590, "isDaimyo": False},
    {"id": "off_hojo_ujikuni", "name": "北条氏邦", "clanId": "hojo", "defaultProv": "kazusa",
     "military": 86, "politic": 80, "intel": 82, "era": "sengoku", "skill": "鉢形城主の武威",
     "lore": "北条氏康の四男。武蔵鉢形城主。神流川の戦いで滝川一益を破る大功を挙げた剛将。",
     "birthYear": 1541, "deathYear": 1597, "isDaimyo": False},

    # 鎌倉・室町守護・国司
    {"id": "off_shiba_yoshitake", "name": "斯波義健", "clanId": "shiba", "defaultProv": "totomi",
     "military": 80, "politic": 82, "intel": 78, "era": "nanboku", "skill": "斯波宗家",
     "lore": "室町幕府管領・斯波氏当主。越前・尾張・遠江守護職を務めた。",
     "birthYear": 1435, "deathYear": 1452, "isDaimyo": False},
    {"id": "off_hatakeyama_masanaga", "name": "畠山政長", "clanId": "hatakeyama", "defaultProv": "kii",
     "military": 86, "politic": 88, "intel": 86, "era": "sengoku", "skill": "管領政長",
     "lore": "室町幕府管領。応仁の乱東軍主将。河内・紀伊守護。正覚寺合戦で自刃した。",
     "birthYear": 1442, "deathYear": 1493, "isDaimyo": True},
    {"id": "off_ashina_moriuji_anc", "name": "蘆名盛信", "clanId": "ashina", "defaultProv": "iwaki",
     "military": 82, "politic": 80, "intel": 78, "era": "nanboku", "skill": "黒川城の守護",
     "lore": "蘆名氏当主。会津黒川城を拠点に陸奥南部の領国支配を固めた。",
     "birthYear": 1345, "deathYear": 1400, "isDaimyo": False},
    {"id": "off_ando_morisue", "name": "安東盛季", "clanId": "ando", "defaultProv": "ezo",
     "military": 82, "politic": 80, "intel": 82, "era": "nanboku", "skill": "津軽安東氏",
     "lore": "津軽十三湊の豪族。南部氏との戦いに敗れ蝦夷へ渡り松前・渡島半島の基礎を築いた。",
     "birthYear": 1400, "deathYear": 1460, "isDaimyo": False},
    {"id": "off_kushitsuno_naganori", "name": "楠木正勝", "clanId": "kusunoki", "defaultProv": "yamato",
     "military": 84, "politic": 78, "intel": 80, "era": "nanboku", "skill": "南朝の勇士",
     "lore": "楠木正儀の長男。父と共に南朝方として紀伊・大和で奮戦した。",
     "birthYear": 1355, "deathYear": 1405, "isDaimyo": False},
    {"id": "off_kitabatake_akiyoshi", "name": "北畠顕能", "clanId": "kitabatake", "defaultProv": "yamato",
     "military": 84, "politic": 85, "intel": 82, "era": "nanboku", "skill": "伊勢国司の武威",
     "lore": "北畠親房の三男。伊勢国司。南朝の重鎮として大和・伊勢を固め足利軍と戦い抜いた。",
     "birthYear": 1326, "deathYear": 1383, "isDaimyo": False},
    {"id": "off_kitabatake_akinobu", "name": "北畠顕信", "clanId": "kitabatake", "defaultProv": "mutsu",
     "military": 85, "politic": 84, "intel": 85, "era": "nanboku", "skill": "鎮守府将軍",
     "lore": "親房の次男。顕家の弟。陸奥国府や多賀城を拠点に奥羽の南朝軍を率いて戦った。",
     "birthYear": 1317, "deathYear": 1380, "isDaimyo": False}
]

existing_ids = {o['id'] for o in officers}
existing_names = {o['name'] for o in officers}
for eo in EXTRA_MEDIEVAL:
    if eo['id'] not in existing_ids and eo['name'] not in existing_names:
        officers.append(eo)
        existing_ids.add(eo['id'])
        existing_names.add(eo['name'])

fill_extra = {
    # 1582, 1590
    ('1582', 'etchu'): 'off_maeda_toshiie',
    ('1590', 'shimousa'): 'off_hojo_ujiteru',
    ('1590', 'kazusa'): 'off_hojo_ujikuni',

    # 1331, 1333, 1336, 1350
    ('1331', 'mutsu'): 'off_kitabatake_akinobu',
    ('1331', 'tsugaru'): 'off_kitabatake_akinobu',
    ('1331', 'iwaki'): 'off_ashina_moriuji_anc',
    ('1331', 'owari'): 'off_ashikaga_takauji',
    ('1331', 'kazusa'): 'off_uesugi_noriaki',
    ('1331', 'etchu'): 'off_shiba_takatsune',
    ('1331', 'hida'): 'off_toki_yorisada',
    ('1331', 'tango'): 'off_isshiki_norouji',
    ('1331', 'wakasa'): 'off_sasakidoyo',
    ('1331', 'bicchu'): 'off_akamatsu_sadanori',
    ('1331', 'bingo'): 'off_hosokawa_yoriharu',
    ('1331', 'nagato'): 'off_ouchi_hiroyo',
    ('1333', 'tsugaru'): 'off_kitabatake_akinobu',
    ('1333', 'bingo'): 'off_hosokawa_yoriharu',
    ('1333', 'izu'): 'off_uesugi_noriaki',
    ('1333', 'uzen'): 'off_shiba_takatsune',
    ('1336', 'iwaki'): 'off_ashina_moriuji_anc',
    ('1336', 'etchu'): 'off_shiba_takatsune',
    ('1336', 'mikawa'): 'off_ashikaga_takauji',
    ('1336', 'shima'): 'off_kitabatake_akiyoshi',
    ('1336', 'yamato'): 'off_kitabatake_akiyoshi',
    ('1336', 'tsugaru'): 'off_kitabatake_akinobu',
    ('1336', 'iwami'): 'off_yamana_tokiuji',
    ('1336', 'bicchu'): 'off_akamatsu_sadanori',
    ('1336', 'bingo'): 'off_hosokawa_yoriharu',
    ('1336', 'chikuzen'): 'off_shoni_yorihisa',
    ('1336', 'chikugo'): 'off_kikuchi_takemitsu',
    ('1336', 'hyuga'): 'off_shimazu_sadahisa',
    ('1350', 'mutsu'): 'off_kitabatake_akinobu',
    ('1350', 'tsugaru'): 'off_ando_morisue',
    ('1350', 'iwaki'): 'off_ashina_moriuji_anc',
    ('1350', 'wakasa'): 'off_shiba_takatsune',

    # 1438, 1467, 1495
    ('1438', 'ezo'): 'off_ando_morisue',
    ('1438', 'iwaki'): 'off_ashina_moriuji_anc',
    ('1438', 'etchu'): 'off_hatakeyama_mochikuni',
    ('1438', 'kii'): 'off_hatakeyama_masanaga',
    ('1438', 'wakasa'): 'off_isshiki_yoshinori',
    ('1438', 'mikawa'): 'off_isshiki_yoshinori',
    ('1438', 'iga'): 'off_niki_yoriaki',
    ('1438', 'tamba'): 'off_hosokawa_katsumoto',
    ('1438', 'totomi'): 'off_shiba_yoshitake',
    ('1438', 'shima'): 'off_kitabatake_akiyoshi',
    ('1438', 'izumi'): 'off_hosokawa_katsumoto',
    ('1438', 'bicchu'): 'off_hosokawa_shigeyuki',
    ('1438', 'bingo'): 'off_yamana_koretoyo',
    ('1438', 'izumo'): 'off_kyogoku_mochikiyo',
    ('1438', 'oki'): 'off_kyogoku_mochikiyo',
    ('1438', 'aki'): 'off_takeda_nobukata' if 'off_takeda_nobukata' in existing_ids else 'off_takeda_nobumitsu',
    ('1438', 'chikugo'): 'off_otomo_chikashige' if 'off_otomo_chikashige' in existing_ids else 'off_otomo_sorin',
    ('1467', 'ezo'): 'off_ando_morisue',
    ('1467', 'iwaki'): 'off_ashina_moriuji_anc',
    ('1467', 'wakasa'): 'off_isshiki_yoshinori',
    ('1467', 'iga'): 'off_niki_yoriaki',
    ('1467', 'kazusa'): 'off_chiba_tanenao' if 'off_chiba_tanenao' in existing_ids else 'off_hojo_ujikuni',
    ('1467', 'awa_boshu'): 'off_chiba_tanenao' if 'off_chiba_tanenao' in existing_ids else 'off_hojo_ujikuni',
    ('1467', 'izu'): 'off_uesugi_norizane' if 'off_uesugi_norizane' in existing_ids else 'off_uesugi_noriaki',
    ('1467', 'shima'): 'off_kitabatake_akiyoshi',
    ('1467', 'izumo'): 'off_kyogoku_mochikiyo',
    ('1467', 'oki'): 'off_kyogoku_mochikiyo',
    ('1467', 'bicchu'): 'off_hosokawa_shigeyuki',
    ('1467', 'bingo'): 'off_yamana_koretoyo',
    ('1467', 'chikugo'): 'off_otomo_sorin',
    ('1495', 'iwaki'): 'off_ashina_moriuji_anc',
    ('1495', 'kazusa'): 'off_hojo_ujikuni',
    ('1495', 'awa_boshu'): 'off_hojo_ujikuni',
    ('1495', 'hida'): 'off_saito_dosan_anc' if 'off_saito_dosan_anc' in existing_ids else 'off_toki_yorito',
    ('1495', 'totomi'): 'off_imagawa_ujichika',
    ('1495', 'shima'): 'off_kitabatake_akiyoshi',
    ('1495', 'iga'): 'off_rokkaku_sadayori',
    ('1495', 'yamashiro'): 'off_hosokawa_masamoto',
    ('1495', 'izumi'): 'off_hosokawa_masamoto',
    ('1495', 'inaba'): 'off_yamana_suketoyo',
    ('1495', 'mimasaka'): 'off_uragami_norimune',
    ('1495', 'bicchu'): 'off_amago_tsunehisa',
    ('1495', 'bingo'): 'off_amago_tsunehisa',
    ('1495', 'oki'): 'off_amago_tsunehisa',
    ('1495', 'chikugo'): 'off_otomo_sorin'
}

for (sid, prov), oid in fill_extra.items():
    if sid not in hist_govs:
        hist_govs[sid] = {}
    hist_govs[sid][prov] = oid

print(f"Applied {len(fill_extra)} extra medieval and Sengoku governor fills.")

# Save back to data.js cleanly
new_data_content = f"""// 統一 - データベース定義 (Provinces, Officers, Scenarios, Clans)

window.PROVINCES_DATA = {json.dumps(json.loads(provs_str), ensure_ascii=False, indent=2)};

window.OFFICERS_MASTER = {json.dumps(officers, ensure_ascii=False, indent=2)};

window.SCENARIOS_DATA = {json.dumps(scenarios, ensure_ascii=False, indent=2)};

window.CLAN_MASTER_DATA = {json.dumps(clans, ensure_ascii=False, indent=2)};

window.CLAN_ABILITIES = {json.dumps(json.loads(clan_ab_str), ensure_ascii=False, indent=2)};

window.HISTORICAL_EVENTS_DATA = {json.dumps(events, ensure_ascii=False, indent=2)};

window.HISTORICAL_CASTLE_CHANGES = {json.dumps(json.loads(castle_str), ensure_ascii=False, indent=2)};

window.DAIMYO_LIFESPAN_DATA = {json.dumps(json.loads(lifespan_str), ensure_ascii=False, indent=2)};

window.SCENARIO_HISTORICAL_GOVERNORS = {json.dumps(hist_govs, ensure_ascii=False, indent=2)};

window.CLAN_CAPITAL_PROVINCES = {json.dumps(capitals, ensure_ascii=False, indent=2)};
"""

with open('js/data.js', 'w', encoding='utf-8') as f:
    f.write(new_data_content)

print(f"Saved completed data.js! Total Officers={len(officers)}")
