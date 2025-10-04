#!/usr/bin/env python3

import sys
import os
from datetime import datetime, timedelta

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.core.config import settings
import asyncpg
import asyncio


async def check_data():
    """Check if there's actual data in the database"""
    # Parse the database URL to get connection parameters
    db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    
    try:
        # Connect to the database
        conn = await asyncpg.connect(db_url)
        
        # Check total users
        total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
        print(f"Total users: {total_users}")
        
        # Check total symptom logs
        total_symptom_logs = await conn.fetchval("SELECT COUNT(*) FROM symptom_logs")
        print(f"Total symptom logs: {total_symptom_logs}")
        
        # Check total diet logs
        total_diet_logs = await conn.fetchval("SELECT COUNT(*) FROM diet_logs")
        print(f"Total diet logs: {total_diet_logs}")
        
        # Check recent symptom logs (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_symptom_logs = await conn.fetchval(
            "SELECT COUNT(*) FROM symptom_logs WHERE logged_at >= $1", 
            thirty_days_ago
        )
        print(f"Recent symptom logs (last 30 days): {recent_symptom_logs}")
        
        # Check recent diet logs (last 30 days)
        recent_diet_logs = await conn.fetchval(
            "SELECT COUNT(*) FROM diet_logs WHERE consumed_at >= $1", 
            thirty_days_ago
        )
        print(f"Recent diet logs (last 30 days): {recent_diet_logs}")
        
        # Show some sample symptom logs
        print("\nSample symptom logs:")
        sample_logs = await conn.fetch(
            "SELECT user_id, symptom_id, severity, logged_at FROM symptom_logs LIMIT 5"
        )
        for log in sample_logs:
            print(f"  User: {log['user_id']}, Symptom ID: {log['symptom_id']}, Severity: {log['severity']}, Date: {log['logged_at']}")
        
        # Show some sample diet logs
        print("\nSample diet logs:")
        sample_diet_logs = await conn.fetch(
            "SELECT user_id, food_id, consumed_at FROM diet_logs LIMIT 5"
        )
        for log in sample_diet_logs:
            print(f"  User: {log['user_id']}, Food ID: {log['food_id']}, Date: {log['consumed_at']}")
        
        # Check for a specific user
        test_user = await conn.fetchrow(
            "SELECT id, email FROM users WHERE email = $1", 
            "ayush121@gmail.com"
        )
        if test_user:
            print(f"\nChecking data for user: {test_user['email']} (ID: {test_user['id']})")
            user_symptom_logs = await conn.fetchval(
                "SELECT COUNT(*) FROM symptom_logs WHERE user_id = $1", 
                test_user['id']
            )
            user_diet_logs = await conn.fetchval(
                "SELECT COUNT(*) FROM diet_logs WHERE user_id = $1", 
                test_user['id']
            )
            print(f"  Symptom logs: {user_symptom_logs}")
            print(f"  Diet logs: {user_diet_logs}")
            
            # Show recent logs for this user
            recent_user_symptoms = await conn.fetch(
                "SELECT symptom_id, severity, logged_at FROM symptom_logs WHERE user_id = $1 AND logged_at >= $2 LIMIT 5",
                test_user['id'], thirty_days_ago
            )
            print(f"  Recent symptom logs:")
            for log in recent_user_symptoms:
                print(f"    Symptom ID {log['symptom_id']}: {log['severity']} on {log['logged_at']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(check_data())