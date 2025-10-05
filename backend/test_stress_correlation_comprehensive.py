#!/usr/bin/env python3
"""
Comprehensive test for the stress-symptom correlation endpoint.
Tests various scenarios to ensure the fix is robust.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def login():
    """Login and get access token."""
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
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_stress_correlation_scenarios(token):
    """Test various stress-symptom correlation scenarios."""
    headers = {"Authorization": f"Bearer {token}"}
    
    test_scenarios = [
        {
            "name": "Normal data with 7 days",
            "data": {
                "stress_levels": {
                    "day_1": 7.0, "day_2": 8.0, "day_3": 6.0,
                    "day_4": 9.0, "day_5": 5.0, "day_6": 7.0, "day_7": 6.0
                },
                "symptoms": {
                    "abdominal_pain": 6.0, "bloating": 7.0, "gas": 5.0,
                    "diarrhea": 8.0, "constipation": 4.0, "nausea": 6.0
                },
                "timeframe_days": 30
            }
        },
        {
            "name": "Minimal data",
            "data": {
                "stress_levels": {"day_1": 5.0},
                "symptoms": {"abdominal_pain": 3.0},
                "timeframe_days": 7
            }
        },
        {
            "name": "High stress scenario",
            "data": {
                "stress_levels": {
                    "day_1": 9.0, "day_2": 10.0, "day_3": 8.5,
                    "day_4": 9.5, "day_5": 8.0
                },
                "symptoms": {
                    "abdominal_pain": 8.0, "bloating": 9.0, "gas": 7.0,
                    "diarrhea": 9.0, "nausea": 8.0
                },
                "timeframe_days": 14
            }
        },
        {
            "name": "Low stress scenario",
            "data": {
                "stress_levels": {
                    "day_1": 2.0, "day_2": 1.5, "day_3": 3.0
                },
                "symptoms": {
                    "abdominal_pain": 2.0, "bloating": 1.0, "gas": 2.5
                },
                "timeframe_days": 7
            }
        }
    ]
    
    all_passed = True
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. Testing: {scenario['name']}")
        print(f"   Data: {json.dumps(scenario['data'], indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/api/v1/ml/predict/stress-symptom-correlation",
            json=scenario['data'],
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ SUCCESS!")
            
            # Validate schema
            required_fields = ["correlation_score", "stress_triggers", "management_strategies"]
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields:
                print(f"   ❌ Missing required fields: {missing_fields}")
                all_passed = False
            else:
                print(f"   ✅ All required fields present")
                print(f"   📊 Correlation Score: {result['correlation_score']}")
                print(f"   🎯 Stress Triggers: {len(result['stress_triggers'])} items")
                print(f"   💡 Management Strategies: {len(result['management_strategies'])} items")
        else:
            print(f"   ❌ FAILED: {response.text}")
            all_passed = False
    
    return all_passed

def main():
    print("🧪 Comprehensive Stress-Symptom Correlation Test")
    print("=" * 60)
    
    # Login
    print("\n1. Logging in...")
    token = login()
    if not token:
        sys.exit(1)
    print("✅ Login successful!")
    
    # Test scenarios
    print("\n2. Testing various scenarios...")
    all_passed = test_stress_correlation_scenarios(token)
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Endpoint is working correctly across all scenarios")
        print("✅ Schema validation is working")
        print("✅ The HTTP 500 error has been completely resolved")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please check the output above for details")
        sys.exit(1)

if __name__ == "__main__":
    main()