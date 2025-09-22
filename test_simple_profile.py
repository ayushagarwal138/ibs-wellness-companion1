#!/usr/bin/env python3
"""
Simple Profile Test Script

Tests basic profile functionality with proper authentication.
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

class SimpleProfileTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.access_token = None
        self.test_user_id = None
        
    async def create_and_authenticate_user(self) -> bool:
        """Create a test user and authenticate."""
        try:
            # Create unique test user
            user_data = {
                "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
                "password": "TestPassword123!",
                "confirm_password": "TestPassword123!",
                "first_name": "Test",
                "last_name": "User"
            }
            
            # Register user
            response = await self.client.post(f"{API_BASE}/auth/register", json=user_data)
            
            if response.status_code == 201:
                logger.info("✅ User created successfully")
                
                # Login to get token
                login_data = {
                    "email": user_data["email"],
                    "password": user_data["password"]
                }
                
                login_response = await self.client.post(
                    f"{API_BASE}/auth/login",
                    json=login_data
                )
                
                if login_response.status_code == 200:
                    token_data = login_response.json()
                    self.access_token = token_data["access_token"]
                    logger.info("✅ Authentication successful")
                    return True
                else:
                    logger.error(f"❌ Login failed: {login_response.status_code}")
                    return False
            else:
                logger.error(f"❌ Registration failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating test user: {str(e)}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers."""
        return {"Authorization": f"Bearer {self.access_token}"}
    
    async def test_profile_retrieval(self) -> bool:
        """Test profile retrieval."""
        try:
            response = await self.client.get(
                f"{API_BASE}/users/profile",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Profile retrieval successful")
                logger.info(f"Profile data: {json.dumps(data, indent=2)}")
                return True
            else:
                logger.error(f"❌ Profile retrieval failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error retrieving profile: {str(e)}")
            return False
    
    async def test_simple_profile_update(self) -> bool:
        """Test simple profile update."""
        try:
            update_data = {
                "first_name": "Updated",
                "last_name": "Name"
            }
            
            response = await self.client.patch(
                f"{API_BASE}/users/profile",
                json=update_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Profile update successful")
                logger.info(f"Updated profile: {json.dumps(data, indent=2)}")
                return True
            else:
                logger.error(f"❌ Profile update failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error updating profile: {str(e)}")
            return False
    
    async def run_tests(self) -> bool:
        """Run all tests."""
        logger.info("🚀 Starting Simple Profile Tests")
        logger.info("=" * 50)
        
        # Test 1: Create and authenticate user
        if not await self.create_and_authenticate_user():
            logger.error("❌ Authentication failed - stopping tests")
            return False
        
        # Test 2: Retrieve profile
        profile_success = await self.test_profile_retrieval()
        
        # Test 3: Update profile
        update_success = await self.test_simple_profile_update()
        
        # Summary
        logger.info("=" * 50)
        total_tests = 2
        passed_tests = sum([profile_success, update_success])
        
        logger.info(f"📊 Test Summary: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            logger.info("🎉 All tests passed!")
            return True
        else:
            logger.error(f"❌ {total_tests - passed_tests} tests failed")
            return False
    
    async def cleanup(self):
        """Cleanup resources."""
        await self.client.aclose()

async def main():
    """Main test function."""
    tester = SimpleProfileTester()
    try:
        success = await tester.run_tests()
        sys.exit(0 if success else 1)
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())