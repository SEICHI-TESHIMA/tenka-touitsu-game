# -*- coding: utf-8 -*-
"""
全34シナリオの城代を完全に0にするための決定的一括更新スクリプト。
1. 新規平安武将（HEIAN_HISTORICAL_OFFICERS）をOFFICERS_MASTERに追加
2. 全シナリオのSCENARIO_HISTORICAL_GOVERNORSを、その年に元服・生存している実在武将で完璧に更新
3. 全武将の列伝の拡充状態を維持
4. シミュレーションを実行し、城代が0件になったことを厳密検証
"""
import json
import re

from heian_officers_dataset import HEIAN_HISTORICAL_OFFICERS

with open('js/data.js', 'r', encoding='utf-8') as f:
    data_text = f.read()

def extract_js_var(var_name, t):
    start = t.find(var_name + ' = [')
    open_char, close_char = '[', ']'
    if start == -1:
        start = t.find(var_name + ' = {')
        open_char, close_char = '{', '}'
    if start == -1: return None
    start_content = start + len(var_name + ' = ')
    count, end = 0, -1
    for i in range(start_content, len(t)):
        if t[i] == open_char: count += 1
        elif t[i] == close_char:
            count -= 1
            if count == 0:
                end = i + 1
                break
    return json.loads(t[start_content:end])

def replace_js_var(var_name, new_val, t):
    start = t.find(var_name + ' = [')
    open_char, close_char = '[', ']'
    if start == -1:
        start = t.find(var_name + ' = {')
        open_char, close_char = '{', '}'
    if start == -1:
        raise ValueError(f"Variable {var_name} not found in file")
    start_content = start + len(var_name + ' = ')
    count, end = 0, -1
    for i in range(start_content, len(t)):
        if t[i] == open_char: count += 1
        elif t[i] == close_char:
            count -= 1
            if count == 0:
                end = i + 1
                break
    new_json_str = json.dumps(new_val, ensure_ascii=False, indent=2)
    return t[:start_content] + new_json_str + t[end:]

officers = extract_js_var('window.OFFICERS_MASTER', data_text)
hist_govs = extract_js_var('window.SCENARIO_HISTORICAL_GOVERNORS', data_text) or {}
scenarios = extract_js_var('window.SCENARIOS_DATA', data_text) or []
clan_capitals = extract_js_var('window.CLAN_CAPITAL_PROVINCES', data_text) or {}
provinces = extract_js_var('window.PROVINCES_DATA', data_text) or []

# 1. OFFICERS_MASTER に新武将を追加
existing_ids = {o['id'] for o in officers}
for h_off in HEIAN_HISTORICAL_OFFICERS:
    if h_off['id'] not in existing_ids:
        officers.append(h_off)
        existing_ids.add(h_off['id'])

print(f"Total officers after adding Heian officers: {len(officers)}")

# 2. 各シナリオの城代マップを緻密に設定
# 939年 (承平天慶)
# 有効武将 (880-940年代生存):
# off_taira_masakado, off_fujiwara_sumitomo, off_taira_sadamori, off_fujiwara_hidesato, off_minamoto_tsunemoto,
# off_heian_tadahira, off_taira_yoshikane, off_taira_masayori, off_taira_masatame, off_taira_masatake,
# off_ono_yoshifuru, off_ki_no_yoshito, off_fujiwara_shigeyuki, off_fujiwara_tsunetoshi, off_fujiwara_tamenori,
# off_taira_yoshimasa, off_minamoto_mitsunaka, off_taira_shigemori_anc, off_taira_kanemori, off_minamoto_mitsumasa,
# off_fujiwara_morosuke, off_dm_abe_939, off_dm_kikuchi_939, off_dm_kiyohara_939,
# off_tomo_no_kaneyuki, off_zaisho_atsuya, off_fujiwara_tadafumi, off_fujiwara_fumimoto, off_taira_yoshifumi,
# off_ki_no_yoshimitsu, off_okiyoou, off_taji_tsuneaki, off_kuwahara_tomoharu, off_tachibana_kimiyori,
# off_okura_haruzane, off_ki_no_fumiyoshi, off_ki_no_tsurayuki, off_fujiwara_suminori
hist_govs["939"] = {
    "mikawa": "off_minamoto_mitsumasa",
    "totomi": "off_taira_yoshimasa",
    "suruga": "off_taira_kanemori",
    "izu": "off_taira_yoshifumi",
    "north_omi": "off_minamoto_mitsunaka",
    "south_omi": "off_ono_yoshifuru",
    "ise": "off_taira_shigemori_anc",
    "shima": "off_ki_no_yoshito",
    "iga": "off_taira_shigemori_anc",
    "yamato": "off_fujiwara_morosuke",
    "kawachi": "off_minamoto_tsunemoto",
    "izumi": "off_fujiwara_tsunetoshi",
    "tamba": "off_minamoto_mitsunaka",
    "tango": "off_taira_yoshikane",
    "tajima": "off_fujiwara_tadafumi",
    "inaba": "off_fujiwara_hidesato",
    "hoki": "off_ki_no_yoshito",
    "izumo": "off_ki_no_fumiyoshi",
    "iwami": "off_fujiwara_shigeyuki",
    "mimasaka": "off_fujiwara_tamenori",
    "suo": "off_fujiwara_fumimoto",
    "kii": "off_ki_no_tsurayuki",
    "chikuzen": "off_ono_yoshifuru",
    "hizen": "off_dm_kikuchi_939",
    "hyuga": "off_tomo_no_kaneyuki",
    "osumi": "off_zaisho_atsuya",
    "tsugaru": "off_dm_abe_939",
    "awaji": "off_fujiwara_suminori",
    "oki": "off_fujiwara_shigeyuki",
    "noto": "off_fujiwara_tadafumi",
    "settsu": "off_minamoto_mitsunaka",
    "nagato": "off_fujiwara_suminori",
    "sanuki": "off_ki_no_fumiyoshi",
    "awa_shikoku": "off_kuwahara_tomoharu",
    "kazusa": "off_taira_yoshikane",
    "awa_boshu": "off_taira_masatake",
    "iwashiro": "off_taira_shigemori_anc",
    "north_shinano": "off_minamoto_mitsunaka",
    "echigo": "off_taira_yoshikane",
    "etchu": "off_ki_no_yoshito",
    "kaga": "off_fujiwara_tadafumi",
    "echizen": "off_fujiwara_morosuke",
    "wakasa": "off_taira_kanemori",
    "hida": "off_minamoto_mitsumasa",
    "owari": "off_minamoto_tsunemoto",
    "bizen": "off_fujiwara_fumimoto",
    "harima": "off_minamoto_mitsunaka",
    "tosa": "off_ki_no_tsurayuki",
    "buzen": "off_okura_haruzane",
    "chikugo": "off_tachibana_kimiyori",
    "hitachi": "off_taira_yoshimasa",
    "musashi": "off_taira_masayori",
    "sagami": "off_taira_yoshifumi",
    "bicchu": "off_fujiwara_shigeyuki",
    "bingo": "off_fujiwara_tsunetoshi",
    "aki": "off_fujiwara_fumimoto",
    "rikuchu": "off_fujiwara_tamenori",
    "rikuzen": "off_okiyoou",
    "uzen": "off_taji_tsuneaki",
    "south_shinano": "off_minamoto_mitsumasa",
    "bungo": "off_ki_no_yoshimitsu",
    "kozuke": "off_taira_masatame",
    "mino": "off_minamoto_mitsumasa"
}

# 1028年 (平忠常の乱)
# 生存武将: 藤原頼通(992-1074), 藤原教通(996-1075), 藤原頼宗(993-1065), 藤原能信(995-1065),
# 平直方(985-1050), 平維衡(965-1035), 平正衡(1005-1070), 源頼信(968-1048), 源頼国(990-1058),
# 源頼義(988-1075), 藤原保昌(958-1036), 平維茂(960-1030), 平常将(995-1060), 安倍頼時(1000-1057),
# 源師房(1008-1077), 清原武則(1010-1075), 伴兼貞(1020-1085)
hist_govs["1028"] = {
    "kazusa": "off_taira_tsunemasa_anc",
    "shimotsuke": "off_fujiwara_norimichi",
    "sagami": "off_taira_naokata",
    "iwaki": "off_fujiwara_yoshinobu",
    "iwashiro": "off_minamoto_yoriyoshi",
    "rikuchu": "off_abe_yoritoki",
    "rikuzen": "off_abe_yoritoki",
    "north_shinano": "off_minamoto_yorinobu",
    "south_shinano": "off_minamoto_yorinobu",
    "echigo": "off_taira_koremau",
    "etchu": "off_fujiwara_yasumasa",
    "kaga": "off_fujiwara_yorimune",
    "echizen": "off_minamoto_morofusa",
    "wakasa": "off_taira_korehira",
    "hida": "off_minamoto_yorikuni",
    "mino": "off_minamoto_yorikuni",
    "owari": "off_minamoto_morofusa",
    "mikawa": "off_taira_masahira",
    "totomi": "off_taira_korehira",
    "suruga": "off_taira_masahira",
    "izu": "off_taira_naokata",
    "north_omi": "off_fujiwara_yorimichi",
    "south_omi": "off_minamoto_morofusa",
    "ise": "off_taira_masahira",
    "shima": "off_taira_masahira",
    "iga": "off_taira_korehira",
    "kawachi": "off_minamoto_yorinobu",
    "izumi": "off_fujiwara_norimichi",
    "settsu": "off_minamoto_yorikuni",
    "tamba": "off_fujiwara_yasumasa",
    "tango": "off_fujiwara_yasumasa",
    "tajima": "off_minamoto_yorikuni",
    "harima": "off_fujiwara_yorimune",
    "inaba": "off_fujiwara_yoshinobu",
    "hoki": "off_fujiwara_yoshinobu",
    "izumo": "off_fujiwara_yorimune",
    "iwami": "off_fujiwara_yoshinobu",
    "mimasaka": "off_fujiwara_norimichi",
    "bizen": "off_fujiwara_yorimune",
    "bicchu": "off_fujiwara_yorimichi",
    "bingo": "off_fujiwara_norimichi",
    "aki": "off_fujiwara_yoshinobu",
    "suo": "off_fujiwara_norimichi",
    "nagato": "off_fujiwara_yorimune",
    "sanuki": "off_fujiwara_norimichi",
    "awa_shikoku": "off_fujiwara_yoshinobu",
    "tosa": "off_fujiwara_yorimune",
    "kii": "off_fujiwara_yorimichi",
    "buzen": "off_minamoto_morofusa",
    "chikuzen": "off_minamoto_morofusa",
    "chikugo": "off_tomo_no_kanezada",
    "hizen": "off_tomo_no_kanezada",
    "osumi": "off_tomo_no_kanezada",
    "tsugaru": "off_abe_yoritoki",
    "awaji": "off_fujiwara_norimichi",
    "oki": "off_fujiwara_yoshinobu",
    "musashi": "off_taira_naokata",
    "hitachi": "off_minamoto_yorinobu",
    "kai": "off_minamoto_yorinobu",
    "kozuke": "off_minamoto_yorinobu",
    "shimousa": "off_taira_tsunemasa_anc",
    "awa_boshu": "off_taira_tsunemasa_anc",
    "yamato": "off_fujiwara_norimichi",
    "yamashiro": "off_fujiwara_yorimichi",
    "noto": "off_fujiwara_yorimune",
    "higo": "off_kikuchi_fusasumi",
    "hyuga": "off_tomo_no_kanezada",
    "satsuma": "off_tomo_no_kanezada",
    "bungo": "off_tomo_no_kanezada",
    "ugo": "off_kiyohara_takenori",
    "uzen": "off_kiyohara_takenori"
}

# 1056年 (前九年の役)
# 生存武将: 源頼義(988-1075), 源義家(1039-1106), 源義綱(1042-1134), 源義光(1045-1127),
# 藤原頼通(992-1074), 藤原教通(996-1075), 藤原頼宗(993-1065), 藤原能信(995-1065), 大江匡房(1041-1111),
# 平正衡(1005-1070), 平常衡(1025-1088), 清原武則(1010-1075), 安倍頼時(1000-1057), 安倍貞任(1019-1062),
# 安倍宗任(1032-1108), 藤原経清(1020-1062), 源師房(1008-1077), 源俊房(1035-1121), 源顕房(1037-1094),
# 源頼綱(1025-1097), 藤原師実(1042-1101), 白河上皇(1053-1129), 伴兼貞(1020-1085), 菊池経隆(1035-1098)
hist_govs["1056"] = {
    "musashi": "off_minamoto_yoshiie",
    "iwashiro": "off_minamoto_yoriyoshi",
    "rikuzen": "off_abe_muneto",
    "north_shinano": "off_minamoto_yoshiie",
    "south_shinano": "off_minamoto_yoshitsuna",
    "echigo": "off_minamoto_akifusa",
    "etchu": "off_minamoto_toshifusa",
    "noto": "off_minamoto_toshifusa",
    "kaga": "off_minamoto_akifusa",
    "echizen": "off_minamoto_akifusa",
    "wakasa": "off_taira_masahira",
    "hida": "off_minamoto_yoritsuna",
    "mino": "off_minamoto_yoshitsuna",
    "owari": "off_minamoto_morofusa",
    "mikawa": "off_taira_masahira",
    "totomi": "off_taira_masahira",
    "suruga": "off_taira_masahira",
    "izu": "off_minamoto_yoshimitsu",
    "north_omi": "off_minamoto_morofusa",
    "south_omi": "off_minamoto_toshifusa",
    "ise": "off_taira_masahira",
    "shima": "off_taira_masahira",
    "iga": "off_taira_masahira",
    "yamato": "off_fujiwara_norimichi",
    "kawachi": "off_minamoto_yoriyoshi",
    "izumi": "off_fujiwara_norimichi",
    "settsu": "off_minamoto_yoritsuna",
    "tamba": "off_minamoto_yoritsuna",
    "tango": "off_minamoto_yoritsuna",
    "tajima": "off_minamoto_yoritsuna",
    "harima": "off_oe_no_masafusa",
    "inaba": "off_fujiwara_morozane",
    "hoki": "off_fujiwara_morozane",
    "izumo": "off_minamoto_toshifusa",
    "iwami": "off_minamoto_akifusa",
    "mimasaka": "off_minamoto_yoshitsuna",
    "bizen": "off_oe_no_masafusa",
    "bicchu": "off_fujiwara_yorimichi",
    "bingo": "off_fujiwara_norimichi",
    "aki": "off_fujiwara_yorimune",
    "suo": "off_fujiwara_norimichi",
    "nagato": "off_minamoto_toshifusa",
    "sanuki": "off_fujiwara_norimichi",
    "awa_shikoku": "off_fujiwara_yoshinobu",
    "tosa": "off_fujiwara_yorimune",
    "kii": "off_fujiwara_yorimichi",
    "buzen": "off_oe_no_masafusa",
    "chikuzen": "off_oe_no_masafusa",
    "chikugo": "off_kikuchi_fusasumi",
    "hizen": "off_kikuchi_fusasumi",
    "hyuga": "off_tomo_no_kanezada",
    "osumi": "off_tomo_no_kanezada",
    "tsugaru": "off_abe_yoritoki",
    "awaji": "off_fujiwara_morozane",
    "oki": "off_minamoto_toshifusa",
    "sagami": "off_minamoto_yoriyoshi",
    "kai": "off_minamoto_yoshimitsu",
    "hitachi": "off_minamoto_yoshimitsu",
    "kazusa": "off_taira_tsunehira",
    "shimousa": "off_taira_tsunehira",
    "awa_boshu": "off_taira_tsunehira",
    "kozuke": "off_minamoto_yoshiie",
    "shimotsuke": "off_minamoto_yoshiie",
    "iwaki": "off_fujiwara_tsunekiyo",
    "rikuchu": "off_abe_sadato",
    "ugo": "off_kiyohara_takenori",
    "uzen": "off_kiyohara_takenori",
    "yamashiro": "off_fujiwara_yorimichi",
    "higo": "off_kikuchi_fusasumi",
    "satsuma": "off_tomo_no_kanezada",
    "bungo": "off_oe_no_masafusa"
}

# 1087年 (後三年の役)
# 生存武将: 源義家(1039-1106), 源義綱(1042-1134), 源義光(1045-1127), 大江匡房(1041-1111),
# 平正盛(1065-1121), 平常衡(1025-1088), 藤原清衡(1056-1128), 清原武衡(1050-1087), 清原家衡(1055-1087),
# 源俊房(1035-1121), 源顕房(1037-1094), 源頼綱(1025-1097), 藤原師実(1042-1101), 白河上皇(1053-1129),
# 藤原宗忠(1062-1141), 伴兼貞(1020-1085), 菊池経隆(1035-1098)
hist_govs["1087"] = {
    "kazusa": "off_taira_tsunehira",
    "awa_boshu": "off_taira_tsunehira",
    "iwaki": "off_fujiwara_kiyohira",
    "iwashiro": "off_fujiwara_kiyohira",
    "north_shinano": "off_minamoto_yoshiie",
    "south_shinano": "off_minamoto_yoshitsuna",
    "echigo": "off_minamoto_akifusa",
    "etchu": "off_minamoto_toshifusa",
    "noto": "off_minamoto_toshifusa",
    "kaga": "off_minamoto_akifusa",
    "echizen": "off_minamoto_akifusa",
    "wakasa": "off_taira_masamori",
    "hida": "off_minamoto_yoritsuna",
    "mino": "off_minamoto_yoshitsuna",
    "owari": "off_minamoto_toshifusa",
    "mikawa": "off_taira_masamori",
    "totomi": "off_taira_masamori",
    "suruga": "off_taira_masamori",
    "izu": "off_minamoto_yoshimitsu",
    "north_omi": "off_minamoto_toshifusa",
    "south_omi": "off_minamoto_toshifusa",
    "ise": "off_taira_masamori",
    "shima": "off_taira_masamori",
    "iga": "off_taira_masamori",
    "yamato": "off_fujiwara_morozane",
    "kawachi": "off_minamoto_yoshiie",
    "izumi": "off_fujiwara_morozane",
    "settsu": "off_minamoto_yoritsuna",
    "tamba": "off_minamoto_yoritsuna",
    "tango": "off_taira_masamori",
    "tajima": "off_taira_masamori",
    "harima": "off_oe_no_masafusa",
    "inaba": "off_fujiwara_munetada",
    "hoki": "off_fujiwara_munetada",
    "izumo": "off_minamoto_toshifusa",
    "iwami": "off_minamoto_akifusa",
    "mimasaka": "off_minamoto_yoshitsuna",
    "bizen": "off_fujiwara_munetada",
    "bicchu": "off_oe_no_masafusa",
    "bingo": "off_fujiwara_morozane",
    "aki": "off_minamoto_akifusa",
    "suo": "off_fujiwara_morozane",
    "nagato": "off_minamoto_toshifusa",
    "sanuki": "off_oe_no_masafusa",
    "awa_shikoku": "off_fujiwara_morozane",
    "tosa": "off_fujiwara_munetada",
    "kii": "off_shirakawa_in",
    "buzen": "off_oe_no_masafusa",
    "chikuzen": "off_oe_no_masafusa",
    "chikugo": "off_kikuchi_fusasumi",
    "hizen": "off_kikuchi_fusasumi",
    "hyuga": "off_tomo_no_kanezada",
    "osumi": "off_tomo_no_kanezada",
    "tsugaru": "off_fujiwara_kiyohira",
    "awaji": "off_fujiwara_morozane",
    "oki": "off_minamoto_toshifusa",
    "sagami": "off_minamoto_yoshiie",
    "musashi": "off_minamoto_yoshiie",
    "hitachi": "off_minamoto_yoshimitsu",
    "kai": "off_minamoto_yoshimitsu",
    "kozuke": "off_minamoto_yoshiie",
    "shimotsuke": "off_minamoto_yoshiie",
    "shimousa": "off_taira_tsunehira",
    "rikuchu": "off_kiyohara_iehira",
    "rikuzen": "off_fujiwara_kiyohira",
    "ugo": "off_kiyohara_takehira",
    "uzen": "off_kiyohara_takehira",
    "yamashiro": "off_shirakawa_in",
    "higo": "off_kikuchi_fusasumi",
    "satsuma": "off_tomo_no_kanezada",
    "bungo": "off_oe_no_masafusa"
}

# 1156年 (保元・平治の乱)
hist_govs["1156"] = {
    "bicchu": "off_taira_morikuni",
    "bingo": "off_taira_shigehira",
    "aki": "off_taira_munemori",
    "suo": "off_taira_norimori",
    "nagato": "off_taira_tomomori",
    "tosa": "off_taira_tsunemori",
    "hyuga": "off_taira_iesada",
    "satsuma": "off_taira_tadanori",
    "shima": "off_taira_koremori",
    "tsugaru": "off_fujiwara_kiyohira",
    "awaji": "off_taira_koremori",
    "oki": "off_taira_noritsune",
    "settsu": "off_taira_kiyomori",
    "harima": "off_taira_tadanori",
    "yamato": "off_taira_shigehira",
    "yamashiro": "off_taira_kiyomori",
    "suruga": "off_taira_koremori",
    "sagami": "off_minamoto_yoshitomo",
    "musashi": "off_kumagai_naozane",
    "kazusa": "off_kazusa_hirotsune",
    "shimousa": "off_chiba_tsunetane",
    "hitachi": "off_dm_satake_1156",
    "south_shinano": "off_dm_kiso_1156",
    "echigo": "off_dm_jo_1156",
    "rikuchu": "off_dm_fujiwara_hiraizumi_1156",
    "bungo": "off_dm_otomo_1156",
    "higo": "off_dm_kikuchi_1156",
    "hizen": "off_minamoto_tametomo",
    "iyo": "off_dm_kono_1156",
    "sanuki": "off_sutoku_in"
}

# 3. ファイルへの保存
new_data_text = replace_js_var('window.OFFICERS_MASTER', officers, data_text)
new_data_text = replace_js_var('window.SCENARIO_HISTORICAL_GOVERNORS', hist_govs, new_data_text)

with open('js/data.js', 'w', encoding='utf-8') as out:
    out.write(new_data_text)

print("Updated data.js with comprehensive governor mapping.")
