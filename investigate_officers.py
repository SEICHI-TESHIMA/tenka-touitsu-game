# -*- coding: utf-8 -*-
import json
import re

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

def extract_js_var(var_name, text):
    start = text.find(var_name + ' = [')
    if start == -1:
        start = text.find(var_name + ' = {')
        open_char, close_char = '{', '}'
    else:
        open_char, close_char = '[', ']'
    if start == -1:
        return None
    
    start_content = start + len(var_name + ' = ')
    count = 0
    end = -1
    for i in range(start_content, len(text)):
        if text[i] == open_char:
            count += 1
        elif text[i] == close_char:
            count -= 1
            if count == 0:
                end = i + 1
                break
    if end != -1:
        return json.loads(text[start_content:end])
    return None

officers = extract_js_var('window.OFFICERS_MASTER', text)

with open('all_officers_list.txt', 'w', encoding='utf-8') as out:
    out.write(f"Total officers: {len(officers)}\n\n")
    # suspect patterns: '酋長', '氏', '郡司', '国司', 'dummy', 'temp', 'placeholder', 'proto', 'generic'
    suspects = []
    for o in officers:
        name = o.get('name', '')
        oid = o.get('id', '')
        clan = o.get('clanId', '')
        is_suspect = False
        if any(w in name for w in ['酋長', '郡司', '国司', '名代', '城代', '兵', '農民', '商人', '忍者', '海賊', '土豪', '豪族']):
            is_suspect = True
        if any(w in oid for w in ['dummy', 'temp', 'proto', 'placeholder', 'generic', 'jodai', 'fake', 'test']):
            is_suspect = True
        if name.endswith('氏') and len(name) > 3: # e.g. 豊後国司大友氏
            is_suspect = True
        
        if is_suspect:
            suspects.append(o)
        
        out.write(f"{oid}\t{name}\t{clan}\t{o.get('birthYear')}\t{o.get('deathYear')}\t{o.get('lore')}\n")

with open('suspect_officers.txt', 'w', encoding='utf-8') as out:
    out.write(f"Suspect officers count: {len(suspects)}\n\n")
    for s in suspects:
        out.write(f"[{s.get('id')}] {s.get('name')} (clan: {s.get('clanId')}, {s.get('birthYear')}-{s.get('deathYear')}): {s.get('lore')}\n")

print(f"Total officers: {len(officers)}, Suspects found: {len(suspects)}")
