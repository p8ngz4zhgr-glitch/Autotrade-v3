import sys, os
sys.path.append(os.path.abspath('bot_code'))
from core_api.models import SessionLocal, User
db = SessionLocal()
users = db.query(User).filter().all()
print(f"Total Users: {len(users)}")
for u in users:
    print(f"UID: {u.telegram_id}, active: {u.is_active}, auto_trade: {u.auto_trade}, capital: {u.capital}, min_conf: {u.min_confidence}")
