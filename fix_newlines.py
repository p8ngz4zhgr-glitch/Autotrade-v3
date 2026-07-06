with open('./bot_code/core_api/main.py', 'r') as f:
    content = f.read()

# Let's fix the f-strings
content = content.replace('</b>\n\n"', '</b>\\n\\n"')
content = content.replace('(Conf: {conf}%).\n"', '(Conf: {conf}%).\\n"')
content = content.replace('@ ${entry:.4f}\n"', '@ ${entry:.4f}\\n"')
content = content.replace('| PnL: {pnl_pct:+.2f}%\n"', '| PnL: {pnl_pct:+.2f}%\\n"')

content = content.replace('MỚI: {sym}</b>\n"', 'MỚI: {sym}</b>\\n"')
content = content.replace('| Conf: {conf:.1f}%\n"', '| Conf: {conf:.1f}%\\n"')
content = content.replace('| Lev: {user.leverage}x\n"', '| Lev: {user.leverage}x\\n"')
content = content.replace('🛑 SL: <code>${new_sl:.4f}</code>\n"', '🛑 SL: <code>${new_sl:.4f}</code>\\n"')

with open('./bot_code/core_api/main.py', 'w') as f:
    f.write(content)
