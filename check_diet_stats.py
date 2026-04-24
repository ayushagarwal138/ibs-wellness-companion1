#!/usr/bin/env python3
"""
Quick script to check diet stats API response
"""
import requests
import json

def check_diet_stats():
    base_url = "http://localhost:8000"
    
    # Login to get token
    login_data = {
        "email": "test@example.com",
        "password": "TestPassword123!"
    }
    
    response = requests.post(f"{base_url}/api/v1/auth/login", json=login_data)
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Check diet stats
        print("Diet Stats API Response:")
        response = requests.get(f"{base_url}/api/v1/diet/stats/diet", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: {response.text}")
            
        # Check a single diet log to see the structure
        print("\nSample Diet Log:")
        response = requests.get(f"{base_url}/api/v1/diet/logs?limit=1", headers=headers)
        if response.status_code == 200:
            logs = response.json()
            if logs:
                print(json.dumps(logs[0], indent=2))
            else:
                print("No logs found")
        else:
            print(f"Error: {response.text}")

if __name__ == "__main__":
    check_diet_stats()