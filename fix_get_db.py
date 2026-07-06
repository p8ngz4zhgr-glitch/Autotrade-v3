with open('./bot_code/core_api/main.py', 'r') as f:
    content = f.read()

get_db_code = """
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""

# inject before 'class UserRegister'
content = content.replace('class UserRegister(BaseModel):', get_db_code + '\nclass UserRegister(BaseModel):')

with open('./bot_code/core_api/main.py', 'w') as f:
    f.write(content)
