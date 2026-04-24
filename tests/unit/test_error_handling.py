#!/usr/bin/env python3
"""
Error Handling and Fallback States Test Suite
Tests the IBS Wellness Companion dashboard for proper error handling and fallback states.
"""

import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Any, Tuple
import threading
import subprocess
import signal
import os


class ErrorHandlingTester:
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.backend_url = "http://localhost:8000"
        self.test_results = {}
        self.auth_token = None
        
    def authenticate(self) -> bool:
        """Authenticate user for testing"""
        try:
            # Register test user
            register_data = {
                "email": "error.test@example.com",
                "password": "TestPass123!",
                "confirm_password": "TestPass123!",
                "first_name": "Error",
                "last_name": "Tester"
            }
            
            register_response = requests.post(
                f"{self.backend_url}/api/v1/auth/register",
                json=register_data
            )
            
            # Login
            login_data = {
                "email": "error.test@example.com",
                "password": "TestPass123!"
            }
            
            login_response = requests.post(
                f"{self.backend_url}/api/v1/auth/login",
                json=login_data
            )
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                self.auth_token = token_data.get("access_token")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False

    def test_invalid_authentication(self) -> Tuple[bool, List[str]]:
        """Test error handling for invalid authentication"""
        issues = []
        
        try:
            # Test with invalid token
            invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
            
            endpoints = [
                "/api/v1/ml/predictions",
                "/api/v1/recommendations/personalized",
                "/api/v1/ml/realtime-predictions"
            ]
            
            for endpoint in endpoints:
                response = requests.get(
                    f"{self.backend_url}{endpoint}",
                    headers=invalid_headers,
                    timeout=10
                )
                
                # Should return 401 Unauthorized or 403 Forbidden
                if response.status_code not in [401, 403]:
                    issues.append(f"Invalid auth should return 401/403 for {endpoint}, got {response.status_code}")
                else:
                    # Check if response has proper error structure
                    try:
                        error_data = response.json()
                        if "detail" not in error_data and "message" not in error_data:
                            issues.append(f"Missing error message in response for {endpoint}")
                    except json.JSONDecodeError:
                        issues.append(f"Invalid JSON in error response for {endpoint}")
            
            # Test with no authorization header
            for endpoint in endpoints:
                response = requests.get(
                    f"{self.backend_url}{endpoint}",
                    timeout=10
                )
                
                if response.status_code not in [401, 403]:
                    issues.append(f"No auth should return 401/403 for {endpoint}, got {response.status_code}")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            return False, [f"Authentication error test failed: {str(e)}"]

    def test_malformed_requests(self) -> Tuple[bool, List[str]]:
        """Test error handling for malformed requests"""
        issues = []
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test POST requests with invalid JSON
            post_endpoints = [
                "/api/v1/auth/login",
                "/api/v1/auth/register"
            ]
            
            for endpoint in post_endpoints:
                # Test with invalid JSON
                response = requests.post(
                    f"{self.backend_url}{endpoint}",
                    data="invalid json data",
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code not in [400, 422]:
                    issues.append(f"Invalid JSON should return 400/422 for {endpoint}, got {response.status_code}")
            
            # Test with missing required fields
            login_response = requests.post(
                f"{self.backend_url}/api/v1/auth/login",
                json={"email": "test@example.com"},  # Missing password
                timeout=10
            )
            
            if login_response.status_code not in [400, 422]:
                issues.append(f"Missing password should return 400/422, got {login_response.status_code}")
            
            # Test with invalid email format
            login_response = requests.post(
                f"{self.backend_url}/api/v1/auth/login",
                json={"email": "invalid-email", "password": "test123"},
                timeout=10
            )
            
            if login_response.status_code not in [400, 422]:
                issues.append(f"Invalid email should return 400/422, got {login_response.status_code}")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            return False, [f"Malformed requests test failed: {str(e)}"]

    def test_nonexistent_endpoints(self) -> Tuple[bool, List[str]]:
        """Test error handling for non-existent endpoints"""
        issues = []
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test non-existent endpoints
            fake_endpoints = [
                "/api/v1/nonexistent",
                "/api/v1/ml/fake-predictions",
                "/api/v1/recommendations/invalid",
                "/api/v2/ml/predictions"  # Wrong version
            ]
            
            for endpoint in fake_endpoints:
                response = requests.get(
                    f"{self.backend_url}{endpoint}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code != 404:
                    issues.append(f"Non-existent endpoint should return 404 for {endpoint}, got {response.status_code}")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            return False, [f"Non-existent endpoints test failed: {str(e)}"]

    def test_rate_limiting(self) -> Tuple[bool, List[str]]:
        """Test rate limiting behavior"""
        issues = []
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Make rapid requests to test rate limiting
            endpoint = "/api/v1/ml/predictions"
            rapid_requests = 20
            
            responses = []
            for i in range(rapid_requests):
                response = requests.get(
                    f"{self.backend_url}{endpoint}",
                    headers=headers,
                    timeout=5
                )
                responses.append(response.status_code)
                time.sleep(0.1)  # Small delay between requests
            
            # Check if any requests were rate limited (429)
            rate_limited = [r for r in responses if r == 429]
            
            # It's okay if there's no rate limiting implemented yet
            # But if there is, it should work properly
            if rate_limited:
                print(f"  ℹ️  Rate limiting detected: {len(rate_limited)} requests limited")
            
            # Check for server errors due to overload
            server_errors = [r for r in responses if r >= 500]
            if server_errors:
                issues.append(f"Server errors during rapid requests: {len(server_errors)} errors")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            return False, [f"Rate limiting test failed: {str(e)}"]

    def test_timeout_handling(self) -> Tuple[bool, List[str]]:
        """Test timeout handling"""
        issues = []
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test with very short timeout
            endpoints = [
                "/api/v1/ml/predictions",
                "/api/v1/recommendations/personalized"
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(
                        f"{self.backend_url}{endpoint}",
                        headers=headers,
                        timeout=0.001  # Very short timeout
                    )
                    # If this succeeds, the endpoint is very fast (good)
                    if response.status_code == 200:
                        print(f"  ✅ {endpoint} responded very quickly")
                except requests.exceptions.Timeout:
                    # This is expected with such a short timeout
                    print(f"  ℹ️  {endpoint} timed out as expected with 0.001s timeout")
                except Exception as e:
                    issues.append(f"Unexpected error during timeout test for {endpoint}: {str(e)}")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            return False, [f"Timeout handling test failed: {str(e)}"]

    def test_data_validation_errors(self) -> Tuple[bool, List[str]]:
        """Test data validation error handling"""
        issues = []
        
        try:
            # Test registration with invalid data
            invalid_registrations = [
                {
                    "email": "test@example.com",
                    "password": "123",  # Too short
                    "confirm_password": "123",
                    "first_name": "Test",
                    "last_name": "User"
                },
                {
                    "email": "invalid-email",  # Invalid email
                    "password": "TestPass123!",
                    "confirm_password": "TestPass123!",
                    "first_name": "Test",
                    "last_name": "User"
                },
                {
                    "email": "test2@example.com",
                    "password": "TestPass123!",
                    "confirm_password": "DifferentPass123!",  # Passwords don't match
                    "first_name": "Test",
                    "last_name": "User"
                }
            ]
            
            for invalid_data in invalid_registrations:
                response = requests.post(
                    f"{self.backend_url}/api/v1/auth/register",
                    json=invalid_data,
                    timeout=10
                )
                
                if response.status_code not in [400, 422]:
                    issues.append(f"Invalid registration data should return 400/422, got {response.status_code}")
                else:
                    # Check if error message is informative
                    try:
                        error_data = response.json()
                        if not any(key in error_data for key in ["detail", "message", "errors"]):
                            issues.append("Error response missing informative error message")
                    except json.JSONDecodeError:
                        issues.append("Invalid JSON in validation error response")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            return False, [f"Data validation test failed: {str(e)}"]

    def test_frontend_accessibility(self) -> Tuple[bool, List[str]]:
        """Test if frontend is accessible and handles backend errors gracefully"""
        issues = []
        
        try:
            # Test if frontend is accessible
            response = requests.get(self.base_url, timeout=10)
            if response.status_code != 200:
                issues.append(f"Frontend not accessible: {response.status_code}")
                return False, issues
            
            # Test if frontend serves static assets
            common_assets = [
                "/favicon.ico",
                "/manifest.json"
            ]
            
            for asset in common_assets:
                try:
                    asset_response = requests.get(f"{self.base_url}{asset}", timeout=5)
                    # It's okay if these don't exist, but they shouldn't cause server errors
                    if asset_response.status_code >= 500:
                        issues.append(f"Server error for asset {asset}: {asset_response.status_code}")
                except requests.exceptions.RequestException:
                    # Network errors are okay for optional assets
                    pass
            
            return len(issues) == 0, issues
            
        except Exception as e:
            return False, [f"Frontend accessibility test failed: {str(e)}"]

    def test_graceful_degradation(self) -> Tuple[bool, List[str]]:
        """Test graceful degradation when ML services are unavailable"""
        issues = []
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test what happens when we make requests to ML endpoints
            # (We can't easily simulate service unavailability without stopping services)
            
            # Test if endpoints return consistent error formats
            endpoints = [
                "/api/v1/ml/predictions",
                "/api/v1/recommendations/personalized",
                "/api/v1/ml/realtime-predictions"
            ]
            
            for endpoint in endpoints:
                response = requests.get(
                    f"{self.backend_url}{endpoint}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    # Service is working, check data structure
                    try:
                        data = response.json()
                        if not isinstance(data, dict):
                            issues.append(f"Response from {endpoint} is not a JSON object")
                    except json.JSONDecodeError:
                        issues.append(f"Invalid JSON response from {endpoint}")
                elif response.status_code >= 500:
                    # Server error - check if it has proper error format
                    try:
                        error_data = response.json()
                        if "detail" not in error_data and "message" not in error_data:
                            issues.append(f"Server error missing proper error message for {endpoint}")
                    except json.JSONDecodeError:
                        issues.append(f"Server error with invalid JSON for {endpoint}")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            return False, [f"Graceful degradation test failed: {str(e)}"]

    def run_error_test(self, test_name: str, test_func) -> Dict[str, Any]:
        """Run a single error handling test"""
        try:
            success, issues = test_func()
            return {
                "status": "PASS" if success else "FAIL",
                "issues": issues
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "issues": [f"Test error: {str(e)}"]
            }

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all error handling tests"""
        print("🚀 Starting Error Handling and Fallback States Tests...")
        
        if not self.authenticate():
            return {"error": "Authentication failed"}
        
        # Define all tests
        tests = [
            ("Invalid Authentication", self.test_invalid_authentication),
            ("Malformed Requests", self.test_malformed_requests),
            ("Non-existent Endpoints", self.test_nonexistent_endpoints),
            ("Rate Limiting", self.test_rate_limiting),
            ("Timeout Handling", self.test_timeout_handling),
            ("Data Validation Errors", self.test_data_validation_errors),
            ("Frontend Accessibility", self.test_frontend_accessibility),
            ("Graceful Degradation", self.test_graceful_degradation)
        ]
        
        test_results = {}
        
        try:
            for test_name, test_func in tests:
                print(f"🧪 Testing {test_name}...")
                result = self.run_error_test(test_name, test_func)
                test_results[test_name] = result
                
                if result["status"] == "PASS":
                    print(f"  ✅ {test_name}: PASS")
                else:
                    print(f"  ❌ {test_name}: {result['status']}")
                    for issue in result["issues"]:
                        print(f"     ⚠️  {issue}")
            
            # Calculate summary
            total_tests = len(tests)
            passed_tests = len([t for t in test_results.values() if t["status"] == "PASS"])
            failed_tests = total_tests - passed_tests
            
            summary = {
                "timestamp": datetime.now().isoformat(),
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests / total_tests) * 100,
                "overall_status": "PASS" if passed_tests == total_tests else "FAIL"
            }
            
            final_results = {
                "summary": summary,
                "test_results": test_results
            }
            
            # Save detailed report
            with open("error_handling_report.json", "w") as f:
                json.dump(final_results, f, indent=2)
            
            # Print summary
            print(f"\n📊 Error Handling Test Summary:")
            print(f"   Total Tests: {total_tests}")
            print(f"   Passed: {passed_tests}")
            print(f"   Failed: {failed_tests}")
            print(f"   Success Rate: {summary['success_rate']:.1f}%")
            print(f"   Overall Status: {summary['overall_status']}")
            print(f"\n📄 Detailed report saved to: error_handling_report.json")
            
            if summary['overall_status'] == 'PASS':
                print("🎉 All error handling tests passed!")
            else:
                print("❌ Some error handling tests failed. Check the report for details.")
            
            return final_results
            
        except Exception as e:
            return {"error": f"Test execution failed: {str(e)}"}


if __name__ == "__main__":
    tester = ErrorHandlingTester()
    results = tester.run_all_tests()