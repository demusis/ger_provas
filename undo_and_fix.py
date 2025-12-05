
import os

path = r'd:\Meu Drive\ger_provas\templates\exams\create.html'

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

br_open = "{" + "{"
br_close = "}" + "}"

html_restored = False
js_fixed = False

for i in range(len(lines)):
    line = lines[i]
    
    # 1. Check for the accidental replacement in the HTML section (approx lines 70-90)
    # The accidental line looks like: "        "{{ cat.id }}": {{ cat.questions|length }},"
    # But indentation might be different.
    # It DEFINITELY shouldn't be there if we want to restore <option>
    
    if i < 100:
        if '":' in line and 'cat.questions' in line and '<option' not in line:
            # Found the broken line!
            print(f"Found broken HTML line at {i+1}")
            # Restore it
            # <option value="{{ cat.id }}" data-avail="{{ cat.questions|length }}" data-name="{{ cat.name }}">
            restored = f'                        <option value="{br_open} cat.id {br_close}" data-avail="{br_open} cat.questions|length {br_close}" data-name="{br_open} cat.name {br_close}">\n'
            lines[i] = restored
            html_restored = True
            
    # 2. Check for the JS line in the script section (approx lines 100+)
    if i > 100:
        if 'cat.questions' in line and ('{ {' in line or '{ {' in line): # Checking for the space-broken version
             # Found the broken JS line!
             print(f"Found broken JS line at {i+1}")
             indent = line[:line.find('"')] if '"' in line else "            "
             fixed = f'{indent}"{br_open} cat.id {br_close}": {br_open} cat.questions|length {br_close},\n'
             lines[i] = fixed
             js_fixed = True
        elif 'cat.questions' in line and '":' in line and '<option' not in line: 
             # Maybe it was already fixed but I want to be SURE because of the previous messes.
             # Or maybe it has the bad spaces from the agent tool
             # Let's just force overwrite it to be safe if it looks like the JS map entry
             print(f"Forcing JS line fix at {i+1}")
             indent = line[:line.find('"')] if '"' in line else "            "
             fixed = f'{indent}"{br_open} cat.id {br_close}": {br_open} cat.questions|length {br_close},\n'
             lines[i] = fixed
             js_fixed = True

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

if html_restored:
    print("HTML line restored.")
if js_fixed:
    print("JS line fixed.")
if not html_restored and not js_fixed:
    print("No changes made.")

