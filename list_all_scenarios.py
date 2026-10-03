import re

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Find all scenarios: id, year, title
scenarios = []
for m in re.finditer(r'\{\s*"id":\s*"([^"]+)",\s*"year":\s*(\d+),\s*"title":\s*"([^"]+)"', text):
    scenarios.append((m.group(1), m.group(2), m.group(3)))

print(f"Total scenarios found: {len(scenarios)}")
for s in scenarios:
    print(f"ID: {s[0]}, Year: {s[1]}, Title: {s[2]}")
