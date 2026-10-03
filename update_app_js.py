import sys
import json
from officer_merge_definitions import OFFICER_MERGES

sys.stdout.reconfigure(encoding='utf-8')

# Build merge_id_map
merge_id_map = {}
for canon_id, merged_list, _, desc in OFFICER_MERGES:
    for mid in merged_list:
        merge_id_map[mid] = canon_id

with open('js/app.js', 'r', encoding='utf-8') as f:
    app_text = f.read()

# 1. Add window.OFFICER_ID_ALIASES at the top
alias_json = json.dumps(merge_id_map, ensure_ascii=False, indent=2)
alias_code = f"// 重複武将統合IDエイリアスマップ (後方互換・セーブデータ・動的参照対応)\nwindow.OFFICER_ID_ALIASES = {alias_json};\n\n"

if 'window.OFFICER_ID_ALIASES =' not in app_text:
    # Insert right before class Game or top level
    insert_pos = app_text.find('class Game {')
    if insert_pos != -1:
        app_text = app_text[:insert_pos] + alias_code + app_text[insert_pos:]
    else:
        app_text = alias_code + app_text
    print("Added window.OFFICER_ID_ALIASES to app.js")

# 2. Update getCanonicalName
old_canon_block = """      if (clean === '羽柴秀吉' || clean === '豊臣秀吉') return '秀吉';
      if (clean === '羽柴秀長' || clean === '豊臣秀長') return '秀長';
      if (clean === '羽柴秀次' || clean === '豊臣秀次') return '秀次';
      if (clean === '松平元康' || clean === '徳川家康') return '家康';
      if (clean === '黒田官兵衛' || clean === '黒田孝高' || clean === '黒田如水') return '黒田官兵衛';"""

new_canon_block = """      if (clean === '羽柴秀吉' || clean === '豊臣秀吉') return '秀吉';
      if (clean === '羽柴秀長' || clean === '豊臣秀長') return '秀長';
      if (clean === '羽柴秀次' || clean === '豊臣秀次') return '秀次';
      if (clean === '松平元康' || clean === '徳川家康') return '家康';
      if (clean === '黒田官兵衛' || clean === '黒田孝高' || clean === '黒田如水') return '黒田官兵衛';
      if (clean === '細川藤孝' || clean === '細川幽斎') return '細川藤孝';
      if (clean === '片倉景綱' || clean === '片倉小十郎') return '片倉景綱';
      if (clean === '穴山信君' || clean === '穴山梅雪') return '穴山信君';
      if (clean === '佐々木広綱' || clean === '佐佐木広綱') return '佐々木広綱';
      if (clean === '後白河天皇' || clean === '後白河院') return '後白河天皇';
      if (clean === '後鳥羽上皇' || clean === '後鳥羽天皇') return '後鳥羽上皇';
      if (clean === '後嵯峨上皇' || clean === '後嵯峨天皇') return '後嵯峨上皇';
      if (clean === '松平秀忠' || clean === '徳川秀忠') return '徳川秀忠';
      if (clean === '松平家光' || clean === '徳川家光') return '徳川家光';
      if (clean === '松平家綱' || clean === '徳川家綱') return '徳川家綱';
      if (clean === '松平綱吉' || clean === '徳川綱吉') return '徳川綱吉';
      if (clean === '松平家宣' || clean === '徳川家宣') return '徳川家宣';
      if (clean === '松平治郷' || clean === '松平不昧') return '松平治郷';"""

if old_canon_block in app_text:
    app_text = app_text.replace(old_canon_block, new_canon_block)
    print("Updated getCanonicalName in app.js")
else:
    print("Warning: old_canon_block not matched exactly")

# 3. Update showOfficerDetailModal to resolve alias
old_modal_lookup = """    const off = typeof offOrId === 'string'
      ? (this.activeOfficers || []).find(o => o.id === offOrId) || (this.officers || []).find(o => o.id === offOrId) || (window.OFFICERS_MASTER || []).find(o => o.id === offOrId) || { name: offOrId }
      : offOrId;"""

new_modal_lookup = """    const targetId = typeof offOrId === 'string' ? ((window.OFFICER_ID_ALIASES && window.OFFICER_ID_ALIASES[offOrId]) || offOrId) : null;
    const off = typeof offOrId === 'string'
      ? (this.activeOfficers || []).find(o => o.id === targetId || o.id === offOrId) || (this.officers || []).find(o => o.id === targetId || o.id === offOrId) || (window.OFFICERS_MASTER || []).find(o => o.id === targetId || o.id === offOrId) || { name: offOrId }
      : offOrId;"""

if old_modal_lookup in app_text:
    app_text = app_text.replace(old_modal_lookup, new_modal_lookup)
    print("Updated showOfficerDetailModal in app.js")
else:
    print("Warning: old_modal_lookup not matched exactly")

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(app_text)
print("js/app.js updated successfully.")
