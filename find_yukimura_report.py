with open('detailed_ronin_report.txt', 'r', encoding='utf-8') as f:
    text = f.read()

for i, line in enumerate(text.splitlines()):
    if '真田幸村' in line:
        print(f"Line {i+1}: {line}")
