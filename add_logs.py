import re

with open("bot_code/core_api/main.py", "r") as f:
    content = f.read()

# Add log for BOT_GLOBAL_AUTO
content = content.replace(
    "if not BOT_GLOBAL_AUTO or BOT_KILL_SWITCH:\n                    continue",
    "if not BOT_GLOBAL_AUTO or BOT_KILL_SWITCH:\n                    log.info(f\"Skip trade: GLOBAL_AUTO={BOT_GLOBAL_AUTO}, KILL_SWITCH={BOT_KILL_SWITCH}\")\n                    continue"
)

# Add log for users
content = content.replace(
    "users = (db.query(User)",
    "log.info(f\"Processing signal {sym} for users...\")\n                    users = (db.query(User)"
)

with open("bot_code/core_api/main.py", "w") as f:
    f.write(content)
print("Logs added")
