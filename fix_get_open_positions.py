with open('bot_code/worker/bingx_trader.py', 'r') as f:
    content = f.read()

old_code = """
                        qty = float(p.get("positionAmt", 0))
                        if qty == 0:
                            continue
                        sym = p.get("symbol", "")
                        normalized_sym = sym.replace("-", "") if sym else ""
                        positions.append({
                            "symbol": normalized_sym,
                            "direction": "LONG" if qty > 0 else "SHORT",
                            "entry": float(p.get("entryPrice", 0)),
                            "qty": abs(qty),
                            "pnl": float(p.get("unrealizedProfit", 0)),
                        })
"""

new_code = """
                        qty = float(p.get("positionAmt", 0))
                        if qty == 0:
                            continue
                        sym = p.get("symbol", "")
                        normalized_sym = sym.replace("-", "") if sym else ""
                        
                        pos_side = p.get("positionSide")
                        if pos_side in ("LONG", "SHORT"):
                            direction = pos_side
                        else:
                            direction = "LONG" if qty > 0 else "SHORT"
                            
                        positions.append({
                            "symbol": normalized_sym,
                            "direction": direction,
                            "entry": float(p.get("entryPrice", 0)),
                            "qty": abs(qty),
                            "pnl": float(p.get("unrealizedProfit", 0)),
                        })
"""

if old_code.strip() in content:
    content = content.replace(old_code.strip(), new_code.strip())
    with open('bot_code/worker/bingx_trader.py', 'w') as f:
        f.write(content)
    print("Fixed get_open_positions!")
else:
    print("Code not found. Here is what's in the file:")
    import re
    match = re.search(r'qty = float\(p\.get\("positionAmt".*?\}\)', content, re.DOTALL)
    if match:
        print(match.group(0))
