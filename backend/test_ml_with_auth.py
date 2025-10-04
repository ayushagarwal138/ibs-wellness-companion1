#!/usr/bin/env python3
"""
Test ML endpoints with proper authentication.

This script tests the complete authentication flow and ML prediction endpoints
to verify that the integration between frontend, backend, and ML models works.
"""

import asyncio
import uuid
from typing import Dict, Any

import httpx
import os


BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')


class MLEndpointTester:
    """Test ML endpoints with authentication."""

    def __init__(self):
        self.base_url = BASE_URL
        self.access_token = None
        self.user_id = None

    async def register_test_user(self) -> Dict[str, Any]:
        """Register a test user and return the response."""
        test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        user_data = {
            "email": test_email,
            "password": "TestPassword123!",
            "confirm_password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User",
            "date_of_birth": "1990-01-01",
            "height_cm": 170,
            "weight_kg": 70
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/register",
                json=user_data
            )
            
            if response.status_code == 201:
                data = response.json()
                self.access_token = data["access_token"]
                self.user_id = data["user"]["id"]
                print(f"✅ User registered successfully: {test_email}")
                return data
            else:
                print(f"❌ Registration failed: {response.status_code} - "
                      f"{response.text}")
                return {}

    async def test_ml_predictions_endpoint(self) -> Dict[str, Any]:
        """Test the main ML predictions endpoint."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        async with httpx.AsyncClient() as client:
            url = (f"{self.base_url}/api/v1/ml/predictions?"
                   f"timeframe=week&include_recommendations=true")
            response = await client.get(url, headers=headers)
            
            print(f"ML Predictions endpoint: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                risk_level = data.get('risk_level')
                confidence = data.get('confidence')
                print(f"✅ Predictions received: risk_level={risk_level}, "
                      f"confidence={confidence}")
                return data
            else:
                print(f"❌ Predictions failed: {response.text}")
                return {}

    async def test_severity_prediction(self) -> Dict[str, Any]:
        """Test severity prediction endpoint."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        request_data = {
            "symptoms": {
                "pain_level": 6,
                "bloating": 7,
                "diarrhea": 4,
                "constipation": 2,
                "nausea": 3,
                "fatigue": 5
            },
            "context": {
                "stress_level": 7,
                "sleep_quality": 6,
                "recent_meals": ["pasta", "coffee", "salad"],
                "medications": ["ibuprofen"]
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/ml/predict/severity",
                json=request_data,
                headers=headers
            )
            
            print(f"Severity prediction endpoint: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Severity prediction: {data.get('severity_category')} "
                      f"(score: {data.get('predicted_severity')})")
                return data
            else:
                print(f"❌ Severity prediction failed: {response.text}")
                return {}

    async def test_flareup_prediction(self) -> Dict[str, Any]:
        """Test flareup prediction endpoint."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        request_data = {
            "recent_symptoms": [
                {
                    "date": "2024-01-15",
                    "symptoms": {"abdominal_pain": 6, "bloating": 7},
                    "triggers": ["stress", "dairy"]
                }
            ],
            "lifestyle_factors": {
                "stress_level": 7,
                "sleep_quality": 5,
                "exercise_frequency": 2,
                "diet_adherence": 0.8
            },
            "prediction_horizon": 7
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/ml/predict/flareup",
                json=request_data,
                headers=headers
            )
            
            print(f"Flareup prediction endpoint: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Flareup prediction: {data.get('risk_level')} risk "
                      f"(probability: {data.get('flareup_probability')})")
                return data
            else:
                print(f"❌ Flareup prediction failed: {response.text}")
                return {}

    async def test_recommendations_endpoint(self) -> Dict[str, Any]:
        """Test recommendations endpoint."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        request_data = {
            "user_profile": {
                "age": 28,
                "ibs_type": "IBS-M",
                "dietary_restrictions": ["lactose_intolerant"],
                "activity_level": "moderate"
            },
            "current_symptoms": {
                "abdominal_pain": 5.5,
                "bloating": 7.0,
                "gas": 4.0
            },
            "preferences": {
                "dietary_approach": "low_fodmap",
                "exercise_preference": "yoga",
                "supplement_tolerance": "high"
            },
            "recommendation_types": ["dietary", "lifestyle", "supplements"]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/ml/recommendations",
                json=request_data,
                headers=headers
            )
            
            print(f"Recommendations endpoint: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                dietary_count = len(data.get('dietary_recommendations', []))
                lifestyle_count = len(data.get('lifestyle_insights', []))
                print(f"✅ Recommendations received: {dietary_count} dietary, "
                      f"{lifestyle_count} lifestyle")
                return data
            else:
                print(f"❌ Recommendations failed: {response.text}")
                return {}

    async def test_multimodal_prediction(self) -> Dict[str, Any]:
        """Test multimodal prediction endpoint."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/ml/predict/multimodal?timeframe_days=30",
                headers=headers
            )
            
            print(f"Multimodal prediction endpoint: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Multimodal prediction: {data.get('risk_category')} risk "
                      f"(score: {data.get('overall_risk_score')})")
                return data
            else:
                print(f"❌ Multimodal prediction failed: {response.text}")
                return {}

    async def test_realtime_predictions(self) -> Dict[str, Any]:
        """Test real-time predictions endpoint."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/ml/realtime-predictions",
                headers=headers
            )
            
            print(f"Real-time predictions endpoint: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Real-time predictions: risk={data.get('current_risk')}, "
                      f"confidence={data.get('confidence_score')}")
                return data
            else:
                print(f"❌ Real-time predictions failed: {response.text}")
                return {}

    async def run_all_tests(self):
        """Run all ML endpoint tests."""
        print("🚀 Starting ML endpoint tests with authentication...")
        print("=" * 60)
        
        # Register test user
        await self.register_test_user()
        if not self.access_token:
            print("❌ Cannot proceed without authentication token")
            return
        
        token_preview = self.access_token[:20]
        print(f"\n🔑 Authentication token obtained: {token_preview}...")
        print("=" * 60)
        
        # Test all endpoints
        test_results = {}
        
        print("\n📊 Testing ML Prediction Endpoints:")
        print("-" * 40)
        
        test_results['predictions'] = await self.test_ml_predictions_endpoint()
        test_results['severity'] = await self.test_severity_prediction()
        test_results['flareup'] = await self.test_flareup_prediction()
        test_results['recommendations'] = await self.test_recommendations_endpoint()
        test_results['multimodal'] = await self.test_multimodal_prediction()
        test_results['realtime'] = await self.test_realtime_predictions()
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 Test Summary:")
        successful_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        print(f"✅ Successful tests: {successful_tests}/{total_tests}")
        
        if successful_tests == total_tests:
            print("🎉 All ML endpoints are working correctly with authentication!")
        else:
            print("⚠️  Some ML endpoints may need attention.")
        
        return test_results


async def main():
    """Main test function."""
    tester = MLEndpointTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())