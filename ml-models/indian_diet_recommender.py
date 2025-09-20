"""
Indian Diet Recommendation System for IBS Management
Provides personalized Indian food recommendations based on user's IBS triggers and preferences.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

class IndianDietRecommender:
    """
    Personalized Indian diet recommendation system for IBS management.
    """
    
    def __init__(self, models_dir: str = "trained_models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        # Initialize Indian food databases
        self.indian_dishes = self._load_indian_dishes_database()
        self.spices_data = self._load_spices_database()
        self.regional_preferences = self._load_regional_preferences()
        self.fodmap_indian_foods = self._load_indian_fodmap_data()
        
    def _load_indian_dishes_database(self) -> pd.DataFrame:
        """Load comprehensive Indian dishes database."""
        dishes_data = {
            'dish_name': [
                'Dal Tadka', 'Khichdi', 'Curd Rice', 'Moong Dal Soup', 'Vegetable Upma',
                'Idli', 'Dosa', 'Sambar', 'Rasam', 'Coconut Rice',
                'Palak Paneer', 'Aloo Gobi', 'Bhindi Masala', 'Lauki Sabzi', 'Turai Sabzi',
                'Chapati', 'Brown Rice', 'Quinoa Pulao', 'Oats Khichdi', 'Millet Roti',
                'Buttermilk', 'Coconut Water', 'Herbal Tea', 'Jeera Water', 'Mint Tea',
                'Steamed Fish', 'Chicken Soup', 'Egg Curry', 'Paneer Tikka', 'Tofu Curry'
            ],
            'region': [
                'North', 'All', 'South', 'All', 'South',
                'South', 'South', 'South', 'South', 'South',
                'North', 'North', 'North', 'North', 'North',
                'All', 'All', 'All', 'All', 'All',
                'All', 'South', 'All', 'All', 'All',
                'All', 'All', 'All', 'North', 'All'
            ],
            'fodmap_level': [
                'Low', 'Low', 'Low', 'Low', 'Medium',
                'Low', 'Low', 'Medium', 'Low', 'Low',
                'Medium', 'Medium', 'Low', 'Low', 'Low',
                'Low', 'Low', 'Low', 'Low', 'Low',
                'Low', 'Low', 'Low', 'Low', 'Low',
                'Low', 'Low', 'Medium', 'Medium', 'Low'
            ],
            'spice_level': [3, 1, 1, 2, 2, 1, 2, 3, 2, 1, 4, 3, 3, 2, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 3, 3, 2],
            'fiber_content': ['High', 'High', 'Low', 'High', 'Medium', 'Medium', 'Medium', 'High', 'Low', 'Medium', 'High', 'High', 'High', 'High', 'High', 'High', 'High', 'High', 'High', 'High', 'Low', 'Low', 'Low', 'Low', 'Low', 'Low', 'Low', 'Medium', 'Medium', 'Medium'],
            'digestibility': ['Easy', 'Easy', 'Easy', 'Easy', 'Medium', 'Easy', 'Medium', 'Medium', 'Easy', 'Easy', 'Medium', 'Medium', 'Medium', 'Easy', 'Easy', 'Easy', 'Easy', 'Easy', 'Easy', 'Easy', 'Easy', 'Easy', 'Easy', 'Easy', 'Easy', 'Easy', 'Easy', 'Medium', 'Medium', 'Medium'],
            'meal_type': ['Lunch', 'All', 'All', 'All', 'Breakfast', 'Breakfast', 'Breakfast', 'Lunch', 'Lunch', 'Lunch', 'Lunch', 'Lunch', 'Lunch', 'Lunch', 'Lunch', 'All', 'All', 'Lunch', 'Breakfast', 'All', 'Snack', 'Snack', 'Snack', 'Snack', 'Snack', 'Lunch', 'Lunch', 'Lunch', 'Lunch', 'Lunch'],
            'ibs_friendly_score': [9, 10, 10, 9, 7, 9, 8, 6, 8, 9, 6, 7, 8, 9, 9, 9, 10, 8, 9, 8, 10, 10, 9, 9, 9, 8, 9, 6, 6, 7]
        }
        
        return pd.DataFrame(dishes_data)
    
    def _load_spices_database(self) -> pd.DataFrame:
        """Load Indian spices and their IBS impact."""
        spices_data = {
            'spice_name': [
                'Turmeric', 'Cumin', 'Coriander', 'Ginger', 'Fennel',
                'Cardamom', 'Cinnamon', 'Cloves', 'Asafoetida', 'Mint',
                'Fenugreek', 'Mustard Seeds', 'Curry Leaves', 'Ajwain', 'Black Pepper'
            ],
            'ibs_impact': ['Positive', 'Positive', 'Positive', 'Positive', 'Positive', 'Positive', 'Positive', 'Neutral', 'Positive', 'Positive', 'Neutral', 'Neutral', 'Positive', 'Positive', 'Neutral'],
            'digestive_benefit': ['Anti-inflammatory', 'Digestive', 'Digestive', 'Anti-nausea', 'Carminative', 'Digestive', 'Warming', 'Antiseptic', 'Digestive', 'Cooling', 'Digestive', 'Stimulant', 'Antioxidant', 'Carminative', 'Stimulant'],
            'recommended_amount': ['1/2 tsp', '1/2 tsp', '1 tsp', '1 inch', '1/2 tsp', '2-3 pods', '1 stick', '2-3 pieces', 'Pinch', '1 tbsp', '1/4 tsp', '1/4 tsp', '8-10 leaves', '1/4 tsp', '1/4 tsp']
        }
        
        return pd.DataFrame(spices_data)
    
    def _load_regional_preferences(self) -> Dict[str, List[str]]:
        """Load regional Indian food preferences."""
        return {
            'North': ['Dal Tadka', 'Palak Paneer', 'Aloo Gobi', 'Chapati', 'Paneer Tikka'],
            'South': ['Idli', 'Dosa', 'Sambar', 'Rasam', 'Coconut Rice', 'Curd Rice'],
            'East': ['Fish Curry', 'Rice', 'Dal', 'Vegetable Curry'],
            'West': ['Dhokla', 'Thepla', 'Dal Dhokli', 'Khichdi'],
            'Central': ['Poha', 'Bhutte ka Kees', 'Dal Bafla', 'Khichdi']
        }
    
    def _load_indian_fodmap_data(self) -> Dict[str, str]:
        """Load FODMAP levels for Indian foods."""
        return {
            'Rice': 'Low', 'Wheat': 'High', 'Moong Dal': 'Low', 'Chana Dal': 'Medium',
            'Toor Dal': 'Low', 'Urad Dal': 'Medium', 'Coconut': 'Low', 'Ginger': 'Low',
            'Turmeric': 'Low', 'Cumin': 'Low', 'Coriander': 'Low', 'Onion': 'High',
            'Garlic': 'High', 'Tomato': 'Low', 'Potato': 'Low', 'Carrot': 'Low',
            'Spinach': 'Low', 'Bottle Gourd': 'Low', 'Ridge Gourd': 'Low', 'Okra': 'Low'
        }
    
    def generate_personalized_recommendations(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized Indian diet recommendations based on user's IBS profile.
        
        Args:
            user_profile: Dictionary containing user's preferences and IBS triggers
            
        Returns:
            Dictionary with personalized recommendations
        """
        logger.info("Generating personalized Indian diet recommendations...")
        
        # Extract user preferences
        ibs_severity = user_profile.get('ibs_severity_score', 5)
        spice_tolerance = user_profile.get('spice_tolerance', 3)
        regional_preference = user_profile.get('regional_preference', 'All')
        dietary_restrictions = user_profile.get('dietary_restrictions', [])
        trigger_foods = user_profile.get('trigger_foods', [])
        preferred_meal_times = user_profile.get('preferred_meal_times', ['Breakfast', 'Lunch', 'Dinner'])
        
        # Filter dishes based on user profile
        suitable_dishes = self._filter_suitable_dishes(
            ibs_severity, spice_tolerance, regional_preference, 
            dietary_restrictions, trigger_foods
        )
        
        # Generate meal plan
        meal_plan = self._create_weekly_meal_plan(suitable_dishes, preferred_meal_times)
        
        # Generate spice recommendations
        spice_recommendations = self._get_beneficial_spices(ibs_severity)
        
        # Generate lifestyle tips
        lifestyle_tips = self._get_indian_lifestyle_tips(user_profile)
        
        # Calculate nutritional insights
        nutritional_insights = self._calculate_nutritional_insights(suitable_dishes)
        
        return {
            'recommended_dishes': suitable_dishes.to_dict('records'),
            'weekly_meal_plan': meal_plan,
            'beneficial_spices': spice_recommendations,
            'lifestyle_tips': lifestyle_tips,
            'nutritional_insights': nutritional_insights,
            'personalization_score': self._calculate_personalization_score(user_profile, suitable_dishes),
            'generated_at': datetime.now().isoformat()
        }
    
    def _filter_suitable_dishes(self, ibs_severity: int, spice_tolerance: int, 
                              regional_preference: str, dietary_restrictions: List[str],
                              trigger_foods: List[str]) -> pd.DataFrame:
        """Filter dishes based on user's IBS profile and preferences."""
        
        dishes = self.indian_dishes.copy()
        
        # Filter by IBS severity (higher severity = need gentler foods)
        if ibs_severity >= 7:
            dishes = dishes[dishes['ibs_friendly_score'] >= 8]
            dishes = dishes[dishes['digestibility'] == 'Easy']
        elif ibs_severity >= 4:
            dishes = dishes[dishes['ibs_friendly_score'] >= 6]
        
        # Filter by spice tolerance
        dishes = dishes[dishes['spice_level'] <= spice_tolerance]
        
        # Filter by regional preference
        if regional_preference != 'All':
            dishes = dishes[
                (dishes['region'] == regional_preference) | 
                (dishes['region'] == 'All')
            ]
        
        # Filter by FODMAP level for severe IBS
        if ibs_severity >= 7:
            dishes = dishes[dishes['fodmap_level'] == 'Low']
        elif ibs_severity >= 4:
            dishes = dishes[dishes['fodmap_level'].isin(['Low', 'Medium'])]
        
        # Apply dietary restrictions
        if 'vegetarian' in dietary_restrictions:
            non_veg_dishes = ['Steamed Fish', 'Chicken Soup', 'Egg Curry']
            dishes = dishes[~dishes['dish_name'].isin(non_veg_dishes)]
        
        if 'vegan' in dietary_restrictions:
            dairy_dishes = ['Curd Rice', 'Palak Paneer', 'Paneer Tikka', 'Buttermilk']
            dishes = dishes[~dishes['dish_name'].isin(dairy_dishes)]
        
        # Remove trigger foods
        if trigger_foods:
            dishes = dishes[~dishes['dish_name'].isin(trigger_foods)]
        
        return dishes.sort_values('ibs_friendly_score', ascending=False)
    
    def _create_weekly_meal_plan(self, suitable_dishes: pd.DataFrame, 
                               preferred_meal_times: List[str]) -> Dict[str, Dict[str, str]]:
        """Create a 7-day meal plan with Indian dishes."""
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        meal_plan = {}
        
        for day in days:
            daily_meals = {}
            
            for meal_time in preferred_meal_times:
                # Get dishes suitable for this meal time
                meal_dishes = suitable_dishes[
                    (suitable_dishes['meal_type'] == meal_time) |
                    (suitable_dishes['meal_type'] == 'All')
                ]
                
                if not meal_dishes.empty:
                    # Select a random dish from top-rated options
                    top_dishes = meal_dishes.head(min(5, len(meal_dishes)))
                    selected_dish = top_dishes.sample(1).iloc[0]
                    daily_meals[meal_time.lower()] = selected_dish['dish_name']
                else:
                    # Fallback to any suitable dish
                    if not suitable_dishes.empty:
                        daily_meals[meal_time.lower()] = suitable_dishes.iloc[0]['dish_name']
            
            meal_plan[day] = daily_meals
        
        return meal_plan
    
    def _get_beneficial_spices(self, ibs_severity: int) -> List[Dict[str, str]]:
        """Get spices that are beneficial for IBS management."""
        
        beneficial_spices = self.spices_data[
            self.spices_data['ibs_impact'] == 'Positive'
        ].copy()
        
        # For severe IBS, recommend only the gentlest spices
        if ibs_severity >= 7:
            gentle_spices = ['Turmeric', 'Ginger', 'Fennel', 'Mint', 'Ajwain']
            beneficial_spices = beneficial_spices[
                beneficial_spices['spice_name'].isin(gentle_spices)
            ]
        
        return beneficial_spices[['spice_name', 'digestive_benefit', 'recommended_amount']].to_dict('records')
    
    def _get_indian_lifestyle_tips(self, user_profile: Dict[str, Any]) -> List[str]:
        """Generate Indian lifestyle tips for IBS management."""
        
        tips = [
            "Start your day with warm water and a pinch of turmeric for digestive health",
            "Practice eating mindfully - chew each bite 20-30 times as recommended in Ayurveda",
            "Include buttermilk or lassi (if dairy-tolerant) after meals for probiotics",
            "Try herbal teas like ginger-mint or fennel tea after meals",
            "Follow the Ayurvedic principle of eating your largest meal at lunch when digestion is strongest"
        ]
        
        ibs_severity = user_profile.get('ibs_severity_score', 5)
        
        if ibs_severity >= 7:
            tips.extend([
                "Consider following a temporary khichdi-based diet for gut healing",
                "Practice pranayama (breathing exercises) to reduce stress and improve digestion",
                "Avoid raw foods and opt for cooked, warm meals during flare-ups"
            ])
        
        if user_profile.get('stress_level', 5) >= 7:
            tips.extend([
                "Practice meditation or yoga daily - stress significantly impacts IBS",
                "Try Abhyanga (oil massage) before bath to reduce stress",
                "Consider adaptogenic herbs like Ashwagandha (consult with healthcare provider)"
            ])
        
        return tips
    
    def _calculate_nutritional_insights(self, suitable_dishes: pd.DataFrame) -> Dict[str, Any]:
        """Calculate nutritional insights from recommended dishes."""
        
        total_dishes = len(suitable_dishes)
        high_fiber_dishes = len(suitable_dishes[suitable_dishes['fiber_content'] == 'High'])
        easy_digest_dishes = len(suitable_dishes[suitable_dishes['digestibility'] == 'Easy'])
        low_fodmap_dishes = len(suitable_dishes[suitable_dishes['fodmap_level'] == 'Low'])
        
        return {
            'total_recommended_dishes': total_dishes,
            'high_fiber_percentage': round((high_fiber_dishes / total_dishes) * 100, 1) if total_dishes > 0 else 0,
            'easy_digest_percentage': round((easy_digest_dishes / total_dishes) * 100, 1) if total_dishes > 0 else 0,
            'low_fodmap_percentage': round((low_fodmap_dishes / total_dishes) * 100, 1) if total_dishes > 0 else 0,
            'average_ibs_friendly_score': round(suitable_dishes['ibs_friendly_score'].mean(), 1) if total_dishes > 0 else 0,
            'dietary_diversity_score': len(suitable_dishes['region'].unique()) if total_dishes > 0 else 0
        }
    
    def _calculate_personalization_score(self, user_profile: Dict[str, Any], 
                                       suitable_dishes: pd.DataFrame) -> float:
        """Calculate how well the recommendations match user's profile."""
        
        score = 0.0
        max_score = 100.0
        
        # Check regional preference matching
        regional_pref = user_profile.get('regional_preference', 'All')
        if regional_pref != 'All':
            regional_matches = len(suitable_dishes[suitable_dishes['region'] == regional_pref])
            score += (regional_matches / len(suitable_dishes)) * 25 if len(suitable_dishes) > 0 else 0
        else:
            score += 25  # Full points for no regional restriction
        
        # Check spice tolerance matching
        spice_tolerance = user_profile.get('spice_tolerance', 3)
        appropriate_spice_dishes = len(suitable_dishes[suitable_dishes['spice_level'] <= spice_tolerance])
        score += (appropriate_spice_dishes / len(suitable_dishes)) * 25 if len(suitable_dishes) > 0 else 0
        
        # Check IBS severity appropriateness
        ibs_severity = user_profile.get('ibs_severity_score', 5)
        if ibs_severity >= 7:
            high_friendly_dishes = len(suitable_dishes[suitable_dishes['ibs_friendly_score'] >= 8])
            score += (high_friendly_dishes / len(suitable_dishes)) * 25 if len(suitable_dishes) > 0 else 0
        else:
            score += 25  # Full points for moderate IBS
        
        # Check dietary restrictions compliance
        dietary_restrictions = user_profile.get('dietary_restrictions', [])
        if not dietary_restrictions:
            score += 25  # Full points for no restrictions
        else:
            # This would need more complex logic based on actual dish ingredients
            score += 20  # Assume good compliance for now
        
        return min(score, max_score)

def main():
    """Test the Indian Diet Recommender."""
    recommender = IndianDietRecommender()
    
    # Test user profile
    test_profile = {
        'ibs_severity_score': 6,
        'spice_tolerance': 3,
        'regional_preference': 'South',
        'dietary_restrictions': ['vegetarian'],
        'trigger_foods': ['Onion', 'Garlic'],
        'stress_level': 5,
        'preferred_meal_times': ['Breakfast', 'Lunch', 'Dinner']
    }
    
    recommendations = recommender.generate_personalized_recommendations(test_profile)
    
    print("=== Indian Diet Recommendations ===")
    print(f"Personalization Score: {recommendations['personalization_score']:.1f}%")
    print(f"\nRecommended Dishes: {len(recommendations['recommended_dishes'])}")
    
    for dish in recommendations['recommended_dishes'][:5]:
        print(f"- {dish['dish_name']} (IBS Score: {dish['ibs_friendly_score']}/10)")
    
    print(f"\nBeneficial Spices: {len(recommendations['beneficial_spices'])}")
    for spice in recommendations['beneficial_spices'][:3]:
        print(f"- {spice['spice_name']}: {spice['digestive_benefit']}")
    
    print(f"\nLifestyle Tips: {len(recommendations['lifestyle_tips'])}")
    for tip in recommendations['lifestyle_tips'][:3]:
        print(f"- {tip}")

if __name__ == "__main__":
    main()