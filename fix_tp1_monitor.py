with open("bot_code/core_api/main.py", "r") as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if "def _tp1_monitor():" in line:
        start_idx = i
        # find the end of the function
        for j in range(i+1, len(lines)):
            if lines[j].startswith("def ") or lines[j].startswith("@app."):
                end_idx = j
                break
        break

if start_idx != -1 and end_idx != -1:
    insert_code = """def _tp1_monitor():
    global LIVE_POSITIONS
    while True:
        try:
            with _POS_LOCK:
                positions = LIVE_POSITIONS.copy()
            
            db = SessionLocal()
            user_positions_map = {}
            for p in positions:
                if not isinstance(p, dict): continue
                uid = p.get("user_id")
                if uid:
                    if uid not in user_positions_map:
                        user_positions_map[uid] = []
                    user_positions_map[uid].append(p)
                    
            for user_id, user_positions in user_positions_map.items():
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
    with open("bot_code/core_api/main.py", "w") as f:
        f.writelines(lines)
    print("Fixed _tp1_monitor")
