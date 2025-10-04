#!/usr/bin/env python3
"""
Debug script that replicates the exact API query logic.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select
from app.core.database import get_db
from app.models.symptom import Symptom

async def debug_api_exact():
    """Test the exact same query logic as the API."""
    print("Testing exact API query logic...")
    
    # Use the same get_db dependency as the API
    async for db in get_db():
        try:
            print("Database session obtained via get_db()")
            
            # Use the exact same query as the API
            print("Executing: select(Symptom).where(Symptom.is_active is True)")
            result = await db.execute(select(Symptom).where(Symptom.is_active is True))
            symptoms = result.scalars().all()
            
            print(f"Query result: {len(symptoms)} symptoms found")
            
            if symptoms:
                print("\nFirst 5 symptoms:")
                for symptom in symptoms[:5]:
                    print(f"  ID: {symptom.id}, Name: {symptom.name}, Active: {symptom.is_active}, Category: {symptom.category}")
            else:
                print("No symptoms found!")
                
                # Let's check what's in the database
                print("\nChecking all symptoms in database...")
                all_result = await db.execute(select(Symptom))
                all_symptoms = all_result.scalars().all()
                print(f"Total symptoms in database: {len(all_symptoms)}")
                
                if all_symptoms:
                    print("First 5 symptoms (regardless of active status):")
                    for symptom in all_symptoms[:5]:
                        print(f"  ID: {symptom.id}, Name: {symptom.name}, Active: {symptom.is_active}, Category: {symptom.category}")
                        
                    # Check active status distribution
                    active_count = sum(1 for s in all_symptoms if s.is_active)
                    print(f"\nActive symptoms: {active_count}")
                    print(f"Inactive symptoms: {len(all_symptoms) - active_count}")
                    
                    # Test different query variations
                    print("\nTesting query variations:")
                    
                    # Test with == True
                    result2 = await db.execute(select(Symptom).where(Symptom.is_active == True))
                    symptoms2 = result2.scalars().all()
                    print(f"Using '== True': {len(symptoms2)} symptoms")
                    
                    # Test with just the column
                    result3 = await db.execute(select(Symptom).where(Symptom.is_active))
                    symptoms3 = result3.scalars().all()
                    print(f"Using just column: {len(symptoms3)} symptoms")
                    
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await db.close()
        break  # Only process the first (and only) db session

if __name__ == "__main__":
    asyncio.run(debug_api_exact())