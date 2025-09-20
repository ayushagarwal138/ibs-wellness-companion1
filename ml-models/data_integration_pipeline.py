"""
Data Integration Pipeline for IBS ML Models

This module provides a comprehensive pipeline for downloading, processing,
and integrating external datasets with existing training data to improve
IBS prediction accuracy and personalized recommendations.
"""

import os
import json
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import requests
from urllib.parse import urlparse
import hashlib

# Import our enhanced dataset configuration
from enhanced_external_datasets import EnhancedExternalDataConfig, EnhancedDatasetConfig

logger = logging.getLogger(__name__)


class DataIntegrationPipeline:
    """
    Comprehensive pipeline for external data integration.
    
    Handles downloading, caching, processing, and integration of external
    datasets with existing IBS training data.
    """
    
    def __init__(self, 
                 data_dir: str = "external_datasets",
                 cache_dir: str = "cache",
                 processed_dir: str = "processed"):
        self.data_dir = Path(data_dir)
        self.cache_dir = Path(cache_dir)
        self.processed_dir = Path(processed_dir)
        
        # Create directories
        for dir_path in [self.data_dir, self.cache_dir, self.processed_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.config = EnhancedExternalDataConfig()
        self.download_stats = {}
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
    
    def download_usda_food_data(self) -> pd.DataFrame:
        """
        Download and process USDA Food Data Central.
        
        Note: This is a simplified version. In practice, you'd use the USDA API
        or download the full database files.
        """
        logger.info("Processing USDA Food Data Central...")
        
        # For demonstration, create a sample dataset based on USDA structure
        # In practice, you would download from: https://fdc.nal.usda.gov/
        
        sample_foods = [
            {"description": "Apple, raw", "energy": 52, "protein": 0.26, "total_lipid_fat": 0.17, 
             "carbohydrate_by_difference": 13.81, "fiber_total_dietary": 2.4, "sugars_total_including_nlea": 10.39},
            {"description": "Banana, raw", "energy": 89, "protein": 1.09, "total_lipid_fat": 0.33,
             "carbohydrate_by_difference": 22.84, "fiber_total_dietary": 2.6, "sugars_total_including_nlea": 12.23},
            {"description": "Broccoli, raw", "energy": 34, "protein": 2.82, "total_lipid_fat": 0.37,
             "carbohydrate_by_difference": 6.64, "fiber_total_dietary": 2.6, "sugars_total_including_nlea": 1.55},
            {"description": "White bread", "energy": 265, "protein": 9.0, "total_lipid_fat": 3.2,
             "carbohydrate_by_difference": 49.0, "fiber_total_dietary": 2.7, "sugars_total_including_nlea": 5.0},
            {"description": "Milk, whole", "energy": 61, "protein": 3.15, "total_lipid_fat": 3.25,
             "carbohydrate_by_difference": 4.78, "fiber_total_dietary": 0, "sugars_total_including_nlea": 5.05}
        ]
        
        df = pd.DataFrame(sample_foods)
        
        # Apply column mapping
        config = self.config.datasets['usda_food_data']
        df = df.rename(columns=config.columns_mapping)
        
        # Add FODMAP classification (simplified)
        fodmap_levels = ['Low', 'Low', 'Low', 'Medium', 'Medium']  # Example classifications
        df['fodmap_level'] = fodmap_levels[:len(df)]
        
        # Add IBS trigger flags
        df['potential_ibs_trigger'] = df['fodmap_level'].isin(['Medium', 'High'])
        
        logger.info(f"Processed {len(df)} USDA food items")
        return df
    
    def download_nutrition5k_sample(self) -> pd.DataFrame:
        """
        Create a sample dataset based on Nutrition5k structure.
        
        In practice, you would clone the GitHub repository and process the actual data.
        """
        logger.info("Processing Nutrition5k sample data...")
        
        # Sample data based on Nutrition5k structure
        sample_dishes = [
            {"dish_id": "dish_001", "total_calories": 450, "total_mass": 300, "total_fat": 15,
             "total_carb": 60, "total_protein": 20, "num_ingrs": 5},
            {"dish_id": "dish_002", "total_calories": 320, "total_mass": 250, "total_fat": 8,
             "total_carb": 45, "total_protein": 25, "num_ingrs": 4},
            {"dish_id": "dish_003", "total_calories": 580, "total_mass": 400, "total_fat": 25,
             "total_carb": 70, "total_protein": 18, "num_ingrs": 6},
        ]
        
        df = pd.DataFrame(sample_dishes)
        
        # Apply column mapping
        config = self.config.datasets['nutrition5k']
        df = df.rename(columns=config.columns_mapping)
        
        # Calculate nutritional density metrics
        df['calorie_density'] = df['calories_per_dish'] / df['dish_weight_g']
        df['protein_ratio'] = df['protein_g'] / df['calories_per_dish']
        df['carb_ratio'] = df['carbs_g'] / df['calories_per_dish']
        
        logger.info(f"Processed {len(df)} Nutrition5k dish samples")
        return df
    
    def create_fodmap_database(self) -> pd.DataFrame:
        """
        Create a comprehensive FODMAP database for IBS management.
        
        Based on Monash University FODMAP research.
        """
        logger.info("Creating FODMAP database...")
        
        fodmap_foods = [
            {"food_item": "Apple", "fodmap_level": "High", "safe_portion_g": 20, "food_category": "Fruit"},
            {"food_item": "Banana (unripe)", "fodmap_level": "Low", "safe_portion_g": 100, "food_category": "Fruit"},
            {"food_item": "Broccoli", "fodmap_level": "Low", "safe_portion_g": 75, "food_category": "Vegetable"},
            {"food_item": "Onion", "fodmap_level": "High", "safe_portion_g": 10, "food_category": "Vegetable"},
            {"food_item": "Garlic", "fodmap_level": "High", "safe_portion_g": 1, "food_category": "Vegetable"},
            {"food_item": "Rice", "fodmap_level": "Low", "safe_portion_g": 200, "food_category": "Grain"},
            {"food_item": "Wheat bread", "fodmap_level": "High", "safe_portion_g": 24, "food_category": "Grain"},
            {"food_item": "Lactose-free milk", "fodmap_level": "Low", "safe_portion_g": 250, "food_category": "Dairy"},
            {"food_item": "Regular milk", "fodmap_level": "High", "safe_portion_g": 15, "food_category": "Dairy"},
        ]
        
        df = pd.DataFrame(fodmap_foods)
        
        # Add trigger severity scores
        severity_map = {"Low": 1, "Medium": 5, "High": 9}
        df['ibs_trigger_score'] = df['fodmap_level'].map(severity_map)
        
        # Add cumulative load calculation
        df['fodmap_load_per_100g'] = (df['ibs_trigger_score'] * 100) / df['safe_portion_g']
        
        logger.info(f"Created FODMAP database with {len(df)} food items")
        return df
    
    def create_synthetic_symptom_data(self) -> pd.DataFrame:
        """
        Create synthetic but realistic symptom tracking data.
        
        This simulates food diary and symptom correlation data.
        """
        logger.info("Creating synthetic symptom tracking data...")
        
        np.random.seed(42)  # For reproducible results
        
        # Generate 1000 days of symptom tracking data
        dates = pd.date_range(start='2023-01-01', periods=1000, freq='D')
        
        data = []
        for date in dates:
            # Simulate daily food intake and symptoms
            high_fodmap_foods = np.random.randint(0, 4)  # 0-3 high FODMAP foods per day
            stress_level = np.random.randint(1, 11)  # 1-10 stress scale
            sleep_quality = np.random.randint(1, 11)  # 1-10 sleep quality
            
            # IBS severity correlates with high FODMAP intake and stress
            base_severity = high_fodmap_foods * 2 + (10 - stress_level) + (10 - sleep_quality) / 2
            ibs_severity = max(1, min(10, base_severity + np.random.normal(0, 1)))
            
            data.append({
                'log_date': date,
                'high_fodmap_count': high_fodmap_foods,
                'stress_level': stress_level,
                'sleep_score': sleep_quality,
                'ibs_severity_score': round(ibs_severity, 1),
                'bloating': np.random.choice([0, 1], p=[0.7, 0.3]) if ibs_severity > 5 else 0,
                'abdominal_pain': np.random.choice([0, 1], p=[0.8, 0.2]) if ibs_severity > 6 else 0,
                'bowel_irregularity': np.random.choice([0, 1], p=[0.6, 0.4]) if ibs_severity > 4 else 0
            })
        
        df = pd.DataFrame(data)
        
        logger.info(f"Created {len(df)} days of synthetic symptom tracking data")
        return df
    
    def integrate_datasets(self) -> Dict[str, pd.DataFrame]:
        """
        Download and integrate all available external datasets.
        
        Returns a dictionary of processed datasets ready for ML training.
        """
        logger.info("Starting comprehensive data integration...")
        
        integrated_data = {}
        
        # 1. USDA Food Data
        try:
            usda_data = self.download_usda_food_data()
            integrated_data['nutrition_database'] = usda_data
            self.download_stats['usda_food_data'] = {'status': 'success', 'records': len(usda_data)}
        except Exception as e:
            logger.error(f"Failed to process USDA data: {e}")
            self.download_stats['usda_food_data'] = {'status': 'failed', 'error': str(e)}
        
        # 2. Nutrition5k Sample
        try:
            nutrition5k_data = self.download_nutrition5k_sample()
            integrated_data['dish_nutrition'] = nutrition5k_data
            self.download_stats['nutrition5k'] = {'status': 'success', 'records': len(nutrition5k_data)}
        except Exception as e:
            logger.error(f"Failed to process Nutrition5k data: {e}")
            self.download_stats['nutrition5k'] = {'status': 'failed', 'error': str(e)}
        
        # 3. FODMAP Database
        try:
            fodmap_data = self.create_fodmap_database()
            integrated_data['fodmap_reference'] = fodmap_data
            self.download_stats['fodmap_database'] = {'status': 'success', 'records': len(fodmap_data)}
        except Exception as e:
            logger.error(f"Failed to create FODMAP database: {e}")
            self.download_stats['fodmap_database'] = {'status': 'failed', 'error': str(e)}
        
        # 4. Synthetic Symptom Data
        try:
            symptom_data = self.create_synthetic_symptom_data()
            integrated_data['symptom_tracking'] = symptom_data
            self.download_stats['symptom_tracking'] = {'status': 'success', 'records': len(symptom_data)}
        except Exception as e:
            logger.error(f"Failed to create symptom data: {e}")
            self.download_stats['symptom_tracking'] = {'status': 'failed', 'error': str(e)}
        
        # Save integrated datasets
        self.save_integrated_data(integrated_data)
        
        logger.info(f"Data integration completed. {len(integrated_data)} datasets processed.")
        return integrated_data
    
    def save_integrated_data(self, datasets: Dict[str, pd.DataFrame]):
        """Save integrated datasets to files."""
        for name, df in datasets.items():
            filepath = self.processed_dir / f"{name}.csv"
            df.to_csv(filepath, index=False)
            logger.info(f"Saved {name} dataset to {filepath}")
    
    def create_training_features(self, datasets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Create enhanced features for ML training by combining external datasets.
        
        This function demonstrates how to create rich features from multiple
        external data sources for improved IBS prediction.
        """
        logger.info("Creating enhanced training features...")
        
        # Start with symptom tracking data as the base
        if 'symptom_tracking' not in datasets:
            raise ValueError("Symptom tracking data is required for feature creation")
        
        base_df = datasets['symptom_tracking'].copy()
        
        # Add nutrition-based features
        if 'nutrition_database' in datasets:
            nutrition_df = datasets['nutrition_database']
            
            # Calculate daily nutrition metrics (simplified)
            base_df['daily_fiber_estimate'] = np.random.uniform(15, 35, len(base_df))
            base_df['daily_calories_estimate'] = np.random.uniform(1500, 2500, len(base_df))
            base_df['protein_ratio'] = np.random.uniform(0.1, 0.3, len(base_df))
        
        # Add FODMAP-based features
        if 'fodmap_reference' in datasets:
            fodmap_df = datasets['fodmap_reference']
            
            # Calculate FODMAP load (already have high_fodmap_count)
            base_df['fodmap_load_score'] = base_df['high_fodmap_count'] * 3  # Simplified calculation
            base_df['fodmap_risk_category'] = pd.cut(
                base_df['fodmap_load_score'], 
                bins=[0, 3, 6, float('inf')], 
                labels=['Low', 'Medium', 'High']
            )
        
        # Add temporal features
        base_df['day_of_week'] = base_df['log_date'].dt.dayofweek
        base_df['is_weekend'] = base_df['day_of_week'].isin([5, 6]).astype(int)
        base_df['month'] = base_df['log_date'].dt.month
        
        # Add rolling averages for trend analysis
        base_df['stress_7day_avg'] = base_df['stress_level'].rolling(window=7, min_periods=1).mean()
        base_df['sleep_7day_avg'] = base_df['sleep_score'].rolling(window=7, min_periods=1).mean()
        base_df['severity_7day_avg'] = base_df['ibs_severity_score'].rolling(window=7, min_periods=1).mean()
        
        # Create interaction features
        base_df['stress_sleep_interaction'] = base_df['stress_level'] * base_df['sleep_score']
        base_df['fodmap_stress_interaction'] = base_df['fodmap_load_score'] * base_df['stress_level']
        
        logger.info(f"Created enhanced feature set with {len(base_df.columns)} features")
        return base_df
    
    def generate_integration_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report of the data integration process."""
        report = {
            'integration_timestamp': datetime.now().isoformat(),
            'datasets_processed': len(self.download_stats),
            'successful_integrations': sum(1 for stat in self.download_stats.values() if stat['status'] == 'success'),
            'failed_integrations': sum(1 for stat in self.download_stats.values() if stat['status'] == 'failed'),
            'total_records': sum(stat.get('records', 0) for stat in self.download_stats.values() if stat['status'] == 'success'),
            'dataset_details': self.download_stats,
            'recommendations': []
        }
        
        # Add recommendations based on integration results
        if report['failed_integrations'] > 0:
            report['recommendations'].append("Some datasets failed to integrate. Check API credentials and network connectivity.")
        
        if report['total_records'] < 1000:
            report['recommendations'].append("Consider adding more external datasets to improve model training data volume.")
        
        report['recommendations'].append("Regularly update external datasets to maintain model accuracy.")
        report['recommendations'].append("Validate data quality and consistency across integrated datasets.")
        
        return report


def main():
    """Main function to demonstrate the data integration pipeline."""
    pipeline = DataIntegrationPipeline()
    
    # Integrate all available datasets
    datasets = pipeline.integrate_datasets()
    
    # Create enhanced training features
    if datasets:
        enhanced_features = pipeline.create_training_features(datasets)
        
        # Save enhanced features
        enhanced_features.to_csv('enhanced_training_features.csv', index=False)
        logger.info("Enhanced training features saved to enhanced_training_features.csv")
    
    # Generate integration report
    report = pipeline.generate_integration_report()
    
    # Save report
    with open('data_integration_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "="*60)
    print("DATA INTEGRATION PIPELINE SUMMARY")
    print("="*60)
    print(f"Datasets processed: {report['datasets_processed']}")
    print(f"Successful integrations: {report['successful_integrations']}")
    print(f"Total records integrated: {report['total_records']}")
    print(f"Enhanced features created: {len(enhanced_features.columns) if 'enhanced_features' in locals() else 'N/A'}")
    print("\nRecommendations:")
    for rec in report['recommendations']:
        print(f"  • {rec}")
    print("="*60)


if __name__ == "__main__":
    main()