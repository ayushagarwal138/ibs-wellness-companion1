#!/usr/bin/env python3
"""
Script to create symptom reference data in the database.
"""

import sys
import os
import asyncio

# Add the backend directory to the path
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
            print(f"Current symptoms in database: {existing_count}")
            
            symptoms_data = [
                # Digestive symptoms
                {"name": "Abdominal Pain", "description": "Pain or discomfort in the abdominal area", "category": "digestive"},
                {"name": "Bloating", "description": "Feeling of fullness or swelling in the abdomen", "category": "digestive"},
                {"name": "Gas", "description": "Excessive gas or flatulence", "category": "digestive"},
                {"name": "Diarrhea", "description": "Loose or watery bowel movements", "category": "digestive"},
                {"name": "Constipation", "description": "Difficulty passing stool or infrequent bowel movements", "category": "digestive"},
                {"name": "Urgency", "description": "Sudden, strong urge to have a bowel movement", "category": "digestive"},
                {"name": "Incomplete Evacuation", "description": "Feeling that bowel movement is not complete", "category": "digestive"},
                {"name": "Cramping", "description": "Painful muscle contractions in the abdomen", "category": "digestive"},
                {"name": "Nausea", "description": "Feeling of sickness with an inclination to vomit", "category": "digestive"},
                
                # Pain symptoms
                {"name": "Lower Abdominal Pain", "description": "Pain in the lower part of the abdomen", "category": "pain"},
                {"name": "Upper Abdominal Pain", "description": "Pain in the upper part of the abdomen", "category": "pain"},
                {"name": "Back Pain", "description": "Pain in the back area", "category": "pain"},
                {"name": "Pelvic Pain", "description": "Pain in the pelvic region", "category": "pain"},
                
                # Systemic symptoms
                {"name": "Fatigue", "description": "Feeling of tiredness or lack of energy", "category": "systemic"},
                {"name": "Headache", "description": "Pain in the head or neck area", "category": "systemic"},
                {"name": "Dizziness", "description": "Feeling of unsteadiness or lightheadedness", "category": "systemic"},
                {"name": "Weakness", "description": "Lack of physical strength", "category": "systemic"},
                
                # Mood and mental symptoms
                {"name": "Anxiety", "description": "Feeling of worry, nervousness, or unease", "category": "mental"},
                {"name": "Depression", "description": "Feeling of sadness or low mood", "category": "mental"},
                {"name": "Irritability", "description": "Feeling easily annoyed or made angry", "category": "mental"},
                {"name": "Brain Fog", "description": "Difficulty concentrating or thinking clearly", "category": "mental"},
                
                # Sleep and energy symptoms
                {"name": "Insomnia", "description": "Difficulty falling or staying asleep", "category": "sleep"},
                {"name": "Poor Sleep Quality", "description": "Non-restful or interrupted sleep", "category": "sleep"},
                {"name": "Daytime Sleepiness", "description": "Excessive sleepiness during the day", "category": "sleep"},
                
                # Other symptoms
                {"name": "Loss of Appetite", "description": "Reduced desire to eat", "category": "other"},
                {"name": "Food Intolerance", "description": "Adverse reaction to certain foods", "category": "other"},
                {"name": "Heartburn", "description": "Burning sensation in the chest", "category": "other"},
                {"name": "Acid Reflux", "description": "Stomach acid backing up into the esophagus", "category": "other"},
                {"name": "Mucus in Stool", "description": "Presence of mucus in bowel movements", "category": "digestive"},
                {"name": "Blood in Stool", "description": "Presence of blood in bowel movements", "category": "digestive"},
                {"name": "Excessive Burping", "description": "Frequent belching or burping", "category": "digestive"},
                {"name": "Stomach Rumbling", "description": "Audible sounds from the stomach", "category": "digestive"},
            ]
            
            # Get existing symptom names to avoid duplicates
            result = await db.execute(select(Symptom.name))
            existing_names = {row[0] for row in result.all()}
            
            # Create symptoms that don't already exist
            created_count = 0
            for symptom_data in symptoms_data:
                if symptom_data["name"] not in existing_names:
                    symptom = Symptom(
                        name=symptom_data["name"],
                        description=symptom_data["description"],
                        category=symptom_data["category"],
                        is_active=True
                    )
                    db.add(symptom)
                    created_count += 1
                    print(f"Adding symptom: {symptom_data['name']}")
                else:
                    print(f"Symptom already exists: {symptom_data['name']}")
            
            await db.commit()
            print(f"Successfully created {created_count} new symptoms.")
            
            # Verify final count
            result = await db.execute(select(func.count(Symptom.id)))
            final_count = result.scalar()
            print(f"Total symptoms in database: {final_count}")
            
        except Exception as e:
            print(f"Error creating symptoms: {e}")
            await db.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(create_symptoms())