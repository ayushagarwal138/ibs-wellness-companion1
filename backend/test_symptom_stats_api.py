#!/usr/bin/env python3
"""
Test script to verify the symptom statistics API endpoint works correctly.
"""

import requests
import json


# API configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_EMAIL = "test_api@example.com"
TEST_PASSWORD = "testpassword123"


def authenticate():
    """Authenticate and get access token."""
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        f"{BASE_URL}/auth/login", json=login_data, headers=headers
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    else:
        print(f"Authentication failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None


def test_symptom_stats(token):
    """Test the symptom statistics endpoint."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test the symptom stats endpoint
    response = requests.get(
        f"{BASE_URL}/symptom-logs/stats/summary?days=30", headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Symptom stats API working!")
        print(f"Response data: {json.dumps(data, indent=2)}")
        return True
    else:
        print(f"❌ Symptom stats API failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False


def main():
    print("🔐 Authenticating...")
    token = authenticate()
    
    if not token:
        print("❌ Authentication failed. Cannot test symptom stats.")
        return
    
    print(f"✅ Authentication successful! Token: {token[:20]}...")

    print("\n📊 Testing symptom statistics endpoint...")
    success = test_symptom_stats(token)
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Tests failed!")

if __name__ == "__main__":
    main()