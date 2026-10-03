import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('window.OFFICERS_MASTER = [')
end_idx = text.find('\n];', start_idx) + 2
officers = json.loads(text[start_idx + len('window.OFFICERS_MASTER = '):end_idx])

existing_ids = set(o['id'] for o in officers)

additional_heroes = [
    # 幕末・江戸後期の藩主・重臣
    {
        "id": "off_nanbu_nobuyuki",
        "name": "南部信順",
        "clanId": "nanbu",
        "defaultProv": "mutsu",
        "military": 72,
        "politic": 82,
        "intel": 80,
        "era": "bakumatsu",
        "skill": "八戸藩主・薩摩の英主",
        "comment": "島津重豪の十四男で八戸藩第8代藩主。藩政を近代化",
        "lore": "薩摩藩主・島津重豪の男子として生まれ八戸南部家を継承。洋式砲術や学問を奨励し、奥羽列藩同盟にあっても冷静に藩を保全した。",
        "birthYear": 1814,
        "deathYear": 1872,
        "isDaimyo": False
    },
    {
        "id": "off_narayama_sado",
        "name": "楢山佐渡",
        "clanId": "nanbu",
        "defaultProv": "rikuchu",
        "military": 80,
        "politic": 75,
        "intel": 76,
        "era": "bakumatsu",
        "skill": "盛岡藩家老・奥羽の義戦",
        "comment": "盛岡藩筆頭家老。戊辰戦争で盛岡軍を統率",
        "lore": "盛岡藩執政。会津支援と奥羽列藩同盟加盟を主導し、秋田方面へ出兵して奮戦した。敗戦後は責任を一身に背負い自刃した義将。",
        "birthYear": 1828,
        "deathYear": 1869,
        "isDaimyo": False
    },
    {
        "id": "off_maeda_toshiyasu",
        "name": "前田利保",
        "clanId": "maeda",
        "defaultProv": "etchu",
        "military": 65,
        "politic": 85,
        "intel": 88,
        "era": "edo",
        "skill": "富山藩主・本草学者",
        "comment": "富山藩第10代藩主。本草学・蘭学を極めた大名",
        "lore": "加賀前田家一門・越中富山藩主。名君として製薬・売薬業を育成し、自身も世界的な博物学・本草学の著作を遺した学者大名。",
        "birthYear": 1800,
        "deathYear": 1859,
        "isDaimyo": False
    },
    {
        "id": "off_maeda_toshitomo",
        "name": "前田利同",
        "clanId": "maeda",
        "defaultProv": "etchu",
        "military": 68,
        "politic": 78,
        "intel": 76,
        "era": "bakumatsu",
        "skill": "富山藩最後の大名",
        "comment": "富山藩第13代（最後）藩主。戊辰戦争で北越出兵",
        "lore": "越中富山藩主。戊辰戦争では加賀本藩とともに新政府軍に従軍して北越戦争で戦った。維新後は伯爵に叙された。",
        "birthYear": 1856,
        "deathYear": 1921,
        "isDaimyo": False
    },
    {
        "id": "off_kabayama_sukemori",
        "name": "樺山資紀",
        "clanId": "shimazu",
        "defaultProv": "osumi",
        "military": 85,
        "politic": 80,
        "intel": 82,
        "era": "bakumatsu",
        "skill": "薩摩隼人・初代海軍軍令部長",
        "comment": "薩摩藩士。戊辰戦争を奮戦、のち海軍大将・総督",
        "lore": "樺山資敬の三男。寺田屋事件を鎮圧し戊辰戦争では東北各地を転戦。のちに海軍大将・内務大臣・初代台湾総督を務めた巨星。",
        "birthYear": 1837,
        "deathYear": 1922,
        "isDaimyo": False
    },
    {
        "id": "off_masaki_tokishige",
        "name": "正木時茂",
        "clanId": "satomi",
        "defaultProv": "kazusa",
        "military": 88,
        "politic": 70,
        "intel": 75,
        "era": "sengoku",
        "skill": "槍大膳・里見双璧",
        "comment": "里見家筆頭家老。上総大多喜城主、無双の槍名人",
        "lore": "里見義堯の右腕。『槍大膳』の異名を取り北条軍を何度も撃退した武勇無双の豪傑。上総勝浦城・大多喜城を守備した。",
        "birthYear": 1513,
        "deathYear": 1561,
        "isDaimyo": False
    }
]

added = 0
for h in additional_heroes:
    if h['id'] not in existing_ids:
        officers.append(h)
        added += 1

print(f"Added {added} specialized historical heroes.")

# Write back to OFFICERS_MASTER
new_json = json.dumps(officers, ensure_ascii=False, indent=2)
new_text = text[:start_idx + len('window.OFFICERS_MASTER = ')] + new_json + text[end_idx:]

with open('js/data.js', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Saved js/data.js.")
