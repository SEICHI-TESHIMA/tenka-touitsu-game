import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. OFFICERS_MASTER
off_start_key = 'window.OFFICERS_MASTER ='
scen_start_key = 'window.SCENARIOS_DATA ='
clan_start_key = 'window.CLAN_MASTER_DATA ='
abilities_start_key = 'window.CLAN_ABILITIES ='
events_start_key = 'window.HISTORICAL_EVENTS_DATA ='
castles_start_key = 'window.HISTORICAL_CASTLE_CHANGES ='

off_s = text.find(off_start_key) + len(off_start_key)
off_e = text.find(scen_start_key)
officers = json.loads(text[off_s:off_e].strip().rstrip(';'))

new_officers = [
    {
        "id": "off_kunohe_masazane",
        "name": "九戸政実",
        "clanId": "kunohe",
        "defaultProv": "mutsu",
        "military": 93,
        "politic": 68,
        "intel": 84,
        "era": "sengoku",
        "skill": "白水の激闘・九戸鉄壁",
        "lore": "陸奥九戸城主。南部一族屈指の猛将。秀吉の奥州仕置に真っ向から反旗を翻し、蒲生氏郷・浅野長政・井伊直政ら十万の奥州仕置大軍を九戸城にて迎え撃った。",
        "birthYear": 1536,
        "deathYear": 1591,
        "isDaimyo": True
    },
    {
        "id": "off_kunohe_sanechika",
        "name": "九戸実親",
        "clanId": "kunohe",
        "defaultProv": "mutsu",
        "military": 84,
        "politic": 62,
        "intel": 76,
        "era": "sengoku",
        "skill": "一族結束の義旗",
        "lore": "九戸政実の実弟。兄とともに南部信直および豊臣仕置軍十万に頑強に抵抗し、九戸城の死闘を支えた猛勇の将。",
        "birthYear": 1542,
        "deathYear": 1591,
        "isDaimyo": False
    },
    {
        "id": "off_takeda_kounsai",
        "name": "武田耕雲斎",
        "clanId": "mito",
        "defaultProv": "hitachi",
        "military": 82,
        "politic": 85,
        "intel": 84,
        "era": "bakumatsu",
        "skill": "天狗党総大将",
        "lore": "水戸藩家老。徳川斉昭の側近。尊皇攘夷激派・天狗党千余名を率いて筑波山で挙兵し、厳寒の中山道を西上して京都・朝廷を目指した。",
        "birthYear": 1803,
        "deathYear": 1865,
        "isDaimyo": False
    },
    {
        "id": "off_fujita_koshiro",
        "name": "藤田小四郎",
        "clanId": "mito",
        "defaultProv": "hitachi",
        "military": 85,
        "politic": 72,
        "intel": 81,
        "era": "bakumatsu",
        "skill": "筑波山義勇の魁",
        "lore": "水戸学の巨頭・藤田東湖の四男。若くして尊王攘夷論を主導し、同志を糾合して筑波山で天狗党挙兵の火蓋を切った。",
        "birthYear": 1842,
        "deathYear": 1865,
        "isDaimyo": False
    },
    {
        "id": "off_yoshimura_torataro",
        "name": "吉村寅太郎",
        "clanId": "tosa",
        "defaultProv": "yamato",
        "military": 86,
        "politic": 68,
        "intel": 78,
        "era": "bakumatsu",
        "skill": "天誅組の魁",
        "lore": "土佐藩出身の尊攘激派。武市半平太の土佐勤王党に参加後脱藩。公卿・中山忠光とともに大和五條代官所を急襲し、倒幕の先鋒となった。",
        "birthYear": 1837,
        "deathYear": 1863,
        "isDaimyo": False
    },
    {
        "id": "off_nakayama_tadamitsu",
        "name": "中山忠光",
        "clanId": "meiji",
        "defaultProv": "yamato",
        "military": 72,
        "politic": 76,
        "intel": 74,
        "era": "bakumatsu",
        "skill": "尊皇大義の主将",
        "lore": "権大納言中山忠能の七男、明治天皇の叔父。尊皇攘夷の先頭に立ち、大和天誅組の総裁として五條で挙兵した。",
        "birthYear": 1845,
        "deathYear": 1864,
        "isDaimyo": False
    },
    {
        "id": "off_hirano_kuniomi",
        "name": "平野国臣",
        "clanId": "kuroda",
        "defaultProv": "tajima",
        "military": 84,
        "politic": 78,
        "intel": 83,
        "era": "bakumatsu",
        "skill": "生野義勇の熱誠",
        "lore": "福岡藩脱藩の志士。西郷隆盛・月照の入水に立ち会い救出。但馬生野代官所を急襲し、農兵を組織して倒幕の義挙を企てた。",
        "birthYear": 1828,
        "deathYear": 1864,
        "isDaimyo": False
    },
    {
        "id": "off_ikuta_yorozu",
        "name": "生田万",
        "clanId": "oshio",
        "defaultProv": "echigo",
        "military": 80,
        "politic": 72,
        "intel": 82,
        "era": "bakumatsu",
        "skill": "越後柏崎の義挙",
        "lore": "平田篤胤門下の国学者。大塩平八郎の乱に共鳴し、飢民救済を掲げて越後柏崎の陣屋を急襲した熱血の義民。",
        "birthYear": 1801,
        "deathYear": 1837,
        "isDaimyo": False
    }
]

existing_off_ids = {o['id'] for o in officers}
for no in new_officers:
    if no['id'] not in existing_off_ids:
        officers.append(no)

# Also update Marubashi Chuya, Yui Shosetsu, Oshio Heihachiro stats
for o in officers:
    if o.get('id') == 'off_edo_yui_1605_0':
        o['military'] = 86
        o['intel'] = 93
        o['politic'] = 80
        o['isDaimyo'] = True
    elif o.get('id') == 'off_edo_yui_1605_1':
        o['military'] = 92
        o['intel'] = 74
        o['politic'] = 60
    elif o.get('id') == 'off_edo_oshio_1793_8':
        o['military'] = 85
        o['intel'] = 92
        o['politic'] = 88
        o['isDaimyo'] = True

# 2. CLAN_MASTER_DATA
clan_s = text.find(clan_start_key) + len(clan_start_key)
clan_e = text.find(abilities_start_key)
clans = json.loads(text[clan_s:clan_e].strip().rstrip(';'))

clans['kunohe'] = {
    "family": "九戸党",
    "color": "#8b0000",
    "kamon": "kamon-kunohe",
    "capital_pref": ["mutsu", "rikuchu"],
    "tactic": "白水の激闘・九戸鉄壁",
    "tacticDesc": "峻険なる九戸城の要害と精強な弓鉄砲部隊により、十万の大軍をも撃退する鉄壁の防衛力を誇る。",
    "desc": "南部一族きっての猛将・九戸政実が率いる反豊臣・東北独立武士団。秀吉の奥州仕置に真っ向から抵抗し、天下統一の最後の難関となった。",
    "leaders": { "1590": "九戸政実", "default": "九戸政実" }
}

clans['tenguto'] = {
    "family": "水戸天狗党",
    "color": "#2c3e50",
    "kamon": "kamon-tengu",
    "capital_pref": ["hitachi"],
    "tactic": "筑波義勇の魁",
    "tacticDesc": "尊皇攘夷の熱誠に燃える志士と農兵が一体となり、厳寒の中山道を突破する驚異の突進力を発揮する。",
    "desc": "武田耕雲斎・藤田小四郎ら水戸藩尊王攘夷派の決死隊。筑波山で挙兵し、雪深い中山道を越えて京都・朝廷を目指した。",
    "leaders": { "1864": "武田耕雲斎", "default": "武田耕雲斎" }
}

# 3. CLAN_ABILITIES
ab_s = text.find(abilities_start_key) + len(abilities_start_key)
ab_e = text.find(events_start_key)
abilities = json.loads(text[ab_s:ab_e].strip().rstrip(';'))

abilities['kunohe'] = {
    "military": 91,
    "politics": 68,
    "stratagem": 84,
    "personality": "aggressive",
    "title": "九戸鉄壁",
    "note": "秀吉の奥州仕置軍十万を迎え撃った奥羽屈指の猛将"
}

abilities['tenguto'] = {
    "military": 86,
    "politics": 78,
    "stratagem": 83,
    "personality": "aggressive",
    "title": "天狗義勇の魁",
    "note": "筑波山挙兵から中山道西上・尊皇維新の先駆"
}

# 4. HISTORICAL_EVENTS_DATA
ev_s = text.find(events_start_key) + len(events_start_key)
ev_e = text.find(castles_start_key)
events = json.loads(text[ev_s:ev_e].strip().rstrip(';'))

new_events = [
    {
        "id": "evt_1591_kunohe_rebellion",
        "scenarioId": "*",
        "year": 1591,
        "season": "夏",
        "title": "九戸政実の乱・奥州仕置軍十万の進発",
        "desc": "豊臣秀吉の奥州仕置と南部信直の支配に反発した九戸政実が陸奥九戸城にて五千の精鋭とともに蜂起！秀吉は蒲生氏郷・浅野長政・井伊直政・前田利家ら十万の奥州仕置大軍を派遣した！",
        "changes": {
            "message": "九戸政実の乱が勃発！東北奥羽が反豊臣の激震に見舞われました！"
        }
    },
    {
        "id": "evt_1591_kunohe_victory_if",
        "scenarioId": "*",
        "year": 1591,
        "season": "秋",
        "title": "【歴史IF】九戸政実の乱成功・奥州独立と仕置軍撃退",
        "desc": "九戸政実の卓越した用兵と鉄壁の要害により、豊臣仕置軍十万を馬淵川・九戸城にて撃破！秀吉の奥州仕置を粉砕し、九戸政実は東北の独立覇王として威名を天下に轟かせた！",
        "changes": {
            "territory": {
                "mutsu": "kunohe",
                "rikuchu": "kunohe"
            },
            "message": "【九戸の乱 大勝利】九戸政実が陸奥・陸中を完全掌握！豊臣軍を撃退し奥州独立を果たしました！"
        }
    },
    {
        "id": "evt_1651_keian_success_if",
        "scenarioId": "1651",
        "year": 1651,
        "season": "冬",
        "title": "【歴史IF】由比正雪の乱成功・江戸城掌握と浪人政権樹立",
        "desc": "丸橋忠弥が江戸城大手門を夜襲急襲！火薬庫を制圧し老中・幕閣を捕縛！由比正雪が駿河から三万の牢人軍を率いて進駐し、十万の困窮牢人を救済する新秩序・張孔堂政権を樹立した！",
        "changes": {
            "territory": {
                "musashi": "yui",
                "suruga": "yui",
                "sagami": "yui"
            },
            "message": "【慶安の変 大勝利】由比正雪一党が江戸城を制圧！十万牢人の復権と新幕府秩序が打ち立てられました！"
        }
    },
    {
        "id": "evt_1837_oshio_success_if",
        "scenarioId": "1837",
        "year": 1837,
        "season": "夏",
        "title": "【歴史IF】大塩平八郎の乱成功・大坂城解放と救民政権",
        "desc": "大塩平八郎の精密なる大砲射撃が町奉行所と大坂城代を屈服させ、大坂城を完全占拠！三井・鴻池ら豪商の米蔵・金蔵を万民に開放し、西国数万の義農兵が集結して『洗心洞・民衆救済政権』が誕生した！",
        "changes": {
            "territory": {
                "settsu": "oshio",
                "kawachi": "oshio",
                "izumi": "oshio"
            },
            "message": "【大塩の乱 大勝利】「救民」の旗印のもと大坂城を完全解放！摂津・河内・和泉を掌握しました！"
        }
    },
    {
        "id": "evt_1837_ikuta_success_if",
        "scenarioId": "1837",
        "year": 1837,
        "season": "秋",
        "title": "【歴史IF】生田万の乱成功・越後柏崎解放と北越蜂起",
        "desc": "国学者・生田万が大塩平八郎の義挙に呼応して越後柏崎陣屋を占拠！飢民を救うべく米蔵を開放し、越後天領の義農軍を組織して北越を解放した！",
        "changes": {
            "territory": {
                "echigo": "oshio"
            },
            "message": "【生田万の乱 成功】越後柏崎を制圧し、北越の民衆救済拠点を確立しました！"
        }
    },
    {
        "id": "evt_1853_sanhei_ikki",
        "scenarioId": "*",
        "year": 1853,
        "season": "夏",
        "title": "嘉永三閉伊一揆・百姓一万六千の越訴大勝利",
        "desc": "南部盛岡藩の重税と苛政に抗し、百姓一万六千が整然と規律を保って仙台藩へ集団越訴！藩庁に要求を全面受諾させ、悪代官罷免と大幅減税・農民自治を勝ち取った！",
        "changes": {
            "message": "【三閉伊一揆 大勝利】百姓一万六千の団結が実を結び、農民自治と大幅減税が確立されました！"
        }
    },
    {
        "id": "evt_1863_tenchugumi_success_if",
        "scenarioId": "*",
        "year": 1863,
        "season": "秋",
        "title": "【歴史IF】天誅組の変成功・大和五條解放と維新先鋒",
        "desc": "吉村寅太郎・公卿中山忠光率いる天誅組が高取城を電光石火で攻略！十津川郷士千余名と合流して大和国を一円掌握し、大和行幸の先鋒として倒幕の狼煙を上げた！",
        "changes": {
            "territory": {
                "yamato": "tosa"
            },
            "message": "【天誅組の変 成功】大和国が解放され、尊王攘夷義勇軍の大和拠点が確立されました！"
        }
    },
    {
        "id": "evt_1863_ikuno_success_if",
        "scenarioId": "*",
        "year": 1863,
        "season": "冬",
        "title": "【歴史IF】生野の変成功・但馬銀山掌握と山陰義勇軍",
        "desc": "福岡藩脱藩の志士・平野国臣らが但馬生野代官所・銀山を接収！農民との信頼を結び、豊富な銀資金をもとに『山陰農兵義勇軍』を組織して京都を衝く態勢を確立した！",
        "changes": {
            "territory": {
                "tajima": "kuroda"
            },
            "message": "【生野の変 成功】生野銀山を掌握し、巨額の銀資金と農兵隊を確保しました！"
        }
    },
    {
        "id": "evt_1864_tenguto_success_if",
        "scenarioId": "*",
        "year": 1864,
        "season": "冬",
        "title": "【歴史IF】水戸天狗党の乱成功・中山道突破と御所進駐",
        "desc": "武田耕雲斎・藤田小四郎率いる天狗党が敦賀の包囲網を猛突破し、京都御所に到達！孝明天皇に直訴して尊皇討幕の密勅を獲得、長州藩と合流して維新回天を成し遂げた！",
        "changes": {
            "territory": {
                "omi": "mito",
                "hitachi": "mito"
            },
            "message": "【天狗党の乱 成功】中山道を完全踏破し京都へ進駐！尊皇攘夷の主導権を確立しました！"
        }
    }
]

existing_ev_ids = {e['id'] for e in events}
for ne in new_events:
    if ne['id'] not in existing_ev_ids:
        events.append(ne)

# Rebuild data.js
# We replace each section carefully
new_off_json = json.dumps(officers, ensure_ascii=False, indent=2)
new_clan_json = json.dumps(clans, ensure_ascii=False, indent=2)
new_ab_json = json.dumps(abilities, ensure_ascii=False, indent=2)
new_ev_json = json.dumps(events, ensure_ascii=False, indent=2)

part1 = text[:off_s] + " " + new_off_json + ";\n\n"
part2 = text[off_e:clan_s] + " " + new_clan_json + ";\n\n"
part3 = text[clan_e:ab_s] + " " + new_ab_json + ";\n\n"
part4 = text[ab_e:ev_s] + " " + new_ev_json + ";\n\n"
part5 = text[ev_e:]

rebuilt = part1 + part2 + part3 + part4 + part5

with open('js/data.js', 'w', encoding='utf-8') as f:
    f.write(rebuilt)

print("Successfully updated js/data.js!")
print(f"  Officers count: {len(officers)}")
print(f"  Clans count: {len(clans)}")
print(f"  Abilities count: {len(abilities)}")
print(f"  Events count: {len(events)}")
