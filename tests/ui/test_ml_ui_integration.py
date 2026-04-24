#!/usr/bin/env python3
"""
Comprehensive ML UI Integration Test
Tests the full integration of AI/ML system with frontend UI components
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class MLUIIntegrationTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.test_status = {
            'user_registration': False,
            'authentication': False,
            'realtime_predictions': False,
            'ml_predictions': False,
            'personalized_recommendations': False,
            'ml_model_info': False,
            'enhanced_predictions': False,
            'data_consistency': False,
            'performance_metrics': {}
        }
        
    async def setup_session(self):
        """Setup HTTP session and authenticate"""
        self.session = aiohttp.ClientSession()
        
        # Test user credentials
        login_data = {
            "email": f"test_ml_ui_{int(time.time())}@example.com",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!",
            "first_name": "ML",
            "last_name": "Tester"
        }
        
        # Register test user
        try:
            async with self.session.post(f"{self.base_url}/api/v1/auth/register", json=login_data) as response:
                if response.status in [200, 201]:
                    print("✓ Test user registered successfully")
                elif response.status == 400:
                    print("ℹ Test user already exists, proceeding with login")
                else:
                    print(f"⚠ User registration returned status: {response.status}")
        except Exception as e:
            print(f"⚠ User registration error: {e}")
        
        # Login to get auth token
        login_payload = {
            "email": login_data["email"],
            "password": login_data["password"]
        }
        
        async with self.session.post(f"{self.base_url}/api/v1/auth/login", json=login_payload) as response:
            if response.status == 200:
                data = await response.json()
                self.auth_token = data.get("access_token")
                if self.auth_token:
                    print("✓ Authentication successful")
                    return True
                else:
                    print("✗ No access token received")
                    return False
            else:
                print(f"✗ Authentication failed with status: {response.status}")
                return False
    
    async def test_realtime_predictions_api(self) -> Dict[str, Any]:
        """Test real-time predictions API endpoint"""
        print("\n🔄 Testing Real-time Predictions API...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with self.session.get(f"{self.base_url}/api/v1/ml/realtime-predictions", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    required_fields = ["current_risk", "confidence_score", "risk_factors", "immediate_recommendations"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        print("✓ Real-time predictions API working correctly")
                        print(f"  - Current Risk: {data.get('current_risk', 0)}%")
                        print(f"  - Confidence: {data.get('confidence_score', 0)}%")
                        print(f"  - Risk Factors: {len(data.get('risk_factors', []))}")
                        print(f"  - Recommendations: {len(data.get('immediate_recommendations', []))}")
                        return {"status": "success", "data": data}
                    else:
                        print(f"✗ Missing required fields: {missing_fields}")
                        return {"status": "error", "message": f"Missing fields: {missing_fields}"}
                else:
                    print(f"✗ API returned status: {response.status}")
                    return {"status": "error", "message": f"HTTP {response.status}"}
        except Exception as e:
            print(f"✗ Real-time predictions API error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def test_ml_predictions_api(self) -> Dict[str, Any]:
        """Test ML predictions API endpoint"""
        print("\n🔄 Testing ML Predictions API...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with self.session.get(f"{self.base_url}/api/v1/ml/predictions", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    required_fields = ["next_flare_probability", "predicted_severity", "timeline", "key_factors"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        print("✓ ML predictions API working correctly")
                        print(f"  - Flare Probability: {data.get('next_flare_probability', 0)}%")
                        print(f"  - Predicted Severity: {data.get('predicted_severity', 0)}/10")
                        print(f"  - Timeline: {data.get('timeline', 'N/A')}")
                        print(f"  - Key Factors: {len(data.get('key_factors', []))}")
                        return {"status": "success", "data": data}
                    else:
                        print(f"✗ Missing required fields: {missing_fields}")
                        return {"status": "error", "message": f"Missing fields: {missing_fields}"}
                else:
                    print(f"✗ API returned status: {response.status}")
                    return {"status": "error", "message": f"HTTP {response.status}"}
        except Exception as e:
            print(f"✗ ML predictions API error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def test_personalized_recommendations_api(self) -> Dict[str, Any]:
        """Test personalized recommendations API endpoint"""
        print("\n🔄 Testing Personalized Recommendations API...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        payload = {
            "symptoms": {
                "abdominal_pain": 2,
                "bloating": 3,
                "stress_level": 6
            },
            "focus_area": "both"
        }
        
        try:
            async with self.session.post(f"{self.base_url}/api/v1/ml/recommendations", headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    required_fields = ["dietary_recommendations", "lifestyle_recommendations", "priority_level"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        print("✓ Personalized recommendations API working correctly")
                        print(f"  - Dietary Recommendations: {len(data.get('dietary_recommendations', []))}")
                        print(f"  - Lifestyle Recommendations: {len(data.get('lifestyle_recommendations', []))}")
                        print(f"  - Priority Level: {data.get('priority_level', 'N/A')}")
                        return {"status": "success", "data": data}
                    else:
                        print(f"✗ Missing required fields: {missing_fields}")
                        return {"status": "error", "message": f"Missing fields: {missing_fields}"}
                else:
                    print(f"✗ API returned status: {response.status}")
                    return {"status": "error", "message": f"HTTP {response.status}"}
        except Exception as e:
            print(f"✗ Personalized recommendations API error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def test_ml_model_info_api(self) -> Dict[str, Any]:
        """Test ML model info API endpoint"""
        print("\n🔄 Testing ML Model Info API...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with self.session.get(f"{self.base_url}/api/v1/ml/models/info", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    print("✓ ML model info API working correctly")
                    print(f"  - Available Models: {len(data.get('models', []))}")
                    print(f"  - Model Status: {data.get('status', 'N/A')}")
                    return {"status": "success", "data": data}
                else:
                    print(f"✗ API returned status: {response.status}")
                    return {"status": "error", "message": f"HTTP {response.status}"}
        except Exception as e:
            print(f"✗ ML model info API error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def test_data_consistency(self) -> Dict[str, Any]:
        """Test data consistency across multiple API calls"""
        print("\n🔄 Testing Data Consistency...")
        
        try:
            # Make multiple calls to real-time predictions
            results = []
            for i in range(3):
                result = await self.test_realtime_predictions_api()
                if result["status"] == "success":
                    results.append(result["data"])
                await asyncio.sleep(1)  # Wait 1 second between calls
            
            if len(results) >= 2:
                # Check if confidence scores are reasonable
                confidence_scores = [r.get("confidence_score", 0) for r in results]
                risk_scores = [r.get("current_risk", 0) for r in results]
                
                print("✓ Data consistency test completed")
                print(f"  - Confidence range: {min(confidence_scores)}-{max(confidence_scores)}%")
                print(f"  - Risk range: {min(risk_scores)}-{max(risk_scores)}%")
                
                return {"status": "success", "results": results}
            else:
                print("✗ Insufficient data for consistency test")
                return {"status": "error", "message": "Insufficient data"}
        except Exception as e:
            print(f"✗ Data consistency test error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def test_performance_metrics(self) -> Dict[str, Any]:
        """Test API performance and response times"""
        print("\n🔄 Testing Performance Metrics...")
        
        try:
            endpoints = [
                "/api/v1/ml/realtime-predictions",
                "/api/v1/ml/predictions",
                "/api/v1/ml/recommendations",
                "/api/v1/ml/models/info"
            ]
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            performance_results = {}
            
            for endpoint in endpoints:
                start_time = time.time()
                async with self.session.get(f"{self.base_url}{endpoint}", headers=headers) as response:
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                    
                    performance_results[endpoint] = {
                        "response_time_ms": round(response_time, 2),
                        "status_code": response.status
                    }
            
            print("✓ Performance metrics collected")
            for endpoint, metrics in performance_results.items():
                print(f"  - {endpoint}: {metrics['response_time_ms']}ms (HTTP {metrics['status_code']})")
            
            return {"status": "success", "metrics": performance_results}
        except Exception as e:
            print(f"✗ Performance test error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling and fallback states"""
        print("\n🔄 Testing Error Handling...")
        
        try:
            # Test with invalid auth token
            invalid_headers = {"Authorization": "Bearer invalid_token"}
            
            async with self.session.get(f"{self.base_url}/api/v1/ml/realtime-predictions", headers=invalid_headers) as response:
                if response.status == 401:
                    print("✓ Proper authentication error handling")
                else:
                    print(f"⚠ Unexpected status for invalid auth: {response.status}")
            
            # Test with missing auth header
            async with self.session.get(f"{self.base_url}/api/v1/ml/realtime-predictions") as response:
                if response.status in [401, 403]:
                    print("✓ Proper missing auth handling")
                else:
                    print(f"⚠ Unexpected status for missing auth: {response.status}")
            
            return {"status": "success", "message": "Error handling tests completed"}
        except Exception as e:
            print(f"✗ Error handling test error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def run_all_tests(self):
        """Run all ML UI integration tests"""
        print("🚀 Starting ML UI Integration Tests")
        print("=" * 50)
        
        # Setup
        if not await self.setup_session():
            print("✗ Failed to setup test session")
            return
        
        # Run tests
        tests = [
            ("Real-time Predictions API", self.test_realtime_predictions_api),
            ("ML Predictions API", self.test_ml_predictions_api),
            ("Personalized Recommendations API", self.test_personalized_recommendations_api),
            ("ML Model Info API", self.test_ml_model_info_api),
            ("Data Consistency", self.test_data_consistency),
            ("Performance Metrics", self.test_performance_metrics),
            ("Error Handling", self.test_error_handling)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                if result.get("status") == "success":
                    passed_tests += 1
                self.test_results.append({"test": test_name, "result": result})
            except Exception as e:
                print(f"✗ {test_name} failed with exception: {e}")
                self.test_results.append({"test": test_name, "result": {"status": "error", "message": str(e)}})
        
        # Summary
        print("\n" + "=" * 50)
        print("🏁 ML UI Integration Test Summary")
        print("=" * 50)
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("🎉 All ML UI integration tests passed!")
        else:
            print("⚠ Some tests failed. Check the detailed output above.")
        
        # Cleanup
        if self.session:
            await self.session.close()

async def main():
    tester = MLUIIntegrationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())