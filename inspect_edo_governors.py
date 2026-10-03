import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

hist_govs = json.loads(text[text.find('window.SCENARIO_HISTORICAL_GOVERNORS =') + len('window.SCENARIO_HISTORICAL_GOVERNORS ='):text.find('window.CLAN_CAPITAL_PROVINCES =')].strip().rstrip(';'))
officers = json.loads(text[text.find('window.OFFICERS_MASTER =') + len('window.OFFICERS_MASTER ='):text.find('window.SCENARIOS_DATA =')].strip().rstrip(';'))

officers_dict = {o['id']: o for o in officers}

print("=== GOVERNORS FOR SCENARIO 1651 (慶安の変) ===")
govs_1651 = hist_govs.get('1651', {})
for prov, gid in sorted(govs_1651.items()):
    off = officers_dict.get(gid)
    name = off['name'] if off else gid
    clan = off.get('clanId') if off else 'unknown'
    print(f"  {prov:15}: {name:15} ({gid}) [clan: {clan}]")

print(f"\nTotal in 1651: {len(govs_1651)}")

print("\n=== GOVERNORS FOR SCENARIO 1853 (ペリー来航) ===")
govs_1853 = hist_govs.get('1853', {})
for prov, gid in sorted(list(govs_1853.items())[:15]):
    off = officers_dict.get(gid)
    name = off['name'] if off else gid
    clan = off.get('clanId') if off else 'unknown'
    print(f"  {prov:15}: {name:15} ({gid}) [clan: {clan}]")
print(f"Total in 1853: {len(govs_1853)}")
