#!/usr/bin/env python3
"""
Test script to verify all ML prediction endpoints are working correctly.
"""

import requests
import json
import sys
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"

def login():
    """Login and get access token."""
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_endpoint(endpoint, method="GET", data=None, headers=None, description=""):
    """Test a single endpoint."""
    print(f"\n🧪 Testing {description}: {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data, headers=headers)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ SUCCESS")
            return True
        else:
            print(f"   ❌ FAILED: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def main():
    print("🚀 Testing ML Prediction Endpoints")
    print("=" * 50)
    
    # Login
    print("\n🔐 Logging in...")
    token = login()
    if not token:
        print("❌ Failed to login. Exiting.")
        sys.exit(1)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test results
    results = []
    
    # 1. Test model info endpoint
    results.append(test_endpoint(
        "/ml/models/info",
        "GET",
        headers=headers,
        description="Model Info"
    ))
    
    # 2. Test severity prediction
    severity_data = {
        "symptoms": {
            "abdominal_pain": 7.5,
            "bloating": 6.0,
            "gas": 4.5,
            "diarrhea": 3.0,
            "constipation": 0.0,
            "nausea": 2.5
        },
        "triggers": {
            "foods": ["dairy", "gluten"],
            "stress_level": 8,
            "sleep_quality": 4
        },
        "user_context": {
            "age": 32,
            "gender": "female",
            "ibs_type": "IBS-D"
        }
    }
    
    results.append(test_endpoint(
        "/ml/predict/severity",
        "POST",
        data=severity_data,
        headers=headers,
        description="Severity Prediction"
    ))
    
    # 3. Test flareup prediction
    flareup_data = {
        "recent_symptoms": [
            {
                "date": "2024-01-15",
                "symptoms": {"abdominal_pain": 6, "bloating": 7},
                "triggers": ["stress", "dairy"]
            }
        ],
        "lifestyle_factors": {
            "stress_level": 7,
            "sleep_quality": 5,
            "exercise_frequency": 2,
            "diet_adherence": 0.8
        },
        "prediction_horizon": 7
    }
    
    results.append(test_endpoint(
        "/ml/predict/flareup",
        "POST",
        data=flareup_data,
        headers=headers,
        description="Flareup Prediction"
    ))
    
    # 4. Test recommendations
    recommendation_data = {
        "user_profile": {
            "age": 28,
            "ibs_type": "IBS-M",
            "dietary_restrictions": ["lactose_intolerant"],
            "activity_level": "moderate"
        },
        "current_symptoms": {
            "abdominal_pain": 5.5,
            "bloating": 7.0,
            "gas": 4.0
        },
        "preferences": {
            "dietary_approach": "low_fodmap",
            "exercise_preference": "yoga",
            "supplement_tolerance": "high"
        },
        "recommendation_types": ["dietary", "lifestyle", "supplements"]
    }
    
    results.append(test_endpoint(
        "/ml/recommendations",
        "POST",
        data=recommendation_data,
        headers=headers,
        description="Recommendations"
    ))
    
    # 5. Test medication effectiveness prediction
    medication_data = {
        "medication_history": [
            {
                "medication": "loperamide",
                "dosage": "2mg",
                "frequency": "twice_daily",
                "adherence_rate": 0.85,
                "effectiveness_score": 7.2,
                "side_effects": ["mild_constipation"],
                "duration_days": 30
            }
        ],
        "current_symptoms": {
            "diarrhea": 6.5,
            "urgency": 7.0,
            "abdominal_pain": 5.5
        },
        "user_profile": {
            "age": 35,
            "weight": 70,
            "ibs_subtype": "IBS-D",
            "comorbidities": []
        },
        "prediction_period": 30
    }
    
    results.append(test_endpoint(
        "/ml/predict/medication-effectiveness",
        "POST",
        data=medication_data,
        headers=headers,
        description="Medication Effectiveness"
    ))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All ML endpoints are working correctly!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} endpoint(s) failed. Check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()