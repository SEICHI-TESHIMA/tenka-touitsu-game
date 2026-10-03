with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re

m = re.search(r'getHistoricalEventsMaster\(\)\s*\{(.*?)\n\s*\}\s*\n\s*checkHistoricalEvents', text, re.DOTALL)
if m:
    body = m.group(1)
    event_blocks = re.findall(r"id:\s*'([^']+)'[,\s]+scenarioId:\s*'([^']+)'[,\s]+title:\s*'([^']+)'", body)
    with open('master_events_list.txt', 'w', encoding='utf-8') as out:
        out.write(f"Found {len(event_blocks)} events in getHistoricalEventsMaster:\n")
        for eid, scid, title in event_blocks:
            out.write(f"  id: {eid}, scenario: {scid}, title: {title}\n")
    print(f"Wrote {len(event_blocks)} events to master_events_list.txt")
else:
    print("Could not find getHistoricalEventsMaster")
