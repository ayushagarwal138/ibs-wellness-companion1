#!/usr/bin/env python3
"""
Test script to verify mood data functionality in the IBS Wellness Companion.
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any

BASE_URL = "http://localhost:8000/api/v1"

# Test user credentials
EMAIL = "mood_test@example.com"
PASSWORD = "TestPassword123!"


def login():
    """Login and return access token."""
    login_data = {
        "email": EMAIL,
        "password": PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(
            f"Login failed: {response.status_code} - {response.text}"
        )


def create_diet_log(token: str, foods: List[str], meal_type: str,
                    mood_before: int, mood_after: int) -> Dict[str, Any]:
    """Create a diet log with mood data."""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create food items data
    food_items = []
    for food_name in foods:
        food_items.append({
            "food_name": food_name,
            "quantity": 1.0,
            "unit": "serving"
        })
    
    diet_log_data = {
        "meal_type": meal_type,
        "consumed_at": (datetime.now() - timedelta(days=1)).isoformat(),
        "mood_before": mood_before,
        "mood_after": mood_after,
        "food_items": food_items
    }
    
    response = requests.post(
        f"{BASE_URL}/diet/logs", json=diet_log_data, headers=headers
    )
    return response


def get_diet_stats(token: str) -> Dict[str, Any]:
    """Get diet statistics including mood correlation."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/diet/stats", headers=headers)
    return response


def main():
    print("Testing mood data functionality...")
    
    try:
        # Login
        token = login()
        print("✓ Login successful")
        
        print("\nCreating diet logs with mood data...")
        
        # Create diet logs with different mood patterns
        test_meals = [
            (["Apple", "Banana"], "breakfast", 6, 8),
            (["Chicken", "Rice"], "lunch", 5, 7),
            (["Salad"], "dinner", 7, 9),
            (["Pasta"], "lunch", 4, 6),
            (["Fish", "Vegetables"], "dinner", 8, 9),
        ]
        
        for i, (foods, meal_type, mood_before, mood_after) in enumerate(
            test_meals, 1
        ):
            response = create_diet_log(
                token, foods, meal_type, mood_before, mood_after
            )
            if response.status_code == 201:
                mood_change = f"{mood_before}→{mood_after}"
                print(f"✓ Created diet log {i}: {foods} (mood: {mood_change})")
            else:
                error_msg = f"{response.status_code} - {response.text}"
                print(f"✗ Failed to create diet log {i}: {error_msg}")
        
        print("\nFetching diet statistics...")
        stats_response = get_diet_stats(token)
        
        if stats_response.status_code == 200:
            print("✓ Diet stats retrieved successfully")
            stats = stats_response.json()
            print(f"Total meals logged: {stats.get('total_meals', 0)}")
            mood_correlation = stats.get('mood_correlation', {})
            print(f"Mood correlation: {mood_correlation}")
            
            if mood_correlation:
                print("✓ Mood correlation data found!")
            else:
                print("✗ Mood correlation is empty")
        else:
            error_msg = f"{stats_response.status_code} - {stats_response.text}"
            print(f"✗ Failed to get stats: {error_msg}")
            
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    main()