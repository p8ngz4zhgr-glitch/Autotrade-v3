with open('bot_code/core_api/main.py', 'r') as f:
    lines = f.readlines()

for i in range(267, 391):
    # Strip leading spaces and add 12 spaces for all lines between try: and except:
    line = lines[i].lstrip()
    if line:
        if i == 267:
            lines[i] = "        try:\n"
        else:
            # wait, there's another try/except inside the for loop!
            pass

# Let's just fix it using black if I can install it
