
import os

path = r'd:\Meu Drive\ger_provas\templates\exams\create.html'

try:
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    found = False
    for i in range(len(lines)):
        line = lines[i]
        if 'cat.questions' in line and 'cat.id' in line:
            # We found the line.
            # Capture the indentation
            indent_len = len(line) - len(line.lstrip())
            indent = line[:indent_len]
            
            # Construct the clean line avoiding direct use of the literal that breaks the tool
            # Target: "{{ cat.id }}": {{ cat.questions|length }},
            
            br_open = "{" + "{"
            br_close = "}" + "}"
            
            # We construct it: indentation + " + br_open + " cat.id " + br_close + ": " + br_open + " cat.questions|length " + br_close + ",\n"
            
            new_line = f'{indent}"{br_open} cat.id {br_close}": {br_open} cat.questions|length {br_close},\n'
            
            print(f"Replacing line {i+1}:")
            print(f"Old: {line.rstrip()}")
            print(f"New: {new_line.rstrip()}")
            
            lines[i] = new_line
            found = True
            break

    if found:
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("SUCCESS: File patched.")
    else:
        print("ERROR: Target line not found.")
        
except Exception as e:
    print(f"EXCEPTION: {e}")
