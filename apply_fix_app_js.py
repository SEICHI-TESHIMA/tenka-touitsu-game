import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect exact block for 1584 to 1690
idx_start = text.find('// 【最優先: シナリオ固有の史実所属・配属】')
idx_end = text.find('// 既に浪人として流浪している武将は浪人を維持', idx_start)

if idx_start == -1 or idx_end == -1:
    print("Error: Markers not found!")
    sys.exit(1)

old_block = text[idx_start:idx_end]

# Design new clean replacement block with all additions
new_block = """// 【最優先: シナリオ固有の史実所属・配属】
      // 共通ルール: 津軽為信（南部領のシナリオでは南部配下・津軽城代、津軽家独立後は津軽当主）
      if (off.id === 'off_tsugaru_tamenobu' || off.name === '津軽為信') {
        const tsugaruProv = this.provinces.find(p => p.id === 'tsugaru');
        if (tsugaruProv && tsugaruProv.ownerId === 'nanbu' && ownersSet.has('nanbu')) {
          off.clanId = 'nanbu';
          off.isDaimyo = false;
          return;
        } else if (ownersSet.has('tsugaru')) {
          off.clanId = 'tsugaru';
          return;
        }
      }

      // 共通ルール: 北信愛（南部家重臣）
      if (off.id === 'off_kita_nobuchika' || off.name === '北信愛') {
        if (ownersSet.has('nanbu')) {
          off.clanId = 'nanbu';
          off.isDaimyo = false;
          return;
        }
      }

      // 共通ルール: 山浦景国（上杉家重臣）
      if (off.id.includes('succ_murakami_1555_100') || off.name === '山浦景国') {
        if (ownersSet.has('uesugi')) {
          off.clanId = 'uesugi';
          off.isDaimyo = false;
          return;
        }
      }

      // 共通ルール: 木俣守勝（井伊家・徳川家臣）
      if (off.id === 'off_kimata_morikatsu' || off.name === '木俣守勝') {
        if (ownersSet.has('ii')) { off.clanId = 'ii'; off.isDaimyo = false; return; }
        if (ownersSet.has('tokugawa')) { off.clanId = 'tokugawa'; off.isDaimyo = false; return; }
      }

      // 1582年 本能寺の変前夜: 信長存命期の織田家臣団
      if (String(scen.id) === '1582' || year === 1582) {
        const odaRetainers = [
          '秀吉', '秀長', '秀次', '明智光秀', '斎藤利三', '溝尾庄兵衛', '妻木', '藤田行政', '並河易家',
          '柴田勝家', '佐久間盛政', '佐久間安政', '柴田勝豊', '前田利家', '前田利益', '佐々成政',
          '丹羽長秀', '滝川一益', '森長可', '蒲生氏郷', '池田恒興', '池田元助', '池田輝政',
          '高山右近', '中川清秀', '細川藤孝', '細川幽斎', '細川忠興', '筒井順慶', '織田信忠', '織田信雄', '織田信孝',
          '黒田官兵衛', '黒田孝高', '黒田如水', '蜂須賀正勝', '蜂須賀小六', '蜂須賀家政', '石田三成', '大谷吉継',
          '福島正則', '加藤清正', '浅野長政', '山内一豊', '堀秀政', '長谷川秀一', '稲葉一鉄', '安藤守就', '氏家卜全', '氏家行広',
          '小西行長', '長連龍'
        ];
        if (odaRetainers.some(kw => off.name.includes(kw) || off.id.includes(kw))) {
          if (ownersSet.has('oda')) {
            off.clanId = 'oda';
            return;
          }
        }
        const tokuRetainers = ['徳川家康', '松平元康', '本多忠勝', '酒井忠次', '榊原康政', '井伊直政', '服部半蔵', '石川数正', '大久保忠世', '鳥居元忠'];
        if (tokuRetainers.some(kw => off.name.includes(kw) || off.id.includes(kw))) {
          if (ownersSet.has('tokugawa')) {
            off.clanId = 'tokugawa';
            return;
          }
        }
        if (off.name.includes('真田昌幸') || off.name.includes('真田信之') || off.name.includes('真田幸村')) {
          if (ownersSet.has('sanada')) { off.clanId = 'sanada'; return; }
        }
        if (off.name.includes('千葉邦胤') || off.name.includes('千葉重胤') || off.id.includes('chiba')) {
          if (ownersSet.has('hojo')) { off.clanId = 'hojo'; off.isDaimyo = false; return; }
        }
      }

      // 1584年 小牧長久手の戦い: 羽柴方・織田信雄方・徳川方・北条方・佐々方
      if (String(scen.id) === '1584' || year === 1584) {
        const toyoRetainers = [
          '秀吉', '秀長', '秀次', '池田恒興', '池田輝政', '森長可', '堀秀政', '前田利家', '浅野長政',
          '石田三成', '大谷吉継', '蒲生氏郷', '丹羽長秀', '蜂須賀正勝', '蜂須賀家政', '加藤清正', '福島正則',
          '小西行長', '細川藤孝', '細川幽斎', '細川忠興', '長連龍', '前田玄以', '山名豊国', '金森可重',
          '脇坂安治', '伊東祐兵', '小出吉政'
        ];
        if (toyoRetainers.some(kw => off.name.includes(kw) || off.id.includes(kw))) {
          if (ownersSet.has('toyotomi')) {
            off.clanId = 'toyotomi';
            off.isDaimyo = false;
            return;
          }
        }
        const tokuRetainers = [
          '徳川家康', '酒井忠次', '本多忠勝', '榊原康政', '井伊直政', '鳥居元忠', '大久保忠世',
          '木曾義昌', '小笠原貞慶', '石川数正', '大久保忠隣', '服部半蔵', '諏訪頼忠', '木俣守勝'
        ];
        if (tokuRetainers.some(kw => off.name.includes(kw) || off.id.includes(kw))) {
          if (ownersSet.has('tokugawa')) {
            off.clanId = 'tokugawa';
            return;
          }
        }
        const hojoRetainers = ['北条氏邦', '北条氏規', '千葉邦胤', '成田氏長', '成田長親'];
        if (hojoRetainers.some(kw => off.name.includes(kw) || off.id.includes(kw))) {
          if (ownersSet.has('hojo')) {
            off.clanId = 'hojo';
            off.isDaimyo = false;
            return;
          }
        }
        const odaRetainers = ['織田信雄', '滝川雄利', '滝川一益'];
        if (odaRetainers.some(kw => off.name.includes(kw) || off.id.includes(kw))) {
          if (ownersSet.has('oda')) {
            off.clanId = 'oda';
            return;
          }
        }
        if (off.name.includes('佐々成政') || off.id.includes('sassa')) {
          if (ownersSet.has('sassa')) {
            off.clanId = 'sassa';
            return;
          }
        }
        if (off.name.includes('吉川広家') || off.id.includes('kikkawa_hiroie')) {
          if (ownersSet.has('mori')) { off.clanId = 'mori'; off.isDaimyo = false; return; }
        }
        if (off.name.includes('高橋紹運') || off.name.includes('立花道雪') || off.id.includes('takahashi_shoun') || off.id.includes('tachibana_dosetsu')) {
          if (ownersSet.has('otomo')) { off.clanId = 'otomo'; off.isDaimyo = false; return; }
        }
        if (off.name.includes('相良頼房') || off.id.includes('sagara')) {
          if (ownersSet.has('shimazu')) { off.clanId = 'shimazu'; off.isDaimyo = false; return; }
        }
        if (off.name.includes('島左近') || off.name.includes('筒井順慶')) {
          if (ownersSet.has('tsutsui')) { off.clanId = 'tsutsui'; return; }
          if (ownersSet.has('toyotomi')) { off.clanId = 'toyotomi'; off.isDaimyo = false; return; }
        }
      }

      // 1587年 秀吉の九州征伐: 豊臣親征軍・島津軍・大友軍・龍造寺軍
      if (String(scen.id) === '1587' || year === 1587) {
        const toyoRetainers = [
          '秀吉', '秀長', '秀次', '黒田官兵衛', '黒田孝高', '黒田長政', '立花宗茂', '加藤清正', '福島正則',
          '浅野長政', '石田三成', '大谷吉継', '蒲生氏郷', '蜂須賀家政', '前田利家', '堀秀政', '小早川隆景',
          '小西行長', '細川藤孝', '細川幽斎', '細川忠興', '長連龍', '前田利長', '丹羽長重', '前田玄以',
          '山名豊国', '金森可重', '加藤嘉明', '仙石秀久', '伊東祐兵', '脇坂安治'
        ];
        if (toyoRetainers.some(kw => off.name.includes(kw) || off.id.includes(kw))) {
          if (ownersSet.has('toyotomi')) {
            off.clanId = 'toyotomi';
            off.isDaimyo = false;
            return;
          }
        }
        const hojoRetainers = ['北条氏邦', '北条氏規', '千葉邦胤', '千葉重胤', '成田氏長', '成田長親'];
        if (hojoRetainers.some(kw => off.name.includes(kw) || off.id.includes(kw))) {
          if (ownersSet.has('hojo')) {
            off.clanId = 'hojo';
            off.isDaimyo = false;
            return;
          }
        }
        const shimazuRetainers = ['島津義久', '島津義弘', '島津家久', '島津歳久', '新納忠元', '山田有栄'];
        if (shimazuRetainers.some(kw => off.name.includes(kw) || off.id.includes(kw))) {
          if (ownersSet.has('shimazu')) {
            off.clanId = 'shimazu';
            return;
          }
        }
        const otomoRetainers = ['大友宗麟', '大友義統'];
        if (otomoRetainers.some(kw => off.name.includes(kw) || off.id.includes(kw))) {
          if (ownersSet.has('otomo')) {
            off.clanId = 'otomo';
            return;
          }
        }
        const ryuzojiRetainers = ['鍋島直茂', '龍造寺政家'];
        if (ryuzojiRetainers.some(kw => off.name.includes(kw) || off.id.includes(kw))) {
          if (ownersSet.has('ryuzoji')) {
            off.clanId = 'ryuzoji';
            return;
          }
        }
        const tokuRetainers = ['徳川家康', '本多忠勝', '酒井忠次', '榊原康政', '井伊直政', '鳥居元忠', '大久保忠世'];
        if (tokuRetainers.some(kw => off.name.includes(kw) || off.id.includes(kw))) {
          if (ownersSet.has('tokugawa')) {
            off.clanId = 'tokugawa';
            return;
          }
        }
      }

      // 1590年 小田原征伐: 豊臣政権下の大名・配下
      if (String(scen.id) === '1590' || year === 1590) {
        const toyoRetainers = [
          '秀吉', '秀長', '秀次', '前田利家', '前田利長', '堀秀政', '丹羽長重', '宇喜多秀家', '黒田官兵衛', '黒田孝高', '黒田長政',
          '小早川隆景', '立花宗茂', '加藤清正', '小西行長', '鍋島直茂', '浅野長政', '石田三成', '大谷吉継', '蒲生氏郷',
          '福島正則', '蜂須賀家政', '蜂須賀正勝', '山内一豊', '脇坂安治', '加藤嘉明', '片桐且元', '木村重成',
          '細川藤孝', '細川幽斎', '細川忠興', '長連龍', '相馬義胤', '伊東祐兵', '山名豊国', '前田玄以'
        ];
        if (toyoRetainers.some(kw => off.name.includes(kw) || off.id.includes(kw))) {
          if (ownersSet.has('toyotomi')) {
            off.clanId = 'toyotomi';
            off.isDaimyo = false;
            return;
          }
        }
        const hojoRetainers = ['北条氏直', '北条氏政', '北条氏照', '北条氏邦', '北条氏規', '成田氏長', '成田長親', '千葉重胤'];
        if (hojoRetainers.some(kw => off.name.includes(kw) || off.id.includes(kw))) {
          if (ownersSet.has('hojo')) {
            off.clanId = 'hojo';
            off.isDaimyo = false;
            return;
          }
        }
        const tokuRetainers = ['徳川家康', '本多忠勝', '酒井忠次', '榊原康政', '井伊直政', '鳥居元忠', '大久保忠世'];
        if (tokuRetainers.some(kw => off.name.includes(kw) || off.id.includes(kw))) {
          if (ownersSet.has('tokugawa')) {
            off.clanId = 'tokugawa';
            return;
          }
        }
        if (off.name.includes('島左近')) {
          if (ownersSet.has('toyotomi')) { off.clanId = 'toyotomi'; off.isDaimyo = false; return; }
        }
      }

      // 1592年 文禄の役: 名護屋集結・全国大名
      if (String(scen.id) === '1592' || year === 1592) {
        const toyoRetainers = [
          '秀吉', '秀次', '小西行長', '加藤清正', '黒田官兵衛', '黒田孝高', '黒田長政', '小早川隆景',
          '立花宗茂', '福島正則', '浅野長政', '石田三成', '大谷吉継', '蒲生氏郷', '蜂須賀家政',
          '増田長盛', '前田玄以', '長束正家', '鍋島直茂', '大友義統', '細川藤孝', '細川幽斎', '細川忠興',
          '長連龍', '相馬義胤', '伊東祐兵', '山内一豊', '田中吉政', '藤堂高虎', '京極高次', '小出吉政',
          '池田輝政', '加藤嘉明', '中村一氏', '石川数正', '脇坂安治', '仙石秀久'
        ];
        if (toyoRetainers.some(kw => off.name.includes(kw) || off.id.includes(kw))) {
          if (ownersSet.has('toyotomi')) {
            off.clanId = 'toyotomi';
            off.isDaimyo = false;
            return;
          }
        }
        const tokuRetainers = [
          '徳川家康', '徳川秀忠', '本多忠勝', '榊原康政', '井伊直政', '鳥居元忠', '大久保忠隣',
          '平岩親吉', '酒井忠次'
        ];
        if (tokuRetainers.some(kw => off.name.includes(kw) || off.id.includes(kw))) {
          if (ownersSet.has('tokugawa')) {
            off.clanId = 'tokugawa';
            return;
          }
        }
        const maedaRetainers = ['前田利家', '前田利長'];
        if (maedaRetainers.some(kw => off.name.includes(kw) || off.id.includes(kw))) {
          if (ownersSet.has('maeda')) {
            off.clanId = 'maeda';
            return;
          }
        }
        if (off.name.includes('島左近')) {
          if (ownersSet.has('toyotomi')) { off.clanId = 'toyotomi'; off.isDaimyo = false; return; }
        }
      }

      // 1600年 関ヶ原の戦い: 西軍 (ishida) と東軍 (tokugawa)
      if (String(scen.id) === '1600' || year === 1600) {
        const westRetainers = [
          '石田三成', '大谷吉継', '島左近', '宇喜多秀家', '小早川秀秋', '織田秀信', '前田玄以', '増田長盛',
          '長束正家', '安国寺恵瓊', '小西行長', '平塚為広', '戸田重政', '木下頼継', '立花宗茂'
        ];
        if (westRetainers.some(kw => off.name.includes(kw) || off.id.includes(kw))) {
          if (ownersSet.has('ishida')) {
            off.clanId = 'ishida';
            off.isDaimyo = false;
            return;
          }
        }
        const eastRetainers = [
          '徳川家康', '徳川秀忠', '本多忠勝', '井伊直政', '榊原康政', '鳥居元忠', '大久保忠隣',
          '福島正則', '山内一豊', '中村一氏', '田中吉政', '堀秀治', '細川藤孝', '細川幽斎', '細川忠興',
          '京極高次', '浅野幸長', '黒田長政', '藤堂高虎', '北条氏規', '成田長親', '山名豊国',
          '諏訪頼忠', '諏訪頼水', '木俣守勝'
        ];
        if (eastRetainers.some(kw => off.name.includes(kw) || off.id.includes(kw))) {
          if (off.name.includes('黒田') && ownersSet.has('kuroda')) { off.clanId = 'kuroda'; return; }
          if (off.name.includes('加藤清正') && ownersSet.has('kato')) { off.clanId = 'kato'; return; }
          if (off.name.includes('鍋島') && ownersSet.has('nabeshima')) { off.clanId = 'nabeshima'; return; }
          if (ownersSet.has('tokugawa')) {
            off.clanId = 'tokugawa';
            off.isDaimyo = false;
            return;
          }
        }
        if (off.name.includes('相馬義胤')) {
          if (ownersSet.has('uesugi')) { off.clanId = 'uesugi'; off.isDaimyo = false; return; }
          if (ownersSet.has('tokugawa')) { off.clanId = 'tokugawa'; off.isDaimyo = false; return; }
        }
        if (off.name.includes('淀殿') || off.name.includes('片桐且元') || off.name.includes('大野治長')) {
          if (ownersSet.has('toyotomi')) {
            off.clanId = 'toyotomi';
            return;
          }
        }
        if (this.isHideyoriOfficer(off) && ownersSet.has('toyotomi') && !this.isServingLandedClan(off, ownersSet)) {
          off.clanId = 'toyotomi';
          return;
        }
      }

      // 1614年 大坂の陣: 諸大名の名簿整理
      if (String(scen.id) === '1614' || year === 1614) {
        if (off.name.includes('鍋島直茂') || off.name.includes('鍋島勝茂') || off.id.includes('nabeshima')) {
          if (ownersSet.has('nabeshima')) { off.clanId = 'nabeshima'; return; }
        }
        if (off.name.includes('黒田長政') || off.id.includes('kuroda')) {
          if (ownersSet.has('kuroda')) { off.clanId = 'kuroda'; return; }
        }
        if (off.name.includes('織田信雄') || off.id.includes('oda_nobukatsu')) {
          if (ownersSet.has('owari')) { off.clanId = 'owari'; off.isDaimyo = false; return; }
          if (ownersSet.has('tokugawa')) { off.clanId = 'tokugawa'; off.isDaimyo = false; return; }
        }
        if (off.name.includes('丹羽長重') || off.name.includes('相馬義胤') || off.name.includes('最上義光') || off.name.includes('鮭延秀綱')) {
          if (ownersSet.has('tokugawa')) { off.clanId = 'tokugawa'; off.isDaimyo = false; return; }
        }
      }

      // 1570年 信長包囲網
      if (String(scen.id) === '1570' || year === 1570) {
        const odaMembers = ['秀吉', '秀長', '光秀', '勝家', '長秀', '利家', '一益', '信忠', '恒興', '浅野長政', '仙石秀久', '山内一豊'];
        if (odaMembers.some(kw => off.name.includes(kw) || off.id.includes(kw))) {
          if (ownersSet.has('oda')) { off.clanId = 'oda'; return; }
        }
        if (off.name.includes('家康') || off.name.includes('忠勝') || off.name.includes('直政') || off.name.includes('忠次') || off.name.includes('康政')) {
          if (ownersSet.has('tokugawa')) { off.clanId = 'tokugawa'; return; }
        }
      }

      // 1560年 桶狭間の戦い
      if (String(scen.id) === '1560' || year === 1560) {
        if (off.name.includes('家康') || off.name.includes('元康') || off.name.includes('忠次') || off.name.includes('忠勝') || off.name.includes('元忠') || off.name.includes('正信')) {
          if (ownersSet.has('imagawa')) { off.clanId = 'imagawa'; off.isDaimyo = false; return; }
        }
        const odaMembers = ['勝家', '長秀', '利家', '秀吉', '藤吉郎', '信盛', '恒興', '秀長', '一豊'];
        if (odaMembers.some(kw => off.name.includes(kw) || off.id.includes(kw))) {
          if (ownersSet.has('oda')) { off.clanId = 'oda'; return; }
        }
      }
"""

new_text = text[:idx_start] + new_block + text[idx_end:]

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Successfully replaced affiliations block in js/app.js!")
