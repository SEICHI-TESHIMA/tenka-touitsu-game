import re

with open('js/data.js', 'r', encoding='utf-8') as f:
    data_content = f.read()

with open('js/app.js', 'r', encoding='utf-8') as f:
    app_content = f.read()

print("--- DATA.JS SEARCH ---")
print("真田幸村 in data.js:", len(re.findall(r'真田幸村', data_content)))
for m in re.finditer(r'.{0,50}真田幸村.{0,50}', data_content):
    print("  data.js match:", m.group(0).strip())

print("\n大塩 in data.js:")
for m in re.finditer(r'.{0,30}大塩.{0,50}', data_content):
    print("  data.js match:", m.group(0).strip())

print("\n--- APP.JS SEARCH ---")
print("真田幸村 in app.js:", len(re.findall(r'真田幸村', app_content)))
for m in re.finditer(r'.{0,50}真田幸村.{0,50}', app_content):
    print("  app.js match:", m.group(0).strip())

print("\n大塩 in app.js:")
for m in re.finditer(r'.{0,30}大塩.{0,50}', app_content):
    print("  app.js match:", m.group(0).strip())
