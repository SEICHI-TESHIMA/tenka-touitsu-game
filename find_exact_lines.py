with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.finditer(r'"id":\s*"([^"]+)"', text)
for m in matches:
    eid = m.group(1)
    if any(k in eid for k in ['1031', 'dannoura', 'honnouji', '1028', '1087', 'fujikawa', 'ichinotani', 'tenguto']):
        line_num = text[:m.start()].count('\n') + 1
        print(f"{eid:35} line {line_num}")
