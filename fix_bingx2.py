import re

with open('./bot_code/worker/bingx_trader.py', 'r') as f:
    content = f.read()

content = content.replace("res = self._safe_order(params)\n        return res", "res = self._request(\"POST\", \"/openApi/swap/v2/trade/order\", params)\n        return res")

with open('./bot_code/worker/bingx_trader.py', 'w') as f:
    f.write(content)
print("Fixed bingx_trader.py again")
