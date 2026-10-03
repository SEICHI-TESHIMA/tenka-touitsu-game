# -*- coding: utf-8 -*-
"""
史実リサーチに基づく包括的アップデートスクリプト。
1. 架空・非実在武将（真田十勇士・総称武将など24名）の削除
2. 実在史実武将（真田家臣、平安受領、中世戦国城代、江戸藩主など）の追加
3. 全34シナリオの城代（233箇所）の完全解消
4. 全武将列伝の全面刷新・充実（手抜き感の完全解消・100〜160文字）
5. 検証（城代数0、架空武将0、短列伝0）
"""
import json
import re
import shutil
import os

print("Starting comprehensive updates...")

# 1. バックアップ作成
shutil.copyfile('js/data.js', 'js/data.js.bak_hist_research')
shutil.copyfile('js/app.js', 'js/app.js.bak_hist_research')
if os.path.exists('js/historical_jodai.js'):
    shutil.copyfile('js/historical_jodai.js', 'js/historical_jodai.js.bak_hist_research')

print("Backups created.")
