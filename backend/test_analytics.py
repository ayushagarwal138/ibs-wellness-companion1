#!/usr/bin/env python3

import sys
import os
from datetime import datetime, timedelta

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.core.config import settings
import asyncpg
import asyncio


async def test_analytics():
    """Test the analytics data directly from the database"""
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
        print(f"Testing analytics for user: {test_user['email']} (ID: {user_id})")
        
        # Test the same queries that the analytics endpoint uses
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # 1. Total symptom logs
        total_symptom_logs = await conn.fetchval("""
            SELECT COUNT(*) FROM symptom_logs 
            WHERE user_id = $1 AND logged_at >= $2
        """, user_id, thirty_days_ago)
        print(f"Total symptom logs (last 30 days): {total_symptom_logs}")
        
        # 2. Total diet logs  
        total_diet_logs = await conn.fetchval("""
            SELECT COUNT(*) FROM diet_logs 
            WHERE user_id = $1 AND consumed_at >= $2
        """, user_id, thirty_days_ago)
        print(f"Total diet logs (last 30 days): {total_diet_logs}")
        
        # 3. Average symptom severity
        avg_severity_result = await conn.fetchrow("""
            SELECT 
                AVG(CASE 
                    WHEN severity = 'NONE' THEN 0
                    WHEN severity = 'MILD' THEN 1
                    WHEN severity = 'MODERATE' THEN 2
                    WHEN severity = 'SEVERE' THEN 3
                    WHEN severity = 'VERY_SEVERE' THEN 4
                    ELSE 0
                END) as avg_severity,
                COUNT(*) as total_logs
            FROM symptom_logs 
            WHERE user_id = $1 AND logged_at >= $2
        """, user_id, thirty_days_ago)
        
        if avg_severity_result and avg_severity_result['total_logs'] > 0:
            avg_severity = float(avg_severity_result['avg_severity'])
            print(f"Average severity: {avg_severity:.2f} (from {avg_severity_result['total_logs']} logs)")
        else:
            print("No symptom logs found for severity calculation")
        
        # 4. Most common symptoms
        common_symptoms = await conn.fetch("""
            SELECT s.name, COUNT(*) as count
            FROM symptom_logs sl
            JOIN symptoms s ON sl.symptom_id = s.id
            WHERE sl.user_id = $1 AND sl.logged_at >= $2
            GROUP BY s.name
            ORDER BY count DESC
            LIMIT 5
        """, user_id, thirty_days_ago)
        
        print("Most common symptoms:")
        for symptom in common_symptoms:
            print(f"  {symptom['name']}: {symptom['count']} times")
        
        # 5. Symptom-free days
        symptom_free_days = await conn.fetchval("""
            SELECT COUNT(DISTINCT DATE(logged_at))
            FROM symptom_logs 
            WHERE user_id = $1 AND logged_at >= $2
        """, user_id, thirty_days_ago)
        
        total_days = 30
        actual_symptom_free_days = total_days - symptom_free_days
        print(f"Days with symptoms: {symptom_free_days}")
        print(f"Symptom-free days: {actual_symptom_free_days}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_analytics())