# -*- coding: utf-8 -*-
"""
平安時代（1028, 1056, 1087）の全城代を埋めるための実在受領・武将データセット。
各人物の生没年を正確に設定し、重厚な史実列伝を付与する。
"""

HEIAN_HISTORICAL_OFFICERS = [
    # --- 1028年〜1056年〜1087年期の実在受領・公卿・武将 ---
    {
        "id": "off_fujiwara_yorimichi",
        "name": "藤原頼通",
        "clanId": "heian_court",
        "defaultProv": "yamashiro",
        "military": 75, "politic": 95, "intel": 90,
        "era": "ancient",
        "skill": "鳳凰堂の栄華",
        "lore": "藤原道長の嫡男。後一条・後朱雀・後冷泉の三代天皇の関白を半世紀にわたり務め、摂関政治の極盛期を維持した大政治家。宇治に平等院鳳凰堂を建立し、浄土信仰に基づく王朝文化を花開かせた。平忠常の乱の追討や前九年の役の戦局を見守り、平安朝の絶頂期を統率した。",
        "birthYear": 992, "deathYear": 1074, "isDaimyo": False
    },
    {
        "id": "off_fujiwara_norimichi",
        "name": "藤原教通",
        "clanId": "heian_court",
        "defaultProv": "yamato",
        "military": 72, "politic": 92, "intel": 86,
        "era": "ancient",
        "skill": "摂関の輔弼",
        "lore": "藤原道長の五男。兄・頼通の跡を継いで関白・太政大臣を務めた。内大臣・右大臣を歴任し、朝廷の政務を長年にわたり統括。後三条天皇の即位に際しても摂関家の重鎮として朝政を支え、荘園整理令への対応や朝儀の整備に尽力して平安後期の貴族社会を指導した。",
        "birthYear": 996, "deathYear": 1075, "isDaimyo": False
    },
    {
        "id": "off_fujiwara_yorimune",
        "name": "藤原頼宗",
        "clanId": "heian_court",
        "defaultProv": "settsu",
        "military": 70, "politic": 88, "intel": 84,
        "era": "ancient",
        "skill": "中御門の祖",
        "lore": "藤原道長の次男。中御門流の祖。右大臣として兄・頼通を補佐し、朝政の枢要に参画した。有職故実に通じた碩学として知られ、朝廷の儀礼や受領補任の公正な執行に尽力。多くの受領や武士と良好な関係を結び、平安中期の摂関政治の安定に大きく貢献した。",
        "birthYear": 993, "deathYear": 1065, "isDaimyo": False
    },
    {
        "id": "off_fujiwara_yoshinobu",
        "name": "藤原能信",
        "clanId": "heian_court",
        "defaultProv": "tamba",
        "military": 76, "politic": 89, "intel": 88,
        "era": "ancient",
        "skill": "大覚寺大納言",
        "lore": "藤原道長の四男。権大納言。気骨ある公卿として知られ、頼通・教通と対立しつつも後三条天皇の擁立を主導した名臣。受領層の武士たちと深く結びつき、東国や畿内の軍事・財政に通暁。院政期へと向かう歴史の転換点において決定的な役割を果たした。",
        "birthYear": 995, "deathYear": 1065, "isDaimyo": False
    },
    {
        "id": "off_oe_no_masafusa",
        "name": "大江匡房",
        "clanId": "heian_court",
        "defaultProv": "harima",
        "military": 82, "politic": 94, "intel": 96,
        "era": "ancient",
        "skill": "江家の兵法",
        "lore": "大江匡衡の曾孫。当代無双の大学者にして軍略家。白河院政の最高顧問・権中納言・大宰権帥。八幡太郎義家に兵法を授けた師として名高く、『闘戦経』等の軍書に通じた。西国の治安維持や防備、日宋貿易の振興に尽力し、文武両道をもって武家社会の形成に絶大な影響を与えた。",
        "birthYear": 1041, "deathYear": 1111, "isDaimyo": False
    },
    {
        "id": "off_minamoto_morofusa",
        "name": "源師房",
        "clanId": "heian_court",
        "defaultProv": "north_omi",
        "military": 74, "politic": 90, "intel": 85,
        "era": "ancient",
        "skill": "村上源氏の祖",
        "lore": "具平親王の長男で村上源氏の祖。太政大臣。藤原道長の猶子となって摂関家と結び、村上源氏発展の強固な礎を築いた。受領層の源氏・平氏武士団に人望厚く、近江・美濃などの要衝の受領を親族に配して治安を維持。宮中において摂関家に次ぐ大勢力を形成した。",
        "birthYear": 1008, "deathYear": 1077, "isDaimyo": False
    },
    {
        "id": "off_minamoto_toshifusa",
        "name": "源俊房",
        "clanId": "heian_court",
        "defaultProv": "south_omi",
        "military": 75, "politic": 91, "intel": 88,
        "era": "ancient",
        "skill": "久我左大臣",
        "lore": "源師房の長男。久我流の祖。左大臣として白河上皇の院政草創期を支えた。理財に長け、朝廷財政の再建と地方受領の監察を厳格に実施。公家社会の長老として重きをなし、源義家ら武家源氏とも良好な協調関係を維持して都の治安安定に尽くした。",
        "birthYear": 1035, "deathYear": 1121, "isDaimyo": False
    },
    {
        "id": "off_minamoto_akifusa",
        "name": "源顕房",
        "clanId": "heian_court",
        "defaultProv": "echizen",
        "military": 78, "politic": 90, "intel": 86,
        "era": "ancient",
        "skill": "六条右大臣",
        "lore": "源師房の次男。右大臣。娘の賢子が白河天皇の皇后（堀河天皇の生母）となったことで院政期における外戚の地位を確立した。越前・尾張等の大国の受領を歴任し、北陸道の経済・通商を統轄。武士層への理解も深く、王朝権力と武家勢力の調停に活躍した。",
        "birthYear": 1037, "deathYear": 1094, "isDaimyo": False
    },
    {
        "id": "off_minamoto_yoritsuna",
        "name": "源頼綱",
        "clanId": "minamoto_tsunemoto",
        "defaultProv": "settsu",
        "military": 82, "politic": 84, "intel": 85,
        "era": "ancient",
        "skill": "多田の歌将",
        "lore": "源頼国の五男。多田源氏4代。摂津守・丹後守。多田院を中心に広大な武士団を統率する一方、勅撰歌人としても名高く「多田蔵人」と称された。白河院に近仕して近畿・山陰の治安維持にあたり、後三年の役期には源氏一門の京洛における地位を保全した知勇の武将。",
        "birthYear": 1025, "deathYear": 1097, "isDaimyo": False
    },
    {
        "id": "off_fujiwara_morozane",
        "name": "藤原師実",
        "clanId": "heian_court",
        "defaultProv": "yamashiro",
        "military": 70, "politic": 93, "intel": 88,
        "era": "ancient",
        "skill": "京極関白",
        "lore": "藤原頼通の長男。白河天皇・堀河天皇の関白・太政大臣。院政の開始に伴い摂関家の権勢が陰りを見せる中、柔和な人柄と卓越した政治手腕で白河上皇と協調。後三年の役の善後策など東国・北方の紛争調停にあたり、摂関家の格式と領地を守護した。",
        "birthYear": 1042, "deathYear": 1101, "isDaimyo": False
    },
    {
        "id": "off_shirakawa_in",
        "name": "白河上皇",
        "clanId": "heian_court",
        "defaultProv": "yamashiro",
        "military": 85, "politic": 96, "intel": 92,
        "era": "ancient",
        "skill": "治天の君",
        "lore": "第72代天皇。譲位後に「院政」を開始し、四十余年にわたり専制君主（治天の君）として君臨した巨星。「賀茂川の水、双六の賽、山法師」を意のままにならぬ天下三大不如意と嘆いた。北面の武士を創設して平正盛・忠盛を登用し、武士台頭の決定的な契機を作った。",
        "birthYear": 1053, "deathYear": 1129, "isDaimyo": True
    },
    {
        "id": "off_fujiwara_munetada",
        "name": "藤原宗忠",
        "clanId": "heian_court",
        "defaultProv": "bizen",
        "military": 72, "politic": 88, "intel": 91,
        "era": "ancient",
        "skill": "中右記の筆",
        "lore": "右大臣。平安後期の公卿で日記『中右記』の作者。備前守などの受領を務め、院政期の政治・社会の詳細な記録を残した。源義家・義綱の動向や平正盛の抜擢、地方武士の蜂起など当代の大事件を公正な視点で克明に書き留め、歴史研究における不朽の金字塔を打ち立てた。",
        "birthYear": 1062, "deathYear": 1141, "isDaimyo": False
    },
    {
        "id": "off_taira_koremau",
        "name": "平維茂",
        "clanId": "heian_court",
        "defaultProv": "echigo",
        "military": 88, "politic": 76, "intel": 78,
        "era": "ancient",
        "skill": "余五将軍",
        "lore": "平繁盛の子で貞盛の養子。「余五将軍」と称された坂東平氏屈指の猛将。越後守・下総守を歴任。陸奥守の藤原諸成と結んで平忠常の乱の平定に功を挙げ、越後城氏や越後平氏の祖となった。謡曲『紅葉狩』の鬼女退治伝説でも知られる剛勇の武人。",
        "birthYear": 960, "deathYear": 1030, "isDaimyo": False
    },
    {
        "id": "off_taira_tsunemasa_anc",
        "name": "平常将",
        "clanId": "taira_masakado",
        "defaultProv": "kazusa",
        "military": 80, "politic": 75, "intel": 74,
        "era": "ancient",
        "skill": "房総の棟梁",
        "lore": "平忠常の長男。平忠常の乱では父とともに上総・下総の軍勢を率いて朝廷軍と激戦を繰り広げた。乱の終息後は源頼信に臣従し、房総平氏の血統を守り抜いた。その子孫から千葉氏・上総氏が勃興し、鎌倉幕府創業を支える東国有力御家人団の礎となった。",
        "birthYear": 995, "deathYear": 1060, "isDaimyo": False
    },
    {
        "id": "off_taira_tsunehira",
        "name": "平常衡",
        "clanId": "taira_masakado",
        "defaultProv": "shimousa",
        "military": 82, "politic": 76, "intel": 75,
        "era": "ancient",
        "skill": "下総の守護神",
        "lore": "平常将の長男で千葉氏・上総氏の祖父。下総国印旛郡を拠点に在地武士団を再編し、前九年の役・後三年の役期に源頼義・義家父子に従って出陣。武功を重ねて武門としての家格を向上させ、坂東における平氏武士団の不動の勢力基盤を確立した。",
        "birthYear": 1025, "deathYear": 1088, "isDaimyo": False
    },
    {
        "id": "off_kiyohara_takehira",
        "name": "清原武衡",
        "clanId": "kiyohara",
        "defaultProv": "ugo",
        "military": 80, "politic": 72, "intel": 76,
        "era": "ancient",
        "skill": "金沢柵の防戦",
        "lore": "清原武則の孫で清原武貞の弟。後三年の役において甥の清原家衡を擁護して金沢柵に拠り、源義家・藤原清衡連合軍の猛攻に頑強に抵抗した。難攻不落の城柵で冬の豪雪まで持ち堪えたが、兵糧攻めに遭って陥落、捕縛されて斬首された。出羽清原氏最後の意地を示した勇士。",
        "birthYear": 1050, "deathYear": 1087, "isDaimyo": False
    },
    {
        "id": "off_kiyohara_iehira",
        "name": "清原家衡",
        "clanId": "kiyohara",
        "defaultProv": "rikuchu",
        "military": 82, "politic": 70, "intel": 74,
        "era": "ancient",
        "skill": "沼柵の猛威",
        "lore": "清原武貞の次男。後三年の役の当事者。異父兄・藤原清衡と対立し、叔父・武衡とともに沼柵・金沢柵で源義家軍を撃退。豪雪の中、飢えと凍えに苦しむ義家軍を大敗させた。最後は義家の兵糧攻めの前に敗れ討死。奥羽の覇権を激しく争った山北の猛将。",
        "birthYear": 1055, "deathYear": 1087, "isDaimyo": False
    },
    {
        "id": "off_tomo_no_kanezada",
        "name": "伴兼貞",
        "clanId": "shimazu_proto",
        "defaultProv": "osumi",
        "military": 76, "politic": 78, "intel": 74,
        "era": "ancient",
        "skill": "大隅弁済使",
        "lore": "伴兼行の孫。大隅弁済使として薩摩・大隅の荘園経営と在地武士団の統率を強化し、肝付氏の基礎を固めた。南九州の有力領主として国衙と協調しつつ独自の自立体制を維持し、島津荘の拡大期にあっても揺るぎない地盤を守り抜いた名領主。",
        "birthYear": 1020, "deathYear": 1085, "isDaimyo": False
    },
    {
        "id": "off_kikuchi_fusasumi",
        "name": "菊池経隆",
        "clanId": "kikuchi",
        "defaultProv": "higo",
        "military": 80, "politic": 76, "intel": 75,
        "era": "ancient",
        "skill": "菊池の武威",
        "lore": "肥後菊池氏の祖・則隆の嫡男。肥後国菊池郡に拠点を構え、大宰府の指揮下で九州の治安維持にあたった。前九年・後三年の役期に西国武士団としての実力を誇示し、後の菊池武時・武光へと至る九州屈指の勤皇武家・菊池氏の土台を築き上げた。",
        "birthYear": 1035, "deathYear": 1098, "isDaimyo": False
    }
]

print(f"Total Heian historical officers defined: {len(HEIAN_HISTORICAL_OFFICERS)}")
