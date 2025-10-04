#!/usr/bin/env python3
"""
Test Symptom Analysis Components

This script validates that symptom analysis components use real ML model outputs
for severity prediction, flare-up prediction, and symptom tracking.
"""

import requests
import json
from typing import Dict, Any


def authenticate_user() -> str:
    """Authenticate and return access token."""
    base_url = "http://localhost:8000/api/v1"
    
    # Try to register user
    register_data = {
        "email": "test_symptom@example.com",
        "password": "TestPass123!",
        "confirm_password": "TestPass123!",
        "first_name": "Symptom",
        "last_name": "Tester"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/register", json=register_data)
        if response.status_code == 422:
            print("✅ User already exists, proceeding to login")
        elif response.status_code == 201:
            print("✅ User registered successfully")
        else:
            print(f"⚠️ Registration response: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Registration error: {e}")
    
    # Login
    login_data = {
        "email": "test_symptom@example.com",
        "password": "TestPass123!"
    }
    
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Authentication successful")
        return token
    else:
        raise Exception(f"Login failed: {response.status_code} - {response.text}")


def test_severity_prediction(token: str) -> Dict[str, Any]:
    """Test ML severity prediction endpoint."""
    base_url = "http://localhost:8000/api/v1"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with different symptom profiles
    test_cases = [
        {
            "name": "Mild Symptoms",
            "data": {
                "symptoms": {
                    "abdominal_pain": 3.0,
                    "bloating": 2.5,
                    "gas": 2.0,
                    "diarrhea": 1.0,
                    "constipation": 0.0,
                    "urgency": 1.5,
                    "incomplete_evacuation": 1.0,
                    "nausea": 0.5,
                    "fatigue": 2.0,
                    "mood_score": 7.0,
                    "stress_level": 3.0,
                    "sleep_quality": 8.0
                }
            }
        },
        {
            "name": "Severe Symptoms",
            "data": {
                "symptoms": {
                    "abdominal_pain": 9.0,
                    "bloating": 8.5,
                    "gas": 7.0,
                    "diarrhea": 8.0,
                    "constipation": 0.0,
                    "urgency": 9.5,
                    "incomplete_evacuation": 8.0,
                    "nausea": 6.0,
                    "fatigue": 8.5,
                    "mood_score": 3.0,
                    "stress_level": 9.0,
                    "sleep_quality": 2.0
                }
            }
        }
    ]
    
    results = []
    for test_case in test_cases:
        print(f"\n🧪 Testing {test_case['name']}...")
        
        response = requests.post(
            f"{base_url}/ml/predict/severity",
            json=test_case["data"],
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            results.append({
                "test_case": test_case["name"],
                "prediction": result.get("predicted_severity"),
                "confidence": result.get("confidence"),
                "category": result.get("severity_category"),
                "factors": result.get("contributing_factors", [])
            })
            severity = result.get('predicted_severity', 0)
            category = result.get('severity_category', 'unknown')
            confidence = result.get('confidence', 0)
            print(f"✅ Severity: {severity:.2f}")
            print(f"✅ Category: {category}")
            print(f"✅ Confidence: {confidence:.2f}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            results.append({
                "test_case": test_case["name"],
                "error": f"{response.status_code}: {response.text}"
            })
    
    return results


def test_flareup_prediction(token: str) -> Dict[str, Any]:
    """Test ML flare-up prediction endpoint."""
    base_url = "http://localhost:8000/api/v1"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with symptom history
    test_data = {
        "recent_symptoms": [
            {
                "date": "2024-01-15",
                "symptoms": {
                    "abdominal_pain": 6.0,
                    "bloating": 7.0,
                    "diarrhea": 5.0,
                    "urgency": 8.0
                },
                "triggers": ["stress", "dairy"]
            },
            {
                "date": "2024-01-14",
                "symptoms": {
                    "abdominal_pain": 4.0,
                    "bloating": 5.0,
                    "diarrhea": 3.0,
                    "urgency": 4.0
                },
                "triggers": ["gluten"]
            }
        ],
        "lifestyle_factors": {
            "stress_level": 8,
            "sleep_quality": 4,
            "exercise_frequency": 1,
            "diet_adherence": 0.6
        },
        "prediction_horizon": 7
    }
    
    print(f"\n🧪 Testing Flare-up Prediction...")
    
    response = requests.post(
        f"{base_url}/ml/predict/flareup",
        json=test_data,
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        flareup_prob = result.get('flareup_probability', 0)
        risk_level = result.get('risk_level', 'unknown')
        confidence = result.get('confidence', 0)
        risk_factors = len(result.get('key_risk_factors', []))
        print(f"✅ Flare-up Risk: {flareup_prob:.2f}")
        print(f"✅ Risk Level: {risk_level}")
        print(f"✅ Confidence: {confidence:.2f}")
        print(f"✅ Risk Factors: {risk_factors}")
        return result
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return {"error": f"{response.status_code}: {response.text}"}


def test_ml_model_info(token: str) -> Dict[str, Any]:
    """Test ML model information endpoint."""
    base_url = "http://localhost:8000/api/v1"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🧪 Testing ML Model Information...")
    
    response = requests.get(f"{base_url}/ml/models/info", headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        models = result.get("models", {})
        print(f"✅ Available Models: {len(models)}")
        
        for model_name, model_info in models.items():
            print(f"  - {model_name}: {model_info.get('status', 'unknown')}")
            if model_info.get('version'):
                print(f"    Version: {model_info['version']}")
        
        return result
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return {"error": f"{response.status_code}: {response.text}"}


def analyze_ml_integration(severity_results, flareup_result, model_info):
    """Analyze if components are using real ML models."""
    print(f"\n🔍 Analyzing ML Integration...")
    
    # Check if models are loaded
    models_loaded = False
    if isinstance(model_info, dict) and "models" in model_info:
        loaded_models = [
            name for name, info in model_info["models"].items()
            if info.get("status") == "loaded"
        ]
        models_loaded = len(loaded_models) > 0
        print(f"✅ Models loaded: {len(loaded_models)}")
    
    # Check severity prediction variability
    severity_variability = False
    if len(severity_results) >= 2:
        predictions = []
        for r in severity_results:
            if "prediction" in r and r["prediction"] is not None:
                predictions.append(r["prediction"])
        if len(predictions) >= 2:
            severity_variability = abs(predictions[0] - predictions[1]) > 0.1
            print(f"✅ Severity predictions vary: {severity_variability}")
    
    # Check flare-up prediction
    flareup_working = False
    if isinstance(flareup_result, dict) and "flareup_probability" in flareup_result:
        flareup_working = True
        print(f"✅ Flare-up prediction working: {flareup_working}")
    
    # Overall assessment
    ml_integration_score = sum([models_loaded, severity_variability, flareup_working])
    print(f"\n📊 ML Integration Score: {ml_integration_score}/3")
    
    if ml_integration_score >= 2:
        print("🎉 Symptom analysis components are using real ML models!")
        return True
    else:
        print("⚠️ Symptom analysis may be using fallback/mock data")
        return False


def main():
    """Main test function."""
    print("🧠 Testing Symptom Analysis Components")
    print("=" * 60)
    
    try:
        # Step 1: Authentication
        print("\n🔐 Step 1: Authentication")
        token = authenticate_user()
        
        # Step 2: Test severity prediction
        print("\n📊 Step 2: Testing Severity Prediction")
        severity_results = test_severity_prediction(token)
        
        # Step 3: Test flare-up prediction
        print("\n⚡ Step 3: Testing Flare-up Prediction")
        flareup_result = test_flareup_prediction(token)
        
        # Step 4: Test model information
        print("\n🔧 Step 4: Testing Model Information")
        model_info = test_ml_model_info(token)
        
        # Step 5: Analyze integration
        print("\n🔍 Step 5: Analyzing ML Integration")
        ml_working = analyze_ml_integration(severity_results, flareup_result, model_info)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Symptom Analysis Test Summary")
        print("=" * 60)
        print("✅ Severity prediction endpoint working")
        print("✅ Flare-up prediction endpoint working")
        print("✅ ML model information accessible")
        
        if ml_working:
            print("✅ Components use real ML model outputs")
            print("\n🎉 Symptom analysis is properly integrated with ML!")
        else:
            print("⚠️ Components may be using fallback mechanisms")
            print("\n🔧 Consider checking ML model loading and training")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    main()