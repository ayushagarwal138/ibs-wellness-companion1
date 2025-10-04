#!/usr/bin/env python3
"""
Test script to check authentication and API access
"""
import requests
import json


def test_authentication_and_api():
    """Test authentication flow and API access"""
    base_url = "http://localhost:8000"
    
    print("Testing Authentication and API Access")
    print("=" * 50)
    
    # Test 1: Check if we can create a test user and get a token
    print("\n1. Testing user registration/login:")
    
    # Try to register a test user
    test_user = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        # Try registration first
        response = requests.post(
            f"{base_url}/api/v1/auth/register",
            json=test_user,
            timeout=10
        )
        print(f"   Registration status: {response.status_code}")
        
        if response.status_code == 409:  # User already exists
            print("   User already exists, trying login...")
        elif response.status_code == 201:
            print("   User registered successfully")
        
    except Exception as e:
        print(f"   Registration error: {e}")
    
    # Try to login
    try:
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json=login_data,  # Use JSON data
            timeout=10
        )
        
        print(f"   Login status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            if access_token:
                print(f"   Got access token: {access_token[:20]}...")
            else:
                print("   No token received")
            
            if access_token:
                # Test 2: Use the token to access the diet stats API
                print("\n2. Testing diet stats API with authentication:")
                
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                response = requests.get(
                    f"{base_url}/api/v1/diet/stats/diet?days=30",
                    headers=headers,
                    timeout=10
                )
                
                print(f"   Diet stats API status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   Response data: {json.dumps(data, indent=2)}")
                else:
                    print(f"   Error response: {response.text}")
                
                # Test 3: Check if there's any diet data
                print("\n3. Testing diet logs to see if there's data:")
                
                response = requests.get(
                    f"{base_url}/api/v1/diet/logs",
                    headers=headers,
                    timeout=10
                )
                
                print(f"   Diet logs API status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    print(f"   Number of diet log entries: {len(items)}")
                    if len(items) == 0:
                        print("   No diet log entries found - this explains why stats show 0")
                else:
                    print(f"   Error response: {response.text}")
                    
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            print(f"   Login failed: {error_data}")
            
    except Exception as e:
        print(f"   Login error: {e}")


def test_sample_data_creation():
    """Create some sample data for testing"""
    base_url = "http://localhost:8000"
    
    print("\n4. Creating sample diet data for testing:")
    
    # First login to get token
    login_data = {
        "email": "test@example.com",
        "password": "TestPassword123!"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            
            if access_token:
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                # Create sample diet log entries (using recent dates)
                from datetime import datetime, timedelta
                today = datetime.utcnow()
                yesterday = today - timedelta(days=1)
                
                sample_logs = [
                    {
                        "foods": ["Apple", "Banana"],
                        "meal_type": "breakfast",
                        "consumed_at": yesterday.strftime(
                            "%Y-%m-%dT08:00:00Z"
                        ),
                        "calories": 150,
                        "notes": "Morning fruit"
                    },
                    {
                        "foods": ["Chicken Salad", "Bread"],
                        "meal_type": "lunch", 
                        "consumed_at": yesterday.strftime(
                            "%Y-%m-%dT12:00:00Z"
                        ),
                        "calories": 400,
                        "notes": "Healthy lunch"
                    },
                    {
                        "foods": ["Pasta", "Tomato Sauce"],
                        "meal_type": "dinner",
                        "consumed_at": yesterday.strftime(
                            "%Y-%m-%dT19:00:00Z"
                        ), 
                        "calories": 500,
                        "notes": "Dinner meal"
                    }
                ]
                
                for i, log_data in enumerate(sample_logs):
                    try:
                        response = requests.post(
                            f"{base_url}/api/v1/diet/logs",
                            json=log_data,
                            headers=headers,
                            timeout=10
                        )
                        print(f"   Sample log {i+1} creation status: {response.status_code}")
                        if response.status_code != 201:
                            print(f"   Error: {response.text}")
                    except Exception as e:
                        print(f"   Error creating sample log {i+1}: {e}")
                        
                print("   Sample data creation completed")
                
    except Exception as e:
        print(f"   Error in sample data creation: {e}")


if __name__ == "__main__":
    test_authentication_and_api()
    test_sample_data_creation()
    
    print("\n" + "=" * 50)
    print("Test completed. Check the results above.")