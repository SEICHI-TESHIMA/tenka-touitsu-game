import json
import re

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

prov_match = re.search(r'window\.PROVINCES_DATA\s*=\s*(\[.*?\]);', text, re.DOTALL)
provs = set(p['id'] for p in json.loads(prov_match.group(1)))

clan_match = re.search(r'window\.CLAN_MASTER_DATA\s*=\s*(\{.*?\});\s*window\.CLAN_ABILITIES', text, re.DOTALL)
clans = json.loads(clan_match.group(1))

evt_match = re.search(r'window\.HISTORICAL_EVENTS_DATA\s*=\s*(\[.*?\]);\s*window\.HISTORICAL_CASTLE_CHANGES', text, re.DOTALL)
evts = json.loads(evt_match.group(1))

print("=== CHECKING ALL OWNERS IN HISTORICAL_EVENTS_DATA ===")
missing_clans = {}
for ev in evts:
    terr = ev.get('changes', {}).get('territory', {})
    for p, o in terr.items():
        if o not in clans:
            missing_clans.setdefault(o, []).append((ev['id'], ev.get('title'), p))

for o, occs in missing_clans.items():
    print(f"Missing clanId: '{o}' (count: {len(occs)})")
    for eid, title, p in occs:
        print(f"   Event: {eid} ({title}), prov: {p}")

print("\n=== CHECKING PROVINCE IDS ===")
invalid_provs = {}
for ev in evts:
    terr = ev.get('changes', {}).get('territory', {})
    for p, o in terr.items():
        if p not in provs:
            invalid_provs.setdefault(p, []).append((ev['id'], ev.get('title'), o))

for p, occs in invalid_provs.items():
    print(f"Invalid provId: '{p}' (count: {len(occs)})")
    for eid, title, o in occs:
        print(f"   Event: {eid} ({title}), owner: {o}")
