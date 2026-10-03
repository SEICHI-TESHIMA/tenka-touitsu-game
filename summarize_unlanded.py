with open('all_scenarios_unlanded_utf8.txt', 'r', encoding='utf-8') as f:
    text = f.read()

scen_blocks = text.split("=== Scenario ")
for b in scen_blocks[1:]:
    lines = b.splitlines()
    header = lines[0]
    count = len(lines) - 1
    print(header)
    # print up to 5 officers
    for l in lines[1:6]:
        print("  ", l.strip())
