import json, sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

def parse_section(prefix, next_prefix):
    start = text.find(prefix) + len(prefix)
    end = text.find(next_prefix, start) if next_prefix else len(text)
    body = text[start:end].strip()
    last_b = max(body.rfind(']'), body.rfind('}'))
    return json.loads(body[:last_b+1])

provs = parse_section('window.PROVINCES_DATA =', 'window.OFFICERS_MASTER =')
officers_master = parse_section('window.OFFICERS_MASTER =', 'window.SCENARIOS_DATA =')
scenarios = parse_section('window.SCENARIOS_DATA =', 'window.CLAN_MASTER_DATA =')
clans = parse_section('window.CLAN_MASTER_DATA =', 'window.CLAN_ABILITIES =')
hist_govs = parse_section('window.SCENARIO_HISTORICAL_GOVERNORS =', 'window.CLAN_CAPITAL_PROVINCES =')
capitals = parse_section('window.CLAN_CAPITAL_PROVINCES =', None)

# Prepare updates to hist_govs
govs_updates = {
    '1584': {
        'tsugaru': 'off_tsugaru_tamenobu', # 津軽為信
        'mutsu': 'off_kita_nobuchika',     # 北信愛
        'kozuke': 'off_hojo_ujikuni',      # 北条氏邦
        'shimousa': 'off_chiba_kunitane',  # 千葉邦胤
        'kazusa': 'off_hojo_ujinori',      # 北条氏規
        'noto': 'off_cho_tsuratatsu',      # 長連龍
        'tango': 'off_hosokawa_yusai_add', # 細川幽斎
        'tamba': 'off_maeda_geni',         # 前田玄以
        'tajima': 'off_yamana_toyokuni',   # 山名豊国
        'kawachi': 'off_succ2_hachisuka_1558', # 蜂須賀家政
        'izumi': 'off_konishi_yukinaga',   # 小西行長
        'wakasa': 'off_asano_nagamasa',    # 浅野長政
        'hida': 'off_kanamori_arishige',   # 金森可重
        'iyo': 'off_succ_kono_1555_74',    # 河野通直
        'izumo': 'off_kikkawa_hiroie',     # 吉川広家
        'buzen': 'off_takahashi_shoun',    # 高橋紹運
        'chikuzen': 'off_tachibana_dosetsu', # 立花道雪
        'higo': 'off_succ_sagara_1570_136' # 相良頼房
    },
    '1587': {
        'tsugaru': 'off_tsugaru_tamenobu', # 津軽為信
        'mutsu': 'off_kita_nobuchika',     # 北信愛
        'kozuke': 'off_hojo_ujikuni',      # 北条氏邦
        'shimousa': 'off_chiba_kunitane',  # 千葉邦胤
        'kazusa': 'off_hojo_ujinori',      # 北条氏規
        'south_shinano': 'off_okubo_tadayo', # 大久保忠世
        'etchu': 'off_dm_maeda_1600',      # 前田利長
        'noto': 'off_cho_tsuratatsu',      # 長連龍
        'echizen': 'off_niwa_nagashige',   # 丹羽長重
        'wakasa': 'off_asano_nagamasa',    # 浅野長政
        'hida': 'off_kanamori_arishige',   # 金森可重
        'totomi': 'off_ii_naomasa',        # 井伊直政
        'mikawa': 'off_sakai_tadatsugu',   # 酒井忠次
        'kai': 'off_torii_mototada',       # 鳥居元忠
        'tango': 'off_hosokawa_tadaoki',   # 細川忠興
        'tamba': 'off_maeda_geni',         # 前田玄以
        'kawachi': 'off_succ2_hachisuka_1558', # 蜂須賀家政
        'izumi': 'off_konishi_yukinaga',   # 小西行長
        'sanuki': 'off_sengoku_hidehisa',  # 仙石秀久
        'iyo': 'off_kato_yoshiaki',        # 加藤嘉明
        'buzen': 'off_kuroda_kanbei',      # 黒田官兵衛
        'chikuzen': 'off_kobayakawa_takakage', # 小早川隆景
        'chikugo': 'off_tachibana_muneshige', # 立花宗茂
        'higo': 'off_kato_kiyomasa'        # 加藤清正
    },
    '1590': {
        'mutsu': 'off_kita_nobuchika'      # 北信愛 (津軽為信から修正)
    },
    '1592': {
        'mutsu': 'off_kita_nobuchika',     # 北信愛
        'iwaki': 'off_soma_yoshitane',     # 相馬義胤
        'kazusa': 'off_honda_tadakatsu',   # 本多忠勝
        'awa_boshu': 'off_succ2_satomi_1573', # 里見義康
        'suruga': 'off_nakamura_kazuuji',  # 中村一氏
        'kai': 'off_asano_nagamasa',       # 浅野長政
        'south_shinano': 'off_ishikawa_kazumasa', # 石川数正
        'etchu': 'off_dm_maeda_1600',      # 前田利長
        'noto': 'off_cho_tsuratatsu',      # 長連龍
        'totomi': 'off_yamauchi_kazutoyo', # 山内一豊
        'mikawa': 'off_tanaka_yoshimasa',  # 田中吉政
        'ise': 'off_todo_takatora',        # 藤堂高虎
        'south_omi': 'off_kyogoku_takatsugu', # 京極高次
        'yamato': 'off_mashita_nagamori',  # 増田長盛
        'tamba': 'off_maeda_geni',         # 前田玄以
        'tango': 'off_hosokawa_tadaoki',   # 細川忠興
        'tajima': 'off_koide_yoshimasa',   # 小出吉政
        'harima': 'off_ikeda_terumasa',    # 池田輝政
        'sanuki': 'off_sengoku_hidehisa',  # 仙石秀久
        'awa_shikoku': 'off_succ2_hachisuka_1558', # 蜂須賀家政
        'iyo': 'off_kato_yoshiaki',        # 加藤嘉明
        'bungo': 'off_dm_otomo_1600',      # 大友義統
        'hyuga': 'off_succ_ito_1550_45'    # 伊東祐兵
    },
    '1600': {
        'mutsu': 'off_kita_nobuchika'      # 北信愛 (津軽為信から修正)
    }
}

# Apply test updates
for sid, updates in govs_updates.items():
    if sid not in hist_govs:
        hist_govs[sid] = {}
    for pid, gid in updates.items():
        hist_govs[sid][pid] = gid

print("Testing 1584 scenario with updates:")
scen_1584 = next(s for s in scenarios if str(s['id']) == '1584')
for pid in ['tsugaru', 'mutsu', 'kozuke', 'shimousa', 'kazusa', 'noto', 'tango', 'tamba', 'tajima', 'kawachi', 'izumi']:
    gov_id = hist_govs['1584'].get(pid)
    off = next((o for o in officers_master if o['id'] == gov_id), None)
    print(f"  {pid:12s}: owner={scen_1584['owners'].get(pid):10s} -> gov={off['name'] if off else gov_id} ({gov_id})")

