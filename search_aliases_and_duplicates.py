import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'window\.OFFICERS_MASTER\s*=\s*(\[.*?\]);', text, re.DOTALL)
officers = json.loads(m.group(1))

queries = [
    '秀吉', '家康', '元康', '官兵衛', '孝高', '如水', '幸村', '信繁',
    '信玄', '晴信', '謙信', '景虎', '道三', '秀長', '秀次', '道誉',
    '義昭', '義輝', '光秀', '勝家', '利家', '宗茂', '統虎', '政宗'
]

lines = []
for q in queries:
    matched = [o for o in officers if q in o.get('name', '')]
    if len(matched) > 1:
        lines.append(f"=== Query: {q} ({len(matched)}) ===")
        for o in matched:
            lines.append(f"  {o.get('id')}: {o.get('name')} ({o.get('birthYear')}-{o.get('deathYear')}) clan:{o.get('clanId')}")

with open('search_aliases_out.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("Search completed.")
