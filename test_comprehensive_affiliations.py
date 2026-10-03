import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('window.OFFICERS_MASTER = [')
end_idx = text.find('\n];', start_idx) + 2
officers = json.loads(text[start_idx + len('window.OFFICERS_MASTER = '):end_idx])

start_idx_scen = text.find('window.SCENARIOS_DATA = [')
end_idx_scen = text.find('\n];', start_idx_scen) + 2
scenarios = json.loads(text[start_idx_scen + len('window.SCENARIOS_DATA = '):end_idx_scen])

idx_gov = text.find('window.SCENARIO_HISTORICAL_GOVERNORS = {')
end_idx_gov = text.find('\n};', idx_gov) + 3
hist_govs = json.loads(text[idx_gov + len('window.SCENARIO_HISTORICAL_GOVERNORS = '):end_idx_gov-1])

# Build comprehensive affiliation mapping
def simulate_new_affiliations(scen):
    sid = str(scen['id'])
    year = scen['year']
    owners_map = scen.get('owners', {})
    owners_set = set(owners_map.values())
    gov_map = hist_govs.get(sid, {})
    # reverse gov map: officerId -> prov
    officer_to_gov_prov = {oid: p for p, oid in gov_map.items()}
    
    alive = [o for o in officers if (o.get('birthYear', 9999) <= year <= o.get('deathYear', -9999))]
    
    court_clans = set(['heian_court', 'kamakura_shogunate', 'muromachi_shogunate', 'imperial', 'meiji_court'])
    
    ronin = []
    placed = []
    
    for o in alive:
        oid = o['id']
        name = o.get('name', '')
        clan = o.get('clanId')
        prov = o.get('defaultProv')
        
        # 1. Assigned governor of a province on the map
        if oid in officer_to_gov_prov:
            g_prov = officer_to_gov_prov[oid]
            prov_owner = owners_map.get(g_prov)
            if prov_owner and prov_owner in owners_set:
                placed.append((o, prov_owner, f"Governor of {g_prov}"))
                continue
                
        # 2. Existing landed clan
        if clan in owners_set:
            placed.append((o, clan, "Landed Clan"))
            continue
            
        # 3. Clan aliases
        alias_map = {
            'matsudaira': 'tokugawa',
            'shogunate': 'tokugawa',
            'shonai': 'tokugawa',
            'kuwana': 'tokugawa',
            'makino': 'tokugawa',
            'fukuoka_kuroda': 'kuroda',
            'kuroda': 'fukuoka_kuroda',
            'kumamoto_hosokawa': 'hosokawa',
            'hosokawa': 'kumamoto_hosokawa',
            'ii': 'meiji',
            'chiba': 'hojo',
            'kunohe': 'nanbu',
            'tsugaru': 'nanbu' if year < 1585 else 'tsugaru',
        }
        
        target_clan = None
        
        # Check alias
        if clan in alias_map and alias_map[clan] in owners_set:
            target_clan = alias_map[clan]
        elif clan == 'tokugawa' and 'matsudaira' in owners_set:
            target_clan = 'matsudaira'
            
        # 4. Historical Bakumatsu Retainers
        if not target_clan and year >= 1837:
            # Tokugawa Bakumatsu vassals & Fudai Daimyos
            tokugawa_bakumatsu_names = [
                '小栗忠順', '小栗上野介', '板倉勝静', '山田方谷', '大久保忠礼', '林忠崇', '阿部正方', '阿部正弘',
                '酒井忠惇', '酒井忠篤', '松平定敬', '松平定法', '松平頼種', '小笠原忠忱', '中川久成', '前田利同',
                '南部信順', '楢山佐渡', '立見鑑三郎', '河井継之助', '榎本武揚', '大鳥圭介', '人見勝太郎',
                '中島登', '春日左衛門', '島田魁', '酒井吉之丞', '伴百悦', '真田幸教', '真田幸民', '真田幸貫',
                '勝海舟', '福沢諭吉', '近藤勇', '土方歳三', '沖田総司', '斎藤一', '永倉新八'
            ]
            if (any(kw in name for kw in tokugawa_bakumatsu_names) or 'sanada' in oid) and 'tokugawa' in owners_set:
                target_clan = 'tokugawa'
                
            # Satsuma
            satsuma_names = ['西郷隆盛', '大久保利通', '小松帯刀', '黒田清隆', '桐野利秋', '大山巌', '伊地知正治', '樺山資紀', '島津久光', '島津忠義']
            if any(kw in name for kw in satsuma_names):
                if 'shimazu' in owners_set: target_clan = 'shimazu'
                elif 'meiji' in owners_set: target_clan = 'meiji'
                
            # Choshu
            choshu_names = ['木戸孝允', '桂小五郎', '高杉晋作', '大村益次郎', '伊藤博文', '井上馨', '山田顕義', '山縣有朋', '品川弥二郎', '世良修蔵', '久坂玄瑞', '吉田松陰']
            if any(kw in name for kw in choshu_names):
                if 'mori' in owners_set: target_clan = 'mori'
                elif 'meiji' in owners_set: target_clan = 'meiji'
                
            # Tosa
            tosa_names = ['坂本龍馬', '中岡慎太郎', '板垣退助', '後藤象二郎', '武市半平太', '岡田以蔵']
            if any(kw in name for kw in tosa_names):
                if 'tosa' in owners_set: target_clan = 'tosa'
                elif 'meiji' in owners_set: target_clan = 'meiji'
                
            # Hosokawa / Kumamoto
            if '細川' in name or 'hosokawa' in oid:
                if 'kumamoto_hosokawa' in owners_set: target_clan = 'kumamoto_hosokawa'
                elif 'hosokawa' in owners_set: target_clan = 'hosokawa'
                elif 'meiji' in owners_set: target_clan = 'meiji'
                
            # Kuroda / Fukuoka
            if '黒田' in name or 'kuroda' in oid:
                if 'fukuoka_kuroda' in owners_set: target_clan = 'fukuoka_kuroda'
                elif 'kuroda' in owners_set: target_clan = 'kuroda'
                elif 'meiji' in owners_set: target_clan = 'meiji'
                
        # 5. Sengoku Retainers (1546-1614)
        if not target_clan and 1546 <= year <= 1614:
            # Toyotomi Retainers (from 1582)
            if year >= 1582 and 'toyotomi' in owners_set:
                toyo_keys = [
                    '秀吉', '秀長', '秀次', '三成', '吉継', '長政', '長盛', '玄以', '正家', '正則', '清正',
                    '行長', '重成', '嘉明', '秀久', '一豊', '吉政', '一氏', '嘉隆', '且元', '安治',
                    '家政', '親正', '長康', '継潤', '元続', '頼隆', '吉政', '氏郷', '長秀', '重成',
                    '大野治長', '淀殿'
                ]
                if any(kw in name for kw in toyo_keys) or clan == 'toyotomi':
                    target_clan = 'toyotomi'
                    
            # Tokugawa Retainers
            if 'tokugawa' in owners_set:
                toku_keys = [
                    '家康', '秀忠', '忠勝', '康政', '直政', '忠次', '元忠', '忠世', '忠隣', '正信',
                    '清成', '頼勝', '可重', '長安', '守勝', '親吉', '勝重', '氏勝', '忠輝'
                ]
                if any(kw in name for kw in toku_keys) or clan in ['tokugawa', 'matsudaira']:
                    target_clan = 'tokugawa'
            elif 'imagawa' in owners_set and year <= 1560:
                toku_keys = ['家康', '元康', '忠次', '忠勝', '元忠', '正信']
                if any(kw in name for kw in toku_keys) or clan in ['tokugawa', 'matsudaira']:
                    target_clan = 'imagawa'
                    
            # Oda Retainers
            if 'oda' in owners_set and year < 1582:
                oda_keys = ['秀吉', '秀長', '藤吉郎', '光秀', '勝家', '長秀', '利家', '一益', '恒興', '成政', '長可', '信忠', '信雄', '信孝']
                if any(kw in name for kw in oda_keys) or clan in ['oda', 'toyotomi', 'shibata', 'akechi', 'maeda']:
                    target_clan = 'oda'

        if target_clan:
            placed.append((o, target_clan, "Faction Rule"))
        elif o.get('id') in ['off_meiji_tenno', 'off_dm_meiji_1868'] or clan in court_clans:
            # Court figure - excluded from ronin
            pass
        else:
            ronin.append(o)
            
    return placed, ronin

# Test for 1866, 1860, 1853, 1600, 1582
for sid in ['1866', '1868', '1860', '1853', '1837', '1789', '1600', '1582']:
    scen = next(s for s in scenarios if str(s['id']) == sid)
    placed, ronin = simulate_new_affiliations(scen)
    print(f"\nScenario {sid} ({scen['year']} {scen.get('title')}) - Placed: {len(placed)}, Ronin: {len(ronin)}")
    if len(ronin) <= 20:
        print("  Remaining Ronin:")
        for r in ronin:
            print(f"    {r['id']:<28} {r['name']:<12} clan:{r.get('clanId'):<15} prov:{r.get('defaultProv')}")
