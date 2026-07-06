with open('./bot_code/core_api/main.py', 'r') as f:
    lines = f.readlines()

# Undo the previous removal of 4 spaces!
for i in range(268, 391):
    lines[i] = '    ' + lines[i]

# Now, we want `try:` to be 8 spaces (it is at 267 actually, wait! The lines list is 0-indexed.
# Line 268 was `        try:\n`
# So index 267 is `        try:\n`
