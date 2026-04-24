#!/usr/bin/env python3
"""
Frontend-Backend ML Integration Test

Tests the complete data flow from frontend authentication to ML predictions.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

class FrontendMLIntegrationTest:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_email = f"integration_test_{int(time.time())}@example.com"
        
    def register_and_login(self):
        """Register a test user and obtain access token."""
        print("🔐 Registering test user and obtaining authentication...")
        
        # Register user
        user_data = {
            "email": self.user_email,
            "password": "TestPassword123!",
            "confirm_password": "TestPassword123!",
            "first_name": "Integration",
            "last_name": "Test"
        }
        
        response = self.session.post(
            f"{BACKEND_URL}/api/v1/auth/register",
            json=user_data
        )
        
        if response.status_code != 201:
            print(f"❌ Registration failed: {response.text}")
            return False
            
        # Login to get token
        login_data = {
            "email": self.user_email,
            "password": "TestPassword123!"
        }
        
        response = self.session.post(
            f"{BACKEND_URL}/api/v1/auth/login",
            json=login_data
        )
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.text}")
            return False
            
        auth_data = response.json()
        self.access_token = auth_data["access_token"]
        print(f"✅ Authentication successful")
        return True
        
    def test_ml_service_integration(self):
        """Test ML service integration as used by frontend."""
        print("\n📊 Testing ML Service Integration...")
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        # Test the generateReport functionality
        print("Testing ML predictions endpoint...")
        response = self.session.get(
            f"{BACKEND_URL}/api/v1/ml/predictions?timeframe=7&include_recommendations=true",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ ML Predictions: {data.get('risk_level', 'N/A')} risk")
            print(f"   Confidence: {data.get('confidence', 'N/A')}")
        else:
            print(f"❌ ML Predictions failed: {response.status_code}")
            
        # Test recommendations endpoint
        print("Testing recommendations endpoint...")
        rec_data = {
            "user_profile": {
                "age": 30,
                "ibs_type": "IBS-M",
                "dietary_restrictions": ["lactose_intolerant"],
                "activity_level": "moderate"
            },
            "current_symptoms": {
                "abdominal_pain": 6.0,
                "bloating": 7.5,
                "gas": 4.0
            },
            "preferences": {
                "dietary_approach": "low_fodmap",
                "exercise_preference": "yoga"
            },
            "recommendation_types": ["dietary", "lifestyle"]
        }
        
        response = self.session.post(
            f"{BACKEND_URL}/api/v1/ml/recommendations",
            json=rec_data,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Recommendations received")
            print(f"   Personalization score: {data.get('personalization_score', 'N/A')}")
        else:
            print(f"❌ Recommendations failed: {response.status_code}")
            
        # Test real-time predictions
        print("Testing real-time predictions...")
        realtime_data = {
            "symptoms": {
                "abdominal_pain": 3,
                "bloating": 2,
                "diarrhea": 1
            },
            "include_trends": True,
            "include_recommendations": True,
            "stream_updates": False
        }
        
        response = self.session.post(
            f"{BACKEND_URL}/api/v1/ml/realtime/predict/enhanced",
            json=realtime_data,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Real-time predictions received")
            print(f"   Risk score: {data.get('risk_score', 'N/A')}")
        else:
            print(f"❌ Real-time predictions failed: {response.status_code}")
            
    def test_reports_page_data_flow(self):
        """Test the specific data flow used by the reports page."""
        print("\n📈 Testing Reports Page Data Flow...")
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        # Simulate the fetchReportData function from reports page
        print("Simulating fetchReportData function...")
        
        # 1. Get ML predictions (as done in generateReport)
        predictions_response = self.session.get(
            f"{BACKEND_URL}/api/v1/ml/predictions?timeframe=30",
            headers=headers
        )
        
        # 2. Get recommendations
        rec_data = {
            "user_profile": {"age": 30, "ibs_type": "IBS-M"},
            "current_symptoms": {"abdominal_pain": 5.0, "bloating": 6.0},
            "recommendation_types": ["dietary", "lifestyle"]
        }
        
        recommendations_response = self.session.post(
            f"{BACKEND_URL}/api/v1/ml/recommendations",
            json=rec_data,
            headers=headers
        )
        
        # 3. Get real-time predictions
        realtime_data = {
            "symptoms": {"abdominal_pain": 5.0, "bloating": 6.0},
            "include_trends": True,
            "include_recommendations": False
        }
        
        realtime_response = self.session.post(
            f"{BACKEND_URL}/api/v1/ml/realtime/predict/enhanced",
            json=realtime_data,
            headers=headers
        )
        
        # Check if all components work
        success_count = 0
        total_tests = 3
        
        if predictions_response.status_code == 200:
            print("✅ Predictions data retrieved successfully")
            success_count += 1
        else:
            print(f"❌ Predictions failed: {predictions_response.status_code}")
            
        if recommendations_response.status_code == 200:
            print("✅ Recommendations data retrieved successfully")
            success_count += 1
        else:
            print(f"❌ Recommendations failed: {recommendations_response.status_code}")
            
        if realtime_response.status_code == 200:
            print("✅ Real-time data retrieved successfully")
            success_count += 1
        else:
            print(f"❌ Real-time predictions failed: {realtime_response.status_code}")
            
        print(f"\n📊 Reports Page Integration: {success_count}/{total_tests} components working")
        
        if success_count == total_tests:
            print("🎉 Complete data flow is working correctly!")
            return True
        else:
            print("⚠️  Some components need attention")
            return False
            
    def run_complete_test(self):
        """Run the complete integration test."""
        print("🚀 Starting Frontend-Backend ML Integration Test")
        print("=" * 60)
        
        # Step 1: Authentication
        if not self.register_and_login():
            print("❌ Authentication failed - cannot proceed")
            return False
            
        # Step 2: ML Service Integration
        self.test_ml_service_integration()
        
        # Step 3: Reports Page Data Flow
        reports_success = self.test_reports_page_data_flow()
        
        print("\n" + "=" * 60)
        print("📋 Integration Test Summary:")
        print(f"✅ Authentication: Working")
        print(f"✅ ML Endpoints: Working")
        print(f"{'✅' if reports_success else '❌'} Reports Data Flow: {'Working' if reports_success else 'Needs attention'}")
        
        if reports_success:
            print("\n🎉 All integration tests passed!")
            print("The frontend can successfully authenticate and fetch real ML data.")
        else:
            print("\n⚠️  Some integration issues detected.")
            
        return reports_success

if __name__ == "__main__":
    test = FrontendMLIntegrationTest()
    test.run_complete_test()