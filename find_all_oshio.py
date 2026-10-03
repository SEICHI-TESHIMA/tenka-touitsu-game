with open('js/data.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

out = []
seen_officers = set()
for i, line in enumerate(lines):
    if '大塩' in line:
        out.append(f"Line {i+1}: {line.rstrip()}")

with open('all_oshio_out_utf8.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(out))
print("Saved all_oshio_out_utf8.txt")
