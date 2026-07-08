with open("bot_code/analyzer/main_scanner.py", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "if final_sig == \"WAIT\" and conf < 70 and ev_ratio < 0.3:" in line:
        # Check the next line, it should be return
        if "return" in lines[i+1]:
            # Check the line after that, if it's also return, remove it
            if "return" in lines[i+2]:
                lines.pop(i+2)
        break

with open("bot_code/analyzer/main_scanner.py", "w") as f:
    f.writelines(lines)
print("Fixed double return")
