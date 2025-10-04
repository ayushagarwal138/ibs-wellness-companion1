#!/usr/bin/env python3

import sys
import os
from datetime import datetime, timedelta
import uuid

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.core.config import settings
import asyncpg
import asyncio


async def add_test_data():
    """Add some test symptom data for the current user"""
    # Parse the database URL to get connection parameters
    db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    
    try:
        # Connect to the database
        conn = await asyncpg.connect(db_url)
        
        # Get the current user
        test_user = await conn.fetchrow(
            "SELECT id, email FROM users WHERE email = $1", 
            "ayush121@gmail.com"
        )
        
        if not test_user:
            print("User ayush121@gmail.com not found")
            return
            
        user_id = test_user['id']
        print(f"Adding test data for user: {test_user['email']} (ID: {user_id})")
        
        # Get some symptom IDs
        symptoms = await conn.fetch("SELECT id, name FROM symptoms LIMIT 5")
        if not symptoms:
            print("No symptoms found in database")
            return
            
        print(f"Found {len(symptoms)} symptoms")
        
        # Add some symptom logs for the last 30 days
        severities = ['MILD', 'MODERATE', 'SEVERE']
        
        for i in range(10):  # Add 10 symptom logs
            # Random date in the last 30 days
            days_ago = i * 3  # Spread them out
            log_date = datetime.utcnow() - timedelta(days=days_ago)
            
            # Pick a random symptom and severity
            symptom = symptoms[i % len(symptoms)]
            severity = severities[i % len(severities)]
            
            # Insert the symptom log
            await conn.execute("""
                INSERT INTO symptom_logs (user_id, symptom_id, severity, logged_at, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, user_id, symptom['id'], severity, log_date, datetime.utcnow(), datetime.utcnow())
            
            print(f"Added symptom log: {symptom['name']} - {severity} on {log_date.date()}")
        
        print(f"\nAdded 10 symptom logs for user {test_user['email']}")
        
        # Verify the data was added
        count = await conn.fetchval(
            "SELECT COUNT(*) FROM symptom_logs WHERE user_id = $1", 
            user_id
        )
        print(f"Total symptom logs for user: {count}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(add_test_data())