with open('truly_jodai_scenarios_utf8.txt', 'r', encoding='utf-8') as f:
    text = f.read()

out = []
scen_blocks = text.split("Scenario ")
for b in scen_blocks:
    if any(s in b for s in ['1866', '1853', '1837', '1702', '1651']):
        lines = b.splitlines()
        out.append(f"=== Scenario {lines[0]} ===")
        for l in lines[1:]:
            out.append(l)

with open('edo_jodai_detail_utf8.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(out))

print("Saved edo_jodai_detail_utf8.txt")
