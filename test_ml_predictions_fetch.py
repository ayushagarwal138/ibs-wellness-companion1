#!/usr/bin/env python3
"""
Test script to verify ML predictions fetch process completion
This simulates the same API calls made by the DataVisualization component
"""

import requests
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"


def login():
    """Login and get authentication token"""
    login_data = {
        "email": "api_test@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None


def test_ml_predictions_fetch(token):
    """Test ML predictions fetch process that DataVisualization performs"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔍 Testing ML Predictions Fetch Process")
    print("=" * 50)
    
    # Track results
    results = {
        "ml_predictions": {"status": "pending", "duration": 0, "error": None},
        "stress_correlation": {"status": "pending", "duration": 0, 
                               "error": None},
        "flareup_predictions": {"status": "pending", "duration": 0, 
                                "error": None},
        "pattern_insights": {"status": "pending", "duration": 0, 
                             "error": None}
    }
    
    # 1. Test ML Predictions (getPredictions)
    print("\n1. Testing ML Predictions API...")
    start_time = time.time()
    try:
        response = requests.get(f"{BASE_URL}/api/v1/ml/predictions", 
                                headers=headers)
        duration = time.time() - start_time
        results["ml_predictions"]["duration"] = duration
        
        if response.status_code == 200:
            data = response.json()
            results["ml_predictions"]["status"] = "success"
            print(f"   ✅ Success ({duration:.2f}s)")
            print(f"   📊 Risk Level: {data.get('risk_level', 'N/A')}")
            print(f"   📈 Flare Probability: "
                  f"{data.get('next_flare_probability', 'N/A')}")
        else:
            results["ml_predictions"]["status"] = "failed"
            error_msg = f"HTTP {response.status_code}: {response.text}"
            results["ml_predictions"]["error"] = error_msg
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        duration = time.time() - start_time
        results["ml_predictions"]["duration"] = duration
        results["ml_predictions"]["status"] = "error"
        results["ml_predictions"]["error"] = str(e)
        print(f"   💥 Error: {e}")
    
    # 2. Test Stress-Symptom Correlation
    print("\n2. Testing Stress-Symptom Correlation API...")
    start_time = time.time()
    try:
        payload = {
            "stress_levels": {
                'day1': 7, 'day2': 8, 'day3': 6, 'day4': 9,
                'day5': 5, 'day6': 7, 'day7': 8
            },
            "symptoms": {
                'abdominal_pain': 6, 'bloating': 7, 'diarrhea': 5,
                'constipation': 8, 'nausea': 4, 'fatigue': 6, 
                'cramping': 7
            },
            "timeframe_days": 30
        }
        
        correlation_url = (f"{BASE_URL}/api/v1/ml/predict/"
                           "stress-symptom-correlation")
        response = requests.post(correlation_url, headers=headers,
                                 json=payload)
        duration = time.time() - start_time
        results["stress_correlation"]["duration"] = duration
        
        if response.status_code == 200:
            data = response.json()
            results["stress_correlation"]["status"] = "success"
            print(f"   ✅ Success ({duration:.2f}s)")
            print(f"   🔗 Correlation Score: "
                  f"{data.get('correlation_score', 'N/A')}")
            triggers_count = len(data.get('stress_triggers', []))
            print(f"   🎯 Stress Triggers: {triggers_count} found")
        else:
            results["stress_correlation"]["status"] = "failed"
            error_msg = f"HTTP {response.status_code}: {response.text}"
            results["stress_correlation"]["error"] = error_msg
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        duration = time.time() - start_time
        results["stress_correlation"]["duration"] = duration
        results["stress_correlation"]["status"] = "error"
        results["stress_correlation"]["error"] = str(e)
        print(f"   💥 Error: {e}")
    
    # 3. Test Flareup Predictions
    print("\n3. Testing Flareup Predictions API...")
    start_time = time.time()
    try:
        payload = {
            "recent_symptoms": [
                {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "symptoms": {"abdominal_pain": 6, "bloating": 7,
                                 "diarrhea": 5},
                    "triggers": ["stress", "dairy"]
                }
            ],
            "lifestyle_factors": {
                "stress_level": 7,
                "sleep_quality": 6,
                "exercise_frequency": 3,
                "diet_adherence": 8
            },
            "prediction_horizon": 30
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/ml/predict/flareup",
                                 headers=headers, json=payload)
        duration = time.time() - start_time
        results["flareup_predictions"]["duration"] = duration
        
        if response.status_code == 200:
            data = response.json()
            results["flareup_predictions"]["status"] = "success"
            print(f"   ✅ Success ({duration:.2f}s)")
            print(f"   📊 Risk Score: {data.get('risk_score', 'N/A')}")
            horizon_days = data.get('prediction_horizon_days', 'N/A')
            print(f"   📅 Prediction Days: {horizon_days}")
        else:
            results["flareup_predictions"]["status"] = "failed"
            error_msg = f"HTTP {response.status_code}: {response.text}"
            results["flareup_predictions"]["error"] = error_msg
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        duration = time.time() - start_time
        results["flareup_predictions"]["duration"] = duration
        results["flareup_predictions"]["status"] = "error"
        results["flareup_predictions"]["error"] = str(e)
        print(f"   💥 Error: {e}")
    
    # 4. Test Pattern Insights (if available)
    print("\n4. Testing Pattern Insights API...")
    start_time = time.time()
    try:
        insights_url = f"{BASE_URL}/api/v1/analytics/pattern-insights?days=30"
        response = requests.get(insights_url, headers=headers)
        duration = time.time() - start_time
        results["pattern_insights"]["duration"] = duration
        
        if response.status_code == 200:
            data = response.json()
            results["pattern_insights"]["status"] = "success"
            print(f"   ✅ Success ({duration:.2f}s)")
            insights_count = len(data.get('insights', []))
            print(f"   🔍 Insights Found: {insights_count}")
        else:
            results["pattern_insights"]["status"] = "failed"
            error_msg = f"HTTP {response.status_code}: {response.text}"
            results["pattern_insights"]["error"] = error_msg
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        duration = time.time() - start_time
        results["pattern_insights"]["duration"] = duration
        results["pattern_insights"]["status"] = "error"
        results["pattern_insights"]["error"] = str(e)
        print(f"   💥 Error: {e}")
    
    return results


def print_summary(results):
    """Print a summary of the test results"""
    print("\n" + "=" * 50)
    print("📋 ML PREDICTIONS FETCH SUMMARY")
    print("=" * 50)
    
    total_duration = sum(result["duration"] for result in results.values())
    success_count = sum(1 for result in results.values()
                        if result["status"] == "success")
    total_calls = len(results)
    
    print(f"⏱️  Total Duration: {total_duration:.2f}s")
    print(f"✅ Successful Calls: {success_count}/{total_calls}")
    print(f"📊 Success Rate: {(success_count/total_calls)*100:.1f}%")
    
    print("\n📝 Detailed Results:")
    for service, result in results.items():
        if result["status"] == "success":
            status_icon = "✅"
        elif result["status"] == "failed":
            status_icon = "❌"
        else:
            status_icon = "💥"
        service_name = service.replace('_', ' ').title()
        duration = result['duration']
        status = result['status']
        print(f"   {status_icon} {service_name}: {status} ({duration:.2f}s)")
        if result["error"]:
            print(f"      Error: {result['error']}")
    
    # Determine overall status
    if success_count == total_calls:
        print("\n🎉 RESULT: All ML predictions fetch operations "
              "completed successfully!")
        print("   The DataVisualization component should be working "
              "properly.")
    elif success_count > 0:
        print(f"\n⚠️  RESULT: Partial success - {success_count}/"
              f"{total_calls} services working.")
        print("   Some ML features may not be available in the UI.")
    else:
        print("\n🚨 RESULT: All ML predictions fetch operations failed!")
        print("   The DataVisualization component will likely show errors "
              "or fallback data.")


def main():
    print("🚀 Starting ML Predictions Fetch Verification")
    print(f"🕐 Timestamp: {datetime.now().isoformat()}")
    
    # Login first
    token = login()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    print("✅ Authentication successful")
    
    # Test ML predictions fetch
    results = test_ml_predictions_fetch(token)
    
    # Print summary
    print_summary(results)

if __name__ == "__main__":
    main()