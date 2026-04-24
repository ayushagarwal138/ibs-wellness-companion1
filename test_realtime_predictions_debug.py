#!/usr/bin/env python3
"""
Test script to debug real-time predictions endpoint and enhanced ML models initialization.
"""

import requests
import json
import sys
from datetime import datetime

BACKEND_URL = "http://localhost:8000"

def test_realtime_predictions():
    """Test the real-time predictions endpoint and debug initialization issues."""
    print("🔍 Testing Real-time Predictions Endpoint")
    print("=" * 50)
    
    try:
        # First, register a test user
        print("1. Registering test user...")
        register_data = {
            "email": "realtime_test@example.com",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!",
            "first_name": "Realtime",
            "last_name": "Test",
            "date_of_birth": "1990-01-01",
            "gender": "other",
            "ibs_type": "ibs_d"
        }
        
        response = requests.post(f"{BACKEND_URL}/api/v1/auth/register", json=register_data)
        if response.status_code == 201:
            print("   ✅ User registered successfully")
        elif response.status_code == 400 and "already registered" in response.text:
            print("   ℹ️  User already exists, continuing...")
        else:
            print(f"   ❌ Registration failed: {response.status_code} - {response.text}")
            return False
        
        # Login to get token
        print("2. Logging in...")
        login_data = {
            "email": "realtime_test@example.com",
            "password": "TestPass123!"
        }
        
        response = requests.post(f"{BACKEND_URL}/api/v1/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"   ❌ Login failed: {response.status_code} - {response.text}")
            return False
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("   ✅ Login successful")
        
        # Test ML models info endpoint first
        print("3. Checking ML models info...")
        response = requests.get(f"{BACKEND_URL}/api/v1/ml/models/info", headers=headers)
        print(f"   Models info status: {response.status_code}")
        if response.status_code == 200:
            models_info = response.json()
            print(f"   Available models: {models_info.get('available_models', 0)}")
            print(f"   Models loaded: {models_info.get('models_loaded', False)}")
            print(f"   Model versions: {models_info.get('model_versions', {})}")
        else:
            print(f"   ❌ Models info failed: {response.text}")
        
        # Test the main realtime-predictions endpoint
        print("4. Testing realtime-predictions endpoint...")
        response = requests.get(f"{BACKEND_URL}/api/v1/ml/realtime-predictions", headers=headers)
        print(f"   Realtime predictions status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Realtime predictions successful!")
            print(f"   Current risk: {data.get('current_risk', 'N/A')}%")
            print(f"   Confidence score: {data.get('confidence_score', 'N/A')}")
            print(f"   Risk factors: {data.get('risk_factors', [])}")
            print(f"   Recommendations: {data.get('immediate_recommendations', [])}")
        else:
            print(f"   ❌ Realtime predictions failed: {response.text}")
            return False
        
        # Test the enhanced real-time predictions endpoint
        print("5. Testing enhanced real-time predictions endpoint...")
        enhanced_data = {
            "symptoms": {
                "abdominal_pain": 7,
                "bloating": 6,
                "diarrhea": 5,
                "stress_level": 8
            },
            "include_trends": True,
            "include_recommendations": True,
            "stream_updates": False
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/v1/ml/realtime/predict/enhanced", 
            json=enhanced_data, 
            headers=headers
        )
        print(f"   Enhanced predictions status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Enhanced predictions successful!")
            print(f"   Prediction data keys: {list(data.keys())}")
            if 'severity_prediction' in data:
                severity = data['severity_prediction']
                print(f"   Severity: {severity.get('predicted_severity', 'N/A')}")
                print(f"   Confidence: {severity.get('confidence', 'N/A')}")
        else:
            print(f"   ❌ Enhanced predictions failed: {response.text}")
        
        # Test model reload endpoint
        print("6. Testing model reload...")
        response = requests.post(f"{BACKEND_URL}/api/v1/ml/models/reload", headers=headers)
        print(f"   Model reload status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Model reload successful")
            reload_data = response.json()
            print(f"   Reload message: {reload_data.get('message', 'N/A')}")
        else:
            print(f"   ❌ Model reload failed: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def main():
    """Main test function."""
    print(f"🚀 Real-time Predictions Debug Test")
    print(f"⏰ Started at: {datetime.now()}")
    print()
    
    success = test_realtime_predictions()
    
    print()
    print("=" * 50)
    if success:
        print("✅ Real-time predictions test completed successfully!")
    else:
        print("❌ Real-time predictions test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()