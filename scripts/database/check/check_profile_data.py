import asyncio
import sqlalchemy
from app.core.database import engine

async def check_profile_data():
    async with engine.begin() as conn:
        # Get all users with their profile data
        result = await conn.execute(sqlalchemy.text("""
            SELECT 
                id, email, first_name, last_name, phone_number, 
                date_of_birth, gender, height_cm, weight_kg,
                ibs_type, diagnosis_date, emergency_contact_name, 
                emergency_contact_phone, medical_notes,
                created_at, updated_at
            FROM users 
            ORDER BY updated_at DESC 
            LIMIT 10;
        """))
        users = result.fetchall()
        
        print("=== USER PROFILE DATA IN DATABASE ===")
        print(f"Found {len(users)} users")
        print()
        
        for i, user in enumerate(users, 1):
            print(f"--- User {i} ---")
            print(f"ID: {user[0]}")
            print(f"Email: {user[1]}")
            print(f"Name: {user[2]} {user[3]}")
            print(f"Phone: {user[4]}")
            print(f"Date of Birth: {user[5]}")
            print(f"Gender: {user[6]}")
            print(f"Height: {user[7]} cm")
            print(f"Weight: {user[8]} kg")
            print(f"IBS Type: {user[9]}")
            print(f"Diagnosis Date: {user[10]}")
            print(f"Emergency Contact: {user[11]} ({user[12]})")
            print(f"Medical Notes: {user[13]}")
            print(f"Created: {user[14]}")
            print(f"Updated: {user[15]}")
            print()

        # Check for the test user specifically
        test_result = await conn.execute(sqlalchemy.text("""
            SELECT 
                id, email, first_name, last_name, phone_number, 
                date_of_birth, gender, height_cm, weight_kg,
                ibs_type, diagnosis_date, emergency_contact_name, 
                emergency_contact_phone, medical_notes
            FROM users 
            WHERE email = 'test@example.com';
        """))
        test_user = test_result.fetchone()
        
        if test_user:
            print("=== TEST USER PROFILE DATA ===")
            print(f"ID: {test_user[0]}")
            print(f"Email: {test_user[1]}")
            print(f"Name: {test_user[2]} {test_user[3]}")
            print(f"Phone: {test_user[4]}")
            print(f"Date of Birth: {test_user[5]}")
            print(f"Gender: {test_user[6]}")
            print(f"Height: {test_user[7]} cm")
            print(f"Weight: {test_user[8]} kg")
            print(f"IBS Type: {test_user[9]}")
            print(f"Diagnosis Date: {test_user[10]}")
            print(f"Emergency Contact: {test_user[11]} ({test_user[12]})")
            print(f"Medical Notes: {test_user[13]}")
        else:
            print("Test user not found!")

if __name__ == "__main__":
    asyncio.run(check_profile_data())