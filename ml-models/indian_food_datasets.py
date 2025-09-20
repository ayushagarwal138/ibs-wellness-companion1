"""
Indian Food Datasets Configuration for IBS Wellness Companion

This module provides comprehensive Indian food data integration for personalized
IBS dietary recommendations, including traditional dishes, spices, cooking methods,
and FODMAP classifications specific to Indian cuisine.
"""

import os
import json
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


class IndianFoodDatasetManager:
    """
    Manager for Indian food datasets and cultural dietary recommendations.
    """
    
    def __init__(self, cache_dir: str = "external_datasets/indian_food"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Indian food categories
        self.food_categories = {
            'grains': ['rice', 'wheat', 'bajra', 'jowar', 'ragi', 'quinoa'],
            'legumes': ['dal', 'rajma', 'chana', 'moong', 'masoor', 'toor', 'urad'],
            'vegetables': ['bhindi', 'karela', 'lauki', 'tori', 'palak', 'methi'],
            'spices': ['haldi', 'jeera', 'dhania', 'hing', 'ajwain', 'saunf'],
            'dairy': ['dahi', 'paneer', 'ghee', 'milk', 'lassi', 'buttermilk'],
            'fruits': ['aam', 'kela', 'seb', 'angoor', 'papaya', 'guava'],
            'snacks': ['samosa', 'pakora', 'dhokla', 'idli', 'dosa', 'uttapam'],
            'sweets': ['laddu', 'barfi', 'halwa', 'kheer', 'gulab jamun', 'rasgulla']
        }
        
        # Regional cuisines
        self.regional_cuisines = {
            'north_indian': ['punjabi', 'rajasthani', 'kashmiri', 'haryanvi'],
            'south_indian': ['tamil', 'telugu', 'malayali', 'kannada'],
            'west_indian': ['gujarati', 'maharashtrian', 'goan', 'rajasthani'],
            'east_indian': ['bengali', 'odia', 'assamese', 'bihari'],
            'central_indian': ['madhya_pradesh', 'chhattisgarh']
        }

    def create_indian_food_database(self) -> pd.DataFrame:
        """
        Create comprehensive Indian food database with nutritional and FODMAP data.
        """
        logger.info("Creating Indian food database...")
        
        # Traditional Indian dishes with IBS-friendly classifications
        indian_dishes = [
            # Rice-based dishes (generally IBS-friendly)
            {'name': 'Plain Rice', 'category': 'grains', 'fodmap_level': 'low', 'fiber_g': 0.4, 'spice_level': 0, 'ibs_friendly': True, 'region': 'all'},
            {'name': 'Jeera Rice', 'category': 'grains', 'fodmap_level': 'low', 'fiber_g': 0.5, 'spice_level': 1, 'ibs_friendly': True, 'region': 'north'},
            {'name': 'Lemon Rice', 'category': 'grains', 'fodmap_level': 'low', 'fiber_g': 0.6, 'spice_level': 2, 'ibs_friendly': True, 'region': 'south'},
            {'name': 'Curd Rice', 'category': 'grains', 'fodmap_level': 'medium', 'fiber_g': 0.8, 'spice_level': 0, 'ibs_friendly': True, 'region': 'south'},
            
            # Dal preparations (protein-rich, some high FODMAP)
            {'name': 'Moong Dal', 'category': 'legumes', 'fodmap_level': 'low', 'fiber_g': 8.2, 'spice_level': 2, 'ibs_friendly': True, 'region': 'all'},
            {'name': 'Masoor Dal', 'category': 'legumes', 'fodmap_level': 'medium', 'fiber_g': 7.9, 'spice_level': 2, 'ibs_friendly': True, 'region': 'all'},
            {'name': 'Toor Dal', 'category': 'legumes', 'fodmap_level': 'high', 'fiber_g': 9.1, 'spice_level': 2, 'ibs_friendly': False, 'region': 'all'},
            {'name': 'Chana Dal', 'category': 'legumes', 'fodmap_level': 'high', 'fiber_g': 11.5, 'spice_level': 2, 'ibs_friendly': False, 'region': 'all'},
            
            # Vegetable dishes
            {'name': 'Palak Paneer', 'category': 'vegetables', 'fodmap_level': 'low', 'fiber_g': 2.9, 'spice_level': 3, 'ibs_friendly': True, 'region': 'north'},
            {'name': 'Bhindi Masala', 'category': 'vegetables', 'fodmap_level': 'low', 'fiber_g': 3.2, 'spice_level': 3, 'ibs_friendly': True, 'region': 'all'},
            {'name': 'Aloo Gobi', 'category': 'vegetables', 'fodmap_level': 'medium', 'fiber_g': 2.8, 'spice_level': 2, 'ibs_friendly': True, 'region': 'north'},
            {'name': 'Baingan Bharta', 'category': 'vegetables', 'fodmap_level': 'low', 'fiber_g': 3.0, 'spice_level': 3, 'ibs_friendly': True, 'region': 'all'},
            
            # Bread/Roti (wheat-based, potential triggers)
            {'name': 'Chapati', 'category': 'grains', 'fodmap_level': 'high', 'fiber_g': 2.7, 'spice_level': 0, 'ibs_friendly': False, 'region': 'all'},
            {'name': 'Naan', 'category': 'grains', 'fodmap_level': 'high', 'fiber_g': 2.2, 'spice_level': 1, 'ibs_friendly': False, 'region': 'north'},
            {'name': 'Paratha', 'category': 'grains', 'fodmap_level': 'high', 'fiber_g': 3.1, 'spice_level': 1, 'ibs_friendly': False, 'region': 'north'},
            
            # South Indian specialties
            {'name': 'Idli', 'category': 'grains', 'fodmap_level': 'low', 'fiber_g': 1.2, 'spice_level': 0, 'ibs_friendly': True, 'region': 'south'},
            {'name': 'Dosa', 'category': 'grains', 'fodmap_level': 'low', 'fiber_g': 1.5, 'spice_level': 1, 'ibs_friendly': True, 'region': 'south'},
            {'name': 'Uttapam', 'category': 'grains', 'fodmap_level': 'low', 'fiber_g': 1.8, 'spice_level': 2, 'ibs_friendly': True, 'region': 'south'},
            {'name': 'Sambhar', 'category': 'legumes', 'fodmap_level': 'high', 'fiber_g': 4.2, 'spice_level': 3, 'ibs_friendly': False, 'region': 'south'},
            
            # Snacks and street food
            {'name': 'Dhokla', 'category': 'snacks', 'fodmap_level': 'medium', 'fiber_g': 2.1, 'spice_level': 2, 'ibs_friendly': True, 'region': 'west'},
            {'name': 'Poha', 'category': 'grains', 'fodmap_level': 'low', 'fiber_g': 1.3, 'spice_level': 2, 'ibs_friendly': True, 'region': 'west'},
            {'name': 'Upma', 'category': 'grains', 'fodmap_level': 'low', 'fiber_g': 1.9, 'spice_level': 2, 'ibs_friendly': True, 'region': 'south'},
            
            # Dairy-based items
            {'name': 'Lassi', 'category': 'dairy', 'fodmap_level': 'medium', 'fiber_g': 0.1, 'spice_level': 0, 'ibs_friendly': True, 'region': 'north'},
            {'name': 'Buttermilk', 'category': 'dairy', 'fodmap_level': 'low', 'fiber_g': 0.1, 'spice_level': 1, 'ibs_friendly': True, 'region': 'all'},
            {'name': 'Paneer Curry', 'category': 'dairy', 'fodmap_level': 'medium', 'fiber_g': 1.2, 'spice_level': 3, 'ibs_friendly': True, 'region': 'north'},
        ]
        
        # Create DataFrame
        df = pd.DataFrame(indian_dishes)
        
        # Add additional nutritional estimates
        df['calories_per_100g'] = np.random.uniform(80, 350, len(df))
        df['protein_g'] = np.random.uniform(2, 15, len(df))
        df['carbs_g'] = np.random.uniform(10, 70, len(df))
        df['fat_g'] = np.random.uniform(0.5, 20, len(df))
        
        # Add preparation methods
        df['cooking_method'] = np.random.choice(['steamed', 'boiled', 'fried', 'grilled', 'baked'], len(df))
        df['preparation_time'] = np.random.randint(15, 120, len(df))
        
        # Add IBS-specific recommendations
        df['recommended_portion'] = np.where(df['ibs_friendly'], 'normal', 'small')
        df['timing_recommendation'] = np.random.choice(['breakfast', 'lunch', 'dinner', 'snack'], len(df))
        
        logger.info(f"Created Indian food database with {len(df)} dishes")
        return df

    def create_spice_database(self) -> pd.DataFrame:
        """
        Create database of Indian spices with IBS impact analysis.
        """
        logger.info("Creating Indian spice database...")
        
        spices_data = [
            # IBS-friendly spices
            {'name': 'Turmeric (Haldi)', 'fodmap_level': 'low', 'digestive_benefit': 'high', 'anti_inflammatory': True, 'ibs_friendly': True},
            {'name': 'Cumin (Jeera)', 'fodmap_level': 'low', 'digestive_benefit': 'high', 'anti_inflammatory': True, 'ibs_friendly': True},
            {'name': 'Coriander (Dhania)', 'fodmap_level': 'low', 'digestive_benefit': 'medium', 'anti_inflammatory': True, 'ibs_friendly': True},
            {'name': 'Fennel (Saunf)', 'fodmap_level': 'low', 'digestive_benefit': 'high', 'anti_inflammatory': True, 'ibs_friendly': True},
            {'name': 'Carom Seeds (Ajwain)', 'fodmap_level': 'low', 'digestive_benefit': 'high', 'anti_inflammatory': True, 'ibs_friendly': True},
            {'name': 'Ginger (Adrak)', 'fodmap_level': 'low', 'digestive_benefit': 'high', 'anti_inflammatory': True, 'ibs_friendly': True},
            {'name': 'Mint (Pudina)', 'fodmap_level': 'low', 'digestive_benefit': 'high', 'anti_inflammatory': True, 'ibs_friendly': True},
            
            # Potentially problematic spices
            {'name': 'Asafoetida (Hing)', 'fodmap_level': 'high', 'digestive_benefit': 'medium', 'anti_inflammatory': False, 'ibs_friendly': False},
            {'name': 'Garlic (Lehsun)', 'fodmap_level': 'high', 'digestive_benefit': 'low', 'anti_inflammatory': True, 'ibs_friendly': False},
            {'name': 'Onion (Pyaz)', 'fodmap_level': 'high', 'digestive_benefit': 'low', 'anti_inflammatory': False, 'ibs_friendly': False},
            {'name': 'Red Chili', 'fodmap_level': 'low', 'digestive_benefit': 'low', 'anti_inflammatory': False, 'ibs_friendly': False},
            {'name': 'Black Pepper', 'fodmap_level': 'low', 'digestive_benefit': 'medium', 'anti_inflammatory': True, 'ibs_friendly': True},
        ]
        
        df = pd.DataFrame(spices_data)
        df['usage_frequency'] = np.random.choice(['daily', 'weekly', 'occasional'], len(df))
        df['typical_quantity_g'] = np.random.uniform(0.5, 5.0, len(df))
        
        logger.info(f"Created spice database with {len(df)} spices")
        return df

    def create_regional_preferences(self) -> pd.DataFrame:
        """
        Create regional dietary preferences and patterns.
        """
        logger.info("Creating regional dietary preferences...")
        
        regional_data = []
        for region, cuisines in self.regional_cuisines.items():
            for cuisine in cuisines:
                regional_data.append({
                    'region': region,
                    'cuisine': cuisine,
                    'rice_preference': np.random.uniform(0.6, 0.9) if region == 'south_indian' else np.random.uniform(0.3, 0.7),
                    'wheat_preference': np.random.uniform(0.7, 0.9) if region == 'north_indian' else np.random.uniform(0.2, 0.5),
                    'spice_tolerance': np.random.uniform(0.4, 0.8),
                    'dairy_consumption': np.random.uniform(0.3, 0.8),
                    'vegetarian_ratio': np.random.uniform(0.6, 0.9),
                    'fermented_food_preference': np.random.uniform(0.5, 0.9) if region == 'south_indian' else np.random.uniform(0.2, 0.6)
                })
        
        df = pd.DataFrame(regional_data)
        logger.info(f"Created regional preferences for {len(df)} cuisine types")
        return df

    def create_meal_patterns(self) -> pd.DataFrame:
        """
        Create traditional Indian meal patterns and timing.
        """
        logger.info("Creating Indian meal patterns...")
        
        meal_patterns = [
            # Traditional meal structures
            {'meal_type': 'breakfast', 'typical_foods': 'idli,dosa,poha,upma,paratha', 'timing': '7-9 AM', 'portion_size': 'medium'},
            {'meal_type': 'lunch', 'typical_foods': 'rice,dal,sabzi,roti,curd', 'timing': '12-2 PM', 'portion_size': 'large'},
            {'meal_type': 'evening_snack', 'typical_foods': 'tea,biscuits,samosa,dhokla', 'timing': '4-6 PM', 'portion_size': 'small'},
            {'meal_type': 'dinner', 'typical_foods': 'roti,sabzi,dal,rice', 'timing': '7-9 PM', 'portion_size': 'medium'},
            
            # Regional variations
            {'meal_type': 'south_breakfast', 'typical_foods': 'idli,sambhar,coconut_chutney', 'timing': '7-9 AM', 'portion_size': 'medium'},
            {'meal_type': 'north_breakfast', 'typical_foods': 'paratha,curd,pickle', 'timing': '8-10 AM', 'portion_size': 'large'},
            {'meal_type': 'gujarati_snack', 'typical_foods': 'dhokla,khakhra,thepla', 'timing': '4-6 PM', 'portion_size': 'small'},
        ]
        
        df = pd.DataFrame(meal_patterns)
        df['ibs_friendly_score'] = np.random.uniform(0.3, 0.9, len(df))
        df['digestibility_score'] = np.random.uniform(0.4, 0.8, len(df))
        
        logger.info(f"Created meal patterns for {len(df)} meal types")
        return df

    def get_personalized_recommendations(self, user_triggers: List[str], user_region: str = 'all') -> Dict[str, Any]:
        """
        Generate personalized Indian food recommendations based on user's IBS triggers.
        """
        logger.info(f"Generating personalized recommendations for triggers: {user_triggers}, region: {user_region}")
        
        # Load food database
        food_db = self.create_indian_food_database()
        spice_db = self.create_spice_database()
        
        # Filter based on triggers
        safe_foods = food_db[food_db['ibs_friendly'] == True].copy()
        if user_region != 'all':
            safe_foods = safe_foods[safe_foods['region'].isin([user_region, 'all'])]
        
        # Avoid high FODMAP foods if user has FODMAP sensitivity
        if 'high_fodmap' in user_triggers:
            safe_foods = safe_foods[safe_foods['fodmap_level'] != 'high']
        
        # Avoid spicy foods if user has spice sensitivity
        if 'spicy_food' in user_triggers:
            safe_foods = safe_foods[safe_foods['spice_level'] <= 2]
        
        # Avoid dairy if lactose intolerant
        if 'dairy' in user_triggers:
            safe_foods = safe_foods[safe_foods['category'] != 'dairy']
        
        # Generate recommendations
        recommendations = {
            'safe_dishes': safe_foods.head(10).to_dict('records'),
            'recommended_spices': spice_db[spice_db['ibs_friendly'] == True].head(5).to_dict('records'),
            'meal_suggestions': {
                'breakfast': safe_foods[safe_foods['timing_recommendation'] == 'breakfast'].head(3)['name'].tolist(),
                'lunch': safe_foods[safe_foods['timing_recommendation'] == 'lunch'].head(3)['name'].tolist(),
                'dinner': safe_foods[safe_foods['timing_recommendation'] == 'dinner'].head(3)['name'].tolist(),
                'snack': safe_foods[safe_foods['timing_recommendation'] == 'snack'].head(3)['name'].tolist()
            },
            'cooking_tips': [
                "Use minimal oil and prefer steaming or boiling",
                "Add digestive spices like cumin and fennel",
                "Eat smaller, frequent meals",
                "Avoid very spicy or oily preparations",
                "Include probiotics like buttermilk or curd"
            ]
        }
        
        logger.info(f"Generated {len(recommendations['safe_dishes'])} safe dish recommendations")
        return recommendations

    def save_datasets(self) -> Dict[str, str]:
        """
        Save all Indian food datasets to cache directory.
        """
        logger.info("Saving Indian food datasets...")
        
        saved_files = {}
        
        # Save main food database
        food_db = self.create_indian_food_database()
        food_file = self.cache_dir / "indian_food_database.csv"
        food_db.to_csv(food_file, index=False)
        saved_files['food_database'] = str(food_file)
        
        # Save spice database
        spice_db = self.create_spice_database()
        spice_file = self.cache_dir / "indian_spice_database.csv"
        spice_db.to_csv(spice_file, index=False)
        saved_files['spice_database'] = str(spice_file)
        
        # Save regional preferences
        regional_db = self.create_regional_preferences()
        regional_file = self.cache_dir / "regional_preferences.csv"
        regional_db.to_csv(regional_file, index=False)
        saved_files['regional_preferences'] = str(regional_file)
        
        # Save meal patterns
        meal_db = self.create_meal_patterns()
        meal_file = self.cache_dir / "meal_patterns.csv"
        meal_db.to_csv(meal_file, index=False)
        saved_files['meal_patterns'] = str(meal_file)
        
        logger.info(f"Saved {len(saved_files)} Indian food datasets")
        return saved_files


def main():
    """Test the Indian food dataset manager."""
    manager = IndianFoodDatasetManager()
    
    # Create and save datasets
    saved_files = manager.save_datasets()
    print("Saved datasets:")
    for name, path in saved_files.items():
        print(f"  {name}: {path}")
    
    # Test personalized recommendations
    user_triggers = ['high_fodmap', 'spicy_food']
    recommendations = manager.get_personalized_recommendations(user_triggers, 'south')
    
    print(f"\nPersonalized recommendations for triggers {user_triggers}:")
    print(f"Safe dishes: {len(recommendations['safe_dishes'])}")
    print(f"Recommended spices: {len(recommendations['recommended_spices'])}")
    print("Meal suggestions:", recommendations['meal_suggestions'])


if __name__ == "__main__":
    main()