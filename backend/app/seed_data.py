"""Seed initial data into the database."""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.symptom import Symptom
from app.models.diet import Food, FoodCategoryEnum, FODMAPLevelEnum

SYMPTOMS = [
    {"name": "Abdominal Pain", "category": "pain", "description": "Pain or cramping in the abdomen"},
    {"name": "Bloating", "category": "digestive", "description": "Feeling of fullness or swelling in abdomen"},
    {"name": "Diarrhea", "category": "digestive", "description": "Loose or watery stools"},
    {"name": "Constipation", "category": "digestive", "description": "Difficulty passing stools"},
    {"name": "Gas/Flatulence", "category": "digestive", "description": "Excess gas in digestive system"},
    {"name": "Nausea", "category": "digestive", "description": "Feeling of sickness with urge to vomit"},
    {"name": "Fatigue", "category": "general", "description": "Extreme tiredness or lack of energy"},
    {"name": "Urgency", "category": "digestive", "description": "Sudden urgent need to use bathroom"},
    {"name": "Mucus in Stool", "category": "digestive", "description": "Presence of mucus in bowel movements"},
    {"name": "Incomplete Evacuation", "category": "digestive", "description": "Feeling of incomplete bowel movement"},
    {"name": "Heartburn", "category": "digestive", "description": "Burning sensation in chest or throat"},
    {"name": "Loss of Appetite", "category": "general", "description": "Reduced desire to eat"},
    {"name": "Anxiety", "category": "mood", "description": "Feeling of worry or nervousness"},
    {"name": "Brain Fog", "category": "general", "description": "Difficulty thinking clearly or concentrating"},
    {"name": "Back Pain", "category": "pain", "description": "Pain in the lower back area"},
]

FOODS = [
    {"name": "Chicken breast", "category": FoodCategoryEnum.PROTEINS, "calories_per_100g": 165, "protein_g": 31, "carbs_g": 0, "fat_g": 3.6, "fodmap_level": FODMAPLevelEnum.LOW},
    {"name": "Brown rice", "category": FoodCategoryEnum.GRAINS, "calories_per_100g": 216, "protein_g": 5, "carbs_g": 45, "fat_g": 1.8, "fodmap_level": FODMAPLevelEnum.LOW},
    {"name": "White rice", "category": FoodCategoryEnum.GRAINS, "calories_per_100g": 206, "protein_g": 4.3, "carbs_g": 45, "fat_g": 0.4, "fodmap_level": FODMAPLevelEnum.LOW},
    {"name": "Salmon", "category": FoodCategoryEnum.PROTEINS, "calories_per_100g": 208, "protein_g": 20, "carbs_g": 0, "fat_g": 13, "fodmap_level": FODMAPLevelEnum.LOW},
    {"name": "Eggs", "category": FoodCategoryEnum.PROTEINS, "calories_per_100g": 155, "protein_g": 13, "carbs_g": 1.1, "fat_g": 11, "fodmap_level": FODMAPLevelEnum.LOW},
    {"name": "Banana", "category": FoodCategoryEnum.FRUITS, "calories_per_100g": 89, "protein_g": 1.1, "carbs_g": 23, "fat_g": 0.3, "fodmap_level": FODMAPLevelEnum.MODERATE},
    {"name": "Blueberries", "category": FoodCategoryEnum.FRUITS, "calories_per_100g": 57, "protein_g": 0.7, "carbs_g": 14, "fat_g": 0.3, "fodmap_level": FODMAPLevelEnum.LOW},
    {"name": "Strawberries", "category": FoodCategoryEnum.FRUITS, "calories_per_100g": 32, "protein_g": 0.7, "carbs_g": 7.7, "fat_g": 0.3, "fodmap_level": FODMAPLevelEnum.LOW},
    {"name": "Spinach", "category": FoodCategoryEnum.VEGETABLES, "calories_per_100g": 23, "protein_g": 2.9, "carbs_g": 3.6, "fat_g": 0.4, "fodmap_level": FODMAPLevelEnum.LOW},
    {"name": "Carrots", "category": FoodCategoryEnum.VEGETABLES, "calories_per_100g": 41, "protein_g": 0.9, "carbs_g": 10, "fat_g": 0.2, "fodmap_level": FODMAPLevelEnum.LOW},
    {"name": "Broccoli", "category": FoodCategoryEnum.VEGETABLES, "calories_per_100g": 34, "protein_g": 2.8, "carbs_g": 7, "fat_g": 0.4, "fodmap_level": FODMAPLevelEnum.MODERATE},
    {"name": "Oats", "category": FoodCategoryEnum.GRAINS, "calories_per_100g": 389, "protein_g": 17, "carbs_g": 66, "fat_g": 7, "fodmap_level": FODMAPLevelEnum.MODERATE},
    {"name": "Greek yogurt", "category": FoodCategoryEnum.DAIRY, "calories_per_100g": 59, "protein_g": 10, "carbs_g": 3.6, "fat_g": 0.4, "fodmap_level": FODMAPLevelEnum.MODERATE},
    {"name": "Almonds", "category": FoodCategoryEnum.PROTEINS, "calories_per_100g": 579, "protein_g": 21, "carbs_g": 22, "fat_g": 50, "fodmap_level": FODMAPLevelEnum.MODERATE},
    {"name": "Olive oil", "category": FoodCategoryEnum.FATS_OILS, "calories_per_100g": 884, "protein_g": 0, "carbs_g": 0, "fat_g": 100, "fodmap_level": FODMAPLevelEnum.LOW},
    {"name": "Sweet potato", "category": FoodCategoryEnum.VEGETABLES, "calories_per_100g": 86, "protein_g": 1.6, "carbs_g": 20, "fat_g": 0.1, "fodmap_level": FODMAPLevelEnum.MODERATE},
    {"name": "Apple", "category": FoodCategoryEnum.FRUITS, "calories_per_100g": 52, "protein_g": 0.3, "carbs_g": 14, "fat_g": 0.2, "fodmap_level": FODMAPLevelEnum.HIGH},
    {"name": "Wheat bread", "category": FoodCategoryEnum.GRAINS, "calories_per_100g": 265, "protein_g": 9, "carbs_g": 49, "fat_g": 3.2, "fodmap_level": FODMAPLevelEnum.HIGH},
    {"name": "Milk", "category": FoodCategoryEnum.DAIRY, "calories_per_100g": 61, "protein_g": 3.2, "carbs_g": 4.8, "fat_g": 3.3, "fodmap_level": FODMAPLevelEnum.HIGH},
    {"name": "Green tea", "category": FoodCategoryEnum.BEVERAGES, "calories_per_100g": 1, "protein_g": 0.2, "carbs_g": 0.2, "fat_g": 0, "fodmap_level": FODMAPLevelEnum.LOW},
    {"name": "Coffee", "category": FoodCategoryEnum.BEVERAGES, "calories_per_100g": 2, "protein_g": 0.3, "carbs_g": 0, "fat_g": 0, "fodmap_level": FODMAPLevelEnum.LOW},
    {"name": "Tofu", "category": FoodCategoryEnum.PROTEINS, "calories_per_100g": 76, "protein_g": 8, "carbs_g": 1.9, "fat_g": 4.8, "fodmap_level": FODMAPLevelEnum.LOW},
    {"name": "Quinoa", "category": FoodCategoryEnum.GRAINS, "calories_per_100g": 120, "protein_g": 4.4, "carbs_g": 21, "fat_g": 1.9, "fodmap_level": FODMAPLevelEnum.LOW},
    {"name": "Cucumber", "category": FoodCategoryEnum.VEGETABLES, "calories_per_100g": 16, "protein_g": 0.7, "carbs_g": 3.6, "fat_g": 0.1, "fodmap_level": FODMAPLevelEnum.LOW},
    {"name": "Tomato", "category": FoodCategoryEnum.VEGETABLES, "calories_per_100g": 18, "protein_g": 0.9, "carbs_g": 3.9, "fat_g": 0.2, "fodmap_level": FODMAPLevelEnum.LOW},
]

async def seed():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Seed symptoms
        from sqlalchemy import select
        result = await session.execute(select(Symptom).limit(1))
        if not result.scalar():
            for s in SYMPTOMS:
                session.add(Symptom(**s, is_active=True))
            print(f"Added {len(SYMPTOMS)} symptoms")
        else:
            print("Symptoms already seeded")
        
        # Seed foods
        result = await session.execute(select(Food).limit(1))
        if not result.scalar():
            for f in FOODS:
                session.add(Food(**f, is_active=True))
            print(f"Added {len(FOODS)} foods")
        else:
            print("Foods already seeded")
        
        await session.commit()
        print("Seeding complete!")

if __name__ == "__main__":
    asyncio.run(seed())
