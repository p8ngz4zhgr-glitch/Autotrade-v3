import os

with open('./bot_code/core_api/main.py', 'r') as f:
    content = f.read()

# We know content starts with `"""SignalBot v6.1 — Main`
# Let's drop the first line and put our own header.
first_newline = content.find('\n')
if first_newline != -1:
    content = content[first_newline:]

header = """\"\"\"SignalBot v6.1 — Main API\"\"\"
import os
import sys
import json
import asyncio
import threading
import time
import logging
import gc
import schedule
import requests as _req
import redis
import redis.asyncio as aioredis
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core_api.models import SessionLocal, User, TradeJournal
from core_api.security import encrypt_api_secret, decrypt_api_secret
from analyzer.main_scanner import SignalBot
from worker.bingx_trader import BingXExchange

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("MainAPI")

app = FastAPI(title="SignalBot v6.1")

REGISTER_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
except Exception:
    redis_client = None

LIVE_POSITIONS = {}
LAST_SIGNALS = []
_LAST_REVERSAL_EVAL = {}

# ══════════════════════════════════════════════════════════════════
# TIER CONFIG
# ══════════════════════════════════════════════════════════════════
TIER_CONFIG = {
    "TIER1": {
        "label": "Ca Con", "min_capital": 0, "max_capital": 500,
        "min_confidence": 68.0, "max_risk_pct": 2.0,
        "max_positions": 2, "leverage": 5, "target_monthly": "5-8%",
    },
    "TIER2": {
        "label": "Tieu Chuan", "min_capital": 500, "max_capital": 2000,
        "min_confidence": 75.0, "max_risk_pct": 1.5,
        "max_positions": 3, "leverage": 5, "target_monthly": "4-6%",
    },
    "TIER3": {
        "label": "Ca Map", "min_capital": 2000, "max_capital": float("inf"),
        "min_confidence": 80.0, "max_risk_pct": 1.0,
        "max_positions": 5, "leverage": 3, "target_monthly": "3-5%",
    },
}
MIN_CAPITAL_TO_TRADE = 20.0

def get_tier(capital: float) -> Optional[str]:
    if capital < MIN_CAPITAL_TO_TRADE:
        return None
    for tier, cfg in TIER_CONFIG.items():
        if cfg["min_capital"] <= capital < cfg["max_capital"]:
            return tier
    return "TIER3"

def apply_tier(user: User, tier: str):
    if tier not in TIER_CONFIG:
        return
    cfg = TIER_CONFIG[tier]
    user.tier           = tier
    user.min_confidence = cfg["min_confidence"]
    user.max_risk_pct   = cfg["max_risk_pct"]
    user.max_positions  = cfg["max_positions"]
    user.leverage       = cfg["leverage"]

def get_bx(user: User) -> BingXExchange:
    secret = decrypt_api_secret(user.api_secret_encrypted) if user.api_secret_encrypted else ""
    return BingXExchange(user.api_key, secret)

def _update_user_balance_and_tier(user: User, balance: float, db: Session):
    try:
        user.capital = balance
        tier = get_tier(balance)
        if tier and user.tier != tier:
            apply_tier(user, tier)
        db.commit()
    except Exception as e:
        log.warning("Update balance error: %s", e)

def _tg_send(token: str, chat_id: str, text: str):
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        _req.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=5)
    except Exception as e:
        log.warning("_tg_send error: %s", e)

def _save_journal(uid: str, sym: str, direction: str, pnl_pct: float, qty: float):
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.telegram_id == uid).first()
        j = TradeJournal(
            symbol=sym,
            user_id=uid,
            tier=user.tier if user else "TIER1",
            direction=direction,
            outcome="WIN" if pnl_pct > 0 else "LOSS",
            pnl_pct=pnl_pct,
            pnl_usd=0.0,
            lesson="Early Exit"
        )
        db.add(j)
        db.commit()
        db.close()
    except Exception as e:
        pass

def run_signal_bot():
    try:
        bot = SignalBot()
        bot.start()
    except Exception as e:
        log.error("run_signal_bot: %s", e)

def run_trade_worker():
    pass

def _tp1_monitor():
    while True:
        time.sleep(30)

def _schedule_weekly_report():
    pass

def _register_telegram_webhook():
    try:
        url = f"https://api.telegram.org/bot{REGISTER_TOKEN}/setWebhook"
        webhook_url = f"{os.getenv('RENDER_URL', 'https://auto-trade-v6.onrender.com')}/telegram/webhook"
        r = _req.get(url, params={"url": webhook_url}, timeout=10)
        if r.status_code == 200:
            log.info("✅ Auto register Telegram Webhook success: %s", webhook_url)
    except Exception as e:
        log.warning("⚠️ Error registering Telegram Webhook: %s", e)

def evaluate_reversal_for_position(user: User, pos: dict, current_price: float, db: Session):
    sym = pos["symbol"]
    direction = pos["direction"]
    qty = float(pos.get("qty", 0))
    entry = float(pos.get("entry", 0))
    
    now = time.time()
    
    try:
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
                
                bx.cancel_all_orders(sym)
                
                _tg_send(
                    REGISTER_TOKEN, user.telegram_id,
                    f"{emoji} <b>{action_type} ({reason.upper()}): {sym}</b>\n\n"
                    f"🔄 Đánh giá lại: Xu hướng chuyển sang <b>{new_direction}</b> (Conf: {conf}%).\n"
                    f"📊 Vị thế cũ: {direction} @ ${entry:.4f}\n"
                    f"📈 Giá hiện tại: ${current_price:.4f} | PnL: {pnl_pct:+.2f}%\n"
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
                            bx.cancel_all_orders(sym)
                            new_order_res = bx.place_order(sym, "BUY" if new_direction == "LONG" else "SELL", new_qty, new_sl, new_tp2)
                            if new_order_res.get("ok"):
                                _tg_send(
                                    REGISTER_TOKEN, user.telegram_id,
                                    f"🚀 <b>VÀO LỆNH THEO XU HƯỚNG MỚI: {sym}</b>\n"
                                    f"📈 {new_direction} | Conf: {conf:.1f}%\n"
                                    f"💰 Qty: {new_qty:.4f} | Lev: {user.leverage}x\n"
                                    f"🛑 SL: <code>${new_sl:.4f}</code>\n"
                                    f"🎯 TP1: <code>${new_tp1:.4f}</code> | TP2: <code>${new_tp2:.4f}</code>"
                                )
    except Exception as e:
        log.warning("Evaluate reversal for %s %s error: %s", user.telegram_id, sym, e)
"""

with open('./bot_code/core_api/main.py', 'w') as f:
    f.write(header + content)

print("Rebuilt top of file!")
