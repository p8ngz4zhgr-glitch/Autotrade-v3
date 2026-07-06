with open('./bot_code/core_api/main.py', 'r') as f:
    lines = f.readlines()

inside_func = False
for i in range(len(lines)):
    if 'def evaluate_reversal_for_position' in lines[i]:
        inside_func = True
    
    if inside_func and lines[i].startswith('        try:'):
        # The next line is `        cached = _LAST_REVERSAL_EVAL.get(sym)` which has 8 spaces.
        # We need to indent everything after `try:` until we hit `    except Exception as e:`
        j = i + 1
        while j < len(lines):
            if lines[j].startswith('    except Exception as e:'):
                break
            # Add 4 spaces if it starts with 8 spaces. Actually, just add 4 spaces to all lines that are not empty.
            if lines[j].strip():
                if lines[j].startswith('        '):
                    # The try block was unindented when I copy-pasted in my rebuild_top.py because I probably forgot the 4 spaces.
                    lines[j] = '    ' + lines[j]
            j += 1
        break

with open('./bot_code/core_api/main.py', 'w') as f:
    f.writelines(lines)
