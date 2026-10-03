# -*- coding: utf-8 -*-
import re

suspect_names = [
    '猿飛佐助',
    '霧隠才蔵',
    '三好清海',
    '三好伊三',
    '穴山小助',
    '由利鎌之助',
    '筧十蔵',
    '海野六郎',
    '根津甚八',
    '望月六郎',
    '豊後国司大友氏',
    '蝦夷酋長',
    '薩摩郡司',
    'コシャマイン先祖',
    '大隅豪族'
]

files = ['js/data.js', 'js/app.js', 'js/historical_jodai.js']

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"=== Checking {fpath} for names ===")
    for sname in suspect_names:
        matches = len(re.findall(re.escape(sname), content))
        if matches > 0:
            print(f"  {sname}: {matches} matches")

