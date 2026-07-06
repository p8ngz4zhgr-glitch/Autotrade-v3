with open('./bot_code/core_api/main.py', 'r') as f:
    content = f.read()

idx = content.find(' API\n"""')
if idx != -1:
    print("Found at", idx)
    
    end_of_new_func = content.find('# ══════════════════════════════════════════════════════════════════')
    if end_of_new_func != -1:
        # Move past it
        end_of_new_func += len('# ══════════════════════════════════════════════════════════════════')
        # Maybe there's a newline
        if content[end_of_new_func] == '\n':
            end_of_new_func += 1
            
        suffix = content[end_of_new_func:]
        original_content = content[:25] + suffix
        with open('./bot_code/core_api/main.py', 'w') as f:
            f.write(original_content)
        print("Recovered!")
