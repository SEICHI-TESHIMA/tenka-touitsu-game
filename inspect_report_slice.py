with open('detailed_ronin_report.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(410, 440):
    print(f"{i+1}: {lines[i]}", end='')
