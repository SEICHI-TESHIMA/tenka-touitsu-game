with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('switchScenario(')
sub = text[idx:idx+2500]

with open('switch_scenario_body.txt', 'w', encoding='utf-8') as f:
    f.write(sub)

print("Saved switchScenario body.")
