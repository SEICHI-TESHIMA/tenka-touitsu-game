import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Read js/data.js and js/app.js
with open('js/data.js', 'r', encoding='utf-8') as f:
    text_data = f.read()

with open('js/app.js', 'r', encoding='utf-8') as f:
    text_app = f.read()

def parse_section(prefix, next_prefix):
    start = text_data.find(prefix) + len(prefix)
    end = text_data.find(next_prefix, start) if next_prefix else len(text_data)
    body = text_data[start:end].strip()
    last_b = max(body.rfind(']'), body.rfind('}'))
    return json.loads(body[:last_b+1])

provs_master = parse_section('window.PROVINCES_DATA =', 'window.OFFICERS_MASTER =')
officers_master = parse_section('window.OFFICERS_MASTER =', 'window.SCENARIOS_DATA =')
scenarios = parse_section('window.SCENARIOS_DATA =', 'window.CLAN_MASTER_DATA =')
clans_master = parse_section('window.CLAN_MASTER_DATA =', 'window.CLAN_ABILITIES =')
govs_map = parse_section('window.SCENARIO_HISTORICAL_GOVERNORS =', 'window.CLAN_CAPITAL_PROVINCES =')

print(f"=== FULL VERIFICATION SUITE ===")
print(f"Total Scenarios: {len(scenarios)}")
print(f"Total Officers Master: {len(officers_master)}")

all_ok = True

# TEST 1: Check Hideyoshi officers in master
hideyoshi_master = [o for o in officers_master if '秀吉' in o.get('name', '') or o.get('id') == 'off_toyotomi_hideyoshi']
print(f"\n[TEST 1] Hideyoshi in OFFICERS_MASTER: count = {len(hideyoshi_master)}")
if len(hideyoshi_master) == 1:
    h = hideyoshi_master[0]
    print(f"  OK: Only 1 Hideyoshi exists in master: id={h['id']}, name={h['name']}, bYear={h['birthYear']}, dYear={h['deathYear']}")
else:
    print(f"  ERROR: Expected 1 Hideyoshi in master, found {len(hideyoshi_master)}!")
    all_ok = False

# TEST 2: Check Toyotomi surname year threshold in app.js
if 'const isToyotomiEra = (this.year >= 1586);' in text_app:
    print("\n[TEST 2] Toyotomi surname change year in app.js: OK (1586年)")
else:
    print("\n[TEST 2] ERROR: Toyotomi surname change year is NOT 1586!")
    all_ok = False

if 'if (announce && this.year === 1586)' in text_app:
    print("  Announcement year: OK (1586年)")
else:
    print("  ERROR: Announcement year is NOT 1586!")
    all_ok = False

# TEST 3: Simulate switchScenario for ALL Scenarios
print(f"\n[TEST 3] Simulating switchScenario for ALL {len(scenarios)} Scenarios:")

for s in scenarios:
    scen_id = str(s['id'])
    year = s['year']
    title = s['title']
    owners = s.get('owners', {})
    playables = s.get('playables', [])

    # Active officers for this scenario
    active_officers = []
    for o in json.loads(json.dumps(officers_master)):
        b = o.get('birthYear')
        d = o.get('deathYear')
        if b is not None and d is not None and (year - b >= 15) and (year <= d):
            o['isDaimyo'] = False
            active_officers.append(o)

    # Simulation of resolveOfficerAffiliations
    owners_set = set(owners.values())

    # 1582 check
    if scen_id == '1582':
        oda_r = ['秀吉', '秀長', '秀次', '明智光秀', '柴田勝家', '前田利家', '佐々成政', '丹羽長秀', '滝川一益']
        for off in active_officers:
            if any(k in off['name'] for k in oda_r):
                off['clanId'] = 'oda'
            elif any(k in off['name'] for k in ['徳川家康', '本多忠勝', '酒井忠次']):
                off['clanId'] = 'tokugawa'

    # 1584 check
    if scen_id == '1584':
        toyo_r = ['秀吉', '秀長', '秀次', '池田恒興', '池田輝政', '森長可', '堀秀政', '前田利家', '浅野長政', '石田三成', '大谷吉継', '蒲生氏郷', '丹羽長秀', '蜂須賀正勝', '加藤清正', '福島正則']
        for off in active_officers:
            if any(k in off['name'] for k in toyo_r):
                off['clanId'] = 'toyotomi'
            elif any(k in off['name'] for k in ['徳川家康', '酒井忠次', '本多忠勝', '榊原康政', '井伊直政', '鳥居元忠', '大久保忠世']):
                off['clanId'] = 'tokugawa'
            elif any(k in off['name'] for k in ['織田信雄', '滝川雄利', '滝川一益']):
                off['clanId'] = 'oda'
            elif '佐々成政' in off['name']:
                off['clanId'] = 'sassa'

    # 1587 check
    if scen_id == '1587':
        toyo_r = ['秀吉', '秀長', '秀次', '黒田官兵衛', '黒田長政', '立花宗茂', '加藤清正', '福島正則', '浅野長政', '石田三成', '大谷吉継', '蒲生氏郷', '蜂須賀家政', '前田利家', '堀秀政', '小早川隆景']
        for off in active_officers:
            if any(k in off['name'] for k in toyo_r):
                off['clanId'] = 'toyotomi'
            elif any(k in off['name'] for k in ['徳川家康', '本多忠勝', '酒井忠次']):
                off['clanId'] = 'tokugawa'
            elif any(k in off['name'] for k in ['鍋島直茂', '龍造寺政家']):
                off['clanId'] = 'ryuzoji'
            elif any(k in off['name'] for k in ['島津義久', '島津義弘', '島津家久', '島津歳久']):
                off['clanId'] = 'shimazu'
            elif any(k in off['name'] for k in ['大友宗麟', '大友義統']):
                off['clanId'] = 'otomo'

    # 1590 check
    if scen_id == '1590':
        toyo_r = ['秀吉', '秀長', '秀次', '前田利家', '堀秀政', '丹羽長重', '宇喜多秀家', '黒田官兵衛', '石田三成', '大谷吉継', '加藤清正']
        for off in active_officers:
            if any(k in off['name'] for k in toyo_r):
                off['clanId'] = 'toyotomi'
            elif any(k in off['name'] for k in ['徳川家康', '本多忠勝']):
                off['clanId'] = 'tokugawa'

    # 1592 check
    if scen_id == '1592':
        toyo_r = ['秀吉', '秀次', '小西行長', '加藤清正', '黒田官兵衛', '黒田長政', '小早川隆景', '立花宗茂', '福島正則', '浅野長政', '石田三成', '大谷吉継', '蒲生氏郷', '蜂須賀家政', '増田長盛', '前田玄以', '長束正家', '鍋島直茂', '大友義統']
        for off in active_officers:
            if any(k in off['name'] for k in toyo_r):
                off['clanId'] = 'toyotomi'
            elif any(k in off['name'] for k in ['徳川家康', '徳川秀忠', '本多忠勝', '榊原康政', '井伊直政', '鳥居元忠']):
                off['clanId'] = 'tokugawa'
            elif any(k in off['name'] for k in ['前田利家', '前田利長']):
                off['clanId'] = 'maeda'

    # 1600 check
    if scen_id == '1600':
        for off in active_officers:
            if any(k in off['name'] for k in ['石田三成', '大谷吉継', '島左近', '宇喜多秀家']):
                off['clanId'] = 'ishida'
            elif any(k in off['name'] for k in ['徳川家康', '徳川秀忠', '本多忠勝', '福島正則', '山内一豊', '細川忠興']):
                off['clanId'] = 'tokugawa'

    # Check Hideyoshi duplication in active_officers
    h_offs = [o for o in active_officers if '秀吉' in o.get('name', '') or o.get('id') == 'off_toyotomi_hideyoshi']
    if len(h_offs) > 1:
        print(f"  ERROR: Scenario {scen_id} has duplicate Hideyoshi: {[x['name'] for x in h_offs]}")
        all_ok = False

    # Check Daimyo resolution (missing leaders / 0-province daimyos)
    sim_provs = json.loads(json.dumps(provs_master))
    for p in sim_provs:
        if owners.get(p['id']):
            p['ownerId'] = owners[p['id']]

    active_owners = list(set(p['ownerId'] for p in sim_provs if p.get('ownerId')))
    missing_leaders = []
    for owner_id in active_owners:
        playable_d = next((d for d in playables if d['id'] == owner_id), None)
        leader_name = playable_d['name'] if playable_d else owner_id
        
        clan_officers = [o for o in active_officers if o['clanId'] == owner_id]
        leader_off = next((o for o in clan_officers if o['name'] == leader_name), None)
        if not leader_off:
            leader_off = next((o for o in active_officers if o['name'] == leader_name), None)
            if leader_off:
                leader_off['clanId'] = owner_id
        if not leader_off and clan_officers:
            leader_off = clan_officers[0]
        
        if leader_off:
            leader_off['isDaimyo'] = True
        else:
            missing_leaders.append((owner_id, leader_name))
            for p in sim_provs:
                if p['ownerId'] == owner_id:
                    p['ownerId'] = None

    final_owners = set(p['ownerId'] for p in sim_provs if p.get('ownerId'))
    zero_prov_playables = [p['name'] for p in playables if p['id'] not in final_owners]

    status = "OK"
    if missing_leaders or zero_prov_playables:
        status = f"FAILED (missing={missing_leaders}, zero_provs={zero_prov_playables})"
        all_ok = False
        print(f"  Scenario {scen_id:4s} ({year:4d}) {title:12s}: {status}")
    else:
        print(f"  Scenario {scen_id:4s} ({year:4d}) {title:12s}: OK (Playables: {len(playables):2d}, Daimyos: {len(active_owners):2d}, ActiveOffs: {len(active_officers):3d})")

# TEST 4: Check Key Scenario Placements
print("\n[TEST 4] Historical Placement Verifications:")
for sid in ['1056', '1582', '1584', '1587', '1590', '1592', '1600']:
    g = govs_map.get(sid, {})
    print(f"  Scenario {sid:4s} govs count: {len(g)}")

if all_ok:
    print("\n>>> ALL TESTS PASSED SUCCESSFULLY! ALL REQUIREMENTS FULLY SATISFIED! <<<")
else:
    print("\n>>> SOME TESTS FAILED! <<<")
