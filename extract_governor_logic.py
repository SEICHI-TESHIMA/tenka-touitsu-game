# -*- coding: utf-8 -*-
with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# search for governor / jodai assignment logic
lines = text.splitlines()
governor_lines = []
for i, line in enumerate(lines):
    if '城代' in line or 'governor' in line.lower() or 'SCENARIO_HISTORICAL_GOVERNORS' in line or 'switchScenario' in line or 'initGame' in line:
        governor_lines.append(i)

with open('app_governor_logic.txt', 'w', encoding='utf-8') as out:
    # let's look at regions where SCENARIO_HISTORICAL_GOVERNORS or 城代 appears
    blocks = set()
    for l in lines:
        if 'SCENARIO_HISTORICAL_GOVERNORS' in l or '城代' in l:
            idx = lines.index(l)
            start = max(0, idx - 30)
            end = min(len(lines), idx + 40)
            blocks.add((start, end))
    
    # merge overlapping blocks
    sorted_blocks = sorted(list(blocks))
    merged = []
    for s, e in sorted_blocks:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append([s, e])
            
    for s, e in merged:
        out.write(f"--- Lines {s+1} to {e} ---\n")
        for i in range(s, e):
            out.write(f"{i+1}: {lines[i]}\n")
        out.write("\n")

print("Wrote app_governor_logic.txt")
