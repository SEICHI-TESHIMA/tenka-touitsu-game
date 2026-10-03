# -*- coding: utf-8 -*-
"""
各シナリオの城代国に対して、史実の国司・城代・守護・武将候補をマッピングするための調査スクリプト。
"""
import json

with open('scenarios_jodai_scan.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

current_scen = None
scen_jodai = {}
for line in lines:
    if line.startswith('Scenario ['):
        parts = line.split(']')
        scen_id = parts[0].replace('Scenario [', '').strip()
        scen_title = parts[1].split(':')[0].strip()
        current_scen = (scen_id, scen_title)
        scen_jodai[current_scen] = []
    elif line.strip().startswith('- '):
        # - mikawa (三河) [勢力: heian_court]
        parts = line.strip().split()
        pid = parts[1]
        pname = parts[2].replace('(', '').replace(')', '')
        cid = parts[4].replace(']', '')
        scen_jodai[current_scen].append((pid, pname, cid))

with open('jodai_detailed_analysis.txt', 'w', encoding='utf-8') as out:
    for (sid, stitle), provs in scen_jodai.items():
        if provs:
            out.write(f"=== {sid} {stitle} ({len(provs)} 件) ===\n")
            for pid, pname, cid in provs:
                out.write(f"  {pid:14} {pname:6} (勢力: {cid})\n")
            out.write("\n")

print("Wrote jodai_detailed_analysis.txt")
