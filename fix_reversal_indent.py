import re

with open('./bot_code/core_api/main.py', 'r') as f:
    content = f.read()

# We need to replace evaluate_reversal_for_position completely
# Let's extract the full function
start_marker = "def evaluate_reversal_for_position(user: User, pos: dict, current_price: float, db):"
end_marker = "# SYNC POSITIONS & BALANCE"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

old_func = content[start_idx:end_idx]

new_func = """def evaluate_reversal_for_position(user: User, pos: dict, current_price: float, db):
    sym = pos["symbol"]
    direction = pos["direction"]
    qty = float(pos.get("qty", 0))
    entry = float(pos.get("entry", 0))
    
    now = time.time()
    
    try:
        # Check cache first
        cached = _LAST_REVERSAL_EVAL.get(sym)
        if cached and isinstance(cached, dict) and now - cached.get("time", 0) < 180:
            new_direction = cached.get("direction", "WAIT")
            conf = cached.get("conf", 0)
            analysis = cached.get("analysis", {})
        else:
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
            
        is_reversal = (direction == "LONG" and new_direction == "SHORT") or (direction == "SHORT" and new_direction == "LONG")
        
        if is_reversal and conf >= 70:
            bx = get_bx(user)
            in_profit = (direction == "LONG" and current_price > entry) or (direction == "SHORT" and current_price < entry)
            pnl_pct = ((current_price - entry) / entry * 100 if direction == "LONG" else (entry - current_price) / entry * 100)
            
            action_type = "CHỐT LỜI SỚM" if in_profit else "CẮT LỖ SỚM"
            emoji = "💰" if in_profit else "⚠️"
            
            log.info("🚨 Reversal detected for %s %s: %s", user.telegram_id, sym, action_type)
            
            res = bx.close_position(sym, qty, direction)
            if res.get("ok"):
                if redis_client:
                    try:
                        redis_client.setex(f"REVERSAL_CLOSED:{user.telegram_id}:{sym}:{direction}", 120, "1")
                    except Exception:
                        pass
                
                # Cẩn thận: hệ thống không tự xoá SL/TP khi tự đóng lệnh.
                # Tuy nhiên, hàm close_position đã gọi self.cancel_all_orders(symbol), nên SL/TP sẽ bị xoá
                
                _tg_send(
                    REGISTER_TOKEN, user.telegram_id,
                    f"{emoji} <b>{action_type} (REVERSAL): {sym}</b>\\n\\n"
                    f"🔄 Xu hướng thị trường đã đảo chiều sang <b>{new_direction}</b> (Conf: {conf}%).\\n"
                    f"📊 Vị thế cũ: {direction} @ ${entry:.4f}\\n"
                    f"📈 Giá hiện tại: ${current_price:.4f} | PnL: {pnl_pct:+.2f}%\\n"
                    f"🔒 Đã tự động đóng vị thế cũ để bảo vệ vốn.\\n\\n"
                    f"⚡ <i>Hệ thống phân tích lại thị trường và đảo lệnh theo xu hướng mới...</i>"
                )
                
                _save_journal(user.telegram_id, sym, direction, pnl_pct, qty)
                
                time.sleep(1.5)
                
                new_entry = float(analysis["plan"]["entry"])
                new_sl    = float(analysis["plan"]["sl"])
                new_tp1   = float(analysis["plan"]["tp1"])
                new_tp2   = float(analysis["plan"].get("tp2", 0))
                if new_tp2 <= 0:
                    new_tp2 = round(new_tp1 + abs(new_tp1 - new_entry), 4)
                
                sl_pct = abs(new_entry - new_sl) / new_entry
                if sl_pct >= 0.001:
                    risk_amt = user.capital * (user.max_risk_pct / 100)
                    new_qty = round(risk_amt / (new_entry * sl_pct), 4)
                    if new_qty > 0:
                        bx.set_leverage(sym, leverage=user.leverage)
                        bx.cancel_all_orders(sym)
                        new_order_res = bx.place_order(sym, "BUY" if new_direction == "LONG" else "SELL", new_qty, new_sl, new_tp2)
                        if new_order_res.get("ok"):
                            _tg_send(
                                REGISTER_TOKEN, user.telegram_id,
                                f"🚀 <b>VÀO LỆNH THEO XU HƯỚNG MỚI: {sym}</b>\\n"
                                f"📈 {new_direction} | Conf: {conf:.1f}%\\n"
                                f"💰 Qty: {new_qty:.4f} | Lev: {user.leverage}x\\n"
                                f"🛑 SL: <code>${new_sl:.4f}</code>\\n"
                                f"🎯 TP1: <code>${new_tp1:.4f}</code> | TP2: <code>${new_tp2:.4f}</code>"
                            )
    except Exception as e:
        log.warning("Evaluate reversal for %s %s error: %s", user.telegram_id, sym, e)

# ══════════════════════════════════════════════════════════════════
"""

content = content[:start_idx] + new_func + content[end_idx + len(end_marker):]

with open('./bot_code/core_api/main.py', 'w') as f:
    f.write(content)

print("Replaced evaluate_reversal_for_position successfully")
