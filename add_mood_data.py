#!/usr/bin/env python3
"""
Script to add diet logs with mood data for testing mood correlation
"""
import requests
import json
from datetime import datetime, timedelta

def add_mood_data():
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
        
        # Create diet logs with mood data
        today = datetime.utcnow()
        
        mood_logs = [
            {
                "foods": ["Oatmeal", "Berries"],
                "meal_type": "breakfast",
                "consumed_at": (today - timedelta(days=1)).strftime("%Y-%m-%dT08:00:00Z"),
                "calories": 200,
                "mood_before": 6,
                "mood_after": 8,
                "notes": "Felt better after breakfast"
            },
            {
                "foods": ["Grilled Chicken", "Rice"],
                "meal_type": "lunch",
                "consumed_at": (today - timedelta(days=1)).strftime("%Y-%m-%dT12:30:00Z"),
                "calories": 350,
                "mood_before": 5,
                "mood_after": 7,
                "notes": "Good energy after lunch"
            },
            {
                "foods": ["Salmon", "Vegetables"],
                "meal_type": "dinner",
                "consumed_at": (today - timedelta(days=1)).strftime("%Y-%m-%dT19:00:00Z"),
                "calories": 400,
                "mood_before": 4,
                "mood_after": 6,
                "notes": "Relaxing dinner"
            },
            {
                "foods": ["Yogurt", "Granola"],
                "meal_type": "breakfast",
                "consumed_at": today.strftime("%Y-%m-%dT08:15:00Z"),
                "calories": 180,
                "mood_before": 7,
                "mood_after": 8,
                "notes": "Great start to the day"
            },
            {
                "foods": ["Turkey Sandwich"],
                "meal_type": "lunch",
                "consumed_at": today.strftime("%Y-%m-%dT12:45:00Z"),
                "calories": 320,
                "mood_before": 6,
                "mood_after": 7,
                "notes": "Satisfying lunch"
            }
        ]
        
        print("Adding diet logs with mood data...")
        for i, log_data in enumerate(mood_logs):
            try:
                response = requests.post(
                    f"{base_url}/api/v1/diet/logs",
                    json=log_data,
                    headers=headers
                )
                print(f"Log {i+1}: Status {response.status_code}")
                if response.status_code != 201:
                    print(f"  Error: {response.text}")
            except Exception as e:
                print(f"  Error creating log {i+1}: {e}")
        
        print("\nChecking updated diet stats...")
        response = requests.get(f"{base_url}/api/v1/diet/stats/diet", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("Updated mood correlation:")
            print(json.dumps(data.get("mood_correlation", {}), indent=2))
        else:
            print(f"Error getting stats: {response.text}")

if __name__ == "__main__":
    add_mood_data()