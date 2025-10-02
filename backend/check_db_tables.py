#!/usr/bin/env python3
"""
Simple script to check database tables.
"""
import asyncio
import sqlalchemy
from app.core.database import engine


async def check_tables():
    try:
        async with engine.begin() as conn:
            query = ("SELECT table_name FROM information_schema.tables "
                     "WHERE table_schema = 'public' ORDER BY table_name;")
            result = await conn.execute(sqlalchemy.text(query))
            tables = [row[0] for row in result]
            print("Existing tables:")
            for table in tables:
                print(f"  - {table}")
            print(f"\nTotal tables: {len(tables)}")
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    asyncio.run(check_tables())