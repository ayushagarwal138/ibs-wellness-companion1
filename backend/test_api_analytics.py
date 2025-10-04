#!/usr/bin/env python3
"""
Test script to verify analytics API endpoint with authentication
"""
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta


async def test_analytics_api():
    """Test the analytics API endpoint with proper authentication"""
    
    # Test user credentials
    email = "api_test@example.com"
    password = "testpass123"
    
    base_url = "http://localhost:8000/api/v1"
    
    async with aiohttp.ClientSession() as session:
        # 1. Login to get access token
        print("1. Logging in...")
        login_data = {
            "email": email,
            "password": password
        }
        
        async with session.post(
            f"{base_url}/auth/login",
            json=login_data
        ) as response:
            if response.status != 200:
                print(f"Login failed: {response.status}")
                text = await response.text()
                print(f"Response: {text}")
                return
            
            login_result = await response.json()
            access_token = login_result.get("access_token")
            print(f"Login successful! Token: {access_token[:20]}...")
        
        # 2. Test analytics endpoint
        print("\n2. Testing analytics endpoint...")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Calculate date range (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        async with session.get(
            f"{base_url}/analytics/user-analytics",
            headers=headers,
            params={"days": 30}
        ) as response:
            print(f"Analytics response status: {response.status}")
            
            if response.status == 200:
                analytics_data = await response.json()
                print("Analytics data:")
                print(json.dumps(analytics_data, indent=2))
            else:
                text = await response.text()
                print(f"Error response: {text}")
        
        # 3. Test symptom logs endpoint
        print("\n3. Testing symptom logs endpoint...")
        async with session.get(
            f"{base_url}/symptom-logs/",
            headers=headers,
            params={"days": 30}
        ) as response:
            print(f"Symptom logs response status: {response.status}")
            
            if response.status == 200:
                logs_response = await response.json()
                logs_data = logs_response.get("data", [])
                print(f"Found {len(logs_data)} symptom logs")
                if logs_data and len(logs_data) > 0:
                    print("Sample log:")
                    print(json.dumps(logs_data[0], indent=2, default=str))
                else:
                    print("No symptom logs found for this user")
            else:
                text = await response.text()
                print(f"Error response: {text}")


if __name__ == "__main__":
    asyncio.run(test_analytics_api())