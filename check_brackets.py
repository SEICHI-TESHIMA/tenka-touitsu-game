with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Check brackets balance
counts = {'{': 0, '}': 0, '(': 0, ')': 0, '[': 0, ']': 0}
in_str = False
str_char = ''
in_comment_single = False
in_comment_multi = False

i = 0
n = len(text)
while i < n:
    c = text[i]
    if in_comment_single:
        if c == '\n':
            in_comment_single = False
    elif in_comment_multi:
        if c == '*' and i + 1 < n and text[i+1] == '/':
            in_comment_multi = False
            i += 1
    elif in_str:
        if c == '\\':
            i += 1
        elif c == str_char:
            in_str = False
    else:
        if c == '/' and i + 1 < n and text[i+1] == '/':
            in_comment_single = True
            i += 1
        elif c == '/' and i + 1 < n and text[i+1] == '*':
            in_comment_multi = True
            i += 1
        elif c in ["'", '"', '`']:
            in_str = True
            str_char = c
        elif c in counts:
            counts[c] += 1
    i += 1

print("Brackets counts in js/app.js:")
print('{ :', counts['{'], '} :', counts['}'], 'diff:', counts['{'] - counts['}'])
print('( :', counts['('], ') :', counts[')'], 'diff:', counts['('] - counts[')'])
print('[ :', counts['['], '] :', counts[']'], 'diff:', counts['['] - counts[']'])
