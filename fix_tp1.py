with open("bot_code/core_api/main.py", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "def _tp1_monitor():" in line:
        start_idx = i
        end_idx = i + 1
        while "def " not in lines[end_idx]:
            end_idx += 1
            if end_idx >= len(lines):
                break
        
        insert_code = """def _tp1_monitor():
    global LIVE_POSITIONS
    while True:
        try:
            with _POS_LOCK:
                positions = LIVE_POSITIONS.copy()
            
            db = SessionLocal()
            for user_id, user_positions in positions.items():
                if not user_positions: continue
                user = db.query(User).filter_by(telegram_id=user_id).first()
                if not user or not user.api_key: continue
                
                bx = get_bx(user)
                
                for p in user_positions:
                    sym = p.get("symbol")
                    direction = p.get("direction")
                    cur_price = p.get("current_price", 0)
                    tp1 = p.get("tp1", 0)
                    tp2 = p.get("tp2", 0)
                    entry = p.get("entry", 0)
                    qty = p.get("qty", 0)
                    
                    if not sym or not cur_price or not tp1 or qty <= 0:
                        continue
                        
                    # Tránh trigger nhiều lần
                    redis_key = f"TP1_HIT:{user_id}:{sym}:{direction}"
                    if redis_client and redis_client.exists(redis_key):
                        continue
                        
                    is_hit = False
                    if direction == "LONG" and cur_price >= tp1 and tp1 > entry:
                        is_hit = True
                    elif direction == "SHORT" and cur_price <= tp1 and tp1 < entry:
                        is_hit = True
                        
                    if is_hit:
                        res = bx.handle_tp1_hit(sym, direction, qty, entry, tp2)
                        if res.get("ok"):
                            if redis_client:
                                redis_client.setex(redis_key, 86400, "1")  # Lưu 1 ngày
                            _tg_send(
                                REGISTER_TOKEN, user_id,
                                f"🎯 <b>TP1 HIT: {sym}</b>\\n"
                                f"📈 Đã chốt 50% vị thế tại ${tp1:.4f}\\n"
                                f"🛡️ Đã dời SL về Entry (${entry:.4f}) để bảo toàn vốn."
                            )
            db.close()
        except Exception as e:
            log.error("_tp1_monitor error: %s", e)
        time.sleep(15)

"""
        lines[start_idx:end_idx] = [insert_code]
        break

with open("bot_code/core_api/main.py", "w") as f:
    f.writelines(lines)
print("Added tp1 monitor")
