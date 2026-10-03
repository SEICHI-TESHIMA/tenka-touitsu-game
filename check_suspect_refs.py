# -*- coding: utf-8 -*-
"""
削除候補の架空武将が、JSコード内で参照されているかをチェックするスクリプト。
"""
import re

suspect_ids = [
    'off_sarutobi_sasuke',
    'off_kirigakure_saizo',
    'off_miyoshi_seikai',
    'off_miyoshi_isa',
    'off_anayama_kosuke',
    'off_yuri_kamanosuke',
    'off_kakei_juzo',
    'off_unno_rokuro',
    'off_nezu_jinpachi',
    'off_mochizuki_rokuro',
    'off_dm_otomo_939',
    'off_dm_ezo_native_939',
    'off_dm_shimazu_proto_939',
    'off_ezo_ainu_chou2',
    'off_ezo_chief_3',
    'off_shimazu_proto_succ3'
]

files = ['js/data.js', 'js/app.js', 'js/historical_jodai.js']

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"=== Checking {fpath} ===")
    for sid in suspect_ids:
        matches = len(re.findall(re.escape(sid), content))
        if matches > 0:
            print(f"  {sid}: {matches} matches")

