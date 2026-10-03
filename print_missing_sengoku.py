with open('missing_govs_analysis_utf8.txt', 'r', encoding='utf-8') as f:
    text = f.read()

out = []
scen_blocks = text.split("Scenario ")
for b in scen_blocks[1:]:
    header = b.splitlines()[0]
    year = int(header.split('(')[1].split()[0])
    if year >= 1546:
        out.append(f"=== {header} ===")
        for l in b.splitlines()[1:]:
            out.append(l)

with open('missing_sengoku_detail_utf8.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(out))

print("Saved missing_sengoku_detail_utf8.txt")
