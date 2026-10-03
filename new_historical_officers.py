# -*- coding: utf-8 -*-
"""
城代解消に必要な史実武将データ定義ファイル。
各武将について、ID, 名前, 所属, 時代, 初期国, 能力値, スキル, 重厚な史実列伝（100〜160文字）を定義。
"""

HISTORICAL_NEW_OFFICERS = [
    # === 平安時代 (939, 1028, 1056, 1087, 1156) ===
    {
        "id": "off_minamoto_yorimitsu",
        "name": "源頼光",
        "clanId": "minamoto_tsunemoto",
        "defaultProv": "settsu",
        "military": 92, "politic": 80, "intel": 85,
        "era": "ancient",
        "skill": "童子切安綱",
        "lore": "清和源氏3代。満仲の長男で摂津源氏の祖。藤原道長に臣従し「朝家の守護」と称された。丹波大江山の酒呑童子退治や土蜘蛛退治の伝説で名高い武勇の巨星。頼光四天王（渡辺綱、坂田金時、碓井貞光、卜部季武）を従え、武家源氏の武名を天下に轟かせた。",
        "birthYear": 948, "deathYear": 1021, "isDaimyo": True
    },
    {
        "id": "off_minamoto_yorinobu",
        "name": "源頼信",
        "clanId": "minamoto_tsunemoto",
        "defaultProv": "kawachi",
        "military": 91, "politic": 82, "intel": 86,
        "era": "ancient",
        "skill": "河内源氏の覇",
        "lore": "満仲の三男で河内源氏の祖。甲斐・常陸・上野の受領を歴任。平忠常の乱では追討使に任じられ、東国へ向かうと忠常は頼信の武名を恐れて戦わずして降伏した。坂東武士と深い主従関係を結び、のちの八幡太郎義家や源頼朝へと続く武家棟梁の不動の基盤を築いた。",
        "birthYear": 968, "deathYear": 1048, "isDaimyo": True
    },
    {
        "id": "off_taira_naokata",
        "name": "平直方",
        "clanId": "heian_court",
        "defaultProv": "sagami",
        "military": 82, "politic": 75, "intel": 78,
        "era": "ancient",
        "skill": "坂東の重鎮",
        "lore": "桓武平氏・平貞盛の曾孫。平忠常の乱に際して追討使に任じられ東国へ下向。鎌倉に居館を構えて後の鎌倉発展の礎を築いた。娘を源頼信の子・頼義に嫁がせて鎌倉の地を譲り渡し、河内源氏と坂東平氏の強力な結びつきを形成。後北条氏や三浦氏の共通の先祖とされる。",
        "birthYear": 985, "deathYear": 1050, "isDaimyo": False
    },
    {
        "id": "off_minamoto_yorikuni",
        "name": "源頼国",
        "clanId": "minamoto_tsunemoto",
        "defaultProv": "mino",
        "military": 80, "politic": 78, "intel": 76,
        "era": "ancient",
        "skill": "美濃の棟梁",
        "lore": "源頼光の長男。美濃守をはじめ山城・常陸・播磨の受領を歴任し、美濃源氏・多田源氏の発展に寄与した。藤原頼通ら摂関家に近侍して宮中の警固を担い、武門の家格を維持。多くの武士を子孫に送り出し、美濃・近江における清和源氏の勢力伸張の礎を築いた。",
        "birthYear": 990, "deathYear": 1058, "isDaimyo": False
    },
    {
        "id": "off_fujiwara_yasumasa",
        "name": "藤原保昌",
        "clanId": "heian_court",
        "defaultProv": "tamba",
        "military": 86, "politic": 74, "intel": 75,
        "era": "ancient",
        "skill": "剛勇の貴公子",
        "lore": "平安中期の貴族・武将。和泉式部の夫。大和守・丹後守を歴任。笛の名手として知られる一方、夜道で強盗の袴垂に襲撃された際に動じず返り討ちにした逸話など、武勇の誉れ高き人物。源頼光と並び「武勇の士」と称され、摂関期の朝廷防衛に大きな役割を果たした。",
        "birthYear": 958, "deathYear": 1036, "isDaimyo": False
    },
    {
        "id": "off_taira_korehira",
        "name": "平維衡",
        "clanId": "taira_sadamori",
        "defaultProv": "ise",
        "military": 85, "politic": 76, "intel": 78,
        "era": "ancient",
        "skill": "伊勢平氏の祖",
        "lore": "平貞盛の四男。伊勢平氏の実質的な祖。伊勢国・下総国の受領を歴任し、一族の平致頼と激しく抗争した「長徳の私闘」などで武名を轟かせた。藤原道長に武勇を買われて伊勢国に広大な勢力基盤を確立し、後の平正盛・忠盛・清盛へと至る平家全盛の血脈を拓いた。",
        "birthYear": 965, "deathYear": 1035, "isDaimyo": True
    },
    {
        "id": "off_taira_masahira",
        "name": "平正衡",
        "clanId": "taira_sadamori",
        "defaultProv": "ise",
        "military": 82, "politic": 75, "intel": 76,
        "era": "ancient",
        "skill": "伊勢の基盤",
        "lore": "平維衡の長男。伊勢平氏3代。出羽守・伊賀守などを務め、伊勢・伊賀における在地支配を強化した。白河院政の草創期において朝廷の軍事力を支え、子・正盛が追討使として武名を馳せる土台を整えた。伊勢を本拠とする武士団平氏の在地領主化を推し進めた重鎮。",
        "birthYear": 1005, "deathYear": 1070, "isDaimyo": True
    },
    {
        "id": "off_minamoto_yoriyoshi",
        "name": "源頼義",
        "clanId": "minamoto_tsunemoto",
        "defaultProv": "sagami",
        "military": 93, "politic": 80, "intel": 84,
        "era": "ancient",
        "skill": "陸奥の覇弓",
        "lore": "源頼信の長男。八幡太郎義家の父。前九年の役で陸奥守兼鎮守府将軍として安倍頼時・貞任・宗任と十二年にわたり死闘を演じる。清原武則の助力を得て苦戦の末に安倍氏を滅ぼし、奥羽に源氏の威名を確立。鶴岡若宮を創祀するなど、東国武士に崇敬される源氏の祖となった。",
        "birthYear": 988, "deathYear": 1075, "isDaimyo": True
    },
    {
        "id": "off_minamoto_yoshiie",
        "name": "源義家",
        "clanId": "minamoto_tsunemoto",
        "defaultProv": "sagami",
        "military": 98, "politic": 82, "intel": 88,
        "era": "ancient",
        "skill": "八幡太郎の神威",
        "lore": "源頼義の長男。「八幡太郎」と号した武家源氏最大の英雄。前九年の役で獅子奮迅の武勇を見せ、後三年の役では清原氏の内紛に介入してこれを平定、奥州藤原氏の成立を促した。東国武士から絶大な信望を集め、全国の武士が私領を寄進するほどの武門の頂点を極めた。",
        "birthYear": 1039, "deathYear": 1106, "isDaimyo": True
    },
    {
        "id": "off_minamoto_yoshitsuna",
        "name": "源義綱",
        "clanId": "minamoto_tsunemoto",
        "defaultProv": "kai",
        "military": 86, "politic": 75, "intel": 80,
        "era": "ancient",
        "skill": "賀茂次郎",
        "lore": "源頼義の次男。「賀茂次郎」と称された猛将。美濃守をはじめ美作守などを歴任し、後三年の役後には白河上皇の近臣として比叡山強訴を撃退するなど武功を重ねた。兄・義家と競う実力を持ったが、のちに源氏の内紛に巻き込まれ甲斐・伊豆方面で波乱の生涯を送った。",
        "birthYear": 1042, "deathYear": 1134, "isDaimyo": False
    },
    {
        "id": "off_minamoto_yoshimitsu",
        "name": "源義光",
        "clanId": "minamoto_tsunemoto",
        "defaultProv": "hitachi",
        "military": 90, "politic": 82, "intel": 89,
        "era": "ancient",
        "skill": "新羅三郎の軍略",
        "lore": "源頼義の三男。「新羅三郎」と称される智勇兼備の武将。足柄山で豊原時秋に笙の秘曲を授けた逸話や、後三年の役で官職を辞して兄・義家救援に奥州へ駆けつけた義心で名高い。甲斐源氏（武田氏・小笠原氏）や常陸佐竹氏の始祖となり、後世の武家社会に巨大な足跡を残した。",
        "birthYear": 1045, "deathYear": 1127, "isDaimyo": False
    },
    {
        "id": "off_abe_yoritoki",
        "name": "安倍頼時",
        "clanId": "abe",
        "defaultProv": "mutsu",
        "military": 88, "politic": 82, "intel": 80,
        "era": "ancient",
        "skill": "奥六郡の巨頭",
        "lore": "奥六郡（岩手県中部・南部）を支配した俘囚長安倍氏の棟梁。安倍忠良の子で旧名は頼良。衣川以南への進出を図り、朝廷から派遣された源頼義と衝突して前九年の役を引き起こす。一族と配下の蝦夷武士団を率いて国府軍を圧倒したが、鳥海柵での戦いの最中に流れ矢を受けて戦死した。",
        "birthYear": 1000, "deathYear": 1057, "isDaimyo": True
    },
    {
        "id": "off_abe_sadato",
        "name": "安倍貞任",
        "clanId": "abe",
        "defaultProv": "rikuchu",
        "military": 92, "politic": 75, "intel": 78,
        "era": "ancient",
        "skill": "厨川の巨魁",
        "lore": "安倍頼時の長男。六尺余の偉丈夫で「厨川次郎」と称された豪傑。前九年の役で黄海の戦いにおいて大吹雪を利用し源頼義・義家軍を壊滅寸前に追い込む。最後は厨川柵で清原・源氏連合軍の猛攻に包囲され、防柵に火を放たれながらも奮戦し、薙刀を振るって壮烈な最期を遂げた。",
        "birthYear": 1019, "deathYear": 1062, "isDaimyo": False
    },
    {
        "id": "off_abe_muneto",
        "name": "安倍宗任",
        "clanId": "abe",
        "defaultProv": "rikuzen",
        "military": 87, "politic": 80, "intel": 82,
        "era": "ancient",
        "skill": "鳥海柵の勇",
        "lore": "安倍頼時の三男。「鳥海の三郎」。兄・貞任とともに前九年の役を戦い抜く。敗北後、捕虜となって都へ送られた際、梅の花を見て「わが国の 梅の花とは 見つれども 大宮人はいかが言ふらむ」と詠んで貴族たちを感嘆させた。のちに筑前大島へ流され、宗像氏・松浦党に血脈を伝えた。",
        "birthYear": 1032, "deathYear": 1108, "isDaimyo": False
    },
    {
        "id": "off_kiyohara_takenori",
        "name": "清原武則",
        "clanId": "kiyohara",
        "defaultProv": "ugo",
        "military": 88, "politic": 85, "intel": 84,
        "era": "ancient",
        "skill": "山北の覇主",
        "lore": "出羽山北の豪族清原氏の棟梁。前九年の役において、苦戦する源頼義の懇請に応じ一万の大軍を率いて参戦。厨川柵の攻略で決定的な功績を挙げ、安倍氏を滅ぼした。その功により鎮守府将軍に任じられ、奥羽全域にまたがる清原氏一大王国の基礎を築いた。",
        "birthYear": 1010, "deathYear": 1075, "isDaimyo": True
    },
    {
        "id": "off_fujiwara_tsunekiyo",
        "name": "藤原経清",
        "clanId": "fujiwara_hiraizumi",
        "defaultProv": "iwaki",
        "military": 85, "politic": 84, "intel": 85,
        "era": "ancient",
        "skill": "亘理の知将",
        "lore": "藤原秀郷の末裔で亘理権太夫。奥州藤原氏初代・清衡の実父。安倍頼時の娘を妻とし、前九年の役では苦悩の末に安倍方に合流。優れた軍略で国府軍を苦しめたが、厨川柵の陥落時に捕縛され、源頼義により錆びた刀で鋸挽きの刑に処されて悲劇的な討死を遂げた。",
        "birthYear": 1020, "deathYear": 1062, "isDaimyo": False
    },
    {
        "id": "off_fujiwara_kiyohira",
        "name": "藤原清衡",
        "clanId": "fujiwara_hiraizumi",
        "defaultProv": "rikuchu",
        "military": 86, "politic": 92, "intel": 90,
        "era": "ancient",
        "skill": "金色堂の祈念",
        "lore": "奥州藤原氏初代当主。藤原経清の子。前九年・後三年の役の惨劇で一族を失う過酷な試練を生き抜き、奥州六郡・出羽を統一。平泉に本拠を移して中尊寺金色堂を建立し、仏教による非戦・平和郷を建設。百年に及ぶ奥州黄金文化の礎を築いた名君。",
        "birthYear": 1056, "deathYear": 1128, "isDaimyo": True
    },
    {
        "id": "off_taira_masamori",
        "name": "平正盛",
        "clanId": "taira_sadamori",
        "defaultProv": "ise",
        "military": 88, "politic": 84, "intel": 85,
        "era": "ancient",
        "skill": "六波羅の魁",
        "lore": "平正衡の子で平清盛の祖父。白河院政期に院の信頼を獲得し、出雲で反乱を起こした源義親（八幡太郎義家の嫡男）を討伐して一躍天下に名を轟かせた。但馬・丹後・備前守などを歴任し、平氏の受領階級としての経済力と軍事力を飛躍させ、平家台頭の決定的な足がかりを作った。",
        "birthYear": 1065, "deathYear": 1121, "isDaimyo": True
    },
    {
        "id": "off_taira_tadamori",
        "name": "平忠盛",
        "clanId": "taira",
        "defaultProv": "yamashiro",
        "military": 89, "politic": 88, "intel": 87,
        "era": "ancient",
        "skill": "西海鎮撫",
        "lore": "平清盛の父。白河・鳥羽両院に重用され、瀬戸内海の海賊を平定して日宋貿易の端緒を開いた。武士として初めて昇殿を許されるなど朝廷内で異例の出世を遂げ、得長寿院を造営して院の信任を確立。清盛が天下に覇を唱えるための巨大な経済・軍事基盤を完成させた名将。",
        "birthYear": 1096, "deathYear": 1153, "isDaimyo": True
    },
    {
        "id": "off_taira_morikuni",
        "name": "平盛国",
        "clanId": "taira",
        "defaultProv": "bicchu",
        "military": 84, "politic": 86, "intel": 82,
        "era": "heian",
        "skill": "平家の執事",
        "lore": "伊勢平氏の譜代重臣・平盛遠の子。主馬判官。平清盛の最側近・家政の総責任者として活躍し、保元・平治の乱で軍功を挙げた。備中守・日向守などを務め、平家一門の軍事・財政を陰で支えた。壇ノ浦の合戦で捕虜となるも、武士の気節を守り武蔵国で食を断って絶命した。",
        "birthYear": 1113, "deathYear": 1186, "isDaimyo": False
    },
    {
        "id": "off_taira_iesada",
        "name": "平家貞",
        "clanId": "taira",
        "defaultProv": "hyuga",
        "military": 88, "politic": 78, "intel": 80,
        "era": "heian",
        "skill": "第一の郎党",
        "lore": "平忠盛・清盛の二代に仕えた「平家第一の郎党」。筑後守・日向守。保元の乱では清盛の先頭に立って源為朝・頼長軍と戦い、平治の乱でも信西追捕や六波羅警固で武名を挙げた。西国における平家の軍事基盤を確立し、武蔵坊弁慶や東国武士からも恐れられた歴戦の猛将。",
        "birthYear": 1098, "deathYear": 1167, "isDaimyo": False
    },

    # === 中世・戦国・安土桃山・関ヶ原 ===
    {
        "id": "off_sasaki_tsunetaka",
        "name": "佐々木経高",
        "clanId": "gotoba_in",
        "defaultProv": "awaji",
        "military": 82, "politic": 70, "intel": 72,
        "era": "kamakura",
        "skill": "淡路の孤塁",
        "lore": "近江佐々木氏秀義の長男。源頼朝の挙兵に従い淡路・阿波・土佐守護となる。承久の乱では後鳥羽上皇方に味方し、淡路島に拠って幕府軍を迎え撃った。小野盛綱らの幕府軍と激戦の末に城を枕に自害。源平争乱を駆け抜け、最後は朝廷に殉じた誇り高き武士。",
        "birthYear": 1150, "deathYear": 1221, "isDaimyo": False
    },
    {
        "id": "off_sasaki_shigekiyo",
        "name": "佐々木重清",
        "clanId": "gotoba_in",
        "defaultProv": "oki",
        "military": 78, "politic": 68, "intel": 70,
        "era": "kamakura",
        "skill": "隠岐防潮",
        "lore": "隠岐守護・佐々木定綱の子。佐々木一門として隠岐の支配を任される。承久の乱では朝廷方として隠岐・山陰の防備を固め、乱後に隠岐へ配流された後鳥羽上皇の世話と警固に心を配った。日本海の離島にあって朝廷の威光を守り抜いた鎌倉初期の守護武将。",
        "birthYear": 1182, "deathYear": 1245, "isDaimyo": False
    },
    {
        "id": "off_ouchi_noriyuki",
        "name": "大内教幸",
        "clanId": "ouchi",
        "defaultProv": "chikuzen",
        "military": 80, "politic": 74, "intel": 76,
        "era": "muromachi",
        "skill": "西国の鎮護",
        "lore": "大内持盛の子で大内持世の弟。永享の乱前後の大内氏重臣。筑前守護代として博多の貿易と大宰府の防備を統括し、少弐氏や大友氏の侵攻を何度も撃退した。朝鮮・明との貿易航路を確保し、大内氏の西国覇権と国際的通商経済を支えた有能な武将。",
        "birthYear": 1400, "deathYear": 1460, "isDaimyo": False
    },
    {
        "id": "off_hosokawa_mochikata",
        "name": "細川持賢",
        "clanId": "hosokawa",
        "defaultProv": "awaji",
        "military": 82, "politic": 78, "intel": 75,
        "era": "muromachi",
        "skill": "典厩家の祖",
        "lore": "室町幕府管領・細川満元の三男。細川典厩家の初代当主。淡路守護・摂津守護補佐を務め、永享の乱や結城合戦、嘉吉の乱で幕府軍の主力を担った。兄・持之とともに幕政の中枢を支え、四国・瀬戸内海から京都に至る細川宗家の軍事・兵站ルートを確固たるものにした。",
        "birthYear": 1403, "deathYear": 1468, "isDaimyo": False
    },
    {
        "id": "off_kurokawa_harunari",
        "name": "黒川春成",
        "clanId": "ouchi",
        "defaultProv": "buzen",
        "military": 78, "politic": 72, "intel": 75,
        "era": "muromachi",
        "skill": "門司の関守",
        "lore": "大内氏重臣で豊前守護代。門司城・規矩郡を本拠に豊前国の支配を担当。応仁の乱では大内政弘に従って西軍の主力を率いて上洛し、山城・摂津の各地で東軍の細川軍と激闘を繰り広げた。関門海峡の制海権を保持し、大内軍の兵站と背後を守り抜いた忠臣。",
        "birthYear": 1425, "deathYear": 1485, "isDaimyo": False
    },
    {
        "id": "off_aso_ieharu",
        "name": "麻生家春",
        "clanId": "ouchi",
        "defaultProv": "chikuzen",
        "military": 79, "politic": 70, "intel": 74,
        "era": "muromachi",
        "skill": "筑前立花城代",
        "lore": "筑前有力国人麻生氏当主。大内氏に仕えて筑前守護代を務めた。立花山城や若杉山を拠点に少弐氏残党と戦い、博多商人の商業特権を保護。応仁の乱に際しても筑前国内の治安を保ち、大内政弘の遠征軍の後方を安定させた西国の守護代。",
        "birthYear": 1430, "deathYear": 1492, "isDaimyo": False
    },
    {
        "id": "off_monchujo_yasusumi",
        "name": "問註所康純",
        "clanId": "otomo",
        "defaultProv": "chikugo",
        "military": 77, "politic": 73, "intel": 72,
        "era": "muromachi",
        "skill": "筑後の防壁",
        "lore": "鎌倉幕府問注所執事・三善康信の末裔。筑後生葉郡を本拠とする在地領主で大友氏の重臣。応仁の乱期、筑後国において大友氏の勢力を守り、少弐・菊池両氏の干渉を阻止した。一族を挙げて大友家に忠誠を尽くし、筑後における大友支配の楔となった堅実な武将。",
        "birthYear": 1432, "deathYear": 1490, "isDaimyo": False
    },
    {
        "id": "off_oki_tamekiyo",
        "name": "隠岐為清",
        "clanId": "amago",
        "defaultProv": "oki",
        "military": 76, "politic": 75, "intel": 78,
        "era": "sengoku",
        "skill": "島州の治世",
        "lore": "隠岐国守護代・在地領主。甲斐源氏の流れを汲む隠岐氏当主。尼子経久・晴久に服属して隠岐一国の支配を委ねられ、日本海沿岸の廻船交易を押さえて財力を蓄えた。尼子氏衰退後は毛利元就に通じて所領を安堵され、巧みな外交と水軍力で隠岐の独立を守り抜いた。",
        "birthYear": 1515, "deathYear": 1573, "isDaimyo": False
    },
    {
        "id": "off_oki_kiyomasa_sengoku",
        "name": "隠岐清政",
        "clanId": "mori",
        "defaultProv": "oki",
        "military": 74, "politic": 76, "intel": 77,
        "era": "sengoku",
        "skill": "隠岐の水運",
        "lore": "隠岐為清の子。毛利元就・輝元に仕え、隠岐国国人領主として島の防備と日本海航路の警固を担った。文禄・慶長の役では毛利水軍の一翼として兵粮輸送に従軍。関ヶ原合戦後も毛利家の減封に従って長州藩士となり、隠岐氏の家名を江戸時代へと繋いだ。",
        "birthYear": 1545, "deathYear": 1608, "isDaimyo": False
    },
    {
        "id": "off_naito_takaharu",
        "name": "内藤隆春",
        "clanId": "mori",
        "defaultProv": "suo",
        "military": 82, "politic": 88, "intel": 85,
        "era": "sengoku",
        "skill": "防長の柱石",
        "lore": "大内氏重臣・内藤興盛の次男。大内義長敗死後は姉（尾崎局）が毛利隆元に嫁いでいた縁から毛利元就に帰順。長門守護代・且山城主として周防・長門の統治を一任された。大内輝弘の乱では山口を急襲されるも冷静に対処して鎮圧。毛利家の防長支配を確立した大功臣。",
        "birthYear": 1528, "deathYear": 1600, "isDaimyo": False
    },
    {
        "id": "off_ichikawa_tsuneyoshi",
        "name": "市川経好",
        "clanId": "mori",
        "defaultProv": "suo",
        "military": 80, "politic": 86, "intel": 83,
        "era": "sengoku",
        "skill": "高嶺城の守護",
        "lore": "吉川氏一族で毛利元就に仕えた重臣。周防高嶺城代・山口奉行を務め、大内遺領の治安維持と行政を一手に担った。九州遠征中に大内輝弘が山口に侵入した際、留守を預かる妻（市川局）とともに僅かな手勢で城を死守し、毛利軍の反撃を支えた。忠勇義烈を讃えられた名奉行。",
        "birthYear": 1520, "deathYear": 1584, "isDaimyo": False
    },
    {
        "id": "off_naito_motosori",
        "name": "内藤元盛",
        "clanId": "mori",
        "defaultProv": "nagato",
        "military": 83, "politic": 74, "intel": 78,
        "era": "sengoku",
        "skill": "佐野道可の意気",
        "lore": "宍戸元秀の次男で内藤隆春の養子。別名・佐野道可。毛利輝元に仕え長門且山城を守備。大坂の陣に際しては、毛利本家の関与を隠すため浪人「佐野道可」と偽って大坂城に入城し豊臣方に味方した。夏の陣で奮戦後、毛利家への累が及ぶのを防ぐため京都で自害した義士。",
        "birthYear": 1565, "deathYear": 1615, "isDaimyo": False
    },
    {
        "id": "off_masuda_fujikane",
        "name": "益田藤兼",
        "clanId": "mori",
        "defaultProv": "iwami",
        "military": 83, "politic": 80, "intel": 82,
        "era": "sengoku",
        "skill": "七尾城の猛将",
        "lore": "石見の名門領主・益田氏19代当主。七尾城主。当初は大内義隆に従ったが、のちに毛利元就に服属して石見銀山争奪戦などで軍功を重ねた。吉川元春と連携して山陰道を平定し、毛利氏の中国制覇に大きく貢献。晩年は嫡男・元祥に家督を譲り、領内の寺社復興に努めた。",
        "birthYear": 1529, "deathYear": 1597, "isDaimyo": False
    },
    {
        "id": "off_masuda_motoyoshi",
        "name": "益田元祥",
        "clanId": "mori",
        "defaultProv": "iwami",
        "military": 84, "politic": 92, "intel": 88,
        "era": "sengoku",
        "skill": "長州の財政祖",
        "lore": "益田藤兼の嫡男。小田原征伐や朝鮮出兵に従軍し、関ヶ原合戦後は毛利家の防長減封に従って須佐領主となった。長州藩の財政危機に際して永代家老として藩政改革を指揮し、検地や新田開発、財政規律を断行。毛利家三百年の財政基盤を築き上げた長州藩屈指の名家老。",
        "birthYear": 1558, "deathYear": 1640, "isDaimyo": False
    },
    {
        "id": "off_masaki_yoritada",
        "name": "正木頼忠",
        "clanId": "satomi",
        "defaultProv": "kazusa",
        "military": 82, "politic": 78, "intel": 76,
        "era": "sengoku",
        "skill": "大多喜の剛将",
        "lore": "里見氏重臣・正木時茂の弟。勝浦城主・大多喜城主を務め、後北条氏の侵攻から上総を守り抜いた。娘の養珠院（お万の方）は徳川家康の側室となり、紀州徳川頼宣・水戸徳川頼房の生母となった。里見家の屋台骨を支え、のちに徳川家とも深い縁を結んだ名将。",
        "birthYear": 1551, "deathYear": 1622, "isDaimyo": False
    },

    # === 江戸時代 1789年（寛政の改革期） ===
    {
        "id": "off_kyogoku_takawaki",
        "name": "京極高備",
        "clanId": "tokugawa",
        "defaultProv": "tango",
        "military": 65, "politic": 84, "intel": 80,
        "era": "edo",
        "skill": "峰山の治政",
        "lore": "丹後峰山藩第6代藩主。松平定信の寛政の改革に参画し、若年寄を務めて幕政を支えた。領内では名産品「丹後ちりめん」の保護・育成に力を注ぎ、機業の振興によって藩財政を潤した。凶作に備えた義倉の設置など民政に尽力し、名君として領民から深く敬愛された。",
        "birthYear": 1757, "deathYear": 1835, "isDaimyo": False
    },
    {
        "id": "off_sengoku_hisamichi",
        "name": "仙石久道",
        "clanId": "tokugawa",
        "defaultProv": "tajima",
        "military": 68, "politic": 82, "intel": 78,
        "era": "edo",
        "skill": "出石の文治",
        "lore": "但馬出石藩第5代藩主。仙石秀久の血を引く。松平定信の推挙により奏者番を務める。藩校「弘道館」を開設して文武を奨励し、領内の特産品「出石焼」の保護育成や治水事業を推進した。質素倹約を率先垂範して藩政を立て直した名藩主。",
        "birthYear": 1774, "deathYear": 1834, "isDaimyo": False
    },
    {
        "id": "off_kamei_koresada",
        "name": "亀井矩貞",
        "clanId": "tokugawa",
        "defaultProv": "iwami",
        "military": 66, "politic": 85, "intel": 82,
        "era": "edo",
        "skill": "津和野の養正",
        "lore": "石見津和野藩第7代藩主。名門亀井家当主。藩校「養老館」を創設して国学・医学・軍学の教育を推進し、西周や森鴎外を輩出する津和野の学問的土壌を築いた。寛政の改革に呼応して倹約令と備蓄米の制度を整え、石見の山間部における民政安定に尽くした。",
        "birthYear": 1761, "deathYear": 1819, "isDaimyo": False
    },
    {
        "id": "off_miura_maetsugu",
        "name": "三浦前次",
        "clanId": "tokugawa",
        "defaultProv": "mimasaka",
        "military": 67, "politic": 80, "intel": 76,
        "era": "edo",
        "skill": "勝山の仁政",
        "lore": "美作勝山藩第2代藩主。三浦明次の長男。奏者番として江戸城中で勤務しつつ、領内では天明の大飢饉からの復興を指揮した。倹約を徹底し年貢の負担軽減を図るとともに、義倉を整備して凶作に備えるなど、領民の救済と地域社会の再建に生涯を捧げた。",
        "birthYear": 1759, "deathYear": 1826, "isDaimyo": False
    },
    {
        "id": "off_matsudaira_yoritaka_sanuki",
        "name": "松平頼謙",
        "clanId": "tokugawa",
        "defaultProv": "sanuki",
        "military": 70, "politic": 86, "intel": 82,
        "era": "edo",
        "skill": "讃岐の英明",
        "lore": "讃岐高松藩第6代藩主。水戸徳川家の血筋。天明の大飢饉に直面すると、自ら率先して倹約を行い、領民救済のために蔵米を放出した。藩校「講道館」を拡張して学問を振興し、栗林荘（栗林公園）の修築を行うなど、文化・行政の両面で高松藩中興の治世を築いた。",
        "birthYear": 1755, "deathYear": 1806, "isDaimyo": False
    },
    {
        "id": "off_matsudaira_chikasada",
        "name": "松平親貞",
        "clanId": "tokugawa",
        "defaultProv": "bungo",
        "military": 65, "politic": 83, "intel": 80,
        "era": "edo",
        "skill": "杵築の学林",
        "lore": "豊後杵築藩第6代藩主。能見松平家当主。藩校「学習館」を開校して藩士のみならず領民の教育にも門戸を開き、文教政策を強力に推進した。天明の飢饉では救済策を迅速に講じ、豊後湾の海防警備と沿岸警備の強化にも力を尽くした名君。",
        "birthYear": 1751, "deathYear": 1803, "isDaimyo": False
    },
    {
        "id": "off_kabayama_hisatomo",
        "name": "樺山久言",
        "clanId": "shimazu",
        "defaultProv": "osumi",
        "military": 78, "politic": 85, "intel": 80,
        "era": "edo",
        "skill": "薩南の宿老",
        "lore": "薩摩藩家老で大隅給領主。島津重豪・斉宣の二代に仕えた名家老。大隅半島の防備と治水開墾を統括し、調所広郷に先立って財政健全化の基盤作りに取り組んだ。名門樺山家の当主として家中武士の規律粛正と領内農村の復興を推進した薩摩屈指の重鎮。",
        "birthYear": 1750, "deathYear": 1818, "isDaimyo": False
    },
    {
        "id": "off_matsudaira_naotsune",
        "name": "松平直恒",
        "clanId": "tokugawa",
        "defaultProv": "oki",
        "military": 68, "politic": 84, "intel": 78,
        "era": "edo",
        "skill": "隠岐管見",
        "lore": "出雲松江藩第6代藩主。松平不昧（治郷）の養父。幕府より隠岐国の預かり支配を命じられ、隠岐島民の生活安定と回船通商の統制に意を用いた。松江城下の治水と藩財政再建にも取り組み、のちに不昧が推進する名高い藩政改革の礎を築いた。",
        "birthYear": 1762, "deathYear": 1820, "isDaimyo": False
    },
    {
        "id": "off_inada_toshitane",
        "name": "稲田敏植",
        "clanId": "tokugawa",
        "defaultProv": "awaji",
        "military": 76, "politic": 86, "intel": 82,
        "era": "edo",
        "skill": "洲本城代の誉",
        "lore": "徳島藩筆頭家老・洲本城代（一万四千石）。淡路一国の統治を一任され、洲本城下町の整備や農業・水産業の振興に尽力した。寛政の改革に呼応して藩士の風紀刷新と文武奨励を行い、淡路島民から領主として深く慕われた。明治の庚午事変に至る稲田家の名声を高めた重臣。",
        "birthYear": 1756, "deathYear": 1824, "isDaimyo": False
    }
]

print(f"Total new historical officers defined: {len(HISTORICAL_NEW_OFFICERS)}")
