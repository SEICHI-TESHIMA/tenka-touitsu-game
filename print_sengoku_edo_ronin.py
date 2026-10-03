with open('all_scenarios_ronin_check_utf8.txt', 'r', encoding='utf-8') as f:
    text = f.read()

out = []
scen_blocks = text.split("Scenario ")
for b in scen_blocks[1:]:
    header = b.splitlines()[0]
    year = int(header.split('(')[1].split()[0])
    if year >= 1546:
        lines = b.splitlines()
        out.append(f"=== {lines[0]} ===")
        for l in lines[1:]:
            out.append(l)

with open('sengoku_edo_ronin_detail_utf8.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(out))

print("Saved sengoku_edo_ronin_detail_utf8.txt")
