# -*- coding: utf-8 -*-
with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.splitlines()
with open('suspect_occurrences.txt', 'w', encoding='utf-8') as out:
    for i, line in enumerate(lines):
        for name in ['猿飛佐助', '蝦夷酋長', '薩摩郡司']:
            if name in line:
                out.write(f"Line {i+1} [{name}]: {line.strip()[:150]}\n")

print("Wrote suspect_occurrences.txt")
