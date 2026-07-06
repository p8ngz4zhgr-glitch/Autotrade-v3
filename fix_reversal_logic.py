import re

with open('./bot_code/core_api/main.py', 'r') as f:
    content = f.read()

# Extract evaluate_reversal_for_position
start_marker = "def evaluate_reversal_for_position(user: User, pos: dict, current_price: float, db):"
end_marker = "# SYNC POSITIONS & BALANCE"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

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
        is_weak_trend = (new_direction == "WAIT" and conf < 40)
        
        should_close_early = False
        should_reverse = False
        
        if is_reversal and conf >= 70:
            should_close_early = True
            should_reverse = True
        elif is_reversal and conf >= 40:
            should_close_early = True
        elif is_weak_trend:
            should_close_early = True
            
        if should_close_early:
            bx = get_bx(user)
            in_profit = (direction == "LONG" and current_price > entry) or (direction == "SHORT" and current_price < entry)
            pnl_pct = ((current_price - entry) / entry * 100 if direction == "LONG" else (entry - current_price) / entry * 100)
            
            # Cẩn thận: Nếu đang lỗ quá nhỏ hoặc lời thì đóng, nếu đang lỗ nặng mà chạm SL thì để SL tự dính
            # Tuỳ chiến lược, ở đây user muốn đóng sớm.
            
            action_type = "CHỐT LỜI SỚM" if in_profit else "CẮT LỖ SỚM"
            emoji = "💰" if in_profit else "⚠️"
            reason = "đảo chiều mạnh" if should_reverse else ("đảo chiều yếu" if is_reversal else "xu hướng suy yếu (WAIT)")
            
            log.info("🚨 Early Exit detected for %s %s: %s (Reason: %s)", user.telegram_id, sym, action_type, reason)
            
            res = bx.close_position(sym, qty, direction)
            if res.get("ok"):
                if redis_client:
                    try:
                        redis_client.setex(f"REVERSAL_CLOSED:{user.telegram_id}:{sym}:{direction}", 120, "1")
                    except Exception:
                        pass
                
                # Hàm close_position đã gọi self.cancel_all_orders(symbol), nên SL/TP sẽ bị xoá
                # Gọi thêm một lần cho chắc chắn
                bx.cancel_all_orders(sym)
                
                _tg_send(
                    REGISTER_TOKEN, user.telegram_id,
                    f"{emoji} <b>{action_type} ({reason.upper()}): {sym}</b>\\n\\n"
                    f"🔄 Đánh giá lại: Xu hướng chuyển sang <b>{new_direction}</b> (Conf: {conf}%).\\n"
                    f"📊 Vị thế cũ: {direction} @ ${entry:.4f}\\n"
                    f"📈 Giá hiện tại: ${current_price:.4f} | PnL: {pnl_pct:+.2f}%\\n"
                    f"🔒 Đã tự động đóng vị thế và huỷ SL/TP cũ để bảo vệ vốn."
                )
                
                _save_journal(user.telegram_id, sym, direction, pnl_pct, qty)
                time.sleep(1.5)
                
                if should_reverse:
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
                            # Gọi lại cancel cho an toàn
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

print("Updated evaluate_reversal_for_position logic successfully")
