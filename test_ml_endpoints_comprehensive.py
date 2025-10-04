#!/usr/bin/env python3
"""
Comprehensive test script for ML endpoints after fixes
Tests all ML prediction endpoints with proper authentication
"""

import requests
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"


def get_auth_token():
    """Get authentication token for API requests."""
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login",
                            json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Authentication failed: {response.status_code} - "
              f"{response.text}")
        return None


def test_severity_prediction(token):
    """Test severity prediction endpoint with triggers as dictionary"""
    print("\n🧪 Testing Severity Prediction...")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "symptoms": {
            "pain_level": 6,
            "bloating": 7,
            "diarrhea": 4,
            "constipation": 2,
            "nausea": 3,
            "fatigue": 5
        },
        "context": {
            "stress_level": 7,
            "sleep_quality": 5,
            "recent_meals": ["dairy", "spicy food"],
            "medications": ["probiotics"]
        },
        "triggers": {
            "foods": ["dairy", "spicy food"],
            "stress_level": 7,
            "sleep_quality": 5,
            "medications": ["probiotics"]
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/ml/predict/severity",
                             headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        severity = result['severity_level']
        score = result['severity_score']
        print(f"✅ Severity Prediction: {severity} (score: {score:.2f})")
        return True
    else:
        print(f"❌ Severity Prediction failed: {response.status_code} - "
              f"{response.text}")
        return False

def test_medication_effectiveness(token):
    """Test medication effectiveness endpoint"""
    print("\n💊 Testing Medication Effectiveness...")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "medication_history": [
            {
                "medication": "Probiotics",
                "dosage": "1 capsule",
                "frequency": "daily",
                "adherence_rate": 0.9,
                "effectiveness_score": 7,
                "side_effects": [],
                "duration_days": 30
            }
        ],
        "current_symptoms": {
            "abdominal_pain": 6,
            "diarrhea": 4,
            "bloating": 7,
            "constipation": 2,
            "nausea": 3
        },
        "user_profile": {
            "age": 30,
            "weight": 70,
            "ibs_type": "IBS-M",
            "comorbidities": []
        },
        "prediction_period": 30
    }
    
    url = f"{BASE_URL}/api/v1/ml/predict/medication-effectiveness"
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        effectiveness = result['effectiveness_score']
        confidence = result['confidence']
        print(f"✅ Medication Effectiveness: {effectiveness:.2f} "
              f"(confidence: {confidence:.2f})")
        return True
    else:
        print(f"❌ Medication Effectiveness failed: "
              f"{response.status_code} - {response.text}")
        return False

def test_flareup_prediction(token):
    """Test flareup prediction endpoint"""
    print("\n🔥 Testing Flareup Prediction...")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "recent_symptoms": [
            {
                "date": "2024-01-15",
                "symptoms": {
                    "abdominal_pain": 6,
                    "bloating": 7,
                    "diarrhea": 4,
                    "constipation": 2
                },
                "triggers": ["stress", "dairy"]
            }
        ],
        "lifestyle_factors": {
            "stress_level": 7,
            "sleep_quality": 5,
            "exercise_frequency": 3,
            "diet_adherence": 6
        },
        "prediction_horizon": 7
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/ml/predict/flareup",
                             headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        risk_level = result['risk_level']
        probability = result['flareup_probability']
        print(f"✅ Flareup Prediction: {risk_level} "
              f"(probability: {probability:.2f})")
        return True
    else:
        print(f"❌ Flareup Prediction failed: {response.status_code} - "
              f"{response.text}")
        return False

def test_model_info(token):
    """Test model info endpoint"""
    print("\n📊 Testing Model Info...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/ml/models/info",
                            headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        active = result['active_models']
        total = result['total_models']
        print(f"✅ Model Info: {active}/{total} models active")
        return True
    else:
        print(f"❌ Model Info failed: {response.status_code} - "
              f"{response.text}")
        return False

def test_personalized_recommendations(token):
    """Test personalized recommendations endpoint"""
    print("\n🎯 Testing Personalized Recommendations...")
    
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/api/v1/recommendations/personalized"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        dietary_recs = len(result.get('dietary_recommendations', []))
        print(f"✅ Personalized Recommendations: {dietary_recs} "
              f"dietary recommendations")
        return True
    else:
        print(f"❌ Personalized Recommendations failed: "
              f"{response.status_code} - {response.text}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Comprehensive ML Endpoints Test")
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"⏰ Test started at: {timestamp}")
    
    # Get authentication token
    print("\n🔐 Getting authentication token...")
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        sys.exit(1)
    
    print("✅ Authentication successful")
    
    # Run all tests
    tests = [
        ("Severity Prediction", test_severity_prediction),
        ("Medication Effectiveness", test_medication_effectiveness),
        ("Flareup Prediction", test_flareup_prediction),
        ("Model Info", test_model_info),
        ("Personalized Recommendations", test_personalized_recommendations)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func(token)
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📋 TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! ML endpoints are working correctly.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()