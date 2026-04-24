#!/usr/bin/env python3
"""Test script to verify trained ML models."""

import joblib
import numpy as np
import json
from pathlib import Path

def test_model_loading():
    """Test loading all trained models."""
    checkpoints_dir = Path(__file__).parent.parent.parent / "checkpoints"
    
    models_to_test = [
        "severity_classifier.pkl",
        "flareup_predictor.pkl", 
        "medication_effectiveness.pkl",
        "dietary_triggers.pkl",
        "stress_correlation.pkl",
        "sleep_impact.pkl",
        "exercise_tolerance.pkl",
        "symptom_progression.pkl",
        "treatment_response.pkl"
    ]
    
    print("Testing model loading...")
    print("=" * 50)
    
    for model_name in models_to_test:
        model_path = checkpoints_dir / model_name
        try:
            model = joblib.load(model_path)
            print(f"✅ {model_name}: Loaded successfully")
            print(f"   Type: {type(model).__name__}")
            
            # Test basic prediction if possible
            if hasattr(model, 'predict'):
                try:
                    # Create dummy input data with correct shape
                    if 'severity' in model_name or 'flareup' in model_name:
                        dummy_input = np.random.rand(1, 10)
                    else:
                        dummy_input = np.random.rand(1, 15)
                    
                    prediction = model.predict(dummy_input)
                    print(f"   Prediction test: ✅ (shape: {np.array(prediction).shape})")
                except Exception as e:
                    print(f"   Prediction test: ⚠️  ({str(e)[:50]}...)")
            
        except Exception as e:
            print(f"❌ {model_name}: Failed to load - {e}")
        
        print()

def test_metadata():
    """Test loading training metadata."""
    checkpoints_dir = Path(__file__).parent.parent.parent / "checkpoints"
    metadata_path = checkpoints_dir / "training_metadata.json"
    
    print("Testing metadata loading...")
    print("=" * 50)
    
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        print("✅ Training metadata loaded successfully")
        timestamp = metadata.get('training_timestamp', 'N/A')
        print(f"   Training timestamp: {timestamp}")
        models = metadata.get('models', {})
        print(f"   Number of models: {len(models)}")
        
        for model_name, model_info in models.items():
            print(f"   {model_name}:")
            accuracy = model_info.get('accuracy', model_info.get('r2_score', 'N/A'))
            print(f"     - Accuracy/R²: {accuracy}")
            model_type = model_info.get('model_type', 'N/A')
            print(f"     - Model type: {model_type}")
        
    except Exception as e:
        print(f"❌ Failed to load metadata: {e}")

if __name__ == "__main__":
    print("ML Models Test Suite")
    print("=" * 60)
    print()
    
    test_model_loading()
    print()
    test_metadata()
    
    print("\nTest completed!")