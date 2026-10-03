with open('all_scenarios_unlanded_utf8.txt', 'r', encoding='utf-8') as f:
    text = f.read()

out = []
scen_blocks = text.split("=== Scenario ")
for b in scen_blocks:
    if any(s in b for s in ['1837', '1853', '1860', '1866', '1868']):
        lines = b.splitlines()
        out.append("=== Scenario " + lines[0])
        for l in lines[1:]:
            out.append(l)

with open('bakumatsu_unlanded_detail_utf8.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(out))

print("Saved bakumatsu_unlanded_detail_utf8.txt")
