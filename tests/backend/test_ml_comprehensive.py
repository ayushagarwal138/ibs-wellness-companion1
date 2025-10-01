#!/usr/bin/env python3
"""
Comprehensive ML Model Validation

This script tests all ML models to ensure they return reasonable and varied predictions.
"""

import sys
import numpy as np
from pathlib import Path

def test_enhanced_models():
    """Test the enhanced recommendation service."""
    print("=== Testing Enhanced Models ===")
    
    try:
        # Import the backend service
        sys.path.append(str(Path(__file__).parent))
        from app.services.enhanced_recommendation_service import EnhancedRecommendationService
        
        # Create a mock database session
        class MockDB:
            pass
        
        service = EnhancedRecommendationService(MockDB())
        
        print(f"✓ Loaded models: {list(service.ml_models.keys())}")
        print(f"✓ Feature names: {len(service.feature_names)} features")
        print(f"✓ Has scaler: {service.scaler is not None}")
        
        # Test scenarios with different risk levels
        test_scenarios = [
            {
                'name': 'Low risk user',
                'features': {
                    'total_symptom_logs': 5,
                    'severe_symptoms': 0,
                    'moderate_symptoms': 2,
                    'avg_pain_level': 2,
                    'bowel_movement_logs': 10,
                    'food_reactions': 1,
                    'severe_food_reactions': 0,
                    'medication_logs': 8,
                    'age': 25,
                    'is_female': 1,
                    'stress_level': 3,
                    'sleep_score': 8,
                    'fodmap_load_score': 2,
                    'daily_fiber_estimate': 30,
                    'wellness_composite': 8,
                    'exercise_frequency': 5,
                    'hydration_level': 8,
                    'meal_regularity': 9,
                    'social_support': 7,
                    'work_stress': 3
                }
            },
            {
                'name': 'High risk user',
                'features': {
                    'total_symptom_logs': 25,
                    'severe_symptoms': 8,
                    'moderate_symptoms': 12,
                    'avg_pain_level': 8,
                    'bowel_movement_logs': 3,
                    'food_reactions': 10,
                    'severe_food_reactions': 5,
                    'medication_logs': 2,
                    'age': 45,
                    'is_female': 1,
                    'stress_level': 9,
                    'sleep_score': 3,
                    'fodmap_load_score': 9,
                    'daily_fiber_estimate': 10,
                    'wellness_composite': 2,
                    'exercise_frequency': 1,
                    'hydration_level': 3,
                    'meal_regularity': 2,
                    'social_support': 3,
                    'work_stress': 9
                }
            },
            {
                'name': 'Medium risk user',
                'features': {
                    'total_symptom_logs': 15,
                    'severe_symptoms': 3,
                    'moderate_symptoms': 7,
                    'avg_pain_level': 5,
                    'bowel_movement_logs': 6,
                    'food_reactions': 5,
                    'severe_food_reactions': 2,
                    'medication_logs': 5,
                    'age': 35,
                    'is_female': 0,
                    'stress_level': 6,
                    'sleep_score': 5,
                    'fodmap_load_score': 5,
                    'daily_fiber_estimate': 20,
                    'wellness_composite': 5,
                    'exercise_frequency': 3,
                    'hydration_level': 5,
                    'meal_regularity': 6,
                    'social_support': 5,
                    'work_stress': 6
                }
            }
        ]
        
        results = []
        for scenario in test_scenarios:
            result = service.predict_symptom_risk(scenario['features'])
            results.append((scenario['name'], result))
            print(f"\n{scenario['name']}:")
            print(f"  Risk Probability: {result.get('risk_probability', 'N/A'):.3f}")
            print(f"  Risk Level: {result.get('risk_level', 'N/A')}")
            print(f"  Confidence: {result.get('confidence', 'N/A'):.3f}")
            print(f"  Model Used: {result.get('model_used', 'N/A')}")
        
        # Check if results are varied
        probabilities = [r[1].get('risk_probability', 0) for r in results]
        if len(set([round(p, 1) for p in probabilities])) > 1:
            print("\n✓ Enhanced models return varied predictions")
            return True
        else:
            print("\n✗ Enhanced models return similar predictions for different scenarios")
            return False
            
    except Exception as e:
        print(f"✗ Error testing enhanced models: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flareup_predictor():
    """Test the FlareupPredictor."""
    print("\n=== Testing FlareupPredictor ===")
    
    try:
        # Import the FlareupPredictor
        ml_models_path = Path(__file__).parent.parent / "ml-models"
        sys.path.append(str(ml_models_path / "src"))
        from models.flareup_predictor import FlareupPredictor
        
        # Load the model
        model_path = ml_models_path / "trained_models" / "flareup_predictor.joblib"
        if not model_path.exists():
            print(f"✗ FlareupPredictor model not found at {model_path}")
            return False
        
        predictor = FlareupPredictor()
        predictor.load_model(str(model_path))
        print("✓ FlareupPredictor loaded successfully")
        
        # Test scenarios
        test_scenarios = [
            {
                'name': 'Very low risk',
                'features': {
                    'recent_avg_severity': 1.0,
                    'current_stress_level': 2.0,
                    'days_since_last_flareup': 30,
                    'recent_high_fodmap_intake': 0.5,
                    'trigger_foods_consumed': 0,
                    'sleep_quality_trend': 9.0,
                    'medication_adherence_rate': 0.95
                }
            },
            {
                'name': 'Low risk',
                'features': {
                    'recent_avg_severity': 3.0,
                    'current_stress_level': 4.0,
                    'days_since_last_flareup': 20,
                    'recent_high_fodmap_intake': 1.0,
                    'trigger_foods_consumed': 0,
                    'sleep_quality_trend': 7.0,
                    'medication_adherence_rate': 0.9
                }
            },
            {
                'name': 'Medium risk',
                'features': {
                    'recent_avg_severity': 5.0,
                    'current_stress_level': 6.0,
                    'days_since_last_flareup': 10,
                    'recent_high_fodmap_intake': 3.0,
                    'trigger_foods_consumed': 1,
                    'sleep_quality_trend': 5.0,
                    'medication_adherence_rate': 0.7
                }
            },
            {
                'name': 'High risk',
                'features': {
                    'recent_avg_severity': 8.0,
                    'current_stress_level': 9.0,
                    'days_since_last_flareup': 2,
                    'recent_high_fodmap_intake': 7.0,
                    'trigger_foods_consumed': 3,
                    'sleep_quality_trend': 2.0,
                    'medication_adherence_rate': 0.4
                }
            },
            {
                'name': 'Very high risk',
                'features': {
                    'recent_avg_severity': 10.0,
                    'current_stress_level': 10.0,
                    'days_since_last_flareup': 1,
                    'recent_high_fodmap_intake': 10.0,
                    'trigger_foods_consumed': 5,
                    'sleep_quality_trend': 1.0,
                    'medication_adherence_rate': 0.2
                }
            }
        ]
        
        results = []
        for scenario in test_scenarios:
            result = predictor.predict_flareup_risk(scenario['features'])
            results.append((scenario['name'], result))
            print(f"\n{scenario['name']}:")
            print(f"  Flareup Probability: {result['flareup_probability']:.3f}")
            print(f"  Risk Level: {result['risk_level']}")
            print(f"  Contributing Factors: {len(result['contributing_factors'])}")
            print(f"  Recommendations: {len(result['recommendations'])}")
        
        # Validate results
        probabilities = [r[1]['flareup_probability'] for r in results]
        
        # Check if probabilities are in ascending order (roughly)
        if probabilities[0] < probabilities[2] < probabilities[4]:
            print("\n✓ FlareupPredictor returns varied predictions based on risk level")
            
            # Check reasonable ranges
            if probabilities[0] < 0.4 and probabilities[-1] > 0.6:
                print("✓ FlareupPredictor returns reasonable probability ranges")
                return True
            else:
                print(f"✗ Probability ranges seem unreasonable: {probabilities[0]:.3f} to {probabilities[-1]:.3f}")
                return False
        else:
            print(f"✗ FlareupPredictor doesn't show clear risk progression: {[round(p, 3) for p in probabilities]}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing FlareupPredictor: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_comprehensive_validation():
    """Run comprehensive validation of all ML models."""
    print("🔬 Running Comprehensive ML Model Validation")
    print("=" * 60)
    
    results = {
        'enhanced_models': False,
        'flareup_predictor': False
    }
    
    # Test enhanced models
    results['enhanced_models'] = test_enhanced_models()
    
    # Test FlareupPredictor
    results['flareup_predictor'] = test_flareup_predictor()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 VALIDATION SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All ML models are working correctly!")
        return True
    else:
        print("⚠️  Some ML models need attention")
        return False

if __name__ == "__main__":
    success = run_comprehensive_validation()
    sys.exit(0 if success else 1)