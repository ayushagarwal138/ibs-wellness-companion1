#!/usr/bin/env python3
"""
Profile Validation Integration Tests

Tests the profile update endpoint to ensure proper validation of user data.
"""

import asyncio
import aiohttp
import json
from datetime import datetime, date
import sys
import traceback

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = "testuser@example.com"  # Use the newly created user
TEST_USER_PASSWORD = "TestPass123!"

class ProfileValidationTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = None
        self.auth_token = None
        self.test_results = []
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
            
    async def register_test_user(self):
        """Register a test user for authentication"""
        try:
            user_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "first_name": "Test",
                "last_name": "User"
            }
            
            async with self.session.post(f"{self.base_url}/api/v1/auth/register", json=user_data) as response:
                if response.status in [200, 201]:
                    print("✓ Test user registered successfully")
                    return True
                elif response.status == 400:
                    # User might already exist, try to login
                    print("Test user already exists, proceeding to login")
                    return True
                else:
                    print(f"Failed to register test user: {response.status}")
                    return False
        except Exception as e:
            print(f"Error registering test user: {e}")
            return False
            
    async def login_test_user(self):
        """Login and get authentication token"""
        try:
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/auth/login", 
                json=login_data,  # Use JSON instead of form data
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.auth_token = result.get("access_token")
                    print("✓ Successfully authenticated")
                    return True
                else:
                    response_text = await response.text()
                    print(f"Failed to login: {response.status}")
                    print(f"Response: {response_text}")
                    return False
        except Exception as e:
            print(f"Error during login: {e}")
            return False
            
    def get_auth_headers(self):
        """Get authentication headers"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
        
    async def test_profile_validation_errors(self):
        """Test that invalid profile data is properly rejected"""
        print("\n=== Testing Profile Validation Errors ===")
        
        # Invalid data that should trigger validation errors
        invalid_data = {
            "first_name": "",  # Empty string should fail min_length validation
            "last_name": "A" * 100,  # Too long, should fail max_length validation
            "phone_number": "invalid-phone-123!@#",  # Invalid phone format
            "height_cm": -10,  # Negative height should fail gt=0 validation
            "weight_kg": 2000,  # Too high weight should fail le=1000 validation
            "date_of_birth": "2030-01-01",  # Future date should be invalid
            "emergency_contact_phone": "invalid-phone-456!@#"  # Invalid phone format
        }
        
        try:
            headers = self.get_auth_headers()
            headers["Content-Type"] = "application/json"
            
            async with self.session.patch(
                f"{self.base_url}/api/v1/users/profile", 
                json=invalid_data,
                headers=headers
            ) as response:
                status = response.status
                response_text = await response.text()
                
                print(f"Response Status: {status}")
                print(f"Response: {response_text}")
                
                # Should return 422 (Unprocessable Entity) for validation errors
                if status == 422:
                    print("✓ Profile validation correctly rejected invalid data")
                    self.test_results.append(("Profile Validation Errors", True, "Correctly rejected invalid data"))
                    return True
                else:
                    print(f"✗ Expected 422 validation error, got {status}")
                    self.test_results.append(("Profile Validation Errors", False, f"Expected 422, got {status}"))
                    return False
                    
        except Exception as e:
            print(f"✗ Error testing profile validation: {e}")
            self.test_results.append(("Profile Validation Errors", False, f"Exception: {e}"))
            return False
            
    async def test_valid_profile_update(self):
        """Test that valid profile data is accepted"""
        print("\n=== Testing Valid Profile Update ===")
        
        valid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "+1-555-123-4567",
            "height_cm": 175.5,
            "weight_kg": 70.0,
            "date_of_birth": "1990-01-01"
        }
        
        try:
            headers = self.get_auth_headers()
            headers["Content-Type"] = "application/json"
            
            async with self.session.patch(
                f"{self.base_url}/api/v1/users/profile", 
                json=valid_data,
                headers=headers
            ) as response:
                status = response.status
                response_text = await response.text()
                
                print(f"Response Status: {status}")
                
                if status == 200:
                    print("✓ Valid profile data accepted")
                    self.test_results.append(("Valid Profile Update", True, "Profile updated successfully"))
                    return True
                else:
                    print(f"✗ Expected 200, got {status}")
                    print(f"Response: {response_text}")
                    self.test_results.append(("Valid Profile Update", False, f"Expected 200, got {status}"))
                    return False
                    
        except Exception as e:
            print(f"✗ Error testing valid profile update: {e}")
            self.test_results.append(("Valid Profile Update", False, f"Exception: {e}"))
            return False
            
    async def run_all_tests(self):
        """Run all profile validation tests"""
        print("Starting Profile Validation Tests...")
        print(f"Testing against: {self.base_url}")
        
        await self.setup_session()
        
        try:
            # Skip registration, just try to login directly
            if not await self.login_test_user():
                print("Failed to login test user")
                return False
            
            # Run tests
            await self.test_valid_profile_update()
            await self.test_profile_validation_errors()
            
            # Print results
            print("\n" + "="*50)
            print("TEST RESULTS SUMMARY")
            print("="*50)
            
            passed = 0
            total = len(self.test_results)
            
            for test_name, success, message in self.test_results:
                status = "PASS" if success else "FAIL"
                print(f"{status}: {test_name} - {message}")
                if success:
                    passed += 1
            
            print(f"\nTests passed: {passed}/{total}")
            
            if passed == total:
                print("🎉 All tests passed!")
                return True
            else:
                print("❌ Some tests failed!")
                return False
                
        finally:
            await self.cleanup_session()

async def main():
    """Main test runner"""
    tester = ProfileValidationTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())