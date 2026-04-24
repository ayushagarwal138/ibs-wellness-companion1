#!/usr/bin/env python3
"""
Direct ML Model Test Script

Tests the ML models directly to understand why they return consistent scores.
"""

import sys
import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

# Add the ML models path
ml_models_path = Path(__file__).parent.parent / "ml-models"
sys.path.append(str(ml_models_path))

def test_enhanced_models():
    """Test the enhanced models directly."""
    print("=== Testing Enhanced Models ===")
    
    models_dir = ml_models_path / "trained_models"
    
    # Test enhanced models
    enhanced_models = {
        'random_forest': 'enhanced_random_forest.joblib',
        'gradient_boosting': 'enhanced_gradient_boosting.joblib',
        'logistic_regression': 'enhanced_logistic_regression.joblib'
    }
    
    for model_name, filename in enhanced_models.items():
        model_path = models_dir / filename
        if model_path.exists():
            print(f"\n--- Testing {model_name} ---")
            try:
                model = joblib.load(model_path)
                print(f"Model type: {type(model)}")
                
                # Test with sample data
                sample_features = np.random.rand(1, 20)  # 20 features as per training report
                
                if hasattr(model, 'predict_proba'):
                    proba = model.predict_proba(sample_features)
                    print(f"Prediction probabilities: {proba}")
                    
                if hasattr(model, 'predict'):
                    pred = model.predict(sample_features)
                    print(f"Prediction: {pred}")
                    
            except Exception as e:
                print(f"Error testing {model_name}: {e}")
        else:
            print(f"Model {filename} not found")

def test_original_models():
    """Test the original IBS-specific models."""
    print("\n=== Testing Original IBS Models ===")
    
    models_dir = ml_models_path / "trained_models"
    
    # Test original models
    original_models = {
        'flareup_predictor': 'flareup_predictor.joblib',
        'recommendation_engine': 'recommendation_engine.joblib'
    }
    
    for model_name, filename in original_models.items():
        model_path = models_dir / filename
        if model_path.exists():
            print(f"\n--- Testing {model_name} ---")
            try:
                model_data = joblib.load(model_path)
                print(f"Model data type: {type(model_data)}")
                print(f"Model data keys: {model_data.keys() if isinstance(model_data, dict) else 'Not a dict'}")
                
                if isinstance(model_data, dict):
                    if 'model' in model_data:
                        model = model_data['model']
                        print(f"Actual model type: {type(model)}")
                        
                        # Test with sample features
                        if hasattr(model, 'feature_names_'):
                            print(f"Feature names: {model.feature_names_}")
                        
                        # Create sample data based on the model's expected features
                        if model_name == 'flareup_predictor':
                            # Based on FlareupPredictor.prepare_features
                            sample_data = {
                                'recent_avg_severity': 5.0,
                                'symptom_trend': 0.1,
                                'days_since_last_flareup': 10,
                                'recent_high_fodmap_intake': 2.0,
                                'trigger_foods_consumed': 1,
                                'meal_timing_irregularity': 0.5,
                                'current_stress_level': 6.0,
                                'sleep_quality_trend': 4.0,
                                'exercise_deficit': 50,
                                'medication_adherence_rate': 0.8,
                                'missed_doses_recent': 0,
                                'seasonal_factor': 0,
                                'historical_flareup_frequency': 0.2,
                                'time_of_day_risk': 1
                            }
                            
                            # Test prediction
                            try:
                                # Load the actual model class
                                sys.path.append(str(ml_models_path / "src"))
                                from models.flareup_predictor import FlareupPredictor
                                
                                predictor = FlareupPredictor()
                                predictor.load_model(str(model_path))
                                
                                result = predictor.predict_flareup_risk(sample_data)
                                print(f"Flareup prediction result: {result}")
                                
                            except Exception as e:
                                print(f"Error in flareup prediction: {e}")
                
            except Exception as e:
                print(f"Error testing {model_name}: {e}")
        else:
            print(f"Model {filename} not found")

def test_backend_service():
    """Test the backend service model loading."""
    print("\n=== Testing Backend Service ===")
    
    try:
        # Import the backend service
        sys.path.append(str(Path(__file__).parent))
        from app.services.enhanced_recommendation_service import EnhancedRecommendationService
        
        # Create a mock database session
        class MockDB:
            pass
        
        service = EnhancedRecommendationService(MockDB())
        
        print(f"Loaded models: {list(service.ml_models.keys())}")
        print(f"Feature names: {service.feature_names}")
        print(f"Has scaler: {service.scaler is not None}")
        
        # Test prediction
        sample_features = {
            'total_symptom_logs': 10,
            'severe_symptoms': 2,
            'moderate_symptoms': 5,
            'avg_pain_level': 6,
            'bowel_movement_logs': 8,
            'food_reactions': 3,
            'severe_food_reactions': 1,
            'medication_logs': 5,
            'age': 30,
            'is_female': 1,
            'stress_level': 7,
            'sleep_score': 4,
            'fodmap_load_score': 6,
            'daily_fiber_estimate': 25,
            'wellness_composite': 5
        }
        
        result = service.predict_symptom_risk(sample_features)
        print(f"Backend prediction result: {result}")
        
    except Exception as e:
        print(f"Error testing backend service: {e}")

if __name__ == "__main__":
    test_enhanced_models()
    test_original_models()
    test_backend_service()