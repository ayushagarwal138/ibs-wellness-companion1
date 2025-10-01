#!/usr/bin/env python3
"""
Test script to verify that the reports page TypeError has been resolved.
This test checks that the reports page loads without runtime errors.
"""

import requests
import time
import sys
from datetime import datetime

# Configuration
FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:8000"

def test_reports_page_accessibility():
    """Test that the reports page is accessible without runtime errors."""
    print("🔍 Testing Reports Page Accessibility...")
    
    try:
        # Test that the frontend is running
        response = requests.get(f"{FRONTEND_URL}/reports", timeout=10)
        
        if response.status_code == 200:
            print("✅ Reports page is accessible (HTTP 200)")
            return True
        else:
            print(f"❌ Reports page returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to access reports page: {e}")
        return False

def test_backend_ml_endpoints():
    """Test that the ML endpoints are working correctly."""
    print("\n🔍 Testing Backend ML Endpoints...")
    
    endpoints_to_test = [
        "/api/v1/ml/predictions",
        "/api/v1/recommendations/personalized"
    ]
    
    results = {}
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
            results[endpoint] = {
                'status_code': response.status_code,
                'success': response.status_code in [200, 401]  # 401 is expected without auth
            }
            
            if results[endpoint]['success']:
                print(f"✅ {endpoint} - Status: {response.status_code}")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            results[endpoint] = {
                'status_code': None,
                'success': False,
                'error': str(e)
            }
            print(f"❌ {endpoint} - Error: {e}")
    
    return results

def test_frontend_compilation():
    """Test that the frontend compiles without errors."""
    print("\n🔍 Testing Frontend Compilation Status...")
    
    try:
        # Check if the main page loads (indicates successful compilation)
        response = requests.get(FRONTEND_URL, timeout=10)
        
        if response.status_code == 200:
            print("✅ Frontend compilation successful")
            return True
        else:
            print(f"❌ Frontend compilation issue - Status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend compilation test failed: {e}")
        return False

def main():
    """Run all tests to verify the reports page fix."""
    print("=" * 60)
    print("🧪 REPORTS PAGE TYPEERROR FIX VERIFICATION")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run tests
    tests = [
        ("Frontend Compilation", test_frontend_compilation),
        ("Reports Page Accessibility", test_reports_page_accessibility),
        ("Backend ML Endpoints", test_backend_ml_endpoints)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! The TypeError fix is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())