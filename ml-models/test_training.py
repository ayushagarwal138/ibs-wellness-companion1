#!/usr/bin/env python3
"""
Training Pipeline Test Script

This script tests the ML model training pipeline with the generated sample data
to ensure all components work correctly.
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import logging

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from training.data_preparation import DataPreparator
from models.ibs_severity_classifier import IBSSeverityClassifier
from models.flareup_predictor import FlareupPredictor
from models.recommendation_engine import RecommendationEngine

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_data_loading():
    """Test loading the generated sample data."""
    logger.info("🔍 Testing data loading...")
    
    data_dir = Path(__file__).parent / "data"
    
    # Check if all required files exist
    required_files = ["train_data.csv", "val_data.csv", "test_data.csv"]
    for file in required_files:
        file_path = data_dir / file
        if not file_path.exists():
            raise FileNotFoundError(f"Required file not found: {file}")
        logger.info(f"   ✅ Found {file}")
    
    # Load training data
    train_data = pd.read_csv(data_dir / "train_data.csv")
    val_data = pd.read_csv(data_dir / "val_data.csv")
    test_data = pd.read_csv(data_dir / "test_data.csv")
    
    logger.info(f"   📊 Train data: {train_data.shape}")
    logger.info(f"   📊 Validation data: {val_data.shape}")
    logger.info(f"   📊 Test data: {test_data.shape}")
    
    # Check for required columns
    required_columns = ["pain_severity", "fodmap_level", "severity_score"]
    for col in required_columns:
        if col not in train_data.columns:
            raise ValueError(f"Required column missing: {col}")
        logger.info(f"   ✅ Column '{col}' present")
    
    return train_data, val_data, test_data


def test_severity_classifier(train_data, val_data, test_data):
    """Test the IBS Severity Classifier."""
    logger.info("🧠 Testing IBS Severity Classifier...")
    
    try:
        classifier = IBSSeverityClassifier()
        
        # Create severity labels from severity_score
        train_data_copy = train_data.copy()
        train_data_copy['severity_label'] = pd.cut(
            train_data_copy['severity_score'], 
            bins=[0, 3, 6, 10], 
            labels=['mild', 'moderate', 'severe']
        )
        
        logger.info(f"   📊 Training data: {train_data_copy.shape}")
        
        # Train the model (expects training_data and target_column)
        results = classifier.train(train_data_copy, target_column='severity_label')
        
        logger.info(f"   ✅ Training completed")
        logger.info(f"   📈 Training accuracy: {results.get('accuracy', 'N/A')}")
        
        # Test prediction on a sample - convert to dictionary format
        sample_data = val_data.head(1)  # Use single sample for testing
        sample_dict = sample_data.iloc[0].to_dict()  # Convert to dictionary
        prediction = classifier.predict(sample_dict)
        logger.info(f"   ✅ Generated prediction: {prediction['predicted_severity']}")
        
        return True
        
    except Exception as e:
        logger.error(f"   ❌ Severity classifier failed: {str(e)}")
        return False


def test_flareup_predictor(train_data, val_data, test_data):
    """Test the Flareup Predictor."""
    logger.info("🔮 Testing Flareup Predictor...")
    
    try:
        predictor = FlareupPredictor()
        
        # Create binary flareup target (severity_score > 6)
        train_data_copy = train_data.copy()
        train_data_copy['flareup'] = (train_data_copy['severity_score'] > 6).astype(int)
        
        logger.info(f"   📊 Training data: {train_data_copy.shape}")
        logger.info(f"   📊 Flareup rate: {train_data_copy['flareup'].mean():.3f}")
        
        # Train the model (expects training_data and prediction_window_hours)
        results = predictor.train(train_data_copy, prediction_window_hours=24)
        
        logger.info(f"   ✅ Training completed")
        logger.info(f"   📈 Training accuracy: {results.get('accuracy', 'N/A')}")
        
        # Test prediction on a sample
        sample_features = {
            'recent_avg_severity': 4.5,
            'symptom_trend': 0.2,
            'days_since_last_flareup': 10,
            'recent_high_fodmap_intake': 150.0,
            'trigger_foods_consumed': 2,
            'meal_timing_irregularity': 1.2,
            'current_stress_level': 6,
            'sleep_quality': 7,
            'exercise_deficit': 0.3,
            'missed_doses_recent': 1,
            'historical_flareup_frequency': 0.15,
            'weather_humidity': 65.0,
            'is_weekend': 0,
            'time_of_day': 14
        }
        prediction = predictor.predict_flareup_risk(sample_features)
        logger.info(f"   ✅ Generated prediction: {prediction.get('risk_level', 'unknown')}")
        
        return True
        
    except Exception as e:
        logger.error(f"   ❌ Flareup predictor failed: {str(e)}")
        return False


def test_recommendation_engine(train_data, val_data, test_data):
    """Test the Recommendation Engine."""
    logger.info("💡 Testing Recommendation Engine...")
    
    try:
        engine = RecommendationEngine()
        
        # Train the model
        engine.train(train_data)
        
        # Test recommendations for a sample user
        # Create user features that match what the model expects
        sample_user_features = {
            'avg_severity': 4.5,
            'severity_variance': 2.1,
            'flareup_frequency': 0.15,
            'high_fodmap_frequency': 0.3,
            'trigger_food_frequency': 0.2,
            'meal_regularity': 1.2,
            'avg_portion_size': 150.0,
            'avg_stress_level': 6.0,
            'avg_sleep_quality': 7.0,
            'exercise_frequency': 0.4,
            'medication_adherence': 0.8,
            'medication_effectiveness': 4.2,
            'weekend_severity_diff': 0.5,
            'morning_severity': 4.8
        }
        recommendations = engine.generate_recommendations(sample_user_features)
        
        logger.info(f"   ✅ Generated recommendations")
        logger.info(f"   📋 Diet recommendations: {len(recommendations.get('diet', []))}")
        logger.info(f"   📋 Lifestyle recommendations: {len(recommendations.get('lifestyle', []))}")
        
        return True
        
    except Exception as e:
        logger.error(f"   ❌ Recommendation engine failed: {str(e)}")
        return False


def main():
    """Run all training pipeline tests."""
    logger.info("🚀 Starting ML Training Pipeline Tests")
    logger.info("=" * 50)
    
    results = {}
    
    try:
        # Test data loading
        train_data, val_data, test_data = test_data_loading()
        results['data_loading'] = True
        
        # Test each model
        results['severity_classifier'] = test_severity_classifier(train_data, val_data, test_data)
        results['flareup_predictor'] = test_flareup_predictor(train_data, val_data, test_data)
        results['recommendation_engine'] = test_recommendation_engine(train_data, val_data, test_data)
        
    except Exception as e:
        logger.error(f"❌ Critical error in data loading: {str(e)}")
        results['data_loading'] = False
    
    # Summary
    logger.info("=" * 50)
    logger.info("📊 Test Results Summary:")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"   {test_name}: {status}")
    
    logger.info(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("🎉 All tests passed! Training pipeline is working correctly.")
        return True
    else:
        logger.error("⚠️  Some tests failed. Please check the logs above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)