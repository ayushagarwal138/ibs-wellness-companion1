import asyncio
import sqlalchemy
from app.core.database import engine

async def check_users_columns():
    async with engine.begin() as conn:
        result = await conn.execute(sqlalchemy.text("SELECT column_name FROM information_schema.columns WHERE table_name = 'users' AND table_schema = 'public';"))
        columns = [row[0] for row in result]
        print("Users table columns:", columns)

if __name__ == "__main__":
    asyncio.run(check_users_columns())