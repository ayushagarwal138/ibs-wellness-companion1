#!/usr/bin/env python3
"""
Script to verify and enhance nutritional information in the food_items
database. This script checks for completeness and accuracy of nutritional data.
"""

import asyncio
import sys
import os
from sqlalchemy import text

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
sys.path.append(backend_path)

# Import with proper error handling
AsyncSessionLocal = None
try:
    from app.core.database import AsyncSessionLocal  # noqa: E402
except ImportError:  # noqa: F401
    print("Warning: Could not import database module.")
    print("Ensure backend dependencies are installed.")


async def verify_food_nutrition():
    """Verify nutritional completeness of food items."""
    if AsyncSessionLocal is None:
        print("Error: Database connection not available.")
        return
    
    async with AsyncSessionLocal() as db:
        print("🔍 Verifying Food Items Database...")
        print("=" * 50)
        
        # Get total count
        total_count = await db.execute(text(
            "SELECT COUNT(*) FROM food_items"
        ))
        total = total_count.scalar()
        print(f"📊 Total food items: {total}")
        
        # Check for missing nutritional information
        missing_calories = await db.execute(text(
            "SELECT COUNT(*) FROM food_items "
            "WHERE calories_per_100g IS NULL"
        ))
        missing_protein = await db.execute(text(
            "SELECT COUNT(*) FROM food_items "
            "WHERE protein_per_100g IS NULL"
        ))
        missing_carbs = await db.execute(text(
            "SELECT COUNT(*) FROM food_items "
            "WHERE carbs_per_100g IS NULL"
        ))
        missing_fat = await db.execute(text(
            "SELECT COUNT(*) FROM food_items "
            "WHERE fat_per_100g IS NULL"
        ))
        missing_fiber = await db.execute(text(
            "SELECT COUNT(*) FROM food_items "
            "WHERE fiber_per_100g IS NULL"
        ))
        
        print("\n🔍 Nutritional Completeness Check:")
        print(f"❌ Missing calories: {missing_calories.scalar()}")
        print(f"❌ Missing protein: {missing_protein.scalar()}")
        print(f"❌ Missing fat: {missing_fat.scalar()}")
        print(f"❌ Missing carbs: {missing_carbs.scalar()}")
        print(f"❌ Missing fiber: {missing_fiber.scalar()}")
        
        # Check FODMAP distribution with percentages
        fodmap_stats = await db.execute(text("""
            SELECT 
                fodmap_level,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (
                    SELECT COUNT(*) FROM food_items
                ), 2) as percentage
            FROM food_items 
            GROUP BY fodmap_level 
            ORDER BY count DESC
        """))
        
        print("\n📊 FODMAP Level Distribution:")
        for row in fodmap_stats:
            print(f"  - {row[0]}: {row[1]} items ({row[2]}%)")
        
        # Check categories
        category_stats = await db.execute(text(
            "SELECT category, COUNT(*) FROM food_items "
            "GROUP BY category ORDER BY COUNT(*) DESC"
        ))
        
        print("\n🏷️ Food Categories:")
        for row in category_stats:
            print(f"  - {row[0]}: {row[1]} items")
        
        # Check trigger foods
        trigger_foods = await db.execute(text(
            "SELECT COUNT(*) FROM food_items "
            "WHERE common_triggers = true"
        ))
        trigger_count = trigger_foods.scalar()
        print(f"\n⚠️ Common trigger foods: {trigger_count}")
        
        # Sample nutritional data
        sample_data = await db.execute(text(
            "SELECT name, calories_per_100g, protein_per_100g, "
            "carbs_per_100g FROM food_items LIMIT 5"
        ))
        
        print("\n📋 Sample Nutritional Data:")
        print("-" * 60)
        print(f"{'Food Name':>25} {'Cal':>8} {'Protein':>8} {'Carbs':>8}")
        print("-" * 60)
        for row in sample_data:
            print(f"{row[0]:>25} {row[1]:>8} {row[2]:>8} {row[3]:>8}")
        
        # Find foods with highest protein content
        high_protein = await db.execute(text("""
            SELECT name, protein_per_100g, category 
            FROM food_items 
            WHERE protein_per_100g IS NOT NULL 
            ORDER BY protein_per_100g DESC 
            LIMIT 10
        """))
        
        print("\n💪 Top High-Protein Foods:")
        print("-" * 50)
        print(f"{'Food Name':>25} {'Protein (g)':>12} {'Category':>15}")
        print("-" * 50)
        for row in high_protein:
            print(f"{row[0]:>25} {row[1]:>12} {row[2]:>15}")
        
        # Find low-FODMAP, high-fiber foods
        high_fiber = await db.execute(text("""
            SELECT name, fiber_per_100g, category 
            FROM food_items 
            WHERE fodmap_level = 'low' 
            AND fiber_per_100g IS NOT NULL 
            AND fiber_per_100g > 5 
            ORDER BY fiber_per_100g DESC 
            LIMIT 10
        """))
        
        print("\n🌾 Top High-Fiber, Low-FODMAP Foods:")
        print("-" * 50)
        print(
            f"{'Food Name':>25} {'Fiber (g)':>10} {'Category':>15}"
        )
        print("-" * 50)
        for row in high_fiber:
            print(f"{row[0]:>25} {row[1]:>10} {row[2]:>15}")
        
        # Check for potential data quality issues
        unusual_calories = await db.execute(text("""
            SELECT name, calories_per_100g 
            FROM food_items 
            WHERE calories_per_100g > 800 OR calories_per_100g < 10
        """))
        
        print("\n⚠️ Foods with Unusual Calorie Values:")
        for row in unusual_calories:
            print(f"  - {row[0]}: {row[1]} cal/100g")


async def suggest_enhancements():
    """Suggest enhancements to the food database."""
    print("\n💡 Suggested Enhancements:")
    print("-" * 40)
    print("1. Add sodium content (mg per 100g)")
    print("2. Add sugar content (g per 100g)")
    print("3. Add glycemic index values")
    print("4. Add digestibility scores (1-10)")
    print("5. Add preparation methods (raw, cooked, etc.)")
    print("6. Add allergen information")
    print("7. Add seasonal availability")
    print("8. Add regional cuisine tags")
    print("9. Add cooking time estimates")
    print("10. Add portion size recommendations")
    
    print("\n🎯 IBS-Specific Enhancements:")
    print("-" * 40)
    print("1. Add fermentation potential scores")
    print("2. Add gut transit time impact")
    print("3. Add bloating risk levels")
    print("4. Add probiotic/prebiotic content")
    print("5. Add anti-inflammatory properties")


async def main():
    """Main function to run all verification tasks."""
    await verify_food_nutrition()
    await suggest_enhancements()


if __name__ == "__main__":
    asyncio.run(main())