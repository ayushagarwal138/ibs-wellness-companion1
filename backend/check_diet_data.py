#!/usr/bin/env python3
"""
Check diet logs and food items in the database
"""
import asyncio
import asyncpg
from app.core.config import settings


async def check_data():
    # Convert asyncpg URL to regular postgresql URL
    db_url = settings.DATABASE_URL.replace(
        "postgresql+asyncpg://", "postgresql://"
    )
    conn = await asyncpg.connect(db_url)
    try:
        # Check total users
        users = await conn.fetch('SELECT COUNT(*) as count FROM users')
        print(f'Total users: {users[0]["count"]}')
        
        # Check total diet logs
        diet_logs = await conn.fetch('SELECT COUNT(*) as count FROM diet_logs')
        print(f'Total diet logs: {diet_logs[0]["count"]}')
        
        # Check total food items
        food_items = await conn.fetch(
            'SELECT COUNT(*) as count FROM food_items'
        )
        print(f'Total food items: {food_items[0]["count"]}')
        
        # Get a test user ID
        test_user = await conn.fetchrow(
            "SELECT id FROM users WHERE email = 'api_test@example.com'"
        )
        if test_user:
            user_id = test_user['id']
            print(f'Test user ID: {user_id}')
            
            # Check diet logs for this user
            user_logs = await conn.fetch(
                'SELECT COUNT(*) as count FROM diet_logs WHERE user_id = $1',
                user_id
            )
            print(f'Diet logs for test user: {user_logs[0]["count"]}')
            
            # Check if there are any diet logs at all
            sample_logs = await conn.fetch(
                'SELECT * FROM diet_logs LIMIT 3'
            )
            print(f'Sample diet logs: {len(sample_logs)}')
            for log in sample_logs:
                print(f'  Log: {dict(log)}')
        else:
            print('Test user not found')
    
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(check_data())