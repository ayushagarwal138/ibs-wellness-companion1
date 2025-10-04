#!/usr/bin/env python3
"""
Check users in the database
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check_users():
    """Check users in the database"""
    
    # Database connection
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="ayushagarwal",
        password="ayush1",
        database="ibs_wellness"
    )
    
    try:
        # Get all users
        users = await conn.fetch("""
            SELECT id, email, first_name, last_name, is_active, is_verified, created_at
            FROM users 
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  ID: {user['id']}")
            print(f"  Email: {user['email']}")
            print(f"  Name: {user['first_name']} {user['last_name']}")
            print(f"  Active: {user['is_active']}")
            print(f"  Verified: {user['is_verified']}")
            print(f"  Created: {user['created_at']}")
            print("  ---")
        
        # Check specific user
        target_email = "ayush121@gmail.com"
        user = await conn.fetchrow("""
            SELECT id, email, first_name, last_name, is_active, is_verified, password_hash
            FROM users 
            WHERE email = $1
        """, target_email)
        
        if user:
            print(f"\nTarget user {target_email}:")
            print(f"  ID: {user['id']}")
            print(f"  Active: {user['is_active']}")
            print(f"  Verified: {user['is_verified']}")
            print(f"  Has password hash: {bool(user['password_hash'])}")
        else:
            print(f"\nUser {target_email} not found!")
            
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_users())