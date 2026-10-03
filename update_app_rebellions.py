import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Target section in getHistoricalEventsMaster
# From id: 'tobafushimi' to id: 'gunshi_join'
tobafushimi_marker = "id: 'tobafushimi',"
gunshi_marker = "id: 'gunshi_join',"

tobafushimi_idx = text.find(tobafushimi_marker)
gunshi_idx = text.find(gunshi_marker)

if tobafushimi_idx == -1 or gunshi_idx == -1:
    print("Error: Could not locate markers in app.js")
    sys.exit(1)

# Find the start of the object containing tobafushimi
obj_start = text.rfind('{', 0, tobafushimi_idx)
# Find the start of the object containing gunshi
obj_end = text.rfind('{', 0, gunshi_idx)

replacement_events = """      {
        id: 'tobafushimi',
        scenarioId: '1868',
        title: '❖ 鳥羽・伏見の戦い ＆ 錦の御旗 ❖',
        subTitle: '幕末維新の夜明け・近代兵器と武士魂の激突',
        check: (game) => game.year >= 1868 && (game.playerClanId === 'meiji' || game.playerClanId === 'tokugawa' || game.playerClanId === 'shimazu' || game.playerClanId === 'mori'),
        narrative: (game) => (game.playerClanId === 'meiji' || game.playerClanId === 'shimazu' || game.playerClanId === 'mori')
          ? '鳥羽街道・伏見街道で始まった新政府軍五千と旧幕府軍一万五千の激突。薩摩の砲兵と長州の銃隊が奮戦する中、朝廷より授かりし「錦の御旗」が前線に翻る！朝敵の汚名を恐れる旧幕府軍に対し、総攻撃を仕掛けるか、あるいは降伏を促すか！'
          : '大坂城から進軍した旧幕府軍。兵力では三倍勝るものの、新政府軍の最新式アームストロング砲とスナイドル銃に阻まれる。そこへ突如翻る「錦の御旗」！恭順の道を選び海路江戸へ退くか、大坂城に籠もり徹底抗戦を挑むか！',
        choices: (game) => (game.playerClanId === 'meiji' || game.playerClanId === 'shimazu' || game.playerClanId === 'mori') ? [
          {
            text: '【史実ルート】錦の御旗を高く掲げ、朝廷の官軍として総攻撃！',
            desc: '旧幕府軍は戦意喪失し大坂城へ退却！新政府軍兵力+5,000、近畿一円を完全制圧！',
            isHistorical: true,
            action: (g) => {
              const p = g.provinces.find(pr => pr.ownerId === g.playerClanId) || g.provinces[0];
              p.troops += 5000;
              g.provinces.filter(pr => pr.ownerId === 'tokugawa').forEach(pr => pr.troops = Math.round(pr.troops * 0.4));
              g.log('【錦の御旗の奇跡】官軍の錦旗に敵軍は総崩れ！鳥羽・伏見の大勝利を収めました！', 'important');
              return '菊の御紋の錦旗が翻ると、敵兵は戦意を失い潰走！維新への決定打となりました！';
            }
          },
          {
            text: '【歴史改変IF】徳川宗家に対し寛大な講和を提示し、無血で公議政体を発足！',
            desc: '内乱を即時終結させ、国力を温存。軍資金+2,000、全領地治安最大化！',
            isHistorical: false,
            action: (g) => {
              g.gold += 2000;
              g.provinces.forEach(pr => pr.order = 100);
              g.log('【大政奉還・無血融和】内戦の流血を最小限に防ぎ、諸藩合議の新国家を樹立しました！', 'important');
              return '徳川家と速やかに和睦を結び、国力を損なうことなく近代国家の建設へ踏み出しました！';
            }
          }
        ] : [
          {
            text: '【歴史改変IF】大坂城に籠もり諸藩を糾合！近代砲兵で徹底持久戦！',
            desc: '大坂城の巨城を盾に反撃！幕府海軍の軍艦を活用し、旧幕府軍兵力+6,000！',
            isHistorical: false,
            action: (g) => {
              const p = g.provinces.find(pr => pr.ownerId === 'tokugawa') || g.provinces[0];
              p.troops += 6000;
              g.log('【大坂城死守の英断】幕府海軍と近代砲兵を組織し、新政府軍の進撃を阻止しました！', 'important');
              return '東洋一の名城・大坂城に拠り、榎本海軍の艦砲射撃とともに反撃を開始しました！';
            }
          },
          {
            text: '【史実ルート】朝敵となるを恐れ、海路江戸へ退却し恭順謹慎の道を選ぶ。',
            desc: '無用な戦火を避け、江戸を戦火から救う。軍資金+1,500獲得。',
            isHistorical: true,
            action: (g) => {
              g.gold += 1500;
              g.log('【恭順の道】無駄な流血を避けるため海路江戸へ退却。再起を図ります。');
              return '朝廷への恭順を示しつつ江戸へ後退。万民を戦火から守る英断を下しました。';
            }
          }
        ]
      },
      {
        id: 'shimabara_rebellion',
        scenarioId: '1637',
        title: '❖ 島原の乱・原城籠城と幕府総動員 ❖',
        subTitle: '十字架の御旗を掲げる三万七千と西国諸大名十二万の激突',
        check: (game) => game.year >= 1637 && (game.playerClanId === 'tokugawa' || game.playerClanId === 'amakusa' || game.playerClanId === 'hosokawa' || game.playerClanId === 'tachibana' || game.playerClanId === 'kuroda' || game.playerClanId === 'nabeshima'),
        narrative: (game) => game.playerClanId === 'amakusa'
          ? '苛酷を極める年貢取り立てとキリシタン弾圧に対し、島原・天草の農民・浪人三万七千が原城に蜂起！16歳の天草四郎時貞を中心に十字架の御旗のもと固く結束した。幕府軍十二万が城を重囲する中、信仰と有馬・小西旧臣の軍法で鉄壁の籠城戦を挑むか、あるいは闇夜に乗じて出撃し長崎を占拠して南蛮船と合流するか！'
          : '肥前島原・天草において天草四郎率いるキリシタン・浪人衆三万七千が原城に立て籠もり、幕府上使・板倉重昌が討死する大騒乱となった。幕府は知恵伊豆・松平信綱を総大将に、九州・西国の諸大名を総動員！兵糧攻めの末に大軍で原城を一気に総攻撃するか、あるいは苛政の元凶・松倉勝家を処罰し減税と和睦で乱の早期収拾を図るか！',
        choices: (game) => game.playerClanId === 'amakusa' ? [
          {
            text: '【歴史改変IF・反乱大成功】十字架の御旗のもと幕府十二万を完全撃退！九州西海に自由独立国を樹立！',
            desc: '原城の要害と不退転の団結で幕府軍を返り討ち！肥前を完全掌握し肥後へ進撃！自軍兵力+7,000、金+2,500！',
            isHistorical: false,
            action: (g) => {
              g.gold += 2500;
              const hizen = g.provinces.find(pr => pr.id === 'hizen');
              if (hizen) {
                hizen.troops += 7000;
                hizen.defense = 100;
                hizen.order = 100;
              }
              const higo = g.provinces.find(pr => pr.id === 'higo');
              if (higo) {
                higo.ownerId = 'amakusa';
                higo.troops = 4000;
              }
              g.provinces.filter(pr => pr.ownerId === 'tokugawa').forEach(pr => {
                pr.troops = Math.round(pr.troops * 0.7);
              });
              g.log('【島原の乱 大勝利】天草四郎の奇跡の軍配により幕府軍十二万を完膚なきまでに撃退！九州西海にキリシタン独立領国を樹立しました！', 'important');
              return '十字架の御旗翻る原城にて幕府軍を撃滅！民衆の自由と信仰を守り抜き、西海に新たな時代を切り拓きました！';
            }
          },
          {
            text: '【史実ルート】十字架の御旗のもと、原城に死守籠城！奇跡の信仰で幕府軍を幾度も撃退！',
            desc: '驚異の団結力で籠城防衛！自軍兵力+5,000、防御度+40！敵軍に痛烈な打撃を与える！',
            isHistorical: true,
            action: (g) => {
              const hizen = g.provinces.find(pr => pr.id === 'hizen');
              if (hizen) {
                hizen.troops += 5000;
                hizen.defense = Math.min(100, (hizen.defense || 50) + 40);
              }
              g.provinces.filter(pr => pr.ownerId === 'tokugawa').forEach(pr => {
                pr.troops = Math.round(pr.troops * 0.85);
              });
              g.log('【原城死守の奇跡】天草四郎の統率のもと、一揆軍は幕府軍の猛攻を幾度も撃退しました！', 'important');
              return '十字架の御旗翻る原城にて、三万七千の信徒と武士団が鉄壁の結束を発揮！幕府軍に甚大な損害を与えました！';
            }
          }
        ] : [
          {
            text: '【史実ルート】松平信綱の深謀！兵糧攻めの末に西国十二万の大軍で原城一斉総攻撃！',
            desc: '島原の乱を完全鎮圧！天下の泰平を盤石とし、幕府の威信が劇的向上！自軍兵力+5,000、金+1,500獲得！肥前を天領直轄化！',
            isHistorical: true,
            action: (g) => {
              g.gold += 1500;
              const hizen = g.provinces.find(pr => pr.id === 'hizen');
              if (hizen) {
                hizen.ownerId = g.playerClanId;
                hizen.troops = Math.max(hizen.troops, 5000);
                hizen.order = 95;
              }
              g.provinces.filter(pr => pr.ownerId === g.playerClanId).forEach(pr => {
                pr.troops += 1000;
              });
              g.log('【島原の乱 平定】松平信綱・九州諸大名の総攻撃により原城陥落！乱は完全鎮圧されました！', 'important');
              return '西国諸大名の総力をもって原城を攻略！反乱を完全に鎮圧し、天下の泰平と幕府の威信を揺るぎなきものとしました！';
            }
          },
          {
            text: '【歴史改変IF】苛政の元凶・松倉勝家を改易処断！寛大な減税と和睦で乱を収拾！',
            desc: '無益な殺傷を避け領民の心を掴む。九州全領国の治安+25、兵糧+3,000獲得！キリシタン武士団が帰順！',
            isHistorical: false,
            action: (g) => {
              g.rice += 3000;
              const hizen = g.provinces.find(pr => pr.id === 'hizen');
              if (hizen) {
                hizen.ownerId = g.playerClanId;
                hizen.order = 90;
              }
              g.provinces.forEach(pr => {
                if (pr.region === '九州') pr.order = Math.min(100, (pr.order || 80) + 25);
              });
              g.log('【仁政による和睦】松倉勝家を厳罰に処し減税を断行！一揆勢の帰順を得て平和裏に事態を収拾しました！', 'important');
              return '悪政を糾弾して民心を取り戻し、戦火を未然に鎮火。名君の器量を天下に示しました！';
            }
          }
        ]
      },
      {
        id: 'kunohe_rebellion',
        scenarioId: '*',
        title: '❖ 九戸政実の乱・奥州覇王の蜂起 ❖',
        subTitle: '秀吉の奥州仕置に抗う東北屈指の猛将・陸奥九戸城の死闘',
        check: (game) => (game.year === 1590 || game.year === 1591 || game.year === 1592) && (game.playerClanId === 'nanbu' || game.playerClanId === 'kunohe' || game.playerClanId === 'toyotomi' || game.playerClanId === 'date'),
        narrative: (game) => (game.playerClanId === 'nanbu' || game.playerClanId === 'kunohe')
          ? '豊臣秀吉の小田原征伐・奥州仕置に対し、南部一族最強の猛将・九戸政実（くのへまさざね）と弟・実親が五千の精鋭とともに九戸城に拠って反旗を翻した！秀吉は蒲生氏郷・浅野長政・井伊直政・前田利家ら十万の仕置大軍を派遣。峻険なる九戸城の要害と精強な弓鉄砲で仕置軍十万を迎え撃ち「奥州の独立」を勝ち取るか、あるいは豊臣の天下秩序に従い御家安泰を図るか！'
          : '奥州仕置の検地令に反発し、陸奥九戸城にて猛将・九戸政実が精兵五千とともに蜂起！蒲生氏郷・浅野長政ら十万の仕置軍をもって徹底包囲し力攻めで落城させるか、あるいは政実の武勇を惜しんで破格の条件で調略・豊臣直属大名として取り立てるか！',
        choices: (game) => (game.playerClanId === 'nanbu' || game.playerClanId === 'kunohe') ? [
          {
            text: '【歴史改変IF・九戸政実の乱大成功！】九戸城の鉄壁要害で仕置軍十万を完全撃破！奥州独立の覇王へ！',
            desc: '蒲生・浅野軍を馬淵川の合戦で撃退！陸奥・陸中を強固に直轄化し、自軍兵力+7,000、金+2,000獲得！九戸政実・実親兄弟が大奮戦！',
            isHistorical: false,
            action: (g) => {
              g.gold += 2000;
              const mutsu = g.provinces.find(pr => pr.id === 'mutsu');
              if (mutsu) {
                mutsu.ownerId = g.playerClanId;
                mutsu.troops += 4000;
                mutsu.defense = 100;
                mutsu.order = 100;
              }
              const rikuchu = g.provinces.find(pr => pr.id === 'rikuchu');
              if (rikuchu) {
                rikuchu.ownerId = g.playerClanId;
                rikuchu.troops += 3000;
                rikuchu.defense = 90;
              }
              g.provinces.filter(pr => pr.ownerId === 'toyotomi').forEach(pr => {
                pr.troops = Math.round(pr.troops * 0.75);
              });
              g.log('【九戸政実の乱 大勝利】豊臣仕置軍十万を九戸城にて撃退！秀吉の奥州支配を打ち破り、奥羽独立の覇王として天下に名声を轟かせました！', 'important');
              return '峻険なる九戸城に拠る九戸勢の神速の迎撃！蒲生・浅野の大軍を総崩れに追い込み、みちのくに不抜の独立領国を築き上げました！';
            }
          },
          {
            text: '【史実ルート】豊臣の圧倒的威勢を受け入れ、奥州仕置を完遂して領国安堵を確保。',
            desc: '無益な抗戦を避け、天下統一の秩序に帰順。全領国の治安+20、金+800獲得。',
            isHistorical: true,
            action: (g) => {
              g.gold += 800;
              g.provinces.filter(pr => pr.ownerId === g.playerClanId).forEach(pr => pr.order = Math.min(100, (pr.order || 80) + 20));
              g.log('【奥州仕置受容】豊臣政権への帰順を明確にし、領内の安定と御家安堵を確保しました。');
              return '秀吉公の天下統一令に服し、戦乱を終息させて領民の安寧を優先させました。';
            }
          }
        ] : [
          {
            text: '【史実ルート】蒲生氏郷・浅野長政の十万大軍で九戸城を完全包囲！乱を鎮圧し天下統一を完遂！',
            desc: '圧倒的軍勢で九戸城を落城させ、天下統一を完成！金+1,500獲得、全領国治安+15！',
            isHistorical: true,
            action: (g) => {
              g.gold += 1500;
              g.provinces.forEach(pr => { if (pr.ownerId === g.playerClanId) pr.order = Math.min(100, (pr.order || 80) + 15); });
              g.log('【九戸の乱 鎮圧】奥州仕置軍が九戸城を制圧！豊臣秀吉公による天下統一がここに完成しました！', 'important');
              return '九戸勢の激しい抵抗を圧倒的兵力で制圧！日本全国六十六州の惣無事令が名実ともに達成されました！';
            }
          },
          {
            text: '【歴史改変IF】九戸政実の武勇を認め、奥州探題に抜擢して豊臣政権の東の要とする！',
            desc: '東北最強の精鋭部隊を傘下に編入！本拠地兵力+5,000、九戸一族が心服帰順！',
            isHistorical: false,
            action: (g) => {
              const myProvs = g.provinces.filter(pr => pr.ownerId === g.playerClanId);
              if (myProvs.length > 0) myProvs[0].troops += 5000;
              g.log('【九戸政実の帰順】秀吉公の豪胆な器量により、猛将・九戸政実が豊臣家の忠臣として加わりました！', 'important');
              return '猛勇鳴り響く九戸勢を味方に引き入れ、東北の守りを鉄壁のものとしました！';
            }
          }
        ]
      },
      {
        id: 'keian_yui_rebellion',
        scenarioId: '1651',
        title: '❖ 由比正雪の乱（慶安の変）・十万牢人の江戸城強襲 ❖',
        subTitle: '家光急逝・十万の浪人を束ねて武断政治を揺るがす軍学者の大陰謀',
        check: (game) => game.year >= 1651 && (game.playerClanId === 'yui' || game.playerClanId === 'tokugawa' || game.playerClanId === 'kishu' || game.playerClanId === 'owari' || game.playerClanId === 'aizu'),
        narrative: (game) => game.playerClanId === 'yui'
          ? '三代将軍徳川家光の薨去に乗じ、軍学者・由比正雪と宝蔵院流槍術の達人・丸橋忠弥が牢人救済のため江戸転覆の火蓋を切った！密告の危機を察知して計画を前倒し、丸橋忠弥の決死抜刀隊が江戸城大手門を夜襲！火薬庫を掌握して幕閣を無力化し、駿河から三万の牢人軍を進駐させて「牢人解放・張孔堂新政権」を樹立するか！'
          : '軍学者・由比正雪率いる牢人党が江戸城乗っ取りと火薬庫爆破を企んでいるとの急報！老中・松平信綱の電光石火の捕縛網で一味を一網打尽にするか、あるいは正雪の主張を容れて牢人の幕府登用と改易制限を断行し、天下融和を図るか！',
        choices: (game) => game.playerClanId === 'yui' ? [
          {
            text: '【歴史改変IF・由比正雪の乱大成功！】丸橋忠弥の江戸城大手門奇襲成功！老中を捕縛し江戸・幕府を完全掌握！',
            desc: '密告網を逆手に取り江戸城大手門を突破！火薬庫を制圧し幕閣を完全掌握！武蔵（江戸）・駿河・相模を直轄化し、十万牢人を糾合して自軍兵力+8,000、金+3,000！',
            isHistorical: false,
            action: (g) => {
              g.gold += 3000;
              const musashi = g.provinces.find(pr => pr.id === 'musashi');
              if (musashi) {
                musashi.ownerId = 'yui';
                musashi.troops = 6000;
                musashi.order = 95;
              }
              const suruga = g.provinces.find(pr => pr.id === 'suruga');
              if (suruga) {
                suruga.ownerId = 'yui';
                suruga.troops += 4000;
                suruga.order = 100;
              }
              const sagami = g.provinces.find(pr => pr.id === 'sagami');
              if (sagami) {
                sagami.ownerId = 'yui';
                sagami.troops = 3000;
              }
              g.provinces.filter(pr => pr.ownerId === 'tokugawa').forEach(pr => {
                pr.troops = Math.round(pr.troops * 0.7);
              });
              g.log('【由比正雪の乱 大勝利】丸橋忠弥の奇襲により江戸城を掌握！武断政治を打破し、十万牢人を救済する張孔堂新幕府が誕生しました！', 'important');
              return '江戸城に翻る正雪の軍旗！困窮にあえぐ十万の牢人が歓喜結集し、天下の政権を完全掌握しました！';
            }
          },
          {
            text: '【史実ルート】武断政治の弊害を天下に訴え、保科正之と直接談判して浪人救済の約束を取り付ける。',
            desc: '無益な殺傷を避け、文治政治への転換を促す。自軍治安+30、金+1,500獲得。',
            isHistorical: true,
            action: (g) => {
              g.gold += 1500;
              const suruga = g.provinces.find(pr => pr.id === 'suruga');
              if (suruga) suruga.order = 100;
              g.log('【義挙の訴え】由比正雪の建白が保科正之を動かし、末期養子の禁緩和と文治政治への転換を勝ち取りました！');
              return '正雪の命がけの提言により幕政が刷新！牢人救済の道が開かれました！';
            }
          }
        ] : [
          {
            text: '【史実ルート】知恵伊豆・松平信綱の電光石火の捕縛！慶安の変を未然に防ぎ幕府の天領支配を死守！',
            desc: '正雪一党を捕縛し駿河を天領直轄化！幕府の威信回復、金+1,500獲得！',
            isHistorical: true,
            action: (g) => {
              g.gold += 1500;
              const suruga = g.provinces.find(pr => pr.id === 'suruga');
              if (suruga) {
                suruga.ownerId = g.playerClanId;
                suruga.order = 90;
              }
              g.log('【慶安の変 平定】松平信綱の迅速な捜査により一味を捕縛！幕府の天領支配を強固に防衛しました！', 'important');
              return '幕閣の迅速な対応により騒乱を未然に鎮圧。天下の静謐を維持しました！';
            }
          },
          {
            text: '【歴史改変IF】由比正雪・丸橋忠弥を幕臣に登用！牢人十万を幕府直属軍に再編！',
            desc: '牢人問題を抜本解決！軍学者正雪の指南により全軍の知略向上、兵力+7,000！',
            isHistorical: false,
            action: (g) => {
              const myProvs = g.provinces.filter(pr => pr.ownerId === g.playerClanId);
              if (myProvs.length > 0) myProvs[0].troops += 7000;
              g.provinces.forEach(pr => { if (pr.ownerId === g.playerClanId) pr.order = Math.min(100, (pr.order || 80) + 20); });
              g.log('【牢人登用の英断】由比正雪・丸橋忠弥を厚遇して十万の牢人を親衛軍に編入！幕府の軍事力が劇的向上しました！', 'important');
              return '対立を乗り越え軍学者と武芸達人を幕政に招聘！天下の不満を一掃しました！';
            }
          }
        ]
      },
      {
        id: 'oshio_rebellion',
        scenarioId: '1837',
        title: '❖ 大塩平八郎の乱・「救民」の義旗と大坂城解放 ❖',
        subTitle: '天保の大飢饉・民を救うため決起した陽明学者と万民の怒涛',
        check: (game) => game.year >= 1837 && (game.playerClanId === 'oshio' || game.playerClanId === 'tokugawa' || game.playerClanId === 'mito' || game.playerClanId === 'shimazu' || game.playerClanId === 'mori'),
        narrative: (game) => game.playerClanId === 'oshio'
          ? '天保の大飢饉で路傍に餓死者が溢れる中、大坂東町奉行所と三井・鴻池ら豪商は米を江戸へ廻米し暴利を貪る。元与力・陽明学者たる大塩平八郎は「救民」の旗印と大砲を掲げ決起！大砲隊の精密砲撃で大坂城代・町奉行所を粉砕し、豪商の米蔵を開放して数十万の民衆とともに大坂城を完全占拠するか！'
          : '大坂にて元与力・大塩平八郎が門人・民衆を率いて武装蜂起！大坂市街が炎上し天領支配が揺らいでいる。鉄砲隊を投入して力攻めで鎮圧するか、あるいは大塩の建白書を容れて悪徳商人を取り潰し全国飢民を救済するか！',
        choices: (game) => game.playerClanId === 'oshio' ? [
          {
            text: '【歴史改変IF・大塩平八郎の乱大成功！】大坂城代を降伏させ大坂城を完全占拠！米蔵・金蔵を万民に開放！',
            desc: '大砲隊の猛威により大坂城を完全掌握！鴻池・三井の富を民に分配し、西国数万の義農兵が集結！摂津・河内・和泉を直轄化し、自軍兵力+8,000、米+5,000、金+2,500！',
            isHistorical: false,
            action: (g) => {
              g.gold += 2500;
              g.rice += 5000;
              const settsu = g.provinces.find(pr => pr.id === 'settsu');
              if (settsu) {
                settsu.ownerId = 'oshio';
                settsu.troops += 4000;
                settsu.defense = 100;
                settsu.order = 100;
              }
              const kawachi = g.provinces.find(pr => pr.id === 'kawachi');
              if (kawachi) {
                kawachi.ownerId = 'oshio';
                kawachi.troops = 3000;
                kawachi.order = 100;
              }
              const izumi = g.provinces.find(pr => pr.id === 'izumi');
              if (izumi) {
                izumi.ownerId = 'oshio';
                izumi.troops = 2500;
                izumi.order = 100;
              }
              g.provinces.filter(pr => pr.ownerId === 'tokugawa').forEach(pr => {
                pr.troops = Math.round(pr.troops * 0.7);
              });
              g.log('【大塩平八郎の乱 大勝利】「救民」の旗印のもと大坂城を解放！悪政を打ち破り飢民を救済する洗心洞新政権が誕生しました！', 'important');
              return '大砲轟く大坂城を完全制圧！巨商の米蔵を開放して民衆に施しを行い、近畿一円を義農軍が掌握しました！';
            }
          },
          {
            text: '【史実ルート】市中豪商の米蔵を打ち破り、飢民に米を配給して義挙の志を後世に託す。',
            desc: '民衆に米を配給し圧倒的民心を獲得。米+3,000、摂津の治安が100に！',
            isHistorical: true,
            action: (g) => {
              g.rice += 3000;
              const settsu = g.provinces.find(pr => pr.id === 'settsu');
              if (settsu) settsu.order = 100;
              g.log('【洗心洞の義民救済】大塩平八郎の義挙により蔵米が民衆に配給され、圧倒的な信望を獲得しました！');
              return '困窮する民のために一身を捧げた大塩の志は、全国の民衆に深い勇気を与えました！';
            }
          }
        ] : [
          {
            text: '【史実ルート】大坂町奉行所と諸藩の鉄砲隊を投入し、大坂市中の乱を断固鎮圧！',
            desc: '大塩の蜂起を鎮圧し、天領大坂の統制を再強化。治安回復、金+1,200獲得。',
            isHistorical: true,
            action: (g) => {
              g.gold += 1200;
              const settsu = g.provinces.find(pr => pr.id === 'settsu');
              if (settsu) {
                settsu.ownerId = g.playerClanId;
                settsu.order = 85;
              }
              g.log('【大塩の乱 鎮圧】町奉行所の鉄砲隊により大坂市中の騒乱を鎮圧し、天領の秩序を回復しました。');
              return '大坂市中の混乱を終息させ、幕府の統制を再確認しました。';
            }
          },
          {
            text: '【歴史改変IF】大塩の建白書を全面的に容れ、買占め商人を厳罰に処し全国飢民を救済！',
            desc: '悪徳商人を取り潰し米を放出！全国民衆が歓喜し、全領国治安+30、兵糧米+4,000獲得！',
            isHistorical: false,
            action: (g) => {
              g.rice += 4000;
              g.provinces.forEach(pr => { if (pr.ownerId === g.playerClanId) pr.order = Math.min(100, (pr.order || 80) + 30); });
              g.log('【徳政断行・民衆救済】大塩平八郎の直訴を受け入れ、米の買占めを厳罰処断！天下の民心を掴みました！', 'important');
              return '飢餓に苦しむ万民を救済する名君の英断！幕府に対する領民の信頼が一気に回復しました！';
            }
          }
        ]
      },
      {
        id: 'tenguto_rebellion',
        scenarioId: '*',
        title: '❖ 水戸天狗党の乱・中山道突破と尊皇維新 ❖',
        subTitle: '筑波山挙兵から雪の中山道千キロを踏破・尊皇攘夷の熱誠',
        check: (game) => game.year >= 1864 && (game.playerClanId === 'mito' || game.playerClanId === 'tokugawa' || game.playerClanId === 'mori' || game.playerClanId === 'shimazu' || game.playerClanId === 'aizu'),
        narrative: (game) => game.playerClanId === 'mito'
          ? '元治元年、武田耕雲斎・藤田小四郎ら水戸天狗党千余名が筑波山で挙兵！朝廷への直訴と尊皇攘夷の断行を求め、雪深い中山道を西上する。諸藩の追討軍を連破し、越前敦賀を猛突破して京都・御所へ到達！孝明天皇に直訴して「尊皇討幕」の密勅を獲得し、一挙に維新回天を成し遂げるか！'
          : '水戸藩激派・天狗党が筑波山で挙兵し、中山道を西上して京都へ向かっているとの急報！諸藩の追討軍を派遣して敦賀で完全包囲するか、あるいは天狗党の熱誠を受け入れ、尊皇攘夷親衛軍として朝廷・幕政の主軸に迎えるか！',
        choices: (game) => game.playerClanId === 'mito' ? [
          {
            text: '【歴史改変IF・天狗党の乱大成功！】敦賀の包囲網を猛突破！京都御所に到達し朝廷から尊皇密勅を獲得！',
            desc: '追討軍を連破し京都へ進駐！孝明天皇への直訴に成功し、長州藩・尊攘派と合流して幕府を震撼させる！常陸・近江を掌握、自軍兵力+7,000、士気激増！',
            isHistorical: false,
            action: (g) => {
              g.gold += 2000;
              g.rice += 2500;
              const hitachi = g.provinces.find(pr => pr.id === 'hitachi');
              if (hitachi) {
                hitachi.troops += 4000;
                hitachi.order = 100;
              }
              const omi = g.provinces.find(pr => pr.id === 'omi');
              if (omi) {
                omi.ownerId = 'mito';
                omi.troops = 4000;
                omi.order = 95;
              }
              g.provinces.filter(pr => pr.ownerId === 'tokugawa').forEach(pr => {
                pr.troops = Math.round(pr.troops * 0.75);
              });
              g.log('【天狗党の乱 大勝利】中山道を完全踏破して京都御所に進駐！朝廷より尊皇綸旨を賜り、水戸天狗党が維新の主導権を掌握しました！', 'important');
              return '雪の敦賀を突破した天狗党千余名の熱誠！京洛に進駐して孝明天皇に拝謁し、維新の大業を成し遂げました！';
            }
          },
          {
            text: '【史実ルート】無益な内戦を避け、徳川慶喜への忠節を尽くして大義を後世の維新志士に託す。',
            desc: '志士の魂が全国の尊攘派に受け継がれる。水戸藩の名声天下に轟き、軍資金+1,500獲得。',
            isHistorical: true,
            action: (g) => {
              g.gold += 1500;
              g.provinces.filter(pr => pr.ownerId === g.playerClanId).forEach(pr => pr.order = 100);
              g.log('【天狗党の忠烈】武田耕雲斎らの至誠は全国の志士を奮起させ、水戸学の精神が維新の礎となりました！');
              return '尊王攘夷に命を捧げた天狗党の熱誠は、後世の志士たちへと受け継がれました。';
            }
          }
        ] : [
          {
            text: '【史実ルート】諸藩連合軍を敦賀に布陣し、天狗党を完全包囲して幕府の法度を守る！',
            desc: '幕府の法度を維持し反乱を鎮圧。幕府直轄の威信回復、金+1,500獲得。',
            isHistorical: true,
            action: (g) => {
              g.gold += 1500;
              g.log('【天狗党 鎮圧】越前敦賀にて天狗党を包囲・降伏させ、天下の秩序を維持しました。');
              return '幕府追討軍の布陣により騒乱を収拾し、街道の治安を回復させました。';
            }
          },
          {
            text: '【歴史改変IF】徳川慶喜が天狗党を赦免・受け入れ、精鋭「天狗義勇隊」として幕府直属軍に再編！',
            desc: '水戸の精鋭志士を味方に引き入れ、幕軍の火力と白兵力を大幅強化！兵力+6,000獲得！',
            isHistorical: false,
            action: (g) => {
              const myProvs = g.provinces.filter(pr => pr.ownerId === g.playerClanId);
              if (myProvs.length > 0) myProvs[0].troops += 6000;
              g.log('【天狗義勇隊の結成】天狗党の熱誠を認め、精鋭部隊として編入！倒幕派を圧倒する強大な親衛軍が完成しました！', 'important');
              return '水戸の精鋭武士団を迎え入れ、軍事力を大幅に増強しました！';
            }
          }
        ]
      },
      {
        id: 'tenchugumi_rebellion',
        scenarioId: '*',
        title: '❖ 天誅組の変・大和五條挙兵と大和維新 ❖',
        subTitle: '吉村寅太郎・公卿中山忠光率いる尊攘義士・大和天領を急襲',
        check: (game) => game.year >= 1863 && (game.playerClanId === 'tokugawa' || game.playerClanId === 'mori' || game.playerClanId === 'shimazu' || game.playerClanId === 'tosa' || game.playerClanId === 'aizu'),
        narrative: (game) => '文久三年、土佐脱藩・吉村寅太郎や公卿・中山忠光ら尊攘激派四十余名が、大和行幸の先鋒となるべく大和五條代官所を急襲！代官を討ち取り、十津川郷士千余名を味方に引き入れた。高取城を電光石火で攻略し、大和国一円を解放して「大和維新独立政権」を樹立するか！',
        choices: (game) => [
          {
            text: '【歴史改変IF・天誅組の変大成功！】高取城を急襲制圧！十津川郷士とともに大和国を完全解放！',
            desc: '山岳ゲリラ戦で諸藩追討軍を撃退！大和国を直轄化し、自軍兵力+5,000、金+1,500獲得！倒幕の烽火が大和から燃え上がる！',
            isHistorical: false,
            action: (g) => {
              g.gold += 1500;
              const yamato = g.provinces.find(pr => pr.id === 'yamato');
              if (yamato) {
                yamato.ownerId = g.playerClanId;
                yamato.troops = 5000;
                yamato.defense = 95;
                yamato.order = 100;
              }
              g.log('【天誅組の変 大成功】十津川郷士と尊攘志士が大和五條・高取城を完全掌握！倒幕の先鋒拠点が確立されました！', 'important');
              return '大和の峻険な山岳に拠り追討軍を粉砕！天誅組の義挙が大成功を収めました！';
            }
          },
          {
            text: '【史実ルート】義勇の志を胸に十津川の山中に散るも、倒幕の精神的魁として名を残す。',
            desc: '尊皇攘夷の先駆として全国の志士を奮起させる。全領地治安向上、米+2,000獲得。',
            isHistorical: true,
            action: (g) => {
              g.rice += 2000;
              g.provinces.forEach(pr => { if (pr.ownerId === g.playerClanId) pr.order = Math.min(100, (pr.order || 80) + 15); });
              g.log('【天誅組の至誠】吉村寅太郎らの壮烈な最期は、全国の志士たちに倒幕の決意を固めさせました！');
              return '若き志士たちの散り際が、明治維新への大きな原動力となりました。';
            }
          }
        ]
      },
      {
        id: 'ikuno_rebellion',
        scenarioId: '*',
        title: '❖ 生野の変・但馬銀山掌握と山陰義勇軍 ❖',
        subTitle: '福岡藩脱藩・平野国臣が仕掛ける但馬生野代官所奪取',
        check: (game) => game.year >= 1863 && (game.playerClanId === 'mori' || game.playerClanId === 'tokugawa' || game.playerClanId === 'tosa' || game.playerClanId === 'shimazu' || game.playerClanId === 'kuroda'),
        narrative: (game) => '文久三年、平野国臣・澤宣嘉ら尊攘派志士が、天誅組に呼応して但馬生野代官所を占拠！莫大な富を生み出す生野銀山を確保した。農民たちに減税を布告して強固な信頼を築き、「農兵・山陰義勇軍」を組織して京都・山陰を席巻するか！',
        choices: (game) => [
          {
            text: '【歴史改変IF・生野の変大成功！】生野銀山の巨額資金を確保！数千の農兵義勇軍を組織し山陰を制圧！',
            desc: '但馬銀山の産出銀を軍資金に充当！但馬を完全直轄化し、金+3,000、自軍兵力+4,000獲得！山陰街道を完全に掌握！',
            isHistorical: false,
            action: (g) => {
              g.gold += 3000;
              const tajima = g.provinces.find(pr => pr.id === 'tajima');
              if (tajima) {
                tajima.ownerId = g.playerClanId;
                tajima.troops = 4500;
                tajima.order = 100;
              }
              g.log('【生野の変 大成功】平野国臣が生野銀山を確保し農兵部隊を組織！山陰から京都を窺う強力な拠点を確立しました！', 'important');
              return '農民との強固な信頼により数千の農兵義勇軍が結成！銀山の富とともに山陰を席巻しました！';
            }
          },
          {
            text: '【史実ルート】銀山の保全を最優先とし、産出銀を密かに長州・京の倒幕志士へ送達。',
            desc: '倒幕資金を隠密に移送し国力を蓄える。軍資金+1,500獲得。',
            isHistorical: true,
            action: (g) => {
              g.gold += 1500;
              g.log('【倒幕資金の確保】生野銀山の資金が密かに尊攘派へ送られ、維新の軍資金となりました。');
              return '貴重な資金を安全に確保し、来たるべき決戦に備えました。';
            }
          }
        ]
      },
      {
        id: 'sanhei_ikki',
        scenarioId: '*',
        title: '❖ 嘉永三閉伊一揆・百姓一万六千の越訴大勝利 ❖',
        subTitle: '日本史上最大の組織的一揆・国境を越えた農民自治の奇跡',
        check: (game) => game.year >= 1853 && (game.playerClanId === 'nanbu' || game.playerClanId === 'date' || game.playerClanId === 'tokugawa'),
        narrative: (game) => '南部盛岡藩の重税と苛政に耐えかねた沿岸三閉伊（宮古・大槌など）の百姓一万六千人が蜂起！武器を一切持たず、整然たる規律を保って国境を越え、隣国・仙台藩領へ集団越訴を敢行した！藩庁を震撼させた百姓たちは、悪代官罷免と大幅減税を直接談判で要求！',
        choices: (game) => [
          {
            text: '【史実・農民大勝利ルート】百姓側の要求を全面受諾！悪徳役人を罷免し農民自治と減税を承認！',
            desc: '日本一揆史上稀に見る大勝利！民衆の絶大なる信頼を得て治安が100に達し、生産性向上で兵糧米+3,500、資金+1,000獲得！',
            isHistorical: true,
            action: (g) => {
              g.rice += 3500;
              g.gold += 1000;
              g.provinces.filter(pr => pr.ownerId === g.playerClanId).forEach(pr => pr.order = 100);
              g.log('【三閉伊一揆 和解大勝利】百姓側の要求を全面的に受け入れ悪政を打破！領内治安は最大となり、大増産が達成されました！', 'important');
              return '規律ある百姓一万六千との対話により、悪徳役人を一掃！領民の絶大なる信望を勝ち取りました！';
            }
          },
          {
            text: '【歴史改変IF】一揆の卓越した組織力に着目！農民指導者を郷士に登用し「三閉伊農兵隊」を結成！',
            desc: '規律正しい農民軍団を編成！自軍兵力+4,500、陸中・陸奥の防衛度+30！',
            isHistorical: false,
            action: (g) => {
              const myProvs = g.provinces.filter(pr => pr.ownerId === g.playerClanId);
              if (myProvs.length > 0) {
                myProvs[0].troops += 4500;
                myProvs[0].defense = Math.min(100, (myProvs[0].defense || 50) + 30);
              }
              g.log('【三閉伊農兵隊の誕生】百姓指導者を武士に登用し、規律強固な農兵部隊4,500人を編成しました！', 'important');
              return '百姓の鉄の結束をそのまま軍事力に昇華！精強な郷士部隊が誕生しました！';
            }
          }
        ]
      },
      {
        id: 'ikuta_yorozu_rebellion',
        scenarioId: '1837',
        title: '❖ 生田万の乱・越後柏崎の義挙と北越解放 ❖',
        subTitle: '大塩の義挙に呼応・国学者生田万が桑名藩柏崎陣屋を急襲',
        check: (game) => game.year >= 1837 && (game.playerClanId === 'tokugawa' || game.playerClanId === 'uesugi' || game.playerClanId === 'oshio' || game.playerClanId === 'maeda'),
        narrative: (game) => '大塩平八郎の大坂蜂起に呼応し、越後柏崎の国学者・生田万（いくたよろず）が門人・義農を率いて桑名藩柏崎陣屋を急襲！越後の貧民を救うべく米蔵を破り、北越の民衆蜂起を巻き起こす！',
        choices: (game) => [
          {
            text: '【歴史改変IF・生田万の乱大成功！】柏崎陣屋を占拠し北越の義農軍を組織！越後天領・佐渡金山への道を制圧！',
            desc: '越後全域の民衆が歓喜呼応！自軍兵力+4,500、兵糧米+2,500、金+1,000獲得！越後を完全掌握！',
            isHistorical: false,
            action: (g) => {
              g.rice += 2500;
              g.gold += 1000;
              const echigo = g.provinces.find(pr => pr.id === 'echigo');
              if (echigo) {
                echigo.ownerId = g.playerClanId;
                echigo.troops += 4500;
                echigo.order = 100;
              }
              g.log('【生田万の乱 大成功】越後柏崎陣屋を制圧し飢民を救済！越後天領の義農軍が結集し北越を掌握しました！', 'important');
              return '生田万の熱き志が北越の農民を奮起させ、越後天領を解放することに成功しました！';
            }
          },
          {
            text: '【史実ルート】義挙の志を越後民衆に刻み、義民の鑑として歴史に名を残す。',
            desc: '民衆に米を配給し治安向上。兵糧米+2,000獲得。',
            isHistorical: true,
            action: (g) => {
              g.rice += 2000;
              const echigo = g.provinces.find(pr => pr.id === 'echigo');
              if (echigo) echigo.order = Math.min(100, (echigo.order || 80) + 20);
              g.log('【生田万の義挙】飢民救済を掲げた生田万の志は、越後領民の心に深く刻まれました。');
              return '義民の尊い犠牲が民衆の結束と治安維持につながりました。';
            }
          }
        ]
      },
"""

text = text[:obj_start] + replacement_events + text[obj_end:]

# 2. Add rebellion player reversal in applyHistoricalEventAccept
reversal_marker = "if (ev.changes && ev.changes.territory) {"
reversal_idx = text.find(reversal_marker)

if reversal_idx == -1:
    print("Error: Could not locate reversal_marker in app.js")
    sys.exit(1)

reversal_code = """      // プレイヤーが反乱勢力時の特別逆転勝利処理（史実滅亡イベントを大逆転勝利へ昇華！）
      if (this.playerClanId === 'yui' && ev.id === 'evt_1651_keian_hen') {
        const musashi = this.provinces.find(p => p.id === 'musashi');
        const suruga = this.provinces.find(p => p.id === 'suruga');
        const sagami = this.provinces.find(p => p.id === 'sagami');
        if (musashi) { musashi.ownerId = 'yui'; musashi.troops = Math.max(musashi.troops, 6000); musashi.order = 95; }
        if (suruga) { suruga.ownerId = 'yui'; suruga.troops += 4000; suruga.order = 100; }
        if (sagami) { sagami.ownerId = 'yui'; sagami.troops = Math.max(sagami.troops, 4000); }
        this.gold += 3000;
        this.log('⚔️【由比正雪の乱 大勝利】丸橋忠弥の奇襲により江戸城を掌握！十万牢人を糾合して新幕府秩序を樹立！', 'important');
      } else if (this.playerClanId === 'oshio' && ev.id === 'evt_1837_oshio') {
        const settsu = this.provinces.find(p => p.id === 'settsu');
        const kawachi = this.provinces.find(p => p.id === 'kawachi');
        const izumi = this.provinces.find(p => p.id === 'izumi');
        if (settsu) { settsu.ownerId = 'oshio'; settsu.troops = Math.max(settsu.troops, 6000); settsu.order = 100; }
        if (kawachi) { kawachi.ownerId = 'oshio'; kawachi.troops = Math.max(kawachi.troops, 4000); kawachi.order = 100; }
        if (izumi) { izumi.ownerId = 'oshio'; izumi.troops = Math.max(izumi.troops, 3500); izumi.order = 100; }
        this.rice += 5000;
        this.gold += 2500;
        this.log('⚔️【大塩平八郎の乱 大勝利】「救民」の旗のもと大坂城を完全解放！近畿三箇国を掌握！', 'important');
      } else if (this.playerClanId === 'amakusa' && ev.id === 'evt_1638_shimabara_fall') {
        const hizen = this.provinces.find(p => p.id === 'hizen');
        const higo = this.provinces.find(p => p.id === 'higo');
        if (hizen) { hizen.ownerId = 'amakusa'; hizen.troops = Math.max(hizen.troops, 7000); hizen.order = 100; hizen.defense = 100; }
        if (higo) { higo.ownerId = 'amakusa'; higo.troops = Math.max(higo.troops, 4500); higo.order = 95; }
        this.gold += 2500;
        this.log('⚔️【島原の乱 大勝利】原城にて幕府軍十二万を完全撃退！キリシタン・牢人自由領国を樹立！', 'important');
      } else """ + reversal_marker

text = text[:reversal_idx] + reversal_code + text[reversal_idx + len(reversal_marker):]

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Successfully updated js/app.js with rebellion events and reverse-victory handlers!")
