import json, sys

sys.stdout.reconfigure(encoding='utf-8')

# Read data.js
with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

def parse_section(prefix, next_prefix):
    start = text.find(prefix) + len(prefix)
    end = text.find(next_prefix, start) if next_prefix else len(text)
    body = text[start:end].strip()
    last_b = max(body.rfind(']'), body.rfind('}'))
    return json.loads(body[:last_b+1])

provs = parse_section('window.PROVINCES_DATA =', 'window.OFFICERS_MASTER =')
officers_master = parse_section('window.OFFICERS_MASTER =', 'window.SCENARIOS_DATA =')
scenarios = parse_section('window.SCENARIOS_DATA =', 'window.CLAN_MASTER_DATA =')
hist_govs = parse_section('window.SCENARIO_HISTORICAL_GOVERNORS =', 'window.CLAN_CAPITAL_PROVINCES =')
capitals = parse_section('window.CLAN_CAPITAL_PROVINCES =', None)

print("======================================================================")
print("1. VERIFICATION: TSUGARU TAMENOBU IN ALL SCENARIOS")
print("======================================================================")

for sid in ['1570', '1582', '1584', '1587', '1590', '1592', '1600', '1614']:
    scen = next(s for s in scenarios if str(s['id']) == sid)
    year = scen['year']
    title = scen['title']
    owners = scen.get('owners', {})
    tsugaru_owner = owners.get('tsugaru')
    mutsu_owner = owners.get('mutsu')
    govs = hist_govs.get(sid, {})
    tsugaru_gov = govs.get('tsugaru')
    mutsu_gov = govs.get('mutsu')
    
    # Check officer
    off = next(o for o in officers_master if o['id'] == 'off_tsugaru_tamenobu')
    is_alive = off['birthYear'] + 15 <= year <= off['deathYear']
    
    print(f"[{sid}] {year} {title}:")
    print(f"   tsugaru: owner={tsugaru_owner}, gov={tsugaru_gov}")
    print(f"   mutsu:   owner={mutsu_owner}, gov={mutsu_gov}")
    print(f"   Tsugaru Tamenobu alive: {is_alive} (birth:{off['birthYear']}, death:{off['deathYear']})")

print("\n======================================================================")
print("2. VERIFICATION: 1584 SCENARIO KEY OFFICERS")
print("======================================================================")
govs_1584 = hist_govs.get('1584', {})
scen_1584 = next(s for s in scenarios if str(s['id']) == '1584')
check_provs = [
    'tsugaru', 'mutsu', 'kozuke', 'shimousa', 'kazusa', 'noto', 'tango',
    'tamba', 'tajima', 'kawachi', 'izumi', 'wakasa', 'hida', 'iyo',
    'izumo', 'buzen', 'chikuzen', 'higo'
]
for pid in check_provs:
    owner = scen_1584['owners'].get(pid)
    gov_id = govs_1584.get(pid)
    gov_off = next((o for o in officers_master if o['id'] == gov_id), None)
    gov_name = gov_off['name'] if gov_off else gov_id
    print(f"  {pid:12s}: owner={owner:10s} | gov={gov_name:12s} ({gov_id})")

print("\n======================================================================")
print("3. VERIFICATION: 1587 SCENARIO KEY OFFICERS")
print("======================================================================")
govs_1587 = hist_govs.get('1587', {})
scen_1587 = next(s for s in scenarios if str(s['id']) == '1587')
for pid in ['tsugaru', 'mutsu', 'kozuke', 'shimousa', 'noto', 'tango', 'kawachi', 'izumi', 'buzen', 'chikuzen', 'chikugo', 'higo']:
    owner = scen_1587['owners'].get(pid)
    gov_id = govs_1587.get(pid)
    gov_off = next((o for o in officers_master if o['id'] == gov_id), None)
    gov_name = gov_off['name'] if gov_off else gov_id
    print(f"  {pid:12s}: owner={owner:10s} | gov={gov_name:12s} ({gov_id})")

print("\n======================================================================")
print("4. VERIFICATION: 1590 & 1600 MUTSU GOVERNOR (FIXED FROM TSUGARU)")
print("======================================================================")
for sid in ['1590', '1600']:
    scen = next(s for s in scenarios if str(s['id']) == sid)
    govs = hist_govs.get(sid, {})
    print(f"[{sid}] mutsu (owner:{scen['owners'].get('mutsu')}): gov={govs.get('mutsu')}")
    print(f"[{sid}] tsugaru (owner:{scen['owners'].get('tsugaru')}): gov={govs.get('tsugaru')}")

print("\n======================================================================")
print("5. VERIFICATION: 1592 SCENARIO KEY OFFICERS")
print("======================================================================")
govs_1592 = hist_govs.get('1592', {})
scen_1592 = next(s for s in scenarios if str(s['id']) == '1592')
for pid in ['tsugaru', 'mutsu', 'iwaki', 'kazusa', 'suruga', 'kai', 'noto', 'harima', 'tango', 'awa_shikoku']:
    owner = scen_1592['owners'].get(pid)
    gov_id = govs_1592.get(pid)
    gov_off = next((o for o in officers_master if o['id'] == gov_id), None)
    gov_name = gov_off['name'] if gov_off else gov_id
    print(f"  {pid:12s}: owner={owner:10s} | gov={gov_name:12s} ({gov_id})")

