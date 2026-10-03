import sys
import re

sys.stdout.reconfigure(encoding='utf-8')
with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('getHistoricalEventsMaster()')
end_idx = text.find('checkHistoricalEvents()', idx)
chunk = text[idx:end_idx]

event_ids = re.findall(r"id:\s*['\"](\w+)['\"]", chunk)
titles = re.findall(r"title:\s*['\"]([^'\"]+)['\"]", chunk)
print('Interactive historical events count:', len(event_ids))
for eid, t in zip(event_ids, titles):
    print(f'  {eid}: {t}')
