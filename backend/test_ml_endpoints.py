#!/usr/bin/env python3
"""
Test script to verify ML prediction endpoints are working correctly.
"""

import requests
import os

BASE_URL = f"{os.getenv('API_BASE_URL', 'http://localhost:8000')}/api/v1"


def test_ml_endpoints():
    """Test ML prediction endpoints without authentication to check exist."""
    
    endpoints_to_test = [
        "/ml/predictions",
        "/ml/models/info",
        "/ml/predict/severity",
        "/ml/predict/flareup",
        "/ml/predict/recommendations",
        "/ml/predict/multimodal"
    ]
    
    print("Testing ML Prediction Endpoints...")
    print("=" * 50)
    
    for endpoint in endpoints_to_test:
        url = f"{BASE_URL}{endpoint}"
        try:
            if endpoint == "/ml/predictions":
                # GET request
                response = requests.get(url, timeout=5)
            else:
                # POST request with minimal data
                response = requests.post(url, json={}, timeout=5)
            
            print(f"✓ {endpoint}: Status {response.status_code}")
            
            # Check if it's a 401 (unauthorized) or 422 (validation error)
            # These indicate the endpoint exists but requires auth/proper data
            if response.status_code in [401, 422]:
                print("  → Endpoint exists (requires auth/validation)")
            elif response.status_code == 404:
                print("  → Endpoint NOT FOUND")
            elif response.status_code == 200:
                print("  → Endpoint working (unexpected without auth)")
            else:
                print(f"  → Status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"✗ {endpoint}: Connection error - {e}")
    
    print("\n" + "=" * 50)


if __name__ == "__main__":
    test_ml_endpoints()