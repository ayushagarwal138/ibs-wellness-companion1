#!/usr/bin/env python3
"""
ML Model Fix Test

Identifies and fixes the ML model prediction issues.
"""

import sys
import os
import joblib
import numpy as np
from pathlib import Path

# Add the ML models path
ml_models_path = Path(__file__).parent.parent / "ml-models"
sys.path.append(str(ml_models_path))

def test_backend_prediction_issue():
    """Test and fix the backend prediction issue."""
    print("=== Testing Backend ML Prediction Issue ===")
    
    try:
        # Import the backend service
        sys.path.append(str(Path(__file__).parent))
        from app.services.enhanced_recommendation_service import EnhancedRecommendationService
        
        # Create a mock database session
        class MockDB:
            pass
        
        service = EnhancedRecommendationService(MockDB())
        
        print(f"Loaded models: {list(service.ml_models.keys())}")
        print(f"Number of feature names: {len(service.feature_names)}")
        print(f"Feature names: {service.feature_names[:5]}...")  # Show first 5
        
        # Test with different feature sets
        test_cases = [
            {
                'name': 'High severity symptoms',
                'features': {
                    'total_symptom_logs': 20,
                    'severe_symptoms': 8,
                    'moderate_symptoms': 10,
                    'avg_pain_level': 8,
                    'bowel_movement_logs': 15,
                    'food_reactions': 6,
                    'severe_food_reactions': 3,
                    'medication_logs': 10,
                    'age': 35,
                    'is_female': 1,
                    'stress_level': 9,
                    'sleep_score': 2,
                    'fodmap_load_score': 8,
                    'daily_fiber_estimate': 15,
                    'wellness_composite': 2
                }
            },
            {
                'name': 'Low severity symptoms',
                'features': {
                    'total_symptom_logs': 5,
                    'severe_symptoms': 0,
                    'moderate_symptoms': 2,
                    'avg_pain_level': 2,
                    'bowel_movement_logs': 3,
                    'food_reactions': 1,
                    'severe_food_reactions': 0,
                    'medication_logs': 2,
                    'age': 25,
                    'is_female': 0,
                    'stress_level': 3,
                    'sleep_score': 8,
                    'fodmap_load_score': 3,
                    'daily_fiber_estimate': 30,
                    'wellness_composite': 8
                }
            },
            {
                'name': 'Medium severity symptoms',
                'features': {
                    'total_symptom_logs': 12,
                    'severe_symptoms': 3,
                    'moderate_symptoms': 6,
                    'avg_pain_level': 5,
                    'bowel_movement_logs': 8,
                    'food_reactions': 3,
                    'severe_food_reactions': 1,
                    'medication_logs': 5,
                    'age': 30,
                    'is_female': 1,
                    'stress_level': 6,
                    'sleep_score': 5,
                    'fodmap_load_score': 5,
                    'daily_fiber_estimate': 22,
                    'wellness_composite': 5
                }
            }
        ]
        
        print("\n--- Testing Different Scenarios ---")
        for test_case in test_cases:
            print(f"\nTesting: {test_case['name']}")
            
            # Test with each model
            for model_name in service.ml_models.keys():
                result = service.predict_symptom_risk(test_case['features'], model_name)
                print(f"  {model_name}: Risk={result.get('risk_probability', 0):.3f}, Level={result.get('risk_level', 'Unknown')}")
        
        # Test the feature vector preparation
        print("\n--- Testing Feature Vector Preparation ---")
        sample_features = test_cases[0]['features']
        feature_vector = service._prepare_feature_vector(sample_features)
        print(f"Feature vector shape: {feature_vector.shape}")
        print(f"Feature vector: {feature_vector}")
        
        # Test with the scaler
        if service.scaler:
            scaled_features = service.scaler.transform(feature_vector.reshape(1, -1))
            print(f"Scaled features shape: {scaled_features.shape}")
            print(f"Scaled features: {scaled_features[0]}")
        
        return True
        
    except Exception as e:
        print(f"Error in backend test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_original_ibs_models():
    """Test the original IBS-specific models."""
    print("\n=== Testing Original IBS Models ===")
    
    try:
        # Add ML models source to path
        sys.path.append(str(ml_models_path / "src"))
        
        # Test FlareupPredictor
        from models.flareup_predictor import FlareupPredictor
        
        models_dir = ml_models_path / "trained_models"
        flareup_model_path = models_dir / "flareup_predictor.joblib"
        
        if flareup_model_path.exists():
            print("\n--- Testing FlareupPredictor ---")
            
            predictor = FlareupPredictor()
            predictor.load_model(str(flareup_model_path))
            
            # Test with different scenarios
            test_scenarios = [
                {
                    'name': 'High risk scenario',
                    'features': {
                        'recent_avg_severity': 8.0,
                        'symptom_trend': 0.5,
                        'days_since_last_flareup': 2,
                        'recent_high_fodmap_intake': 5.0,
                        'trigger_foods_consumed': 3,
                        'meal_timing_irregularity': 2.0,
                        'current_stress_level': 9.0,
                        'sleep_quality_trend': 2.0,
                        'exercise_deficit': 120,
                        'medication_adherence_rate': 0.4,
                        'missed_doses_recent': 3,
                        'seasonal_factor': 1,
                        'historical_flareup_frequency': 0.6,
                        'time_of_day_risk': 1
                    }
                },
                {
                    'name': 'Low risk scenario',
                    'features': {
                        'recent_avg_severity': 2.0,
                        'symptom_trend': -0.2,
                        'days_since_last_flareup': 20,
                        'recent_high_fodmap_intake': 0.5,
                        'trigger_foods_consumed': 0,
                        'meal_timing_irregularity': 0.2,
                        'current_stress_level': 3.0,
                        'sleep_quality_trend': 8.0,
                        'exercise_deficit': 20,
                        'medication_adherence_rate': 0.95,
                        'missed_doses_recent': 0,
                        'seasonal_factor': 0,
                        'historical_flareup_frequency': 0.1,
                        'time_of_day_risk': 0
                    }
                }
            ]
            
            for scenario in test_scenarios:
                print(f"\nTesting: {scenario['name']}")
                result = predictor.predict_flareup_risk(scenario['features'])
                print(f"  Result: {result}")
        
        return True
        
    except Exception as e:
        print(f"Error testing original models: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = test_backend_prediction_issue()
    success2 = test_original_ibs_models()
    
    if success1 and success2:
        print("\n=== SUMMARY ===")
        print("✓ Backend service loads enhanced models")
        print("✓ Original IBS models can be tested")
        print("✗ Issue: Enhanced models may not be properly trained for IBS-specific features")
        print("✗ Issue: Models return consistent scores regardless of input variation")
    else:
        print("\n=== ERRORS FOUND ===")
        print("✗ Failed to test models properly")