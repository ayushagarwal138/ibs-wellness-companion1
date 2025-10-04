#!/usr/bin/env python3
"""
Debug script to test the symptoms API endpoint logic.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.symptom import Symptom

async def test_symptoms_query():
    """Test the exact same query used in the symptoms API endpoint."""
    print("Testing symptoms query...")
    
    # Get database session
    async for db in get_db():
        try:
            print("Database connection established")
            
            # Execute the same query as the API
            print("Executing query: select(Symptom).where(Symptom.is_active is True)")
            result = await db.execute(select(Symptom).where(Symptom.is_active is True))
            symptoms = result.scalars().all()
            
            print(f"Query executed successfully")
            print(f"Number of symptoms found: {len(symptoms)}")
            
            if symptoms:
                print("\nSymptoms found:")
                for symptom in symptoms:
                    print(f"  ID: {symptom.id}, Name: {symptom.name}, Category: {symptom.category}, Active: {symptom.is_active}")
            else:
                print("No symptoms found!")
                
                # Let's also try a broader query to see if there are any symptoms at all
                print("\nTrying broader query to check if any symptoms exist...")
                result_all = await db.execute(select(Symptom))
                all_symptoms = result_all.scalars().all()
                print(f"Total symptoms in database: {len(all_symptoms)}")
                
                if all_symptoms:
                    print("All symptoms (including inactive):")
                    for symptom in all_symptoms:
                        print(f"  ID: {symptom.id}, Name: {symptom.name}, Category: {symptom.category}, Active: {symptom.is_active}")
                        
        except Exception as e:
            print(f"Error during query: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await db.close()
        break

if __name__ == "__main__":
    asyncio.run(test_symptoms_query())