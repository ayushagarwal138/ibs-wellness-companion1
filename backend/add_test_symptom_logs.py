#!/usr/bin/env python3
"""
Add test symptom logs for the analytics test user to generate weekly trends.
"""

import asyncio
import asyncpg
from datetime import datetime, timedelta
import random


async def add_test_symptom_logs():
    """Add test symptom logs for the analytics test user."""
    
    # Database connection
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="ayushagarwal",
        password="ayush1",
        database="ibs_wellness"
    )
    
    try:
        # Get the test user ID
        user_result = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1",
            "analytics_test@example.com"
        )
        
        if not user_result:
            print("Test user not found!")
            return
            
        user_id = user_result['id']
        print(f"Found test user with ID: {user_id}")
        
        # Get available symptoms
        symptoms = await conn.fetch(
            "SELECT id, name FROM symptoms WHERE is_active = true"
        )
        print(f"Found {len(symptoms)} available symptoms")
        
        if not symptoms:
            print("No symptoms found in database!")
            return
        
        # Create test logs for the last 4 weeks (28 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=28)
        
        severities = ['MILD', 'MODERATE', 'SEVERE', 'VERY_SEVERE']
        bristol_types = [
            'TYPE_1', 'TYPE_2', 'TYPE_3', 'TYPE_4', 
            'TYPE_5', 'TYPE_6', 'TYPE_7'
        ]
        pain_locations = [
            'Lower Left', 'Lower Right', 'Upper Left', 
            'Upper Right', 'Central'
        ]
        
        logs_created = 0
        
        # Create 2-3 logs per week for 4 weeks
        for week in range(4):
            week_start = start_date + timedelta(weeks=week)
            logs_this_week = random.randint(2, 4)  # 2-4 logs per week
            
            for log_num in range(logs_this_week):
                # Random date within this week
                random_day = random.randint(0, 6)
                random_hour = random.randint(8, 20)  # 8 AM to 8 PM
                log_date = week_start + timedelta(
                    days=random_day, hours=random_hour
                )
                
                # Random symptom
                symptom = random.choice(symptoms)
                
                # Random severity (with some bias towards moderate)
                severity = random.choices(
                    severities, 
                    weights=[20, 40, 30, 10],  # Bias towards mild/moderate
                    k=1
                )[0]
                
                # Random bristol type and pain location
                bristol_type = random.choice(bristol_types)
                pain_location = random.choice(pain_locations)
                
                # Random stress level (1-10)
                stress_level = random.randint(3, 8)
                
                # Insert the symptom log
                await conn.execute(
                    """
                    INSERT INTO symptom_logs (
                        user_id, symptom_id, severity, bristol_stool_type, 
                        pain_location, stress_level, logged_at, notes
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """, 
                    user_id, symptom['id'], severity, bristol_type, 
                    pain_location, stress_level, log_date, 
                    f"Test log for week {week + 1}, log {log_num + 1}"
                )
                
                logs_created += 1
                date_str = log_date.strftime('%Y-%m-%d %H:%M')
                print(f"Created log {logs_created}: {symptom['name']} - "
                      f"{severity} on {date_str}")
        
        print(f"\n✅ Successfully created {logs_created} test symptom logs!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(add_test_symptom_logs())