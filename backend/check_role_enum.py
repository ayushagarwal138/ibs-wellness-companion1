import asyncio
import sqlalchemy
from app.core.database import engine

async def check_role_enum():
    async with engine.begin() as conn:
        # Check enum values for user_role
        result = await conn.execute(sqlalchemy.text("""
            SELECT enumlabel 
            FROM pg_enum 
            WHERE enumtypid = (
                SELECT oid 
                FROM pg_type 
                WHERE typname = 'user_role'
            );
        """))
        enum_values = [row[0] for row in result]
        print("user_role enum values:", enum_values)

if __name__ == "__main__":
    asyncio.run(check_role_enum())