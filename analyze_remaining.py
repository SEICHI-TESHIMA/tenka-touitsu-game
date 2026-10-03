# -*- coding: utf-8 -*-
import sys, json
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

from test_survival_simulation import combined_officers, scenarios, failing_cases

# Get unique clans that are failing
clan_gaps = defaultdict(lambda: defaultdict(set))
for fc in failing_cases:
    cid = fc['clan_id']
    for y in fc.get('all_missing_years', []):
        clan_gaps[cid][fc['scen_id']].add(y)

# For each clan, find ALL missing years across all scenarios
clan_all_missing = defaultdict(set)
for fc in failing_cases:
    cid = fc['clan_id']
    scen_yr = fc['scen_year']
    target_yr = fc['target_year']
    offs = [o for o in combined_officers if o.get('clanId') == cid]
    for y in range(scen_yr, target_yr + 1):
        act = [o for o in offs if o['birthYear'] is not None and o['deathYear'] is not None 
               and y >= o['birthYear'] + 15 and y <= o['deathYear']]
        if not act:
            clan_all_missing[cid].add(y)

for cid in sorted(clan_all_missing.keys()):
    offs = [o for o in combined_officers if o.get('clanId') == cid]
    sorted_offs = sorted(offs, key=lambda x: (x.get('birthYear', 0) or 0,))
    years = sorted(list(clan_all_missing[cid]))
    # compute spans
    spans = []
    if years:
        st = years[0]; prev = st
        for y in years[1:]:
            if y == prev + 1: prev = y
            else: spans.append((st, prev)); st = y; prev = y
        spans.append((st, prev))
    print(f"\n=== {cid} === Gaps: {spans}")
    for o in sorted_offs:
        by = o.get('birthYear')
        dy = o.get('deathYear')
        gp = by + 15 if by is not None else None
        print(f"  {o['name']:14s} B:{by} G:{gp} D:{dy} (id:{o['id']})")
