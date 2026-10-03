import json
import re

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('window.OFFICERS_MASTER = [')
end_idx = text.find('\n];', start_idx) + 2
officers = json.loads(text[start_idx + len('window.OFFICERS_MASTER = '):end_idx])

start_idx = text.find('window.PROVINCES_DATA = [')
end_idx = text.find('\n];', start_idx) + 2
provs = json.loads(text[start_idx + len('window.PROVINCES_DATA = '):end_idx])
valid_provs = set(p['id'] for p in provs)

out = []

suspicious_officers = []
for o in officers:
    name = o.get('name', '')
    oid = o.get('id', '')
    lore = o.get('lore', '')
    comment = o.get('comment', '')
    
    if any(k in name for k in ['門人', '残党', '門弟', '農民', '商人', '足軽', '兵士', '配下', '子孫']):
        suspicious_officers.append((oid, name, "generic name"))
    elif '大塩' in name:
        suspicious_officers.append((oid, name, f"oshio (born {o.get('birthYear')}, died {o.get('deathYear')})"))
    elif any(k in comment for k in ['架空', '完遂']) or any(k in lore for k in ['百五十年を超えて家名を全うした', '名跡を明治', '天保の義挙から百年を超えて家を守った']):
        suspicious_officers.append((oid, name, f"generated lineage: {lore[:40]}"))

out.append(f"Total officers: {len(officers)}")
out.append(f"Suspicious / generated officers found: {len(suspicious_officers)}")
for s in suspicious_officers:
    out.append(str(s))

invalid_prov_officers = []
for o in officers:
    dp = o.get('defaultProv')
    if dp and dp not in valid_provs:
        invalid_prov_officers.append((o['id'], o['name'], dp))

out.append(f"\nOfficers with invalid defaultProv: {len(invalid_prov_officers)}")
for inv in invalid_prov_officers:
    out.append(str(inv))

with open('survey_results_utf8.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(out))

print("Saved survey_results_utf8.txt successfully.")
