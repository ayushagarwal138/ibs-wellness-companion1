#!/usr/bin/env python3
"""
Add test symptom logs for the API test user.
"""

import asyncio
import asyncpg
from datetime import datetime, timedelta
import random

async def add_test_data():
    """Add test symptom logs for the API test user."""
    
    # Database connection
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="ayushagarwal",
        password="postgres",
        database="ibs_wellness"
    )
    
    try:
        # Get the test user ID
        user_result = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1",
            "api_test@example.com"
        )
        
        if not user_result:
            print("Test user not found!")
            return
            
        user_id = user_result['id']
        print(f"Found test user with ID: {user_id}")
        
        # Get available symptoms
        symptoms = await conn.fetch("SELECT id, name FROM symptoms WHERE is_active = true")
        print(f"Found {len(symptoms)} available symptoms")
        
        if not symptoms:
            print("No symptoms found in database!")
            return
        
        # Create test logs for the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        severities = ['MILD', 'MODERATE', 'SEVERE', 'VERY_SEVERE']
        
        logs_created = 0
        for i in range(15):  # Create 15 test logs
            # Random date within the last 30 days
            random_days = random.randint(0, 30)
            log_date = end_date - timedelta(days=random_days)
            
            # Random symptom
            symptom = random.choice(symptoms)
            
            # Random severity
            severity = random.choice(severities)
            
            # Insert the log
            await conn.execute("""
                INSERT INTO symptom_logs (
                    user_id, symptom_id, severity, logged_at, 
                    duration_minutes, stress_level, sleep_quality
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, user_id, symptom['id'], severity, log_date, 
                random.randint(15, 120), random.randint(1, 10), random.randint(1, 10))
            
            logs_created += 1
            print(f"Created log {logs_created}: {symptom['name']} - {severity} on {log_date.date()}")
        
        print(f"\nSuccessfully created {logs_created} test symptom logs for API test user")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(add_test_data())