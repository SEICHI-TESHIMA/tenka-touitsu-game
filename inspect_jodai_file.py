with open('js/historical_jodai.js', 'r', encoding='utf-8') as f:
    text = f.read()

print("Length of historical_jodai.js:", len(text))
for line in text.splitlines()[:30]:
    print(line)
