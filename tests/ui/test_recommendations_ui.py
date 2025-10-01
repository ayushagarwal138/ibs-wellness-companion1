#!/usr/bin/env python3
"""
Personalized Recommendations UI Integration Test
Tests the recommendations component integration with the ML backend.
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class RecommendationsUITester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.session = None
        self.auth_token = None
        
    async def setup_session(self):
        """Setup HTTP session for testing."""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session."""
        if self.session:
            await self.session.close()
            
    async def authenticate_user(self):
        """Authenticate a test user."""
        print("🔐 Setting up authentication for recommendations test...")
        
        # Register test user
        register_data = {
            "email": f"test_rec_{int(time.time())}@example.com",
            "password": "TestPassword123!",
            "confirm_password": "TestPassword123!",
            "first_name": "Recommendations",
            "last_name": "Tester"
        }
        
        try:
            async with self.session.post(f"{self.base_url}/api/v1/auth/register", json=register_data) as response:
                if response.status == 201:
                    print("✓ Test user registered successfully")
                elif response.status == 400:
                    print("ℹ Test user already exists, proceeding with login")
        except Exception as e:
            print(f"⚠ Registration error: {e}")
        
        # Login
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        
        try:
            async with self.session.post(f"{self.base_url}/api/v1/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    print("✓ Authentication successful")
                    return True
                else:
                    print(f"✗ Login failed with status: {response.status}")
                    return False
        except Exception as e:
            print(f"✗ Login error: {e}")
            return False
    
    async def test_recommendations_endpoint(self):
        """Test the recommendations API endpoint with various payloads."""
        print("\n🎯 Testing Recommendations API Endpoint...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        test_cases = [
            {
                "name": "Basic symptoms",
                "payload": {
                    "symptoms": {
                        "abdominal_pain": 7,
                        "bloating": 6,
                        "diarrhea": 5
                    },
                    "focus_area": "dietary"
                }
            },
            {
                "name": "Lifestyle focus",
                "payload": {
                    "symptoms": {
                        "constipation": 8,
                        "gas": 6,
                        "fatigue": 7
                    },
                    "focus_area": "lifestyle"
                }
            },
            {
                "name": "General recommendations",
                "payload": {
                    "symptoms": {
                        "nausea": 5,
                        "cramping": 6
                    },
                    "focus_area": "general"
                }
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            try:
                async with self.session.post(
                    f"{self.base_url}/api/v1/ml/recommendations", 
                    headers=headers,
                    json=test_case["payload"]
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        results.append({
                            "test_case": test_case["name"],
                            "success": True,
                            "response": data,
                            "status_code": response.status
                        })
                        print(f"  ✓ {test_case['name']}: Success")
                        
                        # Validate response structure
                        diet_recs = data.get("diet_recommendations", [])
                        lifestyle_recs = data.get("lifestyle_recommendations", [])
                        total_recs = len(diet_recs) + len(lifestyle_recs)
                        
                        if diet_recs:
                            print(f"    - Found {len(diet_recs)} diet recommendations")
                        if lifestyle_recs:
                            print(f"    - Found {len(lifestyle_recs)} lifestyle recommendations")
                        if "diet_score" in data:
                            print(f"    - Diet score: {data['diet_score']}")
                        if "lifestyle_score" in data:
                            print(f"    - Lifestyle score: {data['lifestyle_score']}")
                            
                    else:
                        results.append({
                            "test_case": test_case["name"],
                            "success": False,
                            "status_code": response.status,
                            "error": await response.text()
                        })
                        print(f"  ✗ {test_case['name']}: Failed with status {response.status}")
                        
            except Exception as e:
                results.append({
                    "test_case": test_case["name"],
                    "success": False,
                    "error": str(e)
                })
                print(f"  ✗ {test_case['name']}: Error - {e}")
        
        return results
    
    async def test_recommendations_data_quality(self):
        """Test the quality and consistency of recommendations data."""
        print("\n📊 Testing Recommendations Data Quality...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        payload = {
            "symptoms": {
                "abdominal_pain": 8,
                "bloating": 7,
                "diarrhea": 6,
                "gas": 5
            },
            "focus_area": "dietary"
        }
        
        quality_metrics = {
            "consistency": False,
            "completeness": False,
            "relevance": False,
            "personalization": False
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/ml/recommendations", 
                headers=headers,
                json=payload
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Check data completeness
                    diet_recs = data.get("diet_recommendations", [])
                    lifestyle_recs = data.get("lifestyle_recommendations", [])
                    total_recs = len(diet_recs) + len(lifestyle_recs)
                    
                    if total_recs > 0:
                        quality_metrics["completeness"] = True
                        print(f"  ✓ Recommendations data is complete ({total_recs} total recommendations)")
                    
                    # Check for scoring system
                    if "diet_score" in data and "lifestyle_score" in data:
                        quality_metrics["consistency"] = True
                        print(f"  ✓ Scoring system present: Diet={data['diet_score']}, Lifestyle={data['lifestyle_score']}")
                    
                    # Check recommendation relevance (should contain dietary advice for dietary focus)
                    recommendations_text = str(data.get("diet_recommendations", "")).lower()
                    if any(keyword in recommendations_text for keyword in ["food", "diet", "eat", "avoid", "meal", "dairy", "wheat"]):
                        quality_metrics["relevance"] = True
                        print("  ✓ Recommendations are relevant to focus area")
                    
                    # Check for personalization (recommendations should vary based on symptoms)
                    if total_recs >= 3:
                        quality_metrics["personalization"] = True
                        print("  ✓ Sufficient personalized recommendations provided")
                    
                    # Show sample recommendations
                    if diet_recs:
                        print(f"  📋 Sample diet recommendation: {diet_recs[0].get('recommendation', 'N/A')[:100]}...")
                    if lifestyle_recs:
                        print(f"  📋 Sample lifestyle recommendation: {lifestyle_recs[0].get('recommendation', 'N/A')[:100]}...")
                    
                else:
                    print(f"  ✗ Failed to get recommendations: {response.status}")
                    
        except Exception as e:
            print(f"  ✗ Data quality test error: {e}")
        
        return quality_metrics
    
    async def test_recommendations_performance(self):
        """Test the performance of recommendations endpoint."""
        print("\n⚡ Testing Recommendations Performance...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        payload = {
            "symptoms": {
                "abdominal_pain": 6,
                "bloating": 5
            },
            "focus_area": "lifestyle"
        }
        
        response_times = []
        
        for i in range(5):
            try:
                start_time = time.time()
                async with self.session.post(
                    f"{self.base_url}/api/v1/ml/recommendations", 
                    headers=headers,
                    json=payload
                ) as response:
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000  # Convert to ms
                    
                    if response.status == 200:
                        response_times.append(response_time)
                        print(f"  Call {i+1}: {response_time:.2f}ms")
                    else:
                        print(f"  Call {i+1}: Failed with status {response.status}")
                        
            except Exception as e:
                print(f"  Call {i+1}: Error - {e}")
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            
            print(f"  📈 Performance Summary:")
            print(f"    - Average: {avg_time:.2f}ms")
            print(f"    - Min: {min_time:.2f}ms")
            print(f"    - Max: {max_time:.2f}ms")
            
            performance_rating = "Excellent" if avg_time < 100 else "Good" if avg_time < 500 else "Needs Improvement"
            print(f"    - Rating: {performance_rating}")
            
            return {
                "average_ms": avg_time,
                "min_ms": min_time,
                "max_ms": max_time,
                "rating": performance_rating,
                "successful_calls": len(response_times)
            }
        else:
            print("  ✗ No successful performance measurements")
            return None
    
    async def generate_recommendations_report(self, endpoint_results, quality_metrics, performance_data):
        """Generate a comprehensive recommendations test report."""
        print("\n" + "="*60)
        print("🎯 Personalized Recommendations UI Integration Report")
        print("="*60)
        
        # Endpoint Tests
        successful_tests = sum(1 for result in endpoint_results if result["success"])
        total_tests = len(endpoint_results)
        print(f"\n🔗 API Endpoint Tests: {successful_tests}/{total_tests} passed")
        
        for result in endpoint_results:
            status = "✓" if result["success"] else "✗"
            print(f"  {status} {result['test_case']}")
        
        # Data Quality
        quality_passed = sum(quality_metrics.values())
        quality_total = len(quality_metrics)
        print(f"\n📊 Data Quality Tests: {quality_passed}/{quality_total} passed")
        
        for metric, passed in quality_metrics.items():
            status = "✓" if passed else "✗"
            print(f"  {status} {metric.replace('_', ' ').title()}")
        
        # Performance
        if performance_data:
            print(f"\n⚡ Performance Tests:")
            print(f"  Average Response Time: {performance_data['average_ms']:.2f}ms")
            print(f"  Performance Rating: {performance_data['rating']}")
        
        # Overall Assessment
        total_checks = total_tests + quality_total + (1 if performance_data else 0)
        total_passed = successful_tests + quality_passed + (1 if performance_data and performance_data['average_ms'] < 500 else 0)
        success_rate = (total_passed / total_checks) * 100
        
        print(f"\n🎯 Overall Assessment:")
        print(f"  Tests Passed: {total_passed}/{total_checks}")
        print(f"  Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("  Status: ✅ EXCELLENT - Recommendations integration is working optimally")
        elif success_rate >= 75:
            print("  Status: ✅ GOOD - Recommendations integration is working well")
        elif success_rate >= 60:
            print("  Status: ⚠️ FAIR - Recommendations integration has some issues")
        else:
            print("  Status: ❌ POOR - Recommendations integration needs significant work")
        
        return {
            'success_rate': success_rate,
            'endpoint_results': endpoint_results,
            'quality_metrics': quality_metrics,
            'performance_data': performance_data
        }

async def main():
    """Main test execution function."""
    print("🚀 Starting Personalized Recommendations UI Integration Test")
    print("="*60)
    
    tester = RecommendationsUITester()
    
    try:
        await tester.setup_session()
        
        # Authenticate
        if not await tester.authenticate_user():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
        
        # Run tests
        endpoint_results = await tester.test_recommendations_endpoint()
        quality_metrics = await tester.test_recommendations_data_quality()
        performance_data = await tester.test_recommendations_performance()
        
        # Generate report
        report = await tester.generate_recommendations_report(
            endpoint_results, quality_metrics, performance_data
        )
        
        # Save report to file
        with open('recommendations_ui_test_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: recommendations_ui_test_report.json")
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
    finally:
        await tester.cleanup_session()

if __name__ == "__main__":
    asyncio.run(main())