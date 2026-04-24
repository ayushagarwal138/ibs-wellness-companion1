#!/usr/bin/env python3
"""
End-to-End ML Integration Test

Tests the complete ML workflow from frontend API calls to database storage.
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any
import httpx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

class E2EMLTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []
        self.test_user_email = f"test_ml_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
        self.test_user_password = "TestPass123!"
        self.auth_token = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data: Dict = None):
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {details}")
    
    async def setup_test_user(self) -> bool:
        """Create or verify test user exists."""
        try:
            # Try to create test user
            user_data = {
                "email": self.test_user_email,
                "password": "TestPass123!",
                "confirm_password": "TestPass123!",
                "first_name": "Test",
                "last_name": "User",
                "date_of_birth": "1990-01-01"
            }
            self.test_user_password = "TestPass123!"
            
            response = await self.client.post(f"{API_BASE}/auth/register", json=user_data)
            
            if response.status_code == 201:
                self.log_test_result("User Setup", True, "Test user created successfully")
                return True
            elif response.status_code == 400 and "already registered" in response.text:
                self.log_test_result("User Setup", True, "Test user already exists")
                return True
            else:
                self.log_test_result("User Setup", False, f"Failed to create user: {response.text}")
                return False
                
        except Exception as e:
            self.log_test_result("User Setup", False, f"Error setting up user: {str(e)}")
            return False
    
    async def authenticate(self) -> bool:
        """Authenticate and get access token."""
        try:
            auth_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            response = await self.client.post(f"{API_BASE}/auth/login", json=auth_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                if self.auth_token:
                    self.log_test_result("Authentication", True, "Successfully authenticated")
                    return True
                else:
                    self.log_test_result("Authentication", False, "No access token in response")
                    return False
            else:
                self.log_test_result("Authentication", False, f"Auth failed: {response.text}")
                return False
                
        except Exception as e:
            self.log_test_result("Authentication", False, f"Error authenticating: {str(e)}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        return {"Authorization": f"Bearer {self.auth_token}"}
    
    async def test_ml_predictions_endpoint(self) -> bool:
        """Test ML predictions endpoint."""
        try:
            headers = self.get_auth_headers()
            params = {
                "timeframe": "week",
                "include_recommendations": "true"
            }
            
            response = await self.client.get(
                f"{API_BASE}/ml/predictions",
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["risk_level", "confidence", "next_flare_probability"]
                
                if all(field in data for field in required_fields):
                    self.log_test_result(
                        "ML Predictions Endpoint", 
                        True, 
                        f"Predictions received: {data['risk_level']} risk",
                        data
                    )
                    return True
                else:
                    self.log_test_result(
                        "ML Predictions Endpoint", 
                        False, 
                        f"Missing required fields in response: {data}"
                    )
                    return False
            else:
                self.log_test_result(
                    "ML Predictions Endpoint", 
                    False, 
                    f"Request failed: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("ML Predictions Endpoint", False, f"Error: {str(e)}")
            return False
    
    async def test_realtime_predictions_endpoint(self) -> bool:
        """Test real-time predictions endpoint."""
        try:
            headers = self.get_auth_headers()
            
            response = await self.client.get(
                f"{API_BASE}/ml/realtime-predictions",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["current_risk", "confidence_score"]
                
                if all(field in data for field in required_fields):
                    self.log_test_result(
                        "Real-time Predictions Endpoint", 
                        True, 
                        f"Real-time data received: {data['current_risk']} risk",
                        data
                    )
                    return True
                else:
                    self.log_test_result(
                        "Real-time Predictions Endpoint", 
                        False, 
                        f"Missing required fields in response: {data}"
                    )
                    return False
            else:
                self.log_test_result(
                    "Real-time Predictions Endpoint", 
                    False, 
                    f"Request failed: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("Real-time Predictions Endpoint", False, f"Error: {str(e)}")
            return False
    
    async def test_personalized_recommendations_endpoint(self) -> bool:
        """Test personalized recommendations endpoint."""
        try:
            headers = self.get_auth_headers()
            
            response = await self.client.get(
                f"{API_BASE}/recommendations/personalized",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["dietary_recommendations", "lifestyle_insights"]
                
                if all(field in data for field in required_fields):
                    self.log_test_result(
                        "Personalized Recommendations Endpoint", 
                        True, 
                        f"Recommendations received: {len(data.get('dietary_recommendations', []))} dietary, {len(data.get('lifestyle_insights', []))} lifestyle",
                        data
                    )
                    return True
                else:
                    self.log_test_result(
                        "Personalized Recommendations Endpoint", 
                        False, 
                        f"Missing required fields in response: {data}"
                    )
                    return False
            else:
                self.log_test_result(
                    "Personalized Recommendations Endpoint", 
                    False, 
                    f"Request failed: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("Personalized Recommendations Endpoint", False, f"Error: {str(e)}")
            return False
    
    async def test_model_info_endpoint(self) -> bool:
        """Test ML model info endpoint."""
        try:
            headers = self.get_auth_headers()
            
            response = await self.client.get(
                f"{API_BASE}/ml/models/info",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["models_loaded", "model_versions"]
                
                if all(field in data for field in required_fields):
                    self.log_test_result(
                        "Model Info Endpoint", 
                        True, 
                        f"Model info received: {len(data.get('models_loaded', {}))} models",
                        data
                    )
                    return True
                else:
                    self.log_test_result(
                        "Model Info Endpoint", 
                        False, 
                        f"Missing required fields in response: {data}"
                    )
                    return False
            else:
                self.log_test_result(
                    "Model Info Endpoint", 
                    False, 
                    f"Request failed: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("Model Info Endpoint", False, f"Error: {str(e)}")
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all end-to-end tests."""
        logger.info("🚀 Starting End-to-End ML Integration Tests")
        logger.info("=" * 50)
        
        # Setup phase
        if not await self.setup_test_user():
            return False
        
        if not await self.authenticate():
            return False
        
        # API endpoint tests
        tests = [
            self.test_ml_predictions_endpoint(),
            self.test_realtime_predictions_endpoint(),
            self.test_personalized_recommendations_endpoint(),
            self.test_model_info_endpoint()
        ]
        
        api_results = await asyncio.gather(*tests, return_exceptions=True)
        
        # Calculate results
        passed_tests = sum(1 for result in api_results if result is True)
        total_tests = len(api_results)
        
        logger.info("=" * 50)
        logger.info(f"📊 Test Summary: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            logger.info("🎉 All end-to-end tests passed!")
            return True
        else:
            logger.info("❌ Some tests failed. Check the logs above.")
            return False
    
    def save_test_report(self, filename: str = "e2e_ml_test_report.json"):
        """Save test results to file."""
        report = {
            "test_run": datetime.now().isoformat(),
            "total_tests": len(self.test_results),
            "passed_tests": sum(1 for r in self.test_results if r["success"]),
            "results": self.test_results
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Test report saved to {filename}")

async def main():
    """Main test runner."""
    async with E2EMLTester() as tester:
        success = await tester.run_all_tests()
        tester.save_test_report()
        
        if success:
            logger.info("✅ End-to-End ML Integration is working correctly!")
            sys.exit(0)
        else:
            logger.error("❌ End-to-End ML Integration has issues!")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())