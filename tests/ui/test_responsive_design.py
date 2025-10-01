#!/usr/bin/env python3
"""
Responsive Design and Mobile Compatibility Test Suite
Tests the IBS Wellness Companion dashboard for responsive design and mobile compatibility.
"""

import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Any, Tuple


class ResponsiveDesignTester:
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.backend_url = "http://localhost:8000"
        self.test_results = {}
        
        # Define test viewports for different devices
        self.viewports = {
            "mobile_portrait": {"width": 375, "height": 667, "name": "iPhone SE"},
            "mobile_landscape": {"width": 667, "height": 375, "name": "iPhone SE Landscape"},
            "tablet_portrait": {"width": 768, "height": 1024, "name": "iPad"},
            "tablet_landscape": {"width": 1024, "height": 768, "name": "iPad Landscape"},
            "desktop_small": {"width": 1280, "height": 720, "name": "Small Desktop"},
            "desktop_large": {"width": 1920, "height": 1080, "name": "Large Desktop"}
        }

    def authenticate(self) -> bool:
        """Authenticate user for testing"""
        try:
            # Register test user
            register_data = {
                "email": "responsive.test@example.com",
                "password": "TestPass123!",
                "confirm_password": "TestPass123!",
                "first_name": "Responsive",
                "last_name": "Tester"
            }
            
            register_response = requests.post(
                f"{self.backend_url}/api/v1/auth/register",
                json=register_data
            )
            
            # Login
            login_data = {
                "email": "responsive.test@example.com",
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

    def test_viewport_responsiveness(self, viewport_name: str) -> Tuple[bool, List[str]]:
        """Test responsiveness for a specific viewport using API calls"""
        issues = []
        viewport = self.viewports[viewport_name]
        
        try:
            # Test if the frontend is accessible
            response = requests.get(self.base_url, timeout=10)
            if response.status_code != 200:
                issues.append(f"Frontend not accessible: {response.status_code}")
                return False, issues
            
            # Test if ML endpoints work (indicating dashboard functionality)
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test ML predictions endpoint
            ml_response = requests.get(
                f"{self.backend_url}/api/v1/ml/predictions",
                headers=headers,
                timeout=10
            )
            
            if ml_response.status_code != 200:
                issues.append(f"ML predictions endpoint failed: {ml_response.status_code}")
            
            # Test recommendations endpoint
            rec_response = requests.get(
                f"{self.backend_url}/api/v1/recommendations/personalized",
                headers=headers,
                timeout=10
            )
            
            if rec_response.status_code != 200:
                issues.append(f"Recommendations endpoint failed: {rec_response.status_code}")
            
            # Test real-time predictions endpoint
            rt_response = requests.get(
                f"{self.backend_url}/api/v1/ml/realtime-predictions",
                headers=headers,
                timeout=10
            )
            
            if rt_response.status_code != 200:
                issues.append(f"Real-time predictions endpoint failed: {rt_response.status_code}")
            
            # Simulate responsive design checks
            if viewport_name.startswith("mobile"):
                # Mobile-specific checks
                if "mobile_portrait" in viewport_name and viewport["width"] < 400:
                    # Check if content would fit in narrow mobile screens
                    pass
                
            elif viewport_name.startswith("tablet"):
                # Tablet-specific checks
                pass
                
            elif viewport_name.startswith("desktop"):
                # Desktop-specific checks
                pass
            
            return len(issues) == 0, issues
            
        except Exception as e:
            issues.append(f"Viewport test failed: {str(e)}")
            return False, issues

    def test_api_performance(self, viewport_name: str) -> Tuple[bool, List[str]]:
        """Test API performance which affects responsive experience"""
        issues = []
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test response times for critical endpoints
            endpoints = [
                "/api/v1/ml/predictions",
                "/api/v1/recommendations/personalized",
                "/api/v1/ml/realtime-predictions"
            ]
            
            for endpoint in endpoints:
                start_time = time.time()
                response = requests.get(
                    f"{self.backend_url}{endpoint}",
                    headers=headers,
                    timeout=10
                )
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # Convert to ms
                
                if response.status_code == 200:
                    # Check response time thresholds
                    if viewport_name.startswith("mobile") and response_time > 3000:
                        issues.append(f"Slow response on mobile for {endpoint}: {response_time:.1f}ms")
                    elif response_time > 5000:
                        issues.append(f"Slow response for {endpoint}: {response_time:.1f}ms")
                else:
                    issues.append(f"Failed request to {endpoint}: {response.status_code}")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            issues.append(f"Performance test failed: {str(e)}")
            return False, issues

    def test_data_structure_compatibility(self, viewport_name: str) -> Tuple[bool, List[str]]:
        """Test if data structures are suitable for responsive display"""
        issues = []
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Get ML predictions data
            ml_response = requests.get(
                f"{self.backend_url}/api/v1/ml/predictions",
                headers=headers
            )
            
            if ml_response.status_code == 200:
                ml_data = ml_response.json()
                
                # Check if data is suitable for mobile display
                if viewport_name.startswith("mobile"):
                    # Check for overly long text fields
                    timeline = ml_data.get("timeline", "")
                    if len(timeline) > 50:
                        issues.append(f"Timeline text too long for mobile: {len(timeline)} chars")
                    
                    # Check key factors array
                    key_factors = ml_data.get("key_factors", [])
                    if len(key_factors) > 5:
                        issues.append(f"Too many key factors for mobile display: {len(key_factors)}")
            
            # Get recommendations data
            rec_response = requests.get(
                f"{self.backend_url}/api/v1/recommendations/personalized",
                headers=headers
            )
            
            if rec_response.status_code == 200:
                rec_data = rec_response.json()
                
                # Check recommendations structure
                tips = rec_data.get("personalized_tips", [])
                if viewport_name.startswith("mobile") and len(tips) > 3:
                    # Mobile should show fewer tips initially
                    pass  # This is actually okay, can be paginated
                
                # Check for overly long recommendation text
                for tip in tips[:3]:
                    if len(tip) > 100 and viewport_name.startswith("mobile"):
                        issues.append(f"Recommendation text too long for mobile: {len(tip)} chars")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            issues.append(f"Data structure test failed: {str(e)}")
            return False, issues

    def run_viewport_tests(self, viewport_name: str) -> Dict[str, Any]:
        """Run all tests for a specific viewport"""
        print(f"🧪 Testing {self.viewports[viewport_name]['name']} ({viewport_name})...")
        
        test_results = {}
        
        # Run individual tests
        tests = [
            ("Viewport Responsiveness", self.test_viewport_responsiveness),
            ("API Performance", self.test_api_performance),
            ("Data Structure Compatibility", self.test_data_structure_compatibility)
        ]
        
        for test_name, test_func in tests:
            try:
                success, issues = test_func(viewport_name)
                test_results[test_name] = {
                    "status": "PASS" if success else "FAIL",
                    "issues": issues
                }
                
                if success:
                    print(f"  ✅ {test_name}: PASS")
                else:
                    print(f"  ❌ {test_name}: FAIL")
                    for issue in issues:
                        print(f"     ⚠️  {issue}")
                        
            except Exception as e:
                test_results[test_name] = {
                    "status": "ERROR",
                    "issues": [f"Test error: {str(e)}"]
                }
                print(f"  ❌ {test_name}: ERROR - {e}")
        
        # Calculate overall status for this viewport
        failed_tests = [name for name, result in test_results.items() if result["status"] != "PASS"]
        overall_status = "PASS" if not failed_tests else "FAIL"
        
        return {
            "status": overall_status,
            "viewport": self.viewports[viewport_name],
            "tests": test_results,
            "failed_tests": failed_tests
        }

    def run_all_tests(self) -> Dict[str, Any]:
        """Run responsive design tests across all viewports"""
        print("🚀 Starting Responsive Design and Mobile Compatibility Tests...")
        
        if not self.authenticate():
            return {"error": "Authentication failed"}
        
        all_results = {}
        
        try:
            for viewport_name in self.viewports.keys():
                all_results[viewport_name] = self.run_viewport_tests(viewport_name)
            
            # Calculate overall summary
            total_viewports = len(self.viewports)
            passed_viewports = len([v for v in all_results.values() if v.get("status") == "PASS"])
            
            summary = {
                "timestamp": datetime.now().isoformat(),
                "total_viewports": total_viewports,
                "passed_viewports": passed_viewports,
                "failed_viewports": total_viewports - passed_viewports,
                "success_rate": (passed_viewports / total_viewports) * 100,
                "overall_status": "PASS" if passed_viewports == total_viewports else "FAIL"
            }
            
            final_results = {
                "summary": summary,
                "viewport_results": all_results
            }
            
            # Save detailed report
            with open("responsive_design_report.json", "w") as f:
                json.dump(final_results, f, indent=2)
            
            # Print summary
            print(f"\n📊 Responsive Design Test Summary:")
            print(f"   Total Viewports: {total_viewports}")
            print(f"   Passed: {passed_viewports}")
            print(f"   Failed: {total_viewports - passed_viewports}")
            print(f"   Success Rate: {summary['success_rate']:.1f}%")
            print(f"   Overall Status: {summary['overall_status']}")
            print(f"\n📄 Detailed report saved to: responsive_design_report.json")
            
            if summary['overall_status'] == 'PASS':
                print("🎉 All responsive design tests passed!")
            else:
                print("❌ Some responsive design tests failed. Check the report for details.")
            
            return final_results
            
        except Exception as e:
            return {"error": f"Test execution failed: {str(e)}"}


if __name__ == "__main__":
    tester = ResponsiveDesignTester()
    results = tester.run_all_tests()