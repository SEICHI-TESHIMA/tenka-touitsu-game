# -*- coding: utf-8 -*-
"""
全シナリオの城代発生国一覧を詳細出力し、
各時代・各勢力・各国の史実適格武将を一覧化する。
"""
import json

with open('scenarios_jodai_scan.txt', 'r', encoding='utf-8') as f:
    text = f.read()

print("Analyzing scenarios jodai...")
