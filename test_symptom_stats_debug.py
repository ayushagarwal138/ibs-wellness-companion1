#!/usr/bin/env python3
"""
Test script to debug symptom stats API response
"""

import requests
import json

def test_symptom_stats():
    base_url = "http://localhost:8000"
    test_email = "api_test@example.com"
    test_password = "testpass123"
    
    print("🔍 Testing symptom stats API response...")
    print(f"🔑 Using test user: {test_email}")
    
    try:
        # Try to login (user should already exist)
        login_data = {
            "email": test_email,
            "password": test_password
        }
        
        login_response = requests.post(f"{base_url}/api/v1/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            print(f"✅ Login successful, token: {access_token[:20]}...")
            
            # Now test the symptom stats endpoint
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            stats_response = requests.get(
                f"{base_url}/api/v1/symptom-logs/stats/summary?days=30",
                headers=headers
            )
            
            print(f"📊 Symptom stats response status: {stats_response.status_code}")
            
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                print(f"📈 Response data keys: {list(stats_data.keys())}")
                
                if 'data' in stats_data:
                    data = stats_data['data']
                    print(f"📊 Data keys: {list(data.keys())}")
                    
                    if 'weekly_trends' in data:
                        print(f"✅ weekly_trends found!")
                        print(f"📈 weekly_trends: {json.dumps(data['weekly_trends'], indent=2)}")
                    else:
                        print(f"❌ weekly_trends NOT found in data")
                        print(f"📊 Full data: {json.dumps(data, indent=2)}")
                else:
                    print(f"❌ No 'data' key in response")
                    print(f"📊 Full response: {json.dumps(stats_data, indent=2)}")
            else:
                print(f"❌ Stats request failed: {stats_response.status_code}")
                print(f"📊 Error response: {stats_response.text}")
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"📊 Login response: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_symptom_stats()