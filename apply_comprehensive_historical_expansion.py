# -*- coding: utf-8 -*-
"""
Comprehensive Historical Expansion Application Script
Updates data.js with:
- Historical officers (OFFICERS_MASTER)
- Scenario leaders and playable alignments (SCENARIOS_DATA)
- Clan Capital Provinces (CLAN_CAPITAL_PROVINCES)
- Scenario Historical Governors (SCENARIO_HISTORICAL_GOVERNORS)
- Territory changing historical events (HISTORICAL_EVENTS_DATA)
"""

import json
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Backup data.js
shutil.copyfile('js/data.js', 'js/data.js.bak_expansion')
print("Backed up data.js to js/data.js.bak_expansion")

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Helper to slice sections
provs_str = text[text.find('window.PROVINCES_DATA =') + len('window.PROVINCES_DATA ='):text.find('window.OFFICERS_MASTER =')].strip().rstrip(';')
officers_str = text[text.find('window.OFFICERS_MASTER =') + len('window.OFFICERS_MASTER ='):text.find('window.SCENARIOS_DATA =')].strip().rstrip(';')
scenarios_str = text[text.find('window.SCENARIOS_DATA =') + len('window.SCENARIOS_DATA ='):text.find('window.CLAN_MASTER_DATA =')].strip().rstrip(';')
clans_str = text[text.find('window.CLAN_MASTER_DATA =') + len('window.CLAN_MASTER_DATA ='):text.find('window.CLAN_ABILITIES =')].strip().rstrip(';')
clan_ab_str = text[text.find('window.CLAN_ABILITIES =') + len('window.CLAN_ABILITIES ='):text.find('window.HISTORICAL_EVENTS_DATA =')].strip().rstrip(';')
events_str = text[text.find('window.HISTORICAL_EVENTS_DATA =') + len('window.HISTORICAL_EVENTS_DATA ='):text.find('window.HISTORICAL_CASTLE_CHANGES =')].strip().rstrip(';')
castle_str = text[text.find('window.HISTORICAL_CASTLE_CHANGES =') + len('window.HISTORICAL_CASTLE_CHANGES ='):text.find('window.DAIMYO_LIFESPAN_DATA =')].strip().rstrip(';')

s_idx = text.find('window.DAIMYO_LIFESPAN_DATA =') + len('window.DAIMYO_LIFESPAN_DATA =')
e_idx = text.find('window.SCENARIO_HISTORICAL_GOVERNORS =')
lifespan_str = text[s_idx:e_idx].strip()
last_b = lifespan_str.rfind('}')
lifespan_str = lifespan_str[:last_b+1]

hist_govs_str = text[text.find('window.SCENARIO_HISTORICAL_GOVERNORS =') + len('window.SCENARIO_HISTORICAL_GOVERNORS ='):text.find('window.CLAN_CAPITAL_PROVINCES =')].strip().rstrip(';')
capitals_str = text[text.find('window.CLAN_CAPITAL_PROVINCES =') + len('window.CLAN_CAPITAL_PROVINCES ='):].strip().rstrip(';')

officers = json.loads(officers_str)
scenarios = json.loads(scenarios_str)
clans = json.loads(clans_str)
events = json.loads(events_str)
hist_govs = json.loads(hist_govs_str)
capitals = json.loads(capitals_str)

print(f"Loaded: Officers={len(officers)}, Scenarios={len(scenarios)}, Events={len(events)}, Capitals={len(capitals)}")

# Import the definitions from generate_comprehensive_governors.py
from generate_comprehensive_governors import GOVERNORS_BY_SCENARIO
from build_historical_expansion import NEW_OFFICERS

# 1. Add NEW_OFFICERS to officers
existing_officer_ids = {o['id'] for o in officers}
existing_officer_names = {o['name'] for o in officers}

added_officers_count = 0
for no in NEW_OFFICERS:
    if no['id'] not in existing_officer_ids:
        officers.append(no)
        existing_officer_ids.add(no['id'])
        existing_officer_names.add(no['name'])
        added_officers_count += 1

# 2. Extract any new officers from GOVERNORS_BY_SCENARIO
for sid, gmap in GOVERNORS_BY_SCENARIO.items():
    year = int(sid)
    for prov_id, gdata in gmap.items():
        gid, gname, gclan, birth, death, mil, pol, intel, skill, lore = gdata
        if gid not in existing_officer_ids and gname not in existing_officer_names:
            era = "edo" if year >= 1600 else ("sengoku" if year >= 1467 else ("nanboku" if year >= 1331 else ("kamakura" if year >= 1185 else "heian")))
            new_o = {
                "id": gid,
                "name": gname,
                "clanId": gclan,
                "defaultProv": prov_id,
                "military": mil,
                "politic": pol,
                "intel": intel,
                "era": era,
                "skill": skill,
                "lore": lore,
                "birthYear": birth,
                "deathYear": death,
                "isDaimyo": False
            }
            officers.append(new_o)
            existing_officer_ids.add(gid)
            existing_officer_names.add(gname)
            added_officers_count += 1

print(f"Added {added_officers_count} new historical officers to OFFICERS_MASTER (Total: {len(officers)})")

# 3. Fix Scenarios Playables and Clan Leaders
for scen in scenarios:
    sid = str(scen['id'])
    playables = scen.get('playables', [])
    
    # 939: 菊池則隆 -> 紀淑光, 豊後国司 -> 小野好古
    if sid == '939':
        for p in playables:
            if p['id'] == 'kikuchi':
                p['name'] = '紀淑光'
                p['desc'] = '平安中期の公卿・受領。土佐守・伊予守・肥後守を歴任。藤原純友に理解を示しつつ九州の治安を回復した名国司。'
            elif p['id'] == 'otomo':
                p['name'] = '小野好古'
                p['desc'] = '大宰大弐・追捕使長官。博多湾海戦にて純友海賊軍を壊滅させ西国の乱を鎮圧した名将。'
                
    # 1331: kyogoku -> 京極道誉, rokkaku -> 六角時信
    if sid == '1331':
        for p in playables:
            if p['id'] == 'kyogoku':
                p['name'] = '佐々木道誉'
                p['desc'] = '京極高氏。婆娑羅大名の代表格。室町幕府の創業を主導し、変幻自在の智謀で南北朝の乱世を生き抜いた巨頭。'
            elif p['id'] == 'rokkaku':
                p['name'] = '六角時信'
                p['desc'] = '近江源氏六角宗家当主。元弘の乱では幕府方として参戦後、建武政権を経て足利尊氏に従い南近江を守った。'

    # 1333: rokkaku -> 六角時信
    if sid == '1333':
        for p in playables:
            if p['id'] == 'rokkaku':
                p['name'] = '六角時信'
                p['desc'] = '近江源氏六角宗家当主。建武新政下で南近江の領国を守備した。'

    # 1350: ogasawara -> 小笠原政長, rokkaku -> 六角氏頼
    if sid == '1350':
        for p in playables:
            if p['id'] == 'ogasawara':
                p['name'] = '小笠原政長'
                p['desc'] = '信濃守護。小笠原貞宗の嫡男。足利尊氏の北朝方として信濃各地の戦乱を平定し幕府を支えた。'
            elif p['id'] == 'rokkaku':
                p['name'] = '六角氏頼'
                p['desc'] = '六角時信の嫡男。南近江守護。室町幕府の侍所頭人を歴任した近江源氏の名君。'

    # 1560: matsudaira -> 松平元康 (Ensure officer off_matsudaira_motoyasu exists)
    if sid == '1560':
        for p in playables:
            if p['id'] == 'matsudaira':
                p['name'] = '松平元康'

    # 1590: toyotomi -> 豊臣秀吉
    if sid == '1590':
        for p in playables:
            if p['id'] == 'toyotomi':
                p['name'] = '豊臣秀吉'
                
    # 1614, 1637: shimazu -> 島津忠恒
    if sid in ['1614', '1637']:
        for p in playables:
            if p['id'] == 'shimazu':
                p['name'] = '島津忠恒'

print("Updated playables for scenarios 939, 1331, 1333, 1350, 1560, 1590, 1614, 1637.")

# 4. Fix CLAN_CAPITAL_PROVINCES
essential_capitals = {
    'owari': 'owari',
    'tottori': 'inaba',
    'okayama': 'bizen',
    'asano': 'aki',
    'fukuoka_kuroda': 'chikuzen',
    'kumamoto_hosokawa': 'higo',
    'kishu': 'kii',
    'mito': 'hitachi',
    'aizu': 'iwashiro',
    'matsue': 'izumo',
    'kuwana': 'ise',
    'fukui_matsudaira': 'echizen',
    'meiji': 'yamashiro',
    'tachibana': 'chikugo',
    'hachisuka': 'awa_shikoku',
    'makino': 'echigo',
    'tsugaru': 'tsugaru',
    'kakizaki': 'ezo',
    'so': 'tsushima'
}
for cid, cap in essential_capitals.items():
    capitals[cid] = cap

print(f"Updated CLAN_CAPITAL_PROVINCES with {len(essential_capitals)} clan capitals.")

# 5. Populate SCENARIO_HISTORICAL_GOVERNORS
for sid, gmap in GOVERNORS_BY_SCENARIO.items():
    if sid not in hist_govs:
        hist_govs[sid] = {}
    for prov_id, gdata in gmap.items():
        gid = gdata[0]
        hist_govs[sid][prov_id] = gid

# Fix duplicates in 1651 (井伊直孝's multiple assignments)
if '1651' in hist_govs:
    # 1651 corrections:
    hist_govs['1651']['buzen'] = 'off_ogasawara_tadazane'  # 小笠原忠真 (小倉藩主)
    hist_govs['1651']['iwami'] = 'off_furuta_shigemasu'    # 浜田藩主
    hist_govs['1651']['izu'] = 'off_inaba_masanori'        # 小田原藩主・幕府代官
    hist_govs['1651']['south_shinano'] = 'off_hoshina_masayuki'  # 保科正之 (高遠藩/会津)
    hist_govs['1651']['musashi'] = 'off_matsudaira_nobutsuna'    # 松平信綱 (川越藩主・老中)

# Copy 1702/1721/1789/1866 governors to cover remaining missing provinces
# By propagating appropriate Edo period governors
edo_template_1651 = hist_govs.get('1651', {})
for target_sid in ['1614', '1637', '1702', '1721', '1789', '1866']:
    t_map = hist_govs.setdefault(target_sid, {})
    scen_obj = next(s for s in scenarios if str(s['id']) == target_sid)
    owners = scen_obj.get('owners', {})
    for pid, cid in owners.items():
        if pid not in t_map and cid == 'tokugawa' and pid in edo_template_1651:
            t_map[pid] = edo_template_1651[pid]

# 1868 戊辰戦争 governors
govs_1868 = hist_govs.setdefault('1868', {})
govs_1868['suruga'] = 'off_katsu_kaishu'
govs_1868['totomi'] = 'off_katsu_kaishu'
govs_1868['izu'] = 'off_egawa_hidetatsu'
govs_1868['yamato'] = 'off_iwakura_tomomi' if 'off_iwakura_tomomi' in existing_officer_ids else 'off_kuroda_kiyotaka'
govs_1868['harima'] = 'off_yamagata_aritomo' if 'off_yamagata_aritomo' in existing_officer_ids else 'off_saigo_tsugumichi'
govs_1868['sanuki'] = 'off_kuroda_kiyotaka'
govs_1868['iyo'] = 'off_itagaki_taisuke'
govs_1868['north_shinano'] = 'off_itagaki_taisuke'
govs_1868['south_shinano'] = 'off_itagaki_taisuke'
govs_1868['north_omi'] = 'off_saigo_takamori'
govs_1868['south_omi'] = 'off_okubo_toshimichi'
govs_1868['sado'] = 'off_kuroda_kiyotaka'

print("Populated and refined SCENARIO_HISTORICAL_GOVERNORS across all scenarios.")

# 6. HISTORICAL_EVENTS_DATA: Replace/expand with 36 dramatic territory changing events!
from build_expanded_events import EXPANDED_HISTORICAL_EVENTS

# Merge expanded events into events list
event_ids = {e['id'] for e in events}
added_events_count = 0
for new_e in EXPANDED_HISTORICAL_EVENTS:
    if new_e['id'] in event_ids:
        # replace existing
        idx = next(i for i, ev in enumerate(events) if ev['id'] == new_e['id'])
        events[idx] = new_e
    else:
        events.append(new_e)
        event_ids.add(new_e['id'])
        added_events_count += 1

print(f"Updated HISTORICAL_EVENTS_DATA: Total events={len(events)} (Added/Updated {len(EXPANDED_HISTORICAL_EVENTS)})")

# 7. Write back to data.js cleanly
new_data_content = f"""// 統一 - データベース定義 (Provinces, Officers, Scenarios, Clans)

window.PROVINCES_DATA = {json.dumps(json.loads(provs_str), ensure_ascii=False, indent=2)};

window.OFFICERS_MASTER = {json.dumps(officers, ensure_ascii=False, indent=2)};

window.SCENARIOS_DATA = {json.dumps(scenarios, ensure_ascii=False, indent=2)};

window.CLAN_MASTER_DATA = {json.dumps(clans, ensure_ascii=False, indent=2)};

window.CLAN_ABILITIES = {json.dumps(json.loads(clan_ab_str), ensure_ascii=False, indent=2)};

window.HISTORICAL_EVENTS_DATA = {json.dumps(events, ensure_ascii=False, indent=2)};

window.HISTORICAL_CASTLE_CHANGES = {json.dumps(json.loads(castle_str), ensure_ascii=False, indent=2)};

window.DAIMYO_LIFESPAN_DATA = {json.dumps(json.loads(lifespan_str), ensure_ascii=False, indent=2)};

window.SCENARIO_HISTORICAL_GOVERNORS = {json.dumps(hist_govs, ensure_ascii=False, indent=2)};

window.CLAN_CAPITAL_PROVINCES = {json.dumps(capitals, ensure_ascii=False, indent=2)};
"""

with open('js/data.js', 'w', encoding='utf-8') as f:
    f.write(new_data_content)

print("Successfully written updated data.js!")
