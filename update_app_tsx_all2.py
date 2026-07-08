import re

files_to_update = [
    "engine.py",
    "fetcher.py",
    "llm_agents.py",
    "main_scanner.py",
    "telegram_bot.py"
]

with open("src/App.tsx", "r") as f:
    app_tsx = f.read()

def escape_backticks(s):
    return s.replace("`", "\\`").replace("$", "\\$")

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

for filename in files_to_update:
    with open(f"bot_code/analyzer/{filename}", "r") as f:
        content = f.read()
    escaped_content = escape_backticks(content)
    app_tsx = replace_block(app_tsx, filename, escaped_content)

with open("src/App.tsx", "w") as f:
    f.write(app_tsx)

print("Updated App.tsx with all files")
