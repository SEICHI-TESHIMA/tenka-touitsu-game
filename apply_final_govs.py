import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Load OFFICERS_MASTER
idx_off = text.find('window.OFFICERS_MASTER = [')
end_off = text.find('];', idx_off)
officers = json.loads(text[idx_off + len('window.OFFICERS_MASTER = '): end_off + 1])
existing_ids = set(o['id'] for o in officers)

# Add correct officers if not present
new_officers = [
    {
        "id": "off_hojo_tokinao_nagato",
        "name": "北条時直",
        "clanId": "hojo_kamakura",
        "defaultProv": "nagato",
        "military": 76, "politic": 74, "intel": 72,
        "era": "kamakura",
        "skill": "長門探題",
        "lore": "鎌倉幕府末期の探題。西国の軍事指揮と元寇後の西国防衛を統率した。",
        "birthYear": 1285, "deathYear": 1333, "isDaimyo": False
    },
    {
        "id": "off_sugawara_takasue",
        "name": "菅原孝標",
        "clanId": "heian_court",
        "defaultProv": "mimasaka",
        "military": 62, "politic": 80, "intel": 85,
        "era": "ancient",
        "skill": "更級受領",
        "lore": "平安中期の貴族・受領。上総介、常陸介、美作守。『更級日記』作者（菅原孝標女）の父。",
        "birthYear": 972, "deathYear": 1045, "isDaimyo": False
    },
    {
        "id": "off_minamoto_kunimoto",
        "name": "源国基",
        "clanId": "heian_court",
        "defaultProv": "nagato",
        "military": 74, "politic": 75, "intel": 72,
        "era": "ancient",
        "skill": "長門守",
        "lore": "清和源氏。長門守。白河院政期に西国受領として武威を振るった。",
        "birthYear": 1050, "deathYear": 1115, "isDaimyo": False
    }
]

added_count = 0
for off in new_officers:
    if off['id'] not in existing_ids:
        officers.append(off)
        existing_ids.add(off['id'])
        added_count += 1

print(f"Added {added_count} officers.")

new_off_json = json.dumps(officers, ensure_ascii=False, indent=2)
text = text[:idx_off + len('window.OFFICERS_MASTER = ')] + new_off_json + text[end_off + 1:]

# 2. Update SCENARIO_HISTORICAL_GOVERNORS
idx_gov = text.find('window.SCENARIO_HISTORICAL_GOVERNORS = {')
end_gov = text.find('};\n\n', idx_gov)
if end_gov == -1: end_gov = text.find('};', idx_gov)

gov_str = text[idx_gov + len('window.SCENARIO_HISTORICAL_GOVERNORS = '): end_gov + 1]
import re
cleaned_gov = re.sub(r'([a-zA-Z0-9_]+):', r'"\1":', gov_str)
hist_govs = json.loads(cleaned_gov)

# Fix 939
hist_govs.setdefault('939', {})['south_omi'] = 'off_taira_kanemori'  # 平兼盛 (910-991, 駿河守・山城介)

# Fix 1028
hist_govs.setdefault('1028', {})['south_omi'] = 'off_jd_024' # 藤原頼通
hist_govs['1028']['mimasaka'] = 'off_sugawara_takasue'
hist_govs['1028']['nagato'] = 'off_jd_028' # 藤原資平
hist_govs['1028']['oki'] = 'off_jd_024' # 藤原頼通

# Fix 1056
hist_govs.setdefault('1056', {})['south_omi'] = 'off_jd_024' # 藤原頼通
hist_govs['1056']['kawachi'] = 'off_jd_020' # 源頼義
hist_govs['1056']['mimasaka'] = 'off_jd_026' # 源頼綱
hist_govs['1056']['nagato'] = 'off_jd_028' # 藤原資平
hist_govs['1056']['oki'] = 'off_jd_025' # 藤原教通

# Fix 1087
hist_govs.setdefault('1087', {})['south_omi'] = 'off_jd_033' # 藤原宗忠
hist_govs['1087']['mimasaka'] = 'off_jd_034' # 源仲政
hist_govs['1087']['nagato'] = 'off_minamoto_kunimoto'
hist_govs['1087']['oki'] = 'off_jd_032' # 源重成

# Fix 1221: mutsu (nanbu) -> 南部光行 (off_nanbu_mitsuyuki)
# Let's find existing nanbu mitsuyuki ID
nanbu_mitsuyuki = next((o['id'] for o in officers if '南部光行' in o['name'] or 'nanbu_mitsuyuki' in o['id']), None)
if nanbu_mitsuyuki:
    hist_govs.setdefault('1221', {})['mutsu'] = nanbu_mitsuyuki

# Fix 1331: nagato (hojo_kamakura) -> 北条時直 (off_hojo_tokinao_nagato)
hist_govs.setdefault('1331', {})['nagato'] = 'off_hojo_tokinao_nagato'

# Fix 1333: bingo (ashikaga) -> 細川頼春 (off_hosokawa_yoriharu)
hosokawa_yoriharu = next((o['id'] for o in officers if '細川頼春' in o['name'] or 'hosokawa_yoriharu' in o['id']), None)
if hosokawa_yoriharu:
    hist_govs.setdefault('1333', {})['bingo'] = hosokawa_yoriharu

# Fix 1336: totomi (imagawa) -> 今川範国 (off_imagawa_norikuni)
imagawa_norikuni = next((o['id'] for o in officers if '今川範国' in o['name'] or 'imagawa_norikuni' in o['id']), None)
if imagawa_norikuni:
    hist_govs.setdefault('1336', {})['totomi'] = imagawa_norikuni

# Fix 1350: wakasa (shiba) -> 斯波高経 (off_shiba_takatsune)
shiba_takatsune = next((o['id'] for o in officers if '斯波高経' in o['name'] or 'shiba_takatsune' in o['id']), None)
if shiba_takatsune:
    hist_govs.setdefault('1350', {})['wakasa'] = shiba_takatsune

new_gov_json = json.dumps(hist_govs, ensure_ascii=False, indent=2)
text = text[:idx_gov + len('window.SCENARIO_HISTORICAL_GOVERNORS = ')] + new_gov_json + text[end_gov + 1:]

with open('js/data.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Successfully updated js/data.js with final historical governors!")
