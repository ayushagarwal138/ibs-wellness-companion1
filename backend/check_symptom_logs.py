#!/usr/bin/env python3
"""
Check symptom logs in the database.
"""

import asyncio
import sys
import os

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.symptom import SymptomLog
from app.models.user import User

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


async def check_symptom_logs():
    """Check symptom logs in the database."""
    async with AsyncSessionLocal() as db:
        try:
            print("Checking symptom logs in database...")
            
            # Get all symptom logs
            result = await db.execute(select(SymptomLog))
            logs = result.scalars().all()
            
            print(f"Total symptom logs: {len(logs)}")
            
            if logs:
                print("\nSymptom logs:")
                for log in logs:
                    print(f"  ID: {log.id}, User ID: {log.user_id}, "
                          f"Symptom ID: {log.symptom_id}")
                    print(f"      Severity: {log.severity}, "
                          f"Logged at: {log.logged_at}")
                    print(f"      Notes: {log.notes}")
                    print()
                    
                # Get user info
                print("Checking users...")
                user_result = await db.execute(select(User))
                users = user_result.scalars().all()
                print(f"Total users: {len(users)}")
                for user in users:
                    print(f"  User ID: {user.id}, Email: {user.email}")
                    
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_symptom_logs())