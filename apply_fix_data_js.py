import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Load all sections
provs = json.loads(text[text.find('window.PROVINCES_DATA =') + len('window.PROVINCES_DATA ='):text.find('window.OFFICERS_MASTER =')].strip().rstrip(';'))
officers = json.loads(text[text.find('window.OFFICERS_MASTER =') + len('window.OFFICERS_MASTER ='):text.find('window.SCENARIOS_DATA =')].strip().rstrip(';'))
scenarios = json.loads(text[text.find('window.SCENARIOS_DATA =') + len('window.SCENARIOS_DATA ='):text.find('window.CLAN_MASTER_DATA =')].strip().rstrip(';'))
clans = json.loads(text[text.find('window.CLAN_MASTER_DATA =') + len('window.CLAN_MASTER_DATA ='):text.find('window.CLAN_ABILITIES =')].strip().rstrip(';'))
clan_abilities = json.loads(text[text.find('window.CLAN_ABILITIES =') + len('window.CLAN_ABILITIES ='):text.find('window.HISTORICAL_EVENTS_DATA =')].strip().rstrip(';'))
events = json.loads(text[text.find('window.HISTORICAL_EVENTS_DATA =') + len('window.HISTORICAL_EVENTS_DATA ='):text.find('window.HISTORICAL_CASTLE_CHANGES =')].strip().rstrip(';'))
castle_changes = json.loads(text[text.find('window.HISTORICAL_CASTLE_CHANGES =') + len('window.HISTORICAL_CASTLE_CHANGES ='):text.find('window.DAIMYO_LIFESPAN_DATA =')].strip().rstrip(';'))

s_idx = text.find('window.DAIMYO_LIFESPAN_DATA =') + len('window.DAIMYO_LIFESPAN_DATA =')
e_idx = text.find('window.SCENARIO_HISTORICAL_GOVERNORS =')
chunk = text[s_idx:e_idx].strip()
last_b = chunk.rfind('}')
lifespan_data = json.loads(chunk[:last_b+1])

hist_govs = json.loads(text[text.find('window.SCENARIO_HISTORICAL_GOVERNORS =') + len('window.SCENARIO_HISTORICAL_GOVERNORS ='):text.find('window.CLAN_CAPITAL_PROVINCES =')].strip().rstrip(';'))
capitals = json.loads(text[text.find('window.CLAN_CAPITAL_PROVINCES =') + len('window.CLAN_CAPITAL_PROVINCES ='):].strip().rstrip(';'))

# 1. Update officers
off_map = {o['id']: o for o in officers}

# Konishi Yukinaga -> toyotomi
if 'off_konishi_yukinaga' in off_map:
    off_map['off_konishi_yukinaga']['clanId'] = 'toyotomi'
    off_map['off_konishi_yukinaga']['defaultProv'] = 'izumi'

# Kuroda Nagamasa -> kuroda
if 'off_kuroda_nagamasa' in off_map:
    off_map['off_kuroda_nagamasa']['clanId'] = 'kuroda'
    off_map['off_kuroda_nagamasa']['defaultProv'] = 'chikuzen'

# Kuroda Kanbei -> kuroda
if 'off_kuroda_kanbei' in off_map:
    off_map['off_kuroda_kanbei']['clanId'] = 'kuroda'
    off_map['off_kuroda_kanbei']['defaultProv'] = 'buzen'

# Nabeshima Naoshige -> nabeshima
if 'off_nabeshima_naoshige' in off_map:
    off_map['off_nabeshima_naoshige']['clanId'] = 'nabeshima'
    off_map['off_nabeshima_naoshige']['defaultProv'] = 'hizen'

# Tachibana Muneshige -> tachibana
if 'off_tachibana_muneshige' in off_map:
    off_map['off_tachibana_muneshige']['clanId'] = 'tachibana'
    off_map['off_tachibana_muneshige']['defaultProv'] = 'chikugo'

# Hosokawa Yusai -> hosokawa
if 'off_hosokawa_yusai_add' in off_map:
    off_map['off_hosokawa_yusai_add']['clanId'] = 'hosokawa'
    off_map['off_hosokawa_yusai_add']['defaultProv'] = 'tango'

# 2. Update SCENARIO_HISTORICAL_GOVERNORS

# 1584年 小牧・長久手の戦い
if '1584' not in hist_govs:
    hist_govs['1584'] = {}
hist_govs['1584'].update({
    'tsugaru': 'off_tsugaru_tamenobu', # 津軽為信（南部配下）
    'mutsu': 'off_kita_nobuchika',     # 北信愛（南部配下）
    'kozuke': 'off_hojo_ujikuni',      # 北条氏邦（北条配下）
    'shimousa': 'off_chiba_kunitane',  # 千葉邦胤（北条配下）
    'kazusa': 'off_hojo_ujinori',      # 北条氏規（北条配下）
    'noto': 'off_cho_tsuratatsu',      # 長連龍（前田・豊臣配下）
    'tango': 'off_hosokawa_yusai_add', # 細川幽斎（豊臣配下）
    'tamba': 'off_maeda_geni',         # 前田玄以（豊臣配下）
    'tajima': 'off_yamana_toyokuni',   # 山名豊国（豊臣配下）
    'kawachi': 'off_succ2_hachisuka_1558', # 蜂須賀家政（豊臣配下）
    'izumi': 'off_konishi_yukinaga',   # 小西行長（豊臣配下）
    'wakasa': 'off_asano_nagamasa',    # 浅野長政（豊臣配下）
    'hida': 'off_kanamori_arishige',   # 金森可重（豊臣配下）
    'iyo': 'off_succ_kono_1555_74',    # 河野通直（長宗我部配下）
    'izumo': 'off_kikkawa_hiroie',     # 吉川広家（毛利配下）
    'buzen': 'off_takahashi_shoun',    # 高橋紹運（大友配下）
    'chikuzen': 'off_tachibana_dosetsu', # 立花道雪（大友配下）
    'higo': 'off_succ_sagara_1570_136' # 相良頼房（島津配下）
})

# 1587年 秀吉の九州征伐
if '1587' not in hist_govs:
    hist_govs['1587'] = {}
hist_govs['1587'].update({
    'tsugaru': 'off_tsugaru_tamenobu', # 津軽為信（南部配下）
    'mutsu': 'off_kita_nobuchika',     # 北信愛（南部配下）
    'kozuke': 'off_hojo_ujikuni',      # 北条氏邦（北条配下）
    'shimousa': 'off_chiba_kunitane',  # 千葉邦胤（北条配下）
    'kazusa': 'off_hojo_ujinori',      # 北条氏規（北条配下）
    'south_shinano': 'off_okubo_tadayo', # 大久保忠世（徳川配下）
    'etchu': 'off_dm_maeda_1600',      # 前田利長（豊臣配下）
    'noto': 'off_cho_tsuratatsu',      # 長連龍（豊臣配下）
    'echizen': 'off_niwa_nagashige',   # 丹羽長重（豊臣配下）
    'wakasa': 'off_asano_nagamasa',    # 浅野長政（豊臣配下）
    'hida': 'off_kanamori_arishige',   # 金森可重（豊臣配下）
    'totomi': 'off_ii_naomasa',        # 井伊直政（徳川配下）
    'mikawa': 'off_sakai_tadatsugu',   # 酒井忠次（徳川配下）
    'kai': 'off_torii_mototada',       # 鳥居元忠（徳川配下）
    'tango': 'off_hosokawa_tadaoki',   # 細川忠興（豊臣配下）
    'tamba': 'off_maeda_geni',         # 前田玄以（豊臣配下）
    'kawachi': 'off_succ2_hachisuka_1558', # 蜂須賀家政（豊臣配下）
    'izumi': 'off_konishi_yukinaga',   # 小西行長（豊臣配下）
    'sanuki': 'off_sengoku_hidehisa',  # 仙石秀久（豊臣配下）
    'iyo': 'off_kato_yoshiaki',        # 加藤嘉明（豊臣配下）
    'buzen': 'off_kuroda_kanbei',      # 黒田官兵衛（豊臣配下）
    'chikuzen': 'off_kobayakawa_takakage', # 小早川隆景（豊臣配下）
    'chikugo': 'off_tachibana_muneshige', # 立花宗茂（豊臣配下）
    'higo': 'off_kato_kiyomasa'        # 加藤清正（豊臣配下）
})

# 1590年 小田原征伐
if '1590' in hist_govs:
    # 陸奥は南部重臣・北信愛に修正（津軽為信は津軽本拠の大名）
    hist_govs['1590']['mutsu'] = 'off_kita_nobuchika'

# 1592年 文禄の役
if '1592' not in hist_govs:
    hist_govs['1592'] = {}
hist_govs['1592'].update({
    'mutsu': 'off_kita_nobuchika',     # 北信愛（南部配下）
    'iwaki': 'off_soma_yoshitane',     # 相馬義胤（伊達/豊臣配下）
    'kazusa': 'off_honda_tadakatsu',   # 本多忠勝（徳川配下）
    'awa_boshu': 'off_succ2_satomi_1573', # 里見義康（徳川配下）
    'suruga': 'off_nakamura_kazuuji',  # 中村一氏（豊臣配下）
    'kai': 'off_asano_nagamasa',       # 浅野長政（豊臣配下）
    'south_shinano': 'off_ishikawa_kazumasa', # 石川数正（豊臣配下）
    'etchu': 'off_dm_maeda_1600',      # 前田利長（豊臣配下）
    'noto': 'off_cho_tsuratatsu',      # 長連龍（豊臣配下）
    'totomi': 'off_yamauchi_kazutoyo', # 山内一豊（豊臣配下）
    'mikawa': 'off_tanaka_yoshimasa',  # 田中吉政（豊臣配下）
    'ise': 'off_todo_takatora',        # 藤堂高虎（豊臣配下）
    'south_omi': 'off_kyogoku_takatsugu', # 京極高次（豊臣配下）
    'yamato': 'off_mashita_nagamori',  # 増田長盛（豊臣配下）
    'tamba': 'off_maeda_geni',         # 前田玄以（豊臣配下）
    'tango': 'off_hosokawa_tadaoki',   # 細川忠興（豊臣配下）
    'tajima': 'off_koide_yoshimasa',   # 小出吉政（豊臣配下）
    'harima': 'off_ikeda_terumasa',    # 池田輝政（豊臣配下）
    'sanuki': 'off_sengoku_hidehisa',  # 仙石秀久（豊臣配下）
    'awa_shikoku': 'off_succ2_hachisuka_1558', # 蜂須賀家政（豊臣配下）
    'iyo': 'off_kato_yoshiaki',        # 加藤嘉明（豊臣配下）
    'bungo': 'off_dm_otomo_1600',      # 大友義統（豊臣配下）
    'hyuga': 'off_succ_ito_1550_45'    # 伊東祐兵（豊臣配下）
})

# 1600年 関ヶ原の戦い
if '1600' in hist_govs:
    # 陸奥は南部重臣・北信愛に修正（津軽為信は津軽本拠の大名）
    hist_govs['1600']['mutsu'] = 'off_kita_nobuchika'

# Write back data.js
out_text = f"""// 天下統一 - データベース定義 (Provinces, Officers, Scenarios, Clans)

window.PROVINCES_DATA = {json.dumps(provs, ensure_ascii=False, indent=2)};

window.OFFICERS_MASTER = {json.dumps(officers, ensure_ascii=False, indent=2)};

window.SCENARIOS_DATA = {json.dumps(scenarios, ensure_ascii=False, indent=2)};

window.CLAN_MASTER_DATA = {json.dumps(clans, ensure_ascii=False, indent=2)};

window.CLAN_ABILITIES = {json.dumps(clan_abilities, ensure_ascii=False, indent=2)};

window.HISTORICAL_EVENTS_DATA = {json.dumps(events, ensure_ascii=False, indent=2)};

window.HISTORICAL_CASTLE_CHANGES = {json.dumps(castle_changes, ensure_ascii=False, indent=2)};

window.DAIMYO_LIFESPAN_DATA = {json.dumps(lifespan_data, ensure_ascii=False, indent=2)};

// 各シナリオにおける時代考証・史実城代配置マッピング (全21シナリオ対応)
window.SCENARIO_HISTORICAL_GOVERNORS = {json.dumps(hist_govs, ensure_ascii=False, indent=2)};

window.CLAN_CAPITAL_PROVINCES = {json.dumps(capitals, ensure_ascii=False, indent=2)};
"""

with open('js/data.js', 'w', encoding='utf-8') as f:
    f.write(out_text)

print("Successfully updated js/data.js with new governors and officer adjustments!")

