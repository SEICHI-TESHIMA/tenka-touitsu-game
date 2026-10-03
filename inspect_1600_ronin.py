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

from test_comprehensive_affiliations import simulate_new_affiliations

scen_1600 = next(s for s in scenarios if str(s['id']) == '1600')
placed, ronin = simulate_new_affiliations(scen_1600)

print(f"Total ronin in 1600: {len(ronin)}")
# Group by clan
clan_counts = {}
for r in ronin:
    c = r.get('clanId', 'none')
    clan_counts[c] = clan_counts.get(c, 0) + 1

for c, count in sorted(clan_counts.items(), key=lambda x: -x[1]):
    sample = [r['name'] for r in ronin if r.get('clanId') == c][:5]
    print(f"  clan:{c:<18} count:{count:<3} sample: {', '.join(sample)}")
