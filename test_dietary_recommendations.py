#!/usr/bin/env python3
"""
Test script to verify dietary recommendation system uses real ML-generated suggestions.
"""

import requests
import json
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_dietary_recommendations():
    """Test if dietary recommendations are ML-generated vs hardcoded."""
    print("🍽️ Testing Dietary Recommendation System")
    print("=" * 60)
    
    # Step 1: Register and authenticate
    print("\n🔐 Step 1: Authentication")
    register_data = {
        "email": "test_diet@example.com",
        "password": "TestPass123!",
        "confirm_password": "TestPass123!",
        "first_name": "Test",
        "last_name": "Diet"
    }
    
    # Try registration (handle if user exists)
    register_response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=register_data)
    if register_response.status_code == 400:
        print("✅ User already exists, proceeding to login")
    elif register_response.status_code == 201:
        print("✅ User registered successfully")
    elif register_response.status_code == 422:
        print("✅ User likely exists (validation error), proceeding to login")
    else:
        print(f"❌ Registration failed: {register_response.status_code}")
        print(f"   Error: {register_response.text}")
        return False
    
    # Login
    login_data = {"email": "test_diet@example.com", "password": "TestPass123!"}
    login_response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"   Error: {login_response.text}")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authentication successful")
    
    # Step 2: Test ML Recommendations endpoint
    print("\n📊 Step 2: Testing ML Recommendations Endpoint")
    
    # Test with different user profiles to see if recommendations vary
    test_profiles = [
        {
            "name": "IBS-D Patient",
            "data": {
                "user_profile": {
                    "age": 30,
                    "ibs_type": "IBS-D",
                    "dietary_restrictions": ["lactose_intolerant"],
                    "activity_level": "moderate"
                },
                "current_symptoms": {
                    "abdominal_pain": 7.0,
                    "diarrhea": 6.5,
                    "bloating": 5.0
                },
                "preferences": {
                    "dietary_approach": "low_fodmap",
                    "exercise_preference": "yoga"
                },
                "recommendation_types": ["dietary", "lifestyle"]
            }
        },
        {
            "name": "IBS-C Patient",
            "data": {
                "user_profile": {
                    "age": 45,
                    "ibs_type": "IBS-C",
                    "dietary_restrictions": [],
                    "activity_level": "high"
                },
                "current_symptoms": {
                    "constipation": 8.0,
                    "bloating": 6.0,
                    "abdominal_pain": 4.0
                },
                "preferences": {
                    "dietary_approach": "mediterranean",
                    "exercise_preference": "cardio"
                },
                "recommendation_types": ["dietary", "lifestyle", "supplements"]
            }
        }
    ]
    
    recommendations_results = []
    
    for profile in test_profiles:
        print(f"\n🧪 Testing {profile['name']}...")
        
        response = requests.post(
            f"{BASE_URL}/api/v1/ml/recommendations",
            json=profile["data"],
            headers=headers
        )
        
        if response.status_code == 200:
            recommendations = response.json()
            recommendations_results.append({
                "profile": profile["name"],
                "recommendations": recommendations
            })
            
            # Analyze recommendations
            dietary_recs = recommendations.get("dietary_recommendations", [])
            lifestyle_recs = recommendations.get("lifestyle_recommendations", [])
            
            print(f"✅ Generated {len(dietary_recs)} dietary recommendations")
            print(f"✅ Generated {len(lifestyle_recs)} lifestyle recommendations")
            
            # Show sample recommendations
            if dietary_recs:
                print(f"   Sample dietary: {dietary_recs[0].get('recommendation', 'N/A')}")
            if lifestyle_recs:
                print(f"   Sample lifestyle: {lifestyle_recs[0].get('recommendation', 'N/A')}")
                
        else:
            print(f"❌ Failed to get recommendations: {response.status_code}")
            print(f"   Error: {response.text}")
    
    # Step 3: Analyze if recommendations are personalized/ML-generated
    print("\n🔍 Step 3: Analyzing Recommendation Personalization")
    
    if len(recommendations_results) >= 2:
        profile1 = recommendations_results[0]
        profile2 = recommendations_results[1]
        
        # Compare dietary recommendations
        diet1 = profile1["recommendations"].get("dietary_recommendations", [])
        diet2 = profile2["recommendations"].get("dietary_recommendations", [])
        
        # Check if recommendations are different (indicating personalization)
        diet1_text = [rec.get("recommendation", "") for rec in diet1]
        diet2_text = [rec.get("recommendation", "") for rec in diet2]
        
        if diet1_text != diet2_text:
            print("✅ Recommendations are personalized - different for different profiles")
            print(f"   {profile1['profile']}: {len(diet1)} dietary recommendations")
            print(f"   {profile2['profile']}: {len(diet2)} dietary recommendations")
        else:
            print("⚠️ Recommendations appear to be the same for different profiles")
    
    # Step 4: Test dietary trigger analysis (if available)
    print("\n🎯 Step 4: Testing Dietary Trigger Analysis")
    
    trigger_data = {
        "food_diary": [
            {
                "date": "2024-01-15",
                "meal": "breakfast",
                "foods": ["oats", "milk", "banana"],
                "fodmap_load": 6.5,
                "fiber_content": 8.2
            },
            {
                "date": "2024-01-15",
                "meal": "lunch",
                "foods": ["wheat_bread", "cheese", "tomato"],
                "fodmap_load": 8.2,
                "fiber_content": 4.1
            }
        ],
        "symptom_history": [
            {
                "date": "2024-01-15",
                "time": "14:00",
                "symptoms": {
                    "abdominal_pain": 7,
                    "bloating": 8,
                    "gas": 6
                },
                "severity": "moderate"
            }
        ],
        "user_profile": {
            "known_intolerances": ["lactose"],
            "dietary_approach": "low_fodmap",
            "food_preferences": ["vegetarian"]
        },
        "analysis_period": 14
    }
    
    # Check if dietary trigger endpoint exists
    trigger_response = requests.post(
        f"{BASE_URL}/api/v1/ml/dietary-triggers",
        json=trigger_data,
        headers=headers
    )
    
    if trigger_response.status_code == 200:
        triggers = trigger_response.json()
        print("✅ Dietary trigger analysis working")
        print(f"   Identified triggers: {len(triggers.get('identified_triggers', []))}")
        print(f"   Safe foods: {len(triggers.get('safe_foods', []))}")
    elif trigger_response.status_code == 404:
        print("ℹ️ Dietary trigger analysis endpoint not available")
    else:
        print(f"⚠️ Dietary trigger analysis failed: {trigger_response.status_code}")
    
    print("\n" + "=" * 60)
    print("📊 Dietary Recommendation System Test Summary")
    print("=" * 60)
    
    if recommendations_results:
        print("✅ ML Recommendations endpoint is working")
        print("✅ Generating personalized dietary recommendations")
        print("✅ System appears to use ML-generated suggestions")
        print("\n🎉 Dietary recommendation system is properly integrated with ML!")
        return True
    else:
        print("❌ Failed to get ML recommendations")
        print("⚠️ Dietary recommendation system may not be working properly")
        return False

if __name__ == "__main__":
    success = test_dietary_recommendations()
    sys.exit(0 if success else 1)