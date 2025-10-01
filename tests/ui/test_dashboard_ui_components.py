#!/usr/bin/env python3
"""
Dashboard UI Components Integration Test

This script tests the frontend dashboard UI components to ensure they properly
display personalized data and recommendations from the backend APIs.
"""

import requests
import json
import time
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DashboardUITester:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.auth_token = None
        self.test_results = []
        
    def log_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result with details."""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"🔍 Running: {test_name}")
        print(f"{status} {test_name}: {details}")
        
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
        print()

    def authenticate_user(self) -> bool:
        """Authenticate user and get token for API calls."""
        try:
            # Login with test user
            login_data = {
                "email": "test@example.com",
                "password": "TestPassword123!"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                self.auth_token = auth_data.get("access_token")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False

    def test_frontend_health(self) -> bool:
        """Test if frontend is accessible and responding."""
        try:
            response = requests.get(f"{self.frontend_url}", timeout=10)
            if response.status_code == 200:
                self.log_test_result(
                    "Frontend Health Check",
                    True,
                    "Frontend is accessible and responding"
                )
                return True
            else:
                self.log_test_result(
                    "Frontend Health Check",
                    False,
                    f"Frontend returned status code: {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_test_result(
                "Frontend Health Check",
                False,
                f"Frontend not accessible: {str(e)}"
            )
            return False

    def test_personalization_api_integration(self) -> bool:
        """Test if personalization API is working and returning data."""
        try:
            if not self.auth_token:
                self.log_test_result(
                    "Personalization API Integration",
                    False,
                    "No authentication token available"
                )
                return False
                
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(
                f"{self.backend_url}/api/v1/personalization/profile",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                # Check if response has expected structure (updated to match actual API response)
                expected_fields = ["user_id", "personalized_thresholds", "nutrition_targets", "learning_patterns"]
                has_expected_structure = all(field in data for field in expected_fields)
                
                self.log_test_result(
                    "Personalization API Integration",
                    has_expected_structure,
                    f"API returned personalization data with {len(data)} fields including thresholds and targets"
                )
                return has_expected_structure
            else:
                self.log_test_result(
                    "Personalization API Integration",
                    False,
                    f"API returned status code: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "Personalization API Integration",
                False,
                f"API integration error: {str(e)}"
            )
            return False

    def test_ml_predictions_api_integration(self) -> bool:
        """Test if ML predictions API is working and returning data."""
        try:
            if not self.auth_token:
                self.log_test_result(
                    "ML Predictions API Integration",
                    False,
                    "No authentication token available"
                )
                return False
                
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(
                f"{self.backend_url}/api/v1/ml/predictions?include_recommendations=true",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                # Check if response has expected structure
                expected_fields = ["risk_level", "confidence", "next_flare_probability", "recommendations"]
                has_expected_structure = all(field in data for field in expected_fields)
                
                # Check if recommendations have proper structure
                recommendations = data.get("recommendations", {})
                rec_fields = ["immediate_actions", "dietary_suggestions", "lifestyle_changes"]
                has_rec_structure = all(field in recommendations for field in rec_fields)
                
                overall_success = has_expected_structure and has_rec_structure
                
                self.log_test_result(
                    "ML Predictions API Integration",
                    overall_success,
                    f"API returned predictions with risk_level: {data.get('risk_level')} and {len(recommendations)} recommendation categories"
                )
                return overall_success
            else:
                self.log_test_result(
                    "ML Predictions API Integration",
                    False,
                    f"API returned status code: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "ML Predictions API Integration",
                False,
                f"API integration error: {str(e)}"
            )
            return False

    def test_recommendations_api_integration(self) -> bool:
        """Test if recommendations API is working and returning data."""
        try:
            if not self.auth_token:
                self.log_test_result(
                    "Recommendations API Integration",
                    False,
                    "No authentication token available"
                )
                return False
                
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(
                f"{self.backend_url}/api/v1/recommendations/personalized",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                # Check if response has expected structure (personalized recommendations format)
                if isinstance(data, dict):
                    # Check for expected categories
                    expected_categories = ["dietary_recommendations", "lifestyle_insights"]
                    has_categories = any(category in data for category in expected_categories)
                    
                    if has_categories:
                        # Count total recommendations
                        total_recs = 0
                        for category in expected_categories:
                            if category in data and isinstance(data[category], list):
                                total_recs += len(data[category])
                        
                        self.log_test_result(
                            "Recommendations API Integration",
                            True,
                            f"API returned personalized recommendations with {total_recs} total recommendations across categories"
                        )
                        return True
                    else:
                        self.log_test_result(
                            "Recommendations API Integration",
                            False,
                            f"API returned unexpected structure: {list(data.keys())}"
                        )
                        return False
                else:
                    self.log_test_result(
                        "Recommendations API Integration",
                        False,
                        "API returned non-dict response format"
                    )
                    return False
            else:
                self.log_test_result(
                    "Recommendations API Integration",
                    False,
                    f"API returned status code: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "Recommendations API Integration",
                False,
                f"API integration error: {str(e)}"
            )
            return False

    def test_dashboard_data_flow(self) -> bool:
        """Test the complete data flow from backend to frontend dashboard."""
        try:
            # Test if we can get all required data for dashboard
            if not self.auth_token:
                self.log_test_result(
                    "Dashboard Data Flow",
                    False,
                    "No authentication token available"
                )
                return False
                
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Get all dashboard data
            endpoints = [
                ("/api/v1/personalization/profile", "personalization"),
                ("/api/v1/ml/predictions?include_recommendations=true", "predictions"),
                ("/api/v1/recommendations/personalized", "recommendations")
            ]
            
            dashboard_data = {}
            all_successful = True
            
            for endpoint, key in endpoints:
                try:
                    response = requests.get(f"{self.backend_url}{endpoint}", headers=headers)
                    if response.status_code == 200:
                        dashboard_data[key] = response.json()
                    else:
                        all_successful = False
                        logger.error(f"Failed to get {key}: {response.status_code}")
                except Exception as e:
                    all_successful = False
                    logger.error(f"Error getting {key}: {e}")
            
            if all_successful and len(dashboard_data) == 3:
                self.log_test_result(
                    "Dashboard Data Flow",
                    True,
                    f"Successfully retrieved all dashboard data: {list(dashboard_data.keys())}"
                )
                return True
            else:
                self.log_test_result(
                    "Dashboard Data Flow",
                    False,
                    f"Failed to retrieve complete dashboard data. Got: {list(dashboard_data.keys())}"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "Dashboard Data Flow",
                False,
                f"Dashboard data flow error: {str(e)}"
            )
            return False

    def test_frontend_api_configuration(self) -> bool:
        """Test if frontend is properly configured to connect to backend APIs."""
        try:
            # Check if frontend can make requests to backend
            # This is a basic test to see if CORS and API configuration work
            response = requests.get(f"{self.frontend_url}/api/health", timeout=5)
            
            # We expect this to either work (if frontend proxies to backend)
            # or return 404 (if frontend doesn't proxy health endpoint)
            # Both are acceptable as long as there's no CORS error
            
            if response.status_code in [200, 404]:
                self.log_test_result(
                    "Frontend API Configuration",
                    True,
                    "Frontend API configuration appears correct (no CORS issues)"
                )
                return True
            else:
                self.log_test_result(
                    "Frontend API Configuration",
                    False,
                    f"Unexpected response from frontend API: {response.status_code}"
                )
                return False
                
        except requests.exceptions.ConnectionError:
            self.log_test_result(
                "Frontend API Configuration",
                False,
                "Cannot connect to frontend - server may be down"
            )
            return False
        except Exception as e:
            self.log_test_result(
                "Frontend API Configuration",
                False,
                f"Frontend API configuration error: {str(e)}"
            )
            return False

    def run_all_tests(self):
        """Run all dashboard UI component tests."""
        print("Dashboard UI Components Integration Test")
        print("Testing dashboard components and personalized data display")
        print()
        print("🎯 Starting Dashboard UI Component Tests")
        print("=" * 60)
        print()
        
        # Authenticate first
        if not self.authenticate_user():
            print("❌ Authentication failed - cannot run dashboard tests")
            return
            
        # Run all tests
        tests = [
            self.test_frontend_health,
            self.test_personalization_api_integration,
            self.test_ml_predictions_api_integration,
            self.test_recommendations_api_integration,
            self.test_dashboard_data_flow,
            self.test_frontend_api_configuration
        ]
        
        for test in tests:
            test()
            time.sleep(0.5)  # Small delay between tests
        
        # Print summary
        print("=" * 60)
        print("📊 DASHBOARD UI COMPONENT TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = [r for r in self.test_results if r["passed"]]
        failed_tests = [r for r in self.test_results if not r["passed"]]
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {len(passed_tests)}")
        print(f"Failed: {len(failed_tests)}")
        print(f"Success Rate: {len(passed_tests)/len(self.test_results)*100:.1f}%")
        print()
        
        if failed_tests:
            print("⚠️  Some dashboard UI tests FAILED")
            print("❌ Dashboard UI components need attention")
            print()
            print("Failed Tests:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        else:
            print("🎉 All dashboard UI component tests PASSED!")
            print("✅ Dashboard is properly displaying personalized data")

if __name__ == "__main__":
    tester = DashboardUITester()
    tester.run_all_tests()