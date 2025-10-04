#!/usr/bin/env python3
"""
Test script to diagnose the symptom statistics authentication issue.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_authentication():
    """Test user authentication and get token."""
    print("🔐 Testing authentication...")
    
    # Try to login with test user
    login_data = {
        "email": "test@example.com",
        "password": "TestPassword123!"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_id = data.get("user", {}).get("id")
            print(f"✅ Authentication successful!")
            print(f"   User ID: {user_id}")
            print(f"   Token: {token[:20]}..." if token else "   No token received")
            return token
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def test_symptom_stats_endpoint(token):
    """Test the symptom stats endpoint with authentication."""
    print("\n📊 Testing symptom stats endpoint...")
    
    if not token:
        print("❌ No token available for testing")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test the exact endpoint the frontend calls
        response = requests.get(
            f"{BASE_URL}/api/v1/symptom-logs/stats/summary?days=30",
            headers=headers
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Symptom stats endpoint working!")
            print(f"   Response: {json.dumps(data, indent=2)}")
            return True
        elif response.status_code == 403:
            print("❌ Authentication failed (403 Forbidden)")
            print(f"   Response: {response.text}")
            return False
        else:
            print(f"❌ Endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def test_without_auth():
    """Test the endpoint without authentication to confirm it requires auth."""
    print("\n🚫 Testing symptom stats endpoint without authentication...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/symptom-logs/stats/summary?days=30")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 403:
            print("✅ Endpoint correctly requires authentication")
            return True
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def main():
    print("🧪 Symptom Statistics Authentication Diagnostic")
    print("=" * 50)
    
    # Test 1: Authentication
    token = test_authentication()
    
    # Test 2: Endpoint without auth
    test_without_auth()
    
    # Test 3: Endpoint with auth
    if token:
        success = test_symptom_stats_endpoint(token)
        
        if success:
            print("\n✅ All tests passed! The backend is working correctly.")
            print("💡 The issue is likely in the frontend authentication state.")
            print("   Check if the user is properly logged in and has a valid token in localStorage.")
        else:
            print("\n❌ Backend authentication issue detected.")
    else:
        print("\n❌ Cannot test authenticated endpoint without valid token.")
        print("💡 Check if the test user exists and has the correct password.")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()