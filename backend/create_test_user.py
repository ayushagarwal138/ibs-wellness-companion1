#!/usr/bin/env python3
"""
Script to create a test user for mood functionality testing.
"""

import requests

BASE_URL = "http://localhost:8000/api/v1"


def create_or_login_test_user():
    """Create a test user or login if already exists."""
    
    # Test user data
    user_data = {
        "email": "mood_test@example.com",
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!",
        "first_name": "Mood",
        "last_name": "Tester"
    }
    
    # Try to register the user first
    try:
        register_response = requests.post(
            f"{BASE_URL}/auth/register", json=user_data
        )
        if register_response.status_code == 201:
            print("✓ Test user created successfully")
        elif register_response.status_code == 400:
            print("ℹ Test user already exists, proceeding with login")
        else:
            status = register_response.status_code
            text = register_response.text
            print(f"Registration failed: {status} - {text}")
            return None
    except Exception as e:
        print(f"Registration error: {e}")
        return None
    
    # Login to get access token
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    try:
        login_response = requests.post(
            f"{BASE_URL}/auth/login", json=login_data
        )
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data["access_token"]
            print(f"Access token: {access_token}")
            print(f"Token: {access_token[:20]}...")
            return access_token
        else:
            status = login_response.status_code
            text = login_response.text
            print(f"Login failed: {status} - {text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None


if __name__ == "__main__":
    create_or_login_test_user()