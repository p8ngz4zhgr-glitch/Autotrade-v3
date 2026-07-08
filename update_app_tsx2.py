import re

with open("bot_code/analyzer/main_scanner.py", "r") as f:
    scanner_content = f.read()

with open("src/App.tsx", "r") as f:
    app_tsx = f.read()

def escape_backticks(s):
    return s.replace("`", "\\`").replace("$", "\\$")

scanner_escaped = escape_backticks(scanner_content)

def replace_block(text, filename, new_content):
    start_tag = f'"{filename}": `'
    start_idx = text.find(start_tag)
    if start_idx == -1: return text
    
    end_idx = text.find('`,', start_idx + len(start_tag))
    if end_idx == -1:
        end_idx = text.find('`\n', start_idx + len(start_tag))
        
    if end_idx != -1:
        return text[:start_idx + len(start_tag)] + new_content + text[end_idx:]
    return text

app_tsx = replace_block(app_tsx, "main_scanner.py", scanner_escaped)

with open("src/App.tsx", "w") as f:
    f.write(app_tsx)

print("Updated App.tsx")
