import json
from bot_code.analyzer.indicators import Indicators

def test_fvg():
    ind = Indicators()
    # Bullish FVG
    highs1 = [100, 110, 115, 118]
    lows1  = [95,  100, 105, 112] # l[2]=105 > h[0]=100! FVG gap is between 105 and 100
    closes1= [98,  108, 112, 115]
    
    fvg1 = ind.order_flow_fvg(highs1, lows1, closes1)
    
    # Bearish FVG
    highs2 = [115, 110, 105, 102]
    lows2  = [110, 100, 95, 90]  # h[2]=105 < l[0]=110! FVG gap is between 110 and 105
    closes2= [112, 105, 98, 95]
    
    fvg2 = ind.order_flow_fvg(highs2, lows2, closes2)
    
    with open("fvg_test_output.json", "w") as f:
        json.dump({
            "bullish_test": {
                "highs": highs1,
                "lows": lows1,
                "closes": closes1,
                "fvg_result": fvg1
            },
            "bearish_test": {
                "highs": highs2,
                "lows": lows2,
                "closes": closes2,
                "fvg_result": fvg2
            }
        }, f, indent=4)
    print("FVG test output generated in fvg_test_output.json")

if __name__ == '__main__':
    test_fvg()
