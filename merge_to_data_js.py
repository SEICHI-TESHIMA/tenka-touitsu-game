# -*- coding: utf-8 -*-
"""
js/data.js に全追加武将を安全にマージ・更新するスクリプト
"""
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

from test_survival_simulation import all_new_officers

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

prefix = 'window.OFFICERS_MASTER ='
next_prefix = 'window.SCENARIOS_DATA ='

start = text.find(prefix) + len(prefix)
end = text.find(next_prefix, start)

body = text[start:end].strip()
last_b = max(body.rfind(']'), body.rfind('}'))
existing_officers = json.loads(body[:last_b+1])

print(f"Existing officers before merge: {len(existing_officers)}")

# マッピング作成
officers_dict = {o['id']: o for o in existing_officers}

added_count = 0
updated_count = 0

for o in all_new_officers:
    oid = o['id']
    formatted = {
        "id": o["id"],
        "name": o["name"],
        "clanId": o["clanId"],
        "defaultProv": o.get("defaultProv", "yamashiro"),
        "military": o.get("military", 75),
        "politic": o.get("politic", 75),
        "intel": o.get("intel", 75),
        "era": o.get("era", "sengoku"),
        "skill": o.get("skill", ""),
        "comment": o.get("comment", ""),
        "lore": o.get("lore", ""),
        "birthYear": o["birthYear"],
        "deathYear": o["deathYear"],
        "isDaimyo": o.get("isDaimyo", False),
        "isDead": o.get("isDead", False),
        "assignedProvId": o.get("assignedProvId", None)
    }
    
    if oid in officers_dict:
        # 既存武将を最新データで更新
        officers_dict[oid].update(formatted)
        updated_count += 1
    else:
        # 新規武将を追加
        officers_dict[oid] = formatted
        existing_officers.append(formatted)
        added_count += 1

print(f"Updated officers: {updated_count}")
print(f"Newly added officers: {added_count}")
print(f"Total officers after merge: {len(existing_officers)}")

# JSONフォーマットして js/data.js に書き戻す
# インデント2スペース
new_json = json.dumps(existing_officers, ensure_ascii=False, indent=2)

new_content = (
    text[:text.find(prefix)] +
    f"window.OFFICERS_MASTER = {new_json};\n\n" +
    text[text.find(next_prefix):]
)

with open('js/data.js', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Successfully written merged data to js/data.js!")
