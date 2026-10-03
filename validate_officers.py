import json

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
hist_govs = parse_section('window.SCENARIO_HISTORICAL_GOVERNORS =', 'window.CLAN_CAPITAL_PROVINCES =')
capitals = parse_section('window.CLAN_CAPITAL_PROVINCES =', None)

off_by_id = {o['id']: o for o in officers_master}
off_by_name = {o['name']: o for o in officers_master}

def find_officer(query):
    if query in off_by_id:
        return off_by_id[query]
    if query in off_by_name:
        return off_by_name[query]
    for o in officers_master:
        if query in o['id'] or query in o['name']:
            return o
    return None

# Test finding all proposed officers
proposed_keys = [
    'off_tsugaru_tamenobu', 'off_kita_nobuchika', 'off_hojo_ujikuni', 'off_chiba_kunitane',
    'off_hojo_ujinori', 'off_cho_tsuratatsu', 'off_hosokawa_yusai_add', 'off_hosokawa_tadaoki',
    'off_maeda_geni', 'off_yamana_toyokuni', 'off_succ2_hachisuka_1558', 'off_konishi_yukinaga',
    'off_wakisaka_yasuharu', 'off_asano_nagamasa', 'off_kikkawa_hiroie', 'off_takahashi_joun',
    'off_tachibana_dosetsu', 'off_tachibana_muneshige', 'off_niiro_tadamoto', 'off_succ_sagara_1570_136',
    'off_maeda_toshinaga', 'off_niwa_nagashige', 'off_sengoku_hidehisa', 'off_kato_yoshiaki',
    'off_soma_yoshitane', 'off_honda_tadakatsu', 'off_nakamura_kazuuji', 'off_yamauchi_kazutoyo',
    'off_tanaka_yoshimasa', 'off_todo_takatora', 'off_kyogoku_takatsugu', 'off_mashita_nagamori',
    'off_asano_yoshinaga', 'off_koide_yoshimasa', 'off_ikeda_terumasa', 'off_succ_ito_1550_45'
]

print("Checking proposed officers existence:")
missing = []
for k in proposed_keys:
    o = find_officer(k)
    if o:
        print(f"  OK: {k:28s} -> {o['name']} ({o['birthYear']}-{o['deathYear']})")
    else:
        print(f"  MISSING: {k}")
        missing.append(k)

print(f"Total checked: {len(proposed_keys)}, Missing: {len(missing)}")

