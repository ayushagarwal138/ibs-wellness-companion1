#!/usr/bin/env python3
"""
Test script to reproduce the ML endpoint 500 error with proper authentication.
"""

import requests
import json

# Backend URL
BACKEND_URL = "http://localhost:8000"

def test_ml_endpoint():
    """Test the ML real-time predictions endpoint with authentication."""
    
    # First, try to login to get a token
    login_data = {
        "username": "test@example.com",  # Default test user
        "password": "testpassword123"
    }
    
    print("🔐 Attempting to login...")
    try:
        login_response = requests.post(
            f"{BACKEND_URL}/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            print(f"✅ Login successful! Token: {access_token[:20]}...")
            
            # Now test the ML endpoint
            print("\n🤖 Testing ML real-time predictions endpoint...")
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            ml_response = requests.get(
                f"{BACKEND_URL}/api/v1/ml/realtime-predictions",
                headers=headers
            )
            
            print(f"Status Code: {ml_response.status_code}")
            print(f"Response Headers: {dict(ml_response.headers)}")
            
            if ml_response.status_code == 200:
                print("✅ ML endpoint working!")
                print(f"Response: {json.dumps(ml_response.json(), indent=2)}")
            else:
                print(f"❌ ML endpoint failed with {ml_response.status_code}")
                print(f"Error response: {ml_response.text}")
                
        else:
            print(f"❌ Login failed with status {login_response.status_code}")
            print(f"Response: {login_response.text}")
            
            # Try without authentication to see the error
            print("\n🔍 Testing ML endpoint without authentication...")
            ml_response = requests.get(f"{BACKEND_URL}/api/v1/ml/realtime-predictions")
            print(f"Status Code: {ml_response.status_code}")
            print(f"Response: {ml_response.text}")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    test_ml_endpoint()