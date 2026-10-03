import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('similar_pairs_candidates.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Filter and display 'similar_name' entries
similar_lines = []
for block in text.split('\n\n'):
    if '[similar_name]' in block:
        similar_lines.append(block)

print(f"Total similar_name blocks: {len(similar_lines)}")
with open('similar_name_only.txt', 'w', encoding='utf-8') as f:
    f.write('\n\n'.join(similar_lines))

print("Saved to similar_name_only.txt")
