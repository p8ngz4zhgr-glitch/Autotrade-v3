import re

with open('./bot_code/worker/bingx_trader.py', 'r') as f:
    content = f.read()

content = content.replace(
    'return self._request("POST", "/openApi/swap/v2/trade/cancelAllAfter", {',
    'return self._request("DELETE", "/openApi/swap/v2/trade/allOpenOrders", {'
)

with open('./bot_code/worker/bingx_trader.py', 'w') as f:
    f.write(content)
print("Fixed cancel_all_orders in bingx_trader.py")
