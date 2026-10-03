# -*- coding: utf-8 -*-
"""
Expanded Historical Events with realistic territory changes across all eras.
"""

EXPANDED_HISTORICAL_EVENTS = [
    # 939 承平・天慶の乱
    {
        "id": "evt_939_masakado_kanto",
        "scenarioId": "939",
        "year": 939,
        "season": "秋",
        "title": "新皇即位・平将門の坂東席巻",
        "desc": "下総を本拠とする平将門が常陸・下野・上野の国府を次々に攻略。八カ国に独自の国司を任命して自ら『新皇』を名乗り、朝廷に反旗を翻した！坂東全土が将門の手に落ちる！",
        "changes": {
            "territory": {
                "hitachi": "taira_masakado",
                "shimousa": "taira_masakado",
                "kazusa": "taira_masakado",
                "shimotsuke": "taira_masakado",
                "kozuke": "taira_masakado",
                "musashi": "taira_masakado"
            },
            "message": "平将門が坂東諸国（常陸・下総・上総・下野・上野・武蔵）を制圧し、新皇として君臨しました！"
        }
    },
    {
        "id": "evt_940_masakado_fall",
        "scenarioId": "*",
        "year": 940,
        "season": "春",
        "title": "北山の決戦・新皇平将門の最期",
        "desc": "朝廷の追捕使・平貞盛と下野押領使・藤原秀郷が連合軍を結成し下総へ侵攻。北山の合戦にて突風の中、秀郷の放った矢が将門の額を射抜き、新皇平将門は壮烈に討死した！",
        "changes": {
            "territory": {
                "hitachi": "heian_court",
                "shimotsuke": "heian_court",
                "kozuke": "heian_court",
                "musashi": "heian_court"
            },
            "message": "平貞盛・藤原秀郷の討伐軍が勝利し、将門領が朝廷の支配下へ復帰しました！"
        }
    },
    {
        "id": "evt_941_sumitomo_fall",
        "scenarioId": "*",
        "year": 941,
        "season": "夏",
        "title": "博多湾海戦・藤原純友の終焉",
        "desc": "大宰府を焼き払った藤原純友軍に対し、追捕使長官・小野好古と次官・大蔵春実が率いる官軍水軍が博多湾で総攻撃。海賊船八百艘を焼き尽くし、純友は伊予へ逃亡の末に討ち取られた！",
        "changes": {
            "territory": {
                "buzen": "heian_court",
                "chikuzen": "heian_court",
                "iyo": "heian_court",
                "sanuki": "heian_court"
            },
            "message": "小野好古・大蔵春実が純友軍を撃滅し、瀬戸内・九州の治安が回復されました！"
        }
    },

    # 1028 平忠常の乱
    {
        "id": "evt_1028_tadatsune_boso",
        "scenarioId": "1028",
        "year": 1028,
        "season": "夏",
        "title": "房総の兵乱・平忠常の南関東席巻",
        "desc": "上総介・平忠常が安房守・平忠綱を殺害して蜂起。上総・下総・安房の房総三国を掌握し、朝廷の命を受けた追捕使・平直方を撃退して南関東に覇を唱えた！",
        "changes": {
            "territory": {
                "kazusa": "taira_tadatsune",
                "shimousa": "taira_tadatsune",
                "awa_boshu": "taira_tadatsune"
            },
            "message": "平忠常が房総三国（上総・下総・安房）を完全制覇しました！"
        }
    },
    {
        "id": "evt_1031_tadatsune_submit",
        "scenarioId": "1028",
        "year": 1031,
        "season": "春",
        "title": "平忠常、名将源頼信に降る",
        "desc": "甲斐守・源頼信が新たな追捕使として東国へ下向。忠常は頼信の武名と威徳に屈し、戦わずして出家降伏。房総三国の兵乱は平定され、河内源氏の武名が東国に鳴り響いた！",
        "changes": {
            "territory": {
                "kazusa": "minamoto_yorinobu",
                "shimousa": "minamoto_yorinobu",
                "awa_boshu": "minamoto_yorinobu"
            },
            "message": "源頼信の威徳により忠常が投降し、房総三国が源氏の勢力圏となりました！"
        }
    },

    # 1087 後三年の役
    {
        "id": "evt_1087_gosannen_kanazawa",
        "scenarioId": "1087",
        "year": 1087,
        "season": "冬",
        "title": "金沢柵陥落・奥州藤原氏の平泉創業",
        "desc": "八幡太郎源義家と清原清衡が率いる軍勢が、出羽金沢柵に籠城する清原家衡・武衡を兵糧攻めと総攻撃で破る！清原氏は滅亡し、清衡が奥羽全土を掌握して平泉に黄金文化を花開かせた！",
        "changes": {
            "territory": {
                "mutsu": "fujiwara_hiraizumi",
                "rikuou": "fujiwara_hiraizumi",
                "ugo": "fujiwara_hiraizumi",
                "tsugaru": "fujiwara_hiraizumi"
            },
            "message": "清原氏が滅亡し、藤原清衡が奥羽全土を統一、黄金郷平泉の時代が始まりました！"
        }
    },

    # 1156 保元の乱 & 1159 平治の乱
    {
        "id": "evt_1156_hogen_end",
        "scenarioId": "*",
        "year": 1156,
        "season": "秋",
        "title": "白河殿炎上・平清盛の台頭と武士の夜明け",
        "desc": "後白河天皇・平清盛・源義朝が夜襲により崇徳上皇・藤原頼長が籠る白河殿を急襲放火！上皇方は壊滅し、崇徳院は讃岐へ配流。朝廷の実権を武士が握る時代の幕が切って落とされた！",
        "changes": {
            "territory": {
                "yamashiro": "taira",
                "settsu": "taira",
                "kawachi": "taira",
                "harima": "taira"
            },
            "message": "平清盛が畿内要衝を制圧し、平氏の勢力が一気に拡大しました！"
        }
    },
    {
        "id": "evt_1159_heiji_rebellion",
        "scenarioId": "*",
        "year": 1159,
        "season": "冬",
        "title": "平治の乱・源氏壊滅と六波羅平氏の栄華",
        "desc": "源義朝と藤原信頼が信西を討ちクーデターを断行。熊野参詣から急遽帰京した平清盛が六波羅に全軍を集結して反撃！義朝軍は六条河原で大敗し、源氏嫡流は衰退、平氏の天下が確立した！",
        "changes": {
            "territory": {
                "owari": "taira",
                "mino": "taira",
                "suruga": "taira",
                "totomi": "taira"
            },
            "message": "源義朝が敗死し、東海道諸国が平氏の知行国となりました！"
        }
    },

    # 1180 治承・寿永の乱
    {
        "id": "evt_1180_fujikawa_vict",
        "scenarioId": "*",
        "year": 1180,
        "season": "秋",
        "title": "富士川の水鳥・源頼朝の関東制覇",
        "desc": "伊豆で挙兵した源頼朝が鎌倉を本拠とし、甲斐武田氏と共に富士川で平維盛率いる追討軍を迎撃。夜半の水鳥の羽音に驚愕した平家軍は矢一本交えず潰走！坂東諸国は源氏の手に落ちた！",
        "changes": {
            "territory": {
                "sagami": "minamoto_yoritomo",
                "musashi": "minamoto_yoritomo",
                "izu": "minamoto_yoritomo",
                "suruga": "takeda"
            },
            "message": "平家追討軍が潰走し、源頼朝・武田信義が関東・駿河を掌握しました！"
        }
    },
    {
        "id": "evt_1183_heike_flee",
        "scenarioId": "*",
        "year": 1183,
        "season": "秋",
        "title": "倶利伽羅峠の勝鬨・平家都落ち",
        "desc": "木曾義仲が火牛の計を用いて倶利伽羅峠で平家十万を谷底へ叩き落とし大勝利！破竹の勢いで京へ進撃する義仲に対し、平宗盛ら平家一門は安徳天皇と三種の神器を奉じて西国へ都落ちした！",
        "changes": {
            "territory": {
                "etchu": "minamoto_yoshitomo",
                "kaga": "minamoto_yoshitomo",
                "echizen": "minamoto_yoshitomo",
                "yamashiro": "minamoto_yoshitomo",
                "settsu": "taira"
            },
            "message": "木曾義仲が京都を占領し、平家一門は西国（屋島・壇ノ浦）へ逃亡しました！"
        }
    },
    {
        "id": "evt_1184_ichinotani",
        "scenarioId": "*",
        "year": 1184,
        "season": "春",
        "title": "鵯越の逆落とし・一ノ谷の大合戦",
        "desc": "源範頼・源義経が率いる鎌倉軍が一ノ谷の平家陣地を強襲！義経は鵯越の断崖絶壁を騎馬で駆け下りて平家本陣に突入。平通盛・忠度・敦盛ら平家名将が次々と討ち死にし福原京は灰燼に帰した！",
        "changes": {
            "territory": {
                "settsu": "minamoto_yoritomo",
                "harima": "minamoto_yoritomo",
                "tamba": "minamoto_yoritomo"
            },
            "message": "義経の神速の奇襲により一ノ谷が陥落、摂津・播磨が鎌倉幕府軍の手に渡りました！"
        }
    },
    {
        "id": "evt_1185_dannoura",
        "scenarioId": "*",
        "year": 1185,
        "season": "春",
        "title": "壇ノ浦の決戦・平家一門滅亡",
        "desc": "関門海峡・壇ノ浦にて源平最後の海上総決戦！潮の流れが変わると共に義経率いる源氏軍が一斉反撃。知盛は碇を担いで入水、二位尼は安徳天皇を抱いて波の下の都へ沈み、平家一門は完全に滅亡した！",
        "changes": {
            "territory": {
                "nagato": "minamoto_yoritomo",
                "suo": "minamoto_yoritomo",
                "aki": "minamoto_yoritomo",
                "bingo": "minamoto_yoritomo",
                "buzen": "minamoto_yoritomo",
                "chikuzen": "minamoto_yoritomo",
                "awa_shikoku": "minamoto_yoritomo",
                "sanuki": "minamoto_yoritomo"
            },
            "message": "壇ノ浦にて平家一門が滅亡し、源頼朝による全国支配と守護・地頭設置が成りました！"
        }
    },

    # 1221 承久の乱
    {
        "id": "evt_1221_jokyu_end",
        "scenarioId": "*",
        "year": 1221,
        "season": "夏",
        "title": "承久の乱終結・六波羅探題創設",
        "desc": "北条泰時・時房率いる東海道軍十九万騎が宇治川を突破し京都へ突入！後鳥羽上皇軍を粉砕し、後鳥羽院は隠岐へ、順徳院は佐渡へ配流。京都に六波羅探題が置かれ、幕府の西国支配が完成した！",
        "changes": {
            "territory": {
                "yamashiro": "hojo_kamakura",
                "settsu": "hojo_kamakura",
                "south_omi": "hojo_kamakura",
                "harima": "hojo_kamakura",
                "tamba": "hojo_kamakura",
                "kawachi": "hojo_kamakura",
                "izumi": "hojo_kamakura"
            },
            "message": "承久の乱に大勝利した鎌倉幕府が朝廷の西国領地をことごとく接収・支配しました！"
        }
    },

    # 1333 建武の新政 & 1336 湊川の戦い
    {
        "id": "evt_1333_kamakura_fall",
        "scenarioId": "*",
        "year": 1333,
        "season": "夏",
        "title": "六波羅陥落と鎌倉炎上・北条得宗家滅亡",
        "desc": "足利尊氏が丹波篠村八幡宮で挙兵して六波羅探題を攻め落とし、新田義貞が稲村ヶ崎を越えて鎌倉へ突入！北条高時ら一族八百余名が東勝寺で自刃し鎌倉幕府百四十年の歴史に幕が下りた！",
        "changes": {
            "territory": {
                "yamashiro": "ashikaga",
                "south_omi": "ashikaga",
                "sagami": "nitta",
                "musashi": "nitta",
                "kozuke": "nitta",
                "shimotsuke": "ashikaga",
                "harima": "akamatsu",
                "bizen": "akamatsu"
            },
            "message": "鎌倉幕府が滅亡し、後醍醐天皇による建武の新政が始まりました！"
        }
    },
    {
        "id": "evt_1336_minatogawa",
        "scenarioId": "*",
        "year": 1336,
        "season": "夏",
        "title": "湊川の戦い・大楠公の最期と室町幕府創立",
        "desc": "九州で軍勢を立て直した足利尊氏の大軍が湊川で楠木正成・新田義貞を迎撃！大楠公は壮絶な死闘の末に一族と共に自刃。尊氏は入京して光明天皇を擁立し、室町幕府を開いた！",
        "changes": {
            "territory": {
                "settsu": "ashikaga",
                "yamashiro": "ashikaga",
                "tamba": "ashikaga",
                "harima": "akamatsu",
                "bizen": "akamatsu",
                "mimasaka": "akamatsu"
            },
            "message": "足利尊氏が京都を制圧し、光明天皇を奉戴して室町幕府を樹立しました！"
        }
    },

    # 1350 南北朝・観応の擾乱
    {
        "id": "evt_1350_kanno_disturb",
        "scenarioId": "*",
        "year": 1350,
        "season": "冬",
        "title": "観応の擾乱・足利兄弟の決裂と南朝反攻",
        "desc": "将軍足利尊氏の執事・高師直と、尊氏の実弟・足利直義が激しく対立！直義は南朝に降り、楠木正儀ら南朝軍と連携して京都を占領。室町幕府は二つに割れ、全国の内乱が激化した！",
        "changes": {
            "territory": {
                "yamashiro": "kusunoki",
                "kawachi": "kusunoki",
                "settsu": "kusunoki",
                "yamato": "kusunoki"
            },
            "message": "足利直義と南朝軍が京都を急襲奪取し、室町幕府の天下が二分されました！"
        }
    },

    # 1441 嘉吉の乱 & 1467 応仁の乱
    {
        "id": "evt_1441_kakitsu",
        "scenarioId": "*",
        "year": 1441,
        "season": "夏",
        "title": "嘉吉の乱・赤松満祐の将軍暗殺と山名領国拡大",
        "desc": "播磨守護・赤松満祐が6代将軍足利義教を自邸に招いて暗殺！幕府追討軍を率いる山名宗全が赤松軍を木山城で全滅させ、赤松家の播磨・備前・美作は山名領へと組み込まれた！",
        "changes": {
            "territory": {
                "harima": "yamana",
                "mimasaka": "yamana",
                "bizen": "yamana"
            },
            "message": "赤松氏が討滅され、山名宗全が播磨・美作・備前を領有し強大化しました！"
        }
    },
    {
        "id": "evt_1467_oninn_outbreak",
        "scenarioId": "*",
        "year": 1467,
        "season": "夏",
        "title": "応仁の乱勃発・天下の兵乱洛中に集まる",
        "desc": "畠山・斯波両家の家督争いに管領・細川勝元（東軍）と山名宗全（西軍）が介入して京都で全面開戦！二十七万の大軍が洛中で激突し、都は業火に包まれ戦国乱世の火蓋が切られた！",
        "changes": {
            "territory": {
                "yamashiro": "hosokawa",
                "tamba": "hosokawa",
                "tajima": "yamana",
                "inaba": "yamana"
            },
            "message": "応仁の乱が勃発し、都は東西両軍に分断され全国の守護大名が激突しました！"
        }
    },

    # 1495 北条早雲 & 1546 河越夜戦
    {
        "id": "evt_1495_soyun_odawara",
        "scenarioId": "*",
        "year": 1495,
        "season": "秋",
        "title": "北条早雲の相模侵攻・小田原城奪取",
        "desc": "伊豆韮山城の北条早雲が、病弱な小田原城主・大森藤頼に対し鹿狩りを口実に箱根山を越えて急襲！難攻不落を誇る名城・小田原城を一昼夜で奪取し、相模平定の拠点を確立した！",
        "changes": {
            "territory": {
                "sagami": "hojo",
                "izu": "hojo"
            },
            "message": "北条早雲が小田原城を急襲奪取し、後北条氏百年の基礎を固めました！"
        }
    },
    {
        "id": "evt_1546_kawagoe_night",
        "scenarioId": "*",
        "year": 1546,
        "season": "春",
        "title": "河越夜戦・北条氏康の奇襲大勝利",
        "desc": "両上杉氏・古河公方の連合軍八万が河越城を完全包囲。北条氏康は兵八千を率いて闇夜と暴風雨の中を奇襲突撃！大軍はパニックに陥り潰走、扇谷上杉氏は滅亡し北条の関東覇権が確立した！",
        "changes": {
            "territory": {
                "musashi": "hojo",
                "kozuke": "hojo"
            },
            "message": "北条氏康が河越夜戦で八万の大軍を破り、武蔵・上野を北条領としました！"
        }
    },

    # 1560 桶狭間の戦い
    {
        "id": "evt_1560_okehazama",
        "scenarioId": "*",
        "year": 1560,
        "season": "夏",
        "title": "桶狭間の奇跡・信長の急襲と松平自立",
        "desc": "駿河・遠江・三河四万を率いて尾張へ乱入した今川義元に対し、織田信長が田楽狭間の豪雨を突いて本陣を強襲！義元を討ち取られた今川軍は総崩れとなり、松平元康（家康）は岡崎城で劇的自立を果たした！",
        "changes": {
            "territory": {
                "mikawa": "matsudaira",
                "owari": "oda"
            },
            "message": "今川義元が討死し、織田信長が尾張を完全掌握、松平元康が三河で独立しました！"
        }
    },

    # 1568 信長上洛
    {
        "id": "evt_1568_nobunaga_joraku",
        "scenarioId": "*",
        "year": 1568,
        "season": "秋",
        "title": "天下布武・信長の上洛と足利義昭奉戴",
        "desc": "美濃を平定した織田信長が足利義昭を奉じて電光石火の上洛を開始！近江六角氏の観音寺城をあっけなく攻略し、三好三人衆を畿内から叩き出して京都・近江を掌握した！",
        "changes": {
            "territory": {
                "south_omi": "oda",
                "north_omi": "oda",
                "yamashiro": "oda",
                "settsu": "oda"
            },
            "message": "織田信長が近江・京都・摂津を掌握し、足利義昭を将軍に擁立しました！"
        }
    },

    # 1573 浅井朝倉滅亡
    {
        "id": "evt_1573_odani_ichijodani",
        "scenarioId": "*",
        "year": 1573,
        "season": "秋",
        "title": "姉川の遺恨晴る・浅井朝倉両家滅亡",
        "desc": "織田信長が一乗谷城に朝倉義景を追い詰め自刃させ、返す刀で小谷城を総攻撃。浅井長政は自害し、お市の方と三姉妹は救出された。越前は柴田勝家に、北近江は羽柴秀吉に与えられた！",
        "changes": {
            "territory": {
                "echizen": "oda",
                "north_omi": "oda"
            },
            "appoint": {
                "echizen": "off_shibata_katsuie",
                "north_omi": "off_toyotomi_hideyoshi"
            },
            "message": "浅井・朝倉両家が滅亡し、柴田勝家が越前を、羽柴秀吉が北近江を拝領しました！"
        }
    },

    # 1575 長篠設楽原
    {
        "id": "evt_1575_nagashino",
        "scenarioId": "*",
        "year": 1575,
        "season": "夏",
        "title": "設楽原の鉄砲三段撃ち・武田騎馬隊壊滅",
        "desc": "三河長篠城をめぐる決戦にて、織田・徳川連合軍の三重の馬防柵と三千挺の鉄砲三段撃ちが武田勝頼の精鋭騎馬隊を粉砕！山県昌景・馬場信春ら名将が討死し、徳川家康は遠江・三河を奪回した！",
        "changes": {
            "territory": {
                "totomi": "tokugawa",
                "mikawa": "tokugawa"
            },
            "message": "長篠設楽原の戦いで武田軍が壊滅し、徳川家康が遠江・三河を完全奪回しました！"
        }
    },

    # 1582 甲州征伐
    {
        "id": "evt_1582_koshu_seibatsu",
        "scenarioId": "*",
        "year": 1582,
        "season": "春",
        "title": "甲州征伐・天目山の落日と名門武田氏滅亡",
        "desc": "織田信忠・徳川家康の大軍が信濃・駿河から甲斐へ怒涛の侵攻。武田勝頼・信勝父子は天目山で壮絶に自刃し、名門甲斐武田氏は滅亡。甲斐・信濃は織田家臣に、駿河は徳川家康に与えられた！",
        "changes": {
            "territory": {
                "kai": "oda",
                "north_shinano": "oda",
                "south_shinano": "oda",
                "suruga": "tokugawa"
            },
            "message": "武田氏が滅亡し、甲斐・信濃が織田領に、駿河が徳川領となりました！"
        }
    },

    # 1582 本能寺の変
    {
        "id": "evt_1582_honnouji_yamazaki",
        "scenarioId": "*",
        "year": 1582,
        "season": "夏",
        "title": "本能寺の変・魔王落命と天下の分裂",
        "desc": "『敵は本能寺にあり！』明智光秀の謀叛により織田信長・信忠父子が落命。羽柴秀吉は中国大返しを敢行し山崎の戦いで光秀を討ち取るも、織田家の巨領は秀吉・勝家・信雄・信孝・家康の間で分裂した！",
        "isHonnouji": True,
        "changes": {
            "territory": {
                "yamashiro": "toyotomi",
                "settsu": "toyotomi",
                "kawachi": "toyotomi",
                "izumi": "toyotomi",
                "harima": "toyotomi",
                "tamba": "toyotomi",
                "echizen": "shibata",
                "kaga": "shibata",
                "noto": "maeda",
                "owari": "oda_nobuo",
                "ise": "oda_nobuo",
                "mino": "oda_nobutaka",
                "kai": "tokugawa",
                "south_shinano": "tokugawa",
                "north_shinano": "sanada",
                "suruga": "tokugawa",
                "totomi": "tokugawa",
                "mikawa": "tokugawa"
            },
            "message": "織田信長公落命！天下は羽柴秀吉、柴田勝家、徳川家康ら後継勢力の割拠へ突入しました！"
        }
    },

    # 1583 賤ヶ岳の戦い
    {
        "id": "evt_1583_shizugatake",
        "scenarioId": "*",
        "year": 1583,
        "season": "春",
        "title": "賤ヶ岳の戦い・羽柴秀吉の覇権確立",
        "desc": "北近江・賤ヶ岳の戦いにて賤ヶ岳七本槍の奮戦により羽柴秀吉が柴田勝家軍を壊滅させる。勝家とお市の方は越前北ノ庄城で自刃。秀吉は信長後継者としての覇権を完全に確立した！",
        "changes": {
            "territory": {
                "echizen": "toyotomi",
                "kaga": "toyotomi",
                "noto": "toyotomi"
            },
            "message": "柴田勝家が滅亡し、羽柴秀吉が北陸諸国を完全に傘下に収めました！"
        }
    },

    # 1590 小田原征伐
    {
        "id": "evt_1590_odawara_fall",
        "scenarioId": "*",
        "year": 1590,
        "season": "夏",
        "title": "小田原開城・後北条氏滅亡と徳川関東移封",
        "desc": "豊臣秀吉の二十万の大軍が小田原城を包囲すること三ヶ月。北条氏政・氏直父子は開城降伏し後北条氏は滅亡。徳川家康は駿河・遠江・三河から関東二百五十万石へ移封され江戸に入府した！",
        "changes": {
            "territory": {
                "sagami": "tokugawa",
                "musashi": "tokugawa",
                "kozuke": "tokugawa",
                "shimotsuke": "tokugawa",
                "kazusa": "tokugawa",
                "shimousa": "tokugawa",
                "suruga": "toyotomi",
                "totomi": "toyotomi",
                "mikawa": "toyotomi",
                "kai": "toyotomi",
                "south_shinano": "toyotomi"
            },
            "message": "後北条氏が滅亡して豊臣秀吉が天下統一を達成！徳川家康は関東へ国替えとなりました！"
        }
    },

    # 1600 関ヶ原の戦い
    {
        "id": "evt_1600_sekigahara",
        "scenarioId": "*",
        "year": 1600,
        "season": "秋",
        "title": "関ヶ原の大決戦・天下分け目の東軍大勝利",
        "desc": "美濃関ヶ原にて徳川家康率いる東軍十万と石田三成率いる西軍八万が全面衝突！小早川秀秋の松尾山寝返りにより西軍は瓦解。三成らは捕縛処刑され、家康が天下の絶対的覇権を確立した！",
        "changes": {
            "territory": {
                "south_omi": "tokugawa",
                "north_omi": "ii",
                "mino": "tokugawa",
                "owari": "tokugawa",
                "settsu": "tokugawa",
                "kawachi": "tokugawa",
                "yamashiro": "tokugawa",
                "chikuzen": "kuroda"
            },
            "message": "徳川家康が関ヶ原の戦いに大勝利し、全国諸大名の領地を大規模に再編しました！"
        }
    },

    # 1615 大坂夏の陣
    {
        "id": "evt_1615_osaka_natsu",
        "scenarioId": "*",
        "year": 1615,
        "season": "夏",
        "title": "大坂夏の陣・天王寺決戦と元和偃武",
        "desc": "真田幸村が家康本陣へ三度の決死突撃を敢行し徳川軍を震撼させるも、圧倒的兵力の前に力尽き討死。大坂城天守は炎上し豊臣秀頼・淀殿は自刃。豊臣家は滅亡し『元和偃武』の泰平の世が到来した！",
        "changes": {
            "territory": {
                "settsu": "tokugawa",
                "kawachi": "tokugawa",
                "izumi": "tokugawa"
            },
            "message": "豊臣家が滅亡し、大坂城周辺が徳川幕府の直轄天領となりました！"
        }
    },

    # 1638 島原の乱終結
    {
        "id": "evt_1638_shimabara_fall",
        "scenarioId": "*",
        "year": 1638,
        "season": "春",
        "title": "原城総攻撃・島原の乱終結と天草天領化",
        "desc": "幕府追討総大将・松平信綱率いる十二万五千の大軍が原城へ総攻撃！天草四郎以下三万七千の一揆軍は玉砕。苛政の責任を問われた島原藩主・松倉勝家は斬首、唐津藩主・寺沢堅高は天草を没収され天領となった！",
        "changes": {
            "territory": {
                "hizen": "tokugawa",
                "higo": "tokugawa"
            },
            "message": "島原の乱が鎮圧され、反乱領地が幕府直轄天領として厳重に管理されました！"
        }
    },

    # 1651 慶安の変
    {
        "id": "evt_1651_keian_hen",
        "scenarioId": "1651",
        "year": 1651,
        "season": "秋",
        "title": "慶安の変と保科正之の文治政治",
        "desc": "軍学者・由井正雪と丸橋忠弥が企てた幕府転覆計画が事前に発覚！老中・松平信綱が電光石火で一味を捕縛。会津藩主・保科正之が主導して末期養子の禁を緩和し、浪人発生を防ぐ文治政治が始まった！",
        "changes": {
            "territory": {
                "musashi": "tokugawa",
                "suruga": "tokugawa"
            },
            "message": "慶安の変が未然に防がれ、幕府の文治政治への転換と天領支配が強固になりました！"
        }
    },

    # 1702 赤穂事件
    {
        "id": "evt_1702_ako_raid",
        "scenarioId": "1702",
        "year": 1702,
        "season": "冬",
        "title": "元禄赤穂事件・吉良邸討ち入りと播磨天領化",
        "desc": "大石内蔵助良雄率いる赤穂義士四十七名が本所吉良邸に乱入！亡君・浅野内匠頭の無念を晴らし吉良上野介を討ち取った。浅野家改易後の播磨赤穂藩領は幕府天領および譜代支配として編入された！",
        "changes": {
            "territory": {
                "harima": "tokugawa"
            },
            "message": "元禄赤穂事件の結着により、播磨赤穂が幕府天領・譜代支配に確定しました！"
        }
    },

    # 1721 享保の改革
    {
        "id": "evt_1721_meyasubako",
        "scenarioId": "1721",
        "year": 1721,
        "season": "秋",
        "title": "享保の改革・目安箱設置と天領新田開発",
        "desc": "8代将軍徳川吉宗が評定所前に『目安箱』を設置し、町奉行・大岡越前忠相を登用。全国の幕府直轄地で大規模な新田開発・治水工事を断行し、米価調整と幕府財政の黒字化を成し遂げた！",
        "changes": {
            "territory": {
                "musashi": "tokugawa",
                "echigo": "tokugawa",
                "yamashiro": "tokugawa"
            },
            "message": "享保の改革により全国天領の新田開発が進み、幕府直轄地が安定強化されました！"
        }
    },

    # 1789 寛政の改革
    {
        "id": "evt_1789_kijokurei",
        "scenarioId": "1789",
        "year": 1789,
        "season": "秋",
        "title": "寛政の改革・棄捐令発布と直轄領統制",
        "desc": "白河藩主・松平定信が老中首座に就任し寛政の改革を断行！旗本・御家人の借金を免除する『棄捐令』を発布し、昌平坂学問所で朱子学を奨励。白河・江戸・東海道の幕府支配基盤を再構築した！",
        "changes": {
            "territory": {
                "musashi": "tokugawa",
                "iwaki": "tokugawa",
                "totomi": "tokugawa"
            },
            "message": "寛政の改革が推進され、親藩・譜代大名による幕政中枢支配が再編されました！"
        }
    },

    # 1837 大塩平八郎の乱
    {
        "id": "evt_1837_oshio",
        "scenarioId": "1837",
        "year": 1837,
        "season": "春",
        "title": "大塩平八郎の乱・大坂市中蜂起",
        "desc": "天保の大飢饉に苦しむ民衆を見捨て買占めに走る豪商と幕府に対し、元大坂町奉行所与力・大塩平八郎が『救民』の旗を掲げて武装蜂起！大坂市街の大半が炎上し、幕府の権威は根底から覆された！",
        "changes": {
            "territory": {
                "settsu": "tokugawa",
                "kawachi": "tokugawa"
            },
            "message": "大塩平八郎の乱が鎮圧されるも、幕府直轄都市大坂の防備が厳重に再編されました！"
        }
    },

    # 1853 ペリー来航
    {
        "id": "evt_1853_perry",
        "scenarioId": "1853",
        "year": 1853,
        "season": "夏",
        "title": "ペリー来航・黒船ショックとお台場築造",
        "desc": "『泰平の眠りを覚ます上喜撰』アメリカ海軍ペリー提督率いる黒船四隻が浦賀沖に出現！幕府は海防令を発布し、江川英龍にお台場砲台の築造を命令。相模・伊豆・武蔵の江戸湾防備が急ピッチで進められた！",
        "changes": {
            "territory": {
                "musashi": "tokugawa",
                "sagami": "tokugawa",
                "izu": "tokugawa"
            },
            "message": "黒船来航により幕府は江戸湾要塞化を断行、直轄防衛態勢を構築しました！"
        }
    },

    # 1860 桜田門外の変
    {
        "id": "evt_1860_sakuradamon",
        "scenarioId": "1860",
        "year": 1860,
        "season": "春",
        "title": "桜田門外の変・大老井伊直弼暗殺",
        "desc": "安政の大獄で尊攘派を弾圧した大老・井伊直弼の行列が、雪の桜田門外で水戸・薩摩浪士十八名に襲撃され直弼は落命！彦根藩は衝撃に包まれ、幕府の独裁権力は致命的な打撃を受けた！",
        "changes": {
            "territory": {
                "musashi": "tokugawa",
                "north_omi": "ii"
            },
            "message": "大老井伊直弼が暗殺され、幕府の権威が失墜し尊王攘夷派が各地で台頭しました！"
        }
    },

    # 1866 第二次長州征伐（四境戦争）
    {
        "id": "evt_1866_satcho_shikyo",
        "scenarioId": "1866",
        "year": 1866,
        "season": "夏",
        "title": "四境戦争（第二次長州征伐）・奇兵隊の快進撃",
        "desc": "幕府軍十万による長州征伐に対し、高杉晋作の奇兵隊と大村益次郎の洋式軍備が芸州口・石州口・小倉口で幕府軍を連破！小倉城は自焼開城し、長州藩が山陽・山陰・北九州で圧倒的勝利を収めた！",
        "changes": {
            "territory": {
                "suo": "mori",
                "nagato": "mori",
                "buzen": "mori",
                "iwami": "mori"
            },
            "message": "長州藩が四境戦争で幕府軍を壊滅させ、周防・長門・豊前・石見を掌握しました！"
        }
    },

    # 1868 戊辰戦争
    {
        "id": "evt_1868_toba_fushimi",
        "scenarioId": "1868",
        "year": 1868,
        "season": "春",
        "title": "鳥羽・伏見の戦い・錦の御旗の翻り",
        "desc": "鳥羽・伏見で旧幕府軍一万五千と薩長軍五千が激突！新政府軍に『錦の御旗』が掲げられると旧幕府軍は朝敵となる恐怖から総崩れ。徳川慶喜は大坂城から海路江戸へ退却し、近畿全土が新政府軍に落ちた！",
        "changes": {
            "territory": {
                "yamashiro": "meiji",
                "settsu": "meiji",
                "kawachi": "meiji",
                "izumi": "meiji",
                "yamato": "meiji"
            },
            "message": "鳥羽・伏見の戦いで新政府軍が大勝利し、近畿全土が明治新政府の支配下に入りました！"
        }
    },
    {
        "id": "evt_1868_edo_castle_open",
        "scenarioId": "1868",
        "year": 1868,
        "season": "夏",
        "title": "江戸城無血開城・勝海舟と西郷隆盛の会談",
        "desc": "東征大総督府参謀・西郷隆盛と陸軍総裁・勝海舟の命がけの直談判により、江戸総攻撃は直前で中止！江戸城は平和裏に新政府軍へ引き渡され、徳川慶喜は水戸へ退去、関東諸国が新政府の管轄となった！",
        "changes": {
            "territory": {
                "musashi": "meiji",
                "sagami": "meiji",
                "suruga": "tokugawa"
            },
            "message": "江戸城が無血開城され、武蔵・相模が新政府領となり徳川家は駿府へ移封されました！"
        }
    },
    {
        "id": "evt_1868_aizu_surrender",
        "scenarioId": "1868",
        "year": 1868,
        "season": "秋",
        "title": "会津鶴ヶ城開城・奥羽越列藩同盟の崩壊",
        "desc": "新政府軍の新鋭アームストロング砲が会津若松城を容赦なく砲撃。白虎隊の自刃など悲劇が相次ぐ中、松平容保公は降伏開城。米沢・仙台など奥羽越列藩同盟加盟諸藩も雪崩を打って降伏した！",
        "changes": {
            "territory": {
                "iwashiro": "meiji",
                "iwaki": "meiji",
                "echigo": "meiji",
                "rikuzen": "meiji"
            },
            "message": "会津若松城が開城し、東北全土が明治新政府軍に平定されました！"
        }
    },
    {
        "id": "evt_1869_goryokaku_fall",
        "scenarioId": "1868",
        "year": 1869,
        "season": "夏",
        "title": "箱館五稜郭開城・戊辰戦争の終焉と明治維新",
        "desc": "新政府軍が箱館五稜郭を海陸から総攻撃！土方歳三は一本木関門で壮烈に戦死、榎本武揚ら蝦夷共和国幹部は降伏した。一年半に及ぶ戊辰戦争は完全に終結し、日本全土の明治維新統一が達成された！",
        "changes": {
            "territory": {
                "ezo": "meiji"
            },
            "message": "箱館五稜郭が開城して戊辰戦争が終結し、日本全土が新政府のもとに統一されました！"
        }
    }
]
