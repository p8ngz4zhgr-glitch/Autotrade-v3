import re

files_to_embed = [
    ("main.py", "bot_code/core_api/main.py"),
]

def escape_backticks(s):
    return s.replace("`", "\\`").replace("$", "\\$")

with open("src/App.tsx", "r") as f:
    app_tsx = f.read()

start_marker = "const pythonFiles: Record<string, string> = {"
start_idx = app_tsx.find(start_marker)

if start_idx != -1:
    end_idx = app_tsx.find("\n};\n", start_idx)
    if end_idx == -1:
        end_idx = app_tsx.find("\n};", start_idx)
    
if start_idx != -1 and end_idx != -1:
    files_to_embed = [
        ("engine.py", "bot_code/analyzer/engine.py"),
        ("fetcher.py", "bot_code/analyzer/fetcher.py"),
        ("llm_agents.py", "bot_code/analyzer/llm_agents.py"),
        ("telegram_bot.py", "bot_code/analyzer/telegram_bot.py"),
        ("main_scanner.py", "bot_code/analyzer/main_scanner.py"),
        ("main.py", "bot_code/core_api/main.py"),
    ]
    new_block = start_marker + "\n"
    for name, path in files_to_embed:
        try:
            with open(path, "r") as pf:
                content = pf.read()
            new_block += f'  "{name}": `{escape_backticks(content)}`,\n'
        except Exception as e:
            print(f"Error reading {path}: {e}")
    new_block += "};"
    
    app_tsx = app_tsx[:start_idx] + new_block + app_tsx[end_idx + 3:]
    
    with open("src/App.tsx", "w") as f:
        f.write(app_tsx)
    print("Replaced pythonFiles block completely.")

