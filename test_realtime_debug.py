#!/usr/bin/env python3
"""
Debug script for real-time predictions endpoint
"""

import requests
import json

# Configuration
BACKEND_URL = "http://localhost:8000"

def test_realtime_endpoint():
    """Test the real-time predictions endpoint with debug info."""
    
    # First, register and get token
    print("🔐 Getting authentication token...")
    
    # Try to register user (skip if already exists)
    register_data = {
        "email": "test_realtime@example.com",
        "password": "TestPass123!",
        "confirm_password": "TestPass123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    register_response = requests.post(
        f"{BACKEND_URL}/api/v1/auth/register",
        json=register_data
    )
    
    if register_response.status_code == 201:
        print("✅ User registered successfully")
    elif register_response.status_code == 400 and "already registered" in register_response.text:
        print("ℹ️ User already exists, proceeding to login")
    else:
        print(f"❌ Registration failed: {register_response.status_code}")
        print(f"Response: {register_response.text}")
        return
    
    # Login to get token
    login_data = {
        "email": "test_realtime@example.com",
        "password": "TestPass123!"
    }
    
    login_response = requests.post(
        f"{BACKEND_URL}/api/v1/auth/login",
        json=login_data
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Authentication successful")
    
    # Test real-time predictions
    print("\n📊 Testing real-time predictions...")
    
    realtime_data = {
        "symptoms": {
            "abdominal_pain": 3,
            "bloating": 2,
            "diarrhea": 1
        },
        "include_trends": True,
        "include_recommendations": True,
        "stream_updates": False
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/ml/realtime/predict/enhanced",
            headers=headers,
            json=realtime_data,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Real-time predictions successful!")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Real-time predictions failed: {response.status_code}")
            print(f"Error response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Request failed with exception: {e}")

if __name__ == "__main__":
    test_realtime_endpoint()