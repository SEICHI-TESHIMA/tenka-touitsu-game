with open('js/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(1470, 1840):
    line = lines[i]
    if any(k in line for k in ['1560', '桶狭間', '1570', '1582', '1600', '1614', '徳川', '織田', '豊臣']):
        print(f"{i+1}: {line.strip()[:100]}")
