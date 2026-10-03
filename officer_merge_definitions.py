import sys
import json
import re

# Complete mapping of duplicate officer IDs to canonical officer ID:
# (canonical_id, [merged_ids], new_name_or_none, description)
OFFICER_MERGES = [
    # 1. 小野好古 (884-968)
    ('off_ono_yoshifuru', ['off_ononoyoshifuru'], None, '小野好古'),
    
    # 2. 平清盛 (1118-1181)
    ('off_taira_kiyomori', ['off_sadamori_kiyomori'], None, '平清盛'),
    
    # 3. 千葉常胤 (1118-1201)
    ('off_chiba_tsunetane', ['off_masakado_succ_5'], None, '千葉常胤'),
    
    # 4. 源義朝 (1123-1160)
    ('off_minamoto_yoshitomo', ['off_tsunemoto_succ_4'], None, '源義朝'),
    
    # 5. 大友能直 (1165-1223)
    ('off_otomo_yoshinao_early_bridge', ['off_dm_otomo_1156'], None, '大友能直'),
    
    # 6. 平宗盛 (1147-1185)
    ('off_taira_munemori', ['off_sadamori_munemori'], None, '平宗盛'),
    
    # 7. 源頼朝 (1147-1199)
    ('off_minamoto_yoritomo', ['off_tsunemoto_yoritomo'], None, '源頼朝'),
    
    # 8. 河野通信 (1156-1223)
    ('off_kono_michinobu_early', ['off_dm_kono_1180'], None, '河野通信'),
    
    # 9. 佐竹秀義 (1184-1272)
    ('off_satake_hideyoshi', ['off_dm_satake_1180'], None, '佐竹秀義'),
    
    # 10. 後鳥羽上皇 / 後鳥羽天皇 (1180-1239)
    ('off_gotoba_in', ['off_heian_court_gotoba', 'off_gotoba_in_as_goshirakawa'], None, '後鳥羽上皇/後鳥羽天皇'),
    
    # 11. 千葉胤綱 (1191-1246)
    ('off_dm_chiba_1221', ['off_masakado_succ_7'], None, '千葉胤綱'),
    
    # 12. 島津忠久 (1157-1227)
    ('off_shimazu_proto_tadahisa', ['off_dm_shimazu_1221'], None, '島津忠久'),
    
    # 13. 佐々木道誉 (1306-1373)
    ('off_sasaki_doyo', ['off_sasakidoyo'], None, '佐々木道誉'),
    
    # 14. 小笠原貞宗 (1292-1347)
    ('off_ogasawara_sadamune', ['off_dm_ogasawara_1331'], None, '小笠原貞宗'),
    
    # 15. 毛利元春 (1323-1385)
    ('off_mori_motoharu', ['off_dm_mori_1331'], None, '毛利元春'),
    
    # 16. 大友貞宗 (1280-1334)
    ('off_otomo_sadamune', ['off_dm_otomo_1331'], None, '大友貞宗'),
    
    # 17. 里見義胤 (1330-1390)
    ('off_satomi_yoshitane', ['off_dm_satomi_1331'], None, '里見義胤'),
    
    # 18. 島津貞久 (1269-1363)
    ('off_shimazu_sadahisa', ['off_dm_shimazu_1331'], None, '島津貞久'),
    
    # 19. 六角氏頼 (1326-1370)
    ('off_rokkaku_ujiyori', ['off_dm_rokkaku_1336'], None, '六角氏頼'),
    
    # 20. 大内弘世 (1325-1380)
    ('off_ouchi_hiroyo', ['off_dm_ouchi_1336'], None, '大内弘世'),
    
    # 21. 小笠原政秀 (1440-1500)
    ('off_ogasawara_masahide', ['off_dm_ogasawara_1350'], None, '小笠原政秀'),
    
    # 22. 北条時行 (1318-1353)
    ('off_hojo_tokiyuki', ['off_hojo_tokiyuki_early'], None, '北条時行'),
    
    # 23. 六角満高 (1369-1416)
    ('off_rokkaku_mitsutaka', ['off_dm_rokkaku_1438'], None, '六角満高'),
    
    # 24. 佐竹義人 (1400-1468)
    ('off_satake_yoshijin', ['off_dm_satake_1438'], None, '佐竹義人'),
    
    # 25. 長宗我部文兼 (1425-1485)
    ('off_chosokabe_fumikane', ['off_dm_chosokabe_1438'], None, '長宗我部文兼'),
    
    # 26. 島津久豊 (1373-1425)
    ('off_shimazu_hisatoyo', ['off_dm_shimazu_1438'], None, '島津久豊'),
    
    # 27. 六角高頼 (1462-1520)
    ('off_rokkaku_takayori', ['off_dm_rokkaku_1467'], None, '六角高頼'),
    
    # 28. 神保長誠 (1437-1492 / 1495-1545)
    ('off_jinbo_nagasei', ['off_dm_jinbo_1467'], None, '神保長誠'),
    
    # 29. 足利義稙 (1466-1523)
    ('off_ashikaga_yoshitane', ['off_dm_ashikaga_1495'], None, '足利義稙'),
    
    # 30. 富樫泰高 (1475-1535)
    ('off_togashi_yasutaka', ['off_dm_togashi_1495'], None, '富樫泰高'),
    
    # 31. 山名政豊 (1441-1499)
    ('off_yamana_masatoyo', ['off_dm_yamana_1495'], None, '山名政豊'),
    
    # 32. 浅井亮政 (1491-1542)
    ('off_azai_sukemasa_add', ['off_dm_azai_1495'], None, '浅井亮政'),
    
    # 33. 村上政清 (1420-1480)
    ('off_murakami_masakiyo', ['off_dm_murakami_1495', 'off_dm_murakami_1467'], None, '村上政清'),
    
    # 34. 細川政元 (1466-1507)
    ('off_hosokawa_masamoto', ['off_dm_hosokawa_1495'], None, '細川政元'),
    
    # 35. 毛利吉就 (1668-1694)
    ('off_mori_yoshinari', ['off_succ_mori_1668_95'], None, '毛利吉就'),
    
    # 36. 北畠晴具 (1503-1563)
    ('off_kitabatake_harutomo', ['off_dm_kitabatake_1546'], None, '北畠晴具'),
    
    # 37. 大友義鑑 (1502-1550)
    ('off_otomo_yoshiaki_early', ['off_dm_otomo_1546'], None, '大友義鑑'),
    
    # 38. 黒田長知 (1838-1902)
    ('off_kuroda_nagashige', ['off_dm_fukuoka_kuroda_1868'], None, '黒田長知'),
    
    # 39. 細川護久 (1839-1893)
    ('off_hosokawa_morihisa', ['off_dm_kumamoto_hosokawa_1868'], None, '細川護久'),
    
    # 40. 京極高次 (1563-1609)
    ('off_kyogoku_takatsugu', ['off_kyogoku_takatsugu_add'], None, '京極高次'),
    
    # 41. 島津忠重 (1886-1968)
    ('off_shimazu_tadashige', ['off_shimazu_tadashige_m'], None, '島津忠重'),
    
    # 42. 藤原文元 (898-941)
    ('off_fujiwara_fumimoto', ['off_fujiwara_fuminori'], None, '藤原文元'),
    
    # 43. 大蔵春実 (895-978)
    ('off_okura_haruzane', ['off_okura_harumi'], None, '大蔵春実'),
    
    # 44. 源頼家 (1182-1204)
    ('off_minamoto_yoriie', ['off_tsunemoto_yoriie'], None, '源頼家'),
    
    # 45. 源実朝 (1192-1219)
    ('off_minamoto_sanetomo', ['off_minamoto_sanetomo_yoshitomo', 'off_tsunemoto_sanetomo'], None, '源実朝'),
    
    # 46. 足利泰氏 (1216-1270)
    ('off_ashikaga_yasuuhi', ['off_ashikaga_yasuuji_yoshitomo'], None, '足利泰氏'),
    
    # 47. 足利家時 (1250-1284)
    ('off_ashikaga_ietoki', ['off_ashikaga_ietoki_yoshitomo'], None, '足利家時'),
    
    # 48. 島津忠時 (1202-1272)
    ('off_shimazu_tadatoki', ['off_shimazu_proto_tadayoshi'], None, '島津忠時'),
    
    # 49. 小山朝政 (1158-1238)
    ('off_koyama_tomomasa', ['off_oyama_tomomasa'], None, '小山朝政'),
    
    # 50. 上杉定勝 (1604-1655)
    ('off_uesugi_sadakatsu', ['off_uesugi_sadakatsu_succ'], None, '上杉定勝'),
    
    # 51. 千葉成胤 (1155-1218)
    ('off_chiba_shigeta', ['off_masakado_succ_6'], None, '千葉成胤'),
    
    # 52. 宇都宮興綱 (1512-1536)
    ('off_utsunomiya_okitsuna', ['off_utsunomiya_okitsuna_early_bridge'], None, '宇都宮興綱'),
    
    # 53. 相馬昌胤 (1658-1728)
    ('off_soma_masatane', ['off_soma_masatane_early_bridge'], None, '相馬昌胤'),
    
    # 54. 蜂須賀正子 (1935-2035)
    ('off_hachisuka_masako', ['off_hachisuka_masako_early'], None, '蜂須賀正子'),
    
    # 55. 黒田長成 (1867-1939)
    ('off_kuroda_nagashige_fuk', ['off_kuroda_nagaaki'], None, '黒田長成'),
    
    # 56. 細川護立 (1883-1970)
    ('off_hosokawa_moritatsu', ['off_hosokawa_moritaka'], None, '細川護立'),
    
    # 57. 武田信吉 (1580-1603)
    ('off_takeda_nobuyoshi_koke', ['off_takeda_nobuyoshi_early_bridge'], None, '武田信吉'),
    
    # 58. 細川護成 (1868-1914)
    ('off_hosokawa_morinari', ['off_hosokawa_morishige'], None, '細川護成'),
    
    # 59. 後嵯峨天皇 / 後嵯峨上皇 (1220-1272)
    ('off_gosaga_in', ['off_succ_gotoba_in_1220_18', 'off_gosaga_in_bridge'], None, '後嵯峨上皇/後嵯峨天皇'),
    
    # 60. 佐竹義明 (1723-1765)
    ('off_succ_satake_1723_148', ['off_satake_yoshitsugu_bridge'], None, '佐竹義明'),
    
    # 61. 蜂須賀家政 (1558-1639)
    ('off_hachisuka_iemasa', ['off_succ2_hachisuka_1558'], None, '蜂須賀家政'),
    
    # 62. 松前崇広 (1829-1880)
    ('off_matsumae_takahiro_bridge', ['off_succ2_kakizaki_1829'], None, '松前崇広'),
    
    # 63. 板倉勝静 (1816-1889)
    ('off_itakura_katsukiyo', ['off_edo_tokugawa_1823_32'], None, '板倉勝静'),
    
    # 64. 山田方谷 (1805-1877)
    ('off_yamada_hokoku', ['off_edo_tokugawa_1805_33'], None, '山田方谷'),
    
    # 65. 細川斉護 (1804-1860)
    ('off_hosokawa_narimori', ['off_edo_kumamoto_hosokawa_1804_212'], None, '細川斉護'),
    
    # 66. 黒田長溥 (1811-1887)
    ('off_kuroda_nagahiro_han', ['off_kuroda_nagahiro2'], None, '黒田長溥'),
    
    # 67. 小栗忠順 (1827-1868)
    ('off_oguri_kozukenosuke', ['off_oguri_tadasumi'], None, '小栗忠順'),
    
    # 68. 阿部正方 (1848-1867)
    ('off_abe_masakata', ['off_abe_masato'], None, '阿部正方'),
    
    # 69. 毛利秀元 (1579-1650)
    ('off_mori_hidemoto', ['off_mori_hidenori'], None, '毛利秀元'),
    
    # 70. 佐々木広綱 / 佐佐木広綱 (1175-1221)
    ('off_sasaki_hirotsuna', ['off_sasaki_hirotuna'], None, '佐々木広綱'),
    
    # 71. 片倉景綱 (小十郎) (1557-1615)
    ('off_katakura_kagenori', ['off_katakura_kojuro'], None, '片倉景綱(小十郎)'),
    
    # 72. 武田信政 / 武田信正 (1630-1690)
    ('off_takeda_nobumasa_koke', ['off_succ_takeda_1630_194'], None, '武田信政/武田信正'),
    
    # 73. 後白河天皇 / 後白河院 (1127-1192)
    ('off_goshirakawa_in', ['off_heian_court_goshira'], None, '後白河天皇/後白河院'),
    
    # 74. 細川藤孝 (幽斎) (1534-1610)
    ('off_hosokawa_fujitaka', ['off_hosokawa_yusai_add'], None, '細川藤孝(幽斎)'),
    
    # 75. 徳川秀忠 / 松平秀忠 (1579-1632)
    ('off_tokugawa_hidetada', ['off_matsudaira_hidetada_m'], None, '徳川秀忠/松平秀忠'),
    
    # 76. 徳川家光 / 松平家光 (1604-1651)
    ('off_tokugawa_iemitsu', ['off_matsudaira_iemitsu_m'], None, '徳川家光/松平家光'),
    
    # 77. 徳川家綱 / 松平家綱 (1641-1680)
    ('off_tokugawa_ietsuna', ['off_matsudaira_ietsuna_m'], None, '徳川家綱/松平家綱'),
    
    # 78. 徳川綱吉 / 松平綱吉 (1646-1709)
    ('off_tokugawa_tsunayoshi', ['off_matsudaira_tsunayoshi_m'], None, '徳川綱吉/松平綱吉'),
    
    # 79. 徳川家宣 / 松平家宣 (1662-1712)
    ('off_tokugawa_ienobu', ['off_matsudaira_yoshinobu_m'], None, '徳川家宣/松平家宣'),
    
    # 80. 穴山信君 (梅雪) (1541-1582)
    ('off_anayama_baisetsu', ['off_succ_takeda_1541_192'], None, '穴山信君(梅雪)'),
    
    # 81. 松平治郷 (不昧) (1751-1818)
    ('off_edo_matsudaira_harusato', ['off_edo_matsue_1743_167'], None, '松平治郷(不昧)'),
    
    # 82. 松平頼真 (1743-1800)
    ('off_edo_matsudaira_yorizane', ['off_matsudaira_yoritaka'], None, '松平頼真'),
    
    # 83. 藤原基衡 (1105-1157)
    ('off_fujiwara_motohira', ['off_dm_fujiwara_hiraizumi_1156'], None, '藤原基衡'),
    
    # 84. 源為義 (1096-1156)
    ('off_minamoto_tameyoshi', ['off_tsunemoto_succ_3'], None, '源為義'),
    
    # 85. 宗清則 (1120-1159)
    ('off_dm_so_1156', ['off_dm_so_1180'], None, '宗清則'),
]

# Rename mapping for dummy successors who had conflicting ancestor names
OFFICER_RENAMES = {
    'off_kiyohara_succ_3': ('清原頼衡', '出羽の豪族清原氏の後裔として血脈を繋いだ。'),
    'off_iehira_succ_2': ('清原兼衡', '出羽山中に隠棲し、清原氏の命脈を保った。'),
    'off_hidesato_succ_3': ('藤原公清', '秀郷流藤原氏の正統として武蔵・下野の基盤を支えた。'),
    'off_kiyohara_succ_4': ('清原長衡', '鎌倉幕府のもとで出羽の在地領主として家名を保った。'),
    'off_succ_satake_1325_141': ('佐竹義直', '南北朝期に常陸守護佐竹氏の一門として家を支えた。'),
}
