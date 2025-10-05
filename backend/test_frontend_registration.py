#!/usr/bin/env python3
"""
Test script to simulate frontend registration request
"""

import requests
import json
from datetime import datetime

def test_registration():
    """Test registration with the exact same format as frontend"""
    
    # API endpoint
    url = "http://localhost:8000/api/v1/auth/register"
    
    # Test data (similar to what frontend would send)
    test_data = {
        "email": f"frontend_test_{int(datetime.now().timestamp())}@example.com",
        "password": "TestPass123!",
        "confirm_password": "TestPass123!",
        "first_name": "Frontend",
        "last_name": "Test"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Testing registration with data: {json.dumps(test_data, indent=2)}")
    print(f"URL: {url}")
    
    try:
        response = requests.post(url, json=test_data, headers=headers, timeout=10)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"Response Body: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Response Body (raw): {response.text}")
            
        if response.status_code == 201:
            print("✅ Registration successful!")
        else:
            print(f"❌ Registration failed with status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is the backend server running?")
    except requests.exceptions.Timeout:
        print("❌ Request timeout")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_registration()