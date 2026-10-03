import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('"off_tsugaru_tamenobu"')
if idx != -1:
    print("Found at:", idx)
    print(text[idx-50:idx+500])
