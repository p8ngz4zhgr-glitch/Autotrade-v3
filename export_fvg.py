import json

def test_fvg_export():
    import sys
    import os
    sys.path.append(os.path.abspath('.'))
    
    from bot_code.analyzer.indicators import Indicators
    ind = Indicators()
    
    # Scenario 2: Bearish FVG
    highs_bear = [120, 115, 105, 100, 95]
    lows_bear  = [110, 100, 90,  85,  80]  
    # l[0] = 110. h[2] = 105. Gap between 110 and 105. 
    closes_bear= [112, 102, 98,  95,  90]
    # c[1] = 102. c[0] = 112. c[1] < c[0].
    
    fvg_bear = ind.order_flow_fvg(highs_bear, lows_bear, closes_bear)
    
    with open("FVG_TEST_REPORT.json", "w", encoding="utf-8") as f:
        json.dump({"BEARISH_SCENARIO": fvg_bear}, f, indent=4)

if __name__ == '__main__':
    test_fvg_export()
