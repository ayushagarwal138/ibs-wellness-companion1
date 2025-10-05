#!/usr/bin/env python3
"""
Add test symptom logs for the current user (ayush121@gmail.com)
to demonstrate weekly trends functionality.
"""

import asyncio
import asyncpg
from datetime import datetime, timedelta
import random


async def add_test_symptom_logs():
    """Add test symptom logs for the current user."""
    
    # Database connection
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="ayushagarwal",
        password="ayush1",
        database="ibs_wellness"
    )
    
    try:
        # Find the current user
        user_result = await conn.fetchrow(
            """SELECT id, first_name, last_name, email 
               FROM users WHERE email = $1""",
            "ayush121@gmail.com"
        )
        
        if not user_result:
            print("❌ User ayush121@gmail.com not found!")
            return
            
        user_id = user_result['id']
        full_name = f"{user_result['first_name']} {user_result['last_name']}"
        print(f"✅ Found user: {full_name} ({user_result['email']})")
        
        # Get available symptoms
        symptoms = await conn.fetch(
            "SELECT id, name FROM symptoms WHERE is_active = true"
        )
        
        if not symptoms:
            print("❌ No active symptoms found!")
            return
            
        print(f"✅ Found {len(symptoms)} active symptoms")
        
        # Delete existing logs for this user to start fresh
        existing_count = await conn.fetchval(
            "SELECT COUNT(*) FROM symptom_logs WHERE user_id = $1",
            user_id
        )
        
        if existing_count > 0:
            await conn.execute(
                "DELETE FROM symptom_logs WHERE user_id = $1",
                user_id
            )
            print(f"🗑️ Deleted {existing_count} existing symptom logs")
        
        # Create test logs for the last 4 weeks
        logs_created = 0
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=4)
        
        # Create 2-4 logs per week
        current_date = start_date
        while current_date <= end_date:
            # Random number of logs for this week (2-4)
            logs_this_week = random.randint(2, 4)
            
            for _ in range(logs_this_week):
                # Random symptom
                symptom = random.choice(symptoms)
                
                # Random severity (1-10) mapped to enum
                severity_num = random.randint(1, 10)
                if severity_num <= 2:
                    severity = "MILD"
                elif severity_num <= 4:
                    severity = "MODERATE"
                elif severity_num <= 7:
                    severity = "SEVERE"
                else:
                    severity = "VERY_SEVERE"
                
                # Random date within this week
                days_offset = random.randint(0, 6)
                log_date = current_date + timedelta(days=days_offset)
                
                # Ensure we don't go beyond end_date
                if log_date > end_date:
                    log_date = end_date
                
                # Create symptom log
                await conn.execute(
                    """
                    INSERT INTO symptom_logs 
                    (user_id, symptom_id, severity, notes, logged_at)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    user_id,
                    symptom['id'],
                    severity,
                    f"Test log for {symptom['name']}",
                    log_date
                )
                
                logs_created += 1
                print(f"📝 Created log: {symptom['name']} "
                      f"(severity: {severity}) on {log_date.date()}")
            
            # Move to next week
            current_date += timedelta(weeks=1)
        
        print(f"\n🎉 Successfully created {logs_created} test symptom logs!")
        print("You can now view the weekly trends chart in the frontend.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(add_test_symptom_logs())