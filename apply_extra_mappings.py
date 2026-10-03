import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('window.OFFICERS_MASTER = [')
end_idx = text.find('\n];', start_idx) + 2
officers = json.loads(text[start_idx + len('window.OFFICERS_MASTER = '):end_idx])

start_idx_scen = text.find('window.SCENARIOS_DATA = [')
end_idx_scen = text.find('\n];', start_idx_scen) + 2
scenarios = json.loads(text[start_idx_scen + len('window.SCENARIOS_DATA = '):end_idx_scen])

idx_gov = text.find('window.SCENARIO_HISTORICAL_GOVERNORS = {')
end_idx_gov = text.find('\n};', idx_gov) + 3
hist_govs = json.loads(text[idx_gov + len('window.SCENARIO_HISTORICAL_GOVERNORS = '):end_idx_gov-1])

idx_cm = text.find('window.CLAN_CAPITAL_PROVINCES = {')
end_idx_cm = text.find('\n};', idx_cm) + 3
caps = json.loads(text[idx_cm + len('window.CLAN_CAPITAL_PROVINCES = '):end_idx_cm-1])

officers_map = {o['id']: o for o in officers}

# Define comprehensive precise mappings for remaining empty branches
extra_mappings = {
    # 1868 戊辰戦争
    ("1868", "mutsu"): "off_nanbu_nobuyuki",             # 南部信順
    ("1868", "rikuchu"): "off_narayama_sado",            # 楢山佐渡
    ("1868", "etchu"): "off_maeda_toshitomo",            # 前田利同（富山藩主）
    ("1868", "osumi"): "off_kabayama_sukemori",          # 樺山資紀
    ("1868", "hyuga"): "off_shimazu_hisamitsu",          # 島津久光

    # 1866 薩長同盟
    ("1866", "mutsu"): "off_nanbu_nobuyuki",             # 南部信順
    ("1866", "rikuchu"): "off_narayama_sado",            # 楢山佐渡
    ("1866", "etchu"): "off_maeda_toshitomo",            # 前田利同
    ("1866", "shimotsuke"): "off_hitomi_katsutaro",      # 人見勝太郎
    ("1866", "osumi"): "off_kabayama_sukemori",          # 樺山資紀
    ("1866", "hyuga"): "off_shimazu_hisamitsu",          # 島津久光

    # 1860 桜田門外の変
    ("1860", "mutsu"): "off_nanbu_nobuyuki",             # 南部信順
    ("1860", "rikuchu"): "off_narayama_sado",            # 楢山佐渡
    ("1860", "etchu"): "off_maeda_toshitomo",            # 前田利同
    ("1860", "hyuga"): "off_shimazu_hisamitsu",          # 島津久光
    ("1860", "osumi"): "off_kabayama_sukemori",          # 樺山資紀

    # 1853 ペリー来航
    ("1853", "mutsu"): "off_nanbu_nobuyuki",             # 南部信順
    ("1853", "rikuchu"): "off_narayama_sado",            # 楢山佐渡
    ("1853", "etchu"): "off_maeda_toshiyasu",            # 前田利保
    ("1853", "hyuga"): "off_shimazu_hisamitsu",          # 島津久光
    ("1853", "osumi"): "off_kabayama_sukemori",          # 樺山資紀

    # 1837 大塩平八郎の乱
    ("1837", "mutsu"): "off_nanbu_nobuyuki",             # 南部信順
    ("1837", "etchu"): "off_maeda_toshiyasu",            # 前田利保
    ("1837", "nagato"): "off_dm_mori_1868",              # 毛利敬親
    ("1837", "osumi"): "off_edo_shimazu_1809_183",      # 島津斉彬
    ("1837", "hyuga"): "off_shimazu_narioki",            # 島津斉興

    # 1651 慶安の変
    ("1651", "mutsu"): "off_nanbu_shigenao",             # 南部重直
    ("1651", "etchu"): "off_maeda_toshitsugu",           # 前田利次
    ("1651", "nagato"): "off_mori_hidemoto",             # 毛利秀元
    ("1651", "osumi"): "off_shimazu_tadahisa_mod",       # 島津忠朗

    # 1637 島原の乱
    ("1637", "mutsu"): "off_nanbu_shigenao",             # 南部重直
    ("1637", "etchu"): "off_maeda_toshitsugu",           # 前田利次

    # 1614 大坂の陣
    ("1614", "mutsu"): "off_nanbu_toshinao",             # 南部利直
    ("1614", "etchu"): "off_maeda_toshitsune",           # 前田利常
    ("1614", "hitachi"): "off_honda_masanobu",           # 本多正信

    # 1600 関ヶ原
    ("1600", "noto"): "off_maeda_toshimasa",             # 前田利政
    ("1600", "tajima"): "off_koide_yoshimasa",           # 小出吉政
    ("1600", "hoki"): "off_nanjo_mototsugu",             # 南条元続/元忠
    ("1600", "bicchu"): "off_kobayakawa_hideaki",        # 小早川秀秋
    ("1600", "wakasa"): "off_kyogoku_takatsugu",         # 京極高次

    # 1582 本能寺
    ("1582", "kazusa"): "off_masaki_tokishige",          # 正木時茂
    ("1582", "awa_boshu"): "off_satomi_yoshihiro",       # 里見義弘
    ("1582", "bicchu"): "off_shimizu_muneharu",          # 清水宗治
    ("1582", "nagato"): "off_kobayakawa_takakage",       # 小早川隆景
    ("1582", "hoki"): "off_nanjo_mototsugu",             # 南条元続
    ("1582", "oki"): "off_kikkawa_hiroie",               # 吉川広家
    ("1582", "sanuki"): "off_kagawa_chikakazu",          # 香川親和

    # 1584 小牧長久手
    ("1584", "mimasaka"): "off_hanabusa_masanari",       # 花房正成
    ("1584", "nagato"): "off_kobayakawa_takakage",       # 小早川隆景
    ("1584", "bicchu"): "off_kikkawa_motoharu",          # 吉川元春
    ("1584", "iwami"): "off_kikkawa_hiroie",             # 吉川広家
    ("1584", "oki"): "off_kikkawa_hiroie",               # 吉川広家

    # 1587 九州征伐
    ("1587", "nagato"): "off_mori_hidemoto",             # 毛利秀元
    ("1587", "bicchu"): "off_kobayakawa_hidekane",       # 小早川秀包
    ("1587", "iwami"): "off_kikkawa_hiroie",             # 吉川広家
    ("1587", "rikuchu"): "off_nanbu_nobunao",            # 南部信直

    # 1590 小田原征伐
    ("1590", "rikuchu"): "off_nanbu_nobunao",            # 南部信直
    ("1590", "iwami"): "off_kikkawa_hiroie",             # 吉川広家
    ("1590", "bicchu"): "off_kobayakawa_hidekane",       # 小早川秀包
    ("1590", "nagato"): "off_mori_hidemoto",             # 毛利秀元

    # 1592 文禄の役
    ("1592", "nagato"): "off_mori_hidemoto",             # 毛利秀元
    ("1592", "bicchu"): "off_kobayakawa_hidekane",       # 小早川秀包
    ("1592", "iwami"): "off_kikkawa_hiroie",             # 吉川広家
    ("1592", "oki"): "off_kikkawa_hiroie",               # 吉川広家

    # 1560 桶狭間
    ("1560", "awa_boshu"): "off_satomi_yoshihiro",       # 里見義弘
    ("1560", "kazusa"): "off_masaki_tokishige",          # 正木時茂
    ("1560", "aki"): "off_mori_motonari",                # 毛利元就
    ("1560", "chikugo"): "off_tachibana_dosetsu",        # 立花道雪
    ("1560", "tsugaru"): "off_tsugaru_tamenobu",         # 津軽為信
    ("1560", "iwami"): "off_kikkawa_motoharu",           # 吉川元春

    # 1570 信長包囲網
    ("1570", "iwami"): "off_kikkawa_motoharu",           # 吉川元春
    ("1570", "bingo"): "off_kobayakawa_takakage",        # 小早川隆景
    ("1570", "aki"): "off_mori_terumoto",                # 毛利輝元
    ("1570", "oki"): "off_kikkawa_hiroie",               # 吉川広家
    ("1570", "mino"): "off_oda_nobunaga",                # 織田信長

    # 1546 河越夜戦
    ("1546", "kazusa"): "off_masaki_tokishige",          # 正木時茂
    ("1546", "awa_boshu"): "off_satomi_yoshitaka",       # 里見義堯
    ("1546", "sagami"): "off_hojo_ujiyasu",              # 北条氏康
    ("1546", "izumo"): "off_amago_haruhisa",             # 尼子晴久
    ("1546", "oki"): "off_amago_kunihisa",               # 尼子国久
}

applied_extra = 0
for (sid, prov), off_id in extra_mappings.items():
    off = officers_map.get(off_id)
    if off:
        scen_h = hist_govs.setdefault(sid, {})
        scen_h[prov] = off['id']
        applied_extra += 1
    else:
        # Check by name
        match = next((o for o in officers if o['name'] == off_id or o['id'].endswith(off_id)), None)
        if match:
            scen_h = hist_govs.setdefault(sid, {})
            scen_h[prov] = match['id']
            applied_extra += 1
        else:
            print(f"Notice: extra mapping {off_id} not matched directly.")

print(f"Applied {applied_extra} extra mappings!")

# Write to js/data.js
new_gov_json = json.dumps(hist_govs, ensure_ascii=False, indent=2)
new_text = text[:idx_gov + len('window.SCENARIO_HISTORICAL_GOVERNORS = ')] + new_gov_json + text[end_idx_gov-1:]

with open('js/data.js', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Saved js/data.js.")
