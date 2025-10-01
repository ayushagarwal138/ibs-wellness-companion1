#!/usr/bin/env python3
"""
Profile Integration Test Script

Tests the complete profile management flow including:
- User authentication
- Profile data validation
- Profile updates
- Data synchronization
- ML integration
"""

import asyncio
import json
import sys
import uuid
from datetime import datetime, date
from typing import Dict, Any, Optional
import httpx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

class ProfileIntegrationTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.auth_token = None
        self.test_user_id = None
        self.test_results = []
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def log_test_result(self, test_name: str, passed: bool, message: str, data: Optional[Dict] = None):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status} {test_name}: {message}")
        
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "message": message,
            "data": data
        })
        
        if data and passed:
            logger.debug(f"Response data: {json.dumps(data, indent=2, default=str)}")
    
    async def test_server_health(self) -> bool:
        """Test server health."""
        try:
            response = await self.client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                self.log_test_result("Server Health", True, "Backend server is running")
                return True
            else:
                self.log_test_result("Server Health", False, f"Health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("Server Health", False, f"Cannot connect to server: {str(e)}")
            return False
    
    async def create_test_user(self) -> bool:
        """Create a test user for profile testing."""
        try:
            # Generate unique test user
            test_email = f"profile_test_{uuid.uuid4().hex[:8]}@example.com"
            test_password = "TestPassword123!"
            
            user_data = {
                "email": test_email,
                "password": test_password,
                "confirm_password": test_password,
                "first_name": "Profile",
                "last_name": "Tester"
            }
            
            response = await self.client.post(
                f"{API_BASE}/auth/register",
                json=user_data
            )
            
            if response.status_code == 201:
                data = response.json()
                self.test_user_id = data.get("user", {}).get("id")
                self.log_test_result("User Creation", True, f"Created test user: {test_email}")
                
                # Now login to get auth token
                login_response = await self.client.post(
                    f"{API_BASE}/auth/login",
                    json={"email": test_email, "password": test_password}
                )
                
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    self.auth_token = login_data.get("access_token")
                    self.log_test_result("User Authentication", True, "Successfully authenticated test user")
                    return True
                else:
                    self.log_test_result("User Authentication", False, f"Login failed: {login_response.status_code}")
                    return False
            else:
                self.log_test_result("User Creation", False, f"Registration failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test_result("User Creation", False, f"Error creating test user: {str(e)}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}
    
    async def test_profile_retrieval(self) -> bool:
        """Test profile retrieval."""
        try:
            response = await self.client.get(
                f"{API_BASE}/profile",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test_result(
                    "Profile Retrieval", 
                    True, 
                    f"Retrieved profile for user: {data.get('email', 'Unknown')}",
                    data
                )
                return True
            else:
                self.log_test_result("Profile Retrieval", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test_result("Profile Retrieval", False, f"Error: {str(e)}")
            return False
    
    async def test_profile_update_basic(self) -> bool:
        """Test basic profile update."""
        try:
            update_data = {
                "first_name": "Updated",
                "last_name": "Profile",
                "phone_number": "+1234567890",
                "date_of_birth": "1990-01-01",
                "gender": "MALE",
                "height_cm": 175,
                "weight_kg": 70
            }
            
            response = await self.client.patch(
                f"{API_BASE}/users/profile",
                json=update_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test_result(
                    "Basic Profile Update", 
                    True, 
                    f"Updated profile: {data.get('first_name')} {data.get('last_name')}",
                    data
                )
                return True
            else:
                error_detail = response.text
                self.log_test_result("Basic Profile Update", False, f"Status: {response.status_code}, Error: {error_detail}")
                return False
                
        except Exception as e:
            self.log_test_result("Basic Profile Update", False, f"Error: {str(e)}")
            return False
    
    async def test_profile_update_medical(self) -> bool:
        """Test medical profile update."""
        try:
            update_data = {
                "ibs_type": "IBS_D",
                "diagnosis_date": "2020-01-01",
                "medical_notes": "Test medical notes for profile validation"
            }
            
            response = await self.client.patch(
                f"{API_BASE}/users/profile",
                json=update_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test_result(
                    "Medical Profile Update", 
                    True, 
                    f"Updated medical info: IBS type {data.get('ibs_type', 'Unknown')}",
                    data
                )
                return True
            else:
                error_detail = response.text
                self.log_test_result("Medical Profile Update", False, f"Status: {response.status_code}, Error: {error_detail}")
                return False
                
        except Exception as e:
            self.log_test_result("Medical Profile Update", False, f"Error: {str(e)}")
            return False
    
    async def test_profile_sync(self) -> bool:
        """Test profile synchronization endpoint."""
        try:
            sync_data = {
                "first_name": "Synced",
                "last_name": "User",
                "height_cm": 180,
                "weight_kg": 75,
                "ibs_type": "IBS_C",
                "diagnosis_date": "2021-06-01"
            }
            
            response = await self.client.post(
                f"{API_BASE}/sync/sync-profile",
                json=sync_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test_result(
                    "Profile Sync", 
                    True, 
                    f"Synced profile successfully. Completion: {data.get('completion_percentage', 0)}%",
                    data
                )
                return True
            else:
                error_detail = response.text
                self.log_test_result("Profile Sync", False, f"Status: {response.status_code}, Error: {error_detail}")
                return False
                
        except Exception as e:
            self.log_test_result("Profile Sync", False, f"Error: {str(e)}")
            return False
    
    async def test_profile_validation_errors(self) -> bool:
        """Test profile validation with invalid data."""
        try:
            invalid_data = {
                "email": "invalid-email",  # Invalid email format
                "height_cm": 50,  # Too low
                "weight_kg": 500,  # Too high
                "date_of_birth": "2030-01-01"  # Future date
            }
            
            response = await self.client.patch(
                f"{API_BASE}/users/profile",
                json=invalid_data,
                headers=self.get_auth_headers()
            )
            
            # We expect this to fail with validation errors
            if response.status_code == 422:  # Validation error
                data = response.json()
                self.log_test_result(
                    "Profile Validation Errors", 
                    True, 
                    f"Correctly rejected invalid data with {len(data.get('detail', []))} validation errors",
                    data
                )
                return True
            elif response.status_code == 400:  # Bad request
                self.log_test_result(
                    "Profile Validation Errors", 
                    True, 
                    "Correctly rejected invalid data with bad request",
                    response.json()
                )
                return True
            else:
                self.log_test_result("Profile Validation Errors", False, f"Expected validation error, got: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test_result("Profile Validation Errors", False, f"Error: {str(e)}")
            return False
    
    async def test_ml_integration(self) -> bool:
        """Test ML integration with profile data."""
        try:
            # First ensure we have a complete profile
            await self.test_profile_update_basic()
            await self.test_profile_update_medical()
            
            # Test ML recommendations
            ml_request = {
                "symptoms": {
                    "abdominal_pain": 3,
                    "bloating": 4,
                    "gas": 2,
                    "diarrhea": 3,
                    "constipation": 0,
                    "urgency": 3,
                    "incomplete_evacuation": 2,
                    "nausea": 1,
                    "fatigue": 3,
                    "mood_score": 3,
                    "stress_level": 6,
                    "sleep_quality": 2
                },
                "focus_area": "both"
            }
            
            response = await self.client.post(
                f"{API_BASE}/ml/recommendations",
                json=ml_request,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                diet_recs = len(data.get("diet_recommendations", []))
                lifestyle_recs = len(data.get("lifestyle_recommendations", []))
                
                self.log_test_result(
                    "ML Integration", 
                    True, 
                    f"Generated {diet_recs} diet and {lifestyle_recs} lifestyle recommendations",
                    data
                )
                return True
            else:
                self.log_test_result("ML Integration", False, f"ML request failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test_result("ML Integration", False, f"Error: {str(e)}")
            return False
    
    async def cleanup_test_user(self) -> bool:
        """Clean up test user (if endpoint exists)."""
        try:
            if not self.test_user_id:
                return True
                
            # Note: This would require a delete user endpoint
            # For now, we'll just log that cleanup would happen here
            self.log_test_result("Test Cleanup", True, f"Test user {self.test_user_id} would be cleaned up")
            return True
            
        except Exception as e:
            self.log_test_result("Test Cleanup", False, f"Error during cleanup: {str(e)}")
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all profile integration tests."""
        logger.info("🧪 Starting Profile Integration Tests")
        logger.info("=" * 60)
        
        # Test server health first
        if not await self.test_server_health():
            logger.error("❌ Server is not running. Please start the backend server first.")
            return False
        
        # Create test user and authenticate
        if not await self.create_test_user():
            logger.error("❌ Failed to create test user.")
            return False
        
        # Run profile tests
        tests = [
            self.test_profile_retrieval,
            self.test_profile_update_basic,
            self.test_profile_update_medical,
            self.test_profile_sync,
            self.test_profile_validation_errors,
            self.test_ml_integration
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            try:
                if await test():
                    passed_tests += 1
                # Add small delay between tests
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Test {test.__name__} failed with exception: {e}")
        
        # Cleanup
        await self.cleanup_test_user()
        
        # Print summary
        logger.info("=" * 60)
        logger.info(f"📊 Profile Integration Test Summary: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            logger.info("🎉 All profile integration tests passed!")
            return True
        else:
            logger.error(f"❌ {total_tests - passed_tests} tests failed")
            
            # Print failed tests
            failed_tests = [result for result in self.test_results if not result["passed"]]
            if failed_tests:
                logger.info("\n📋 Failed Tests:")
                for test in failed_tests:
                    logger.info(f"   • {test['test']}: {test['message']}")
            
            return False

async def main():
    """Main test runner."""
    try:
        async with ProfileIntegrationTester() as tester:
            success = await tester.run_all_tests()
            return 0 if success else 1
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"\n\n❌ Tests failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)