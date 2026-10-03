import sys
import json
import re
import glob
from verify_merges import merges

sys.stdout.reconfigure(encoding='utf-8')

# Collect all merged IDs
all_merged_ids = {}
for canon, m_list, desc in merges:
    for mid in m_list:
        all_merged_ids[mid] = (canon, desc)

# Also add the newly discovered duplicates:
# 松平治郷: off_edo_matsue_1743_167 vs off_edo_matsdaira_harusato
all_merged_ids['off_edo_matsue_1743_167'] = ('off_edo_matsdaira_harusato', '松平治郷 (1751-1818)')
# 松平頼真: off_matsudaira_yoritaka vs off_edo_matsdaira_yorizane
all_merged_ids['off_matsudaira_yoritaka'] = ('off_edo_matsdaira_yorizane', '松平頼真 (1743-1800)')

print(f"Total merged IDs to check: {len(all_merged_ids)}")

files_to_check = glob.glob('js/*.js') + glob.glob('*.html')

ref_counts = {mid: [] for mid in all_merged_ids}

for fpath in files_to_check:
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    for mid in all_merged_ids:
        # Count occurrences outside OFFICERS_MASTER
        # Let's count in file
        matches = [m.start() for m in re.finditer(re.escape(mid), content)]
        if matches:
            ref_counts[mid].append((fpath, len(matches)))

print("\n--- References of merged IDs across codebase ---")
for mid, refs in ref_counts.items():
    if refs:
        canon, desc = all_merged_ids[mid]
        print(f"{mid} -> {canon} ({desc}):")
        for fpath, cnt in refs:
            print(f"    {fpath}: {cnt} times")
