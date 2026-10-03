import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('window.OFFICERS_MASTER = [')
end_idx = text.find('\n];', start_idx) + 2
officers = json.loads(text[start_idx + len('window.OFFICERS_MASTER = '):end_idx])

existing_ids = set(o['id'] for o in officers)

new_heroes = [
    # 1. 戦国・安土桃山
    {
        "id": "off_kuki_yoshitaka",
        "name": "九鬼嘉隆",
        "clanId": "toyotomi",
        "defaultProv": "shima",
        "military": 86,
        "politic": 75,
        "intel": 80,
        "era": "sengoku",
        "skill": "海賊大名・鉄甲船",
        "comment": "九鬼水軍の将。信長・秀吉に仕え日本丸を建造",
        "lore": "志摩鳥羽城主。織田信長に従い巨大な鉄甲船で毛利水軍を壊滅させた。秀吉の天下統一でも水軍筆頭として活躍。",
        "birthYear": 1542,
        "deathYear": 1600,
        "isDaimyo": False
    },
    {
        "id": "off_katagiri_katsumoto",
        "name": "片桐且元",
        "clanId": "toyotomi",
        "defaultProv": "kawachi",
        "military": 74,
        "politic": 85,
        "intel": 82,
        "era": "sengoku",
        "skill": "賤ヶ岳七本槍・豊臣宿老",
        "comment": "賤ヶ岳七本槍の一人。豊臣家の筆頭家老として調停に奔走",
        "lore": "秀吉に仕え賤ヶ岳で武名を轟かせた。秀吉没後は豊臣家の執政として徳川幕府との融和・存続に命を賭して尽力した。",
        "birthYear": 1556,
        "deathYear": 1615,
        "isDaimyo": False
    },
    {
        "id": "off_wakisaka_yasuharu",
        "name": "脇坂安治",
        "clanId": "toyotomi",
        "defaultProv": "awaji",
        "military": 82,
        "politic": 78,
        "intel": 76,
        "era": "sengoku",
        "skill": "賤ヶ岳七本槍・洲本城主",
        "comment": "賤ヶ岳七本槍。淡路洲本城主から伊予大洲藩主へ",
        "lore": "秀吉子飼いの猛将。賤ヶ岳の戦いで武功を挙げ淡路洲本城主となる。水軍を率いて活躍し関ヶ原では東軍へ寝返った。",
        "birthYear": 1554,
        "deathYear": 1626,
        "isDaimyo": False
    },
    {
        "id": "off_hachisuka_iemasa",
        "name": "蜂須賀家政",
        "clanId": "toyotomi",
        "defaultProv": "awa_shikoku",
        "military": 80,
        "politic": 82,
        "intel": 79,
        "era": "sengoku",
        "skill": "阿波徳島藩祖・蓬庵",
        "comment": "蜂須賀正勝の長男。阿波一国を与えられ徳島藩を築く",
        "lore": "秀吉の四国征伐に従軍し阿波国十七万石を拝領。徳島城と城下町を整備し、阿波踊りの起源とも伝わる繁栄を築いた名君。",
        "birthYear": 1558,
        "deathYear": 1639,
        "isDaimyo": False
    },
    {
        "id": "off_ikoma_chikamasa",
        "name": "生駒親正",
        "clanId": "toyotomi",
        "defaultProv": "sanuki",
        "military": 76,
        "politic": 84,
        "intel": 80,
        "era": "sengoku",
        "skill": "三中老・讃岐高松城主",
        "comment": "豊臣三中老の一人。讃岐高松十七万石を治めた",
        "lore": "織田信長・豊臣秀吉に仕え、奉行・代官として重用された。讃岐高松城・丸亀城を築城し領国経営に手腕を発揮した。",
        "birthYear": 1526,
        "deathYear": 1603,
        "isDaimyo": False
    },
    {
        "id": "off_maeno_nagayasu",
        "name": "前野長康",
        "clanId": "toyotomi",
        "defaultProv": "tajima",
        "military": 78,
        "politic": 75,
        "intel": 76,
        "era": "sengoku",
        "skill": "墨俣一夜城・但馬出石城主",
        "comment": "秀吉旗揚げからの最古参。但馬出石十一万石を領す",
        "lore": "墨俣城築城以来秀吉に影のように付き従った股肱の臣。秀次の後見を務めたが、秀次事件に連座して無念の切腹を遂げた。",
        "birthYear": 1528,
        "deathYear": 1595,
        "isDaimyo": False
    },
    {
        "id": "off_miyabe_keijun",
        "name": "宮部継潤",
        "clanId": "toyotomi",
        "defaultProv": "inaba",
        "military": 75,
        "politic": 83,
        "intel": 82,
        "era": "sengoku",
        "skill": "因幡鳥取城主・御咄衆",
        "comment": "浅井家から秀吉に臣従。因幡五万石を治めた老巧の知将",
        "lore": "浅井長政麾下の僧侶出身武将。のちに秀吉に仕えて因幡鳥取城主となり、九州・小田原征伐で軍功を重ね御咄衆に列した。",
        "birthYear": 1528,
        "deathYear": 1599,
        "isDaimyo": False
    },
    {
        "id": "off_nanjo_mototsugu",
        "name": "南条元続",
        "clanId": "toyotomi",
        "defaultProv": "hoki",
        "military": 72,
        "politic": 70,
        "intel": 74,
        "era": "sengoku",
        "skill": "羽衣石城主・伯耆の雄",
        "comment": "伯耆羽衣石城主。毛利と織田の狭間で戦い抜いた",
        "lore": "父宗勝とともに伯耆に君臨。毛利氏に圧迫されるも羽柴秀吉に通じて忠節を尽くし、伯耆二郡を安堵された。",
        "birthYear": 1549,
        "deathYear": 1591,
        "isDaimyo": False
    },
    {
        "id": "off_tsutsui_sadatsugu",
        "name": "筒井定次",
        "clanId": "toyotomi",
        "defaultProv": "iga",
        "military": 74,
        "politic": 72,
        "intel": 70,
        "era": "sengoku",
        "skill": "伊賀上野城主・キリシタン大名",
        "comment": "筒井順慶の養子。伊賀二十万石を治めた",
        "lore": "順慶の家督を継ぎ秀吉の命で伊賀上野へ移封。壮大な伊賀上野城を築き、茶の湯を古田織部に学んだ文化人武将。",
        "birthYear": 1562,
        "deathYear": 1615,
        "isDaimyo": False
    },
    {
        "id": "off_hachiya_yoritaka",
        "name": "蜂屋頼隆",
        "clanId": "toyotomi",
        "defaultProv": "izumi",
        "military": 76,
        "politic": 78,
        "intel": 74,
        "era": "sengoku",
        "skill": "織田黒母衣衆・和泉支配",
        "comment": "織田・豊臣の重臣。和泉岸和田城主・越前敦賀城主",
        "lore": "信長初期からの重臣で黒母衣衆。信長上洛後は和泉支配を担当し、山崎の戦いでは秀吉方として軍功を挙げた。",
        "birthYear": 1534,
        "deathYear": 1589,
        "isDaimyo": False
    },
    {
        "id": "off_matsuda_yasunaga",
        "name": "松田康長",
        "clanId": "hojo",
        "defaultProv": "izu",
        "military": 82,
        "politic": 65,
        "intel": 72,
        "era": "sengoku",
        "skill": "山中城死守・北条の鑑",
        "comment": "北条家臣。山中城代として秀吉軍七万を迎撃し玉砕",
        "lore": "相模松田氏の重臣。小田原征伐では箱根の要衝・山中城の守備に就き、圧倒的兵力の豊臣軍を相手に凄絶な死闘の末討死した。",
        "birthYear": 1525,
        "deathYear": 1590,
        "isDaimyo": False
    },
    {
        "id": "off_kanamori_nagachika",
        "name": "金森長近",
        "clanId": "oda",
        "defaultProv": "hida",
        "military": 82,
        "politic": 86,
        "intel": 85,
        "era": "sengoku",
        "skill": "飛騨高山開祖・茶道宗匠",
        "comment": "織田・豊臣・徳川に仕え飛騨高山藩を開いた名将",
        "lore": "信長に仕え越前大野城を築く。秀吉の命で飛騨平定を果たし高山藩祖となった。千利休の愛弟子としても名高い。",
        "birthYear": 1524,
        "deathYear": 1608,
        "isDaimyo": False
    },
    {
        "id": "off_mori_hidemoto",
        "name": "毛利秀元",
        "clanId": "mori",
        "defaultProv": "nagato",
        "military": 84,
        "politic": 88,
        "intel": 86,
        "era": "sengoku",
        "skill": "長府藩祖・宰相閣下",
        "comment": "毛利元清の長男。長府藩初代藩主として宗家を補佐",
        "lore": "元就の孫。朝鮮出兵で総大将を務め蔚山の戦いで明軍を撃破。関ヶ原では南宮山に陣を張り、のち長府藩主として毛利家を支え抜いた。",
        "birthYear": 1579,
        "deathYear": 1650,
        "isDaimyo": False
    },
    {
        "id": "off_koide_yoshimasa",
        "name": "小出吉政",
        "clanId": "toyotomi",
        "defaultProv": "tajima",
        "military": 74,
        "politic": 78,
        "intel": 75,
        "era": "sengoku",
        "skill": "但馬出石藩主・岸和田城代",
        "comment": "豊臣一門の重臣。但馬出石六万石を領した",
        "lore": "母が秀吉の叔母。前野長康失脚後に出石城主となり、関ヶ原後は岸和田藩主・出石藩主を歴任して家名を保った。",
        "birthYear": 1565,
        "deathYear": 1613,
        "isDaimyo": False
    },

    # 2. 幕末・維新
    {
        "id": "off_oguri_tadasumi",
        "name": "小栗忠順",
        "clanId": "tokugawa",
        "defaultProv": "kozuke",
        "military": 75,
        "politic": 95,
        "intel": 96,
        "era": "bakumatsu",
        "skill": "近代日本の父・勘定奉行",
        "comment": "幕末の勘定奉行・外国奉行。横須賀造船所を建設",
        "lore": "米欧を歴訪し近代工業の重要性を痛感。横須賀造船所を建設し日本海軍の礎を築いた。維新後は上野権田に隠棲するも非業の死を遂げた。",
        "birthYear": 1827,
        "deathYear": 1868,
        "isDaimyo": False
    },
    {
        "id": "off_okubo_tadanori_bakumatsu",
        "name": "大久保忠礼",
        "clanId": "tokugawa",
        "defaultProv": "sagami",
        "military": 70,
        "politic": 76,
        "intel": 74,
        "era": "bakumatsu",
        "skill": "小田原藩主・箱根警備",
        "comment": "相模小田原藩第9代藩主。箱根の関所を守備",
        "lore": "小田原藩主。箱根関所を擁する要衝を守り、幕末動乱の中で新政府と旧幕府の調停に苦心した。",
        "birthYear": 1842,
        "deathYear": 1897,
        "isDaimyo": False
    },
    {
        "id": "off_hayashi_tadataka",
        "name": "林忠崇",
        "clanId": "tokugawa",
        "defaultProv": "kazusa",
        "military": 82,
        "politic": 68,
        "intel": 75,
        "era": "bakumatsu",
        "skill": "最後の大名・請西藩脱藩",
        "comment": "上総請西藩主。自ら脱藩して遊撃隊を率い戊辰を転戦",
        "lore": "唯一自ら脱藩して旧幕府軍に身を投じた大名。遊撃隊を率いて箱根・会津を転戦した。昭和まで生き『最後の大名』と呼ばれた猛将。",
        "birthYear": 1848,
        "deathYear": 1941,
        "isDaimyo": False
    },
    {
        "id": "off_itakura_katsukiyo",
        "name": "板倉勝静",
        "clanId": "tokugawa",
        "defaultProv": "bicchu",
        "military": 76,
        "politic": 92,
        "intel": 90,
        "era": "bakumatsu",
        "skill": "幕府老中首座・箱館転戦",
        "comment": "備中松山藩主・老中首座。山田方谷を登用し財政改革",
        "lore": "備中松山藩主。山田方谷を抜擢して莫大な借財を完済し藩政改革を達成。幕府老中首座として大政奉還に立ち会い、最後は箱館まで戦い抜いた。",
        "birthYear": 1816,
        "deathYear": 1889,
        "isDaimyo": False
    },
    {
        "id": "off_yamada_hokoku",
        "name": "山田方谷",
        "clanId": "tokugawa",
        "defaultProv": "bicchu",
        "military": 70,
        "politic": 98,
        "intel": 96,
        "era": "bakumatsu",
        "skill": "財政改革の神髄・義利合一",
        "comment": "備中松山藩家老。奇跡の藩政改革を成し遂げた大碩学",
        "lore": "陽明学者・農民出身の家老。十万両の負債をわずか八年で完済し十万両の蓄えを作った。河井継之助の師としても名高い大思想家。",
        "birthYear": 1805,
        "deathYear": 1877,
        "isDaimyo": False
    },
    {
        "id": "off_abe_masakata",
        "name": "阿部正方",
        "clanId": "tokugawa",
        "defaultProv": "bingo",
        "military": 68,
        "politic": 75,
        "intel": 76,
        "era": "bakumatsu",
        "skill": "備後福山藩主",
        "comment": "備後福山藩第9代藩主。長州征討に出兵",
        "lore": "阿部正弘の甥。第二次長州征討では幕府軍の先鋒として戦ったが、動乱の中で若くして病没した。",
        "birthYear": 1848,
        "deathYear": 1867,
        "isDaimyo": False
    }
]

added_count = 0
for h in new_heroes:
    if h['id'] not in existing_ids:
        officers.append(h)
        added_count += 1
        print(f"Added new hero: {h['id']} ({h['name']})")

print(f"Total newly added heroes: {added_count}")
print(f"Total officers now: {len(officers)}")

# Write to js/data.js
new_json_str = json.dumps(officers, ensure_ascii=False, indent=2)
new_text = text[:start_idx + len('window.OFFICERS_MASTER = ')] + new_json_str + text[end_idx:]

with open('js/data.js', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Saved js/data.js with new heroes successfully.")
