import re
import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Find SCENARIOS_DATA
m = re.search(r'window\.SCENARIOS_DATA\s*=\s*(\[.*?\]);\s*(?:window|\n\s*const|\n\s*let|\n\s*var|\n\s*function)', text, re.DOTALL)
if m:
    scen_str = m.group(1)
    print("Found SCENARIOS_DATA block, length:", len(scen_str))
else:
    # let's find start
    idx = text.find('window.SCENARIOS_DATA')
    print("SCENARIOS_DATA at idx:", idx)
    # search lines
    lines = text[idx:idx+5000].splitlines()
    for l in lines[:30]:
        print(l)
