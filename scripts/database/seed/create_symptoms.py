#!/usr/bin/env python3
"""
Script to create symptom reference data in the database.
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select, func
from app.core.database import AsyncSessionLocal
from app.models.symptom import Symptom

async def create_symptoms():
    """Create symptom reference data."""
    async with AsyncSessionLocal() as db:
        try:
            # Check if symptoms already exist
            result = await db.execute(select(func.count(Symptom.id)))
            existing_count = result.scalar()
            if existing_count > 0:
                print(f"Symptoms already exist ({existing_count} found). Skipping creation.")
                return
            
            symptoms_data = [
                # Digestive symptoms
                {"name": "Abdominal Pain", "description": "Pain or discomfort in the abdominal area", "category": "digestive"},
                {"name": "Bloating", "description": "Feeling of fullness or swelling in the abdomen", "category": "digestive"},
                {"name": "Gas", "description": "Excessive gas or flatulence", "category": "digestive"},
                {"name": "Diarrhea", "description": "Loose or watery bowel movements", "category": "digestive"},
                {"name": "Constipation", "description": "Difficulty passing stool or infrequent bowel movements", "category": "digestive"},
                {"name": "Urgency", "description": "Sudden, strong urge to have a bowel movement", "category": "digestive"},
                {"name": "Incomplete Evacuation", "description": "Feeling that bowel movement is not complete", "category": "digestive"},
                {"name": "Nausea", "description": "Feeling of sickness or urge to vomit", "category": "digestive"},
                {"name": "Cramping", "description": "Sharp, sudden abdominal pain", "category": "digestive"},
                {"name": "Stomach Gurgling", "description": "Audible sounds from the digestive system", "category": "digestive"},
                
                # Pain symptoms
                {"name": "Lower Abdominal Pain", "description": "Pain in the lower part of the abdomen", "category": "pain"},
                {"name": "Upper Abdominal Pain", "description": "Pain in the upper part of the abdomen", "category": "pain"},
                {"name": "Back Pain", "description": "Pain in the back area", "category": "pain"},
                {"name": "Pelvic Pain", "description": "Pain in the pelvic region", "category": "pain"},
                
                # Systemic symptoms
                {"name": "Fatigue", "description": "Feeling of tiredness or lack of energy", "category": "systemic"},
                {"name": "Headache", "description": "Pain in the head or neck area", "category": "systemic"},
                {"name": "Muscle Aches", "description": "Pain or soreness in muscles", "category": "systemic"},
                {"name": "Joint Pain", "description": "Pain in joints", "category": "systemic"},
                
                # Mood and psychological symptoms
                {"name": "Anxiety", "description": "Feeling of worry, nervousness, or unease", "category": "mood"},
                {"name": "Depression", "description": "Feeling of sadness or low mood", "category": "mood"},
                {"name": "Irritability", "description": "Feeling easily annoyed or frustrated", "category": "mood"},
                {"name": "Stress", "description": "Feeling overwhelmed or under pressure", "category": "mood"},
                
                # Sleep and energy symptoms
                {"name": "Insomnia", "description": "Difficulty falling or staying asleep", "category": "sleep"},
                {"name": "Poor Sleep Quality", "description": "Non-restful or interrupted sleep", "category": "sleep"},
                {"name": "Daytime Sleepiness", "description": "Excessive sleepiness during the day", "category": "sleep"},
                
                # Other symptoms
                {"name": "Loss of Appetite", "description": "Reduced desire to eat", "category": "other"},
                {"name": "Food Intolerance", "description": "Adverse reaction to certain foods", "category": "other"},
                {"name": "Heartburn", "description": "Burning sensation in the chest", "category": "other"},
                {"name": "Acid Reflux", "description": "Stomach acid backing up into the esophagus", "category": "other"},
            ]
            
            # Create symptoms
            created_count = 0
            for symptom_data in symptoms_data:
                symptom = Symptom(
                    name=symptom_data["name"],
                    description=symptom_data["description"],
                    category=symptom_data["category"],
                    is_active=True
                )
                db.add(symptom)
                created_count += 1
            
            await db.commit()
            print(f"Successfully created {created_count} symptoms.")
            
            # Verify creation
            result = await db.execute(select(func.count(Symptom.id)))
            total_count = result.scalar()
            print(f"Total symptoms in database: {total_count}")
            
        except Exception as e:
            print(f"Error creating symptoms: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(create_symptoms())