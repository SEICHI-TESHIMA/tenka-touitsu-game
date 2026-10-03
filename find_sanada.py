import re

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# search for shinano in relation to yukimura or sanada
matches = []
for i, line in enumerate(text.splitlines()):
    if '真田' in line or '幸村' in line:
        matches.append((i+1, line.strip()))

print(f"Total lines matching 真田 or 幸村: {len(matches)}")
with open('sanada_matches.txt', 'w', encoding='utf-8') as f:
    for num, line in matches:
        f.write(f"{num}: {line}\n")

print("Saved to sanada_matches.txt")
