import sys

sys.stdout.reconfigure(encoding='utf-8')

try:
    with open('affiliations_body.txt', 'r', encoding='utf-16') as f:
        text = f.read()
except Exception:
    with open('affiliations_body.txt', 'r', encoding='utf-8') as f:
        text = f.read()

lines = text.splitlines()
print(f"Total lines in resolveOfficerAffiliations: {len(lines)}")
for i, l in enumerate(lines):
    if any(k in l for k in ['if', 'year', 'ownersSet', 'exactName', 'ronin', 'clanAlias']):
        print(f"Line {i+1438}: {l.strip()[:100]}")
