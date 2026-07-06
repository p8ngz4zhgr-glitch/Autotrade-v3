with open('./bot_code/analyzer/engine.py', 'r') as f:
    content = f.read()

# Let's add it right after elliott
old_str = 'score += elliott.get("score_adj", 0)'
new_str = 'score += elliott.get("score_adj", 0)\n        score += fvg.get("score_adj", 0)'

if 'score += fvg.get("score_adj", 0)' not in content:
    content = content.replace(old_str, new_str)
    
with open('./bot_code/analyzer/engine.py', 'w') as f:
    f.write(content)
print("Fixed engine.py to include FVG score")
