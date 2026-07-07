with open('bot_code/core_api/main.py', 'r') as f:
    lines = f.readlines()

for i in range(268, 391):
    if lines[i].startswith('            '):
        lines[i] = lines[i][4:]

lines[391] = '        except Exception as e:\n'
lines[392] = '            log.error("sync_bingx_positions: %s", e)\n'
lines[393] = '\n'
lines[394] = '        cleanup_counter += 1\n'
lines[395] = '        if cleanup_counter >= 2880:\n'
lines[396] = '            cleanup_counter = 0\n'
lines[397] = '            threading.Thread(target=_cleanup_inactive_users, daemon=True).start()\n'
lines[398] = '\n'
lines[399] = '        time.sleep(30)\n'

with open('bot_code/core_api/main.py', 'w') as f:
    f.writelines(lines)
