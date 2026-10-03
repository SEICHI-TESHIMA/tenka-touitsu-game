with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.splitlines()
out = []
for i, line in enumerate(lines):
    if 'ronin' in line.lower() or '浪人' in line:
        out.append(f"app.js Line {i+1}: {line[:120]}")

with open('ronin_logic_in_app.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(out))

print(f"Found {len(out)} lines matching ronin in app.js")
