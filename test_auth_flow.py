#!/usr/bin/env python3
"""
Test authentication flow and create test user if needed.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"

def test_auth_flow():
    """Test the complete authentication flow."""
    print("🔐 Testing Authentication Flow")
    print("=" * 50)
    
    # Step 1: Try to register a test user
    print("\n1. Attempting to register test user...")
    register_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "full_name": "Test User",
        "confirm_password": TEST_PASSWORD
    }
    
    try:
        register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if register_response.status_code == 201:
            print("✅ Test user registered successfully")
        elif register_response.status_code == 400:
            print("ℹ️  Test user already exists (expected)")
        else:
            print(f"⚠️  Registration response: {register_response.status_code} - {register_response.text}")
    except Exception as e:
        print(f"❌ Registration error: {e}")
    
    # Step 2: Try to login
    print("\n2. Attempting to login...")
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            print(f"✅ Login successful! Token: {access_token[:20]}...")
            
            # Step 3: Test ML endpoints with authentication
            print("\n3. Testing ML endpoints with authentication...")
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Test model info endpoint
            try:
                ml_response = requests.get(f"{BASE_URL}/ml/models/info", headers=headers)
                print(f"   Model Info: {ml_response.status_code}")
                if ml_response.status_code == 200:
                    print("   ✅ ML model info endpoint working!")
                else:
                    print(f"   ❌ ML model info failed: {ml_response.text}")
            except Exception as e:
                print(f"   ❌ ML model info error: {e}")
            
            # Test predictions endpoint
            try:
                pred_response = requests.get(f"{BASE_URL}/ml/predictions", headers=headers)
                print(f"   Predictions: {pred_response.status_code}")
                if pred_response.status_code == 200:
                    print("   ✅ ML predictions endpoint working!")
                else:
                    print(f"   ❌ ML predictions failed: {pred_response.text}")
            except Exception as e:
                print(f"   ❌ ML predictions error: {e}")
            
            # Test realtime predictions endpoint
            try:
                rt_response = requests.get(f"{BASE_URL}/ml/realtime-predictions", headers=headers)
                print(f"   Realtime Predictions: {rt_response.status_code}")
                if rt_response.status_code == 200:
                    print("   ✅ ML realtime predictions endpoint working!")
                else:
                    print(f"   ❌ ML realtime predictions failed: {rt_response.text}")
            except Exception as e:
                print(f"   ❌ ML realtime predictions error: {e}")
                
        else:
            print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_auth_flow()
    sys.exit(0 if success else 1)
