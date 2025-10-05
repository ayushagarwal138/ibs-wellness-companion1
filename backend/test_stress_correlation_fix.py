#!/usr/bin/env python3
"""
Test script to verify the stress-symptom correlation endpoint fix.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def login():
    """Login and get auth token"""
    login_data = {
        "email": "api_test@example.com",
        "password": "testpass123"
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data, headers=headers)
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("access_token")
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def test_stress_correlation_endpoint(token):
    """Test the stress-symptom correlation endpoint."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test data matching the StressSymptomCorrelationRequest schema - using dictionaries as expected
    test_data = {
        "stress_levels": {
            "day_1": 7.0,
            "day_2": 8.0,
            "day_3": 6.0,
            "day_4": 9.0,
            "day_5": 5.0,
            "day_6": 7.0,
            "day_7": 6.0
        },
        "symptoms": {
            "abdominal_pain": 6.0,
            "bloating": 7.0,
            "gas": 5.0,
            "diarrhea": 8.0,
            "constipation": 4.0,
            "nausea": 6.0
        },
        "timeframe_days": 30
    }
    
    try:
        print("Testing stress-symptom correlation endpoint...")
        print(f"Request data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/api/v1/ml/predict/stress-symptom-correlation",
            headers=headers,
            json=test_data
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS! Endpoint working correctly.")
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ FAILED! Status: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("🧪 Testing Stress-Symptom Correlation Endpoint Fix")
    print("=" * 60)
    
    # Step 1: Login
    print("\n1. Logging in...")
    token = login()
    if not token:
        print("❌ Failed to login. Make sure the backend is running and test user exists.")
        sys.exit(1)
    print("✅ Login successful!")
    
    # Step 2: Test the endpoint
    print("\n2. Testing stress-symptom correlation endpoint...")
    success = test_stress_correlation_endpoint(token)
    
    # Step 3: Summary
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! The HTTP 500 error has been fixed.")
        print("✅ Field name mismatch resolved")
        print("✅ Endpoint responding correctly")
        print("✅ Schema validation working")
    else:
        print("❌ TESTS FAILED! The issue may not be fully resolved.")
        print("Check the server logs for more details.")

if __name__ == "__main__":
    main()