import json
import re

with open('js/data.js', 'r', encoding='utf-8') as f:
    data_text = f.read()

with open('js/app.js', 'r', encoding='utf-8') as f:
    app_text = f.read()

# Parse OFFICERS_MASTER
start_idx = data_text.find('window.OFFICERS_MASTER = [')
end_idx = data_text.find('\n];', start_idx) + 2
officers_master = json.loads(data_text[start_idx + len('window.OFFICERS_MASTER = '):end_idx])

# Parse SCENARIOS_DATA
start_idx = data_text.find('window.SCENARIOS_DATA = [')
end_idx = data_text.find('\n];', start_idx) + 2
scenarios = json.loads(data_text[start_idx + len('window.SCENARIOS_DATA = '):end_idx])

# Extract resolveOfficerAffiliations method body from app.js
m_start = app_text.find('resolveOfficerAffiliations(scen) {')
m_end = app_text.find('getRosterLeaderName(ownerId) {', m_start)
method_code = app_text[m_start:m_end]

print("Found resolveOfficerAffiliations, length:", len(method_code))
