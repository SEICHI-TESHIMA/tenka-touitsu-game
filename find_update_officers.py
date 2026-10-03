with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'updateActiveOfficers\s*\(', text)]
for idx in matches:
    lines = text[idx-100:idx+800].splitlines()
    print("--- MATCH ---")
    for l in lines[:20]:
        print(l)
