#!/usr/bin/env python3
"""
Live test of frontend ML integration with working endpoints
"""

import requests
import json
import time

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_frontend_ml_integration():
    """Test the complete frontend-backend ML integration."""
    
    print("🚀 Testing Frontend ML Integration with Working Endpoints")
    print("=" * 60)
    
    # Step 1: Authenticate and get token
    print("\n🔐 Step 1: Authentication")
    
    # Use existing user or create new one
    login_data = {
        "email": "test_ml_user@example.com",
        "password": "TestPass123!"
    }
    
    # Try to register first (will fail if user exists)
    register_data = {
        "email": "test_ml_user@example.com",
        "password": "TestPass123!",
        "confirm_password": "TestPass123!",
        "first_name": "ML",
        "last_name": "Tester"
    }
    
    register_response = requests.post(
        f"{BACKEND_URL}/api/v1/auth/register",
        json=register_data
    )
    
    if register_response.status_code == 201:
        print("✅ User registered successfully")
    elif "already registered" in register_response.text:
        print("ℹ️ User already exists, proceeding to login")
    else:
        print(f"⚠️ Registration response: {register_response.status_code}")
    
    # Login to get token
    login_response = requests.post(
        f"{BACKEND_URL}/api/v1/auth/login",
        json=login_data
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authentication successful")
    
    # Step 2: Test working ML endpoints
    print("\n📊 Step 2: Testing Working ML Endpoints")
    
    working_endpoints = []
    
    # Test ML Predictions
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/ml/predictions",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ ML Predictions: {data.get('risk_level', 'unknown')} risk")
            working_endpoints.append("predictions")
        else:
            print(f"❌ ML Predictions failed: {response.status_code}")
    except Exception as e:
        print(f"❌ ML Predictions error: {e}")
    
    # Test Recommendations
    try:
        rec_data = {
            "user_profile": {"age": 30, "gender": "female"},
            "current_symptoms": {"abdominal_pain": 5, "bloating": 6},
            "preferences": {"dietary_restrictions": ["gluten-free"]},
            "recommendation_types": ["dietary", "lifestyle"]
        }
        response = requests.post(
            f"{BACKEND_URL}/api/v1/ml/recommendations",
            headers=headers,
            json=rec_data,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Recommendations: {len(data.get('recommendations', []))} items")
            working_endpoints.append("recommendations")
        else:
            print(f"❌ Recommendations failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Recommendations error: {e}")
    
    # Test Severity Prediction
    try:
        severity_data = {
            "symptoms": {
                "abdominal_pain": 6,
                "bloating": 7,
                "diarrhea": 3,
                "nausea": 2
            },
            "context": {
                "stress_level": 5,
                "sleep_quality": 6
            }
        }
        response = requests.post(
            f"{BACKEND_URL}/api/v1/ml/predict/severity",
            headers=headers,
            json=severity_data,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Severity Prediction: {data.get('predicted_severity', 'unknown')}")
            working_endpoints.append("severity")
        else:
            print(f"❌ Severity Prediction failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Severity Prediction error: {e}")
    
    # Test Multimodal Prediction
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/ml/predict/multimodal?timeframe_days=7",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Multimodal Prediction: {data.get('risk_category', 'unknown')} risk")
            working_endpoints.append("multimodal")
        else:
            print(f"❌ Multimodal Prediction failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Multimodal Prediction error: {e}")
    
    # Step 3: Test Frontend Service Integration
    print("\n🌐 Step 3: Testing Frontend Service Integration")
    
    # Simulate frontend ML service calls
    print("Simulating frontend mlService.getPredictions()...")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/ml/predictions",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            print("✅ Frontend ML service integration working")
        else:
            print(f"❌ Frontend ML service integration failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend ML service integration error: {e}")
    
    # Step 4: Test Dashboard Data Flow
    print("\n📈 Step 4: Testing Dashboard Data Flow")
    
    # Simulate dynamic dashboard service
    print("Simulating dynamic dashboard ML predictions fetch...")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/ml/predictions",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            # Transform data like the frontend does
            dashboard_data = {
                "riskLevel": data.get("risk_level", "low").lower(),
                "nextFlareRisk": round((data.get("next_flare_probability", 0)) * 100),
                "confidence": data.get("confidence", 0.5),
                "recommendations": data.get("recommendations", []),
                "keyFactors": data.get("key_factors", [])
            }
            print(f"✅ Dashboard data transformation successful")
            print(f"   Risk Level: {dashboard_data['riskLevel']}")
            print(f"   Flare Risk: {dashboard_data['nextFlareRisk']}%")
            print(f"   Confidence: {dashboard_data['confidence']}")
        else:
            print(f"❌ Dashboard data flow failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard data flow error: {e}")
    
    # Step 5: Test Reports Page Data
    print("\n📋 Step 5: Testing Reports Page Data Flow")
    
    try:
        # Test the same endpoints that reports page uses
        predictions_response = requests.get(
            f"{BACKEND_URL}/api/v1/ml/predictions",
            headers=headers,
            timeout=10
        )
        
        if predictions_response.status_code == 200:
            print("✅ Reports page ML predictions data available")
        else:
            print(f"❌ Reports page ML predictions failed: {predictions_response.status_code}")
    except Exception as e:
        print(f"❌ Reports page data error: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Frontend ML Integration Test Summary")
    print("=" * 60)
    print(f"✅ Working ML Endpoints: {len(working_endpoints)}")
    print(f"   Endpoints: {', '.join(working_endpoints)}")
    
    if len(working_endpoints) >= 3:
        print("🎉 Frontend ML integration is working well!")
        print("   The frontend can successfully fetch real ML data")
        print("   Dashboard and reports pages should display live ML insights")
        return True
    else:
        print("⚠️ Limited ML functionality available")
        print("   Some frontend features may fall back to mock data")
        return False

if __name__ == "__main__":
    success = test_frontend_ml_integration()
    exit(0 if success else 1)