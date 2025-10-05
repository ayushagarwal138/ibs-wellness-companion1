#!/usr/bin/env python3
"""
Detailed ML Endpoints Test Script
Tests ML prediction endpoints with detailed error reporting
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

async def register_and_login():
    """Register a test user and get authentication token"""
    async with aiohttp.ClientSession() as session:
        # Register user
        register_data = {
            "email": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
            "password": "TestPassword123!",
            "confirm_password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        async with session.post(f"{BASE_URL}/api/v1/auth/register", json=register_data) as response:
            if response.status != 201:
                print(f"Registration failed: {response.status}")
                text = await response.text()
                print(f"Response: {text}")
                return None
        
        # Login to get token
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        
        async with session.post(f"{BASE_URL}/api/v1/auth/login", json=login_data) as response:
            if response.status != 200:
                print(f"Login failed: {response.status}")
                text = await response.text()
                print(f"Response: {text}")
                return None
            
            result = await response.json()
            return result.get("access_token")

async def test_ml_endpoint(session, endpoint, token, data=None, method="GET"):
    """Test a specific ML endpoint with detailed error reporting"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        if method == "GET":
            async with session.get(f"{BASE_URL}{endpoint}", headers=headers) as response:
                status = response.status
                try:
                    result = await response.json()
                except:
                    result = await response.text()
                return status, result
        else:
            async with session.post(f"{BASE_URL}{endpoint}", headers=headers, json=data) as response:
                status = response.status
                try:
                    result = await response.json()
                except:
                    result = await response.text()
                return status, result
    except Exception as e:
        return None, str(e)

async def main():
    print("=== ML Endpoints Detailed Test ===")
    
    # Get authentication token
    token = await register_and_login()
    if not token:
        print("Failed to get authentication token")
        return
    
    print(f"✓ Authentication successful")
    
    async with aiohttp.ClientSession() as session:
        # Test endpoints that were failing
        failing_endpoints = [
            ("/api/v1/ml/recommendations", "POST", {
                "user_profile": {
                    "age": 28,
                    "ibs_type": "IBS-M",
                    "dietary_restrictions": ["lactose_intolerant"],
                    "activity_level": "moderate"
                },
                "current_symptoms": {
                    "abdominal_pain": 5.5,
                    "bloating": 7.0,
                    "gas": 4.0
                },
                "preferences": {
                    "dietary_approach": "low_fodmap",
                    "exercise_preference": "yoga",
                    "supplement_tolerance": "high"
                },
                "recommendation_types": ["dietary", "lifestyle", "supplements"]
            }),
            ("/api/v1/ml/predict/multimodal", "POST", {
                "timeframe_days": 30
            })
        ]
        
        for endpoint, method, data in failing_endpoints:
            print(f"\n--- Testing {endpoint} ({method}) ---")
            status, result = await test_ml_endpoint(session, endpoint, token, data, method)
            
            if status is None:
                print(f"❌ Connection error: {result}")
            elif status == 200:
                print(f"✓ Success (200)")
                print(f"Response: {json.dumps(result, indent=2)}")
            else:
                print(f"❌ Failed ({status})")
                print(f"Response: {json.dumps(result, indent=2) if isinstance(result, dict) else result}")
        
        # Also test working endpoints for comparison
        working_endpoints = [
            ("/api/v1/ml/predictions", "GET", None),
            ("/api/v1/ml/predict/severity", "POST", {
                "symptoms": {
                    "abdominal_pain": 7.0,
                    "bloating": 6.0,
                    "diarrhea": 5.0
                },
                "stress_level": 6.0,
                "sleep_quality": 7.0,
                "exercise_frequency": 3.0,
                "diet_adherence": 8.0
            })
        ]
        
        print(f"\n=== Working Endpoints (for comparison) ===")
        for endpoint, method, data in working_endpoints:
            print(f"\n--- Testing {endpoint} ({method}) ---")
            status, result = await test_ml_endpoint(session, endpoint, token, data, method)
            
            if status is None:
                print(f"❌ Connection error: {result}")
            elif status == 200:
                print(f"✓ Success (200)")
                print(f"Response type: {type(result)}")
            else:
                print(f"❌ Failed ({status})")
                print(f"Response: {json.dumps(result, indent=2) if isinstance(result, dict) else result}")

if __name__ == "__main__":
    asyncio.run(main())