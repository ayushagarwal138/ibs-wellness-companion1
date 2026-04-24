#!/usr/bin/env python3
"""
Test script to verify the ML severity prediction endpoint fix.
"""

import requests
import json

# Backend URL
BACKEND_URL = "http://localhost:8000"

def test_ml_severity_prediction():
    """Test the ML severity prediction endpoint with proper authentication."""
    
    # First, try to login to get a token
    login_data = {
        "email": "test@example.com",
        "password": "TestPassword123!"
    }
    
    print("🔐 Attempting to login...")
    try:
        login_response = requests.post(
            f"{BACKEND_URL}/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            print(f"✅ Login successful! Token: {access_token[:20]}...")
            
            # Now test the ML severity prediction endpoint
            print("\n🤖 Testing ML severity prediction endpoint...")
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Test data for severity prediction
            prediction_data = {
                "symptoms": {
                    "abdominal_pain": 3,
                    "bloating": 2,
                    "diarrhea": 1,
                    "constipation": 0,
                    "nausea": 1
                },
                "additional_factors": {
                    "stress_level": 2,
                    "sleep_quality": 3,
                    "mood_score": 2
                }
            }
            
            ml_response = requests.post(
                f"{BACKEND_URL}/api/v1/ml/predict/severity",
                json=prediction_data,
                headers=headers
            )
            
            print(f"Status Code: {ml_response.status_code}")
            
            if ml_response.status_code == 200:
                print("✅ ML severity prediction endpoint working!")
                response_data = ml_response.json()
                print(f"Response: {json.dumps(response_data, indent=2, default=str)}")
                
                # Check if the response has expected fields
                expected_fields = ["severity_score", "severity_level", "confidence", "predicted_at"]
                missing_fields = [field for field in expected_fields if field not in response_data]
                
                if not missing_fields:
                    print("✅ All expected fields present in response!")
                else:
                    print(f"⚠️ Missing fields in response: {missing_fields}")
                    
            else:
                print(f"❌ ML endpoint failed with {ml_response.status_code}")
                print(f"Error response: {ml_response.text}")
                
        else:
            print(f"❌ Login failed with status {login_response.status_code}")
            print(f"Response: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ml_severity_prediction()