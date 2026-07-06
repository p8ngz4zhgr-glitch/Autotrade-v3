import re

with open('./bot_code/worker/bingx_trader.py', 'r') as f:
    content = f.read()

helper = """
    def _safe_order(self, params: dict) -> dict:
        res = self._request("POST", "/openApi/swap/v2/trade/order", params)
        if res.get("code") == 109400: # One-Way mode error
            params["positionSide"] = "BOTH"
            res = self._request("POST", "/openApi/swap/v2/trade/order", params)
        return res
"""

if "_safe_order" not in content:
    content = content.replace("    def place_order", helper + "\n    def place_order")
    content = content.replace('self._request("POST", "/openApi/swap/v2/trade/order", params)', 'self._safe_order(params)')
    
    # Replace the inline calls in _place_sl_tp
    content = re.sub(
        r'self\._request\("POST", "/openApi/swap/v2/trade/order", \{([^}]+)\}\)',
        r'self._safe_order({\1})',
        content
    )

with open('./bot_code/worker/bingx_trader.py', 'w') as f:
    f.write(content)
print("Added _safe_order fallback to bingx_trader.py")
