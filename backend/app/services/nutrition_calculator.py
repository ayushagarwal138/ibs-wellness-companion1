"""
Nutrition Calculator Service for accurate nutritional data calculation and analysis.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import re

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.food_item import FoodItem
from app.models.diet import DietLog


@dataclass
class NutritionData:
    """Comprehensive nutrition data structure."""

    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    sugar_g: float = 0.0
    sodium_mg: float = 0.0
    calcium_mg: float = 0.0
    iron_mg: float = 0.0
    vitamin_c_mg: float = 0.0
    vitamin_d_ug: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for JSON serialization."""
        return {
            "calories": self.calories,
            "protein_g": self.protein_g,
            "carbs_g": self.carbs_g,
            "fat_g": self.fat_g,
            "fiber_g": self.fiber_g,
            "sugar_g": self.sugar_g,
            "sodium_mg": self.sodium_mg,
            "calcium_mg": self.calcium_mg,
            "iron_mg": self.iron_mg,
            "vitamin_c_mg": self.vitamin_c_mg,
            "vitamin_d_ug": self.vitamin_d_ug,
        }


@dataclass
class MacronutrientBreakdown:
    """Macronutrient percentage breakdown."""

    carbs_percent: float
    protein_percent: float
    fat_percent: float
    fiber_percent: float

    def to_dict(self) -> Dict[str, float]:
        return {
            "carbohydrates": self.carbs_percent,
            "protein": self.protein_percent,
            "fat": self.fat_percent,
            "fiber": self.fiber_percent,
        }


@dataclass
class DailyNutritionSummary:
    """Daily nutrition summary with targets and analysis."""

    total_nutrition: NutritionData
    macronutrient_breakdown: MacronutrientBreakdown
    meals_count: int
    target_calories: Optional[float] = None
    calorie_deficit_surplus: Optional[float] = None
    nutrition_quality_score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_nutrition": self.total_nutrition.to_dict(),
            "macronutrient_breakdown": self.macronutrient_breakdown.to_dict(),
            "meals_count": self.meals_count,
            "target_calories": self.target_calories,
            "calorie_deficit_surplus": self.calorie_deficit_surplus,
            "nutrition_quality_score": self.nutrition_quality_score,
        }


class NutritionCalculator:
    """Service for calculating nutritional data from food items and portions."""

    def __init__(self, db: AsyncSession):
        self.db = db

        # Standard portion size mappings (in grams)
        self.portion_mappings = {
            # Common measurements
            "cup": 240,
            "cups": 240,
            "tablespoon": 15,
            "tablespoons": 15,
            "tbsp": 15,
            "teaspoon": 5,
            "teaspoons": 5,
            "tsp": 5,
            "ounce": 28.35,
            "ounces": 28.35,
            "oz": 28.35,
            "pound": 453.59,
            "pounds": 453.59,
            "lb": 453.59,
            "lbs": 453.59,
            "gram": 1,
            "grams": 1,
            "g": 1,
            "kilogram": 1000,
            "kilograms": 1000,
            "kg": 1000,
            # Food-specific portions
            "slice": 30,  # bread slice
            "slices": 30,
            "piece": 50,  # generic piece
            "pieces": 50,
            "medium": 150,  # medium fruit/vegetable
            "large": 200,
            "small": 100,
            "bowl": 200,
            "plate": 300,
            "serving": 100,
            "portion": 100,
        }

    def parse_portion_size(self, portion_str: str) -> float:
        """Parse portion size string and convert to grams."""
        if not portion_str:
            return 100.0  # Default 100g

        portion_str = portion_str.lower().strip()

        # Try to extract number and unit
        match = re.match(r"(\d*\.?\d+)\s*([a-zA-Z]+)", portion_str)
        if match:
            quantity = float(match.group(1))
            unit = match.group(2)

            if unit in self.portion_mappings:
                return quantity * self.portion_mappings[unit]

        # Try to extract just number (assume grams)
        number_match = re.match(r"(\d*\.?\d+)", portion_str)
        if number_match:
            return float(number_match.group(1))

        # Default fallback
        return 100.0

    async def get_food_nutrition_per_100g(
        self, food_name: str
    ) -> Optional[NutritionData]:
        """Get nutritional data per 100g for a specific food item."""
        query = select(FoodItem).filter(FoodItem.name.ilike(f"%{food_name}%"))
        result = await self.db.execute(query)
        food_item = result.scalar_one_or_none()

        if not food_item:
            return None

        return NutritionData(
            calories=float(food_item.calories_per_100g or 0),
            protein_g=float(food_item.protein_per_100g or 0),
            carbs_g=float(food_item.carbs_per_100g or 0),
            fat_g=float(food_item.fat_per_100g or 0),
            fiber_g=float(food_item.fiber_per_100g or 0),
        )

    def calculate_nutrition_for_portion(
        self, nutrition_per_100g: NutritionData, portion_grams: float
    ) -> NutritionData:
        """Calculate nutrition for a specific portion size."""
        multiplier = portion_grams / 100.0

        return NutritionData(
            calories=nutrition_per_100g.calories * multiplier,
            protein_g=nutrition_per_100g.protein_g * multiplier,
            carbs_g=nutrition_per_100g.carbs_g * multiplier,
            fat_g=nutrition_per_100g.fat_g * multiplier,
            fiber_g=nutrition_per_100g.fiber_g * multiplier,
            sugar_g=nutrition_per_100g.sugar_g * multiplier,
            sodium_mg=nutrition_per_100g.sodium_mg * multiplier,
            calcium_mg=nutrition_per_100g.calcium_mg * multiplier,
            iron_mg=nutrition_per_100g.iron_mg * multiplier,
            vitamin_c_mg=nutrition_per_100g.vitamin_c_mg * multiplier,
            vitamin_d_ug=nutrition_per_100g.vitamin_d_ug * multiplier,
        )

    async def calculate_meal_nutrition(
        self, food_items: List[str], portion_size: Optional[str] = None
    ) -> NutritionData:
        """Calculate total nutrition for a meal with multiple food items."""
        total_nutrition = NutritionData(0, 0, 0, 0, 0)

        # If portion size is provided, distribute it among all foods
        portion_grams = self.parse_portion_size(portion_size) if portion_size else 100.0
        portion_per_food = portion_grams / len(food_items) if food_items else 100.0

        for food_name in food_items:
            food_nutrition = await self.get_food_nutrition_per_100g(food_name)
            if food_nutrition:
                food_portion_nutrition = self.calculate_nutrition_for_portion(
                    food_nutrition, portion_per_food
                )

                # Add to total
                total_nutrition.calories += food_portion_nutrition.calories
                total_nutrition.protein_g += food_portion_nutrition.protein_g
                total_nutrition.carbs_g += food_portion_nutrition.carbs_g
                total_nutrition.fat_g += food_portion_nutrition.fat_g
                total_nutrition.fiber_g += food_portion_nutrition.fiber_g
                total_nutrition.sugar_g += food_portion_nutrition.sugar_g
                total_nutrition.sodium_mg += food_portion_nutrition.sodium_mg
                total_nutrition.calcium_mg += food_portion_nutrition.calcium_mg
                total_nutrition.iron_mg += food_portion_nutrition.iron_mg
                total_nutrition.vitamin_c_mg += food_portion_nutrition.vitamin_c_mg
                total_nutrition.vitamin_d_ug += food_portion_nutrition.vitamin_d_ug

        return total_nutrition

    def calculate_macronutrient_breakdown(
        self, nutrition: NutritionData
    ) -> MacronutrientBreakdown:
        """Calculate macronutrient percentage breakdown."""
        total_calories = nutrition.calories

        if total_calories == 0:
            return MacronutrientBreakdown(0, 0, 0, 0)

        # Calculate calories from each macronutrient
        carb_calories = nutrition.carbs_g * 4  # 4 calories per gram
        protein_calories = nutrition.protein_g * 4  # 4 calories per gram
        fat_calories = nutrition.fat_g * 9  # 9 calories per gram

        # Calculate percentages
        carbs_percent = round((carb_calories / total_calories) * 100, 1)
        protein_percent = round((protein_calories / total_calories) * 100, 1)
        fat_percent = round((fat_calories / total_calories) * 100, 1)
        fiber_percent = (
            round((nutrition.fiber_g / nutrition.carbs_g) * 100, 1)
            if nutrition.carbs_g > 0
            else 0
        )

        return MacronutrientBreakdown(
            carbs_percent=carbs_percent,
            protein_percent=protein_percent,
            fat_percent=fat_percent,
            fiber_percent=fiber_percent,
        )

    async def calculate_daily_nutrition_summary(
        self, user_id: str, date: datetime
    ) -> DailyNutritionSummary:
        """Calculate comprehensive daily nutrition summary."""
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)

        # Get all diet logs for the day
        query = select(DietLog).filter(
            and_(
                DietLog.user_id == user_id,
                DietLog.consumed_at >= start_date,
                DietLog.consumed_at < end_date,
            )
        )
        result = await self.db.execute(query)
        diet_logs = result.scalars().all()

        total_nutrition = NutritionData(0, 0, 0, 0, 0)
        meals_count = len(diet_logs)

        # Calculate total nutrition from all meals
        for log in diet_logs:
            if log.food_items:
                # Parse food items from JSON
                try:
                    if isinstance(log.food_items, str):
                        food_items = json.loads(log.food_items)
                    else:
                        food_items = log.food_items

                    # Extract food names
                    food_names = []
                    if isinstance(food_items, list):
                        for item in food_items:
                            if isinstance(item, dict) and "name" in item:
                                food_names.append(item["name"])
                            elif isinstance(item, str):
                                food_names.append(item)

                    meal_nutrition = await self.calculate_meal_nutrition(
                        food_names, log.portion_size
                    )

                    # Add to total
                    total_nutrition.calories += meal_nutrition.calories
                    total_nutrition.protein_g += meal_nutrition.protein_g
                    total_nutrition.carbs_g += meal_nutrition.carbs_g
                    total_nutrition.fat_g += meal_nutrition.fat_g
                    total_nutrition.fiber_g += meal_nutrition.fiber_g

                except (json.JSONDecodeError, TypeError):
                    continue

        # Calculate macronutrient breakdown
        macronutrient_breakdown = self.calculate_macronutrient_breakdown(
            total_nutrition
        )

        # Calculate nutrition quality score (simplified)
        nutrition_quality_score = self._calculate_nutrition_quality_score(
            total_nutrition
        )

        return DailyNutritionSummary(
            total_nutrition=total_nutrition,
            macronutrient_breakdown=macronutrient_breakdown,
            meals_count=meals_count,
            nutrition_quality_score=nutrition_quality_score,
        )

    def _calculate_nutrition_quality_score(self, nutrition: NutritionData) -> float:
        """Calculate a nutrition quality score (0-100)."""
        score = 0.0

        # Fiber score (0-25 points)
        if nutrition.fiber_g >= 25:
            score += 25
        else:
            score += (nutrition.fiber_g / 25) * 25

        # Protein score (0-25 points)
        protein_calories = nutrition.protein_g * 4
        total_calories = nutrition.calories
        if total_calories > 0:
            protein_percent = (protein_calories / total_calories) * 100
            if 15 <= protein_percent <= 35:  # Optimal protein range
                score += 25
            else:
                score += max(0, 25 - abs(protein_percent - 25) * 2)

        # Fat balance score (0-25 points)
        fat_calories = nutrition.fat_g * 9
        if total_calories > 0:
            fat_percent = (fat_calories / total_calories) * 100
            if 20 <= fat_percent <= 35:  # Optimal fat range
                score += 25
            else:
                score += max(0, 25 - abs(fat_percent - 27.5) * 2)

        # Calorie adequacy score (0-25 points)
        if 1200 <= nutrition.calories <= 2500:  # Reasonable calorie range
            score += 25
        else:
            if nutrition.calories < 1200:
                score += (nutrition.calories / 1200) * 25
            else:
                score += max(0, 25 - ((nutrition.calories - 2500) / 1000) * 10)

        return round(min(100, max(0, score)), 1)

    async def get_nutrition_trends(
        self, user_id: str, days: int = 30
    ) -> Dict[str, Any]:
        """Get nutrition trends over a specified period."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        daily_summaries = []
        current_date = start_date

        while current_date < end_date:
            summary = await self.calculate_daily_nutrition_summary(
                user_id, current_date
            )
            daily_summaries.append(
                {
                    "date": current_date.strftime("%Y-%m-%d"),
                    "summary": summary.to_dict(),
                }
            )
            current_date += timedelta(days=1)

        # Calculate averages and trends
        total_days = len(daily_summaries)
        if total_days == 0:
            return {}

        avg_calories = (
            sum(s["summary"]["total_nutrition"]["calories"] for s in daily_summaries)
            / total_days
        )
        avg_protein = (
            sum(s["summary"]["total_nutrition"]["protein_g"] for s in daily_summaries)
            / total_days
        )
        avg_carbs = (
            sum(s["summary"]["total_nutrition"]["carbs_g"] for s in daily_summaries)
            / total_days
        )
        avg_fat = (
            sum(s["summary"]["total_nutrition"]["fat_g"] for s in daily_summaries)
            / total_days
        )
        avg_fiber = (
            sum(s["summary"]["total_nutrition"]["fiber_g"] for s in daily_summaries)
            / total_days
        )

        return {
            "period_days": days,
            "daily_summaries": daily_summaries,
            "averages": {
                "calories": round(avg_calories, 1),
                "protein_g": round(avg_protein, 1),
                "carbs_g": round(avg_carbs, 1),
                "fat_g": round(avg_fat, 1),
                "fiber_g": round(avg_fiber, 1),
            },
            "recommendations": self._generate_nutrition_recommendations(
                avg_calories, avg_protein, avg_carbs, avg_fat, avg_fiber
            ),
        }

    def _generate_nutrition_recommendations(
        self,
        avg_calories: float,
        avg_protein: float,
        avg_carbs: float,
        avg_fat: float,
        avg_fiber: float,
    ) -> List[str]:
        """Generate personalized nutrition recommendations."""
        recommendations = []

        if avg_fiber < 25:
            recommendations.append(
                "Increase fiber intake with more vegetables, fruits, and whole grains"
            )

        if avg_protein < 50:
            recommendations.append(
                "Consider adding more protein sources like lean meats, legumes, or dairy"
            )

        if avg_calories < 1200:
            recommendations.append(
                "Your calorie intake may be too low - consider consulting a nutritionist"
            )

        protein_percent = (
            (avg_protein * 4 / avg_calories) * 100 if avg_calories > 0 else 0
        )
        if protein_percent < 15:
            recommendations.append(
                "Aim for 15-35% of calories from protein for optimal health"
            )

        fat_percent = (avg_fat * 9 / avg_calories) * 100 if avg_calories > 0 else 0
        if fat_percent > 35:
            recommendations.append(
                "Consider reducing fat intake and focus on healthy fats"
            )

        if not recommendations:
            recommendations.append(
                "Your nutrition profile looks balanced - keep up the good work!"
            )

        return recommendations
