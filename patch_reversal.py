import re

with open('./bot_code/core_api/main.py', 'r') as f:
    content = f.read()

old_reversal = """
    now = time.time()
    if now - _LAST_REVERSAL_EVAL.get(sym, 0) < 180:
        return
    _LAST_REVERSAL_EVAL[sym] = now
    
    try:
        from analyzer.engine import SignalEngine
        engine = SignalEngine()
        analysis = engine.full_analysis(sym)
        new_direction = analysis.get("final", "WAIT")
        conf = analysis.get("confidence", 0)
"""

new_reversal = """
    now = time.time()
    
    # Check cache first
    cached = _LAST_REVERSAL_EVAL.get(sym)
    if cached and isinstance(cached, dict) and now - cached.get("time", 0) < 180:
        new_direction = cached.get("direction", "WAIT")
        conf = cached.get("conf", 0)
        analysis = cached.get("analysis", {})
    else:
        try:
            from analyzer.engine import SignalEngine
            engine = SignalEngine()
            analysis = engine.full_analysis(sym)
            new_direction = analysis.get("final", "WAIT")
            conf = analysis.get("confidence", 0)
            
            _LAST_REVERSAL_EVAL[sym] = {
                "time": now,
                "direction": new_direction,
                "conf": conf,
                "analysis": analysis
            }
        except Exception as e:
            log.warning("Evaluate reversal for %s error: %s", sym, e)
            return
"""

if "if cached and isinstance(cached, dict)" not in content:
    content = content.replace(old_reversal, new_reversal)

with open('./bot_code/core_api/main.py', 'w') as f:
    f.write(content)
print("Fixed _LAST_REVERSAL_EVAL in core_api/main.py")
