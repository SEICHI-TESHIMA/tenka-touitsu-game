# -*- coding: utf-8 -*-
import sys, json
sys.stdout.reconfigure(encoding='utf-8')
with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()
start = text.find('window.SCENARIOS_DATA =') + len('window.SCENARIOS_DATA =')
end = text.find('window.CLAN_MASTER_DATA =', start)
body = text[start:end].strip()
last_b = max(body.rfind(']'), body.rfind('}'))
scenarios = json.loads(body[:last_b+1])
for s in scenarios:
    owners = set(s.get('owners', {}).values()) | set(p['id'] for p in s.get('playables', []))
    sid = s["id"]
    yr = s["year"]
    title = s["title"]
    n = len(owners)
    print(f"ID:{sid:5s} Year:{yr} Title:{title} Clans:{n}")
