#!/usr/bin/env python3
"""
Comprehensive Error Handling Test for ML Models

This script tests the enhanced error handling and logging system
implemented in the ML model service.
"""

import requests
import json
import sys
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER = {
    "email": "test@example.com",
    "password": "TestPassword123!"
}

def login_and_get_token() -> str:
    """Login and get authentication token."""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=TEST_USER,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def test_invalid_inputs(token: str) -> Dict[str, Any]:
    """Test ML endpoints with invalid inputs."""
    headers = {"Authorization": f"Bearer {token}"}
    results = {}
    
    # Test 1: Empty data
    print("\n=== Testing Empty Data ===")
    try:
        response = requests.post(
            f"{BASE_URL}/ml/predict/severity",
            json={},
            headers=headers
        )
        results["empty_data"] = {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text
        }
        print(f"Empty data test: {response.status_code}")
    except Exception as e:
        results["empty_data"] = {"error": str(e)}
        print(f"Empty data test error: {e}")
    
    # Test 2: Invalid data types
    print("\n=== Testing Invalid Data Types ===")
    try:
        response = requests.post(
            f"{BASE_URL}/ml/predict/severity",
            json={
                "symptoms": "not_a_list",  # Should be a list
                "invalid_field": 12345
            },
            headers=headers
        )
        results["invalid_types"] = {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text
        }
        print(f"Invalid types test: {response.status_code}")
    except Exception as e:
        results["invalid_types"] = {"error": str(e)}
        print(f"Invalid types test error: {e}")
    
    # Test 3: Missing required fields
    print("\n=== Testing Missing Required Fields ===")
    try:
        response = requests.post(
            f"{BASE_URL}/ml/predict/flareup",
            json={
                "incomplete_data": True
                # Missing recent_symptoms and lifestyle_factors
            },
            headers=headers
        )
        results["missing_fields"] = {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text
        }
        print(f"Missing fields test: {response.status_code}")
    except Exception as e:
        results["missing_fields"] = {"error": str(e)}
        print(f"Missing fields test error: {e}")
    
    # Test 4: Extremely large data
    print("\n=== Testing Large Data ===")
    try:
        large_symptoms = ["symptom_" + str(i) for i in range(1000)]
        response = requests.post(
            f"{BASE_URL}/ml/predict/severity",
            json={
                "symptoms": large_symptoms,
                "severity_level": 5
            },
            headers=headers
        )
        results["large_data"] = {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text
        }
        print(f"Large data test: {response.status_code}")
    except Exception as e:
        results["large_data"] = {"error": str(e)}
        print(f"Large data test error: {e}")
    
    # Test 5: Invalid recommendation request
    print("\n=== Testing Invalid Recommendation Request ===")
    try:
        response = requests.post(
            f"{BASE_URL}/ml/recommendations",
            json={
                "user_profile": None,  # Invalid null value
                "current_symptoms": [],
                "recommendation_types": ["invalid_type"]
            },
            headers=headers
        )
        results["invalid_recommendations"] = {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text
        }
        print(f"Invalid recommendations test: {response.status_code}")
    except Exception as e:
        results["invalid_recommendations"] = {"error": str(e)}
        print(f"Invalid recommendations test error: {e}")
    
    return results

def test_edge_cases(token: str) -> Dict[str, Any]:
    """Test edge cases and boundary conditions."""
    headers = {"Authorization": f"Bearer {token}"}
    results = {}
    
    # Test 1: Extreme values
    print("\n=== Testing Extreme Values ===")
    try:
        response = requests.post(
            f"{BASE_URL}/ml/predict/severity",
            json={
                "symptoms": ["extreme_pain", "severe_bloating"],
                "severity_level": 999999,  # Extreme value
                "pain_scale": -100,  # Negative value
                "duration": float('inf')  # Infinity
            },
            headers=headers
        )
        results["extreme_values"] = {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text
        }
        print(f"Extreme values test: {response.status_code}")
    except Exception as e:
        results["extreme_values"] = {"error": str(e)}
        print(f"Extreme values test error: {e}")
    
    # Test 2: Unicode and special characters
    print("\n=== Testing Unicode Characters ===")
    try:
        response = requests.post(
            f"{BASE_URL}/ml/predict/severity",
            json={
                "symptoms": ["腹痛", "🤢", "émotions", "Ñoño"],
                "notes": "Special chars: @#$%^&*()[]{}|\\:;\"'<>,.?/~`"
            },
            headers=headers
        )
        results["unicode_chars"] = {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text
        }
        print(f"Unicode characters test: {response.status_code}")
    except Exception as e:
        results["unicode_chars"] = {"error": str(e)}
        print(f"Unicode characters test error: {e}")
    
    # Test 3: Very long strings
    print("\n=== Testing Long Strings ===")
    try:
        long_string = "x" * 10000
        response = requests.post(
            f"{BASE_URL}/ml/predict/severity",
            json={
                "symptoms": [long_string],
                "notes": long_string
            },
            headers=headers
        )
        results["long_strings"] = {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text
        }
        print(f"Long strings test: {response.status_code}")
    except Exception as e:
        results["long_strings"] = {"error": str(e)}
        print(f"Long strings test error: {e}")
    
    return results

def test_model_health(token: str) -> Dict[str, Any]:
    """Test model health and status endpoints."""
    headers = {"Authorization": f"Bearer {token}"}
    results = {}
    
    print("\n=== Testing Model Health ===")
    try:
        response = requests.get(
            f"{BASE_URL}/ml/models/info",
            headers=headers
        )
        results["model_info"] = {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text
        }
        print(f"Model info test: {response.status_code}")
        
        if response.status_code == 200:
            model_info = response.json()
            print(f"Models loaded: {model_info.get('models_loaded', [])}")
            print(f"Model status: {model_info.get('model_status', {})}")
            print(f"Error counts: {model_info.get('error_counts', {})}")
            print(f"Health check: {model_info.get('health_check', {})}")
            
    except Exception as e:
        results["model_info"] = {"error": str(e)}
        print(f"Model info test error: {e}")
    
    return results

def test_graceful_degradation(token: str) -> Dict[str, Any]:
    """Test that the system gracefully handles model failures."""
    headers = {"Authorization": f"Bearer {token}"}
    results = {}
    
    print("\n=== Testing Graceful Degradation ===")
    
    # Test with minimal valid data to see if fallbacks work
    test_cases = [
        {
            "name": "severity_minimal",
            "endpoint": "/ml/predict/severity",
            "data": {"symptoms": ["mild_pain"]}
        },
        {
            "name": "flareup_minimal",
            "endpoint": "/ml/predict/flareup",
            "data": {
                "recent_symptoms": ["bloating"],
                "lifestyle_factors": {"stress": 3}
            }
        },
        {
            "name": "recommendations_minimal",
            "endpoint": "/ml/recommendations",
            "data": {
                "user_profile": {"age": 30},
                "current_symptoms": ["pain"],
                "recommendation_types": ["dietary"]
            }
        }
    ]
    
    for test_case in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}{test_case['endpoint']}",
                json=test_case["data"],
                headers=headers
            )
            results[test_case["name"]] = {
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text
            }
            print(f"{test_case['name']}: {response.status_code}")
            
            if response.status_code == 200:
                resp_data = response.json()
                model_status = resp_data.get("model_status", "unknown")
                print(f"  Model status: {model_status}")
                if "error_message" in resp_data:
                    print(f"  Error message: {resp_data['error_message']}")
                    
        except Exception as e:
            results[test_case["name"]] = {"error": str(e)}
            print(f"{test_case['name']} error: {e}")
    
    return results

def main():
    """Run comprehensive error handling tests."""
    print("=== ML Model Error Handling Comprehensive Test ===")
    
    # Login
    token = login_and_get_token()
    if not token:
        print("Failed to get authentication token. Exiting.")
        sys.exit(1)
    
    print(f"Successfully authenticated")
    
    # Run all tests
    all_results = {}
    
    try:
        all_results["invalid_inputs"] = test_invalid_inputs(token)
        all_results["edge_cases"] = test_edge_cases(token)
        all_results["model_health"] = test_model_health(token)
        all_results["graceful_degradation"] = test_graceful_degradation(token)
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        total_tests = 0
        successful_tests = 0
        
        for category, tests in all_results.items():
            print(f"\n{category.upper()}:")
            for test_name, result in tests.items():
                total_tests += 1
                if isinstance(result, dict) and result.get("status_code") in [200, 422]:
                    successful_tests += 1
                    status = "✓ PASS"
                else:
                    status = "✗ FAIL"
                print(f"  {test_name}: {status}")
        
        print(f"\nOverall: {successful_tests}/{total_tests} tests handled gracefully")
        
        # Save detailed results
        with open("error_handling_test_results.json", "w") as f:
            json.dump(all_results, f, indent=2, default=str)
        print(f"\nDetailed results saved to: error_handling_test_results.json")
        
    except Exception as e:
        print(f"Test execution error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()