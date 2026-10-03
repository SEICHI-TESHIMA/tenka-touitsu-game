import json

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('window.OFFICERS_MASTER = [')
end_idx = text.find('\n];', start_idx) + 2
officers = json.loads(text[start_idx + len('window.OFFICERS_MASTER = '):end_idx])

print(f"Original officers count: {len(officers)}")

delete_ids = {
    'off_oshio_succ_2',        # 大塩門人(残党)
    'off_oshio_succ_3',        # 大塩良助 (架空)
    'off_edo_oshio_1855_12',   # 大塩平明 (架空)
    'off_edo_oshio_1890_13',   # 大塩平康 (架空)
    'off_edo_oshio_1925_14',   # 大塩平正 (架空)
    'off_oshio_succ_1',        # 大塩格之助 (重複)
    'off_sanada_yukimoto',     # 真田幸教 (重複)
}

new_officers = []
for o in officers:
    oid = o['id']
    if oid in delete_ids:
        print(f"Deleting officer: {oid} ({o.get('name')})")
        continue
        
    # Fix Sanada Yukinori (松代藩9代藩主 1835-1869)
    if oid == 'off_sanada_yukinori':
        o['birthYear'] = 1835
        o['deathYear'] = 1869
        o['clanId'] = 'tokugawa'
        o['defaultProv'] = 'north_shinano'
        o['comment'] = '松代藩9代藩主。佐久間象山を重用し洋式軍制を導入'
        o['lore'] = '松代藩主。佐久間象山を信任して開国・洋式調練を導入し、幕末動乱の中で藩論を率いた。'
        
    # Fix Sanada Yukitaka_m (真田幸民 1847-1903)
    if oid == 'off_sanada_yukitaka_m':
        o['clanId'] = 'tokugawa'
        o['defaultProv'] = 'north_shinano'
        o['comment'] = '松代藩10代（最後）の藩主。戊辰戦争で北越へ出兵'
        o['lore'] = '幸教の跡を継ぎ松代藩第十代藩主となる。戊辰戦争では官軍に従軍して北越戦争で戦った。'
        
    # Fix Sanada Yukitsura (真田幸貫 1791-1852)
    if oid == 'off_sanada_yukitsura':
        o['clanId'] = 'tokugawa'
        o['defaultProv'] = 'north_shinano'
        
    # Fix Sanada Yukimasa (真田幸正)
    if oid == 'off_sanada_yukimasa_mod':
        o['defaultProv'] = 'north_shinano'
        
    # Fix Sanada Ten Braves defaultProv
    braves = [
        'off_sarutobi_sasuke', 'off_kirigakure_saizo', 'off_miyoshi_seikai', 'off_miyoshi_isa',
        'off_anayama_kosuke', 'off_yuri_kamanosuke', 'off_kakei_juzo', 'off_unno_rokuro',
        'off_nezu_jinpachi', 'off_mochizuki_rokuro'
    ]
    if oid in braves:
        o['defaultProv'] = 'north_shinano'
        
    # Fix Kyogoku defaultProv
    if o.get('defaultProv') == 'oumi':
        o['defaultProv'] = 'north_omi'
        
    # Fix Ii defaultProv
    if o.get('defaultProv') == 'omi':
        o['defaultProv'] = 'north_omi'
        
    # Fix Satomi defaultProv
    if o.get('defaultProv') == 'awa_boso':
        o['defaultProv'] = 'awa_boshu'
        
    # Fix Dewa defaultProv
    if o.get('defaultProv') == 'dewa':
        o['defaultProv'] = 'uzen'
        
    # Fix Ryukyu defaultProv
    if o.get('defaultProv') == 'ryukyu':
        o['defaultProv'] = 'satsuma'
        
    new_officers.append(o)

print(f"New officers count: {len(new_officers)}")

# Write back to js/data.js
new_json_str = json.dumps(new_officers, ensure_ascii=False, indent=2)
new_text = text[:start_idx + len('window.OFFICERS_MASTER = ')] + new_json_str + text[end_idx:]

with open('js/data.js', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Updated js/data.js successfully.")
