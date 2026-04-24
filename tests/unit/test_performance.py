#!/usr/bin/env python3
"""
Performance Requirements and Loading States Test Suite
Tests the IBS Wellness Companion dashboard for performance requirements and loading states.
"""

import json
import time
import requests
import statistics
from datetime import datetime
from typing import Dict, List, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


class PerformanceTester:
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.backend_url = "http://localhost:8000"
        self.test_results = {}
        self.auth_token = None
        
        # Performance thresholds (in milliseconds)
        self.thresholds = {
            "fast_response": 500,      # Very fast responses
            "acceptable_response": 2000,  # Acceptable responses
            "slow_response": 5000,     # Slow but tolerable
            "timeout": 10000           # Maximum timeout
        }
        
    def authenticate(self) -> bool:
        """Authenticate user for testing"""
        try:
            # Register test user
            register_data = {
                "email": "performance.test@example.com",
                "password": "TestPass123!",
                "confirm_password": "TestPass123!",
                "first_name": "Performance",
                "last_name": "Tester"
            }
            
            register_response = requests.post(
                f"{self.backend_url}/api/v1/auth/register",
                json=register_data
            )
            
            # Login
            login_data = {
                "email": "performance.test@example.com",
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

    def measure_response_time(self, url: str, headers: Dict = None, method: str = "GET", data: Dict = None) -> Tuple[float, int, bool]:
        """Measure response time for a single request"""
        try:
            start_time = time.time()
            
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=self.thresholds["timeout"]/1000)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=self.thresholds["timeout"]/1000)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            return response_time, response.status_code, True
            
        except requests.exceptions.Timeout:
            return self.thresholds["timeout"], 408, False
        except Exception as e:
            return self.thresholds["timeout"], 500, False

    def test_endpoint_performance(self, endpoint: str, method: str = "GET", data: Dict = None, iterations: int = 5) -> Tuple[bool, List[str], Dict[str, Any]]:
        """Test performance of a specific endpoint"""
        issues = []
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        url = f"{self.backend_url}{endpoint}"
        
        response_times = []
        status_codes = []
        success_count = 0
        
        try:
            for i in range(iterations):
                response_time, status_code, success = self.measure_response_time(url, headers, method, data)
                response_times.append(response_time)
                status_codes.append(status_code)
                
                if success and status_code == 200:
                    success_count += 1
                
                # Small delay between requests
                time.sleep(0.1)
            
            # Calculate statistics
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            median_response_time = statistics.median(response_times)
            
            # Performance analysis
            fast_responses = len([t for t in response_times if t <= self.thresholds["fast_response"]])
            acceptable_responses = len([t for t in response_times if t <= self.thresholds["acceptable_response"]])
            slow_responses = len([t for t in response_times if t > self.thresholds["acceptable_response"]])
            
            # Check performance criteria
            if avg_response_time > self.thresholds["acceptable_response"]:
                issues.append(f"Average response time too slow: {avg_response_time:.1f}ms > {self.thresholds['acceptable_response']}ms")
            
            if max_response_time > self.thresholds["slow_response"]:
                issues.append(f"Maximum response time too slow: {max_response_time:.1f}ms > {self.thresholds['slow_response']}ms")
            
            if success_count < iterations * 0.9:  # 90% success rate required
                issues.append(f"Low success rate: {success_count}/{iterations} ({success_count/iterations*100:.1f}%)")
            
            performance_data = {
                "endpoint": endpoint,
                "method": method,
                "iterations": iterations,
                "avg_response_time": avg_response_time,
                "min_response_time": min_response_time,
                "max_response_time": max_response_time,
                "median_response_time": median_response_time,
                "fast_responses": fast_responses,
                "acceptable_responses": acceptable_responses,
                "slow_responses": slow_responses,
                "success_count": success_count,
                "success_rate": success_count / iterations * 100,
                "all_response_times": response_times,
                "status_codes": status_codes
            }
            
            return len(issues) == 0, issues, performance_data
            
        except Exception as e:
            return False, [f"Performance test failed: {str(e)}"], {}

    def test_concurrent_load(self, endpoint: str, concurrent_users: int = 5, requests_per_user: int = 3) -> Tuple[bool, List[str], Dict[str, Any]]:
        """Test performance under concurrent load"""
        issues = []
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        url = f"{self.backend_url}{endpoint}"
        
        all_response_times = []
        all_status_codes = []
        errors = []
        
        def make_requests(user_id: int):
            """Make requests for a single user"""
            user_times = []
            user_codes = []
            
            for i in range(requests_per_user):
                try:
                    response_time, status_code, success = self.measure_response_time(url, headers)
                    user_times.append(response_time)
                    user_codes.append(status_code)
                    
                    if not success:
                        errors.append(f"User {user_id} request {i+1} failed")
                        
                except Exception as e:
                    errors.append(f"User {user_id} request {i+1} error: {str(e)}")
            
            return user_times, user_codes
        
        try:
            # Execute concurrent requests
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
                futures = [executor.submit(make_requests, user_id) for user_id in range(concurrent_users)]
                
                for future in as_completed(futures):
                    try:
                        user_times, user_codes = future.result()
                        all_response_times.extend(user_times)
                        all_status_codes.extend(user_codes)
                    except Exception as e:
                        errors.append(f"Thread execution error: {str(e)}")
            
            end_time = time.time()
            total_test_time = (end_time - start_time) * 1000
            
            if all_response_times:
                # Calculate statistics
                avg_response_time = statistics.mean(all_response_times)
                max_response_time = max(all_response_times)
                successful_requests = len([code for code in all_status_codes if code == 200])
                total_requests = concurrent_users * requests_per_user
                
                # Performance analysis
                if avg_response_time > self.thresholds["acceptable_response"] * 1.5:  # Allow 50% degradation under load
                    issues.append(f"Average response time under load too slow: {avg_response_time:.1f}ms")
                
                if max_response_time > self.thresholds["slow_response"]:
                    issues.append(f"Maximum response time under load too slow: {max_response_time:.1f}ms")
                
                if successful_requests < total_requests * 0.8:  # 80% success rate under load
                    issues.append(f"Low success rate under load: {successful_requests}/{total_requests} ({successful_requests/total_requests*100:.1f}%)")
                
                if len(errors) > total_requests * 0.1:  # Max 10% errors
                    issues.append(f"Too many errors under load: {len(errors)} errors")
                
                load_data = {
                    "endpoint": endpoint,
                    "concurrent_users": concurrent_users,
                    "requests_per_user": requests_per_user,
                    "total_requests": total_requests,
                    "successful_requests": successful_requests,
                    "success_rate": successful_requests / total_requests * 100,
                    "avg_response_time": avg_response_time,
                    "max_response_time": max_response_time,
                    "total_test_time": total_test_time,
                    "errors": errors[:10],  # Limit error list
                    "error_count": len(errors)
                }
                
                return len(issues) == 0, issues, load_data
            else:
                return False, ["No successful responses during load test"], {}
            
        except Exception as e:
            return False, [f"Concurrent load test failed: {str(e)}"], {}

    def test_frontend_performance(self) -> Tuple[bool, List[str], Dict[str, Any]]:
        """Test frontend performance"""
        issues = []
        
        try:
            # Test main page load time
            response_time, status_code, success = self.measure_response_time(self.base_url)
            
            if not success or status_code != 200:
                issues.append(f"Frontend not accessible: status {status_code}")
                return False, issues, {}
            
            # Check if frontend loads quickly
            if response_time > self.thresholds["acceptable_response"]:
                issues.append(f"Frontend loads too slowly: {response_time:.1f}ms > {self.thresholds['acceptable_response']}ms")
            
            # Test static asset performance (if available)
            assets_to_test = [
                "/favicon.ico",
                "/manifest.json"
            ]
            
            asset_times = []
            for asset in assets_to_test:
                try:
                    asset_time, asset_status, asset_success = self.measure_response_time(f"{self.base_url}{asset}")
                    if asset_success and asset_status == 200:
                        asset_times.append(asset_time)
                except:
                    pass  # Assets might not exist
            
            frontend_data = {
                "main_page_response_time": response_time,
                "main_page_status": status_code,
                "asset_response_times": asset_times,
                "avg_asset_time": statistics.mean(asset_times) if asset_times else 0
            }
            
            return len(issues) == 0, issues, frontend_data
            
        except Exception as e:
            return False, [f"Frontend performance test failed: {str(e)}"], {}

    def test_database_performance(self) -> Tuple[bool, List[str], Dict[str, Any]]:
        """Test database-related performance through API endpoints"""
        issues = []
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test endpoints that likely involve database operations
            db_endpoints = [
                "/api/v1/ml/predictions",
                "/api/v1/recommendations/personalized",
                "/api/v1/ml/realtime-predictions"
            ]
            
            db_performance = {}
            
            for endpoint in db_endpoints:
                success, endpoint_issues, perf_data = self.test_endpoint_performance(endpoint, iterations=3)
                
                if not success:
                    issues.extend([f"{endpoint}: {issue}" for issue in endpoint_issues])
                
                db_performance[endpoint] = perf_data
                
                # Check for database-specific performance issues
                if perf_data.get("avg_response_time", 0) > self.thresholds["acceptable_response"]:
                    issues.append(f"Database query too slow for {endpoint}: {perf_data['avg_response_time']:.1f}ms")
            
            return len(issues) == 0, issues, db_performance
            
        except Exception as e:
            return False, [f"Database performance test failed: {str(e)}"], {}

    def test_memory_and_resource_usage(self) -> Tuple[bool, List[str], Dict[str, Any]]:
        """Test for memory leaks and resource usage patterns"""
        issues = []
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Make repeated requests to check for memory leaks
            endpoint = "/api/v1/ml/predictions"
            url = f"{self.backend_url}{endpoint}"
            
            # Measure response times over many requests to detect degradation
            response_times = []
            batch_size = 10
            num_batches = 3
            
            for batch in range(num_batches):
                batch_times = []
                
                for i in range(batch_size):
                    response_time, status_code, success = self.measure_response_time(url, headers)
                    if success and status_code == 200:
                        batch_times.append(response_time)
                    time.sleep(0.05)  # Small delay
                
                if batch_times:
                    avg_batch_time = statistics.mean(batch_times)
                    response_times.append(avg_batch_time)
                    print(f"  📊 Batch {batch + 1} average: {avg_batch_time:.1f}ms")
                
                # Small delay between batches
                time.sleep(0.5)
            
            # Check for performance degradation over time
            if len(response_times) >= 2:
                first_batch = response_times[0]
                last_batch = response_times[-1]
                
                # Allow up to 50% degradation or 10ms increase (whichever is larger)
                # This accounts for normal variance in API response times
                degradation_threshold = max(first_batch * 1.5, first_batch + 10)
                if last_batch > degradation_threshold:
                    issues.append(f"Significant performance degradation detected: {first_batch:.1f}ms -> {last_batch:.1f}ms")
            
            resource_data = {
                "batch_response_times": response_times,
                "total_requests": num_batches * batch_size,
                "performance_trend": "stable" if len(issues) == 0 else "degrading"
            }
            
            return len(issues) == 0, issues, resource_data
            
        except Exception as e:
            return False, [f"Resource usage test failed: {str(e)}"], {}

    def run_performance_test(self, test_name: str, test_func) -> Dict[str, Any]:
        """Run a single performance test"""
        try:
            success, issues, data = test_func()
            return {
                "status": "PASS" if success else "FAIL",
                "issues": issues,
                "data": data
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "issues": [f"Test error: {str(e)}"],
                "data": {}
            }

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all performance tests"""
        print("🚀 Starting Performance Requirements and Loading States Tests...")
        
        if not self.authenticate():
            return {"error": "Authentication failed"}
        
        # Define all tests
        tests = [
            ("Frontend Performance", self.test_frontend_performance),
            ("Database Performance", self.test_database_performance),
            ("Memory and Resource Usage", self.test_memory_and_resource_usage),
            ("ML Predictions Performance", lambda: self.test_endpoint_performance("/api/v1/ml/predictions", iterations=5)),
            ("Recommendations Performance", lambda: self.test_endpoint_performance("/api/v1/recommendations/personalized", iterations=5)),
            ("Real-time Predictions Performance", lambda: self.test_endpoint_performance("/api/v1/ml/realtime-predictions", iterations=5)),
            ("Concurrent Load Test", lambda: self.test_concurrent_load("/api/v1/ml/predictions", concurrent_users=3, requests_per_user=2))
        ]
        
        test_results = {}
        
        try:
            for test_name, test_func in tests:
                print(f"🧪 Testing {test_name}...")
                result = self.run_performance_test(test_name, test_func)
                test_results[test_name] = result
                
                if result["status"] == "PASS":
                    print(f"  ✅ {test_name}: PASS")
                    # Print some performance metrics if available
                    data = result.get("data", {})
                    if "avg_response_time" in data:
                        print(f"     📊 Average response time: {data['avg_response_time']:.1f}ms")
                    if "success_rate" in data:
                        print(f"     📊 Success rate: {data['success_rate']:.1f}%")
                else:
                    print(f"  ❌ {test_name}: {result['status']}")
                    for issue in result["issues"]:
                        print(f"     ⚠️  {issue}")
            
            # Calculate summary
            total_tests = len(tests)
            passed_tests = len([t for t in test_results.values() if t["status"] == "PASS"])
            failed_tests = total_tests - passed_tests
            
            # Calculate overall performance metrics
            all_response_times = []
            for test_result in test_results.values():
                data = test_result.get("data", {})
                if "avg_response_time" in data:
                    all_response_times.append(data["avg_response_time"])
                elif "all_response_times" in data:
                    all_response_times.extend(data["all_response_times"])
            
            overall_avg_response = statistics.mean(all_response_times) if all_response_times else 0
            
            summary = {
                "timestamp": datetime.now().isoformat(),
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests / total_tests) * 100,
                "overall_status": "PASS" if passed_tests == total_tests else "FAIL",
                "overall_avg_response_time": overall_avg_response,
                "performance_thresholds": self.thresholds
            }
            
            final_results = {
                "summary": summary,
                "test_results": test_results
            }
            
            # Save detailed report
            with open("performance_report.json", "w") as f:
                json.dump(final_results, f, indent=2)
            
            # Print summary
            print(f"\n📊 Performance Test Summary:")
            print(f"   Total Tests: {total_tests}")
            print(f"   Passed: {passed_tests}")
            print(f"   Failed: {failed_tests}")
            print(f"   Success Rate: {summary['success_rate']:.1f}%")
            print(f"   Overall Average Response Time: {overall_avg_response:.1f}ms")
            print(f"   Overall Status: {summary['overall_status']}")
            print(f"\n📄 Detailed report saved to: performance_report.json")
            
            if summary['overall_status'] == 'PASS':
                print("🎉 All performance tests passed!")
            else:
                print("❌ Some performance tests failed. Check the report for details.")
            
            return final_results
            
        except Exception as e:
            return {"error": f"Test execution failed: {str(e)}"}


if __name__ == "__main__":
    tester = PerformanceTester()
    results = tester.run_all_tests()