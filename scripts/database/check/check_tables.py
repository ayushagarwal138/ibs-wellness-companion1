import asyncio
import sqlalchemy
from app.core.database import engine

async def check_tables():
    async with engine.begin() as conn:
        result = await conn.execute(sqlalchemy.text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"))
        tables = [row[0] for row in result]
        print("Existing tables:", tables)

if __name__ == "__main__":
    asyncio.run(check_tables())