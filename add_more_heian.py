import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/historical_jodai.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx_reuse = text.find('const reuse = [')
idx_end_roster = text.rfind('];', 0, idx_reuse)

additional_heian_roster = """,
    // 1028〜1087年（摂関期・前九年・後三年）の史実国司・受領・豪族
    { name: "藤原頼通", birth: 992, death: 1074, mil: 60, pol: 95, intel: 90, skill: "平等院鳳凰堂", lore: "藤原道長の嫡男。関白を半世紀にわたり務め、摂関政治の極盛期を築いた。宇治に平等院鳳凰堂を建立。", posts: [{ year: "1028", prov: "yamashiro", clan: "heian_court" }, { year: "1056", prov: "yamashiro", clan: "heian_court" }] },
    { name: "藤原教通", birth: 996, death: 1075, mil: 62, pol: 90, intel: 85, skill: "大二条関白", lore: "藤原道長の五男。頼通の弟。関白・太政大臣。兄の跡を継いで朝政を主導した。", posts: [{ year: "1056", prov: "yamato", clan: "heian_court" }, { year: "1087", prov: "yamashiro", clan: "heian_court" }] },
    { name: "源頼国", birth: 990, death: 1058, mil: 82, pol: 78, intel: 76, skill: "美濃源氏", lore: "源頼光の長男。摂津源氏。美濃守・常陸介。朝廷の武力として宮中を警護した。", posts: [{ year: "1028", prov: "mino", clan: "heian_court" }, { year: "1056", prov: "mino", clan: "heian_court" }] },
    { name: "源頼綱", birth: 1025, death: 1097, mil: 80, pol: 76, intel: 82, skill: "多田源氏", lore: "源頼国の五男。多田源氏の祖。摂津守・三河守。歌人としても知られ、白河天皇の武力として仕えた。", posts: [{ year: "1056", prov: "settsu", clan: "heian_court" }, { year: "1087", prov: "settsu", clan: "heian_court" }] },
    { name: "藤原資平", birth: 986, death: 1067, mil: 82, pol: 86, intel: 84, skill: "刀伊防衛", lore: "大宰大弐。刀伊の入寇に際して九州の武士団を統率し、異民族の侵略を撃退した名長官。", posts: [{ year: "1028", prov: "chikuzen", clan: "heian_court" }] },
    { name: "平常晴", birth: 1005, death: 1070, mil: 78, pol: 72, intel: 70, skill: "房総平氏", lore: "平忠常の子。平忠常の乱後、朝廷に帰服して房総の地を継承し、千葉氏・上総氏の祖となった。", posts: [{ year: "1028", prov: "kazusa", clan: "taira_masakado" }, { year: "1056", prov: "kazusa", clan: "taira_sadamori" }] },
    { name: "藤原経清", birth: 1010, death: 1062, mil: 85, pol: 76, intel: 78, skill: "亘理権太夫", lore: "藤原北家魚名流。亘理権太夫。安倍頼時の娘婿となり前九年の役で安倍方に属して奮戦した。藤原清衡の父。", posts: [{ year: "1056", prov: "iwaki", clan: "heian_court" }] },
    { name: "平正衡", birth: 1030, death: 1090, mil: 84, pol: 75, intel: 76, skill: "伊勢平氏", lore: "平維衡の孫。伊勢平氏。出羽守・越後守。白河天皇の院司として重用され、平清盛の曾祖父にあたる。", posts: [{ year: "1056", prov: "echigo", clan: "heian_court" }, { year: "1087", prov: "ise", clan: "heian_court" }] },
    { name: "吉彦秀武", birth: 1010, death: 1087, mil: 86, pol: 72, intel: 80, skill: "出羽俘囚頭", lore: "出羽国の有力武豪。後三年の役において源義家・藤原清衡に味方し、金沢柵の攻略に決定的な役割を果たした。", posts: [{ year: "1087", prov: "ugo", clan: "kiyohara" }] },
    { name: "清原家衡", birth: 1045, death: 1087, mil: 82, pol: 68, intel: 74, skill: "金沢柵籠城", lore: "出羽清原氏当主。武衡の甥。後三年の役で清衡・源義家連合軍と対立し、難攻不落の金沢柵に籠城して激戦を展開した。", posts: [{ year: "1087", prov: "rikuchu", clan: "kiyohara" }] },
    { name: "源重成", birth: 1050, death: 1110, mil: 78, pol: 74, intel: 75, skill: "院判官代", lore: "清和源氏。白河院の北面武士として仕え、畿内の治安維持と伊賀・伊勢の警護を担当した。", posts: [{ year: "1087", prov: "iga", clan: "heian_court" }, { year: "1087", prov: "totomi", clan: "heian_court" }] },
    { name: "藤原宗忠", birth: 1062, death: 1141, mil: 64, pol: 92, intel: 88, skill: "中右記", lore: "平安後期の公卿。右大臣。院政期の名臣として活躍し、詳細な日記『中右記』を残した。", posts: [{ year: "1087", prov: "yamato", clan: "heian_court" }, { year: "1087", prov: "kawachi", clan: "minamoto_tsunemoto" }] },
    { name: "源仲政", birth: 1060, death: 1125, mil: 80, pol: 76, intel: 78, skill: "下総守", lore: "摂津源氏。下総守・三河守。源頼政の父。東国受領として武名を馳せた。", posts: [{ year: "1087", prov: "mikawa", clan: "heian_court" }] }
"""

if "【1028〜1087年（摂関期・前九年・後三年）の史実国司・受領・豪族】" not in text and "藤原頼通" not in text:
    text = text[:idx_end_roster] + additional_heian_roster + text[idx_end_roster:]
    print("Added additional Heian officers to roster.")
else:
    print("Additional Heian officers already present.")

with open('js/historical_jodai.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Successfully updated js/historical_jodai.js with more Heian officers!")
