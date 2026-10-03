with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.findall(r'"id":\s*"(?:north_shinano|south_shinano|shinano)"[^}]+?"name":\s*"([^"]+)"', text)
print("Shinano province definitions:", m)

idx = text.find('INITIAL_PROVINCES')
sub = text[idx:idx+3000]
for line in sub.splitlines():
    if 'shinano' in line.lower():
        print(line)
