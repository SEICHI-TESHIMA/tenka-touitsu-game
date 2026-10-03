import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("--- 675 to 720 ---")
for i in range(674, 718):
    if i < len(lines):
        print(f"{i+1}: {lines[i]}", end="")

print("\n--- 2680 to 2745 ---")
for i in range(2679, 2745):
    if i < len(lines):
        print(f"{i+1}: {lines[i]}", end="")
