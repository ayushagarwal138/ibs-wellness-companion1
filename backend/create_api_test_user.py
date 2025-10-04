#!/usr/bin/env python3
"""
Create a test user with known credentials for API testing
"""
import asyncio
import asyncpg
from datetime import datetime
import uuid
import bcrypt


async def create_test_user():
    """Create a test user with known credentials"""
    
    # Database connection
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="ayushagarwal",
        password="ayush1",
        database="ibs_wellness"
    )
    
    try:
        # Test user details
        email = "api_test@example.com"
        password = "testpass123"
        
        # Check if user already exists
        existing_user = await conn.fetchrow("""
            SELECT id FROM users WHERE email = $1
        """, email)
        
        if existing_user:
            print(f"User {email} already exists. Updating password...")
            user_id = existing_user['id']
            
            # Update password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            await conn.execute("""
                UPDATE users SET password_hash = $1 WHERE id = $2
            """, password_hash, user_id)
            
        else:
            print(f"Creating new user {email}...")
            user_id = uuid.uuid4()
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Create user
            await conn.execute("""
                INSERT INTO users (
                    id, email, first_name, last_name, password_hash,
                    is_active, is_verified, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, 
                user_id, email, "API", "Test", password_hash,
                True, True, datetime.utcnow(), datetime.utcnow()
            )
        
        print(f"Test user created/updated successfully!")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"User ID: {user_id}")
        
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(create_test_user())