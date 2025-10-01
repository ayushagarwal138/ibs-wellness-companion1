#!/usr/bin/env python3
"""
End-to-End ML Integration Validation Script

This script validates the complete ML workflow from frontend to backend,
including model loading, predictions, and data flow.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import httpx
import requests

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "TestPassword123!"

class MLIntegrationValidator:
    """Validates ML integration across the entire stack."""
    
    def __init__(self):
        self.backend_client = httpx.Client(base_url=BACKEND_URL, timeout=30.0)
        self.auth_token = None
        self.test_results = []
        
    async def run_validation(self):
        """Run complete ML integration validation."""
        logger.info("🚀 Starting End-to-End ML Integration Validation")
        logger.info("=" * 60)
        
        try:
            # Test backend connectivity
            await self.test_backend_connectivity()
            
            # Test ML model availability
            await self.test_ml_models_loaded()
            
            # Test authentication
            await self.test_authentication()
            
            # Test ML prediction endpoints
            await self.test_ml_predictions()
            
            # Test ML recommendations
            await self.test_ml_recommendations()
            
            # Test model reloading
            await self.test_model_reload()
            
            # Test frontend accessibility
            await self.test_frontend_accessibility()
            
            # Generate validation report
            await self.generate_validation_report()
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return False
        finally:
            self.backend_client.close()
            
        return True
    
    async def test_backend_connectivity(self):
        """Test backend server connectivity."""
        logger.info("🔗 Testing backend connectivity...")
        
        try:
            response = self.backend_client.get("/health")
            if response.status_code == 200:
                logger.info("✅ Backend server is accessible")
                self.test_results.append({
                    "test": "backend_connectivity",
                    "status": "PASS",
                    "message": "Backend server is accessible"
                })
            else:
                raise Exception(f"Backend returned status {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Backend connectivity failed: {e}")
            self.test_results.append({
                "test": "backend_connectivity",
                "status": "FAIL",
                "message": str(e)
            })
            raise
    
    async def test_ml_models_loaded(self):
        """Test if ML models are properly loaded."""
        logger.info("🤖 Testing ML model availability...")
        
        try:
            # First authenticate to access ML endpoints
            await self.authenticate()
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = self.backend_client.get("/api/v1/ml/models/info", headers=headers)
            
            if response.status_code == 200:
                models_info = response.json()
                model_count = len(models_info.get("models", []))
                logger.info(f"✅ ML models loaded: {model_count} models available")
                
                # Check for required models
                required_models = ["severity_model", "flareup_model", "recommendation_model"]
                available_models = list(models_info.get("models_loaded", {}).keys())
                
                missing_models = [model for model in required_models if model not in available_models]
                if missing_models:
                    raise Exception(f"Missing required models: {missing_models}")
                
                self.test_results.append({
                    "test": "ml_models_loaded",
                    "status": "PASS",
                    "message": f"{model_count} ML models loaded successfully",
                    "details": models_info
                })
            else:
                raise Exception(f"ML models endpoint returned status {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ ML models test failed: {e}")
            self.test_results.append({
                "test": "ml_models_loaded",
                "status": "FAIL",
                "message": str(e)
            })
            raise
    
    async def test_authentication(self):
        """Test user authentication."""
        logger.info("🔐 Testing authentication...")
        
        try:
            await self.authenticate()
            logger.info("✅ Authentication successful")
            self.test_results.append({
                "test": "authentication",
                "status": "PASS",
                "message": "User authentication successful"
            })
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            self.test_results.append({
                "test": "authentication",
                "status": "FAIL",
                "message": str(e)
            })
            raise
    
    async def test_ml_predictions(self):
        """Test ML prediction endpoints."""
        logger.info("🔮 Testing ML predictions...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test severity prediction
        severity_data = {
            "symptoms": {
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
                "sleep_quality": 3
            }
        }
        
        try:
            response = self.backend_client.post(
                "/api/v1/ml/predict/severity",
                json=severity_data,
                headers=headers
            )
            
            if response.status_code == 200:
                prediction = response.json()
                logger.info(f"✅ Severity prediction: {prediction.get('predicted_severity')} (confidence: {prediction.get('confidence', 0):.2f})")
                self.test_results.append({
                    "test": "severity_prediction",
                    "status": "PASS",
                    "message": "Severity prediction successful",
                    "details": prediction
                })
            else:
                raise Exception(f"Severity prediction failed with status {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Severity prediction failed: {e}")
            self.test_results.append({
                "test": "severity_prediction",
                "status": "FAIL",
                "message": str(e)
            })
        
        # Test flareup prediction
        flareup_data = {
            "recent_symptoms": ["abdominal_pain", "diarrhea"],
            "stress_level": 7,
            "sleep_hours": 6,
            "diet_adherence": 0.8,
            "days_ahead": 3
        }
        
        try:
            response = self.backend_client.post(
                "/api/v1/ml/predict/flareup",
                json=flareup_data,
                headers=headers
            )
            
            if response.status_code == 200:
                prediction = response.json()
                logger.info(f"✅ Flareup prediction: {prediction.get('risk_level')} (probability: {prediction.get('probability', 0):.2f})")
                self.test_results.append({
                    "test": "flareup_prediction",
                    "status": "PASS",
                    "message": "Flareup prediction successful",
                    "details": prediction
                })
            else:
                raise Exception(f"Flareup prediction failed with status {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Flareup prediction failed: {e}")
            self.test_results.append({
                "test": "flareup_prediction",
                "status": "FAIL",
                "message": str(e)
            })
    
    async def test_ml_recommendations(self):
        """Test ML recommendations endpoint."""
        logger.info("💡 Testing ML recommendations...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        recommendations_data = {
            "user_profile": {
                "age": 30,
                "gender": "female",
                "ibs_type": "IBS-D",
                "severity": "moderate"
            },
            "recent_symptoms": ["abdominal_pain", "diarrhea"],
            "dietary_preferences": ["vegetarian"],
            "lifestyle_factors": {
                "stress_level": 6,
                "exercise_frequency": 3,
                "sleep_quality": 7
            }
        }
        
        try:
            response = self.backend_client.post(
                "/api/v1/ml/recommendations",
                json=recommendations_data,
                headers=headers
            )
            
            if response.status_code == 200:
                recommendations = response.json()
                diet_count = len(recommendations.get('dietary_recommendations', []))
                lifestyle_count = len(recommendations.get('lifestyle_recommendations', []))
                logger.info(f"✅ Recommendations generated: {diet_count} dietary, {lifestyle_count} lifestyle")
                self.test_results.append({
                    "test": "ml_recommendations",
                    "status": "PASS",
                    "message": f"Generated {diet_count} dietary and {lifestyle_count} lifestyle recommendations",
                    "details": recommendations
                })
            else:
                raise Exception(f"Recommendations failed with status {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ ML recommendations failed: {e}")
            self.test_results.append({
                "test": "ml_recommendations",
                "status": "FAIL",
                "message": str(e)
            })
    
    async def test_model_reload(self):
        """Test ML model reloading functionality."""
        logger.info("🔄 Testing model reload...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            response = self.backend_client.post("/api/v1/ml/models/reload", headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Model reload successful: {result.get('message')}")
                self.test_results.append({
                    "test": "model_reload",
                    "status": "PASS",
                    "message": "Model reload successful",
                    "details": result
                })
            else:
                raise Exception(f"Model reload failed with status {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Model reload failed: {e}")
            self.test_results.append({
                "test": "model_reload",
                "status": "FAIL",
                "message": str(e)
            })
    
    async def test_frontend_accessibility(self):
        """Test frontend accessibility."""
        logger.info("🌐 Testing frontend accessibility...")
        
        try:
            response = requests.get(FRONTEND_URL, timeout=10)
            if response.status_code == 200:
                logger.info("✅ Frontend is accessible")
                self.test_results.append({
                    "test": "frontend_accessibility",
                    "status": "PASS",
                    "message": "Frontend is accessible"
                })
            else:
                raise Exception(f"Frontend returned status {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Frontend accessibility failed: {e}")
            self.test_results.append({
                "test": "frontend_accessibility",
                "status": "FAIL",
                "message": str(e)
            })
    
    async def authenticate(self):
        """Authenticate with the backend."""
        if self.auth_token:
            return
            
        # Try to create test user first
        try:
            user_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "full_name": "Test User"
            }
            self.backend_client.post("/api/v1/auth/register", json=user_data)
        except:
            pass  # User might already exist
        
        # Login
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        response = self.backend_client.post("/api/v1/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            self.auth_token = token_data["access_token"]
        else:
            raise Exception(f"Authentication failed with status {response.status_code}")
    
    async def generate_validation_report(self):
        """Generate validation report."""
        logger.info("📊 Generating validation report...")
        
        passed_tests = [test for test in self.test_results if test["status"] == "PASS"]
        failed_tests = [test for test in self.test_results if test["status"] == "FAIL"]
        
        report = {
            "validation_timestamp": datetime.now().isoformat(),
            "total_tests": len(self.test_results),
            "passed_tests": len(passed_tests),
            "failed_tests": len(failed_tests),
            "success_rate": len(passed_tests) / len(self.test_results) * 100 if self.test_results else 0,
            "test_results": self.test_results
        }
        
        # Save report
        report_file = Path("ml_e2e_validation_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("=" * 60)
        logger.info(f"📊 Validation Summary:")
        logger.info(f"   Total Tests: {report['total_tests']}")
        logger.info(f"   Passed: {report['passed_tests']}")
        logger.info(f"   Failed: {report['failed_tests']}")
        logger.info(f"   Success Rate: {report['success_rate']:.1f}%")
        logger.info(f"📄 Report saved to: {report_file}")
        
        if failed_tests:
            logger.error("❌ Some tests failed:")
            for test in failed_tests:
                logger.error(f"   - {test['test']}: {test['message']}")
        else:
            logger.info("🎉 All tests passed!")
        
        return report

async def main():
    """Main validation function."""
    validator = MLIntegrationValidator()
    success = await validator.run_validation()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)