import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Load officers, modify off_toyotomi_hideyoshi name, save back
officers_str = text[text.find('window.OFFICERS_MASTER =') + len('window.OFFICERS_MASTER ='):text.find('window.SCENARIOS_DATA =')].strip().rstrip(';')
officers = json.loads(officers_str)

for o in officers:
    if o['id'] == 'off_toyotomi_hideyoshi':
        o['name'] = '豊臣秀吉'
        print(f"Updated officer {o['id']} name to {o['name']}")

new_officers_json = json.dumps(officers, ensure_ascii=False, indent=2)

s_idx = text.find('window.OFFICERS_MASTER =') + len('window.OFFICERS_MASTER =')
e_idx = text.find('window.SCENARIOS_DATA =')

new_text = text[:s_idx] + " " + new_officers_json + ";\n\n" + text[e_idx:]

with open('js/data.js', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Saved updated OFFICERS_MASTER to js/data.js")
