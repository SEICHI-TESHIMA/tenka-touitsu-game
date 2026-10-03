with open('js/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'osakaRonin' in line or 'resolveOfficerAffiliations' in line or 'updateActiveOfficers' in line or '1866' in line:
        print(f"Line {i+1}: {line.strip()[:100]}")
