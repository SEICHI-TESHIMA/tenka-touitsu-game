with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.splitlines()
start = max(0, 8227 - 30)
end = min(len(lines), 8227 + 30)

for i in range(start, end):
    print(f"{i+1}: {lines[i]}")
