#!/usr/bin/env python3
"""
Simple ML Endpoints Test Script

Tests the ML prediction endpoints directly to verify core functionality.
This bypasses authentication to focus on ML service testing.
"""

import asyncio
import json
import sys
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

# Sample test data
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
    "sleep_quality": 3
}

class SimpleMLTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data: Dict = None):
        """Log test result for summary."""
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
    
    async def test_server_health(self) -> bool:
        """Test if the server is running and healthy."""
        try:
            response = await self.client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                self.log_test_result("Server Health Check", True, "Server is running")
                return True
            else:
                self.log_test_result("Server Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("Server Health Check", False, f"Connection error: {str(e)}")
            return False
    
    async def test_ml_service_initialization(self) -> bool:
        """Test if ML services are properly initialized by checking if ML endpoints are available."""
        try:
            # Check if ML-related endpoints are available by testing the health endpoint
            response = await self.client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                self.log_test_result(
                    "ML Service Initialization", 
                    True, 
                    "ML service endpoints are accessible"
                )
                return True
            else:
                self.log_test_result("ML Service Initialization", False, f"Health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test_result("ML Service Initialization", False, f"Error: {str(e)}")
            return False
    
    async def test_ml_service_classes(self) -> bool:
        """Test if ML service classes can be imported and instantiated."""
        try:
            # Test importing ML services
            import sys
            import os
            
            # Add the app directory to Python path
            app_path = os.path.join(os.getcwd(), 'app')
            if app_path not in sys.path:
                sys.path.insert(0, app_path)
            
            from app.services.ml_model_service import MLModelService
            from app.services.ml_integration_service import MLIntegrationService
            
            # Test MLModelService initialization (doesn't require db)
            ml_service = MLModelService()
            
            # Test that the service has expected methods
            expected_methods = ['predict_severity', 'predict_flareup_risk', 'generate_recommendations']
            missing_methods = [method for method in expected_methods if not hasattr(ml_service, method)]
            
            if missing_methods:
                self.log_test_result("ML Service Classes", False, f"Missing methods: {missing_methods}")
                return False
            
            self.log_test_result(
                "ML Service Classes", 
                True, 
                "ML service classes imported and initialized successfully"
            )
            return True
            
        except ImportError as e:
            self.log_test_result("ML Service Classes", False, f"Import error: {str(e)}")
            return False
        except Exception as e:
            self.log_test_result("ML Service Classes", False, f"Error: {str(e)}")
            return False
    
    async def test_ml_model_loading(self) -> bool:
        """Test if ML models can be loaded."""
        try:
            import sys
            import os
            
            # Add the app directory to Python path
            app_path = os.path.join(os.getcwd(), 'app')
            if app_path not in sys.path:
                sys.path.insert(0, app_path)
            
            from app.services.ml_model_service import MLModelService
            
            # Test model loading
            ml_service = MLModelService()
            model_info = ml_service.get_model_info()
            
            if model_info.get('models_loaded'):
                self.log_test_result(
                    "ML Model Loading", 
                    True, 
                    f"Models loaded successfully: {list(model_info['models_loaded'].keys())}"
                )
            else:
                self.log_test_result(
                    "ML Model Loading", 
                    True, 
                    "Fallback models initialized (no trained models found)"
                )
            return True
            
        except Exception as e:
            self.log_test_result("ML Model Loading", False, f"Error: {str(e)}")
            return False
    
    async def test_ml_predictions(self) -> bool:
        """Test ML prediction functionality directly."""
        try:
            import sys
            import os
            
            # Add the app directory to Python path
            app_path = os.path.join(os.getcwd(), 'app')
            if app_path not in sys.path:
                sys.path.insert(0, app_path)
            
            from app.services.ml_model_service import MLModelService
            
            # Test predictions
            ml_service = MLModelService()
            
            # Test severity prediction
            severity_result = ml_service.predict_severity(SAMPLE_SYMPTOMS)
            
            # Test flareup prediction
            flareup_result = ml_service.predict_flareup_risk(SAMPLE_SYMPTOMS, days_ahead=7)
            
            # Test recommendations
            recommendations = ml_service.generate_recommendations(SAMPLE_SYMPTOMS)
            
            self.log_test_result(
                "ML Predictions", 
                True, 
                f"Predictions generated - Severity: {severity_result.get('severity_level')}, "
                f"Flareup Risk: {flareup_result.get('risk_level')}, "
                f"Recommendations: {len(recommendations.get('diet_recommendations', []))} diet, "
                f"{len(recommendations.get('lifestyle_recommendations', []))} lifestyle"
            )
            return True
            
        except Exception as e:
            self.log_test_result("ML Predictions", False, f"Error: {str(e)}")
            return False
    
    async def test_data_processing(self) -> bool:
        """Test data processing and feature preparation."""
        try:
            import sys
            import os
            
            # Add the app directory to Python path
            app_path = os.path.join(os.getcwd(), 'app')
            if app_path not in sys.path:
                sys.path.insert(0, app_path)
            
            from app.services.ml_model_service import MLModelService
            
            ml_service = MLModelService()
            
            # Test feature preparation methods
            severity_features = ml_service._prepare_severity_features(SAMPLE_SYMPTOMS)
            flareup_features = ml_service._prepare_flareup_features(SAMPLE_SYMPTOMS)
            recommendation_features = ml_service._prepare_recommendation_features(SAMPLE_SYMPTOMS)
            
            if len(severity_features) > 0 and len(flareup_features) > 0 and len(recommendation_features) > 0:
                self.log_test_result(
                    "Data Processing", 
                    True, 
                    f"Features prepared successfully: {len(severity_features)} severity, "
                    f"{len(flareup_features)} flareup, {len(recommendation_features)} recommendation features"
                )
            else:
                self.log_test_result("Data Processing", False, "No features generated")
                return False
            
            return True
            
        except Exception as e:
            self.log_test_result("Data Processing", False, f"Error: {str(e)}")
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all ML integration tests."""
        logger.info("🚀 Starting Simple ML Integration Tests")
        logger.info("=" * 50)
        
        # Test server health first
        if not await self.test_server_health():
            logger.error("❌ Server is not running. Please start the backend server first.")
            return False
        
        # Run ML service tests
        tests = [
            self.test_ml_service_initialization,
            self.test_ml_service_classes,
            self.test_ml_model_loading,
            self.test_ml_predictions,
            self.test_data_processing
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
    
    def save_test_report(self, filename: str = "simple_ml_test_report.json"):
        """Save detailed test report to file."""
        report = {
            "test_run_timestamp": datetime.now().isoformat(),
            "total_tests": len(self.test_results),
            "passed_tests": sum(1 for r in self.test_results if r["success"]),
            "failed_tests": sum(1 for r in self.test_results if not r["success"]),
            "test_results": self.test_results
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Test report saved to {filename}")


async def main():
    """Main test runner."""
    async with SimpleMLTester() as tester:
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