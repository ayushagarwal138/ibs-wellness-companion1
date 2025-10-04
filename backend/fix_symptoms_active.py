#!/usr/bin/env python3
"""
Fix script to set all symptoms as active.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select, update
from app.core.database import AsyncSessionLocal
from app.models.symptom import Symptom

async def fix_symptoms_active():
    """Set all symptoms as active."""
    async with AsyncSessionLocal() as db:
        try:
            print("Checking current symptom status...")
            
            # Check current status
            result = await db.execute(select(Symptom))
            all_symptoms = result.scalars().all()
            
            active_count = sum(1 for s in all_symptoms if s.is_active)
            inactive_count = len(all_symptoms) - active_count
            
            print(f"Total symptoms: {len(all_symptoms)}")
            print(f"Active symptoms: {active_count}")
            print(f"Inactive symptoms: {inactive_count}")
            
            if inactive_count > 0:
                print(f"\nUpdating {inactive_count} inactive symptoms to active...")
                
                # Update all symptoms to be active
                await db.execute(
                    update(Symptom).values(is_active=True)
                )
                await db.commit()
                
                print("All symptoms have been set to active!")
                
                # Verify the update
                result = await db.execute(select(Symptom).where(Symptom.is_active == True))
                active_symptoms = result.scalars().all()
                print(f"Verification: {len(active_symptoms)} symptoms are now active")
                
                # Show first few symptoms
                print("\nFirst 5 active symptoms:")
                for symptom in active_symptoms[:5]:
                    print(f"  ID: {symptom.id}, Name: {symptom.name}, Active: {symptom.is_active}")
            else:
                print("All symptoms are already active!")
                
        except Exception as e:
            print(f"Error: {e}")
            await db.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(fix_symptoms_active())