import asyncio
import sqlalchemy
from app.core.database import engine
from app.core.security import verify_password

async def test_password():
    async with engine.begin() as conn:
        result = await conn.execute(sqlalchemy.text("SELECT email, password_hash FROM users WHERE email = 'test@example.com';"))
        user = result.fetchone()
        
        if user:
            email, password_hash = user
            print(f"Found user: {email}")
            
            # Test different passwords
            test_passwords = ["testpassword", "TestPassword123!", "password123", "test123"]
            
            for password in test_passwords:
                is_valid = verify_password(password, password_hash)
                print(f"Password '{password}': {'Valid' if is_valid else 'Invalid'}")
        else:
            print("User not found")

if __name__ == "__main__":
    asyncio.run(test_password())