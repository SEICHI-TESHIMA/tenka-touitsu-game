with open('edo_ronin_analysis_utf8.txt', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('*** Scenario [1866]')
print(text[idx:idx+2500])
