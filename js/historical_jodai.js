// 無名の「城代」を、その年代にその国へ史料上置ける武将で埋める。
// 当主・既存家臣を配ったあとに残る支城だけを対象にする。同名の既存武将は足さない。
(function () {
  if (window.__HISTORICAL_JODAI_LOADED) return;
  window.__HISTORICAL_JODAI_LOADED = true;
  if (!window.OFFICERS_MASTER || !window.SCENARIO_HISTORICAL_GOVERNORS) return;

  const existing = new Set(window.OFFICERS_MASTER.map(o => o.name));

  function eraOf(year) {
    if (year < 1100) return "ancient";
    if (year < 1192) return "heian";
    if (year < 1333) return "kamakura";
    if (year < 1392) return "nanboku";
    if (year < 1573) return "muromachi";
    if (year < 1615) return "sengoku";
    if (year < 1860) return "edo";
    return "bakumatsu";
  }

  // posts: その年のその国。寿命は史料の生没に合わせ、シナリオ年に15歳以上で生存する範囲だけ載せる。
  const roster = [
    { name: "島田惟幹", birth: 900, death: 945, mil: 62, pol: 58, intel: 60, skill: "播磨介", lore: "天慶2年の播磨介。藤原文元らに摂津須岐駅で襲撃され、純友の乱の発端に巻き込まれた国司。", posts: [{ year: "939", prov: "harima", clan: "heian_court" }] },
    { name: "藤原文元", birth: 900, death: 941, mil: 78, pol: 55, intel: 72, skill: "備前の海賊", lore: "純友の乱の急先鋒。備前・播磨を拠点に国司を襲撃し、山陽道の海賊衆を率いた。", posts: [{ year: "939", prov: "bingo", clan: "fujiwara_sumitomo" }] },
    { name: "藤原恒利", birth: 895, death: 941, mil: 74, pol: 60, intel: 76, skill: "純友の次将", lore: "伊予で純友の次将を務めた。のち朝廷に降り、日振島攻撃の案内役となった。", posts: [{ year: "939", prov: "awaji", clan: "fujiwara_sumitomo" }] },
    { name: "橘遠保", birth: 890, death: 941, mil: 80, pol: 64, intel: 70, skill: "純友追捕", lore: "大宰府側の武士。天慶4年、逃亡した藤原純友を捕らえたと伝わる西海の武人。", posts: [{ year: "939", prov: "buzen", clan: "otomo" }] },

    { name: "伊藤忠清", birth: 1120, death: 1185, mil: 76, pol: 62, intel: 68, skill: "平家の侍大将", lore: "平家の実務を担った侍大将。都と西国の間で軍勢を整え、一門の合戦を支えた。", posts: [{ year: "1180", prov: "settsu", clan: "taira" }] },
    { name: "平通盛", birth: 1153, death: 1184, mil: 74, pol: 66, intel: 64, skill: "越前守", lore: "清盛の孫。越前守として北陸に関わり、一ノ谷で討ち死にした平家の公達。", posts: [{ year: "1180", prov: "echizen", clan: "taira" }] },
    { name: "平資盛", birth: 1161, death: 1184, mil: 72, pol: 60, intel: 66, skill: "新三位", lore: "重盛の子。平家都落ち後も一門に従い、壇ノ浦で入水した。", posts: [{ year: "1180", prov: "kaga", clan: "taira" }] },
    { name: "平貞能", birth: 1130, death: 1185, mil: 70, pol: 68, intel: 72, skill: "平家侍", lore: "平家に仕えた実務派の侍。都落ちの途次も一門の身辺を守った。", posts: [{ year: "1180", prov: "ise", clan: "taira" }] },
    { name: "平盛俊", birth: 1148, death: 1184, mil: 84, pol: 58, intel: 62, skill: "平家の猛将", lore: "盛国の子。一ノ谷で源氏方の猪俣則綱と組み打ちし、討ち死にした平家の猛将。", posts: [{ year: "1180", prov: "bicchu", clan: "taira" }] },
    { name: "平経正", birth: 1138, death: 1184, mil: 68, pol: 70, intel: 74, skill: "琵琶の公達", lore: "経盛の子。楽才で知られ、一ノ谷で討ち死にした平家の公達。", posts: [{ year: "1180", prov: "north_omi", clan: "taira" }] },

    { name: "原胤房", birth: 1422, death: 1494, mil: 78, pol: 70, intel: 74, skill: "千葉の宿老", lore: "下総千葉氏の宿老・原氏。享徳の乱で宗家を支え、上総・下総の実戦を預かる。", posts: [{ year: "1467", prov: "kazusa", clan: "chiba" }, { year: "1495", prov: "kazusa", clan: "chiba" }] },
    { name: "武田信賢", birth: 1420, death: 1471, mil: 74, pol: 72, intel: 70, skill: "若狭守護", lore: "若狭武田氏。応仁の乱では細川方に与し、若狭の軍勢を率いた。", posts: [{ year: "1467", prov: "wakasa", clan: "ashikaga" }] },
    { name: "武田元信", birth: 1454, death: 1536, mil: 72, pol: 76, intel: 74, skill: "若狭武田", lore: "若狭守護。明応から大永にかけて若狭を保ち、朝廷や幕府とのパイプを持った。", posts: [{ year: "1495", prov: "wakasa", clan: "ashikaga" }] },

    { name: "正木時茂", birth: 1513, death: 1561, mil: 86, pol: 68, intel: 78, skill: "上総の正木", lore: "里見家臣。上総大多喜・勝浦を押さえ、北条との境目を戦った房総の猛将。", posts: [{ year: "1546", prov: "kazusa", clan: "satomi" }] },
    { name: "松永長頼", birth: 1518, death: 1565, mil: 80, pol: 72, intel: 84, skill: "丹波仕置", lore: "三好長慶の重臣。丹波に入って八木城などを押さえ、丹波仕置を担った。", posts: [{ year: "1546", prov: "tamba", clan: "miyoshi" }] },
    { name: "山名豊定", birth: 1512, death: 1560, mil: 74, pol: 76, intel: 72, skill: "因幡下向", lore: "但馬守護山名祐豊の弟。天文年間に因幡へ下り、鳥取・岩井を拠点に東因幡を固めた。", posts: [{ year: "1546", prov: "inaba", clan: "yamana" }, { year: "1560", prov: "inaba", clan: "yamana" }] },
    { name: "武田高信", birth: 1529, death: 1573, mil: 78, pol: 60, intel: 70, skill: "鳥取城主", lore: "因幡の山名家臣から頭角を現し、永禄年間に鳥取城を押さえて因幡の実権を握った。", posts: [{ year: "1570", prov: "inaba", clan: "yamana" }] },
    { name: "本城常光", birth: 1514, death: 1562, mil: 82, pol: 64, intel: 74, skill: "山吹城", lore: "尼子家臣。石見銀山の要・山吹城を預かり、毛利の石見攻めを何度も撃退した。", posts: [{ year: "1546", prov: "iwami", clan: "amago" }] },
    { name: "三村家親", birth: 1517, death: 1566, mil: 84, pol: 70, intel: 76, skill: "備中の旗頭", lore: "備中の国人盟主。備中松山周辺を固め、尼子・毛利の間で備中の帰趨を左右した。", posts: [{ year: "1495", prov: "bicchu", clan: "amago" }, { year: "1546", prov: "bicchu", clan: "amago" }] },
    { name: "山内隆通", birth: 1508, death: 1560, mil: 76, pol: 72, intel: 70, skill: "備後国人", lore: "備後の国人。天文年間は尼子の影響下にあり、のち毛利へ転じた備後北部の旗頭。", posts: [{ year: "1546", prov: "bingo", clan: "amago" }] },
    { name: "篠原長房", birth: 1514, death: 1573, mil: 80, pol: 74, intel: 78, skill: "三好の執政", lore: "三好家の宿老。阿波・讃岐の仕置と畿内出陣を仕切り、長慶死後の家政を支えた。", posts: [{ year: "1546", prov: "sanuki", clan: "miyoshi" }, { year: "1570", prov: "sanuki", clan: "miyoshi" }] },
    { name: "安宅冬康", birth: 1528, death: 1564, mil: 78, pol: 66, intel: 72, skill: "淡路水軍", lore: "三好長慶の弟。淡路を本拠に水軍を率い、畿内と四国を結ぶ海路を押さえた。", posts: [{ year: "1546", prov: "awaji", clan: "miyoshi" }, { year: "1560", prov: "awaji", clan: "miyoshi" }] },
    { name: "安宅信康", birth: 1552, death: 1578, mil: 72, pol: 64, intel: 68, skill: "淡路守護", lore: "冬康の子。父の死後に淡路を継ぎ、三好一族の海上拠点を守った。", posts: [{ year: "1570", prov: "awaji", clan: "miyoshi" }] },
    { name: "麻生弘家", birth: 1490, death: 1560, mil: 74, pol: 68, intel: 66, skill: "豊前花尾", lore: "豊前の国人麻生氏。天文年間、大内氏の傘下で花尾城など豊前の城を守った。", posts: [{ year: "1546", prov: "chikuzen", clan: "ouchi" }] },
    { name: "大浦為則", birth: 1520, death: 1567, mil: 72, pol: 70, intel: 68, skill: "津軽の大浦", lore: "南部氏傘下の大浦氏。津軽を地盤とし、のち為信が独立する直前の当主。", posts: [{ year: "1546", prov: "tsugaru", clan: "nanbu" }, { year: "1560", prov: "tsugaru", clan: "nanbu" }] },
    { name: "垣屋光成", birth: 1525, death: 1595, mil: 76, pol: 64, intel: 70, skill: "但馬垣屋", lore: "但馬山名氏の重臣。但馬・丹後境の城を預かり、山名家の軍事を担った。", posts: [{ year: "1546", prov: "tango", clan: "yamana" }, { year: "1560", prov: "tango", clan: "yamana" }, { year: "1570", prov: "tango", clan: "yamana" }, { year: "1590", prov: "tajima", clan: "toyotomi" }] },
    { name: "福原貞俊", birth: 1513, death: 1593, mil: 74, pol: 78, intel: 76, skill: "毛利宿老", lore: "毛利元就の宿老。備後・安芸の境目と内政を預かり、毛利政権の柱となった。", posts: [{ year: "1560", prov: "bingo", clan: "mori" }, { year: "1570", prov: "bingo", clan: "mori" }] },
    { name: "益田藤兼", birth: 1545, death: 1613, mil: 76, pol: 74, intel: 72, skill: "石見益田", lore: "石見の国人益田氏。毛利に属して七尾城・三宅御土居を拠点に石見を守った。", posts: [{ year: "1560", prov: "iwami", clan: "mori" }, { year: "1570", prov: "iwami", clan: "mori" }, { year: "1582", prov: "iwami", clan: "mori" }] },

    { name: "村井貞勝", birth: 1528, death: 1582, mil: 70, pol: 88, intel: 80, skill: "京都所司代", lore: "信長の京都所司代。本能寺の変の当夜、二条御所で誠仁親王を守って討ち死にした。", posts: [{ year: "1582", prov: "yamashiro", clan: "oda" }] },
    { name: "滝川雄利", birth: 1543, death: 1610, mil: 74, pol: 76, intel: 72, skill: "伊賀守護", lore: "滝川一益の一族。天正伊賀の乱の後、伊賀を預けられ平定後の仕置を担った。", posts: [{ year: "1582", prov: "iga", clan: "oda" }] },
    { name: "斎藤利三", birth: 1534, death: 1582, mil: 82, pol: 70, intel: 78, skill: "亀山城代", lore: "明智光秀の重臣。丹波亀山城を預かり、本能寺の変後に安土で処刑された。", posts: [{ year: "1582", prov: "tamba", clan: "oda" }] },
    { name: "三好康長", birth: 1523, death: 1589, mil: 76, pol: 72, intel: 74, skill: "若江城", lore: "河内の三好一族。信長に降り、河内若江城を守って畿内の南を押さえた。", posts: [{ year: "1582", prov: "kawachi", clan: "oda" }] },
    { name: "蜂屋頼隆", birth: 1534, death: 1589, mil: 74, pol: 70, intel: 68, skill: "岸和田城", lore: "織田家臣。和泉岸和田城を預かり、大坂湾に面した和泉の抑えとなった。", posts: [{ year: "1582", prov: "izumi", clan: "oda" }] },
    { name: "筒井定次", birth: 1562, death: 1615, mil: 72, pol: 74, intel: 70, skill: "大和筒井", lore: "筒井順慶の養子。天正期の大和で筒井家の城と軍勢を預かった。", posts: [{ year: "1582", prov: "yamato", clan: "oda" }] },
    { name: "神子田正治", birth: 1543, death: 1593, mil: 74, pol: 72, intel: 70, skill: "姫路城代", lore: "羽柴秀吉の家臣。中国攻めのとき姫路城代を務め、播磨の抑えを任された。", posts: [{ year: "1582", prov: "harima", clan: "oda" }] },
    { name: "宮部継潤", birth: 1540, death: 1604, mil: 76, pol: 80, intel: 74, skill: "鳥取城主", lore: "もと浅井家臣で秀吉に属す。鳥取城を与えられ因幡・伯耆の仕置を担った。", posts: [{ year: "1582", prov: "inaba", clan: "oda" }, { year: "1590", prov: "inaba", clan: "toyotomi" }] },
    { name: "南条元続", birth: 1549, death: 1591, mil: 74, pol: 66, intel: 70, skill: "伯耆羽衣石", lore: "伯耆の国人。羽衣石城を本拠に毛利・豊臣の間で伯耆東部を守った。", posts: [{ year: "1582", prov: "hoki", clan: "mori" }] },
    { name: "内藤隆春", birth: 1528, death: 1595, mil: 72, pol: 74, intel: 70, skill: "長門内藤", lore: "毛利家臣。長門を預けられ、西の押さえとして毛利の防長経営を支えた。", posts: [{ year: "1582", prov: "nagato", clan: "mori" }, { year: "1590", prov: "nagato", clan: "mori" }] },
    { name: "香川親和", birth: 1560, death: 1587, mil: 74, pol: 68, intel: 72, skill: "天霧城", lore: "讃岐西部の香川氏。長宗我部元親の姻族として天霧城を守り、阿讃の境を預かった。", posts: [{ year: "1582", prov: "sanuki", clan: "chosokabe" }] },
    { name: "谷忠澄", birth: 1544, death: 1601, mil: 78, pol: 70, intel: 74, skill: "阿波仕置", lore: "長宗我部家臣。阿波平定後に現地の仕置を任され、四国攻めの前線を支えた。", posts: [{ year: "1582", prov: "awa_shikoku", clan: "chosokabe" }] },
    { name: "福留親政", birth: 1540, death: 1586, mil: 80, pol: 64, intel: 72, skill: "長宗我部の槍", lore: "長宗我部の武将。四国平定と戸次川の戦いに従い、伊予・豊後方面の先鋒を務めた。", posts: [{ year: "1582", prov: "iyo", clan: "chosokabe" }] },
    { name: "田尻鑑種", birth: 1528, death: 1588, mil: 76, pol: 68, intel: 74, skill: "筑後田尻", lore: "筑後の国人。龍造寺隆信に属して筑後の城を守ったが、のち離反した。", posts: [{ year: "1582", prov: "chikugo", clan: "ryuzoji" }] },
    { name: "成松信勝", birth: 1530, death: 1584, mil: 80, pol: 62, intel: 68, skill: "龍造寺四天王", lore: "龍造寺隆信の重臣。肥後攻めに従い、沖田畷の戦いで討ち死にした。", posts: [{ year: "1582", prov: "higo", clan: "ryuzoji" }] },
    { name: "毛利秀頼", birth: 1550, death: 1582, mil: 74, pol: 70, intel: 68, skill: "飯田城", lore: "織田家の毛利新介秀頼。武田滅亡後、南信濃飯田城を預けられた。", posts: [{ year: "1582", prov: "south_shinano", clan: "oda" }] },

    { name: "桑山重晴", birth: 1524, death: 1606, mil: 74, pol: 76, intel: 72, skill: "紀伊和歌山", lore: "秀吉の家臣。紀伊平定後に和歌山城を預けられ、紀伊の抑えとなった。", posts: [{ year: "1590", prov: "kii", clan: "toyotomi" }] },
    { name: "小出秀政", birth: 1540, death: 1604, mil: 72, pol: 78, intel: 70, skill: "岸和田城", lore: "秀吉の妻ねねの縁者。和泉岸和田城主として大坂の南を守った。", posts: [{ year: "1590", prov: "izumi", clan: "toyotomi" }] },
    { name: "亀井茲矩", birth: 1557, death: 1612, mil: 76, pol: 74, intel: 78, skill: "鹿野城", lore: "尼子旧臣から秀吉に属す。因幡鹿野を与えられ、山陰の豊臣大名として朝鮮にも渡った。", posts: [{ year: "1590", prov: "hoki", clan: "toyotomi" }] },
    { name: "戸川達安", birth: 1567, death: 1628, mil: 78, pol: 72, intel: 74, skill: "美作戸川", lore: "宇喜多・豊臣に仕えた美作の武将。美作の城を預かり、関ヶ原では宇喜多隊に連なった。", posts: [{ year: "1590", prov: "mimasaka", clan: "toyotomi" }] },
    { name: "宇喜多秀家", birth: 1572, death: 1655, mil: 84, pol: 72, intel: 78, skill: "備前宰相", lore: "宇喜多直家の子。備前岡山を本拠に五大大名の一人となり、関ヶ原では西軍の主力を率いた。", posts: [{ year: "1590", prov: "bizen", clan: "toyotomi" }] },
    { name: "花房職秀", birth: 1553, death: 1621, mil: 76, pol: 74, intel: 72, skill: "宇喜多家老", lore: "宇喜多直家・秀家の重臣。備前の城地と軍務を預かり、関ヶ原では宇喜多隊の一翼を担った。", posts: [{ year: "1600", prov: "bizen", clan: "ukita" }] },
    { name: "蜂須賀家政", birth: 1558, death: 1639, mil: 76, pol: 80, intel: 74, skill: "阿波徳島", lore: "蜂須賀正勝の子。天正13年に阿波を与えられ、徳島を本拠に阿波の仕置を進めた。", posts: [{ year: "1590", prov: "awa_shikoku", clan: "toyotomi" }] },
    { name: "毛利勝信", birth: 1546, death: 1601, mil: 74, pol: 72, intel: 70, skill: "豊前小倉", lore: "秀吉の家臣。豊前小倉城を預けられ、九州仕置後の豊前を守った。", posts: [{ year: "1590", prov: "buzen", clan: "toyotomi" }] },
    { name: "小早川秀包", birth: 1567, death: 1601, mil: 80, pol: 74, intel: 76, skill: "筑後久留米", lore: "元就の九男。筑後久留米を与えられ、九州の小早川勢を率いた。", posts: [{ year: "1590", prov: "chikugo", clan: "toyotomi" }] },
    { name: "立花宗茂", birth: 1567, death: 1643, mil: 90, pol: 78, intel: 82, skill: "西国無双", lore: "立花道雪の養子。筑後柳川を本拠に、九州の合戦と朝鮮の役で名を上げた。", posts: [{ year: "1590", prov: "chikuzen", clan: "toyotomi" }] },
    { name: "鍋島直茂", birth: 1538, death: 1618, mil: 84, pol: 86, intel: 88, skill: "肥前鍋島", lore: "龍造寺家の実権を握り、秀吉の九州仕置後は肥前の執政として鍋島家の基礎を築いた。", posts: [{ year: "1590", prov: "hizen", clan: "toyotomi" }] },
    { name: "脇坂安治", birth: 1554, death: 1626, mil: 82, pol: 70, intel: 76, skill: "洲本水軍", lore: "秀吉の水軍奉行。淡路洲本を与えられ、大坂湾の海上を守った。", posts: [{ year: "1590", prov: "awaji", clan: "toyotomi" }, { year: "1600", prov: "awaji", clan: "tokugawa" }] },
    { name: "毛利元康", birth: 1550, death: 1601, mil: 74, pol: 70, intel: 72, skill: "備中毛利", lore: "毛利一門。備中の城を預けられ、山陽道の境目を守った。", posts: [{ year: "1590", prov: "bicchu", clan: "mori" }, { year: "1600", prov: "bicchu", clan: "mori" }] },
    { name: "福原広俊", birth: 1551, death: 1600, mil: 72, pol: 76, intel: 74, skill: "備後福原", lore: "毛利家臣福原氏。備後の城地を預かり、防長と山陽の連絡を担った。", posts: [{ year: "1590", prov: "bingo", clan: "mori" }, { year: "1600", prov: "bingo", clan: "mori" }] },
    { name: "冷泉元豊", birth: 1555, death: 1611, mil: 74, pol: 72, intel: 70, skill: "周防冷泉", lore: "毛利家臣。周防の城を預けられ、防長の東を固めた。", posts: [{ year: "1590", prov: "suo", clan: "mori" }] },

    { name: "長連龍", birth: 1538, death: 1615, mil: 80, pol: 72, intel: 74, skill: "能登の長", lore: "能登の国人から前田家臣。七尾の戦いの後も能登の城を預かり、加賀の北を守った。", posts: [{ year: "1600", prov: "noto", clan: "maeda" }, { year: "1614", prov: "noto", clan: "maeda" }] },
    { name: "青山吉次", birth: 1556, death: 1608, mil: 74, pol: 80, intel: 78, skill: "越中仕置", lore: "前田利家の重臣。越中の仕置と城普請を任され、前田家の越中支配を固めた。", posts: [{ year: "1600", prov: "etchu", clan: "maeda" }] },
    { name: "木下勝俊", birth: 1569, death: 1649, mil: 68, pol: 74, intel: 72, skill: "若狭小浜", lore: "若狭小浜城主。関ヶ原では西軍に与し、戦後に改易された。", posts: [{ year: "1600", prov: "wakasa", clan: "ishida" }] },
    { name: "桑山一晴", birth: 1560, death: 1630, mil: 72, pol: 74, intel: 70, skill: "和歌山城代", lore: "桑山重晴の子。紀伊和歌山の城代として浅野家の紀伊入りを現地で支えた。", posts: [{ year: "1600", prov: "kii", clan: "asano" }] },
    { name: "益田元祥", birth: 1562, death: 1621, mil: 74, pol: 76, intel: 72, skill: "石見益田", lore: "益田藤兼の子。関ヶ原前後の石見を預かり、毛利の西端を守った。", posts: [{ year: "1600", prov: "iwami", clan: "mori" }] },
    { name: "毛利秀元", birth: 1579, death: 1650, mil: 80, pol: 78, intel: 82, skill: "毛利の総大将", lore: "毛利輝元の養子。関ヶ原では南宮山に布陣し、戦後は長門長府を領した。", posts: [{ year: "1600", prov: "nagato", clan: "mori" }, { year: "1637", prov: "nagato", clan: "mori" }] },
    { name: "大久保長安", birth: 1545, death: 1613, mil: 60, pol: 92, intel: 88, skill: "佐渡奉行", lore: "家康の金山奉行。関ヶ原後に佐渡金山を預かり、佐渡奉行として島を治めた。", posts: [{ year: "1600", prov: "sado", clan: "tokugawa" }, { year: "1614", prov: "sado", clan: "tokugawa" }] },

    { name: "本多正純", birth: 1565, death: 1637, mil: 70, pol: 90, intel: 86, skill: "駿府の老臣", lore: "本多正信の子。家康の駿府大御所を側近として支え、幕府の実務を仕切った。", posts: [{ year: "1614", prov: "suruga", clan: "tokugawa" }] },
    { name: "松平忠輝", birth: 1592, death: 1683, mil: 72, pol: 60, intel: 64, skill: "越後高田", lore: "家康の子。越後高田を領し、大坂の陣にも出陣した。元和2年に改易される。", posts: [{ year: "1614", prov: "echigo", clan: "tokugawa" }] },
    { name: "京極忠高", birth: 1593, death: 1637, mil: 74, pol: 76, intel: 72, skill: "若狭京極", lore: "京極高次の子。若狭小浜を継ぎ、晩年には出雲松江へ移る直前まで若狭を治めた。", posts: [{ year: "1614", prov: "wakasa", clan: "tokugawa" }, { year: "1637", prov: "izumo", clan: "tokugawa" }] },
    { name: "金森可重", birth: 1559, death: 1616, mil: 74, pol: 78, intel: 72, skill: "飛騨高山", lore: "金森長近の後継。飛騨高山を預かり、高山城下の町割を進めた。", posts: [{ year: "1614", prov: "hida", clan: "tokugawa" }] },
    { name: "金森重頼", birth: 1596, death: 1654, mil: 70, pol: 80, intel: 74, skill: "高山藩", lore: "飛騨高山藩主。寛永期の飛騨を治め、幕府の山中領として高山を保った。", posts: [{ year: "1637", prov: "hida", clan: "tokugawa" }] },
    { name: "奥平信昌", birth: 1555, death: 1615, mil: 80, pol: 74, intel: 72, skill: "美濃加納", lore: "家康の女婿。関ヶ原後に美濃加納を領し、大坂の陣の頃まで美濃を守った。", posts: [{ year: "1614", prov: "mino", clan: "tokugawa" }] },
    { name: "九鬼守隆", birth: 1573, death: 1632, mil: 78, pol: 70, intel: 74, skill: "鳥羽水軍", lore: "志摩鳥羽の九鬼氏。大坂の陣では幕府方の水軍として海路を担った。", posts: [{ year: "1614", prov: "shima", clan: "tokugawa" }] },
    { name: "藤堂高吉", birth: 1578, death: 1642, mil: 74, pol: 72, intel: 70, skill: "伊賀上野", lore: "藤堂高虎の弟。伊賀上野の城地を預かり、伊勢津藩の西を固めた。", posts: [{ year: "1614", prov: "iga", clan: "tokugawa" }] },
    { name: "木俣守勝", birth: 1568, death: 1643, mil: 76, pol: 82, intel: 78, skill: "彦根の家老", lore: "井伊家の家老。彦根城の普請と城地の仕置を任され、井伊直孝を支えた。", posts: [{ year: "1614", prov: "south_omi", clan: "ii" }, { year: "1637", prov: "south_omi", clan: "ii" }] },
    { name: "松平忠明", birth: 1583, death: 1644, mil: 76, pol: 80, intel: 74, skill: "大和郡山", lore: "家康の外孫。大坂の陣の後、大和郡山藩主として奈良盆地を治めた。", posts: [{ year: "1637", prov: "yamato", clan: "tokugawa" }] },
    { name: "阿部正次", birth: 1569, death: 1647, mil: 78, pol: 86, intel: 80, skill: "大坂城代", lore: "譜代大名。寛永3年から大坂城代を二十余年務め、島原の乱では江戸と九州の連絡を仕切った。", posts: [{ year: "1637", prov: "settsu", clan: "tokugawa" }] },
    { name: "板倉重宗", birth: 1586, death: 1657, mil: 70, pol: 90, intel: 86, skill: "京都所司代", lore: "板倉勝重の子。元和6年から京都所司代を務め、朝廷と畿内の幕府領を監督した。", posts: [{ year: "1637", prov: "yamashiro", clan: "tokugawa" }] },
    { name: "本多政朝", birth: 1599, death: 1638, mil: 74, pol: 78, intel: 72, skill: "姫路藩主", lore: "本多忠勝の孫。寛永8年に播磨姫路藩を継ぎ、島原の乱の頃まで西国の要を守った。", posts: [{ year: "1637", prov: "harima", clan: "tokugawa" }] },
    { name: "亀井茲政", birth: 1617, death: 1681, mil: 70, pol: 74, intel: 68, skill: "津和野藩", lore: "石見津和野藩主。父政矩の死後、寛永期の石見西部を治めた。", posts: [{ year: "1637", prov: "iwami", clan: "tokugawa" }] },
    { name: "森長継", birth: 1610, death: 1698, mil: 72, pol: 78, intel: 70, skill: "津山藩", lore: "美作津山藩主。森忠政の後を受け、寛永期の美作を治めた。", posts: [{ year: "1637", prov: "mimasaka", clan: "tokugawa" }] },
    { name: "小笠原忠真", birth: 1596, death: 1667, mil: 76, pol: 80, intel: 74, skill: "小倉藩主", lore: "豊前小倉藩主。寛永9年に小倉へ入り、島原の乱では九州の譜代として陣に連なった。", posts: [{ year: "1637", prov: "buzen", clan: "tokugawa" }] },
    { name: "荒尾成利", birth: 1586, death: 1654, mil: 72, pol: 80, intel: 74, skill: "米子城代", lore: "鳥取池田家の家老。伯耆米子城代を世襲し、山陰の城地を預かった。", posts: [{ year: "1637", prov: "hoki", clan: "tokugawa" }] },
    { name: "京極高広", birth: 1599, death: 1677, mil: 72, pol: 76, intel: 70, skill: "宮津藩", lore: "丹後宮津藩主。京極高知の後を受け、寛永期の丹後を治めた。", posts: [{ year: "1637", prov: "tango", clan: "tokugawa" }] },
    { name: "藤堂高次", birth: 1602, death: 1676, mil: 74, pol: 82, intel: 76, skill: "津藩主", lore: "藤堂高虎の後継。伊勢津藩を継ぎ、寛永期の伊勢を治めた。", posts: [{ year: "1637", prov: "ise", clan: "tokugawa" }] },
    { name: "内藤忠重", birth: 1592, death: 1660, mil: 72, pol: 74, intel: 70, skill: "鳥羽藩", lore: "志摩鳥羽藩主。九鬼氏に代わり寛永期の鳥羽を領し、伊勢湾の海口を守った。", posts: [{ year: "1637", prov: "shima", clan: "tokugawa" }] },
    { name: "酒井忠勝", birth: 1587, death: 1662, mil: 74, pol: 88, intel: 84, skill: "小浜藩・大老", lore: "若狭小浜藩主。寛永11年に若狭へ入り、のち大老として幕政を預かった。", posts: [{ year: "1637", prov: "wakasa", clan: "tokugawa" }] },
    { name: "戸田氏鉄", birth: 1576, death: 1655, mil: 76, pol: 80, intel: 74, skill: "大垣藩", lore: "美濃大垣藩主。寛永期の美濃西部を治め、西国街道の抑えとなった。", posts: [{ year: "1637", prov: "mino", clan: "tokugawa" }] },
    { name: "松平忠晴", birth: 1598, death: 1669, mil: 72, pol: 74, intel: 70, skill: "亀山藩", lore: "丹波亀山藩主。寛永期に丹波の城を預かり、京と西国の中間を守った。", posts: [{ year: "1637", prov: "tamba", clan: "tokugawa" }] },
    { name: "小出吉英", birth: 1587, death: 1666, mil: 70, pol: 76, intel: 68, skill: "出石藩", lore: "但馬出石藩主。小出氏として寛永期の但馬を治めた。", posts: [{ year: "1637", prov: "tajima", clan: "tokugawa" }] },
    { name: "松平康重", birth: 1568, death: 1640, mil: 74, pol: 78, intel: 72, skill: "岸和田藩", lore: "和泉岸和田藩主。寛永期まで和泉を領し、大坂の南を固めた。", posts: [{ year: "1637", prov: "izumi", clan: "tokugawa" }] },
    { name: "木下利次", birth: 1605, death: 1666, mil: 68, pol: 74, intel: 70, skill: "足守藩", lore: "備中足守藩主。秀吉正室ねねの縁につながる木下家として備中を治めた。", posts: [{ year: "1637", prov: "bicchu", clan: "tokugawa" }] },
    { name: "生駒高俊", birth: 1611, death: 1659, mil: 66, pol: 70, intel: 64, skill: "高松藩", lore: "讃岐高松藩主。生駒親正の孫。寛永14年の時点ではなお高松を領していた。", posts: [{ year: "1637", prov: "sanuki", clan: "tokugawa" }] },
    { name: "松平定行", birth: 1587, death: 1668, mil: 74, pol: 80, intel: 74, skill: "伊予松山", lore: "久松松平氏。寛永12年に伊予松山へ入り、伊予の中心を治めた。", posts: [{ year: "1637", prov: "iyo", clan: "tokugawa" }] },
    { name: "日根野吉明", birth: 1587, death: 1656, mil: 70, pol: 74, intel: 68, skill: "府内藩", lore: "豊後府内藩主。寛永期の豊後府内を治めた譜代大名。", posts: [{ year: "1637", prov: "bungo", clan: "tokugawa" }] },
    { name: "有馬直純", birth: 1586, death: 1641, mil: 72, pol: 70, intel: 68, skill: "延岡藩", lore: "日向延岡藩主。島津の旧領だった延岡を幕府の城として治めた。", posts: [{ year: "1637", prov: "hyuga", clan: "tokugawa" }] },
    { name: "松平忠昌", birth: 1598, death: 1645, mil: 74, pol: 78, intel: 72, skill: "福井藩", lore: "結城秀康の子。越前福井藩主として寛永期の越前を治めた。", posts: [{ year: "1637", prov: "echizen", clan: "tokugawa" }] },

    { name: "後藤勝基", birth: 1520, death: 1563, mil: 76, pol: 64, intel: 68, skill: "美作の国人", lore: "美作の国人。天文・弘治年間に尼子・浦上の間で美作の城を守った。", posts: [{ year: "1546", prov: "mimasaka", clan: "amago" }] },
    { name: "戸川秀安", birth: 1537, death: 1597, mil: 78, pol: 74, intel: 76, skill: "備前戸川", lore: "宇喜多直家の重臣。備前の城を預かり、宇喜多家の軍事を支えた。", posts: [{ year: "1560", prov: "bizen", clan: "ukita" }] },
    { name: "蒲池鑑盛", birth: 1513, death: 1563, mil: 76, pol: 70, intel: 72, skill: "柳川城", lore: "筑後柳川の蒲池氏。大友氏に属して筑後南部を守った。", posts: [{ year: "1560", prov: "chikugo", clan: "otomo" }] },
    { name: "正木頼忠", birth: 1551, death: 1603, mil: 74, pol: 68, intel: 70, skill: "上総大多喜", lore: "里見家臣・正木氏。上総大多喜を拠点に、天正期の房総で北条との境を守った。", posts: [{ year: "1582", prov: "kazusa", clan: "satomi" }] },
    { name: "九戸政実", birth: 1536, death: 1591, mil: 84, pol: 66, intel: 74, skill: "九戸の乱", lore: "南部家の有力一門。陸奥北部の九戸城を預けられ、のち南部信直に叛いて滅んだ。", posts: [{ year: "1590", prov: "mutsu", clan: "nanbu" }] },
    { name: "石川貞清", birth: 1540, death: 1620, mil: 76, pol: 70, intel: 72, skill: "犬山城", lore: "尾張犬山城主。関ヶ原では西軍に属し、犬山から岐阜へ向かった。", posts: [{ year: "1600", prov: "owari", clan: "ishida" }] },
    { name: "九鬼嘉隆", birth: 1542, death: 1600, mil: 86, pol: 68, intel: 78, skill: "志摩水軍", lore: "志摩鳥羽の水軍大将。関ヶ原では西軍に属し、敗報を聞いて鳥羽で自刃した。", posts: [{ year: "1600", prov: "shima", clan: "ishida" }] },
    { name: "織田信包", birth: 1543, death: 1614, mil: 70, pol: 76, intel: 72, skill: "伊勢安濃津", lore: "信長の弟。伊勢安濃津を領し、関ヶ原のとき伊勢の豊臣系大名として西国寄りに立った。", posts: [{ year: "1600", prov: "ise", clan: "ishida" }] },
    { name: "南条元忠", birth: 1570, death: 1600, mil: 74, pol: 62, intel: 68, skill: "伯耆羽衣石", lore: "南条元続の子。伯耆羽衣石城を継ぎ、関ヶ原では西軍に属して滅んだ。", posts: [{ year: "1600", prov: "hoki", clan: "mori" }] },
    { name: "安藤信勇", birth: 1819, death: 1871, mil: 68, pol: 74, intel: 70, skill: "磐城平藩", lore: "陸奥磐城平藩主。戊辰戦争では奥羽列藩同盟に与し、平城を拠点に戦った。", posts: [{ year: "1866", prov: "iwaki", clan: "date" }, { year: "1868", prov: "iwaki", clan: "date" }] },
    { name: "真田幸民", birth: 1850, death: 1903, mil: 68, pol: 74, intel: 72, skill: "松代藩", lore: "信濃松代藩主。真田家の末代藩主で、幕末の北信濃を治めた。", posts: [{ year: "1866", prov: "north_shinano", clan: "tokugawa" }] },
    { name: "井伊直憲", birth: 1846, death: 1901, mil: 70, pol: 74, intel: 70, skill: "彦根藩", lore: "近江彦根藩主。井伊直弼の子。幕末の北近江を譜代の城として守った。", posts: [{ year: "1866", prov: "north_omi", clan: "tokugawa" }] },
    { name: "本多康穣", birth: 1844, death: 1907, mil: 66, pol: 72, intel: 68, skill: "膳所藩", lore: "近江膳所藩主。琵琶湖の南、膳所城を預かる譜代大名。", posts: [{ year: "1866", prov: "south_omi", clan: "tokugawa" }] },
    { name: "植村家壺", birth: 1837, death: 1891, mil: 68, pol: 70, intel: 66, skill: "高取藩", lore: "大和高取藩主。幕末の大和山地を治めた譜代大名。", posts: [{ year: "1866", prov: "yamato", clan: "tokugawa" }] },
    { name: "北条氏恭", birth: 1841, death: 1907, mil: 66, pol: 72, intel: 68, skill: "狭山藩", lore: "河内狭山藩主。後北条氏の子孫で、幕末の河内を治めた。", posts: [{ year: "1866", prov: "kawachi", clan: "tokugawa" }] },
    { name: "青山忠敏", birth: 1837, death: 1902, mil: 68, pol: 74, intel: 70, skill: "篠山藩", lore: "丹波篠山藩主。京と西国の間、丹波の城を預かる譜代大名。", posts: [{ year: "1866", prov: "tamba", clan: "tokugawa" }] },
    { name: "酒井忠義", birth: 1813, death: 1873, mil: 70, pol: 78, intel: 74, skill: "小浜藩", lore: "若狭小浜藩の前藩主。幕末の若狭で実権を持ち、藩論を主導した。", posts: [{ year: "1866", prov: "wakasa", clan: "tokugawa" }, { year: "1868", prov: "wakasa", clan: "fukui_matsudaira" }] },
    { name: "遠山友禄", birth: 1832, death: 1905, mil: 70, pol: 72, intel: 74, skill: "苗木藩", lore: "美濃苗木藩主。幕末の美濃で勤王に転じ、東濃の小藩を率いた。", posts: [{ year: "1866", prov: "mino", clan: "tokugawa" }, { year: "1868", prov: "mino", clan: "owari" }] },
    { name: "成瀬正肥", birth: 1836, death: 1903, mil: 72, pol: 76, intel: 74, skill: "犬山城代", lore: "尾張藩の城代家老。犬山城を預かり、戊辰戦争では尾張の軍を率いて東征に従った。", posts: [{ year: "1866", prov: "owari", clan: "tokugawa" }, { year: "1868", prov: "owari", clan: "owari" }] },
    { name: "大久保一翁", birth: 1817, death: 1888, mil: 66, pol: 90, intel: 88, skill: "駿府の老中", lore: "幕臣。慶喜の側近として恭順を進め、のち静岡藩の中枢として駿河の仕置を担った。", posts: [{ year: "1866", prov: "suruga", clan: "tokugawa" }, { year: "1868", prov: "suruga", clan: "tokugawa" }] },
    { name: "井上正直", birth: 1837, death: 1904, mil: 70, pol: 74, intel: 72, skill: "浜松藩", lore: "遠江浜松藩主。幕末の遠江を治め、戊辰では新政府側に立った。", posts: [{ year: "1866", prov: "totomi", clan: "tokugawa" }, { year: "1868", prov: "totomi", clan: "tokugawa" }] },
    { name: "立花鑑寛", birth: 1833, death: 1903, mil: 72, pol: 74, intel: 70, skill: "柳川藩", lore: "筑後柳川藩主。幕末の筑後を治め、戊辰戦争では新政府に与した。", posts: [{ year: "1868", prov: "chikugo", clan: "nabeshima" }] },
    { name: "細川行真", birth: 1839, death: 1905, mil: 70, pol: 72, intel: 68, skill: "宇土藩", lore: "肥後宇土藩主。細川宗家に従い、戊辰戦争では熊本の支藩として兵を出した。", posts: [{ year: "1868", prov: "higo", clan: "kumamoto_hosokawa" }] },
    { name: "島津久宝", birth: 1826, death: 1894, mil: 72, pol: 74, intel: 70, skill: "加治木島津", lore: "大隅加治木の島津一門。薩摩藩の分家として大隅の城地を預かった。", posts: [{ year: "1866", prov: "osumi", clan: "shimazu" }, { year: "1868", prov: "osumi", clan: "shimazu" }] },
    { name: "毛利元純", birth: 1818, death: 1883, mil: 74, pol: 76, intel: 72, skill: "清末藩", lore: "長門清末藩主。毛利支藩として幕末の長門西部を守り、四境戦争に連なった。", posts: [{ year: "1866", prov: "nagato", clan: "mori" }, { year: "1868", prov: "nagato", clan: "mori" }] },
    { name: "稲田邦植", birth: 1851, death: 1905, mil: 68, pol: 70, intel: 72, skill: "淡路稲田", lore: "徳島藩家老稲田氏。淡路を預かり、維新前後に洲本を拠点とした。", posts: [{ year: "1868", prov: "awaji", clan: "meiji" }] },
    { name: "木下利恭", birth: 1843, death: 1907, mil: 66, pol: 74, intel: 70, skill: "足守藩", lore: "備中足守藩主。岡山藩の支藩として幕末の備中を治めた。", posts: [{ year: "1868", prov: "bicchu", clan: "okayama" }] },
    { name: "荒尾成裕", birth: 1820, death: 1885, mil: 70, pol: 76, intel: 72, skill: "米子城代", lore: "鳥取藩家老。伯耆米子城代として幕末の山陰西部を預かった。", posts: [{ year: "1868", prov: "hoki", clan: "tottori" }] },

    // 元禄15年秋。討ち入り前夜の藩主・役職。本拠の当主は既存武将のまま、支城だけを置く。
    { name: "松平信庸", birth: 1650, death: 1725, mil: 70, pol: 88, intel: 84, skill: "京都所司代", lore: "丹波亀山藩主。元禄十五年四月から京都所司代を務め、朝廷と畿内の幕府領を監督した。", posts: [{ year: "1702", prov: "yamashiro", clan: "tokugawa" }] },
    { name: "土岐頼殷", birth: 1648, death: 1725, mil: 74, pol: 86, intel: 82, skill: "大坂城代", lore: "沼田藩主。元禄四年から正徳二年まで大坂城代を務め、西国の幕府軍を預かった。", posts: [{ year: "1702", prov: "settsu", clan: "tokugawa" }] },
    { name: "青山幸豊", birth: 1666, death: 1744, mil: 68, pol: 80, intel: 76, skill: "駿府城代", lore: "旗本の大身。駿府城代として駿河の幕府城を預かり、東海道の中継を守った。", posts: [{ year: "1702", prov: "suruga", clan: "tokugawa" }] },
    { name: "大久保忠朝", birth: 1632, death: 1712, mil: 76, pol: 82, intel: 78, skill: "小田原藩", lore: "大久保忠隣の孫。貞享三年から小田原藩主として相模を治め、江戸の西を固めた。", posts: [{ year: "1702", prov: "sagami", clan: "tokugawa" }] },
    { name: "酒井忠挙", birth: 1648, death: 1720, mil: 74, pol: 84, intel: 80, skill: "前橋藩", lore: "厩橋酒井家。前橋十五万石を領し、上野の中心として中山道の抑えとなった。", posts: [{ year: "1702", prov: "kozuke", clan: "tokugawa" }] },
    { name: "稲垣重富", birth: 1652, death: 1710, mil: 70, pol: 82, intel: 78, skill: "烏山藩", lore: "綱吉の側近で若年寄。元禄十五年九月、三河刈谷から下野烏山へ入り、那須の城を預かった。", posts: [{ year: "1702", prov: "shimotsuke", clan: "tokugawa" }] },
    { name: "稲葉正往", birth: 1640, death: 1716, mil: 72, pol: 84, intel: 80, skill: "佐倉藩", lore: "元禄十四年、越後高田から下総佐倉へ移り、江戸の東を譜代の城で守った。", posts: [{ year: "1702", prov: "shimousa", clan: "tokugawa" }] },
    { name: "黒田直邦", birth: 1667, death: 1735, mil: 70, pol: 78, intel: 74, skill: "久留里藩", lore: "譜代の黒田氏。上総久留里を領し、房総の東岸を幕府側の城として守った。", posts: [{ year: "1702", prov: "kazusa", clan: "tokugawa" }] },
    { name: "戸田忠真", birth: 1651, death: 1729, mil: 72, pol: 86, intel: 82, skill: "高田藩", lore: "佐倉藩主戸田忠昌の子。元禄十四年に越後高田へ移り、のちに老中となる。", posts: [{ year: "1702", prov: "echigo", clan: "tokugawa" }] },
    { name: "酒井忠囿", birth: 1654, death: 1706, mil: 72, pol: 84, intel: 80, skill: "小浜藩", lore: "若狭小浜藩主。酒井忠勝の後を受け、北陸道の西口を十万石余で守った。", posts: [{ year: "1702", prov: "wakasa", clan: "tokugawa" }] },
    { name: "戸田氏定", birth: 1671, death: 1730, mil: 72, pol: 80, intel: 74, skill: "大垣藩", lore: "美濃大垣藩主。十万石で西美濃を治め、中山道と東海道の接点を押さえた。", posts: [{ year: "1702", prov: "mino", clan: "tokugawa" }] },
    { name: "本庄資俊", birth: 1649, death: 1725, mil: 72, pol: 80, intel: 76, skill: "浜松藩", lore: "常陸笠間から、元禄十五年九月に遠江浜松七万石へ入った譜代大名。", posts: [{ year: "1702", prov: "totomi", clan: "tokugawa" }] },
    { name: "藤堂高睦", birth: 1667, death: 1703, mil: 74, pol: 82, intel: 78, skill: "津藩", lore: "伊勢津藩主。三十二万石余を領し、伊勢の中心と伊賀口を藤堂家の城で守った。", posts: [{ year: "1702", prov: "ise", clan: "tokugawa" }] },
    { name: "本多康慶", birth: 1645, death: 1711, mil: 70, pol: 78, intel: 74, skill: "膳所藩", lore: "近江膳所藩主。琵琶湖の南岸を譜代の城として預かり、京への東口を固めた。", posts: [{ year: "1702", prov: "south_omi", clan: "tokugawa" }] },
    { name: "本多忠常", birth: 1661, death: 1726, mil: 74, pol: 80, intel: 76, skill: "郡山藩", lore: "大和郡山藩主。十五万石で奈良盆地を治め、京の南を譜代の城で押さえた。", posts: [{ year: "1702", prov: "yamato", clan: "tokugawa" }] },
    { name: "岡部長泰", birth: 1665, death: 1724, mil: 70, pol: 78, intel: 74, skill: "岸和田藩", lore: "和泉岸和田藩主。大坂の南、和泉の城を預かる譜代大名。", posts: [{ year: "1702", prov: "izumi", clan: "tokugawa" }] },
    { name: "青山忠重", birth: 1654, death: 1722, mil: 72, pol: 80, intel: 76, skill: "亀山藩", lore: "遠江浜松から、元禄十五年九月に丹波亀山へ移った。京と西国の中間を守る。", posts: [{ year: "1702", prov: "tamba", clan: "tokugawa" }] },
    { name: "奥平昌成", birth: 1660, death: 1726, mil: 72, pol: 78, intel: 74, skill: "宮津藩", lore: "丹後宮津藩主。京極氏の後を受け、日本海側の丹後を治めた。", posts: [{ year: "1702", prov: "tango", clan: "tokugawa" }] },
    { name: "仙石政明", birth: 1668, death: 1706, mil: 72, pol: 76, intel: 74, skill: "出石藩", lore: "但馬出石藩主。仙石家として但馬の城を預かった。", posts: [{ year: "1702", prov: "tajima", clan: "tokugawa" }] },
    { name: "亀井茲親", birth: 1669, death: 1731, mil: 72, pol: 78, intel: 74, skill: "津和野藩", lore: "石見津和野藩主。山陰西部の城を預かり、石見の西を治めた。", posts: [{ year: "1702", prov: "iwami", clan: "tokugawa" }] },
    { name: "松平宣富", birth: 1673, death: 1726, mil: 72, pol: 80, intel: 76, skill: "津山藩", lore: "越前松平家。森氏改易の後、元禄十一年から美作津山十万石を治めた。", posts: [{ year: "1702", prov: "mimasaka", clan: "tokugawa" }] },
    { name: "安藤信友", birth: 1671, death: 1732, mil: 72, pol: 80, intel: 76, skill: "備中松山", lore: "備中松山藩主。のちに奏者番を務め、正徳元年に美濃加納へ移る直前まで備中を領した。", posts: [{ year: "1702", prov: "bicchu", clan: "tokugawa" }] },
    { name: "松平頼豊", birth: 1680, death: 1735, mil: 70, pol: 80, intel: 76, skill: "高松藩", lore: "水戸家連枝。元禄十三年から讃岐高松十二万石を継ぎ、四国の北岸を守った。", posts: [{ year: "1702", prov: "sanuki", clan: "tokugawa" }] },
    { name: "松平定直", birth: 1660, death: 1720, mil: 74, pol: 82, intel: 78, skill: "伊予松山", lore: "久松松平氏。伊予松山十五万石を領し、伊予の中心を治めた。", posts: [{ year: "1702", prov: "iyo", clan: "tokugawa" }] },
    { name: "小笠原忠雄", birth: 1658, death: 1725, mil: 74, pol: 80, intel: 76, skill: "小倉藩", lore: "豊前小倉藩主。十五万石で関門海峡の東岸を譜代の城として守った。", posts: [{ year: "1702", prov: "buzen", clan: "tokugawa" }] },
    { name: "中川久通", birth: 1663, death: 1706, mil: 72, pol: 78, intel: 74, skill: "岡藩", lore: "豊後岡藩主。七万石余で豊後南部を治め、府内・杵築より大きな城地を持った。", posts: [{ year: "1702", prov: "bungo", clan: "tokugawa" }] },
    { name: "江川英長", birth: 1648, death: 1715, mil: 66, pol: 82, intel: 78, skill: "韮山代官", lore: "世襲の韮山代官。伊豆の幕府領と沿岸を預かり、江戸湾の西口を監視した。", posts: [{ year: "1702", prov: "izu", clan: "tokugawa" }] },
    { name: "前田正甫", birth: 1671, death: 1724, mil: 72, pol: 78, intel: 74, skill: "富山藩", lore: "加賀前田家の支藩。越中富山十万石を領し、売薬の藩として越中を治めた。", posts: [{ year: "1702", prov: "etchu", clan: "maeda" }] },
    { name: "島津惟久", birth: 1671, death: 1715, mil: 72, pol: 76, intel: 74, skill: "佐土原藩", lore: "日向佐土原藩主。島津の支藩として日向の城を預かった。", posts: [{ year: "1702", prov: "hyuga", clan: "shimazu" }] },
    { name: "毛利元次", birth: 1668, death: 1719, mil: 72, pol: 78, intel: 74, skill: "徳山藩", lore: "毛利家の支藩。周防徳山を領し、萩の本家に対して周防の東を守った。", posts: [{ year: "1702", prov: "suo", clan: "mori" }] }
  ,
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
,
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
];

  // 既存武将を、領国が無いときだけ史実の国へ迎える
  const reuse = [
    { year: "1570", prov: "tsugaru", id: "off_tsugaru_tamenobu", clan: "nanbu" },
    { year: "1582", prov: "tsugaru", id: "off_tsugaru_tamenobu", clan: "nanbu" },
    { year: "1582", prov: "north_omi", id: "off_hori_hidemasa" },
    { year: "1584", prov: "tsugaru", id: "off_tsugaru_tamenobu", clan: "nanbu" },
    { year: "1584", prov: "mutsu", id: "off_kita_nobuchika", clan: "nanbu" },
    { year: "1584", prov: "kozuke", id: "off_hojo_ujikuni", clan: "hojo" },
    { year: "1584", prov: "shimousa", id: "off_chiba_kunitane", clan: "hojo" },
    { year: "1584", prov: "kazusa", id: "off_hojo_ujinori", clan: "hojo" },
    { year: "1584", prov: "noto", id: "off_cho_tsuratatsu", clan: "toyotomi" },
    { year: "1584", prov: "tango", id: "off_hosokawa_fujitaka", clan: "toyotomi" },
    { year: "1584", prov: "tamba", id: "off_maeda_geni", clan: "toyotomi" },
    { year: "1584", prov: "tajima", id: "off_yamana_toyokuni", clan: "toyotomi" },
    { year: "1584", prov: "kawachi", id: "off_hachisuka_iemasa", clan: "toyotomi" },
    { year: "1584", prov: "izumi", id: "off_konishi_yukinaga", clan: "toyotomi" },
    { year: "1584", prov: "wakasa", id: "off_asano_nagamasa", clan: "toyotomi" },
    { year: "1584", prov: "hida", id: "off_kanamori_arishige", clan: "toyotomi" },
    { year: "1584", prov: "iyo", id: "off_succ_kono_1555_74", clan: "chosokabe" },
    { year: "1584", prov: "izumo", id: "off_kikkawa_hiroie", clan: "mori" },
    { year: "1584", prov: "buzen", id: "off_takahashi_shoun", clan: "otomo" },
    { year: "1584", prov: "chikuzen", id: "off_tachibana_dosetsu", clan: "ryuzoji" },
    { year: "1584", prov: "higo", id: "off_succ_sagara_1570_136", clan: "shimazu" },
    { year: "1587", prov: "tsugaru", id: "off_tsugaru_tamenobu", clan: "nanbu" },
    { year: "1587", prov: "mutsu", id: "off_kita_nobuchika", clan: "nanbu" },
    { year: "1587", prov: "kozuke", id: "off_hojo_ujikuni", clan: "hojo" },
    { year: "1587", prov: "shimousa", id: "off_chiba_kunitane", clan: "hojo" },
    { year: "1587", prov: "kazusa", id: "off_hojo_ujinori", clan: "hojo" },
    { year: "1587", prov: "etchu", id: "off_dm_maeda_1600", clan: "toyotomi" },
    { year: "1587", prov: "noto", id: "off_cho_tsuratatsu", clan: "toyotomi" },
    { year: "1587", prov: "echizen", id: "off_niwa_nagashige", clan: "toyotomi" },
    { year: "1587", prov: "tango", id: "off_hosokawa_tadaoki", clan: "toyotomi" },
    { year: "1587", prov: "tamba", id: "off_maeda_geni", clan: "toyotomi" },
    { year: "1587", prov: "kawachi", id: "off_hachisuka_iemasa", clan: "toyotomi" },
    { year: "1587", prov: "izumi", id: "off_konishi_yukinaga", clan: "toyotomi" },
    { year: "1587", prov: "sanuki", id: "off_sengoku_hidehisa", clan: "toyotomi" },
    { year: "1587", prov: "iyo", id: "off_kato_yoshiaki", clan: "toyotomi" },
    { year: "1587", prov: "buzen", id: "off_kuroda_kanbei", clan: "toyotomi" },
    { year: "1587", prov: "chikuzen", id: "off_kobayakawa_takakage", clan: "toyotomi" },
    { year: "1587", prov: "chikugo", id: "off_tachibana_muneshige", clan: "toyotomi" },
    { year: "1587", prov: "higo", id: "off_kato_kiyomasa", clan: "toyotomi" },
    { year: "1590", prov: "mutsu", id: "off_kita_nobuchika", clan: "nanbu" },
    { year: "1590", prov: "chikuzen", id: "off_tachibana_muneshige", clan: "toyotomi" },
    { year: "1590", prov: "hizen", id: "off_nabeshima_naoshige", clan: "toyotomi" },
    { year: "1592", prov: "mutsu", id: "off_kita_nobuchika", clan: "nanbu" },
    { year: "1592", prov: "iwaki", id: "off_soma_yoshitane", clan: "date" },
    { year: "1592", prov: "kazusa", id: "off_honda_tadakatsu", clan: "tokugawa" },
    { year: "1592", prov: "awa_boshu", id: "off_succ2_satomi_1573", clan: "tokugawa" },
    { year: "1592", prov: "suruga", id: "off_nakamura_kazuuji", clan: "toyotomi" },
    { year: "1592", prov: "kai", id: "off_asano_nagamasa", clan: "toyotomi" },
    { year: "1592", prov: "south_shinano", id: "off_ishikawa_kazumasa", clan: "toyotomi" },
    { year: "1592", prov: "etchu", id: "off_dm_maeda_1600", clan: "toyotomi" },
    { year: "1592", prov: "noto", id: "off_cho_tsuratatsu", clan: "toyotomi" },
    { year: "1592", prov: "totomi", id: "off_yamauchi_kazutoyo", clan: "toyotomi" },
    { year: "1592", prov: "mikawa", id: "off_tanaka_yoshimasa", clan: "toyotomi" },
    { year: "1592", prov: "ise", id: "off_todo_takatora", clan: "toyotomi" },
    { year: "1592", prov: "south_omi", id: "off_kyogoku_takatsugu", clan: "toyotomi" },
    { year: "1592", prov: "yamato", id: "off_mashita_nagamori", clan: "toyotomi" },
    { year: "1592", prov: "tamba", id: "off_maeda_geni", clan: "toyotomi" },
    { year: "1592", prov: "tango", id: "off_hosokawa_tadaoki", clan: "toyotomi" },
    { year: "1592", prov: "tajima", id: "off_koide_yoshimasa", clan: "toyotomi" },
    { year: "1592", prov: "harima", id: "off_ikeda_terumasa", clan: "toyotomi" },
    { year: "1592", prov: "sanuki", id: "off_sengoku_hidehisa", clan: "toyotomi" },
    { year: "1592", prov: "awa_shikoku", id: "off_hachisuka_iemasa", clan: "toyotomi" },
    { year: "1592", prov: "iyo", id: "off_kato_yoshiaki", clan: "toyotomi" },
    { year: "1592", prov: "bungo", id: "off_dm_otomo_1600", clan: "toyotomi" },
    { year: "1592", prov: "hyuga", id: "off_succ_ito_1550_45", clan: "toyotomi" },
    { year: "1600", prov: "mutsu", id: "off_kita_nobuchika", clan: "nanbu" },
    { year: "1600", prov: "south_shinano", id: "off_hiraiwa_chikayoshi" },
    { year: "1600", prov: "yamashiro", id: "off_maeda_geni", clan: "ishida" },
    { year: "1600", prov: "chikuzen", id: "off_kobayakawa_hideaki", clan: "ishida" },
    { year: "1600", prov: "chikugo", id: "off_tachibana_muneshige", clan: "ishida" },
    { year: "1702", prov: "kai", id: "off_tokugawa_ienobu" },
    { year: "1702", prov: "south_shinano", id: "off_suwa_tadatotora", clan: "tokugawa" },
    { year: "1702", prov: "iwaki", id: "off_soma_masatane", clan: "date" },
    { year: "1702", prov: "kawachi", id: "off_hojo_ujitomo", clan: "tokugawa" }
  ];

  window.JODAI_CLAN_BY_SCENARIO = {};
  let seq = 0;
  for (const r of roster) {
    if (existing.has(r.name)) continue;
    const alivePosts = r.posts.filter(p => {
      const y = Number(p.year);
      return y - r.birth >= 15 && y <= r.death;
    });
    if (!alivePosts.length) continue;
    seq += 1;
    const id = "off_jd_" + String(seq).padStart(3, "0");
    const first = alivePosts[0];
    window.OFFICERS_MASTER.push({
      id,
      name: r.name,
      clanId: first.clan,
      defaultProv: first.prov,
      military: r.mil,
      politic: r.pol,
      intel: r.intel,
      era: eraOf(Number(first.year)),
      skill: r.skill,
      lore: r.lore,
      birthYear: r.birth,
      deathYear: r.death,
      isDaimyo: false
    });
    existing.add(r.name);
    for (const p of alivePosts) {
      const key = String(p.year);
      if (!window.SCENARIO_HISTORICAL_GOVERNORS[key]) window.SCENARIO_HISTORICAL_GOVERNORS[key] = {};
      window.SCENARIO_HISTORICAL_GOVERNORS[key][p.prov] = id;
      if (p.clan !== first.clan) {
        if (!window.JODAI_CLAN_BY_SCENARIO[key]) window.JODAI_CLAN_BY_SCENARIO[key] = {};
        window.JODAI_CLAN_BY_SCENARIO[key][id] = p.clan;
      }
    }
  }

  for (const row of reuse) {
    const key = String(row.year);
    if (!window.SCENARIO_HISTORICAL_GOVERNORS[key]) window.SCENARIO_HISTORICAL_GOVERNORS[key] = {};
    if (!window.OFFICERS_MASTER.some(o => o.id === row.id)) continue;
    window.SCENARIO_HISTORICAL_GOVERNORS[key][row.prov] = row.id;
    if (row.clan) {
      if (!window.JODAI_CLAN_BY_SCENARIO[key]) window.JODAI_CLAN_BY_SCENARIO[key] = {};
      window.JODAI_CLAN_BY_SCENARIO[key][row.id] = row.clan;
    }
  }
})();
