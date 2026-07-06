with open('./bot_code/core_api/main.py', 'r') as f:
    lines = f.readlines()

for i in range(len(lines)):
    if 'except Exception as e:' in lines[i] and 'log.error("sync_bingx_positions: %s", e)' in lines[i+1]:
        # Unindent this except and the next line!
        lines[i] = '        except Exception as e:\n'
        lines[i+1] = '            log.error("sync_bingx_positions: %s", e)\n'
        break

with open('./bot_code/core_api/main.py', 'w') as f:
    f.writelines(lines)
