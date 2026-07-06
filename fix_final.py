with open('./bot_code/core_api/main.py', 'r') as f:
    content = f.read()

start_bad = content.find(' API\n"""')
if start_bad != -1:
    sync_idx = content.find('def sync_bingx_positions():')
    if sync_idx != -1:
        clean_middle = '\n# ══════════════════════════════════════════════════════════════════\n# SYNC POSITIONS & BALANCE\n# ══════════════════════════════════════════════════════════════════\n'
        new_content = content[:start_bad] + clean_middle + content[sync_idx:]
        with open('./bot_code/core_api/main.py', 'w') as f:
            f.write(new_content)
        print("Fixed completely!")
    else:
        print("sync_bingx_positions not found")
else:
    print("API not found")
