import re

with open('./bot_code/worker/bingx_trader.py', 'r') as f:
    content = f.read()

content = content.replace("res = self._safe_order(params)\n        if res.get(\"code\") == 109400", "res = self._request(\"POST\", \"/openApi/swap/v2/trade/order\", params)\n        if res.get(\"code\") == 109400")

with open('./bot_code/worker/bingx_trader.py', 'w') as f:
    f.write(content)
print("Fixed bingx_trader.py")
