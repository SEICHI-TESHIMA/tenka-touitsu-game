import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

scenarios = json.loads(text[text.find('window.SCENARIOS_DATA =') + len('window.SCENARIOS_DATA ='):text.find('window.CLAN_MASTER_DATA =')].strip().rstrip(';'))
officers = json.loads(text[text.find('window.OFFICERS_MASTER =') + len('window.OFFICERS_MASTER ='):text.find('window.SCENARIOS_DATA =')].strip().rstrip(';'))

target_names = [
    "菊池氏祖・則隆", "豊後国司・大友氏", "京極持清", "六角定頼", "小笠原政秀", "松平元康", "豊臣秀吉", "島津忠恒", "徳川家康", "京極高氏", "佐々木導誉", "佐々木道誉", "六角時信", "六角氏頼", "小笠原貞宗"
]

print("=== CHECKING SPECIFIC TARGET NAMES IN OFFICERS_MASTER ===")
for o in officers:
    for tn in target_names:
        if tn in o['name'] or (o.get('id') and tn in o['id']):
            print(f"Match {tn}: id={o.get('id')}, name={o.get('name')}, clanId={o.get('clanId')}, birth={o.get('birthYear')}, death={o.get('deathYear')}")

print("\n=== CHECKING PLAYABLES FOR 1560, 1590, 1614, 1637 ===")
for sid in ['1560', '1590', '1614', '1637']:
    s = next(sc for sc in scenarios if str(sc['id']) == sid)
    print(f"[{sid}] playables:")
    for p in s.get('playables', []):
        if p['id'] in ['matsudaira', 'tokugawa', 'toyotomi', 'shimazu']:
            print(f"  {p}")
