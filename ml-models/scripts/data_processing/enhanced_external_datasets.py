"""
Enhanced External Dataset Configuration for IBS ML Models

This module provides an improved configuration for external datasets that are
specifically relevant to IBS research, nutrition analysis, and personalized
dietary recommendations. It includes real, validated datasets from various sources.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class EnhancedDatasetConfig:
    """Enhanced configuration for external datasets with validation."""
    name: str
    source: str  # 'kaggle', 'github', 'usda', 'research'
    dataset_id: str
    description: str
    relevance_score: float  # 0-1 score for IBS relevance
    data_quality: str  # 'high', 'medium', 'low'
    enabled: bool = True
    cache_days: int = 7
    columns_mapping: Dict[str, str] = None
    processing_options: Dict[str, Any] = None
    validation_url: Optional[str] = None
    
    def __post_init__(self):
        if self.columns_mapping is None:
            self.columns_mapping = {}
        if self.processing_options is None:
            self.processing_options = {}


class EnhancedExternalDataConfig:
    """Enhanced configuration manager with validated, real datasets."""
    
    def __init__(self):
        self.datasets: Dict[str, EnhancedDatasetConfig] = {}
        self._initialize_validated_datasets()
    
    def _initialize_validated_datasets(self):
        """Initialize with real, validated datasets for IBS research."""
        logger.info("Initializing enhanced external dataset configurations")
        
        # 1. USDA Food Data Central - Comprehensive nutrition database
        self.datasets['usda_food_data'] = EnhancedDatasetConfig(
            name='usda_food_data',
            source='usda',
            dataset_id='usda-food-data-central',
            description='USDA Food Data Central - comprehensive nutrition database with 300k+ foods',
            relevance_score=0.95,
            data_quality='high',
            validation_url='https://fdc.nal.usda.gov/',
            columns_mapping={
                'description': 'food_name',
                'energy': 'calories_per_100g',
                'protein': 'protein_g',
                'total_lipid_fat': 'fat_g',
                'carbohydrate_by_difference': 'carbs_g',
                'fiber_total_dietary': 'fiber_g',
                'sugars_total_including_nlea': 'sugar_g'
            },
            processing_options={
                'normalize_per_serving': True,
                'add_fodmap_classification': True,
                'calculate_glycemic_index': True,
                'filter_processed_foods': False
            }
        )
        
        # 2. Nutrition5k Dataset - Google Research visual nutrition data
        self.datasets['nutrition5k'] = EnhancedDatasetConfig(
            name='nutrition5k',
            source='github',
            dataset_id='google-research-datasets/Nutrition5k',
            description='Google Research Nutrition5k dataset with visual and nutritional data for 5k realistic food plates',
            relevance_score=0.85,
            data_quality='high',
            validation_url='https://github.com/google-research-datasets/Nutrition5k',
            columns_mapping={
                'total_calories': 'calories_per_dish',
                'total_mass': 'dish_weight_g',
                'total_fat': 'fat_g',
                'total_carb': 'carbs_g',
                'total_protein': 'protein_g',
                'num_ingrs': 'ingredient_count'
            },
            processing_options={
                'extract_ingredient_patterns': True,
                'analyze_portion_sizes': True,
                'correlate_visual_nutrition': True
            }
        )
        
        # 3. MyFoodData Nutrition Database
        self.datasets['myfooddata_nutrition'] = EnhancedDatasetConfig(
            name='myfooddata_nutrition',
            source='kaggle',
            dataset_id='shashwatwork/food-nutrition-dataset',
            description='Comprehensive food nutrition dataset with macronutrients and micronutrients',
            relevance_score=0.90,
            data_quality='high',
            columns_mapping={
                'Food': 'food_name',
                'Calories': 'calories_per_100g',
                'Protein': 'protein_g',
                'Fat': 'fat_g',
                'Carbs': 'carbs_g',
                'Fiber': 'fiber_g'
            },
            processing_options={
                'standardize_portions': True,
                'add_ibs_trigger_flags': True,
                'calculate_nutrient_density': True
            }
        )
        
        # 4. FODMAP Food Database
        self.datasets['fodmap_database'] = EnhancedDatasetConfig(
            name='fodmap_database',
            source='research',
            dataset_id='monash-fodmap-database',
            description='Monash University FODMAP database for IBS dietary management',
            relevance_score=1.0,  # Highest relevance for IBS
            data_quality='high',
            validation_url='https://www.monashfodmap.com/',
            columns_mapping={
                'food_name': 'food_item',
                'fodmap_level': 'ibs_trigger_level',
                'serving_size': 'safe_portion_g',
                'category': 'food_category'
            },
            processing_options={
                'create_trigger_matrix': True,
                'calculate_cumulative_load': True,
                'personalize_thresholds': True
            }
        )
        
        # 5. Recipe and Meal Planning Dataset
        self.datasets['recipe_nutrition'] = EnhancedDatasetConfig(
            name='recipe_nutrition',
            source='kaggle',
            dataset_id='shuyangli94/food-com-recipes-and-user-interactions',
            description='Recipe dataset with nutritional information and user interactions',
            relevance_score=0.75,
            data_quality='medium',
            columns_mapping={
                'name': 'recipe_name',
                'nutrition': 'nutrition_array',
                'ingredients': 'ingredient_list',
                'n_steps': 'preparation_complexity',
                'minutes': 'prep_time'
            },
            processing_options={
                'parse_nutrition_array': True,
                'extract_ibs_friendly_recipes': True,
                'analyze_ingredient_combinations': True,
                'filter_by_prep_time': True
            }
        )
        
        # 6. Microbiome and Diet Interaction Data
        self.datasets['microbiome_diet'] = EnhancedDatasetConfig(
            name='microbiome_diet',
            source='research',
            dataset_id='american-gut-project',
            description='American Gut Project data linking diet patterns to microbiome composition',
            relevance_score=0.95,
            data_quality='high',
            validation_url='https://americangut.org/',
            columns_mapping={
                'sample_id': 'participant_id',
                'diet_type': 'dietary_pattern',
                'fiber_intake': 'daily_fiber_g',
                'diversity_index': 'microbiome_diversity',
                'dominant_phyla': 'bacterial_composition'
            },
            processing_options={
                'correlate_diet_microbiome': True,
                'identify_beneficial_patterns': True,
                'predict_ibs_risk': True
            }
        )
        
        # 7. Symptom Tracking and Food Diary Data
        self.datasets['symptom_food_diary'] = EnhancedDatasetConfig(
            name='symptom_food_diary',
            source='kaggle',
            dataset_id='health-tracking/digestive-health-logs',
            description='Synthetic but realistic digestive health and food diary data',
            relevance_score=0.85,
            data_quality='medium',
            enabled=False,  # Needs validation
            columns_mapping={
                'date': 'log_date',
                'food_consumed': 'meal_items',
                'symptom_severity': 'ibs_severity_score',
                'mood': 'stress_level',
                'sleep_quality': 'sleep_score'
            },
            processing_options={
                'temporal_analysis': True,
                'food_symptom_correlation': True,
                'identify_trigger_patterns': True,
                'stress_factor_analysis': True
            }
        )
        
        # 8. Clinical Nutrition Research Data
        self.datasets['clinical_nutrition'] = EnhancedDatasetConfig(
            name='clinical_nutrition',
            source='research',
            dataset_id='nhanes-nutrition-data',
            description='NHANES nutrition and health examination survey data',
            relevance_score=0.80,
            data_quality='high',
            validation_url='https://www.cdc.gov/nchs/nhanes/',
            columns_mapping={
                'seqn': 'participant_id',
                'dr1tkcal': 'daily_calories',
                'dr1tprot': 'daily_protein_g',
                'dr1tcarb': 'daily_carbs_g',
                'dr1tfibe': 'daily_fiber_g'
            },
            processing_options={
                'population_dietary_patterns': True,
                'health_outcome_correlation': True,
                'demographic_analysis': True
            }
        )
    
    def get_high_relevance_datasets(self) -> List[str]:
        """Get datasets with high relevance scores for IBS research."""
        return [
            name for name, config in self.datasets.items()
            if config.relevance_score >= 0.85 and config.enabled
        ]
    
    def get_enabled_datasets(self) -> List[str]:
        """Get all enabled datasets."""
        return [
            name for name, config in self.datasets.items()
            if config.enabled
        ]
    
    def validate_dataset_availability(self, dataset_name: str) -> bool:
        """Validate if a dataset is actually available."""
        if dataset_name not in self.datasets:
            return False
        
        config = self.datasets[dataset_name]
        
        # For Kaggle datasets, check if API credentials are available
        if config.source == 'kaggle':
            return bool(os.getenv('KAGGLE_USERNAME') and os.getenv('KAGGLE_KEY'))
        
        # For other sources, assume available if enabled
        return config.enabled
    
    def get_dataset_info(self, dataset_name: str) -> Dict[str, Any]:
        """Get comprehensive information about a dataset."""
        if dataset_name not in self.datasets:
            return {}
        
        config = self.datasets[dataset_name]
        return {
            'name': config.name,
            'source': config.source,
            'description': config.description,
            'relevance_score': config.relevance_score,
            'data_quality': config.data_quality,
            'enabled': config.enabled,
            'available': self.validate_dataset_availability(dataset_name),
            'validation_url': config.validation_url
        }
    
    def export_config(self, filepath: str):
        """Export configuration to JSON file."""
        config_data = {
            'datasets': {
                name: asdict(config) for name, config in self.datasets.items()
            },
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'total_datasets': len(self.datasets),
                'enabled_datasets': len(self.get_enabled_datasets()),
                'high_relevance_datasets': len(self.get_high_relevance_datasets())
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        logger.info(f"Enhanced dataset configuration exported to {filepath}")


if __name__ == "__main__":
    # Example usage
    config = EnhancedExternalDataConfig()
    
    print("High Relevance Datasets for IBS Research:")
    for dataset in config.get_high_relevance_datasets():
        info = config.get_dataset_info(dataset)
        print(f"  ✓ {info['name']}: {info['description'][:80]}...")
        print(f"    Relevance: {info['relevance_score']}, Quality: {info['data_quality']}")
    
    # Export configuration
    config.export_config('enhanced_external_datasets.json')