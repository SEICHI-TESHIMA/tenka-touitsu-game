import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'window\.OFFICERS_MASTER\s*=\s*(\[.*?\]);', text, re.DOTALL)
officers = json.loads(m.group(1))
officer_by_id = {o['id']: o for o in officers}

# Candidates for merge: (canonical_id, [merged_ids], reason)
# Let's define the comprehensive mapping of duplicate officers to merge
merges = [
    # 1. 小野好古
    ('off_ono_yoshifuru', ['off_ononoyoshifuru'], '小野好古 (884-968)'),
    
    # 2. 平清盛
    ('off_taira_kiyomori', ['off_sadamori_kiyomori'], '平清盛 (1118-1181)'),
    
    # 3. 千葉常胤
    ('off_chiba_tsunetane', ['off_masakado_succ_5'], '千葉常胤 (1118-1201)'),
    
    # 4. 源義朝
    ('off_minamoto_yoshitomo', ['off_tsunemoto_succ_4'], '源義朝 (1123-1160)'),
    
    # 5. 大友能直
    ('off_otomo_yoshinao_early_bridge', ['off_dm_otomo_1156'], '大友能直 (1165-1223)'),
    
    # 6. 平宗盛
    ('off_taira_munemori', ['off_sadamori_munemori'], '平宗盛 (1147-1185)'),
    
    # 7. 源頼朝
    ('off_minamoto_yoritomo', ['off_tsunemoto_yoritomo'], '源頼朝 (1147-1199)'),
    
    # 8. 河野通信
    ('off_kono_michinobu_early', ['off_dm_kono_1180'], '河野通信 (1156-1223)'),
    
    # 9. 佐竹秀義
    ('off_satake_hideyoshi', ['off_dm_satake_1180'], '佐竹秀義 (1184-1272)'),
    
    # 10. 後鳥羽上皇 / 後鳥羽天皇
    ('off_gotoba_in', ['off_heian_court_gotoba', 'off_gotoba_in_as_goshirakawa'], '後鳥羽上皇/後鳥羽天皇 (1180-1239)'),
    
    # 11. 千葉胤綱
    ('off_dm_chiba_1221', ['off_masakado_succ_7'], '千葉胤綱 (1191-1246)'),
    
    # 12. 島津忠久
    ('off_shimazu_proto_tadahisa', ['off_dm_shimazu_1221'], '島津忠久 (1157-1227)'),
    
    # 13. 佐々木道誉
    ('off_sasaki_doyo', ['off_sasakidoyo'], '佐々木道誉 (1306-1373)'),
    
    # 14. 小笠原貞宗
    ('off_ogasawara_sadamune', ['off_dm_ogasawara_1331'], '小笠原貞宗 (1292-1347)'),
    
    # 15. 毛利元春
    ('off_mori_motoharu', ['off_dm_mori_1331'], '毛利元春 (1323-1385)'),
    
    # 16. 大友貞宗
    ('off_otomo_sadamune', ['off_dm_otomo_1331'], '大友貞宗 (1280-1334)'),
    
    # 17. 里見義胤
    ('off_satomi_yoshitane', ['off_dm_satomi_1331'], '里見義胤 (1330-1390)'),
    
    # 18. 島津貞久
    ('off_shimazu_sadahisa', ['off_dm_shimazu_1331'], '島津貞久 (1269-1363)'),
    
    # 19. 六角氏頼
    ('off_rokkaku_ujiyori', ['off_dm_rokkaku_1336'], '六角氏頼 (1326-1370)'),
    
    # 20. 大内弘世
    ('off_ouchi_hiroyo', ['off_dm_ouchi_1336'], '大内弘世 (1325-1380)'),
    
    # 21. 小笠原政秀
    ('off_ogasawara_masahide', ['off_dm_ogasawara_1350'], '小笠原政秀 (1440-1500)'),
    
    # 22. 北条時行
    ('off_hojo_tokiyuki', ['off_hojo_tokiyuki_early'], '北条時行 (1318-1353)'),
    
    # 23. 六角満高
    ('off_rokkaku_mitsutaka', ['off_dm_rokkaku_1438'], '六角満高 (1369-1416)'),
    
    # 24. 佐竹義人
    ('off_satake_yoshijin', ['off_dm_satake_1438'], '佐竹義人 (1400-1468)'),
    
    # 25. 長宗我部文兼
    ('off_chosokabe_fumikane', ['off_dm_chosokabe_1438'], '長宗我部文兼 (1425-1485)'),
    
    # 26. 島津久豊
    ('off_shimazu_hisatoyo', ['off_dm_shimazu_1438'], '島津久豊 (1373-1425)'),
    
    # 27. 六角高頼
    ('off_rokkaku_takayori', ['off_dm_rokkaku_1467'], '六角高頼 (1462-1520)'),
    
    # 28. 神保長誠
    ('off_jinbo_nagasei', ['off_dm_jinbo_1467'], '神保長誠 (1437-1492 / 1495-1545)'),
    
    # 29. 足利義稙
    ('off_ashikaga_yoshitane', ['off_dm_ashikaga_1495'], '足利義稙 (1466-1523)'),
    
    # 30. 富樫泰高
    ('off_togashi_yasutaka', ['off_dm_togashi_1495'], '富樫泰高 (1475-1535)'),
    
    # 31. 山名政豊
    ('off_yamana_masatoyo', ['off_dm_yamana_1495'], '山名政豊 (1441-1499)'),
    
    # 32. 浅井亮政
    ('off_azai_sukemasa_add', ['off_dm_azai_1495'], '浅井亮政 (1491-1542)'),
    
    # 33. 村上政清
    ('off_murakami_masakiyo', ['off_dm_murakami_1495', 'off_dm_murakami_1467'], '村上政清 (1420-1480)'),
    
    # 34. 細川政元
    ('off_hosokawa_masamoto', ['off_dm_hosokawa_1495'], '細川政元 (1466-1507)'),
    
    # 35. 毛利吉就
    ('off_mori_yoshinari', ['off_succ_mori_1668_95'], '毛利吉就 (1668-1694)'),
    
    # 36. 北畠晴具
    ('off_kitabatake_harutomo', ['off_dm_kitabatake_1546'], '北畠晴具 (1503-1563)'),
    
    # 37. 大友義鑑
    ('off_otomo_yoshiaki_early', ['off_dm_otomo_1546'], '大友義鑑 (1502-1550)'),
    
    # 38. 黒田長知
    ('off_kuroda_nagashige', ['off_dm_fukuoka_kuroda_1868'], '黒田長知 (1838-1902)'),
    
    # 39. 細川護久
    ('off_hosokawa_morihisa', ['off_dm_kumamoto_hosokawa_1868'], '細川護久 (1839-1893)'),
    
    # 40. 京極高次
    ('off_kyogoku_takatsugu', ['off_kyogoku_takatsugu_add'], '京極高次 (1563-1609)'),
    
    # 41. 島津忠重
    ('off_shimazu_tadashige', ['off_shimazu_tadashige_m'], '島津忠重 (1886-1968)'),
    
    # 42. 藤原文元
    ('off_fujiwara_fumimoto', ['off_fujiwara_fuminori'], '藤原文元 (898-941)'),
    
    # 43. 大蔵春実
    ('off_okura_haruzane', ['off_okura_harumi'], '大蔵春実 (895-978)'),
    
    # 44. 源頼家
    ('off_minamoto_yoriie', ['off_tsunemoto_yoriie'], '源頼家 (1182-1204)'),
    
    # 45. 源実朝
    ('off_minamoto_sanetomo', ['off_minamoto_sanetomo_yoshitomo', 'off_tsunemoto_sanetomo'], '源実朝 (1192-1219)'),
    
    # 46. 足利泰氏
    ('off_ashikaga_yasuuhi', ['off_ashikaga_yasuuji_yoshitomo'], '足利泰氏 (1216-1270)'),
    
    # 47. 足利家時
    ('off_ashikaga_ietoki', ['off_ashikaga_ietoki_yoshitomo'], '足利家時 (1250-1284)'),
    
    # 48. 島津忠時
    ('off_shimazu_tadatoki', ['off_shimazu_proto_tadayoshi'], '島津忠時 (1202-1272)'),
    
    # 49. 小山朝政
    ('off_koyama_tomomasa', ['off_oyama_tomomasa'], '小山朝政 (1158-1238)'),
    
    # 50. 上杉定勝
    ('off_uesugi_sadakatsu', ['off_uesugi_sadakatsu_succ'], '上杉定勝 (1604-1655)'),
    
    # 51. 千葉成胤
    ('off_chiba_shigeta', ['off_masakado_succ_6'], '千葉成胤 (1155-1218)'),
    
    # 52. 宇都宮興綱
    ('off_utsunomiya_okitsuna', ['off_utsunomiya_okitsuna_early_bridge'], '宇都宮興綱 (1512-1536)'),
    
    # 53. 相馬昌胤
    ('off_soma_masatane', ['off_soma_masatane_early_bridge'], '相馬昌胤 (1658-1728)'),
    
    # 54. 蜂須賀正子
    ('off_hachisuka_masako', ['off_hachisuka_masako_early'], '蜂須賀正子 (1935-2035)'),
    
    # 55. 黒田長成
    ('off_kuroda_nagashige_fuk', ['off_kuroda_nagaaki'], '黒田長成 (1867-1939)'),
    
    # 56. 細川護立
    ('off_hosokawa_moritatsu', ['off_hosokawa_moritaka'], '細川護立 (1883-1970)'),
    
    # 57. 武田信吉
    ('off_takeda_nobuyoshi_koke', ['off_takeda_nobuyoshi_early_bridge'], '武田信吉 (1580-1603)'),
    
    # 58. 細川護成
    ('off_hosokawa_morinari', ['off_hosokawa_morishige'], '細川護成 (1868-1914)'),
    
    # 59. 後嵯峨天皇 / 後嵯峨上皇
    ('off_gosaga_in', ['off_succ_gotoba_in_1220_18', 'off_gosaga_in_bridge'], '後嵯峨上皇/後嵯峨天皇 (1220-1272)'),
    
    # 60. 佐竹義明
    ('off_succ_satake_1723_148', ['off_satake_yoshitsugu_bridge'], '佐竹義明 (1723-1765)'),
    
    # 61. 蜂須賀家政
    ('off_hachisuka_iemasa', ['off_succ2_hachisuka_1558'], '蜂須賀家政 (1558-1639)'),
    
    # 62. 松前崇広
    ('off_matsumae_takahiro_bridge', ['off_succ2_kakizaki_1829'], '松前崇広 (1829-1880)'),
    
    # 63. 板倉勝静
    ('off_itakura_katsukiyo', ['off_edo_tokugawa_1823_32'], '板倉勝静 (1816-1889)'),
    
    # 64. 山田方谷
    ('off_yamada_hokoku', ['off_edo_tokugawa_1805_33'], '山田方谷 (1805-1877)'),
    
    # 65. 細川斉護
    ('off_hosokawa_narimori', ['off_edo_kumamoto_hosokawa_1804_212'], '細川斉護 (1804-1860)'),
    
    # 66. 黒田長溥
    ('off_kuroda_nagahiro_han', ['off_kuroda_nagahiro2'], '黒田長溥 (1811-1887)'),
    
    # 67. 小栗忠順
    ('off_oguri_kozukenosuke', ['off_oguri_tadasumi'], '小栗忠順 (1827-1868)'),
    
    # 68. 阿部正方
    ('off_abe_masakata', ['off_abe_masato'], '阿部正方 (1848-1867)'),
    
    # 69. 毛利秀元
    ('off_mori_hidemoto', ['off_mori_hidenori'], '毛利秀元 (1579-1650)'),
    
    # 70. 佐々木広綱 / 佐佐木広綱
    ('off_sasaki_hirotsuna', ['off_sasaki_hirotuna'], '佐々木広綱 (1175-1221)'),
    
    # 71. 片倉景綱 (小十郎)
    ('off_katakura_kagenori', ['off_katakura_kojuro'], '片倉景綱/片倉小十郎 (1557-1615)'),
    
    # 72. 武田信政 / 武田信正 (高家武田氏)
    ('off_takeda_nobumasa_koke', ['off_succ_takeda_1630_194'], '武田信政/武田信正 (1630-1690)'),
    
    # 73. 後白河天皇 / 後白河院
    ('off_goshirakawa_in', ['off_heian_court_goshira'], '後白河天皇/後白河院 (1127-1192)'),
    
    # 74. 細川藤孝 (幽斎)
    ('off_hosokawa_fujitaka', ['off_hosokawa_yusai_add'], '細川藤孝/細川幽斎 (1534-1610)'),
    
    # 75. 徳川秀忠 / 松平秀忠
    ('off_tokugawa_hidetada', ['off_matsudaira_hidetada_m'], '徳川秀忠/松平秀忠 (1579-1632)'),
    
    # 76. 徳川家光 / 松平家光
    ('off_tokugawa_iemitsu', ['off_matsudaira_iemitsu_m'], '徳川家光/松平家光 (1604-1651)'),
    
    # 77. 徳川家綱 / 松平家綱
    ('off_tokugawa_ietsuna', ['off_matsudaira_ietsuna_m'], '徳川家綱/松平家綱 (1641-1680)'),
    
    # 78. 徳川綱吉 / 松平綱吉
    ('off_tokugawa_tsunayoshi', ['off_matsudaira_tsunayoshi_m'], '徳川綱吉/松平綱吉 (1646-1709)'),
    
    # 79. 徳川家宣 / 松平家宣
    ('off_tokugawa_ienobu', ['off_matsudaira_yoshinobu_m'], '徳川家宣/松平家宣 (1662-1712)'),
    
    # 80. 穴山信君 (梅雪)
    ('off_anayama_baisetsu', ['off_succ_takeda_1541_192'], '穴山信君/穴山梅雪 (1541-1582)'),
]

print(f"Total planned merge groups: {len(merges)}")

# Check that all IDs exist
missing_canonical = []
missing_merged = []
for canon, merged_list, desc in merges:
    if canon not in officer_by_id:
        missing_canonical.append((canon, desc))
    for mid in merged_list:
        if mid not in officer_by_id:
            missing_merged.append((mid, desc))

print(f"Missing canonical: {len(missing_canonical)} -> {missing_canonical}")
print(f"Missing merged: {len(missing_merged)} -> {missing_merged}")
