import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/historical_jodai.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Locate the end of the roster array (before const reuse = [)
idx_reuse = text.find('const reuse = [')
if idx_reuse == -1:
    print("Could not find const reuse")
    sys.exit(1)

# Find ]; right before const reuse = [
idx_end_roster = text.rfind('];', 0, idx_reuse)
if idx_end_roster == -1:
    print("Could not find end of roster")
    sys.exit(1)

new_heian_roster = """,
    // 平安時代（承平天慶・平忠常・前九年・後三年）の史実国司・受領・武将
    { name: "紀貫之", birth: 866, death: 945, mil: 65, pol: 88, intel: 92, skill: "土佐日記", lore: "平安前期の歌人・受領。土佐守、和泉守、木工頭を歴任。『古今和歌集』選者。", posts: [{ year: "939", prov: "izumi", clan: "heian_court" }] },
    { name: "藤原仲平", birth: 875, death: 945, mil: 68, pol: 84, intel: 80, skill: "大和守護", lore: "平安前期の公卿。太政官・大納言、大和守。朝廷の中枢として平将門・藤原純友の乱に対処した。", posts: [{ year: "939", prov: "yamato", clan: "heian_court" }] },
    { name: "源清蔭", birth: 884, death: 950, mil: 70, pol: 82, intel: 78, skill: "河内大納言", lore: "陽成源氏。大納言、河内守。天慶の乱に際し畿内の防備を固めた。", posts: [{ year: "939", prov: "kawachi", clan: "heian_court" }] },
    { name: "小野好古", birth: 884, death: 968, mil: 86, pol: 78, intel: 84, skill: "追捕使長官", lore: "小野道風の兄。追捕使長官として西国へ下向し、博多沖の戦い等で藤原純友軍を追討・平定した名将。", posts: [{ year: "939", prov: "tamba", clan: "heian_court" }] },
    { name: "橘澄清", birth: 890, death: 955, mil: 72, pol: 76, intel: 74, skill: "駿河受領", lore: "平安中期の貴族・受領。駿河守として東海道の治安維持と物資輸送を統括した。", posts: [{ year: "939", prov: "suruga", clan: "heian_court" }] },
    { name: "伴保平", birth: 890, death: 960, mil: 70, pol: 74, intel: 72, skill: "遠江受領", lore: "古代豪族伴氏（大伴氏）の後裔。遠江守を務め、東海道の宿駅支配に尽力した。", posts: [{ year: "939", prov: "totomi", clan: "heian_court" }] },
    { name: "藤原元名", birth: 887, death: 955, mil: 68, pol: 80, intel: 76, skill: "三河受領", lore: "平安中期の公卿・受領。三河守。清廉な治績により善政を布いた受領の鑑とされる。", posts: [{ year: "939", prov: "mikawa", clan: "heian_court" }] },
    { name: "藤原為憲", birth: 895, death: 965, mil: 78, pol: 72, intel: 75, skill: "工藤氏祖", lore: "藤原南家、工藤氏・伊東氏の祖。伊豆守。将門追討に従軍し東国武士団の礎を築いた。", posts: [{ year: "939", prov: "izu", clan: "heian_court" }] },
    { name: "藤原忠輔", birth: 890, death: 960, mil: 66, pol: 78, intel: 74, skill: "伊勢守", lore: "平安中期の貴族。伊勢守。神宮領の安堵と伊勢湾の海上警固を担った。", posts: [{ year: "939", prov: "ise", clan: "heian_court" }, { year: "939", prov: "shima", clan: "heian_court" }] },
    { name: "源経基", birth: 894, death: 961, mil: 85, pol: 76, intel: 80, skill: "六孫王", lore: "清和源氏の祖。六孫王。武蔵介・但馬司。将門の謀叛を朝廷にいち早く奏上し追捕使として従軍。", posts: [{ year: "939", prov: "tajima", clan: "heian_court" }] },
    { name: "藤原国経", birth: 890, death: 955, mil: 65, pol: 76, intel: 72, skill: "因幡受領", lore: "在原行平に連なる受領。因幡守として山陰道の治安維持にあたった。", posts: [{ year: "939", prov: "inaba", clan: "heian_court" }, { year: "939", prov: "hoki", clan: "heian_court" }] },
    { name: "源等", birth: 880, death: 951, mil: 64, pol: 82, intel: 78, skill: "出雲受領", lore: "嵯峨源氏。中納言、出雲守。出雲大社の修繕と出雲国の安定を維持した。", posts: [{ year: "939", prov: "izumo", clan: "heian_court" }, { year: "939", prov: "iwami", clan: "heian_court" }] },
    { name: "菅原在躬", birth: 890, death: 955, mil: 66, pol: 78, intel: 75, skill: "美作受領", lore: "菅原道真の系譜を引く文人貴族。美作守として山陽内陸の農地開墾を指導した。", posts: [{ year: "939", prov: "mimasaka", clan: "heian_court" }] },
    { name: "肝付兼行", birth: 900, death: 960, mil: 76, pol: 68, intel: 66, skill: "大隅肝付", lore: "大隅・日向の古代豪族・肝付氏の祖。南九州の在地武士団を束ねた。", posts: [{ year: "939", prov: "hyuga", clan: "shimazu_proto" }, { year: "939", prov: "osumi", clan: "shimazu_proto" }] },
    { name: "紀隆村", birth: 900, death: 960, mil: 74, pol: 70, intel: 68, skill: "肥前紀氏", lore: "九州の在地領主。肥前・肥後方面で勢威を有し、菊池氏の源流の一つとなった。", posts: [{ year: "939", prov: "hizen", clan: "kikuchi" }] },
    { name: "小野資道", birth: 900, death: 965, mil: 68, pol: 72, intel: 70, skill: "隠岐守", lore: "小野篁の子孫。隠岐守として日本海の海運と配流地の警備を統括した。", posts: [{ year: "939", prov: "oki", clan: "heian_court" }] },
    { name: "安倍良照", birth: 900, death: 960, mil: 78, pol: 66, intel: 70, skill: "奥州安倍祖", lore: "奥州安倍氏の初期指導者。津軽および北上川流域を本拠に奥羽に一大勢力を築いた。", posts: [{ year: "939", prov: "tsugaru", clan: "abe" }] },
    { name: "源頼信", birth: 968, death: 1048, mil: 92, pol: 78, intel: 85, skill: "河内源氏祖", lore: "源満仲の三男。河内源氏の祖。平忠常の乱では追捕使として東国へ下向し、その威名により忠常を無血降伏させた武勇の長者。", posts: [{ year: "1028", prov: "kai", clan: "minamoto_tsunemoto" }] },
    { name: "平直方", birth: 990, death: 1060, mil: 86, pol: 75, intel: 80, skill: "北条祖", lore: "桓武平氏。追捕使として平忠常討伐に従軍。相模国鎌倉を本拠とし、娘を源頼義に嫁がせて源氏と結んだ。北条氏の祖。", posts: [{ year: "1028", prov: "sagami", clan: "heian_court" }, { year: "1056", prov: "sagami", clan: "minamoto_tsunemoto" }] },
    { name: "藤原保昌", birth: 958, death: 1036, mil: 88, pol: 76, intel: 82, skill: "袴垂討伐", lore: "大和守・丹後守。武勇に優れ、盗賊・袴垂を捕縛した伝説で名高い剛の者。", posts: [{ year: "1028", prov: "tango", clan: "heian_court" }] },
    { name: "平維衡", birth: 960, death: 1035, mil: 85, pol: 74, intel: 78, skill: "伊勢平氏祖", lore: "平貞盛の甥・猶子。伊勢平氏の祖。伊勢国を基盤に武力を蓄え、後世の平清盛へと連なる基礎を築いた。", posts: [{ year: "1028", prov: "ise", clan: "heian_court" }] },
    { name: "源頼義", birth: 988, death: 1075, mil: 90, pol: 80, intel: 84, skill: "前九年総帥", lore: "源頼信の長男。陸奥守・鎮守府将軍。前九年の役で安倍頼時・貞任父子を12年に及ぶ苦闘の末に滅ぼし、源氏の武名を天下に轟かせた。", posts: [{ year: "1028", prov: "musashi", clan: "minamoto_tsunemoto" }, { year: "1056", prov: "mutsu", clan: "minamoto_tsunemoto" }] },
    { name: "安倍頼時", birth: 1000, death: 1057, mil: 86, pol: 82, intel: 80, skill: "奥六郡の主", lore: "奥州安倍氏の当主。奥六郡を支配し「俘囚の長」として絶大な権勢を誇った。前九年の役で源頼義と衝突し戦死。", posts: [{ year: "1056", prov: "rikuzen", clan: "abe" }] },
    { name: "安倍貞任", birth: 1019, death: 1062, mil: 91, pol: 70, intel: 76, skill: "厨川柵", lore: "安倍頼時の次男。巨躯と剛勇で知られ、前九年の役で源頼義・義家軍を相手に厨川柵で壮絶に戦い抜いた猛将。", posts: [{ year: "1056", prov: "rikuchu", clan: "abe" }] },
    { name: "清原武則", birth: 1000, death: 1065, mil: 88, pol: 76, intel: 82, skill: "出羽の覇王", lore: "出羽国の有力豪族。前九年の役で源頼義に加勢し一万の軍勢を率いて参戦、勝利の決定打となった。鎮守府将軍に任ぜられた。", posts: [{ year: "1056", prov: "ugo", clan: "kiyohara" }] },
    { name: "源義家", birth: 1039, death: 1106, mil: 98, pol: 75, intel: 88, skill: "八幡太郎", lore: "源頼義の長男。通称「八幡太郎」。天下第一の武勇と称され、前九年・後三年の役で武名を轟かせ、全国の武士が源氏を棟梁と仰ぐ契機を作った。", posts: [{ year: "1056", prov: "iwashiro", clan: "minamoto_tsunemoto" }, { year: "1087", prov: "mutsu", clan: "minamoto_tsunemoto" }] },
    { name: "源義光", birth: 1045, death: 1127, mil: 90, pol: 78, intel: 86, skill: "新羅三郎", lore: "源頼義の三男。新羅三郎。甲斐武田氏・佐竹氏の祖。後三年の役では官職を辞して兄・義家の援軍に駆けつけ活躍した。", posts: [{ year: "1087", prov: "kai", clan: "minamoto_tsunemoto" }] }
"""

# Check if already added
if "【平安時代（承平天慶・平忠常・前九年・後三年）の史実国司・受領・武将】" not in text and "紀貫之" not in text:
    text = text[:idx_end_roster] + new_heian_roster + text[idx_end_roster:]
    print("Added Heian officers to roster in historical_jodai.js.")
else:
    print("Heian officers already present.")

with open('js/historical_jodai.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Successfully updated js/historical_jodai.js!")
