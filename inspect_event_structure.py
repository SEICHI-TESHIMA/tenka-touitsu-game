import sys

sys.stdout.reconfigure(encoding='utf-8')
with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find("id: 'kawagoe'")
if idx == -1:
    idx = text.find('kawagoe')
print(text[idx-50:idx+1500])
