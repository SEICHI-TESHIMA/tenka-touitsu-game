# -*- coding: utf-8 -*-
"""
OFFICERS_MASTER と historical_jodai.js 内の全武将を徹底調査。
1. 括弧つき名前
2. 没年・生年の異常（1900年以降など）
3. 名字だけ・総称・役職だけの人物
4. 架空・怪しい人物（真田十勇士の架空人物、架空の武将など）
5. 列伝の長さと内容（手抜き感のある一言コメントの全件抽出）
"""
import json
import re

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

def extract_js_var(var_name, text):
    start = text.find(var_name + ' = [')
    if start == -1:
        start = text.find(var_name + ' = {')
        open_char, close_char = '{', '}'
    else:
        open_char, close_char = '[', ']'
    if start == -1:
        return None
    
    start_content = start + len(var_name + ' = ')
    count = 0
    end = -1
    for i in range(start_content, len(text)):
        if text[i] == open_char:
            count += 1
        elif text[i] == close_char:
            count -= 1
            if count == 0:
                end = i + 1
                break
    if end != -1:
        return json.loads(text[start_content:end])
    return None

officers = extract_js_var('window.OFFICERS_MASTER', text)

with open('officer_full_audit.txt', 'w', encoding='utf-8') as out:
    out.write(f"=== 全武将詳細監査 (計 {len(officers)} 名) ===\n\n")

    # 1. 生没年の異常 (近代・現代)
    modern = [o for o in officers if (o.get('birthYear') or 0) >= 1868 or (o.get('deathYear') or 0) > 1912]
    out.write(f"--- 1. 近代・現代人物 ({len(modern)} 名) ---\n")
    for o in modern:
        out.write(f"  [{o['id']}] {o['name']} ({o.get('birthYear')}-{o.get('deathYear')}): {o.get('lore')}\n")

    # 2. 役職・総称・架空の疑い
    generic_words = ['酋長', '豪族', '郡司', '国司', '商人', '忍者', '代官', '海賊', '土豪', '親王', '天皇', '法皇', '上皇', '女院', '一族', '家臣', '門徒', '農民']
    generic_matches = []
    for o in officers:
        name = o.get('name', '')
        if any(w in name for w in generic_words):
            generic_matches.append(o)
    out.write(f"\n--- 2. 総称・役職・皇族など ({len(generic_matches)} 名) ---\n")
    for o in generic_matches:
        out.write(f"  [{o['id']}] {o['name']} ({o.get('birthYear')}-{o.get('deathYear')}): {o.get('lore')}\n")

    # 3. 括弧つき名前（(祖)、(三代)、通称など）
    paren_names = [o for o in officers if '(' in o.get('name', '') or '（' in o.get('name', '')]
    out.write(f"\n--- 3. 括弧つき名前 ({len(paren_names)} 名) ---\n")
    for o in paren_names:
        out.write(f"  [{o['id']}] {o['name']} ({o.get('birthYear')}-{o.get('deathYear')}): {o.get('lore')}\n")

    # 4. ID に succ, proto, dummy, fake 等を含む武将
    generated_ids = [o for o in officers if any(w in o['id'] for w in ['succ', 'proto', 'dummy', 'fake', 'gen_'])]
    out.write(f"\n--- 4. 自動生成・プロトタイプと思われる武将 ({len(generated_ids)} 名) ---\n")
    for o in generated_ids[:50]:
        out.write(f"  [{o['id']}] {o['name']} ({o.get('birthYear')}-{o.get('deathYear')}): {o.get('lore')}\n")

    # 5. 列伝長調査
    lores = [(o, len(o.get('lore', ''))) for o in officers]
    lores.sort(key=lambda x: x[1])
    out.write(f"\n--- 5. 最も列伝が短い武将 (下位40名) ---\n")
    for o, l_len in lores[:40]:
        out.write(f"  [{o['id']}] {o['name']} (文字数: {l_len}): \"{o.get('lore')}\"\n")

    # 6. 列伝長分布
    len_0_20 = len([o for o, l in lores if l <= 20])
    len_21_40 = len([o for o, l in lores if 21 <= l <= 40])
    len_41_60 = len([o for o, l in lores if 41 <= l <= 60])
    len_61_80 = len([o for o, l in lores if 61 <= l <= 80])
    len_81_plus = len([o for o, l in lores if l > 80])
    out.write(f"\n--- 6. 列伝長分布 ---\n")
    out.write(f"  <= 20文字: {len_0_20}\n")
    out.write(f"  21-40文字: {len_21_40}\n")
    out.write(f"  41-60文字: {len_41_60}\n")
    out.write(f"  61-80文字: {len_61_80}\n")
    out.write(f"  > 80文字: {len_81_plus}\n")

print("Done audit script.")
