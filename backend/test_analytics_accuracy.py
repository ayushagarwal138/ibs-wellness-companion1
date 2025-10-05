#!/usr/bin/env python3
"""
Comprehensive test for analytics accuracy and real-time updates
Tests both backend analytics calculations and frontend data consistency
"""
import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.core.config import settings
import asyncpg


class AnalyticsAccuracyTester:
    def __init__(self):
        self.base_url = "http://localhost:8000/api/v1"
        self.test_user_email = "api_test@example.com"
        self.test_user_password = "testpass123"
        self.access_token = None
        self.user_id = None
        
    async def setup_auth(self, session: aiohttp.ClientSession) -> bool:
        """Authenticate and get access token"""
        print("🔐 Setting up authentication...")
        
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        try:
            async with session.post(f"{self.base_url}/auth/login", json=login_data) as response:
                if response.status != 200:
                    print(f"❌ Login failed: {response.status}")
                    return False
                
                result = await response.json()
                self.access_token = result.get("access_token")
                print(f"✅ Authentication successful")
                return True
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    async def get_database_analytics(self) -> Dict[str, Any]:
        """Get analytics directly from database for comparison"""
        print("📊 Fetching analytics directly from database...")
        
        db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
        
        try:
            conn = await asyncpg.connect(db_url)
            
            # Get user ID
            user = await conn.fetchrow(
                "SELECT id FROM users WHERE email = $1", 
                self.test_user_email
            )
            
            if not user:
                print(f"❌ User {self.test_user_email} not found")
                return {}
            
            self.user_id = user['id']
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            # Get symptom logs count
            symptom_logs_count = await conn.fetchval("""
                SELECT COUNT(*) FROM symptom_logs 
                WHERE user_id = $1 AND logged_at >= $2
            """, self.user_id, thirty_days_ago)
            
            # Get diet logs count
            diet_logs_count = await conn.fetchval("""
                SELECT COUNT(*) FROM diet_logs 
                WHERE user_id = $1 AND consumed_at >= $2
            """, self.user_id, thirty_days_ago)
            
            # Get average severity
            avg_severity_result = await conn.fetchrow("""
                SELECT 
                    AVG(CASE 
                        WHEN severity = 'NONE' THEN 0
                        WHEN severity = 'MILD' THEN 1
                        WHEN severity = 'MODERATE' THEN 2
                        WHEN severity = 'SEVERE' THEN 3
                        WHEN severity = 'VERY_SEVERE' THEN 4
                        ELSE 0
                    END) as avg_severity,
                    COUNT(*) as total_logs
                FROM symptom_logs 
                WHERE user_id = $1 AND logged_at >= $2
            """, self.user_id, thirty_days_ago)
            
            avg_severity = float(avg_severity_result['avg_severity']) if avg_severity_result['avg_severity'] else 0
            
            # Get food reactions count
            food_reactions_count = await conn.fetchval("""
                SELECT COUNT(*) FROM food_reactions 
                WHERE user_id = $1 AND created_at >= $2
            """, self.user_id, thirty_days_ago)
            
            # Get symptom-free days
            days_with_symptoms = await conn.fetchval("""
                SELECT COUNT(DISTINCT DATE(logged_at))
                FROM symptom_logs 
                WHERE user_id = $1 AND logged_at >= $2
            """, self.user_id, thirty_days_ago)
            
            symptom_free_days = 30 - days_with_symptoms
            
            await conn.close()
            
            db_analytics = {
                "total_symptom_logs": symptom_logs_count,
                "total_diet_logs": diet_logs_count,
                "avg_severity": avg_severity,
                "food_reactions": food_reactions_count,
                "symptom_free_days": symptom_free_days,
                "days_with_symptoms": days_with_symptoms
            }
            
            print(f"✅ Database analytics retrieved: {db_analytics}")
            return db_analytics
            
        except Exception as e:
            print(f"❌ Database analytics error: {e}")
            return {}
    
    async def get_api_analytics(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Get analytics from API endpoint"""
        print("🌐 Fetching analytics from API endpoint...")
        
        try:
            async with session.get(
                f"{self.base_url}/analytics/user-analytics",
                headers=self.get_auth_headers(),
                params={"days": 30}
            ) as response:
                if response.status != 200:
                    print(f"❌ API analytics failed: {response.status}")
                    text = await response.text()
                    print(f"Error: {text}")
                    return {}
                
                api_analytics = await response.json()
                print(f"✅ API analytics retrieved: {api_analytics}")
                return api_analytics
                
        except Exception as e:
            print(f"❌ API analytics error: {e}")
            return {}
    
    async def get_dashboard_analytics(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Get analytics from dashboard service endpoints"""
        print("📈 Fetching analytics from dashboard endpoints...")
        
        dashboard_data = {}
        
        try:
            # Get symptom logs
            async with session.get(
                f"{self.base_url}/symptom-logs/",
                headers=self.get_auth_headers(),
                params={"days": 30}
            ) as response:
                if response.status == 200:
                    symptom_data = await response.json()
                    dashboard_data["symptom_logs"] = symptom_data.get("data", [])
                    dashboard_data["symptom_logs_count"] = len(dashboard_data["symptom_logs"])
            
            # Get diet stats
            async with session.get(
                f"{self.base_url}/diet/stats/diet",
                headers=self.get_auth_headers(),
                params={"days": 30}
            ) as response:
                if response.status == 200:
                    diet_data = await response.json()
                    dashboard_data["diet_stats"] = diet_data
                    dashboard_data["meals_logged"] = diet_data.get("total_meals_logged", 0)
            
            # Get food reactions
            async with session.get(
                f"{self.base_url}/diet/reactions",
                headers=self.get_auth_headers(),
                params={"size": 100}
            ) as response:
                if response.status == 200:
                    reactions_data = await response.json()
                    dashboard_data["food_reactions"] = reactions_data.get("data", [])
                    dashboard_data["food_reactions_count"] = len(dashboard_data["food_reactions"])
            
            # Get ML predictions
            async with session.get(
                f"{self.base_url}/ml/predictions",
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    ml_data = await response.json()
                    dashboard_data["ml_predictions"] = ml_data
            
            print(f"✅ Dashboard analytics retrieved")
            return dashboard_data
            
        except Exception as e:
            print(f"❌ Dashboard analytics error: {e}")
            return {}
    
    def compare_analytics(self, db_data: Dict[str, Any], api_data: Dict[str, Any], dashboard_data: Dict[str, Any]) -> Dict[str, bool]:
        """Compare analytics from different sources for accuracy"""
        print("\n🔍 Comparing analytics accuracy...")
        
        results = {}
        
        # Compare symptom logs count
        db_symptom_count = db_data.get("total_symptom_logs", 0)
        api_symptom_count = api_data.get("total_symptom_logs", 0)
        dashboard_symptom_count = dashboard_data.get("symptom_logs_count", 0)
        
        symptom_match = db_symptom_count == api_symptom_count == dashboard_symptom_count
        results["symptom_logs_accuracy"] = symptom_match
        
        print(f"Symptom logs - DB: {db_symptom_count}, API: {api_symptom_count}, Dashboard: {dashboard_symptom_count} {'✅' if symptom_match else '❌'}")
        
        # Compare diet logs count
        db_diet_count = db_data.get("total_diet_logs", 0)
        api_diet_count = api_data.get("total_diet_logs", 0)
        dashboard_diet_count = dashboard_data.get("meals_logged", 0)
        
        diet_match = db_diet_count == api_diet_count == dashboard_diet_count
        results["diet_logs_accuracy"] = diet_match
        
        print(f"Diet logs - DB: {db_diet_count}, API: {api_diet_count}, Dashboard: {dashboard_diet_count} {'✅' if diet_match else '❌'}")
        
        # Compare food reactions count
        db_reactions_count = db_data.get("food_reactions", 0)
        api_reactions_count = api_data.get("food_reactions", 0)
        dashboard_reactions_count = dashboard_data.get("food_reactions_count", 0)
        
        reactions_match = db_reactions_count == api_reactions_count == dashboard_reactions_count
        results["food_reactions_accuracy"] = reactions_match
        
        print(f"Food reactions - DB: {db_reactions_count}, API: {api_reactions_count}, Dashboard: {dashboard_reactions_count} {'✅' if reactions_match else '❌'}")
        
        # Compare average severity (with tolerance for floating point)
        db_avg_severity = db_data.get("avg_severity", 0)
        api_avg_severity = api_data.get("avg_severity", 0)
        
        severity_match = abs(db_avg_severity - api_avg_severity) < 0.01
        results["avg_severity_accuracy"] = severity_match
        
        print(f"Avg severity - DB: {db_avg_severity:.3f}, API: {api_avg_severity:.3f} {'✅' if severity_match else '❌'}")
        
        return results
    
    async def test_real_time_updates(self, session: aiohttp.ClientSession) -> bool:
        """Test real-time data updates by creating new data and checking consistency"""
        print("\n⏱️ Testing real-time updates...")
        
        try:
            # Get initial analytics
            initial_api_data = await self.get_api_analytics(session)
            initial_symptom_count = initial_api_data.get("total_symptom_logs", 0)
            
            # Create a new symptom log
            print("Creating new symptom log...")
            symptom_data = {
                "symptom_id": 1,  # Assuming symptom ID 1 exists
                "severity": "MILD",
                "notes": "Test symptom for real-time update test",
                "logged_at": datetime.utcnow().isoformat()
            }
            
            async with session.post(
                f"{self.base_url}/symptom-logs/",
                headers=self.get_auth_headers(),
                json=symptom_data
            ) as response:
                if response.status not in [200, 201]:
                    print(f"❌ Failed to create symptom log: {response.status}")
                    return False
            
            # Wait a moment for processing
            await asyncio.sleep(2)
            
            # Get updated analytics
            updated_api_data = await self.get_api_analytics(session)
            updated_symptom_count = updated_api_data.get("total_symptom_logs", 0)
            
            # Check if count increased
            real_time_working = updated_symptom_count == initial_symptom_count + 1
            
            print(f"Initial count: {initial_symptom_count}, Updated count: {updated_symptom_count}")
            print(f"Real-time updates: {'✅ Working' if real_time_working else '❌ Not working'}")
            
            return real_time_working
            
        except Exception as e:
            print(f"❌ Real-time update test error: {e}")
            return False
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run the complete analytics accuracy test"""
        print("🚀 Starting comprehensive analytics accuracy test...\n")
        
        async with aiohttp.ClientSession() as session:
            # Setup authentication
            if not await self.setup_auth(session):
                return {"error": "Authentication failed"}
            
            # Get analytics from all sources
            db_data = await self.get_database_analytics()
            api_data = await self.get_api_analytics(session)
            dashboard_data = await self.get_dashboard_analytics(session)
            
            # Compare accuracy
            accuracy_results = self.compare_analytics(db_data, api_data, dashboard_data)
            
            # Test real-time updates
            real_time_working = await self.test_real_time_updates(session)
            
            # Calculate overall accuracy
            total_tests = len(accuracy_results)
            passed_tests = sum(accuracy_results.values())
            accuracy_percentage = (passed_tests / total_tests * 100) if total_tests > 0 else 0
            
            results = {
                "overall_accuracy": f"{accuracy_percentage:.1f}%",
                "tests_passed": passed_tests,
                "total_tests": total_tests,
                "real_time_updates": real_time_working,
                "detailed_results": accuracy_results,
                "raw_data": {
                    "database": db_data,
                    "api": api_data,
                    "dashboard": dashboard_data
                }
            }
            
            print(f"\n📊 Test Results Summary:")
            print(f"Overall Accuracy: {accuracy_percentage:.1f}% ({passed_tests}/{total_tests} tests passed)")
            print(f"Real-time Updates: {'✅ Working' if real_time_working else '❌ Not working'}")
            
            return results


async def main():
    """Main test function"""
    tester = AnalyticsAccuracyTester()
    results = await tester.run_comprehensive_test()
    
    print(f"\n📋 Full Results:")
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())