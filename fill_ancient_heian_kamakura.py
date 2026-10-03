# -*- coding: utf-8 -*-
"""
Fill all remaining ancient, Heian, Kamakura, and Nanbokucho governor gaps.
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

ANCIENT_OFFICERS = [
    # 平安武将・名国司
    {"id": "off_minamoto_yorimitsu", "name": "源頼光", "clanId": "heian_court", "defaultProv": "settsu",
     "military": 94, "politic": 82, "intel": 85, "era": "ancient", "skill": "酒呑童子退治",
     "lore": "摂津源氏の祖。頼光四天王（渡辺綱・坂田金時ら）を率いて丹波大江山の酒呑童子を退治した武勇絶倫の英雄。伊予守・摂津守・美濃守を歴任。",
     "birthYear": 948, "deathYear": 1021, "isDaimyo": False},
    {"id": "off_watanabe_tsuna", "name": "渡辺綱", "clanId": "heian_court", "defaultProv": "settsu",
     "military": 92, "politic": 70, "intel": 78, "era": "ancient", "skill": "一条戻橋の鬼退治",
     "lore": "頼光四天王筆頭。一条戻橋で鬼の腕を名刀・髭切で切り落とした伝説の剛勇。摂津渡辺党の祖。",
     "birthYear": 953, "deathYear": 1025, "isDaimyo": False},
    {"id": "off_fujiwara_yasumasa", "name": "藤原保昌", "clanId": "heian_court", "defaultProv": "tamba",
     "military": 90, "politic": 80, "intel": 84, "era": "ancient", "skill": "盗賊袴垂討伐",
     "lore": "平安中期の武将。道長に仕えた武勇の士。大盗・袴垂を笛の音と気迫で圧倒した逸話で名高い。丹波守・大和守を歴任。",
     "birthYear": 958, "deathYear": 1036, "isDaimyo": False},
    {"id": "off_minamoto_yorichika", "name": "源頼親", "clanId": "heian_court", "defaultProv": "yamato",
     "military": 86, "politic": 78, "intel": 80, "era": "ancient", "skill": "大和源氏の祖",
     "lore": "頼光の弟。大和守。興福寺の僧兵と死闘を繰り広げ大和に強大な武士団を築いた大和源氏の祖。",
     "birthYear": 965, "deathYear": 1040, "isDaimyo": False},
    {"id": "off_oe_no_masahira", "name": "大江匡衡", "clanId": "heian_court", "defaultProv": "owari",
     "military": 65, "politic": 92, "intel": 95, "era": "ancient", "skill": "文道の泰斗",
     "lore": "平安中期の学者・官人。尾張守・丹後守を歴任。赤染衛門の夫。大江広元らの先祖。",
     "birthYear": 952, "deathYear": 1012, "isDaimyo": False},
    {"id": "off_fujiwara_motonao", "name": "藤原元命", "clanId": "heian_court", "defaultProv": "owari",
     "military": 68, "politic": 80, "intel": 78, "era": "ancient", "skill": "尾張守の徴税",
     "lore": "平安中期の受領。尾張守として『尾張国郡司百姓等解文』で訴えられたことで教科書に載る著名な受領。",
     "birthYear": 940, "deathYear": 1000, "isDaimyo": False},
    {"id": "off_taira_koremoto", "name": "平惟基", "clanId": "heian_court", "defaultProv": "buzen",
     "military": 82, "politic": 80, "intel": 78, "era": "ancient", "skill": "九州の大族",
     "lore": "大宰少弐・大隅守等を歴任。九州に土着し緒方氏や大神氏などの祖となった平安の有力武将。",
     "birthYear": 980, "deathYear": 1045, "isDaimyo": False}
]

existing_ids = {o['id'] for o in officers}
existing_names = {o['name'] for o in officers}
for ao in ANCIENT_OFFICERS:
    if ao['id'] not in existing_ids and ao['name'] not in existing_names:
        officers.append(ao)
        existing_ids.add(ao['id'])
        existing_names.add(ao['name'])

# Bulk fill for ancient & medieval court/gotoba lands
court_govs_common = {
    'musashi': 'off_minamoto_tsunemoto',
    'sagami': 'off_taira_naokata',
    'north_shinano': 'off_minamoto_yoshiie',
    'south_shinano': 'off_minamoto_yoshimitsu',
    'echigo': 'off_taira_sadamori',
    'etchu': 'off_taira_sadamori',
    'noto': 'off_fujiwara_yasumasa',
    'kaga': 'off_fujiwara_yasumasa',
    'echizen': 'off_minamoto_yorimitsu',
    'wakasa': 'off_minamoto_yorimitsu',
    'hida': 'off_minamoto_tsunemoto',
    'mino': 'off_minamoto_yorimitsu',
    'owari': 'off_oe_no_masahira',
    'mikawa': 'off_oe_no_masahira',
    'totomi': 'off_ki_no_tsurayuki',
    'suruga': 'off_ki_no_tsurayuki',
    'izu': 'off_taira_kimimasa',
    'north_omi': 'off_fujiwara_yasumasa',
    'south_omi': 'off_fujiwara_yasumasa',
    'shima': 'off_fujiwara_yasumasa',
    'iga': 'off_minamoto_yorimitsu',
    'yamato': 'off_minamoto_yorichika',
    'kawachi': 'off_minamoto_yorimitsu',
    'izumi': 'off_watanabe_tsuna',
    'settsu': 'off_watanabe_tsuna',
    'tamba': 'off_fujiwara_yasumasa',
    'tango': 'off_oe_no_masahira',
    'tajima': 'off_fujiwara_yasumasa',
    'harima': 'off_oe_no_masahira',
    'inaba': 'off_ki_no_yoshimitsu',
    'hoki': 'off_ki_no_yoshimitsu',
    'izumo': 'off_ki_no_yoshimitsu',
    'iwami': 'off_ki_no_yoshimitsu',
    'mimasaka': 'off_ki_no_yoshimitsu',
    'bizen': 'off_fujiwara_fuminori',
    'bicchu': 'off_fujiwara_fuminori',
    'bingo': 'off_fujiwara_fuminori',
    'aki': 'off_fujiwara_fuminori',
    'suo': 'off_fujiwara_fuminori',
    'nagato': 'off_fujiwara_fuminori',
    'sanuki': 'off_ki_no_fumiyoshi',
    'awa_shikoku': 'off_kuwahara_tomoharu',
    'iyo': 'off_ki_no_tsurayuki',
    'tosa': 'off_ki_no_tsurayuki',
    'kii': 'off_minamoto_yorichika',
    'chikuzen': 'off_ono_yoshifuru',
    'buzen': 'off_okura_haruzane',
    'chikugo': 'off_tachibana_kimiyori',
    'higo': 'off_ki_no_yoshimitsu',
    'hyuga': 'off_taira_koremoto',
    'satsuma': 'off_taira_koremoto',
    'osumi': 'off_taira_koremoto',
    'awaji': 'off_kuwahara_tomoharu',
    'oki': 'off_ki_no_yoshimitsu',
    'tsugaru': 'off_ando_morisue'
}

for sid in ['939', '1028', '1087']:
    scen_obj = next(s for s in scenarios if str(s['id']) == sid)
    owners = scen_obj.get('owners', {})
    t_map = hist_govs.setdefault(sid, {})
    for pid, cid in owners.items():
        if pid not in t_map and pid in court_govs_common:
            t_map[pid] = court_govs_common[pid]

# 1156, 1180 平氏支城補完
taira_fill_1156_1180 = {
    'etchu': 'off_taira_sukemori',
    'wakasa': 'off_taira_norimori',
    'hida': 'off_taira_morikuni',
    'tajima': 'off_taira_shigemori',
    'tango': 'off_taira_shigemori',
    'inaba': 'off_taira_morikuni',
    'hoki': 'off_taira_morikuni',
    'izumo': 'off_taira_tomomori',
    'iwami': 'off_taira_tomomori',
    'mimasaka': 'off_seoo_kaneyasu',
    'hyuga': 'off_taira_sadanou',
    'shima': 'off_ito_tadakiyo',
    'izu': 'off_ito_tadakiyo',
    'awaji': 'off_taguchi_shigeyoshi',
    'oki': 'off_taira_tomomori',
    'tosa': 'off_taguchi_shigeyoshi',
    'satsuma': 'off_taira_tadanori',
    'osumi': 'off_taira_tadanori',
    'iga': 'off_ito_tadakiyo',
    'north_omi': 'off_taira_shigemori',
    'south_omi': 'off_taira_shigemori',
    'kawachi': 'off_taira_shigehira',
    'izumi': 'off_taira_shigehira',
    'mikawa': 'off_taira_shigehira',
    'mino': 'off_taira_shigehira'
}
for sid in ['1156', '1180']:
    scen_obj = next(s for s in scenarios if str(s['id']) == sid)
    owners = scen_obj.get('owners', {})
    t_map = hist_govs.setdefault(sid, {})
    for pid, cid in owners.items():
        if pid not in t_map and cid == 'taira' and pid in taira_fill_1156_1180:
            t_map[pid] = taira_fill_1156_1180[pid]

# 1221 承久の乱 上皇領・幕府領補完
jokyu_fill = {
    'kawachi': 'off_miura_taneyoshi',
    'izumi': 'off_miura_taneyoshi',
    'tango': 'off_fujiwara_hideyasu',
    'wakasa': 'off_fujiwara_hideyasu',
    'ise': 'off_yamada_shigetada',
    'shima': 'off_yamada_shigetada',
    'iga': 'off_yamada_shigetada',
    'kii': 'off_kasuya_hisasue',
    'tajima': 'off_kasuya_hisasue',
    'inaba': 'off_kasuya_hisasue',
    'hoki': 'off_kasuya_hisasue',
    'izumo': 'off_kasuya_hisasue',
    'iwami': 'off_kasuya_hisasue',
    'mimasaka': 'off_kasuya_hisasue',
    'bizen': 'off_kasuya_hisasue',
    'bicchu': 'off_kasuya_hisasue',
    'bingo': 'off_kasuya_hisasue',
    'aki': 'off_kasuya_hisasue',
    'suo': 'off_kono_michinobu',
    'nagato': 'off_kono_michinobu',
    'sanuki': 'off_kono_michinobu',
    'awa_shikoku': 'off_kono_michinobu',
    'tosa': 'off_kono_michinobu',
    'awaji': 'off_kono_michinobu',
    'oki': 'off_fujiwara_hideyasu',
    'kozuke': 'off_ashikaga_yoshiuji',
    'echigo': 'off_miura_yoshimura',
    'etchu': 'off_sasaki_nobutsuna',
    'noto': 'off_sasaki_nobutsuna',
    'kaga': 'off_sasaki_nobutsuna',
    'hida': 'off_takeda_nobumitsu',
    'uzen': 'off_utsunomiya_yoritsuna'
}
if '1221' in hist_govs:
    t_map = hist_govs['1221']
    for pid, gid in jokyu_fill.items():
        if pid not in t_map:
            t_map[pid] = gid

print("Applied ancient, Heian, Kamakura, and Jokyu governor bulk fills.")

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

print(f"Saved completed data.js! Officers={len(officers)}")
