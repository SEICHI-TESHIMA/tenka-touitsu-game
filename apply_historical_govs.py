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

idx_cm = text.find('window.CLAN_MASTER_DATA = {')
end_idx_cm = text.find('\n};', idx_cm) + 3
clan_master = json.loads(text[idx_cm + len('window.CLAN_MASTER_DATA = '):end_idx_cm-1])

officers_by_id = {o['id']: o for o in officers}
officers_by_name = {o['name']: o for o in officers}

# Define historical assignments for empty jodai across scenarios
# (sid, prov) -> officer_id
historical_overrides = {
    # === 1866 (薩長同盟) ===
    ("1866", "north_shinano"): "off_sanada_yukinori",     # 真田幸教（松代藩主）
    ("1866", "south_shinano"): "off_oguri_tadasumi",      # 小栗忠順
    ("1866", "sagami"): "off_okubo_tadanori_bakumatsu",   # 大久保忠礼（小田原藩主）
    ("1866", "kozuke"): "off_oguri_tadasumi",             # 小栗忠順（上野権田）
    ("1866", "kazusa"): "off_hayashi_tadataka",           # 林忠崇（請西藩主）
    ("1866", "totomi"): "off_katsu_kaishu",               # 勝海舟
    ("1866", "suruga"): "off_katsu_kaishu",               # 勝海舟
    ("1866", "yamashiro"): "off_kondo_isami",             # 近藤勇（京都守護）
    ("1866", "bicchu"): "off_itakura_katsukiyo",          # 板倉勝静（備中松山藩主）
    ("1866", "bingo"): "off_abe_masakata",                # 阿部正方（福山藩主）
    ("1866", "higo"): "off_hosokawa_yoshikuni",           # 細川韶邦（熊本藩主）
    ("1866", "chikuzen"): "off_kuroda_nagahiro2",         # 黒田長溥（福岡藩主）
    ("1866", "kaga"): "off_dm_maeda_1868",                # 前田慶寧/斉泰
    ("1866", "satsuma"): "off_dm_shimazu_1868",           # 島津忠義
    ("1866", "osumi"): "off_shimazu_hisamitsu",           # 島津久光
    ("1866", "nagato"): "off_mori_takachika",             # 毛利敬親
    ("1866", "suo"): "off_dm_mori_1868",                  # 毛利元徳
    ("1866", "tosa"): "off_yamauchi_yodo",                # 山内容堂
    ("1866", "owari"): "off_dm_owari_1868",               # 徳川慶勝
    ("1866", "settsu"): "off_enomoto_takeaki",            # 榎本武揚（幕府海軍）
    ("1866", "musashi"): "off_tokugawa_yoshinobu",        # 徳川慶喜
    ("1866", "iwaki"): "off_katakura_shigenaga",          # 白石城主

    # === 1853 (ペリー来航) ===
    ("1853", "north_shinano"): "off_sanada_yukinori",     # 真田幸教
    ("1853", "south_shinano"): "off_sakuma_shozen",       # 佐久間象山
    ("1853", "musashi"): "off_abe_masahiro",              # 阿部正弘
    ("1853", "bicchu"): "off_yamada_hokoku",              # 山田方谷
    ("1853", "bingo"): "off_abe_masahiro",                # 阿部正弘
    ("1853", "higo"): "off_hosokawa_narimori",            # 細川斉護
    ("1853", "chikuzen"): "off_kuroda_nagahiro2",         # 黒田長溥
    ("1853", "kaga"): "off_dm_maeda_1868",                # 前田斉泰
    ("1853", "satsuma"): "off_shimazu_nariakira",         # 島津斉彬
    ("1853", "osumi"): "off_shimazu_hisamitsu",           # 島津久光
    ("1853", "nagato"): "off_mori_takachika",             # 毛利敬親
    ("1853", "suo"): "off_dm_mori_1868",                  # 毛利元徳
    ("1853", "tosa"): "off_yamauchi_yodo",                # 山内容堂
    ("1853", "owari"): "off_dm_owari_1868",               # 徳川慶勝

    # === 1860 (桜田門外の変) ===
    ("1860", "north_shinano"): "off_sanada_yukinori",     # 真田幸教
    ("1860", "south_shinano"): "off_sakuma_shozen",       # 佐久間象山
    ("1860", "sagami"): "off_okubo_tadanori_bakumatsu",   # 大久保忠礼
    ("1860", "bicchu"): "off_itakura_katsukiyo",          # 板倉勝静
    ("1860", "bingo"): "off_abe_masakata",                # 阿部正方
    ("1860", "higo"): "off_hosokawa_yoshikuni",           # 細川韶邦
    ("1860", "chikuzen"): "off_kuroda_nagahiro2",         # 黒田長溥
    ("1860", "kaga"): "off_dm_maeda_1868",                # 前田斉泰
    ("1860", "satsuma"): "off_dm_shimazu_1868",           # 島津忠義
    ("1860", "osumi"): "off_shimazu_hisamitsu",           # 島津久光
    ("1860", "nagato"): "off_mori_takachika",             # 毛利敬親
    ("1860", "suo"): "off_dm_mori_1868",                  # 毛利元徳
    ("1860", "tosa"): "off_yamauchi_yodo",                # 山内容堂
    ("1860", "owari"): "off_dm_owari_1868",               # 徳川慶勝

    # === 1837 (大塩平八郎の乱) ===
    ("1837", "north_shinano"): "off_sanada_yukitsura",    # 真田幸貫
    ("1837", "higo"): "off_hosokawa_narimori",            # 細川斉護
    ("1837", "chikuzen"): "off_kuroda_nagahiro2",         # 黒田長溥
    ("1837", "kaga"): "off_dm_maeda_1868",                # 前田斉泰
    ("1837", "satsuma"): "off_shimazu_narioki",           # 島津斉興
    ("1837", "osumi"): "off_shimazu_nariakira",           # 島津斉彬
    ("1837", "nagato"): "off_mori_takachika",             # 毛利敬親
    ("1837", "bicchu"): "off_yamada_hokoku",              # 山田方谷

    # === 1592 (文禄の役) ===
    ("1592", "shima"): "off_kuki_yoshitaka",              # 九鬼嘉隆
    ("1592", "iga"): "off_tsutsui_sadatsugu",             # 筒井定次
    ("1592", "kawachi"): "off_katagiri_katsumoto",        # 片桐且元
    ("1592", "awaji"): "off_wakisaka_yasuharu",           # 脇坂安治
    ("1592", "sanuki"): "off_ikoma_chikamasa",            # 生駒親正
    ("1592", "awa_shikoku"): "off_hachisuka_iemasa",      # 蜂須賀家政
    ("1592", "tajima"): "off_maeno_nagayasu",             # 前野長康
    ("1592", "inaba"): "off_miyabe_keijun",               # 宮部継潤
    ("1592", "hida"): "off_kanamori_nagachika",           # 金森長近
    ("1592", "nagato"): "off_mori_hidemoto",              # 毛利秀元
    ("1592", "izumo"): "off_kikkawa_hiroie",              # 吉川広家
    ("1592", "bicchu"): "off_kobayakawa_hidekane",        # 小早川秀包
    ("1592", "izumi"): "off_konishi_yukinaga",            # 小西行長
    ("1592", "kii"): "off_asano_yoshinaga",               # 浅野幸長

    # === 1590 (小田原征伐) ===
    ("1590", "shima"): "off_kuki_yoshitaka",              # 九鬼嘉隆
    ("1590", "iga"): "off_tsutsui_sadatsugu",             # 筒井定次
    ("1590", "kawachi"): "off_katagiri_katsumoto",        # 片桐且元
    ("1590", "awaji"): "off_wakisaka_yasuharu",           # 脇坂安治
    ("1590", "sanuki"): "off_ikoma_chikamasa",            # 生駒親正
    ("1590", "awa_shikoku"): "off_hachisuka_iemasa",      # 蜂須賀家政
    ("1590", "tajima"): "off_maeno_nagayasu",             # 前野長康
    ("1590", "inaba"): "off_miyabe_keijun",               # 宮部継潤
    ("1590", "nagato"): "off_mori_hidemoto",              # 毛利秀元
    ("1590", "hoki"): "off_nanjo_mototsugu",              # 南条元続
    ("1590", "kii"): "off_asano_yoshinaga",               # 浅野幸長

    # === 1587 (九州征伐) ===
    ("1587", "shima"): "off_kuki_yoshitaka",              # 九鬼嘉隆
    ("1587", "iga"): "off_tsutsui_sadatsugu",             # 筒井定次
    ("1587", "awaji"): "off_wakisaka_yasuharu",           # 脇坂安治
    ("1587", "awa_shikoku"): "off_hachisuka_iemasa",      # 蜂須賀家政
    ("1587", "tajima"): "off_maeno_nagayasu",             # 前野長康
    ("1587", "inaba"): "off_miyabe_keijun",               # 宮部継潤
    ("1587", "hoki"): "off_nanjo_mototsugu",              # 南条元続
    ("1587", "nagato"): "off_mori_hidemoto",              # 毛利秀元
    ("1587", "izu"): "off_matsuda_yasunaga",              # 松田康長
    ("1587", "kii"): "off_asano_yoshinaga",               # 浅野幸長
    ("1587", "izumo"): "off_kikkawa_hiroie",              # 吉川広家

    # === 1584 (小牧長久手の戦い) ===
    ("1584", "shima"): "off_kuki_yoshitaka",              # 九鬼嘉隆
    ("1584", "awaji"): "off_wakisaka_yasuharu",           # 脇坂安治
    ("1584", "inaba"): "off_miyabe_keijun",               # 宮部継潤
    ("1584", "hoki"): "off_nanjo_mototsugu",              # 南条元続
    ("1584", "izu"): "off_matsuda_yasunaga",              # 松田康長
    ("1584", "nagato"): "off_kobayakawa_takakage",        # 小早川隆景
    ("1584", "bicchu"): "off_kikkawa_motoharu",           # 吉川元春
    ("1584", "sanuki"): "off_sengoku_hidehisa",           # 仙石秀久

    # === 1582 (本能寺の変前夜) ===
    ("1582", "hida"): "off_kanamori_nagachika",           # 金森長近
    ("1582", "shima"): "off_kuki_yoshitaka",              # 九鬼嘉隆
    ("1582", "izumi"): "off_hachiya_yoritaka",            # 蜂屋頼隆
    ("1582", "kawachi"): "off_katagiri_katsumoto",        # 片桐且元
    ("1582", "inaba"): "off_miyabe_keijun",               # 宮部継潤
    ("1582", "nagato"): "off_kobayakawa_takakage",        # 小早川隆景

    # === 1560 (桶狭間) ===
    ("1560", "suo"): "off_kikkawa_motoharu",              # 吉川元春
    ("1560", "nagato"): "off_kobayakawa_takakage",        # 小早川隆景
    ("1560", "chikugo"): "off_tachibana_dosetsu",         # 立花道雪
    ("1560", "inaba"): "off_yamana_suketoyo",             # 山名祐豊

    # === 1570 (信長包囲網) ===
    ("1570", "suo"): "off_kikkawa_motoharu",              # 吉川元春
    ("1570", "nagato"): "off_kobayakawa_takakage",        # 小早川隆景
    ("1570", "inaba"): "off_yamana_suketoyo",             # 山名祐豊
    ("1570", "sanuki"): "off_sengoku_hidehisa",           # 仙石秀久

    # === 1028 (平忠常の乱) ===
    ("1028", "kazusa"): "off_taira_tadatsune",            # 平忠常
    ("1028", "north_shinano"): "off_minamoto_yorinobu",   # 源頼信
    ("1028", "south_shinano"): "off_minamoto_yoriyoshi",  # 源頼義
    ("1028", "ise"): "off_taira_naokata",                 # 平直方
    ("1028", "rikuchu"): "off_abe_yoritoki",              # 安倍頼時
    ("1028", "bungo"): "off_otomo_yoshimune_proto",       # 大友氏祖

    # === 1056 (前九年の役) ===
    ("1056", "awa_boshu"): "off_taira_tsuneharu",         # 平常晴
    ("1056", "kai"): "off_minamoto_yoriyoshi",            # 源頼義
    ("1056", "north_shinano"): "off_minamoto_yoshiie",    # 源義家
    ("1056", "south_shinano"): "off_minamoto_yoshimitsu", # 源義光
    ("1056", "ise"): "off_taira_masahira",                # 平正衡
    ("1056", "mino"): "off_minamoto_kunimoto",            # 源国基
}

# Apply historical overrides
applied = 0
for (sid, prov), off_id in historical_overrides.items():
    # verify off_id exists in officers
    off = officers_by_id.get(off_id) or officers_by_name.get(off_id)
    if off:
        scen_h = hist_govs.setdefault(sid, {})
        scen_h[prov] = off['id']
        applied += 1
    else:
        print(f"Warning: officer {off_id} not found!")

print(f"Applied {applied} historical governor overrides!")

# Also auto-fill any remaining empty provinces where a matching alive officer with defaultProv exists
auto_filled = 0
for scen in scenarios:
    sid = str(scen['id'])
    year = scen['year']
    owners = scen.get('owners', {})
    scen_h = hist_govs.setdefault(sid, {})
    
    alive = [o for o in officers if o.get('birthYear') is not None and o.get('deathYear') is not None and (year - o['birthYear'] >= 15) and (year <= o['deathYear'])]
    alive_by_prov = {}
    for al in alive:
        dp = al.get('defaultProv')
        if dp:
            alive_by_prov.setdefault(dp, []).append(al)
            
    assigned_in_scen = set(scen_h.values())
    
    for p, o in owners.items():
        if not o: continue
        # if empty and not capital
        cm = clan_master.get(o)
        is_cap = (cm and cm.get('capital') == p) or (list(owners.keys())[0] == p and list(owners.values())[0] == o)
        if not scen_h.get(p) and not is_cap:
            # find an alive officer matching defaultProv and clanId if possible, or just defaultProv
            cands = alive_by_prov.get(p, [])
            cand = next((c for c in cands if c.get('clanId') == o and c['id'] not in assigned_in_scen), None)
            if not cand:
                cand = next((c for c in cands if c['id'] not in assigned_in_scen and not c.get('isDaimyo')), None)
            if cand:
                scen_h[p] = cand['id']
                assigned_in_scen.add(cand['id'])
                auto_filled += 1

print(f"Auto-filled {auto_filled} additional historical governors with matched alive officers!")

# Write updated hist_govs back to js/data.js
new_gov_json = json.dumps(hist_govs, ensure_ascii=False, indent=2)
new_text = text[:idx_gov + len('window.SCENARIO_HISTORICAL_GOVERNORS = ')] + new_gov_json + text[end_idx_gov-1:]

with open('js/data.js', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Saved updated SCENARIO_HISTORICAL_GOVERNORS to js/data.js successfully.")
