# -*- coding: utf-8 -*-
"""
各時代の武将一覧をチェックして、不自然な人物・架空人物をチェックするスクリプト。
"""
with open('officers_by_era.txt', 'r', encoding='utf-8') as f:
    text = f.read()

sections = text.split('=== ERA: ')
for s in sections[1:]:
    lines = s.strip().splitlines()
    era_title = lines[0]
    print(f"Checking {era_title}...")
    for l in lines[1:]:
        # check for weird words
        for kw in ['酋長', '豪族', '郡司', '国司', 'dummy', 'fake', '十勇士', '先祖', '大友氏', '氏族']:
            if kw in l:
                print(f"  FOUND {kw}: {l.strip()}")

print("Done era check.")
