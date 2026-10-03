# -*- coding: utf-8 -*-
"""
各シナリオの城代国（233箇所）を解消するための完全マッピングテーブルを構築するスクリプト。
"""

# 各シナリオの城代国に対する史実武将の配属辞書
# scenario_id -> { prov_id: officer_id }
GOVERNOR_FIXES = {
    # 939 承平・天慶の乱
    "939": {
        "mikawa": "off_minamoto_mitsumasa",
        "totomi": "off_taira_yoshimasa",
        "suruga": "off_taira_kanemori",
        "izu": "off_taira_yoshifumi",
        "north_omi": "off_heian_tadahira",
        "south_omi": "off_ononoyoshifuru",
        "ise": "off_taira_sadamori",
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
        "mimasaka": "off_fujiwara_fuminori",
        "suo": "off_fujiwara_fumimoto",
        "kii": "off_ki_no_tsurayuki",
        "chikuzen": "off_ono_yoshifuru", # fix daimyo check in matching
        "hizen": "off_dm_kikuchi_939",
        "hyuga": "off_tomo_no_kaneyuki",
        "osumi": "off_zaisho_atsuya",
        "tsugaru": "off_dm_abe_939",
        "awaji": "off_fujiwara_suminori",
        "oki": "off_okura_harumi"
    },
    # 1028 平忠常の乱
    "1028": {
        "kazusa": "off_taira_yoshifumi",
        "iwaki": "off_fujiwara_tsunekiyo",
        "iwashiro": "off_minamoto_yoriyoshi",
        "rikuchu": "off_abe_sadato",
        "rikuzen": "off_abe_muneto",
        "north_shinano": "off_minamoto_yorinobu",
        "south_shinano": "off_minamoto_yoshiie",
        "echigo": "off_taira_naokata",
        "etchu": "off_fujiwara_yasumasa",
        "kaga": "off_fujiwara_tadafumi",
        "echizen": "off_fujiwara_morosuke",
        "wakasa": "off_taira_korehira",
        "hida": "off_minamoto_mitsumasa",
        "mino": "off_minamoto_yorikuni",
        "owari": "off_minamoto_yorimitsu",
        "mikawa": "off_taira_masahira",
        "totomi": "off_taira_korehira",
        "suruga": "off_taira_kanemori",
        "izu": "off_taira_naokata",
        "north_omi": "off_fujiwara_michinaga",
        "south_omi": "off_ononoyoshifuru",
        "shima": "off_ki_no_yoshito",
        "iga": "off_taira_masahira",
        "kawachi": "off_minamoto_yorinobu",
        "izumi": "off_fujiwara_tsunetoshi",
        "settsu": "off_minamoto_yorimitsu",
        "tamba": "off_fujiwara_yasumasa",
        "tango": "off_taira_masamori",
        "tajima": "off_minamoto_mitsunaka",
        "harima": "off_minamoto_yorikuni",
        "inaba": "off_fujiwara_hidesato",
        "hoki": "off_ki_no_yoshito",
        "izumo": "off_ki_no_fumiyoshi",
        "iwami": "off_fujiwara_shigeyuki",
        "mimasaka": "off_fujiwara_fuminori",
        "bizen": "off_fujiwara_fumimoto",
        "bicchu": "off_fujiwara_shigeyuki",
        "bingo": "off_fujiwara_tsunetoshi",
        "aki": "off_ki_no_tsurayuki",
        "suo": "off_fujiwara_suminori",
        "nagato": "off_okura_harumi",
        "sanuki": "off_fujiwara_sumitomo",
        "awa_shikoku": "off_kuwahara_tomoharu",
        "tosa": "off_ki_no_tsurayuki",
        "kii": "off_ki_no_yoshimitsu",
        "buzen": "off_okura_haruzane",
        "chikuzen": "off_ono_yoshifuru",
        "chikugo": "off_tachibana_kimiyori",
        "hizen": "off_dm_kikuchi_939",
        "osumi": "off_zaisho_atsuya",
        "tsugaru": "off_abe_yoritoki",
        "awaji": "off_fujiwara_suminori",
        "oki": "off_okura_harumi"
    },
    # 1056 前九年の役
    "1056": {
        "musashi": "off_taira_naokata",
        "iwashiro": "off_minamoto_yoriyoshi",
        "rikuzen": "off_abe_muneto",
        "north_shinano": "off_minamoto_yoshiie",
        "south_shinano": "off_minamoto_yoshitsuna",
        "echigo": "off_taira_naokata",
        "etchu": "off_fujiwara_yasumasa",
        "noto": "off_fujiwara_tadafumi",
        "kaga": "off_fujiwara_morosuke",
        "echizen": "off_fujiwara_morosuke",
        "wakasa": "off_taira_korehira",
        "hida": "off_minamoto_mitsumasa",
        "mino": "off_minamoto_yorikuni",
        "owari": "off_minamoto_yorimitsu",
        "mikawa": "off_taira_masahira",
        "totomi": "off_taira_korehira",
        "suruga": "off_taira_kanemori",
        "izu": "off_taira_naokata",
        "north_omi": "off_fujiwara_michinaga",
        "south_omi": "off_ononoyoshifuru",
        "ise": "off_taira_masahira",
        "shima": "off_ki_no_yoshito",
        "iga": "off_taira_masahira",
        "yamato": "off_fujiwara_morosuke",
        "izumi": "off_fujiwara_tsunetoshi",
        "settsu": "off_minamoto_yorimitsu",
        "tamba": "off_fujiwara_yasumasa",
        "tango": "off_taira_masamori",
        "tajima": "off_minamoto_mitsunaka",
        "harima": "off_minamoto_yorikuni",
        "inaba": "off_fujiwara_hidesato",
        "hoki": "off_ki_no_yoshito",
        "izumo": "off_ki_no_fumiyoshi",
        "iwami": "off_fujiwara_shigeyuki",
        "mimasaka": "off_fujiwara_fuminori",
        "bizen": "off_fujiwara_fumimoto",
        "bicchu": "off_fujiwara_shigeyuki",
        "bingo": "off_fujiwara_tsunetoshi",
        "aki": "off_ki_no_tsurayuki",
        "suo": "off_fujiwara_suminori",
        "nagato": "off_okura_harumi",
        "sanuki": "off_fujiwara_sumitomo",
        "awa_shikoku": "off_kuwahara_tomoharu",
        "tosa": "off_ki_no_tsurayuki",
        "kii": "off_ki_no_yoshimitsu",
        "buzen": "off_okura_haruzane",
        "chikuzen": "off_ono_yoshifuru",
        "chikugo": "off_tachibana_kimiyori",
        "hizen": "off_dm_kikuchi_939",
        "hyuga": "off_tomo_no_kaneyuki",
        "tsugaru": "off_abe_yoritoki",
        "awaji": "off_fujiwara_suminori",
        "oki": "off_okura_harumi"
    },
    # 1087 後三年の役
    "1087": {
        "kazusa": "off_taira_yoshifumi",
        "awa_boshu": "off_taira_masatake",
        "iwaki": "off_fujiwara_tsunekiyo",
        "iwashiro": "off_minamoto_yoriyoshi",
        "north_shinano": "off_minamoto_yoshiie",
        "south_shinano": "off_minamoto_yoshitsuna",
        "echigo": "off_taira_naokata",
        "etchu": "off_fujiwara_yasumasa",
        "noto": "off_fujiwara_tadafumi",
        "kaga": "off_fujiwara_morosuke",
        "echizen": "off_fujiwara_morosuke",
        "wakasa": "off_taira_korehira",
        "hida": "off_minamoto_mitsumasa",
        "mino": "off_minamoto_yorikuni",
        "owari": "off_minamoto_yorimitsu",
        "mikawa": "off_taira_masahira",
        "totomi": "off_taira_korehira",
        "suruga": "off_taira_kanemori",
        "izu": "off_taira_naokata",
        "north_omi": "off_fujiwara_michinaga",
        "south_omi": "off_ononoyoshifuru",
        "shima": "off_ki_no_yoshito",
        "iga": "off_taira_masahira",
        "yamato": "off_fujiwara_morosuke",
        "izumi": "off_fujiwara_tsunetoshi",
        "settsu": "off_minamoto_yorimitsu",
        "tamba": "off_fujiwara_yasumasa",
        "tango": "off_taira_masamori",
        "tajima": "off_minamoto_mitsunaka",
        "harima": "off_minamoto_yorikuni",
        "inaba": "off_fujiwara_hidesato",
        "hoki": "off_ki_no_yoshito",
        "izumo": "off_ki_no_fumiyoshi",
        "iwami": "off_fujiwara_shigeyuki",
        "mimasaka": "off_fujiwara_fuminori",
        "bizen": "off_fujiwara_fumimoto",
        "bicchu": "off_fujiwara_shigeyuki",
        "bingo": "off_fujiwara_tsunetoshi",
        "aki": "off_ki_no_tsurayuki",
        "suo": "off_fujiwara_suminori",
        "nagato": "off_okura_harumi",
        "sanuki": "off_fujiwara_sumitomo",
        "awa_shikoku": "off_kuwahara_tomoharu",
        "tosa": "off_ki_no_tsurayuki",
        "kii": "off_ki_no_yoshimitsu",
        "buzen": "off_okura_haruzane",
        "chikuzen": "off_ono_yoshifuru",
        "chikugo": "off_tachibana_kimiyori",
        "hizen": "off_dm_kikuchi_939",
        "hyuga": "off_tomo_no_kaneyuki",
        "osumi": "off_zaisho_atsuya",
        "awaji": "off_fujiwara_suminori",
        "oki": "off_okura_harumi"
    },
    # 1156 保元・平治の乱
    "1156": {
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
        "oki": "off_taira_noritsune"
    },
    # 1221 承久の乱
    "1221": {
        "awaji": "off_sasaki_tsunetaka",
        "oki": "off_sasaki_shigekiyo"
    },
    # 1438 永享の乱
    "1438": {
        "chikuzen": "off_ouchi_noriyuki",
        "awaji": "off_hosokawa_mochikata"
    },
    # 1467 応仁の乱
    "1467": {
        "buzen": "off_kurokawa_harunari",
        "chikuzen": "off_aso_ieharu",
        "chikugo": "off_monchujo_yasusumi",
        "tsugaru": "off_nanbu_namioka_akiyasu",
        "oki": "off_kyogoku_oki_kiyomasa"
    },
    # 1546 河越夜戦
    "1546": {
        "oki": "off_oki_tamekiyo"
    },
    # 1560 桶狭間の戦い
    "1560": {
        "suo": "off_naito_takaharu"
    },
    # 1570 信長包囲網
    "1570": {
        "suo": "off_ichikawa_tsuneyoshi",
        "nagato": "off_naito_takaharu",
        "oki": "off_oki_tamekiyo"
    },
    # 1582 本能寺の変前夜
    "1582": {
        "kazusa": "off_masaki_yoritada",
        "nagato": "off_naito_motosori",
        "oki": "off_oki_kiyomasa_sengoku"
    },
    # 1584 小牧長久手の戦い
    "1584": {
        "nagato": "off_naito_motosori",
        "iwami": "off_masuda_fujikane",
        "oki": "off_oki_kiyomasa_sengoku"
    },
    # 1587 秀吉の九州征伐
    "1587": {
        "iwami": "off_masuda_motoyoshi"
    },
    # 1590 小田原征伐
    "1590": {
        "nagato": "off_naito_motosori"
    },
    # 1592 文禄の役
    "1592": {
        "iwami": "off_masuda_motoyoshi",
        "oki": "off_oki_kiyomasa_sengoku"
    },
    # 1600 関ヶ原の戦い
    "1600": {
        "hoki": "off_kikkawa_hiroie"
    },
    # 1789 寛政の改革
    "1789": {
        "tamba": "off_edo_aoyama_tadahiro",
        "tango": "off_kyogoku_takawaki",
        "tajima": "off_sengoku_hisamichi",
        "iwami": "off_kamei_koresada",
        "mimasaka": "off_miura_maetsugu",
        "bicchu": "off_edo_itakura_katsumasa",
        "sanuki": "off_matsudaira_yoritaka_sanuki",
        "bungo": "off_matsudaira_chikasada",
        "osumi": "off_kabayama_hisatomo",
        "oki": "off_matsudaira_naotsune",
        "awaji": "off_inada_toshitane"
    }
}

print("GOVERNOR_FIXES mapping defined.")
