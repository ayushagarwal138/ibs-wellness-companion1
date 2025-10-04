#!/usr/bin/env python3
"""
Test script to verify symptoms in the API's database.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from app.models.symptom import Symptom
from app.core.config import settings

async def test_api_database():
    """Test the exact same database that the API uses."""
    print(f"Testing API database: {settings.DATABASE_URL}")
    
    # Create engine using the same settings as the API
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        future=True,
    )
    
    # Create session factory
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    
    async with AsyncSessionLocal() as session:
        try:
            print("Database connection established")
            
            # Execute the same query as the API
            print("Executing query: select(Symptom).where(Symptom.is_active is True)")
            result = await session.execute(select(Symptom).where(Symptom.is_active is True))
            symptoms = result.scalars().all()
            
            print(f"Query executed successfully")
            print(f"Number of active symptoms found: {len(symptoms)}")
            
            if symptoms:
                print("\nActive symptoms found:")
                for symptom in symptoms[:5]:  # Show first 5
                    print(f"  ID: {symptom.id}, Name: {symptom.name}, Category: {symptom.category}")
                if len(symptoms) > 5:
                    print(f"  ... and {len(symptoms) - 5} more")
            else:
                print("No active symptoms found!")
                
                # Check if any symptoms exist at all
                print("\nChecking for any symptoms (including inactive)...")
                result_all = await session.execute(select(Symptom))
                all_symptoms = result_all.scalars().all()
                print(f"Total symptoms in database: {len(all_symptoms)}")
                
        except Exception as e:
            print(f"Error during query: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await session.close()
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_api_database())