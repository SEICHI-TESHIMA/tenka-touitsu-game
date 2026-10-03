# -*- coding: utf-8 -*-
import sys
import json
from collections import Counter
from test_survival_simulation import combined_officers

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

prefix = 'window.OFFICERS_MASTER ='
next_prefix = 'window.SCENARIOS_DATA ='
start = text.find(prefix) + len(prefix)
end = text.find(next_prefix, start)
body = text[start:end].strip()
last_b = max(body.rfind(']'), body.rfind('}'))
merged_officers = json.loads(body[:last_b+1])

print(f"combined_officers count: {len(combined_officers)}")
print(f"merged_officers count: {len(merged_officers)}")

combined_ids = [o['id'] for o in combined_officers]
c = Counter(combined_ids)
duplicates_in_combined = [k for k, v in c.items() if v > 1]
print(f"Duplicate IDs in combined_officers: {len(duplicates_in_combined)}")

# 失敗している氏族（soma, takeda, chiba, kakizaki, satake など）のID重複を調べる
for target_clan in ['soma', 'takeda', 'chiba', 'kakizaki', 'satake', 'mito']:
    print(f"\n--- Clan {target_clan} ---")
    c_offs = [o for o in combined_officers if o.get('clanId') == target_clan]
    m_offs = [o for o in merged_officers if o.get('clanId') == target_clan]
    print(f"In combined: {len(c_offs)} officers, In merged: {len(m_offs)} officers")
    
    # combined で重複している武将
    c_cids = Counter([o['id'] for o in c_offs])
    for oid, cnt in c_cids.items():
        if cnt > 1:
            matches = [o for o in c_offs if o['id'] == oid]
            print(f"Duplicate in combined: {oid}")
            for m in matches:
                print(f"   {m['name']} B:{m.get('birthYear')} D:{m.get('deathYear')}")
