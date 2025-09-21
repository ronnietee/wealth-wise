import re

with open('static/css/style.css', 'r', encoding='utf-8') as f:
    content = f.read()

print('Checking for CSS issues...')

# Check for unclosed strings
if content.count('"') % 2 != 0:
    print('Unclosed double quotes found')
if content.count("'") % 2 != 0:
    print('Unclosed single quotes found')

# Check for any CSS that might be causing issues
if 'color: transparent' in content:
    print('Found color: transparent')
if 'opacity: 0' in content:
    print('Found opacity: 0')
if 'display: none' in content:
    print('Found display: none')

# Check for any obvious syntax errors
if '{{' in content:
    print('Found double open braces')
if '}}' in content:
    print('Found double close braces')

# Check for any CSS rules that might be malformed
lines = content.split('\n')
for i, line in enumerate(lines):
    if line.strip() and not line.strip().startswith('/*') and not line.strip().startswith('*'):
        if '{' in line and '}' not in line:
            # Check if the next few lines have the closing brace
            found_closing = False
            for j in range(i+1, min(i+10, len(lines))):
                if '}' in lines[j]:
                    found_closing = True
                    break
            if not found_closing:
                print(f'Potentially unclosed rule at line {i+1}: {line.strip()}')

print('CSS check complete')
