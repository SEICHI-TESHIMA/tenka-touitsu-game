import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('sengoku_edo_unlanded_utf8.txt', 'r', encoding='utf-8') as f:
    text = f.read()

keywords = ['津軽', '小西', '蜂須賀', '細川', '長連龍', '千葉', '島左近', '筒井', '立花', '黒田', '加藤', '木曾', '小笠原', '山名', '伊東', '秋田', '佐々', '宇喜多', '鍋島', '浅野', '蒲生', '直江', '真田']

scens = text.split('=======================================================')
for s in scens:
    if any(k in s for k in ['[1546]', '[1560]', '[1570]', '[1582]', '[1584]', '[1587]', '[1590]', '[1592]', '[1600]', '[1614]', '[1637]']):
        lines = s.strip().split('\n')
        print(lines[0])
        for l in lines[1:]:
            if any(kw in l for kw in keywords):
                print(' ', l.strip())

