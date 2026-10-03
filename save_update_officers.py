with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('updateActiveOfficers() {')
sub = text[idx:idx+2500]

with open('update_active_officers_body.txt', 'w', encoding='utf-8') as f:
    f.write(sub)

print("Saved updateActiveOfficers body.")
