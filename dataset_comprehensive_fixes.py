# -*- coding: utf-8 -*-
"""
全残存ギャップ完全解消データセット
30シナリオ×全大名家の150年生存を保証する追加武将
"""

COMPREHENSIVE_GAP_FIXES = [
    # ============================================================
    # 安倍家 (abe) Gap: (1109, 1178)
    # 既存: 安倍宗任(1032-1108) が最後
    # ============================================================
    {"id": "off_abe_muneto_son", "name": "安倍宗良", "clanId": "abe", "defaultProv": "rikuchu",
     "military": 72, "politic": 75, "intel": 73, "era": "heian", "skill": "安倍一門",
     "comment": "安倍宗任の子。奥州の地で安倍氏の血脈を守る", "lore": "父宗任の遺志を継ぎ、九州の地で安倍一族の存続に尽力。",
     "birthYear": 1080, "deathYear": 1145},
    {"id": "off_abe_munetsugu", "name": "安倍宗継", "clanId": "abe", "defaultProv": "rikuchu",
     "military": 70, "politic": 74, "intel": 72, "era": "heian", "skill": "安倍末裔",
     "comment": "安倍宗良の嫡男。安倍一門の再興を図る", "lore": "安倍氏の家名を保ち、後の松浦党に繋がる系譜を守った。",
     "birthYear": 1115, "deathYear": 1180},

    # ============================================================
    # 蝦夷諸部族 (ezo_native) Gap: (1111, 1140)
    # 既存: 蝦夷族長(1040-1110) が最後の該当期間武将
    # ============================================================
    {"id": "off_ezo_chief_3", "name": "蝦夷酋長(三代)", "clanId": "ezo_native", "defaultProv": "ezo",
     "military": 75, "politic": 70, "intel": 68, "era": "heian", "skill": "蝦夷統率",
     "comment": "蝦夷の有力酋長。北方交易を統括", "lore": "アイヌ諸部族を束ね、本州との交易路を維持した族長。",
     "birthYear": 1080, "deathYear": 1145},

    # ============================================================
    # 藤原秀郷軍 (fujiwara_hidesato) Gap: (1103, 1237)
    # 既存: 最終 D:1102付近で途切れ → 1156シナリオの武将に繋がらない
    # ============================================================
    {"id": "off_hidesato_succ_3", "name": "藤原秀衡(祖)", "clanId": "fujiwara_hidesato", "defaultProv": "shimotsuke",
     "military": 73, "politic": 78, "intel": 76, "era": "heian", "skill": "秀郷流嫡流",
     "comment": "藤原秀郷流の嫡裔。下野国を本拠とする", "lore": "秀郷流藤原氏の正統を継ぎ、武蔵・下野の基盤を固めた。",
     "birthYear": 1075, "deathYear": 1140},
    {"id": "off_hidesato_succ_4", "name": "藤原秀澄", "clanId": "fujiwara_hidesato", "defaultProv": "shimotsuke",
     "military": 72, "politic": 76, "intel": 75, "era": "heian", "skill": "下野豪族",
     "comment": "秀郷流の中核。結城・小山氏の祖先筋", "lore": "下野国の有力豪族として院政期の政争に関与した。",
     "birthYear": 1115, "deathYear": 1180},
    {"id": "off_hidesato_succ_5", "name": "小山政光", "clanId": "fujiwara_hidesato", "defaultProv": "shimotsuke",
     "military": 78, "politic": 80, "intel": 77, "era": "kamakura", "skill": "小山初代",
     "comment": "秀郷流小山氏初代。源頼朝の挙兵に呼応", "lore": "野木宮合戦で功を立て、下野守護に任じられた名将。",
     "birthYear": 1150, "deathYear": 1215},
    {"id": "off_oyama_tomomasa", "name": "小山朝政", "clanId": "fujiwara_hidesato", "defaultProv": "shimotsuke",
     "military": 80, "politic": 82, "intel": 78, "era": "kamakura", "skill": "下野守護",
     "comment": "小山政光の嫡男。承久の乱で幕府方", "lore": "鎌倉幕府の有力御家人として下野守護を世襲した。",
     "birthYear": 1178, "deathYear": 1238},

    # ============================================================
    # 平安朝廷 (heian_court) Gap: (1102, 1237)
    # ============================================================
    {"id": "off_heian_court_succ3", "name": "白河法皇", "clanId": "heian_court", "defaultProv": "yamashiro",
     "military": 65, "politic": 95, "intel": 90, "era": "heian", "skill": "院政の祖",
     "comment": "第72代天皇。院政を創始した絶大な権力者", "lore": "「賀茂河の水、双六の賽、山法師」以外は意のままと豪語した院政の創始者。",
     "birthYear": 1053, "deathYear": 1129},
    {"id": "off_heian_court_toba", "name": "鳥羽上皇", "clanId": "heian_court", "defaultProv": "yamashiro",
     "military": 60, "politic": 88, "intel": 85, "era": "heian", "skill": "治天の君",
     "comment": "第74代天皇。白河院の後を継ぎ院政を行う", "lore": "保元の乱の遠因を作りつつも、院政体制を確立した。",
     "birthYear": 1103, "deathYear": 1156},
    {"id": "off_heian_court_goshira", "name": "後白河院", "clanId": "heian_court", "defaultProv": "yamashiro",
     "military": 55, "politic": 92, "intel": 93, "era": "heian", "skill": "日本一の大天狗",
     "comment": "第77代天皇。保元・平治の乱を経て院政を行う", "lore": "源平争乱の時代を巧みに生き抜き「日本一の大天狗」と呼ばれた名政治家。",
     "birthYear": 1127, "deathYear": 1192},
    {"id": "off_heian_court_gotoba", "name": "後鳥羽上皇(朝廷)", "clanId": "heian_court", "defaultProv": "yamashiro",
     "military": 70, "politic": 88, "intel": 85, "era": "kamakura", "skill": "承久の変",
     "comment": "第82代天皇。承久の乱を起こした武闘派帝王", "lore": "文武に秀で、新古今和歌集を編纂。承久の乱で幕府に挑んだ。",
     "birthYear": 1180, "deathYear": 1239},

    # ============================================================
    # 本間家 (honma) Gap: (1096, 1134)
    # 既存: D:1090付近で途切れ → 宗清則 G:1135
    # ============================================================
    {"id": "off_honma_succ_1080", "name": "本間忠兼", "clanId": "honma", "defaultProv": "sado",
     "military": 70, "politic": 73, "intel": 71, "era": "heian", "skill": "佐渡本間",
     "comment": "佐渡本間氏の中興。佐渡国内の所領を拡大", "lore": "院政期の佐渡において本間一族の結束を固めた。",
     "birthYear": 1068, "deathYear": 1135},

    # ============================================================
    # 菊池家 (kikuchi) Gap: (1116, 1140)
    # 既存: D:1100付近 → 菊池経宗 G:1141
    # ============================================================
    {"id": "off_kikuchi_succ_1090", "name": "菊池経頼", "clanId": "kikuchi", "defaultProv": "higo",
     "military": 72, "politic": 75, "intel": 73, "era": "heian", "skill": "肥後菊池",
     "comment": "菊池氏の中継ぎ当主。肥後国の基盤を維持", "lore": "院政期に菊池荘の荘園経営を安定させた。",
     "birthYear": 1085, "deathYear": 1145},

    # ============================================================
    # 清原家 (kiyohara) Gap: (1129, 1237)
    # 既存: 清原家(主家)最終 D:1128付近
    # ============================================================
    {"id": "off_kiyohara_succ_3", "name": "清原清衡(末裔)", "clanId": "kiyohara", "defaultProv": "dewa",
     "military": 70, "politic": 75, "intel": 73, "era": "heian", "skill": "出羽清原",
     "comment": "清原氏の残党。出羽に蟄居して家名を保つ", "lore": "後三年の役後も出羽の地に残り、清原氏の血脈を繋いだ。",
     "birthYear": 1100, "deathYear": 1165},
    {"id": "off_kiyohara_succ_4", "name": "清原真衡(末裔)", "clanId": "kiyohara", "defaultProv": "dewa",
     "military": 68, "politic": 73, "intel": 72, "era": "kamakura", "skill": "出羽一族",
     "comment": "清原末裔。出羽国の在地領主として存続", "lore": "鎌倉幕府のもとで出羽の在地領主として家名を保った。",
     "birthYear": 1140, "deathYear": 1210},
    {"id": "off_kiyohara_succ_5", "name": "清原保衡(末裔)", "clanId": "kiyohara", "defaultProv": "dewa",
     "military": 67, "politic": 72, "intel": 71, "era": "kamakura", "skill": "清原残党",
     "comment": "清原氏末裔。承久の乱後も出羽に存続", "lore": "承久の乱以降も出羽の片隅で清原氏の家名を守り続けた。",
     "birthYear": 1180, "deathYear": 1240},

    # ============================================================
    # 清原家衡 (kiyohara_iehira) Gap: (1093, 1237)
    # ============================================================
    {"id": "off_iehira_succ_1", "name": "清原光衡", "clanId": "kiyohara_iehira", "defaultProv": "dewa",
     "military": 68, "politic": 72, "intel": 70, "era": "heian", "skill": "家衡残党",
     "comment": "清原家衡の残党。出羽で潜伏して家名を保つ", "lore": "後三年の役で敗れたが、一族の生き残りが出羽に潜伏した。",
     "birthYear": 1070, "deathYear": 1135},
    {"id": "off_iehira_succ_2", "name": "清原武衡(末裔)", "clanId": "kiyohara_iehira", "defaultProv": "dewa",
     "military": 67, "politic": 71, "intel": 70, "era": "heian", "skill": "出羽残党",
     "comment": "家衡流末裔。出羽の地で生き延びる", "lore": "源氏の追及を逃れ、出羽山中に隠棲して血脈を保った。",
     "birthYear": 1110, "deathYear": 1175},
    {"id": "off_iehira_succ_3", "name": "清原家重", "clanId": "kiyohara_iehira", "defaultProv": "dewa",
     "military": 66, "politic": 70, "intel": 69, "era": "kamakura", "skill": "出羽在地",
     "comment": "家衡流末裔。鎌倉期に在地領主として存続", "lore": "鎌倉幕府の御家人として出羽の小領主を務めた。",
     "birthYear": 1150, "deathYear": 1215},
    {"id": "off_iehira_succ_4", "name": "清原家長", "clanId": "kiyohara_iehira", "defaultProv": "dewa",
     "military": 65, "politic": 70, "intel": 68, "era": "kamakura", "skill": "家衡裔",
     "comment": "家衡流末裔。承久の乱期に存続を確保", "lore": "鎌倉中期の出羽において清原一門の存続を全うした。",
     "birthYear": 1190, "deathYear": 1245},

    # ============================================================
    # 源経基軍 (minamoto_tsunemoto) Gap: (1128, 1237)
    # 既存: D:1127付近で途切れ
    # ============================================================
    {"id": "off_tsunemoto_succ_3", "name": "源義家(末裔)", "clanId": "minamoto_tsunemoto", "defaultProv": "kawachi",
     "military": 75, "politic": 78, "intel": 76, "era": "heian", "skill": "源氏嫡流",
     "comment": "源義家の系譜を引く河内源氏の一門", "lore": "河内源氏の嫡流として武家の棟梁の家格を維持した。",
     "birthYear": 1100, "deathYear": 1165},
    {"id": "off_tsunemoto_succ_4", "name": "源義朝(経基流)", "clanId": "minamoto_tsunemoto", "defaultProv": "kawachi",
     "military": 82, "politic": 78, "intel": 75, "era": "heian", "skill": "保元の功臣",
     "comment": "源為義の嫡男。保元の乱で父と敵対した悲劇の武将", "lore": "保元・平治の乱を戦い、源氏再興の礎を築いた猛将。",
     "birthYear": 1123, "deathYear": 1160},
    {"id": "off_tsunemoto_yoritomo", "name": "源頼朝(経基流)", "clanId": "minamoto_tsunemoto", "defaultProv": "sagami",
     "military": 78, "politic": 95, "intel": 90, "era": "kamakura", "skill": "鎌倉殿",
     "comment": "征夷大将軍。鎌倉幕府を開いた日本史上最大の英雄の一人", "lore": "流人の身から天下を取り、武家政権を打ち立てた。",
     "birthYear": 1147, "deathYear": 1199},
    {"id": "off_tsunemoto_sanetomo", "name": "源実朝(経基流)", "clanId": "minamoto_tsunemoto", "defaultProv": "sagami",
     "military": 60, "politic": 75, "intel": 82, "era": "kamakura", "skill": "歌人将軍",
     "comment": "鎌倉幕府第三代将軍。金槐和歌集の作者", "lore": "武家の棟梁にして稀代の歌人。鶴岡八幡宮で悲劇の最期を遂げた。",
     "birthYear": 1192, "deathYear": 1219},
    {"id": "off_tsunemoto_succ_7", "name": "源頼茂", "clanId": "minamoto_tsunemoto", "defaultProv": "sagami",
     "military": 72, "politic": 70, "intel": 68, "era": "kamakura", "skill": "源氏門葉",
     "comment": "源頼朝の甥筋。源氏門葉として鎌倉に仕える", "lore": "実朝暗殺後の源氏嫡流断絶後も、門葉として家名を保った。",
     "birthYear": 1203, "deathYear": 1238},

    # ============================================================
    # 大友家 (otomo) Gap: (1101, 1140)
    # 既存: 近藤能成 D:1100, 次: 大友能直 G:1141
    # ============================================================
    {"id": "off_otomo_succ_1085", "name": "中原親能(祖)", "clanId": "otomo", "defaultProv": "bungo",
     "military": 68, "politic": 76, "intel": 74, "era": "heian", "skill": "大友先祖",
     "comment": "大友氏の祖先筋。豊後国の在地豪族", "lore": "院政期の豊後において大友氏の前身となる勢力を形成した。",
     "birthYear": 1078, "deathYear": 1142},

    # ============================================================
    # 日向薩摩豪族 (shimazu_proto) Gap: (1106, 1237)
    # 既存: 肝付兼俊 D:1105 → 島津久経 G:1240
    # ============================================================
    {"id": "off_shimazu_proto_succ3", "name": "大隅豪族(三代)", "clanId": "shimazu_proto", "defaultProv": "osumi",
     "military": 72, "politic": 73, "intel": 70, "era": "heian", "skill": "大隅国人",
     "comment": "大隅国の有力豪族。島津荘の開発に関与", "lore": "院政期の大隅において荘園経営と在地勢力の維持に努めた。",
     "birthYear": 1078, "deathYear": 1142},
    {"id": "off_shimazu_proto_succ4", "name": "惟宗忠久(祖)", "clanId": "shimazu_proto", "defaultProv": "osumi",
     "military": 74, "politic": 76, "intel": 73, "era": "kamakura", "skill": "島津荘荘官",
     "comment": "島津荘の荘官。後の島津氏の祖先筋", "lore": "島津荘の管理を通じて薩摩・大隅の基盤を築いた。",
     "birthYear": 1118, "deathYear": 1185},
    {"id": "off_shimazu_proto_tadahisa", "name": "島津忠久(祖)", "clanId": "shimazu_proto", "defaultProv": "satsuma",
     "military": 78, "politic": 82, "intel": 78, "era": "kamakura", "skill": "島津氏祖",
     "comment": "島津氏初代。源頼朝より薩摩・大隅・日向守護に任ぜられる", "lore": "頼朝の落胤とも伝えられ、島津荘の地頭から三カ国守護に登りつめた。",
     "birthYear": 1157, "deathYear": 1227},

    # ============================================================
    # 宗家 (so) Gap: (1091, 1134)
    # 既存: 宗知宗 D:1090 → 宗清則 G:1135
    # ============================================================
    {"id": "off_so_succ_1075", "name": "宗重宗", "clanId": "so", "defaultProv": "tsushima",
     "military": 70, "politic": 73, "intel": 71, "era": "heian", "skill": "対馬守護代",
     "comment": "対馬宗氏の中継ぎ当主。対馬の交易を管理", "lore": "院政期の対馬において日朝交易の基盤を維持した。",
     "birthYear": 1068, "deathYear": 1135},

    # ============================================================
    # 平将門軍 (taira_masakado) Gap: (1099, 1237)
    # 既存: 平常長 D:1098 → 1156シナリオ以降の武将に繋がらない
    # ============================================================
    {"id": "off_masakado_succ_3", "name": "平常澄", "clanId": "taira_masakado", "defaultProv": "shimousa",
     "military": 74, "politic": 73, "intel": 71, "era": "heian", "skill": "千葉介",
     "comment": "千葉氏の祖。平常長の子で下総国の有力豪族", "lore": "千葉庄を本拠に勢力を拡大し、千葉介を称した。",
     "birthYear": 1073, "deathYear": 1132},
    {"id": "off_masakado_succ_4", "name": "千葉常重", "clanId": "taira_masakado", "defaultProv": "shimousa",
     "military": 72, "politic": 75, "intel": 73, "era": "heian", "skill": "下総権介",
     "comment": "千葉氏二代。下総国の開発領主", "lore": "下総千葉荘を拠点に在地領主としての基盤を確立した。",
     "birthYear": 1083, "deathYear": 1143},
    {"id": "off_masakado_succ_5", "name": "千葉常胤(将門流)", "clanId": "taira_masakado", "defaultProv": "shimousa",
     "military": 82, "politic": 85, "intel": 80, "era": "kamakura", "skill": "源頼朝の功臣",
     "comment": "千葉氏三代。源頼朝挙兵の最大の功臣", "lore": "頼朝の挙兵に際し下総で迎え、鎌倉幕府創設の立役者となった名将。",
     "birthYear": 1118, "deathYear": 1201},
    {"id": "off_masakado_succ_6", "name": "千葉成胤(将門流)", "clanId": "taira_masakado", "defaultProv": "shimousa",
     "military": 76, "politic": 78, "intel": 75, "era": "kamakura", "skill": "千葉介",
     "comment": "千葉常胤の嫡孫。下総守護として幕府に仕える", "lore": "鎌倉幕府の有力御家人として下総の守護を務めた。",
     "birthYear": 1155, "deathYear": 1218},
    {"id": "off_masakado_succ_7", "name": "千葉胤綱(将門流)", "clanId": "taira_masakado", "defaultProv": "shimousa",
     "military": 75, "politic": 76, "intel": 74, "era": "kamakura", "skill": "下総千葉",
     "comment": "千葉氏七代。承久の乱後の千葉一門を統率", "lore": "「坂東一の弓取り」と称された千葉氏の武名を保った。",
     "birthYear": 1199, "deathYear": 1241},

    # ============================================================
    # 平貞盛軍 (taira_sadamori) Gap: (1122, 1237)
    # 既存: 平正盛 D:1121 → 1156シナリオの武将に繋がらない
    # ============================================================
    {"id": "off_sadamori_tadamori", "name": "平忠盛", "clanId": "taira_sadamori", "defaultProv": "ise",
     "military": 80, "politic": 88, "intel": 85, "era": "heian", "skill": "殿上人",
     "comment": "平清盛の父。武士として初めて殿上人に列した出世の先駆け", "lore": "白河院に仕え、武力と政治力で伊勢平氏を飛躍的に発展させた名将。",
     "birthYear": 1096, "deathYear": 1153},
    {"id": "off_sadamori_kiyomori", "name": "平清盛(貞盛流)", "clanId": "taira_sadamori", "defaultProv": "settsu",
     "military": 82, "politic": 96, "intel": 88, "era": "heian", "skill": "平氏政権",
     "comment": "太政大臣。武家初の天下人として日宋貿易を推進", "lore": "保元・平治の乱に勝利し、平氏政権を樹立した日本史上屈指の権力者。",
     "birthYear": 1118, "deathYear": 1181},
    {"id": "off_sadamori_munemori", "name": "平宗盛(貞盛流)", "clanId": "taira_sadamori", "defaultProv": "settsu",
     "military": 55, "politic": 65, "intel": 60, "era": "kamakura", "skill": "平氏棟梁",
     "comment": "清盛の三男。壇ノ浦の戦いで捕縛された平氏最後の棟梁", "lore": "父清盛の死後、平氏を率いたが源義経に敗れて壇ノ浦で捕らえられた。",
     "birthYear": 1147, "deathYear": 1185},
    {"id": "off_sadamori_tokitada", "name": "平時忠(貞盛流)", "clanId": "taira_sadamori", "defaultProv": "noto",
     "military": 50, "politic": 78, "intel": 80, "era": "kamakura", "skill": "平家にあらずんば",
     "comment": "「平家にあらずんば人にあらず」の名言で知られる公卿", "lore": "壇ノ浦後に能登に配流されたが、時氏一門は能登で存続した。",
     "birthYear": 1130, "deathYear": 1189},
    {"id": "off_sadamori_succ_5", "name": "平時実(能登)", "clanId": "taira_sadamori", "defaultProv": "noto",
     "military": 60, "politic": 72, "intel": 70, "era": "kamakura", "skill": "能登平氏",
     "comment": "平時忠の子孫。能登の地で平氏の家名を保つ", "lore": "能登国で在地領主として鎌倉幕府のもとに存続した。",
     "birthYear": 1168, "deathYear": 1228},
    {"id": "off_sadamori_succ_6", "name": "平時定", "clanId": "taira_sadamori", "defaultProv": "noto",
     "military": 58, "politic": 70, "intel": 68, "era": "kamakura", "skill": "平氏末裔",
     "comment": "能登平氏の末裔。承久の乱後も存続", "lore": "鎌倉時代中期に至るまで能登の地で平氏の血脈を守った。",
     "birthYear": 1200, "deathYear": 1245},

    # ============================================================
    # 鎌倉幕府 (hojo_kamakura) Gap: (1334, 1344)
    # 既存: 北条氏 D:1333で全滅, 次: 北条時行 G:1345以降
    # ============================================================
    {"id": "off_hojo_tokiyuki_early", "name": "北条時行(中先代)", "clanId": "hojo_kamakura", "defaultProv": "sagami",
     "military": 78, "politic": 72, "intel": 70, "era": "nanbokucho", "skill": "中先代の乱",
     "comment": "北条高時の遺児。中先代の乱を起こし鎌倉を一時奪回", "lore": "父高時の死後、信濃の諏訪氏に匿われ、1335年に中先代の乱を起こした。",
     "birthYear": 1318, "deathYear": 1353},

    # ============================================================
    # 赤穂浪士 (ako_ronin) Gap: (1704, 1852)
    # 既存: 大石内蔵助ら D:1703で全滅
    # ============================================================
    {"id": "off_ako_succ_1", "name": "大石良恭", "clanId": "ako_ronin", "defaultProv": "harima",
     "military": 72, "politic": 75, "intel": 73, "era": "edo", "skill": "大石一門",
     "comment": "大石内蔵助の遺族。赤穂義士の家名を継承", "lore": "討ち入り後も大石家の血脈は細々と続き、義士の精神を伝承した。",
     "birthYear": 1685, "deathYear": 1750},
    {"id": "off_ako_succ_2", "name": "大石良貞", "clanId": "ako_ronin", "defaultProv": "harima",
     "military": 70, "politic": 74, "intel": 72, "era": "edo", "skill": "義士末裔",
     "comment": "大石良恭の子。赤穂義士の顕彰に尽力", "lore": "義士の事績を後世に伝え、忠臣蔵の物語の基礎を築いた。",
     "birthYear": 1720, "deathYear": 1785},
    {"id": "off_ako_succ_3", "name": "大石良知", "clanId": "ako_ronin", "defaultProv": "harima",
     "military": 68, "politic": 73, "intel": 72, "era": "edo", "skill": "赤穂大石家",
     "comment": "赤穂大石家の当主。義士の霊を祀る", "lore": "花岳寺の義士祭祀を支え、赤穂浪士の名誉を守った。",
     "birthYear": 1755, "deathYear": 1825},
    {"id": "off_ako_succ_4", "name": "大石良雄(末裔)", "clanId": "ako_ronin", "defaultProv": "harima",
     "military": 67, "politic": 72, "intel": 71, "era": "bakumatsu", "skill": "大石家存続",
     "comment": "幕末期の大石家当主。義士の遺徳を慕う", "lore": "幕末の動乱期にあって赤穂義士の精神的遺産を守り抜いた。",
     "birthYear": 1795, "deathYear": 1860},

    # ============================================================
    # 細川家 (hosokawa) Gap: (1811, 1939)
    # 既存: 細川重賢系 D:1810付近で途切れ
    # ============================================================
    {"id": "off_hosokawa_narimori", "name": "細川斉護", "clanId": "hosokawa", "defaultProv": "higo",
     "military": 72, "politic": 82, "intel": 80, "era": "edo", "skill": "肥後藩十代",
     "comment": "熊本藩10代藩主。藩政改革に取り組む", "lore": "天保の飢饉に際し藩民救済に尽力した名君。",
     "birthYear": 1804, "deathYear": 1860},
    {"id": "off_hosokawa_yoshikuni", "name": "細川韶邦", "clanId": "hosokawa", "defaultProv": "higo",
     "military": 70, "politic": 78, "intel": 76, "era": "bakumatsu", "skill": "肥後藩十二代",
     "comment": "熊本藩12代藩主。幕末の動乱を藩の存続に導く", "lore": "戊辰戦争では新政府側に与し、熊本細川家の存続を確保した。",
     "birthYear": 1835, "deathYear": 1876},
    {"id": "off_hosokawa_morihisa", "name": "細川護久", "clanId": "hosokawa", "defaultProv": "higo",
     "military": 68, "politic": 80, "intel": 78, "era": "bakumatsu", "skill": "熊本藩知事",
     "comment": "最後の熊本藩主。廃藩後は熊本県知事を務める", "lore": "版籍奉還・廃藩置県を経て熊本県令として近代化に貢献。",
     "birthYear": 1839, "deathYear": 1893},
    {"id": "off_hosokawa_morishige", "name": "細川護成", "clanId": "hosokawa", "defaultProv": "higo",
     "military": 65, "politic": 78, "intel": 80, "era": "bakumatsu", "skill": "細川侯爵",
     "comment": "細川侯爵家二代。貴族院議員として活躍", "lore": "旧細川家の文化財保護と熊本の教育振興に尽力した。",
     "birthYear": 1870, "deathYear": 1918},
    {"id": "off_hosokawa_moritaka", "name": "細川護立", "clanId": "hosokawa", "defaultProv": "higo",
     "military": 60, "politic": 82, "intel": 90, "era": "bakumatsu", "skill": "永青文庫創設",
     "comment": "細川侯爵家三代。美術品収集家・永青文庫創設者", "lore": "国宝級の美術品を多数収集し永青文庫を設立。日本文化の保存に大功あり。",
     "birthYear": 1883, "deathYear": 1970},

    # ============================================================
    # 黒田家 (kuroda) Gap: (1852, 1939)
    # 既存: D:1851付近で途切れ → 1868武将に繋がらない
    # ============================================================
    {"id": "off_kuroda_nagahiro2", "name": "黒田長溥", "clanId": "kuroda", "defaultProv": "chikuzen",
     "military": 72, "politic": 85, "intel": 82, "era": "bakumatsu", "skill": "福岡藩十一代",
     "comment": "福岡藩11代藩主。島津斉彬の兄。蘭癖大名", "lore": "西洋技術の導入に積極的で、幕末の福岡藩を近代化に導いた。",
     "birthYear": 1811, "deathYear": 1869},
    {"id": "off_kuroda_nagashige", "name": "黒田長知", "clanId": "kuroda", "defaultProv": "chikuzen",
     "military": 68, "politic": 78, "intel": 76, "era": "bakumatsu", "skill": "福岡藩最後",
     "comment": "福岡藩12代（最後の）藩主。廃藩置県を経験", "lore": "戊辰戦争で新政府側に与し、版籍奉還後は福岡藩知事を務めた。",
     "birthYear": 1838, "deathYear": 1902},
    {"id": "off_kuroda_nagaaki", "name": "黒田長成", "clanId": "kuroda", "defaultProv": "chikuzen",
     "military": 60, "politic": 82, "intel": 85, "era": "bakumatsu", "skill": "黒田侯爵",
     "comment": "黒田侯爵家二代。貴族院副議長を歴任", "lore": "ケンブリッジ大学留学後、貴族院副議長として政界で活躍した知識人。",
     "birthYear": 1867, "deathYear": 1939},

    # ============================================================
    # 真田家 (sanada) Gap: (1816, 1939)
    # 既存: 真田幸弘 D:1815 → 1868武将に繋がらない
    # ============================================================
    {"id": "off_sanada_yukitsura", "name": "真田幸貫", "clanId": "sanada", "defaultProv": "shinano",
     "military": 72, "politic": 88, "intel": 85, "era": "edo", "skill": "松代藩八代・老中",
     "comment": "松代藩8代藩主。老中として天保の改革に参画", "lore": "松平定信の孫で真田家に養子入り。佐久間象山を登用した開明的名君。",
     "birthYear": 1791, "deathYear": 1852},
    {"id": "off_sanada_yukimoto", "name": "真田幸教", "clanId": "sanada", "defaultProv": "shinano",
     "military": 68, "politic": 78, "intel": 76, "era": "bakumatsu", "skill": "松代藩九代",
     "comment": "松代藩9代藩主。幕末の動乱期を乗り切る", "lore": "佐久間象山の開国論を支持し、幕末松代藩の存続を導いた。",
     "birthYear": 1830, "deathYear": 1873},
    {"id": "off_sanada_yukitaka_m", "name": "真田幸民", "clanId": "sanada", "defaultProv": "shinano",
     "military": 65, "politic": 76, "intel": 78, "era": "bakumatsu", "skill": "松代藩最後",
     "comment": "松代藩10代（最後の）藩主。戊辰戦争で新政府方", "lore": "北越戦争に出兵して新政府に与し、廃藩後は伯爵に叙された。",
     "birthYear": 1847, "deathYear": 1903},
    {"id": "off_sanada_yukimasa_mod", "name": "真田幸正", "clanId": "sanada", "defaultProv": "shinano",
     "military": 60, "politic": 75, "intel": 78, "era": "bakumatsu", "skill": "真田伯爵",
     "comment": "真田伯爵家。旧松代領の教育振興に貢献", "lore": "真田宝物館の設立に関わり、真田家の歴史遺産を保存した。",
     "birthYear": 1878, "deathYear": 1945},

    # ============================================================
    # 大塩平八郎 (oshio) Gap: (1838, 1869)
    # 既存: 大塩平八郎 D:1837で死亡
    # ============================================================
    {"id": "off_oshio_succ_1", "name": "大塩格之助", "clanId": "oshio", "defaultProv": "settsu",
     "military": 72, "politic": 70, "intel": 75, "era": "edo", "skill": "大塩門下",
     "comment": "大塩平八郎の養子。乱に参加後逃亡", "lore": "養父の志を継ぎ大塩の乱に参加。捕縛後に獄死したと伝わる。",
     "birthYear": 1814, "deathYear": 1837},
    {"id": "off_oshio_succ_2", "name": "大塩門人(残党)", "clanId": "oshio", "defaultProv": "settsu",
     "military": 68, "politic": 72, "intel": 76, "era": "edo", "skill": "陽明学派",
     "comment": "大塩門下の残党。洗心洞の学統を密かに継承", "lore": "大塩の陽明学の教えを密かに伝承し、幕末の尊攘運動に影響を与えた。",
     "birthYear": 1815, "deathYear": 1875},
    {"id": "off_oshio_succ_3", "name": "大塩良助", "clanId": "oshio", "defaultProv": "settsu",
     "military": 65, "politic": 73, "intel": 78, "era": "bakumatsu", "skill": "大塩遺族",
     "comment": "大塩家の遠縁。乱後の大塩家名を継承", "lore": "明治維新後に大塩平八郎の名誉回復に尽力した。",
     "birthYear": 1840, "deathYear": 1900},

    # ============================================================
    # 最終調整 - 残り6件解消
    # ============================================================

    # 平安朝廷 (heian_court) Gap: (1193, 1194)
    # 後白河院 D:1192, 後鳥羽上皇(朝廷) G:1195. 2年ギャップ
    {"id": "off_heian_court_kujo", "name": "九条兼実", "clanId": "heian_court", "defaultProv": "yamashiro",
     "military": 45, "politic": 88, "intel": 90, "era": "kamakura", "skill": "摂政関白",
     "comment": "九条家の祖。後白河院崩御後の朝廷を主導した関白", "lore": "源頼朝と結び、後白河院の死後に政権を掌握した稀代の政治家。",
     "birthYear": 1149, "deathYear": 1207},

    # 源経基軍 (minamoto_tsunemoto) Gap: (1200, 1206)
    # 源頼朝 D:1199, 源実朝 G:1207, 源頼茂 G:1218. 7年ギャップ
    {"id": "off_tsunemoto_yoriie", "name": "源頼家(経基流)", "clanId": "minamoto_tsunemoto", "defaultProv": "sagami",
     "military": 65, "politic": 55, "intel": 58, "era": "kamakura", "skill": "二代将軍",
     "comment": "鎌倉幕府二代将軍。頼朝の嫡男だが北条氏に追われた", "lore": "父頼朝の死後将軍職を継いだが、北条氏の謀略により修善寺で暗殺された。",
     "birthYear": 1182, "deathYear": 1206},

    # 日向薩摩豪族 (shimazu_proto) Gap: (1228, 1237)
    # 島津忠久(祖) D:1227, 島津久経 G:1240. 12年ギャップ
    {"id": "off_shimazu_proto_tadayoshi", "name": "島津忠時", "clanId": "shimazu_proto", "defaultProv": "satsuma",
     "military": 75, "politic": 78, "intel": 76, "era": "kamakura", "skill": "島津二代",
     "comment": "島津氏二代当主。父忠久の遺業を継ぎ薩摩守護を務める", "lore": "鎌倉幕府の有力御家人として薩摩・大隅の守護を務めた。",
     "birthYear": 1202, "deathYear": 1272},

    # 細川家 (hosokawa) Gap: (1811, 1818)
    # 細川斉茲 D:1810, 細川斉護 G:1819. 8年ギャップ
    {"id": "off_hosokawa_narinaga", "name": "細川斉樹", "clanId": "hosokawa", "defaultProv": "higo",
     "military": 68, "politic": 78, "intel": 76, "era": "edo", "skill": "肥後藩九代",
     "comment": "熊本藩9代藩主。斉茲の養嗣子", "lore": "藩政の安定に努め、文化・学問の振興を推進した。",
     "birthYear": 1795, "deathYear": 1826},

    # ============================================================
    # 真田十勇士 - 真田幸村の伝説的配下
    # 大坂の陣を中心に活躍した十人の勇士
    # ============================================================

    # 1. 猿飛佐助 - 甲賀忍者の頭領、十勇士の筆頭
    {"id": "off_sarutobi_sasuke", "name": "猿飛佐助", "clanId": "sanada", "defaultProv": "shinano",
     "military": 88, "politic": 62, "intel": 92, "era": "sengoku", "skill": "甲賀忍術",
     "comment": "真田十勇士筆頭。甲賀流忍術の達人で幸村の右腕",
     "lore": "甲賀の山中で戸沢白雲斎に忍術を学び、真田幸村に仕えた伝説の忍者。大坂の陣では諜報と撹乱工作で徳川軍を翻弄した。",
     "birthYear": 1580, "deathYear": 1615},

    # 2. 霧隠才蔵 - 伊賀忍者、佐助と双璧をなす忍び
    {"id": "off_kirigakure_saizo", "name": "霧隠才蔵", "clanId": "sanada", "defaultProv": "shinano",
     "military": 86, "politic": 60, "intel": 90, "era": "sengoku", "skill": "伊賀忍術",
     "comment": "真田十勇士。伊賀流忍術の名手で猿飛佐助の好敵手",
     "lore": "百地三太夫に伊賀忍術を学んだ後、真田幸村に仕える。霧を自在に操る幻術で知られ、佐助とともに十勇士の双璧と称された。",
     "birthYear": 1578, "deathYear": 1615},

    # 3. 三好清海入道 - 怪力の僧兵、豪傑
    {"id": "off_miyoshi_seikai", "name": "三好清海入道", "clanId": "sanada", "defaultProv": "shinano",
     "military": 92, "politic": 55, "intel": 58, "era": "sengoku", "skill": "怪力無双",
     "comment": "真田十勇士。元は三好一族の僧兵で怪力無双の豪傑",
     "lore": "三好長慶の一族とも伝わる巨躯の僧兵。大薙刀を振るい、大坂夏の陣では真田丸の守備に獅子奮迅の活躍を見せた。",
     "birthYear": 1562, "deathYear": 1615},

    # 4. 三好伊三入道 - 清海入道の弟、同じく豪傑僧兵
    {"id": "off_miyoshi_isa", "name": "三好伊三入道", "clanId": "sanada", "defaultProv": "shinano",
     "military": 88, "politic": 52, "intel": 55, "era": "sengoku", "skill": "剛力僧兵",
     "comment": "真田十勇士。清海入道の弟で兄に劣らぬ剛力の僧兵",
     "lore": "兄・清海入道とともに真田幸村に従い、大坂の陣で奮戦。兄弟そろっての薙刀戦法は徳川方を震え上がらせた。",
     "birthYear": 1565, "deathYear": 1615},

    # 5. 穴山小助 - 幸村の影武者を務めた忠臣
    {"id": "off_anayama_kosuke", "name": "穴山小助", "clanId": "sanada", "defaultProv": "shinano",
     "military": 80, "politic": 68, "intel": 75, "era": "sengoku", "skill": "影武者",
     "comment": "真田十勇士。幸村の影武者を務め、主君の身代わりとなった忠義の士",
     "lore": "幸村に瓜二つの容貌を持ち、大坂夏の陣では影武者として敵中に突入。主君の最期を見届けてから壮絶な討死を遂げた。",
     "birthYear": 1578, "deathYear": 1615},

    # 6. 由利鎌之助 - 鎖鎌の達人
    {"id": "off_yuri_kamanosuke", "name": "由利鎌之助", "clanId": "sanada", "defaultProv": "shinano",
     "military": 85, "politic": 50, "intel": 65, "era": "sengoku", "skill": "鎖鎌術",
     "comment": "真田十勇士。鎖鎌の名手で、一対多の戦闘を得意とした",
     "lore": "紀伊国出身の武芸者。鎖鎌を自在に操り、大坂の陣では単騎で敵陣に斬り込む豪胆さを見せた猛将。",
     "birthYear": 1575, "deathYear": 1615},

    # 7. 筧十蔵 - 火縄銃の名手
    {"id": "off_kakei_juzo", "name": "筧十蔵", "clanId": "sanada", "defaultProv": "shinano",
     "military": 83, "politic": 58, "intel": 72, "era": "sengoku", "skill": "百発百中",
     "comment": "真田十勇士。火縄銃の名手で百発百中の腕前を誇った",
     "lore": "信濃の鉄砲衆の出身。その射撃の腕は「筧の一発」と恐れられ、大坂の陣では狙撃で徳川方の武将を次々と仕留めた。",
     "birthYear": 1578, "deathYear": 1615},

    # 8. 海野六郎 - 真田一族の譜代家臣
    {"id": "off_unno_rokuro", "name": "海野六郎", "clanId": "sanada", "defaultProv": "shinano",
     "military": 78, "politic": 72, "intel": 76, "era": "sengoku", "skill": "諜報術",
     "comment": "真田十勇士。海野氏は真田氏と同族で、幸村の最も信頼厚い側近",
     "lore": "滋野三家の一つ海野氏の末裔。真田家と血縁関係にあり、幸村の参謀として諜報活動と軍略の立案を担った知将。",
     "birthYear": 1576, "deathYear": 1615},

    # 9. 根津甚八 - 元海賊の豪傑
    {"id": "off_nezu_jinpachi", "name": "根津甚八", "clanId": "sanada", "defaultProv": "shinano",
     "military": 84, "politic": 55, "intel": 68, "era": "sengoku", "skill": "水軍戦法",
     "comment": "真田十勇士。元は九鬼水軍の海賊で、水陸両用の戦闘に長けた",
     "lore": "志摩の海賊衆から真田幸村に仕えた異色の勇士。海戦の経験を活かし、大坂の陣では水堀を利用した奇策を立案した。",
     "birthYear": 1573, "deathYear": 1615},

    # 10. 望月六郎 - 火術・爆薬の達人
    {"id": "off_mochizuki_rokuro", "name": "望月六郎", "clanId": "sanada", "defaultProv": "shinano",
     "military": 82, "politic": 55, "intel": 78, "era": "sengoku", "skill": "火術・爆破",
     "comment": "真田十勇士。火薬と爆破術の達人で、真田丸の防衛に貢献",
     "lore": "甲賀望月氏の末裔。火薬の調合と爆破工作に精通し、大坂冬の陣では真田丸に仕掛けた地雷で徳川軍に大打撃を与えた。",
     "birthYear": 1580, "deathYear": 1615},

    # ============================================================
    # 最終完全解消補完 (Abe, Otomo, Ryuzoji, Sassa, Satomi)
    # ============================================================
    # 安倍家 (abe) 1181-1206補完
    {"id": "off_abe_muneyuki", "name": "安倍宗行", "clanId": "abe", "defaultProv": "rikuchu",
     "military": 71, "politic": 74, "intel": 72, "era": "kamakura", "skill": "安倍末裔",
     "comment": "安倍宗継の子。鎌倉期に血統を繋ぐ", "lore": "鎌倉時代初頭の動乱の中、安倍氏の血統と名跡を後世に伝えた。",
     "birthYear": 1160, "deathYear": 1225},

    # 大友家 (otomo) 1626-1634補完
    {"id": "off_otomo_chikamori", "name": "大友親盛", "clanId": "otomo", "defaultProv": "bungo",
     "military": 76, "politic": 75, "intel": 78, "era": "edo", "skill": "大友一門重鎮",
     "comment": "大友宗麟の三男。細川家に仕え大友一門を支える", "lore": "宗麟の三男。兄義統の改易後も細川家に仕え、大友家の血統と武名を江戸時代へと繋いだ重鎮。",
     "birthYear": 1584, "deathYear": 1643},

    # 龍造寺家 (ryuzoji) 1585-1614補完
    {"id": "off_ryuzoji_masaie", "name": "龍造寺政家", "clanId": "ryuzoji", "defaultProv": "hizen",
     "military": 74, "politic": 77, "intel": 72, "era": "sengoku", "skill": "龍造寺二十代",
     "comment": "龍造寺隆信の嫡男。第二十代当主", "lore": "隆信の戦死後、龍造寺家当主となる。豊臣秀吉の九州平定に従い、肥前佐賀の領国を維持した。",
     "birthYear": 1556, "deathYear": 1607},
    {"id": "off_goto_ienobu_ryu", "name": "後藤家信", "clanId": "ryuzoji", "defaultProv": "hizen",
     "military": 78, "politic": 76, "intel": 74, "era": "sengoku", "skill": "武雄領主",
     "comment": "龍造寺隆信の次男。武雄後藤氏を継ぐ", "lore": "龍造寺一門の有力支族として肥前武雄を領し、龍造寺から鍋島への過渡期を支えた猛将。",
     "birthYear": 1563, "deathYear": 1622},

    # 佐々家 (sassa) 1589-1734補完
    {"id": "off_sassa_naomasa", "name": "佐々直政", "clanId": "sassa", "defaultProv": "etchu",
     "military": 75, "politic": 72, "intel": 73, "era": "sengoku", "skill": "佐々家継承",
     "comment": "佐々成政の甥・養嗣子。徳川家に仕える", "lore": "成政の死後、徳川家康に仕えて家名を存続させ、旗本として佐々氏の血脈を繋いだ。",
     "birthYear": 1570, "deathYear": 1620},
    {"id": "off_sassa_sadamasa", "name": "佐々定正", "clanId": "sassa", "defaultProv": "etchu",
     "military": 70, "politic": 75, "intel": 74, "era": "edo", "skill": "旗本佐々家",
     "comment": "佐々直政の嫡男。徳川幕臣として仕える", "lore": "大坂の陣に従軍し、江戸幕府旗本として佐々家の地位を確立した。",
     "birthYear": 1600, "deathYear": 1662},
    {"id": "off_sassa_munekiyo", "name": "佐々宗淳", "clanId": "sassa", "defaultProv": "etchu",
     "military": 65, "politic": 88, "intel": 92, "era": "edo", "skill": "助さんのモデル・史官",
     "comment": "水戸藩士。水戸黄門「助さん」のモデル", "lore": "徳川光圀に重用され『大日本史』編纂総裁を務めた学者。諸国を巡歴して史料を収集した。",
     "birthYear": 1640, "deathYear": 1698},
    {"id": "off_sassa_tsunakiyo", "name": "佐々綱淳", "clanId": "sassa", "defaultProv": "etchu",
     "military": 62, "politic": 80, "intel": 82, "era": "edo", "skill": "水戸佐々家",
     "comment": "佐々宗淳の養嗣子。水戸藩士", "lore": "養父宗淳の学問と志を継ぎ、水戸藩の重臣として佐々家の名声を高めた。",
     "birthYear": 1670, "deathYear": 1738},

    # 里見家 (satomi) 1736-1737補完
    {"id": "off_satomi_yoshihiro_edo", "name": "里見義啓", "clanId": "satomi", "defaultProv": "awa_boso",
     "military": 68, "politic": 75, "intel": 74, "era": "edo", "skill": "江戸里見家",
     "comment": "里見義安の子。江戸幕府旗本として仕える", "lore": "安房里見氏の末裔として旗本を務め、里見氏の祭祀と家名を後世に守り伝えた。",
     "birthYear": 1715, "deathYear": 1780},

    # ============================================================
    # 最終完全精密ゼロギャップ補完 (12 clans precision bridges)
    # ============================================================
    # 千葉家 (chiba) 1366-1374, 1586-1596補完
    {"id": "off_chiba_kanetane_bridge", "name": "千葉兼胤", "clanId": "chiba", "defaultProv": "shimousa",
     "military": 75, "politic": 78, "intel": 76, "era": "nanbokucho", "skill": "千葉介",
     "comment": "千葉氏十四代当主。満胤の弟", "lore": "南北朝末期の下総千葉氏を率い、一族の団結を維持した名将。",
     "birthYear": 1350, "deathYear": 1416},
    {"id": "off_chiba_naoshige_bridge", "name": "千葉直重", "clanId": "chiba", "defaultProv": "shimousa",
     "military": 78, "politic": 76, "intel": 77, "era": "sengoku", "skill": "北条・千葉融和",
     "comment": "北条氏政の子。千葉邦胤の養嗣子", "lore": "邦胤の急死後、千葉家当主として北条氏と千葉氏の同盟を固めた。",
     "birthYear": 1570, "deathYear": 1627},

    # 後白河院 (goshirakawa_in) 1240-1263補完
    {"id": "off_gosaga_in_bridge", "name": "後嵯峨天皇(治天)", "clanId": "goshirakawa_in", "defaultProv": "yamashiro",
     "military": 60, "politic": 90, "intel": 88, "era": "kamakura", "skill": "治天の君",
     "comment": "第88代天皇。院政を行い皇統の基礎を築く", "lore": "後鳥羽院流の皇統を継ぎ、幕府との協調により治天の君として権勢を誇った。",
     "birthYear": 1220, "deathYear": 1272},

    # 蠣崎家 (kakizaki) 1870-1879補完
    {"id": "off_matsumae_takahiro_bridge", "name": "松前崇広(史実晩年)", "clanId": "kakizaki", "defaultProv": "ezo",
     "military": 78, "politic": 86, "intel": 85, "era": "bakumatsu", "skill": "老中・松前藩主",
     "comment": "松前藩第十二代藩主。幕府老中を務める", "lore": "開国派老中として軍備近代化を推進。維新の激動期に松前藩を守り抜いた名君。",
     "birthYear": 1829, "deathYear": 1880},

    # 鎌倉公方 (kamakura_fu) 1584-1588補完
    {"id": "off_ashikaga_kunitomo_bridge", "name": "足利国朝", "clanId": "kamakura_fu", "defaultProv": "shimotsuke",
     "military": 74, "politic": 75, "intel": 73, "era": "sengoku", "skill": "喜連川家祖",
     "comment": "小弓公方頼純の子。足利氏姫の婿", "lore": "豊臣秀吉の命により足利氏姫と婚姻し、名門古河公方の血脈を喜連川藩へと繋いだ。",
     "birthYear": 1568, "deathYear": 1593},

    # 源為朝 (minamoto_tametomo) 1171-1180補完
    {"id": "off_shunten_king_bridge", "name": "舜天王", "clanId": "minamoto_tametomo", "defaultProv": "ryukyu",
     "military": 82, "politic": 85, "intel": 80, "era": "kamakura", "skill": "琉球初代王",
     "comment": "源為朝の落胤伝説を持つ初代琉球国王", "lore": "源為朝が琉球に逃れて成した子と伝えられ、舜天王統を開いた英主。",
     "birthYear": 1155, "deathYear": 1237},

    # 水戸徳川家 (mito) 1731-1742補完
    {"id": "off_matsudaira_yoriaki_bridge", "name": "松平頼章", "clanId": "mito", "defaultProv": "hitachi",
     "military": 72, "politic": 82, "intel": 80, "era": "edo", "skill": "水戸一門後見",
     "comment": "松平頼純の子。幼少の藩主宗翰を後見", "lore": "水戸徳川家の重鎮として一族を補佐し、藩政の動揺を防ぎ家名を支えた。",
     "birthYear": 1695, "deathYear": 1745},

    # 大友家 (otomo) 1182-1186補完
    {"id": "off_otomo_yoshinao_early_bridge", "name": "大友能直(元服早)", "clanId": "otomo", "defaultProv": "bungo",
     "military": 80, "politic": 84, "intel": 82, "era": "kamakura", "skill": "豊後守護",
     "comment": "大友氏初代。源頼朝の近習として登用", "lore": "源頼朝に愛され、若年より相模御家人として仕え豊後・筑後等の守護に抜擢された。",
     "birthYear": 1165, "deathYear": 1223},

    # 佐竹家 (satake) 1759-1762補完
    {"id": "off_satake_yoshitsugu_bridge", "name": "佐竹義明(後見晩年)", "clanId": "satake", "defaultProv": "dewa",
     "military": 75, "politic": 82, "intel": 80, "era": "edo", "skill": "久保田藩主",
     "comment": "久保田藩七代藩主。曙山を育成", "lore": "藩政の財政再建を指導し、若き次代・義敦（曙山）の治世への橋渡しを務めた。",
     "birthYear": 1723, "deathYear": 1765},

    # 相馬家 (soma) 1674-1675補完
    {"id": "off_soma_masatane_early_bridge", "name": "相馬昌胤(家督)", "clanId": "soma", "defaultProv": "iwaki",
     "military": 76, "politic": 84, "intel": 82, "era": "edo", "skill": "相馬中興名君",
     "comment": "中村藩五代藩主。相馬家中興の名君", "lore": "妙見信仰を厚く保護し、学問を振興して相馬中村藩の治世を確立した名君。",
     "birthYear": 1658, "deathYear": 1728},

    # 武田家 (takeda) 1596-1597補完
    {"id": "off_takeda_nobuyoshi_early_bridge", "name": "武田信吉(元服)", "clanId": "takeda", "defaultProv": "kai",
     "military": 78, "politic": 80, "intel": 79, "era": "sengoku", "skill": "武田遺領継承",
     "comment": "徳川家康の五男。武田氏の名跡を継ぐ", "lore": "家康の命により武田氏の名跡を継承。旧武田家臣団を率いて水戸城主となった。",
     "birthYear": 1580, "deathYear": 1603},

    # 宇都宮家 (utsunomiya) 1528補完
    {"id": "off_utsunomiya_okitsuna_early_bridge", "name": "宇都宮興綱(擁立)", "clanId": "utsunomiya", "defaultProv": "shimotsuke",
     "military": 72, "politic": 75, "intel": 73, "era": "sengoku", "skill": "宇都宮二十一代",
     "comment": "宇都宮氏第二十一代当主。壬生氏に擁立", "lore": "兄・忠綱失脚後に若くして家督を継承し、下野の名門宇都宮氏を存続させた。",
     "birthYear": 1512, "deathYear": 1536},

    # 山名家 (yamana) 1661-1674補完
    {"id": "off_yamana_hiroyo_bridge", "name": "山名煕豊", "clanId": "yamana", "defaultProv": "tajima",
     "military": 70, "politic": 75, "intel": 74, "era": "edo", "skill": "山名一門・旗本",
     "comment": "因幡・但馬山名氏の末裔。幕府旗本", "lore": "名門山名氏の血脈を江戸時代に伝え、交代寄合表高知衆として家格を維持した。",
     "birthYear": 1640, "deathYear": 1700},
]

print(f"Comprehensive Gap Fixes defined: {len(COMPREHENSIVE_GAP_FIXES)} officers")
