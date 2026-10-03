import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Look for resolveOfficerAffiliations method
search_header = "resolveOfficerAffiliations(scen) {"
idx_head = text.find(search_header)
if idx_head == -1:
    print("Could not find resolveOfficerAffiliations")
    sys.exit(1)

# Find where the officers loop begins:
# this.activeOfficers.forEach(off => {
search_loop = "this.activeOfficers.forEach(off => {"
idx_loop = text.find(search_loop, idx_head)
if idx_loop == -1:
    print("Could not find forEach loop")
    sys.exit(1)

# Insertion 1: Right after "if (off.clanId === this.playerClanId && ownersSet.has(this.playerClanId)) return;"
target_after_player = "if (off.clanId === this.playerClanId && ownersSet.has(this.playerClanId)) return;"
pos_insert1 = text.find(target_after_player, idx_loop)
if pos_insert1 == -1:
    print("Could not find playerClanId check")
    sys.exit(1)

pos_insert1 += len(target_after_player)

gov_assignment_code = """

      // 【史実城代・配置武将の絶対保証】
      // シナリオの史実城代（SCENARIO_HISTORICAL_GOVERNORS）に指名されている武将は、
      // その領国の領主（ownerId）に確実に配属（浪人化・城主不在を完全防止）
      const scenGovMap = (window.SCENARIO_HISTORICAL_GOVERNORS && window.SCENARIO_HISTORICAL_GOVERNORS[String(scen.id)]) || {};
      const myGovProv = Object.keys(scenGovMap).find(pId => scenGovMap[pId] === off.id);
      if (myGovProv) {
        const pObj = this.provinces.find(p => p.id === myGovProv);
        const provOwner = pObj ? pObj.ownerId : null;
        if (provOwner && ownersSet.has(provOwner)) {
          off.clanId = provOwner;
          off.isDaimyo = false;
          return;
        }
      }"""

# Check if already added
if "【史実城代・配置武将の絶対保証】" not in text:
    text = text[:pos_insert1] + gov_assignment_code + text[pos_insert1:]
    print("Added governor guarantee code to resolveOfficerAffiliations.")
else:
    print("Governor guarantee code already present.")

# Insertion 2: In the clanAlias and fallback section
# Find: const clanAlias = {
alias_pos = text.find("const clanAlias = {")
if alias_pos != -1:
    end_alias_pos = text.find("};", alias_pos)
    # Expand clanAlias object
    old_alias_chunk = text[alias_pos:end_alias_pos+2]
    new_alias_chunk = """const clanAlias = {
        kuroda: 'fukuoka_kuroda',
        fukuoka_kuroda: 'kuroda',
        hosokawa: 'kumamoto_hosokawa',
        kumamoto_hosokawa: 'hosokawa',
        shogunate: 'tokugawa',
        shonai: 'tokugawa',
        kuwana: 'tokugawa',
        makino: 'tokugawa',
        chiba: 'hojo',
        kunohe: 'nanbu',
        tsugaru: (year < 1585 ? 'nanbu' : 'tsugaru'),
        ii: (year === 1868 ? 'meiji' : 'tokugawa')
      };"""
    text = text[:alias_pos] + new_alias_chunk + text[end_alias_pos+2:]
    print("Updated clanAlias dictionary.")

# Insertion 3: Before "// 2. 所属大名が不在の武将は「浪人（諸国流浪・未仕官）」とし、仕官・登用の対象とする"
target_before_ronin = "// 2. 所属大名が不在の武将は「浪人（諸国流浪・未仕官）」とし、仕官・登用の対象とする"
pos_ronin = text.find(target_before_ronin)
if pos_ronin != -1:
    historical_rules_code = """// 【包括的史実配属・浪人化防止ルール】
      // 史実上仕えるべき大名・藩・幕府が地図上に存在する場合、浪人化させずに正しく配属

      // 1. 幕末・明治シナリオ（1837〜1868年）
      if (year >= 1837) {
        // 松代藩真田氏（真田幸教、真田幸民、真田幸貫）
        if (off.id.includes('sanada') || off.name.includes('真田幸教') || off.name.includes('真田幸民') || off.name.includes('真田幸貫')) {
          if (year === 1868 && ownersSet.has('meiji')) { off.clanId = 'meiji'; off.isDaimyo = false; return; }
          if (ownersSet.has('tokugawa')) { off.clanId = 'tokugawa'; off.isDaimyo = false; return; }
        }
        // 熊本藩細川氏（細川斉護、細川韶邦、細川護久）
        if (off.name.includes('細川韶邦') || off.name.includes('細川護久') || off.name.includes('細川斉護') || off.id.includes('hosokawa')) {
          if (ownersSet.has('kumamoto_hosokawa')) { off.clanId = 'kumamoto_hosokawa'; return; }
          if (ownersSet.has('hosokawa')) { off.clanId = 'hosokawa'; return; }
          if (year === 1868 && ownersSet.has('meiji')) { off.clanId = 'meiji'; off.isDaimyo = false; return; }
          if (ownersSet.has('tokugawa')) { off.clanId = 'tokugawa'; off.isDaimyo = false; return; }
        }
        // 福岡藩黒田氏（黒田長溥、黒田長知）
        if (off.name.includes('黒田長溥') || off.name.includes('黒田長知') || off.id.includes('kuroda')) {
          if (ownersSet.has('fukuoka_kuroda')) { off.clanId = 'fukuoka_kuroda'; return; }
          if (ownersSet.has('kuroda')) { off.clanId = 'kuroda'; return; }
          if (year === 1868 && ownersSet.has('meiji')) { off.clanId = 'meiji'; off.isDaimyo = false; return; }
          if (ownersSet.has('tokugawa')) { off.clanId = 'tokugawa'; off.isDaimyo = false; return; }
        }
        // 彦根藩井伊氏（井伊直弼、井伊直憲、木俣守易）
        if (off.id.includes('ii') || off.name.includes('井伊直弼') || off.name.includes('井伊直憲') || off.name.includes('木俣守易')) {
          if (ownersSet.has('ii')) { off.clanId = 'ii'; return; }
          if (year === 1868 && ownersSet.has('meiji')) { off.clanId = 'meiji'; off.isDaimyo = false; return; }
          if (ownersSet.has('tokugawa')) { off.clanId = 'tokugawa'; off.isDaimyo = false; return; }
        }
        // 加賀・富山前田氏（前田利同、前田利保、前田斉泰、前田慶寧）
        if (off.id.includes('maeda') || off.name.includes('前田利同') || off.name.includes('前田利保') || off.name.includes('前田斉泰') || off.name.includes('前田慶寧')) {
          if (ownersSet.has('maeda')) { off.clanId = 'maeda'; return; }
          if (year === 1868 && ownersSet.has('meiji')) { off.clanId = 'meiji'; off.isDaimyo = false; return; }
          if (ownersSet.has('tokugawa')) { off.clanId = 'tokugawa'; off.isDaimyo = false; return; }
        }
        // 南部・八戸（南部信順、楢山佐渡、南部利剛）
        if (off.id.includes('nanbu') || off.name.includes('南部信順') || off.name.includes('楢山佐渡') || off.name.includes('南部利剛')) {
          if (ownersSet.has('nanbu')) { off.clanId = 'nanbu'; return; }
          if (ownersSet.has('tokugawa')) { off.clanId = 'tokugawa'; off.isDaimyo = false; return; }
        }
        // 会津藩松平氏（松平容保、山本八重、佐川官兵衛）
        if (off.name.includes('松平容保') || off.name.includes('山本八重') || off.name.includes('佐川官兵衛')) {
          if (ownersSet.has('aizu')) { off.clanId = 'aizu'; return; }
          if (ownersSet.has('tokugawa')) { off.clanId = 'tokugawa'; off.isDaimyo = false; return; }
        }
        // 幕府譜代大名・老中・幕臣
        const bakufuVassals = [
          '小栗忠順', '小栗上野介', '板倉勝静', '山田方谷', '大久保忠礼', '林忠崇', '阿部正方', '阿部正弘',
          '酒井忠惇', '松平定敬', '松平定法', '松平頼種', '小笠原忠忱', '中川久成', '立見鑑三郎', '河井継之助',
          '榎本武揚', '大鳥圭介', '人見勝太郎', '中島登', '春日左衛門', '島田魁', '酒井吉之丞', '伴百悦'
        ];
        if (bakufuVassals.some(kw => off.name.includes(kw) || off.id.includes(kw))) {
          if (year === 1868 && ownersSet.has('goryokaku') && ['榎本武揚', '大鳥圭介', '土方歳三', '人見勝太郎', '中島登', '春日左衛門', '島田魁'].some(kw => off.name.includes(kw))) {
            off.clanId = 'goryokaku'; return;
          }
          if (year === 1868 && ownersSet.has('shonai') && ['酒井吉之丞', '伴百悦'].some(kw => off.name.includes(kw))) {
            off.clanId = 'shonai'; return;
          }
          if (ownersSet.has('tokugawa')) { off.clanId = 'tokugawa'; off.isDaimyo = false; return; }
        }
      }

      // 2. 関ヶ原の戦い（1600年）
      if (String(scen.id) === '1600' || year === 1600) {
        const eastAdditional = [
          '細川藤孝', '細川幽斎', '細川忠利', '池田利隆', '池田忠継', '山名豊国', '伊東祐兵', '京極高次', '京極忠高',
          '蜂須賀至鎮', '蜂須賀家政', '山内忠義', '今川氏真', '相良頼房', '里見義康', '北条氏長', '小笠原秀政', '金森長近'
        ];
        if (eastAdditional.some(kw => off.name.includes(kw) || off.id.includes(kw))) {
          if (off.name.includes('細川') && ownersSet.has('hosokawa')) { off.clanId = 'hosokawa'; return; }
          if (off.name.includes('池田') && ownersSet.has('okayama')) { off.clanId = 'okayama'; return; }
          if (ownersSet.has('tokugawa')) { off.clanId = 'tokugawa'; off.isDaimyo = false; return; }
        }
        if (off.name.includes('島左近') || off.name.includes('下間頼廉')) {
          if (ownersSet.has('ishida')) { off.clanId = 'ishida'; off.isDaimyo = false; return; }
        }
        if (off.name.includes('龍造寺政家') || off.name.includes('後藤家信')) {
          if (ownersSet.has('nabeshima')) { off.clanId = 'nabeshima'; off.isDaimyo = false; return; }
        }
      }

      // 3. 戦国・安土桃山（豊臣政権下・徳川家臣団・織田家臣団）
      if (year >= 1582 && year <= 1598 && ownersSet.has('toyotomi')) {
        const toyoAllKeys = [
          '九鬼嘉隆', '片桐且元', '脇坂安治', '生駒親正', '前野長康', '宮部継潤', '南条元続', '蜂屋頼隆',
          '小出吉政', '増田長盛', '前田玄以', '長束正家', '浅野長政', '石田三成', '大谷吉継'
        ];
        if (toyoAllKeys.some(kw => off.name.includes(kw) || off.id.includes(kw)) || off.clanId === 'toyotomi') {
          off.clanId = 'toyotomi';
          off.isDaimyo = false;
          return;
        }
      }
      if (ownersSet.has('tokugawa') && year >= 1560 && year <= 1650) {
        const tokuAllKeys = [
          '内藤清成', '平岡頼勝', '金森可重', '大久保長安', '木俣守勝', '平岩親吉', '板倉勝重', '松平秀忠', '徳川秀忠', '松平忠輝'
        ];
        if (tokuAllKeys.some(kw => off.name.includes(kw) || off.id.includes(kw))) {
          off.clanId = 'tokugawa';
          off.isDaimyo = false;
          return;
        }
      }

      """
    if "【包括的史実配属・浪人化防止ルール】" not in text:
        text = text[:pos_ronin] + historical_rules_code + text[pos_ronin:]
        print("Added historical rules code to resolveOfficerAffiliations.")
    else:
        print("Historical rules code already present.")

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Successfully updated js/app.js!")
