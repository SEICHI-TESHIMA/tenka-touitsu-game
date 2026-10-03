with open('gov_coverage_utf8.txt', 'r', encoding='utf-8') as f:
    text = f.read()

for line in text.splitlines():
    if line.startswith('Scenario '):
        print(line)
