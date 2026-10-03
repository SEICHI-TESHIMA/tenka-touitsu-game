# -*- coding: utf-8 -*-
import sys
import json
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

# データセットのインポート
from dataset_heian import GROUP_HEIAN
from dataset_kamakura import GROUP_KAMAKURA
from dataset_nanbokucho import GROUP_NANBOKUCHO
from dataset_sengoku import GROUP_SENGOKU
from dataset_edo_bakumatsu import GROUP_EDO_BAKUMATSU
from dataset_major_clans_extended import GROUP_MAJOR_EXTENDED
from dataset_bakumatsu_fixes import ADDITIONAL_BAKUMATSU_FIXES
from dataset_final_precision import FINAL_PRECISION_FIXES
from dataset_comprehensive_fixes import COMPREHENSIVE_GAP_FIXES

all_new_officers = (
    GROUP_HEIAN +
    GROUP_KAMAKURA +
    GROUP_NANBOKUCHO +
    GROUP_SENGOKU +
    GROUP_EDO_BAKUMATSU +
    GROUP_MAJOR_EXTENDED +
    ADDITIONAL_BAKUMATSU_FIXES +
    FINAL_PRECISION_FIXES +
    COMPREHENSIVE_GAP_FIXES
)

print(f"Total new officers defined: {len(all_new_officers)}")

# 重複IDのチェック
seen_ids = set()
for o in all_new_officers:
    if o['id'] in seen_ids:
        print(f"ERROR: Duplicate new officer ID: {o['id']}")
    seen_ids.add(o['id'])

# 既存データのロード
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

# 新武将をデフォルト値で補完
formatted_new = []
for o in all_new_officers:
    formatted_new.append({
        "id": o["id"],
        "name": o["name"],
        "clanId": o["clanId"],
        "defaultProv": o.get("defaultProv", "yamashiro"),
        "military": o.get("military", 75),
        "politic": o.get("politic", 75),
        "intel": o.get("intel", 75),
        "era": o.get("era", "sengoku"),
        "skill": o.get("skill", ""),
        "comment": o.get("comment", ""),
        "lore": o.get("lore", ""),
        "birthYear": o["birthYear"],
        "deathYear": o["deathYear"],
        "isDaimyo": False,
        "isDead": False,
        "assignedProvId": None
    })

combined_officers = officers_master + formatted_new
print(f"Combined officers count: {len(combined_officers)}")

# シミュレーション実行
officers_by_clan = defaultdict(list)
for o in combined_officers:
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
        # シナリオ開始年時点で元服している武将がいるか？
        active_at_start = [o for o in offs if o['birthYear'] is not None and o['deathYear'] is not None and scen_year >= o['birthYear'] + 15 and scen_year <= o['deathYear']]
        
        # 毎年アクティブな武将がいるか？
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
print(f"SIMULATION RESULT: {len(failing_cases)} failing cases remaining!")
print("=======================================================")

if failing_cases:
    for fc in failing_cases:
        print(f"Scenario {fc['scen_id']} ({fc['scen_year']}->{fc['target_year']}) Clan {fc['clan_id']:15s} ({fc['clan_name']}): startLeader={fc['has_start_leader']}, missing={fc['missing_spans']}")
        print(f"   Missing sample: {fc['all_missing_years']}")
        print(f"   Existing: {fc['existing']}")
else:
    print("SUCCESS! ALL CLANS IN ALL 21 SCENARIOS SURVIVE 150 YEARS!")
