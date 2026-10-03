import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start = 1437
end = 2012

for i in range(start, min(end, len(lines))):
    print(f"{i+1}: {lines[i]}", end='')
