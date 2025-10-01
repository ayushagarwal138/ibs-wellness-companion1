#!/usr/bin/env python3
"""
Comprehensive Dashboard Integration Test
Tests the integration between frontend dashboard and backend personalization APIs
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

class DashboardIntegrationTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str = "", details: Dict = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {json.dumps(details, indent=2)}")
    
    def test_backend_health(self) -> bool:
        """Test backend server health"""
        try:
            response = self.session.get(f"{BACKEND_URL}/health", timeout=5)
            success = response.status_code == 200
            self.log_test(
                "Backend Health Check",
                success,
                f"Status: {response.status_code}",
                {"response": response.json() if success else response.text}
            )
            return success
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Connection failed: {str(e)}")
            return False
    
    def test_frontend_health(self) -> bool:
        """Test frontend server health"""
        try:
            response = self.session.get(f"{FRONTEND_URL}", timeout=5)
            success = response.status_code == 200
            self.log_test(
                "Frontend Health Check",
                success,
                f"Status: {response.status_code}",
                {"content_length": len(response.text)}
            )
            return success
        except Exception as e:
            self.log_test("Frontend Health Check", False, f"Connection failed: {str(e)}")
            return False
    
    def test_personalization_endpoints(self) -> bool:
        """Test personalization API endpoints without authentication"""
        endpoints = [
            ("/api/v1/personalization/profile", "GET"),
            ("/api/v1/ml/predictions", "GET"),
            ("/api/v1/recommendations/personalized", "GET")
        ]
        
        all_success = True
        for endpoint, method in endpoints:
            try:
                url = f"{BACKEND_URL}{endpoint}"
                response = self.session.request(method, url, timeout=5)
                
                # We expect 403 (Forbidden) for unauthenticated requests
                expected_status = 403
                success = response.status_code == expected_status
                
                self.log_test(
                    f"Personalization Endpoint {endpoint}",
                    success,
                    f"Status: {response.status_code} (expected {expected_status})",
                    {"endpoint": endpoint, "method": method}
                )
                
                if not success:
                    all_success = False
                    
            except Exception as e:
                self.log_test(
                    f"Personalization Endpoint {endpoint}",
                    False,
                    f"Request failed: {str(e)}"
                )
                all_success = False
        
        return all_success
    
    def test_dashboard_service_structure(self) -> bool:
        """Test that dashboard service files exist and have correct structure"""
        import os
        
        frontend_path = "/Users/ayushagarwal/ibs-wellness-companion/frontend"
        required_files = [
            "src/services/dynamic-dashboard-service.ts",
            "src/components/dashboard/dashboard.tsx",
            "src/components/dashboard/main-dashboard.tsx"
        ]
        
        all_exist = True
        for file_path in required_files:
            full_path = os.path.join(frontend_path, file_path)
            exists = os.path.exists(full_path)
            
            self.log_test(
                f"Dashboard File Exists: {file_path}",
                exists,
                "File found" if exists else "File missing",
                {"path": full_path}
            )
            
            if not exists:
                all_exist = False
        
        return all_exist
    
    def test_api_integration_points(self) -> bool:
        """Test specific API integration points used by dashboard"""
        # Test OpenAPI docs to verify endpoint structure
        try:
            response = self.session.get(f"{BACKEND_URL}/docs", timeout=5)
            docs_available = response.status_code == 200
            
            self.log_test(
                "API Documentation Available",
                docs_available,
                f"OpenAPI docs status: {response.status_code}"
            )
            
            # Test OpenAPI JSON schema
            response = self.session.get(f"{BACKEND_URL}/openapi.json", timeout=5)
            if response.status_code == 200:
                openapi_data = response.json()
                
                # Check for required endpoints
                paths = openapi_data.get("paths", {})
                required_endpoints = [
                    "/api/v1/personalization/profile",
                    "/api/v1/ml/predictions", 
                    "/api/v1/recommendations/personalized"
                ]
                
                endpoints_found = []
                for endpoint in required_endpoints:
                    if endpoint in paths:
                        endpoints_found.append(endpoint)
                
                all_endpoints_exist = len(endpoints_found) == len(required_endpoints)
                
                self.log_test(
                    "Required API Endpoints in Schema",
                    all_endpoints_exist,
                    f"Found {len(endpoints_found)}/{len(required_endpoints)} endpoints",
                    {"found": endpoints_found, "required": required_endpoints}
                )
                
                return docs_available and all_endpoints_exist
            else:
                self.log_test(
                    "OpenAPI Schema",
                    False,
                    f"Failed to fetch schema: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "API Integration Points",
                False,
                f"Failed to test integration points: {str(e)}"
            )
            return False
    
    def test_dashboard_data_flow(self) -> bool:
        """Test the data flow from backend to frontend dashboard components"""
        # This test verifies the structure matches between backend responses and frontend expectations
        
        # Check if the dynamic dashboard service has the correct API base URL
        try:
            service_file = "/Users/ayushagarwal/ibs-wellness-companion/frontend/src/services/dynamic-dashboard-service.ts"
            with open(service_file, 'r') as f:
                content = f.read()
                
            # Check for correct API base URL configuration
            has_api_url = "API_BASE_URL" in content
            has_localhost_8000 = "localhost:8000" in content
            has_auth_headers = "Authorization" in content and "Bearer" in content
            has_personalization_endpoints = "/api/v1/recommendations/personalized" in content
            has_ml_predictions = "/api/v1/ml/predictions" in content
            
            all_checks = [has_api_url, has_localhost_8000, has_auth_headers, 
                         has_personalization_endpoints, has_ml_predictions]
            
            self.log_test(
                "Dashboard Service Configuration",
                all(all_checks),
                f"Configuration checks: {sum(all_checks)}/{len(all_checks)} passed",
                {
                    "api_url_configured": has_api_url,
                    "correct_backend_url": has_localhost_8000,
                    "auth_headers": has_auth_headers,
                    "personalization_endpoint": has_personalization_endpoints,
                    "ml_predictions_endpoint": has_ml_predictions
                }
            )
            
            return all(all_checks)
            
        except Exception as e:
            self.log_test(
                "Dashboard Data Flow",
                False,
                f"Failed to analyze service file: {str(e)}"
            )
            return False
    
    def test_ui_component_integration(self) -> bool:
        """Test that UI components are properly structured for personalized data"""
        try:
            dashboard_file = "/Users/ayushagarwal/ibs-wellness-companion/frontend/src/components/dashboard/dashboard.tsx"
            with open(dashboard_file, 'r') as f:
                content = f.read()
            
            # Check for key UI integration points
            has_ai_predictions = "aiPredictions" in content
            has_personalized_recommendations = "personalizedRecommendations" in content
            has_dynamic_dashboard_service = "dynamicDashboardService" in content
            has_ml_predictions_display = "AI Health Predictions" in content
            has_recommendation_tabs = "Detailed Recommendations" in content
            has_dietary_recommendations = "dietary" in content and "lifestyle" in content and "medical" in content
            
            ui_checks = [
                has_ai_predictions, has_personalized_recommendations, 
                has_dynamic_dashboard_service, has_ml_predictions_display,
                has_recommendation_tabs, has_dietary_recommendations
            ]
            
            self.log_test(
                "UI Component Integration",
                all(ui_checks),
                f"UI integration checks: {sum(ui_checks)}/{len(ui_checks)} passed",
                {
                    "ai_predictions": has_ai_predictions,
                    "personalized_recommendations": has_personalized_recommendations,
                    "dashboard_service": has_dynamic_dashboard_service,
                    "ml_display": has_ml_predictions_display,
                    "recommendation_tabs": has_recommendation_tabs,
                    "recommendation_categories": has_dietary_recommendations
                }
            )
            
            return all(ui_checks)
            
        except Exception as e:
            self.log_test(
                "UI Component Integration",
                False,
                f"Failed to analyze dashboard component: {str(e)}"
            )
            return False
    
    def run_all_tests(self) -> bool:
        """Run all dashboard integration tests"""
        print("🚀 Starting Dashboard Integration Tests")
        print("=" * 50)
        
        # Test sequence
        tests = [
            ("Backend Health", self.test_backend_health),
            ("Frontend Health", self.test_frontend_health),
            ("Personalization Endpoints", self.test_personalization_endpoints),
            ("Dashboard Service Structure", self.test_dashboard_service_structure),
            ("API Integration Points", self.test_api_integration_points),
            ("Dashboard Data Flow", self.test_dashboard_data_flow),
            ("UI Component Integration", self.test_ui_component_integration)
        ]
        
        all_passed = True
        for test_name, test_func in tests:
            print(f"\n📋 Running: {test_name}")
            try:
                result = test_func()
                if not result:
                    all_passed = False
            except Exception as e:
                self.log_test(test_name, False, f"Test execution failed: {str(e)}")
                all_passed = False
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for r in self.test_results if r["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if all_passed:
            print("\n🎉 All dashboard integration tests PASSED!")
            print("✅ Dashboard is ready for personalized data and recommendations")
        else:
            print("\n⚠️  Some tests FAILED")
            print("❌ Dashboard integration needs attention")
            
            # Show failed tests
            failed_tests = [r for r in self.test_results if not r["success"]]
            if failed_tests:
                print("\nFailed Tests:")
                for test in failed_tests:
                    print(f"  - {test['test']}: {test['message']}")
        
        return all_passed

def main():
    """Main test execution"""
    tester = DashboardIntegrationTester()
    
    print("Dashboard Integration Test Suite")
    print("Testing integration between frontend dashboard and backend personalization APIs")
    print()
    
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()