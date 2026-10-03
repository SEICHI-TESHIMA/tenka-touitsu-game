# -*- coding: utf-8 -*-
"""
js/data.js 単体での150年生存シミュレーション検証スクリプト
外部データセットに依存せず、data.js のデータのみで全シナリオの全大名家が150年間生存することを検証する
"""
import sys
import json
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

def parse_section(prefix, next_prefix):
    start = text.find(prefix) + len(prefix)
    end = text.find(next_prefix, start) if next_prefix else len(text)
    body = text[start:end].strip()
    last_b = max(body.rfind(']'), body.rfind('}'))
    return json.loads(body[:last_b+1])

officers_master = parse_section('window.OFFICERS_MASTER =', 'window.SCENARIOS_DATA =')
scenarios = parse_section('window.SCENARIOS_DATA =', 'window.CLAN_MASTER_DATA =')
clans = parse_section('window.CLAN_MASTER_DATA =', 'window.CLAN_ABILITIES =')

print(f"Loaded {len(officers_master)} officers from js/data.js")
print(f"Loaded {len(scenarios)} scenarios from js/data.js")
print(f"Loaded {len(clans)} clans from js/data.js")

# ID重複チェック
seen_ids = set()
duplicates = []
for o in officers_master:
    oid = o['id']
    if oid in seen_ids:
        duplicates.append(oid)
    seen_ids.add(oid)

if duplicates:
    print(f"WARNING: Duplicate IDs found: {len(duplicates)}: {duplicates[:5]}")
else:
    print("SUCCESS: No duplicate officer IDs found in js/data.js!")

# 真田十勇士の存在確認
sanada_braves = [
    "off_sarutobi_sasuke", "off_kirigakure_saizo", "off_miyoshi_seikai", "off_miyoshi_isa",
    "off_anayama_kosuke", "off_yuri_kamanosuke", "off_kakei_juzo", "off_unno_rokuro",
    "off_nezu_jinpachi", "off_mochizuki_rokuro"
]
found_braves = [o for o in officers_master if o['id'] in sanada_braves]
print(f"Sanada Ten Braves found in data.js: {len(found_braves)} / 10")
for b in found_braves:
    print(f"  - {b['name']} ({b['clanId']}, B:{b['birthYear']} - D:{b['deathYear']}, 統率:{b['military']}, 知略:{b['intel']})")

# 150年生存シミュレーション
officers_by_clan = defaultdict(list)
for o in officers_master:
    cid = o.get('clanId')
    if cid:
        officers_by_clan[cid].append(o)

failing_cases = []

for scen in scenarios:
    scen_id = str(scen['id'])
    scen_year = scen['year']
    target_year = scen_year + 150
    title = scen['title']
    owners = sorted(list(set(scen.get('owners', {}).values()) | set(p['id'] for p in scen.get('playables', []))))
    
    for cid in owners:
        offs = officers_by_clan.get(cid, [])
        active_at_start = [o for o in offs if o['birthYear'] is not None and o['deathYear'] is not None and scen_year >= o['birthYear'] + 15 and scen_year <= o['deathYear']]
        
        missing_years = []
        for y in range(scen_year, target_year + 1):
            act = [o for o in offs if o['birthYear'] is not None and o['deathYear'] is not None and y >= o['birthYear'] + 15 and y <= o['deathYear']]
            if not act:
                missing_years.append(y)
                
        if missing_years or not active_at_start:
            cname = clans.get(cid, {}).get('family', cid)
            failing_cases.append({
                'scen_id': scen_id,
                'scen_year': scen_year,
                'target_year': target_year,
                'scen_title': title,
                'clan_id': cid,
                'clan_name': cname,
                'has_start_leader': len(active_at_start) > 0,
                'missing_count': len(missing_years),
                'missing_spans': [(missing_years[0], missing_years[-1])] if missing_years else [],
                'all_missing_years': missing_years[:10],
                'existing': [f"{o['name']}({o.get('birthYear')}-{o.get('deathYear')})" for o in sorted(offs, key=lambda x: x.get('birthYear', 0))]
            })

print("\n=======================================================")
print(f"VERIFICATION RESULT: {len(failing_cases)} failing cases remaining in js/data.js!")
print("=======================================================")

if failing_cases:
    for fc in failing_cases:
        print(f"Scenario {fc['scen_id']} ({fc['scen_year']}->{fc['target_year']}) Clan {fc['clan_id']:15s} ({fc['clan_name']}): startLeader={fc['has_start_leader']}, missing={fc['missing_spans']}")
        print(f"   Missing sample: {fc['all_missing_years']}")
else:
    print(f"SUCCESS! ALL {len(scenarios)} SCENARIOS AND ALL CLANS SURVIVE 150 YEARS WITH 100% COVERAGE!")
