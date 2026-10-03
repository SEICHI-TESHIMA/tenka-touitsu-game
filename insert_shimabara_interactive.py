import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Check if shimabara_rebellion is already in app.js
if 'shimabara_rebellion' in text:
    print("shimabara_rebellion already in app.js!")
    sys.exit(0)

# Target location to insert: right after tobafushimi event
marker = "id: 'tobafushimi',"
idx = text.find(marker)
if idx == -1:
    print("Marker tobafushimi not found, trying end of getHistoricalEventsMaster")
    idx = text.find("getHistoricalEventsMaster() {")

# Find the end of tobafushimi event block
# Let's locate the next "{" after tobafushimi's closing "}"
close_bracket = text.find("      },", idx)
insert_pos = close_bracket + len("      },\n")

shimabara_event_code = """      {
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
          },
          {
            text: '【歴史改変IF】原城を電光石火で出撃！長崎出島を急襲占拠し南蛮船と合流！',
            desc: '包囲軍の間隙を突き海路長崎へ突入！新式南蛮鉄砲と大砲を獲得し、金+2,000、自軍兵力+6,000！',
            isHistorical: false,
            action: (g) => {
              g.gold += 2000;
              const hizen = g.provinces.find(pr => pr.id === 'hizen');
              if (hizen) hizen.troops += 6000;
              g.log('【長崎急襲の成功】原城を出撃した一揆勢が長崎出島を電光石火で制圧！南蛮鉄砲と資金を確保しました！', 'important');
              return '幕府軍の不意を突いて海路長崎へ進撃！南蛮船の支援を取り付け、新たな戦線を切り拓きました！';
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
"""

new_text = text[:insert_pos] + shimabara_event_code + text[insert_pos:]

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Successfully inserted shimabara_rebellion interactive event into app.js!")
