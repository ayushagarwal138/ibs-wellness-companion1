#!/usr/bin/env python3
"""
ML Integration Test Script

Tests the ML prediction endpoints with sample data to verify functionality.
Run this script to validate that the ML integration is working correctly.
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List
import httpx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Sample test data
SAMPLE_USER_CREDENTIALS = {
    "email": "john.doe@example.com",
    "password": "SecurePassword123!",
}

SAMPLE_SYMPTOMS = {
    "abdominal_pain": 2,
    "bloating": 3,
    "gas": 1,
    "diarrhea": 2,
    "constipation": 0,
    "urgency": 2,
    "incomplete_evacuation": 1,
    "nausea": 1,
    "fatigue": 2,
    "mood_score": 4,
    "stress_level": 7,
    "sleep_quality": 3,
}


class MLIntegrationTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.auth_token = None
        self.test_results = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def log_test_result(
        self,
        test_name: str,
        success: bool,
        details: str = "",
        response_data: Dict = None,
    ):
        """Log test result for summary."""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data,
        }
        self.test_results.append(result)

        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {details}")

    async def test_server_health(self) -> bool:
        """Test if the server is running and healthy."""
        try:
            response = await self.client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                self.log_test_result("Server Health Check", True, "Server is running")
                return True
            else:
                self.log_test_result(
                    "Server Health Check", False, f"Status code: {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_test_result(
                "Server Health Check", False, f"Connection error: {str(e)}"
            )
            return False

    async def authenticate_user(self) -> bool:
        """Authenticate test user and get auth token."""
        try:
            # First try to register the user (in case they don't exist)
            register_data = {
                "email": SAMPLE_USER_CREDENTIALS["email"],
                "password": SAMPLE_USER_CREDENTIALS["password"],
                "confirm_password": SAMPLE_USER_CREDENTIALS["password"],
                "first_name": "John",
                "last_name": "Doe",
            }

            # Try to register (ignore if user already exists)
            register_response = await self.client.post(
                f"{API_BASE}/auth/register",
                json=register_data,
                headers={"Content-Type": "application/json"},
            )

            # Now try to login with existing user
            login_data = {
                "email": SAMPLE_USER_CREDENTIALS["email"],
                "password": SAMPLE_USER_CREDENTIALS["password"],
            }

            response = await self.client.post(
                f"{API_BASE}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data.get("access_token")
                self.log_test_result(
                    "User Authentication", True, "Successfully authenticated"
                )
                return True
            else:
                self.log_test_result(
                    "User Authentication",
                    False,
                    f"Login failed: {response.status_code}",
                )
                return False

        except Exception as e:
            self.log_test_result(
                "User Authentication", False, f"Authentication error: {str(e)}"
            )
            return False

    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}

    async def test_model_info_endpoint(self) -> bool:
        """Test the ML model info endpoint."""
        try:
            response = await self.client.get(
                f"{API_BASE}/ml/models/info", headers=self.get_auth_headers()
            )

            if response.status_code == 200:
                data = response.json()
                self.log_test_result(
                    "Model Info Endpoint",
                    True,
                    f"Retrieved model info with {len(data.get('models_loaded', {}))} models",
                    data,
                )
                return True
            else:
                self.log_test_result(
                    "Model Info Endpoint", False, f"Status code: {response.status_code}"
                )
                return False

        except Exception as e:
            self.log_test_result("Model Info Endpoint", False, f"Error: {str(e)}")
            return False

    async def test_severity_prediction(self) -> bool:
        """Test severity prediction endpoint."""
        try:
            request_data = {"symptoms": SAMPLE_SYMPTOMS}

            response = await self.client.post(
                f"{API_BASE}/ml/predict/severity",
                json=request_data,
                headers=self.get_auth_headers(),
            )

            if response.status_code == 200:
                data = response.json()
                severity_score = data.get("severity_score", 0)
                severity_level = data.get("severity_level", "unknown")
                confidence = data.get("confidence", 0)

                self.log_test_result(
                    "Severity Prediction",
                    True,
                    f"Predicted severity: {severity_level} (score: {severity_score:.2f}, confidence: {confidence:.2f})",
                    data,
                )
                return True
            else:
                error_detail = response.text
                self.log_test_result(
                    "Severity Prediction",
                    False,
                    f"Status: {response.status_code}, Error: {error_detail}",
                )
                return False

        except Exception as e:
            self.log_test_result("Severity Prediction", False, f"Error: {str(e)}")
            return False

    async def test_flareup_prediction(self) -> bool:
        """Test flareup prediction endpoint."""
        try:
            request_data = {"days_ahead": 7, "symptoms": SAMPLE_SYMPTOMS}

            response = await self.client.post(
                f"{API_BASE}/ml/predict/flareup",
                json=request_data,
                headers=self.get_auth_headers(),
            )

            if response.status_code == 200:
                data = response.json()
                risk_score = data.get("risk_score", 0)
                risk_level = data.get("risk_level", "unknown")
                confidence = data.get("confidence", 0)

                self.log_test_result(
                    "Flareup Prediction",
                    True,
                    f"Predicted risk: {risk_level} (score: {risk_score:.2f}, confidence: {confidence:.2f})",
                    data,
                )
                return True
            else:
                error_detail = response.text
                self.log_test_result(
                    "Flareup Prediction",
                    False,
                    f"Status: {response.status_code}, Error: {error_detail}",
                )
                return False

        except Exception as e:
            self.log_test_result("Flareup Prediction", False, f"Error: {str(e)}")
            return False

    async def test_recommendations_endpoint(self) -> bool:
        """Test recommendations endpoint."""
        try:
            request_data = {"symptoms": SAMPLE_SYMPTOMS, "focus_area": "both"}

            response = await self.client.post(
                f"{API_BASE}/ml/recommendations",
                json=request_data,
                headers=self.get_auth_headers(),
            )

            if response.status_code == 200:
                data = response.json()
                diet_recs = len(data.get("diet_recommendations", []))
                lifestyle_recs = len(data.get("lifestyle_recommendations", []))
                diet_score = data.get("diet_score", 0)
                lifestyle_score = data.get("lifestyle_score", 0)

                self.log_test_result(
                    "Recommendations Endpoint",
                    True,
                    f"Generated {diet_recs} diet and {lifestyle_recs} lifestyle recommendations (scores: {diet_score:.1f}, {lifestyle_score:.1f})",
                    data,
                )
                return True
            else:
                error_detail = response.text
                self.log_test_result(
                    "Recommendations Endpoint",
                    False,
                    f"Status: {response.status_code}, Error: {error_detail}",
                )
                return False

        except Exception as e:
            self.log_test_result("Recommendations Endpoint", False, f"Error: {str(e)}")
            return False

    async def test_model_reload_endpoint(self) -> bool:
        """Test model reload endpoint."""
        try:
            response = await self.client.post(
                f"{API_BASE}/ml/models/reload", headers=self.get_auth_headers()
            )

            if response.status_code == 200:
                data = response.json()
                self.log_test_result(
                    "Model Reload Endpoint",
                    True,
                    f"Models reloaded: {data.get('message', 'Success')}",
                    data,
                )
                return True
            else:
                error_detail = response.text
                self.log_test_result(
                    "Model Reload Endpoint",
                    False,
                    f"Status: {response.status_code}, Error: {error_detail}",
                )
                return False

        except Exception as e:
            self.log_test_result("Model Reload Endpoint", False, f"Error: {str(e)}")
            return False

    async def test_edge_cases(self) -> bool:
        """Test edge cases and error handling."""
        success_count = 0
        total_tests = 0

        # Test with missing symptoms data
        total_tests += 1
        try:
            response = await self.client.post(
                f"{API_BASE}/ml/predict/severity",
                json={},  # Empty request
                headers=self.get_auth_headers(),
            )

            if response.status_code in [
                200,
                422,
            ]:  # Accept both success and validation error
                success_count += 1
                self.log_test_result(
                    "Edge Case - Empty Symptoms",
                    True,
                    f"Handled gracefully (status: {response.status_code})",
                )
            else:
                self.log_test_result(
                    "Edge Case - Empty Symptoms",
                    False,
                    f"Unexpected status: {response.status_code}",
                )
        except Exception as e:
            self.log_test_result(
                "Edge Case - Empty Symptoms", False, f"Error: {str(e)}"
            )

        # Test with invalid days_ahead parameter
        total_tests += 1
        try:
            response = await self.client.post(
                f"{API_BASE}/ml/predict/flareup",
                json={
                    "days_ahead": 100,
                    "symptoms": SAMPLE_SYMPTOMS,
                },  # Invalid days_ahead
                headers=self.get_auth_headers(),
            )

            if response.status_code in [
                200,
                422,
            ]:  # Accept both success and validation error
                success_count += 1
                self.log_test_result(
                    "Edge Case - Invalid Days Ahead",
                    True,
                    f"Handled gracefully (status: {response.status_code})",
                )
            else:
                self.log_test_result(
                    "Edge Case - Invalid Days Ahead",
                    False,
                    f"Unexpected status: {response.status_code}",
                )
        except Exception as e:
            self.log_test_result(
                "Edge Case - Invalid Days Ahead", False, f"Error: {str(e)}"
            )

        # Test without authentication
        total_tests += 1
        try:
            response = await self.client.get(
                f"{API_BASE}/ml/models/info"
            )  # No auth headers

            if response.status_code in [401, 403]:  # Should require authentication
                success_count += 1
                self.log_test_result(
                    "Edge Case - No Authentication",
                    True,
                    f"Properly rejected (status: {response.status_code})",
                )
            else:
                self.log_test_result(
                    "Edge Case - No Authentication",
                    False,
                    f"Should require auth (status: {response.status_code})",
                )
        except Exception as e:
            self.log_test_result(
                "Edge Case - No Authentication", False, f"Error: {str(e)}"
            )

        return success_count == total_tests

    async def run_all_tests(self) -> bool:
        """Run all ML integration tests."""
        logger.info("🚀 Starting ML Integration Tests")
        logger.info("=" * 50)

        # Test server health first
        if not await self.test_server_health():
            logger.error(
                "❌ Server is not running. Please start the backend server first."
            )
            return False

        # Authenticate user
        if not await self.authenticate_user():
            logger.error("❌ Authentication failed. Please check user credentials.")
            return False

        # Run ML endpoint tests
        tests = [
            self.test_model_info_endpoint,
            self.test_severity_prediction,
            self.test_flareup_prediction,
            self.test_recommendations_endpoint,
            self.test_model_reload_endpoint,
            self.test_edge_cases,
        ]

        passed_tests = 0
        total_tests = len(tests)

        for test in tests:
            if await test():
                passed_tests += 1

        # Print summary
        logger.info("=" * 50)
        logger.info(f"📊 Test Summary: {passed_tests}/{total_tests} tests passed")

        if passed_tests == total_tests:
            logger.info("🎉 All ML integration tests passed!")
            return True
        else:
            logger.error(f"❌ {total_tests - passed_tests} tests failed")
            return False

    def save_test_report(self, filename: str = "ml_integration_test_report.json"):
        """Save detailed test report to file."""
        report = {
            "test_run_timestamp": datetime.now().isoformat(),
            "total_tests": len(self.test_results),
            "passed_tests": sum(1 for r in self.test_results if r["success"]),
            "failed_tests": sum(1 for r in self.test_results if not r["success"]),
            "test_results": self.test_results,
        }

        with open(filename, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"📄 Test report saved to {filename}")


async def main():
    """Main test runner."""
    async with MLIntegrationTester() as tester:
        success = await tester.run_all_tests()
        tester.save_test_report()

        if success:
            logger.info("✅ ML Integration is working correctly!")
            sys.exit(0)
        else:
            logger.error("❌ ML Integration has issues that need to be addressed.")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
