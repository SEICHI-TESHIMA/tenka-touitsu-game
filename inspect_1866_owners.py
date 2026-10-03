import json
import re

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

p_1866 = re.search(r'id:\s*[\'"]1866[\'"].*?provinces:\s*(\{.*?\})', text, re.DOTALL)
prov_str = p_1866.group(1)
prov_json_str = re.sub(r'([a-zA-Z0-9_]+):', r'"\1":', prov_str)
prov_1866 = json.loads(prov_json_str)
print('1866 unique owners:', sorted(list(set(prov_1866.values()))))
print('1866 north_shinano owner:', prov_1866.get('north_shinano'))
print('1866 musashi owner:', prov_1866.get('musashi'))
print('1866 yamashiro owner:', prov_1866.get('yamashiro'))
