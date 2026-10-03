with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'id:\s*[\'"]([^\'"]+)[\'"].*?name:\s*[\'"]([^\'"]+)[\'"]', text)
for m in matches:
    if '1866' in m[0] or '1866' in m[1] or '薩長' in m[1]:
        print(m)

# Find 1866 in text
idx = 0
while True:
    idx = text.find('1866', idx)
    if idx == -1:
        break
    print("Found '1866' at", idx, ":", repr(text[idx-20:idx+40]))
    idx += 4
