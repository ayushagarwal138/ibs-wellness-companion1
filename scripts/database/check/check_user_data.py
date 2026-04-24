import asyncio
import sqlalchemy
from app.core.database import engine

async def check_user_data():
    async with engine.begin() as conn:
        result = await conn.execute(sqlalchemy.text("SELECT id, email, password_hash FROM users LIMIT 5;"))
        users = result.fetchall()
        print("Users in database:")
        for user in users:
            print(f"ID: {user[0]}, Email: {user[1]}, Password Hash: {user[2][:20] if user[2] else 'None'}...")

if __name__ == "__main__":
    asyncio.run(check_user_data())