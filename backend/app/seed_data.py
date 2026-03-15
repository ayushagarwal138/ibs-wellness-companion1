"""Seed initial data into the database."""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.symptom import Symptom
from app.models.diet import Food, FoodCategoryEnum, FODMAPLevelEnum
from app.models.food_item import FoodItem

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
        from sqlalchemy import select, func
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
        
        # Seed food_items table
        result = await session.execute(select(FoodItem).limit(1))
        if not result.scalar():
            import uuid
            food_items_data = [
                {"id": str(uuid.uuid4()), "name": "Chicken breast", "category": "proteins", "fodmap_level": "low", "calories_per_100g": 165, "protein_per_100g": 31, "carbs_per_100g": 0, "fat_per_100g": 3.6, "fiber_per_100g": 0, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Brown rice", "category": "grains", "fodmap_level": "low", "calories_per_100g": 216, "protein_per_100g": 5, "carbs_per_100g": 45, "fat_per_100g": 1.8, "fiber_per_100g": 1.8, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "White rice", "category": "grains", "fodmap_level": "low", "calories_per_100g": 206, "protein_per_100g": 4.3, "carbs_per_100g": 45, "fat_per_100g": 0.4, "fiber_per_100g": 0.4, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Salmon", "category": "proteins", "fodmap_level": "low", "calories_per_100g": 208, "protein_per_100g": 20, "carbs_per_100g": 0, "fat_per_100g": 13, "fiber_per_100g": 0, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Eggs", "category": "proteins", "fodmap_level": "low", "calories_per_100g": 155, "protein_per_100g": 13, "carbs_per_100g": 1.1, "fat_per_100g": 11, "fiber_per_100g": 0, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Banana", "category": "fruits", "fodmap_level": "moderate", "calories_per_100g": 89, "protein_per_100g": 1.1, "carbs_per_100g": 23, "fat_per_100g": 0.3, "fiber_per_100g": 2.6, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Blueberries", "category": "fruits", "fodmap_level": "low", "calories_per_100g": 57, "protein_per_100g": 0.7, "carbs_per_100g": 14, "fat_per_100g": 0.3, "fiber_per_100g": 2.4, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Spinach", "category": "vegetables", "fodmap_level": "low", "calories_per_100g": 23, "protein_per_100g": 2.9, "carbs_per_100g": 3.6, "fat_per_100g": 0.4, "fiber_per_100g": 2.2, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Carrots", "category": "vegetables", "fodmap_level": "low", "calories_per_100g": 41, "protein_per_100g": 0.9, "carbs_per_100g": 10, "fat_per_100g": 0.2, "fiber_per_100g": 2.8, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Broccoli", "category": "vegetables", "fodmap_level": "moderate", "calories_per_100g": 34, "protein_per_100g": 2.8, "carbs_per_100g": 7, "fat_per_100g": 0.4, "fiber_per_100g": 2.6, "common_triggers": True},
                {"id": str(uuid.uuid4()), "name": "Oats", "category": "grains", "fodmap_level": "moderate", "calories_per_100g": 389, "protein_per_100g": 17, "carbs_per_100g": 66, "fat_per_100g": 7, "fiber_per_100g": 10.6, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Greek yogurt", "category": "dairy", "fodmap_level": "moderate", "calories_per_100g": 59, "protein_per_100g": 10, "carbs_per_100g": 3.6, "fat_per_100g": 0.4, "fiber_per_100g": 0, "common_triggers": True},
                {"id": str(uuid.uuid4()), "name": "Almonds", "category": "proteins", "fodmap_level": "moderate", "calories_per_100g": 579, "protein_per_100g": 21, "carbs_per_100g": 22, "fat_per_100g": 50, "fiber_per_100g": 12.5, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Olive oil", "category": "fats_oils", "fodmap_level": "low", "calories_per_100g": 884, "protein_per_100g": 0, "carbs_per_100g": 0, "fat_per_100g": 100, "fiber_per_100g": 0, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Sweet potato", "category": "vegetables", "fodmap_level": "moderate", "calories_per_100g": 86, "protein_per_100g": 1.6, "carbs_per_100g": 20, "fat_per_100g": 0.1, "fiber_per_100g": 3, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Apple", "category": "fruits", "fodmap_level": "high", "calories_per_100g": 52, "protein_per_100g": 0.3, "carbs_per_100g": 14, "fat_per_100g": 0.2, "fiber_per_100g": 2.4, "common_triggers": True},
                {"id": str(uuid.uuid4()), "name": "Wheat bread", "category": "grains", "fodmap_level": "high", "calories_per_100g": 265, "protein_per_100g": 9, "carbs_per_100g": 49, "fat_per_100g": 3.2, "fiber_per_100g": 2.7, "common_triggers": True},
                {"id": str(uuid.uuid4()), "name": "Milk", "category": "dairy", "fodmap_level": "high", "calories_per_100g": 61, "protein_per_100g": 3.2, "carbs_per_100g": 4.8, "fat_per_100g": 3.3, "fiber_per_100g": 0, "common_triggers": True},
                {"id": str(uuid.uuid4()), "name": "Green tea", "category": "beverages", "fodmap_level": "low", "calories_per_100g": 1, "protein_per_100g": 0.2, "carbs_per_100g": 0.2, "fat_per_100g": 0, "fiber_per_100g": 0, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Coffee", "category": "beverages", "fodmap_level": "low", "calories_per_100g": 2, "protein_per_100g": 0.3, "carbs_per_100g": 0, "fat_per_100g": 0, "fiber_per_100g": 0, "common_triggers": True},
                {"id": str(uuid.uuid4()), "name": "Tofu", "category": "proteins", "fodmap_level": "low", "calories_per_100g": 76, "protein_per_100g": 8, "carbs_per_100g": 1.9, "fat_per_100g": 4.8, "fiber_per_100g": 0.3, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Quinoa", "category": "grains", "fodmap_level": "low", "calories_per_100g": 120, "protein_per_100g": 4.4, "carbs_per_100g": 21, "fat_per_100g": 1.9, "fiber_per_100g": 2.8, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Cucumber", "category": "vegetables", "fodmap_level": "low", "calories_per_100g": 16, "protein_per_100g": 0.7, "carbs_per_100g": 3.6, "fat_per_100g": 0.1, "fiber_per_100g": 0.5, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Tomato", "category": "vegetables", "fodmap_level": "low", "calories_per_100g": 18, "protein_per_100g": 0.9, "carbs_per_100g": 3.9, "fat_per_100g": 0.2, "fiber_per_100g": 1.2, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Dal (Lentils)", "category": "proteins", "fodmap_level": "moderate", "calories_per_100g": 116, "protein_per_100g": 9, "carbs_per_100g": 20, "fat_per_100g": 0.4, "fiber_per_100g": 7.9, "common_triggers": True},
                {"id": str(uuid.uuid4()), "name": "Roti (Wheat)", "category": "grains", "fodmap_level": "high", "calories_per_100g": 297, "protein_per_100g": 9.9, "carbs_per_100g": 55, "fat_per_100g": 3.7, "fiber_per_100g": 2.7, "common_triggers": True},
                {"id": str(uuid.uuid4()), "name": "Paneer", "category": "dairy", "fodmap_level": "moderate", "calories_per_100g": 265, "protein_per_100g": 18, "carbs_per_100g": 1.2, "fat_per_100g": 21, "fiber_per_100g": 0, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Basmati rice", "category": "grains", "fodmap_level": "low", "calories_per_100g": 210, "protein_per_100g": 4.4, "carbs_per_100g": 46, "fat_per_100g": 0.5, "fiber_per_100g": 0.6, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Curd (Yogurt)", "category": "dairy", "fodmap_level": "moderate", "calories_per_100g": 61, "protein_per_100g": 3.5, "carbs_per_100g": 4.7, "fat_per_100g": 3.3, "fiber_per_100g": 0, "common_triggers": True},
                # Indian foods
                {"id": str(uuid.uuid4()), "name": "Idli", "category": "grains", "fodmap_level": "low", "calories_per_100g": 58, "protein_per_100g": 2, "carbs_per_100g": 12, "fat_per_100g": 0.1, "fiber_per_100g": 0.5, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Dosa", "category": "grains", "fodmap_level": "low", "calories_per_100g": 168, "protein_per_100g": 4, "carbs_per_100g": 28, "fat_per_100g": 5, "fiber_per_100g": 1, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Poha", "category": "grains", "fodmap_level": "low", "calories_per_100g": 130, "protein_per_100g": 2.5, "carbs_per_100g": 28, "fat_per_100g": 0.5, "fiber_per_100g": 0.9, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Upma", "category": "grains", "fodmap_level": "moderate", "calories_per_100g": 135, "protein_per_100g": 3, "carbs_per_100g": 22, "fat_per_100g": 4, "fiber_per_100g": 1.2, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Paratha", "category": "grains", "fodmap_level": "high", "calories_per_100g": 300, "protein_per_100g": 7, "carbs_per_100g": 42, "fat_per_100g": 11, "fiber_per_100g": 2, "common_triggers": True},
                {"id": str(uuid.uuid4()), "name": "Aloo Paratha", "category": "grains", "fodmap_level": "high", "calories_per_100g": 320, "protein_per_100g": 7.5, "carbs_per_100g": 45, "fat_per_100g": 12, "fiber_per_100g": 2.5, "common_triggers": True},
                {"id": str(uuid.uuid4()), "name": "Sambar", "category": "proteins", "fodmap_level": "moderate", "calories_per_100g": 55, "protein_per_100g": 3, "carbs_per_100g": 8, "fat_per_100g": 1.5, "fiber_per_100g": 2, "common_triggers": True},
                {"id": str(uuid.uuid4()), "name": "Rajma (Kidney Beans)", "category": "proteins", "fodmap_level": "high", "calories_per_100g": 127, "protein_per_100g": 8.7, "carbs_per_100g": 22, "fat_per_100g": 0.5, "fiber_per_100g": 6.4, "common_triggers": True},
                {"id": str(uuid.uuid4()), "name": "Chana Dal", "category": "proteins", "fodmap_level": "moderate", "calories_per_100g": 164, "protein_per_100g": 8.9, "carbs_per_100g": 27, "fat_per_100g": 2.5, "fiber_per_100g": 5.7, "common_triggers": True},
                {"id": str(uuid.uuid4()), "name": "Moong Dal", "category": "proteins", "fodmap_level": "low", "calories_per_100g": 105, "protein_per_100g": 7, "carbs_per_100g": 19, "fat_per_100g": 0.4, "fiber_per_100g": 4, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Toor Dal", "category": "proteins", "fodmap_level": "moderate", "calories_per_100g": 116, "protein_per_100g": 7, "carbs_per_100g": 20, "fat_per_100g": 0.4, "fiber_per_100g": 5, "common_triggers": True},
                {"id": str(uuid.uuid4()), "name": "Aloo Sabzi", "category": "vegetables", "fodmap_level": "moderate", "calories_per_100g": 110, "protein_per_100g": 2, "carbs_per_100g": 18, "fat_per_100g": 4, "fiber_per_100g": 1.8, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Palak Paneer", "category": "dairy", "fodmap_level": "moderate", "calories_per_100g": 165, "protein_per_100g": 8, "carbs_per_100g": 6, "fat_per_100g": 13, "fiber_per_100g": 1.5, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Chicken Curry", "category": "proteins", "fodmap_level": "moderate", "calories_per_100g": 150, "protein_per_100g": 12, "carbs_per_100g": 5, "fat_per_100g": 9, "fiber_per_100g": 0.5, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Fish Curry", "category": "proteins", "fodmap_level": "low", "calories_per_100g": 130, "protein_per_100g": 14, "carbs_per_100g": 4, "fat_per_100g": 7, "fiber_per_100g": 0.3, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Khichdi", "category": "grains", "fodmap_level": "low", "calories_per_100g": 130, "protein_per_100g": 5, "carbs_per_100g": 24, "fat_per_100g": 2, "fiber_per_100g": 1.5, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Chapati", "category": "grains", "fodmap_level": "high", "calories_per_100g": 297, "protein_per_100g": 9.9, "carbs_per_100g": 55, "fat_per_100g": 3.7, "fiber_per_100g": 2.7, "common_triggers": True},
                {"id": str(uuid.uuid4()), "name": "Puri", "category": "grains", "fodmap_level": "high", "calories_per_100g": 340, "protein_per_100g": 7, "carbs_per_100g": 44, "fat_per_100g": 15, "fiber_per_100g": 1.5, "common_triggers": True},
                {"id": str(uuid.uuid4()), "name": "Rice (Cooked)", "category": "grains", "fodmap_level": "low", "calories_per_100g": 130, "protein_per_100g": 2.7, "carbs_per_100g": 28, "fat_per_100g": 0.3, "fiber_per_100g": 0.4, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Mango", "category": "fruits", "fodmap_level": "high", "calories_per_100g": 60, "protein_per_100g": 0.8, "carbs_per_100g": 15, "fat_per_100g": 0.4, "fiber_per_100g": 1.6, "common_triggers": True},
                {"id": str(uuid.uuid4()), "name": "Papaya", "category": "fruits", "fodmap_level": "low", "calories_per_100g": 43, "protein_per_100g": 0.5, "carbs_per_100g": 11, "fat_per_100g": 0.3, "fiber_per_100g": 1.7, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Guava", "category": "fruits", "fodmap_level": "low", "calories_per_100g": 68, "protein_per_100g": 2.6, "carbs_per_100g": 14, "fat_per_100g": 1, "fiber_per_100g": 5.4, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Coconut Water", "category": "beverages", "fodmap_level": "low", "calories_per_100g": 19, "protein_per_100g": 0.7, "carbs_per_100g": 3.7, "fat_per_100g": 0.2, "fiber_per_100g": 1.1, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Lassi (Sweet)", "category": "dairy", "fodmap_level": "high", "calories_per_100g": 70, "protein_per_100g": 3.5, "carbs_per_100g": 9, "fat_per_100g": 2, "fiber_per_100g": 0, "common_triggers": True},
                {"id": str(uuid.uuid4()), "name": "Buttermilk (Chaas)", "category": "dairy", "fodmap_level": "moderate", "calories_per_100g": 40, "protein_per_100g": 3.3, "carbs_per_100g": 4.8, "fat_per_100g": 1, "fiber_per_100g": 0, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Masala Chai", "category": "beverages", "fodmap_level": "moderate", "calories_per_100g": 35, "protein_per_100g": 1.5, "carbs_per_100g": 5, "fat_per_100g": 1, "fiber_per_100g": 0, "common_triggers": True},
                {"id": str(uuid.uuid4()), "name": "Bhindi (Okra)", "category": "vegetables", "fodmap_level": "low", "calories_per_100g": 33, "protein_per_100g": 1.9, "carbs_per_100g": 7, "fat_per_100g": 0.2, "fiber_per_100g": 3.2, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Lauki (Bottle Gourd)", "category": "vegetables", "fodmap_level": "low", "calories_per_100g": 14, "protein_per_100g": 0.6, "carbs_per_100g": 3.4, "fat_per_100g": 0, "fiber_per_100g": 0.5, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Tinda (Indian Round Gourd)", "category": "vegetables", "fodmap_level": "low", "calories_per_100g": 18, "protein_per_100g": 1.4, "carbs_per_100g": 3.5, "fat_per_100g": 0.2, "fiber_per_100g": 1.6, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Kadhi", "category": "dairy", "fodmap_level": "moderate", "calories_per_100g": 75, "protein_per_100g": 3, "carbs_per_100g": 8, "fat_per_100g": 3.5, "fiber_per_100g": 0.5, "common_triggers": True},
                {"id": str(uuid.uuid4()), "name": "Biryani (Chicken)", "category": "grains", "fodmap_level": "high", "calories_per_100g": 200, "protein_per_100g": 10, "carbs_per_100g": 25, "fat_per_100g": 7, "fiber_per_100g": 1, "common_triggers": True},
                {"id": str(uuid.uuid4()), "name": "Chole (Chickpeas)", "category": "proteins", "fodmap_level": "high", "calories_per_100g": 164, "protein_per_100g": 8.9, "carbs_per_100g": 27, "fat_per_100g": 2.6, "fiber_per_100g": 7.6, "common_triggers": True},
                {"id": str(uuid.uuid4()), "name": "Peanuts", "category": "proteins", "fodmap_level": "moderate", "calories_per_100g": 567, "protein_per_100g": 26, "carbs_per_100g": 16, "fat_per_100g": 49, "fiber_per_100g": 8.5, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Ghee", "category": "fats_oils", "fodmap_level": "low", "calories_per_100g": 900, "protein_per_100g": 0, "carbs_per_100g": 0, "fat_per_100g": 99.5, "fiber_per_100g": 0, "common_triggers": False},
                {"id": str(uuid.uuid4()), "name": "Coconut Milk", "category": "dairy", "fodmap_level": "moderate", "calories_per_100g": 230, "protein_per_100g": 2.3, "carbs_per_100g": 6, "fat_per_100g": 24, "fiber_per_100g": 2.2, "common_triggers": False},
            ]
            added = 0
            for fi in food_items_data:
                exists = await session.execute(
                    select(FoodItem).where(func.lower(FoodItem.name) == func.lower(fi["name"])).limit(1)
                )
                if not exists.scalar():
                    session.add(FoodItem(**fi))
                    added += 1
            print(f"Added {added} new food items")

        await session.commit()
        print("Seeding complete!")

if __name__ == "__main__":
    asyncio.run(seed())
