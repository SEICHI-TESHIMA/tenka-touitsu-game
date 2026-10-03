import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Helper replacement function for each event action
replacements = [
    # 1. kunohe_rebellion player action
    (
        "g.provinces.filter(pr => pr.ownerId === 'toyotomi').forEach(pr => {\n                pr.troops = Math.round(pr.troops * 0.75);\n              });",
        """g.provinces.filter(pr => pr.ownerId === 'toyotomi').forEach(pr => {
                pr.troops = Math.round(pr.troops * 0.75);
              });
              // 猛将・九戸政実＆実親を配下に加入
              ['off_kunohe_masazane', 'off_kunohe_sanechika'].forEach(id => {
                const master = (window.OFFICERS_MASTER || []).find(m => m.id === id);
                if (master) {
                  const existing = g.activeOfficers?.find(o => o.id === id);
                  if (existing) { existing.clanId = g.playerClanId; existing.isDead = false; }
                  else if (g.activeOfficers) { const o = JSON.parse(JSON.stringify(master)); o.clanId = g.playerClanId; g.activeOfficers.push(o); }
                }
              });"""
    ),
    # 2. kunohe_rebellion toyotomi recruit action
    (
        "if (myProvs.length > 0) myProvs[0].troops += 5000;\n              g.log('【九戸政実の帰順】",
        """if (myProvs.length > 0) myProvs[0].troops += 5000;
              ['off_kunohe_masazane', 'off_kunohe_sanechika'].forEach(id => {
                const master = (window.OFFICERS_MASTER || []).find(m => m.id === id);
                if (master) {
                  const existing = g.activeOfficers?.find(o => o.id === id);
                  if (existing) { existing.clanId = g.playerClanId; existing.isDead = false; }
                  else if (g.activeOfficers) { const o = JSON.parse(JSON.stringify(master)); o.clanId = g.playerClanId; g.activeOfficers.push(o); }
                }
              });
              g.log('【九戸政実の帰順】"""
    ),
    # 3. keian_yui_rebellion tokugawa recruit action
    (
        "if (myProvs.length > 0) myProvs[0].troops += 7000;\n              g.provinces.forEach(pr => {",
        """if (myProvs.length > 0) myProvs[0].troops += 7000;
              ['off_edo_yui_1605_0', 'off_edo_yui_1605_1'].forEach(id => {
                const master = (window.OFFICERS_MASTER || []).find(m => m.id === id);
                if (master) {
                  const existing = g.activeOfficers?.find(o => o.id === id);
                  if (existing) { existing.clanId = g.playerClanId; existing.isDead = false; }
                  else if (g.activeOfficers) { const o = JSON.parse(JSON.stringify(master)); o.clanId = g.playerClanId; g.activeOfficers.push(o); }
                }
              });
              g.provinces.forEach(pr => {"""
    ),
    # 4. oshio_rebellion tokugawa reform action
    (
        "g.rice += 4000;\n              g.provinces.forEach(pr => { if (pr.ownerId === g.playerClanId) pr.order = Math.min(100, (pr.order || 80) + 30); });",
        """g.rice += 4000;
              ['off_edo_oshio_1793_8', 'off_ikuta_yorozu'].forEach(id => {
                const master = (window.OFFICERS_MASTER || []).find(m => m.id === id);
                if (master) {
                  const existing = g.activeOfficers?.find(o => o.id === id);
                  if (existing) { existing.clanId = g.playerClanId; existing.isDead = false; }
                  else if (g.activeOfficers) { const o = JSON.parse(JSON.stringify(master)); o.clanId = g.playerClanId; g.activeOfficers.push(o); }
                }
              });
              g.provinces.forEach(pr => { if (pr.ownerId === g.playerClanId) pr.order = Math.min(100, (pr.order || 80) + 30); });"""
    ),
    # 5. tenguto_rebellion mito player action
    (
        "g.provinces.filter(pr => pr.ownerId === 'tokugawa').forEach(pr => {\n                pr.troops = Math.round(pr.troops * 0.75);\n              });",
        """g.provinces.filter(pr => pr.ownerId === 'tokugawa').forEach(pr => {
                pr.troops = Math.round(pr.troops * 0.75);
              });
              ['off_takeda_kounsai', 'off_fujita_koshiro'].forEach(id => {
                const master = (window.OFFICERS_MASTER || []).find(m => m.id === id);
                if (master) {
                  const existing = g.activeOfficers?.find(o => o.id === id);
                  if (existing) { existing.clanId = g.playerClanId; existing.isDead = false; }
                  else if (g.activeOfficers) { const o = JSON.parse(JSON.stringify(master)); o.clanId = g.playerClanId; g.activeOfficers.push(o); }
                }
              });"""
    ),
    # 6. tenguto_rebellion tokugawa recruit action
    (
        "if (myProvs.length > 0) myProvs[0].troops += 6000;\n              g.log('【天狗義勇隊の結成】",
        """if (myProvs.length > 0) myProvs[0].troops += 6000;
              ['off_takeda_kounsai', 'off_fujita_koshiro'].forEach(id => {
                const master = (window.OFFICERS_MASTER || []).find(m => m.id === id);
                if (master) {
                  const existing = g.activeOfficers?.find(o => o.id === id);
                  if (existing) { existing.clanId = g.playerClanId; existing.isDead = false; }
                  else if (g.activeOfficers) { const o = JSON.parse(JSON.stringify(master)); o.clanId = g.playerClanId; g.activeOfficers.push(o); }
                }
              });
              g.log('【天狗義勇隊の結成】"""
    ),
    # 7. tenchugumi_rebellion player action
    (
        "yamato.order = 100;\n              }\n              g.log('【天誅組の変 大成功】",
        """yamato.order = 100;
              }
              ['off_yoshimura_torataro', 'off_nakayama_tadamitsu'].forEach(id => {
                const master = (window.OFFICERS_MASTER || []).find(m => m.id === id);
                if (master) {
                  const existing = g.activeOfficers?.find(o => o.id === id);
                  if (existing) { existing.clanId = g.playerClanId; existing.isDead = false; }
                  else if (g.activeOfficers) { const o = JSON.parse(JSON.stringify(master)); o.clanId = g.playerClanId; g.activeOfficers.push(o); }
                }
              });
              g.log('【天誅組の変 大成功】"""
    ),
    # 8. ikuno_rebellion player action
    (
        "tajima.order = 100;\n              }\n              g.log('【生野の変 大成功】",
        """tajima.order = 100;
              }
              ['off_hirano_kuniomi'].forEach(id => {
                const master = (window.OFFICERS_MASTER || []).find(m => m.id === id);
                if (master) {
                  const existing = g.activeOfficers?.find(o => o.id === id);
                  if (existing) { existing.clanId = g.playerClanId; existing.isDead = false; }
                  else if (g.activeOfficers) { const o = JSON.parse(JSON.stringify(master)); o.clanId = g.playerClanId; g.activeOfficers.push(o); }
                }
              });
              g.log('【生野の変 大成功】"""
    ),
    # 9. ikuta_yorozu_rebellion player action
    (
        "echigo.order = 100;\n              }\n              g.log('【生田万の乱 大成功】",
        """echigo.order = 100;
              }
              ['off_ikuta_yorozu'].forEach(id => {
                const master = (window.OFFICERS_MASTER || []).find(m => m.id === id);
                if (master) {
                  const existing = g.activeOfficers?.find(o => o.id === id);
                  if (existing) { existing.clanId = g.playerClanId; existing.isDead = false; }
                  else if (g.activeOfficers) { const o = JSON.parse(JSON.stringify(master)); o.clanId = g.playerClanId; g.activeOfficers.push(o); }
                }
              });
              g.log('【生田万の乱 大成功】"""
    )
]

for src, dst in replacements:
    if src in text:
        text = text.replace(src, dst, 1)
        print("Replaced a section successfully!")
    else:
        print("Warning: could not find snippet:\n", src[:50])

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Finished enriching rebellion events with officer assignments!")
