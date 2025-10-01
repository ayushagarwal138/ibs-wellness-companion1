#!/usr/bin/env python3
"""
ML Model Logic and Performance Validation

This script validates the correctness and performance of the ML models
by testing various scenarios and edge cases.
"""

import requests
import json
import time
import statistics
from datetime import datetime
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
API_BASE = "http://localhost:8000/api/v1"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "TestPassword123!"

class MLModelValidator:
    def __init__(self):
        self.headers = None
        self.test_results = {
            "severity_tests": [],
            "flareup_tests": [],
            "recommendation_tests": [],
            "performance_tests": [],
            "edge_case_tests": []
        }
        
    def authenticate(self):
        """Authenticate and get access token."""
        logger.info("🔐 Authenticating...")
        auth_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        response = requests.post(f"{API_BASE}/auth/login", json=auth_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {token}"}
            logger.info("✅ Authentication successful")
            return True
        else:
            logger.error(f"❌ Authentication failed: {response.status_code}")
            return False
    
    def test_severity_prediction_logic(self):
        """Test severity prediction with various symptom combinations."""
        logger.info("🧠 Testing severity prediction logic...")
        
        test_cases = [
            {
                "name": "Mild symptoms",
                "symptoms": {
                    "abdominal_pain": 1,
                    "bloating": 1,
                    "gas": 1,
                    "diarrhea": 0,
                    "constipation": 0,
                    "urgency": 1,
                    "stress_level": 3,
                    "sleep_quality": 8
                },
                "expected_severity": "Low"
            },
            {
                "name": "Moderate symptoms",
                "symptoms": {
                    "abdominal_pain": 5,
                    "bloating": 4,
                    "gas": 3,
                    "diarrhea": 3,
                    "constipation": 0,
                    "urgency": 4,
                    "stress_level": 6,
                    "sleep_quality": 5
                },
                "expected_severity": "Medium"
            },
            {
                "name": "Severe symptoms",
                "symptoms": {
                    "abdominal_pain": 8,
                    "bloating": 7,
                    "gas": 6,
                    "diarrhea": 7,
                    "constipation": 0,
                    "urgency": 8,
                    "stress_level": 9,
                    "sleep_quality": 2
                },
                "expected_severity": "High"
            },
            {
                "name": "High stress impact",
                "symptoms": {
                    "abdominal_pain": 3,
                    "bloating": 3,
                    "gas": 2,
                    "diarrhea": 2,
                    "constipation": 0,
                    "urgency": 3,
                    "stress_level": 10,
                    "sleep_quality": 2
                },
                "expected_severity": "Medium"
            }
        ]
        
        for test_case in test_cases:
            logger.info(f"  Testing: {test_case['name']}")
            
            response = requests.post(
                f"{API_BASE}/ml/predict/severity",
                headers=self.headers,
                json={"symptoms": test_case["symptoms"]}
            )
            
            if response.status_code == 200:
                result = response.json()
                severity_level = result.get("severity_level", "Unknown")
                severity_score = result.get("severity_score", 0)
                confidence = result.get("confidence", 0)
                
                test_result = {
                    "test_name": test_case["name"],
                    "input_symptoms": test_case["symptoms"],
                    "predicted_severity": severity_level,
                    "severity_score": severity_score,
                    "confidence": confidence,
                    "expected": test_case["expected_severity"],
                    "passed": severity_level == test_case["expected_severity"]
                }
                
                self.test_results["severity_tests"].append(test_result)
                
                status = "✅" if test_result["passed"] else "⚠️"
                logger.info(f"    {status} Predicted: {severity_level} (score: {severity_score:.2f}, confidence: {confidence:.2f})")
            else:
                logger.error(f"    ❌ Request failed: {response.status_code}")
    
    def test_flareup_prediction_logic(self):
        """Test flareup prediction with various scenarios."""
        logger.info("🔮 Testing flareup prediction logic...")
        
        test_cases = [
            {
                "name": "Low risk scenario",
                "symptoms": {
                    "abdominal_pain": 1,
                    "bloating": 1,
                    "stress_level": 2,
                    "sleep_quality": 8
                },
                "days_ahead": 7,
                "expected_risk": "Low"
            },
            {
                "name": "High stress scenario",
                "symptoms": {
                    "abdominal_pain": 4,
                    "bloating": 5,
                    "stress_level": 9,
                    "sleep_quality": 3
                },
                "days_ahead": 3,
                "expected_risk": "High"
            },
            {
                "name": "Moderate symptoms",
                "symptoms": {
                    "abdominal_pain": 3,
                    "bloating": 4,
                    "stress_level": 6,
                    "sleep_quality": 5
                },
                "days_ahead": 14,
                "expected_risk": "Medium"
            }
        ]
        
        for test_case in test_cases:
            logger.info(f"  Testing: {test_case['name']}")
            
            response = requests.post(
                f"{API_BASE}/ml/predict/flareup",
                headers=self.headers,
                json={
                    "symptoms": test_case["symptoms"],
                    "days_ahead": test_case["days_ahead"]
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                risk_level = result.get("risk_level", "Unknown")
                risk_score = result.get("risk_score", 0)
                confidence = result.get("confidence", 0)
                
                test_result = {
                    "test_name": test_case["name"],
                    "input_symptoms": test_case["symptoms"],
                    "days_ahead": test_case["days_ahead"],
                    "predicted_risk": risk_level,
                    "risk_score": risk_score,
                    "confidence": confidence,
                    "expected": test_case["expected_risk"],
                    "passed": risk_level == test_case["expected_risk"]
                }
                
                self.test_results["flareup_tests"].append(test_result)
                
                status = "✅" if test_result["passed"] else "⚠️"
                logger.info(f"    {status} Predicted: {risk_level} (score: {risk_score:.2f}, confidence: {confidence:.2f})")
            else:
                logger.error(f"    ❌ Request failed: {response.status_code}")
    
    def test_recommendation_logic(self):
        """Test recommendation generation logic."""
        logger.info("💡 Testing recommendation logic...")
        
        test_cases = [
            {
                "name": "High stress symptoms",
                "symptoms": {
                    "abdominal_pain": 6,
                    "bloating": 5,
                    "stress_level": 9,
                    "sleep_quality": 3
                },
                "focus_area": "lifestyle"
            },
            {
                "name": "Digestive symptoms",
                "symptoms": {
                    "abdominal_pain": 4,
                    "bloating": 7,
                    "gas": 6,
                    "diarrhea": 5,
                    "stress_level": 4,
                    "sleep_quality": 6
                },
                "focus_area": "diet"
            },
            {
                "name": "General symptoms",
                "symptoms": {
                    "abdominal_pain": 3,
                    "bloating": 4,
                    "stress_level": 5,
                    "sleep_quality": 5
                },
                "focus_area": "both"
            }
        ]
        
        for test_case in test_cases:
            logger.info(f"  Testing: {test_case['name']}")
            
            response = requests.post(
                f"{API_BASE}/ml/recommendations",
                headers=self.headers,
                json={
                    "symptoms": test_case["symptoms"],
                    "focus_area": test_case["focus_area"]
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                diet_recs = result.get("diet_recommendations", [])
                lifestyle_recs = result.get("lifestyle_recommendations", [])
                diet_score = result.get("diet_score", 0)
                lifestyle_score = result.get("lifestyle_score", 0)
                
                test_result = {
                    "test_name": test_case["name"],
                    "input_symptoms": test_case["symptoms"],
                    "focus_area": test_case["focus_area"],
                    "diet_recommendations_count": len(diet_recs),
                    "lifestyle_recommendations_count": len(lifestyle_recs),
                    "diet_score": diet_score,
                    "lifestyle_score": lifestyle_score,
                    "total_recommendations": len(diet_recs) + len(lifestyle_recs)
                }
                
                self.test_results["recommendation_tests"].append(test_result)
                
                logger.info(f"    ✅ Generated {len(diet_recs)} diet + {len(lifestyle_recs)} lifestyle recommendations")
                logger.info(f"    📊 Scores - Diet: {diet_score:.1f}, Lifestyle: {lifestyle_score:.1f}")
            else:
                logger.error(f"    ❌ Request failed: {response.status_code}")
    
    def test_performance(self):
        """Test model performance and response times."""
        logger.info("⚡ Testing performance...")
        
        # Test response times for each endpoint
        endpoints = [
            ("severity", "/ml/predict/severity", {"symptoms": {"abdominal_pain": 3, "bloating": 4, "stress_level": 5}}),
            ("flareup", "/ml/predict/flareup", {"symptoms": {"abdominal_pain": 3, "bloating": 4}, "days_ahead": 7}),
            ("recommendations", "/ml/recommendations", {"symptoms": {"abdominal_pain": 3, "bloating": 4}})
        ]
        
        for endpoint_name, endpoint_path, test_data in endpoints:
            logger.info(f"  Testing {endpoint_name} endpoint performance...")
            
            response_times = []
            for i in range(5):  # Test 5 times
                start_time = time.time()
                response = requests.post(f"{API_BASE}{endpoint_path}", headers=self.headers, json=test_data)
                end_time = time.time()
                
                if response.status_code == 200:
                    response_times.append(end_time - start_time)
                else:
                    logger.error(f"    ❌ Request {i+1} failed: {response.status_code}")
            
            if response_times:
                avg_time = statistics.mean(response_times)
                min_time = min(response_times)
                max_time = max(response_times)
                
                performance_result = {
                    "endpoint": endpoint_name,
                    "avg_response_time": avg_time,
                    "min_response_time": min_time,
                    "max_response_time": max_time,
                    "total_requests": len(response_times)
                }
                
                self.test_results["performance_tests"].append(performance_result)
                
                logger.info(f"    ✅ Avg: {avg_time:.3f}s, Min: {min_time:.3f}s, Max: {max_time:.3f}s")
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        logger.info("🔍 Testing edge cases...")
        
        edge_cases = [
            {
                "name": "Empty symptoms",
                "endpoint": "/ml/predict/severity",
                "data": {"symptoms": {}},
                "should_succeed": True
            },
            {
                "name": "Missing symptoms field",
                "endpoint": "/ml/predict/severity",
                "data": {},
                "should_succeed": True
            },
            {
                "name": "Invalid days_ahead (too high)",
                "endpoint": "/ml/predict/flareup",
                "data": {"days_ahead": 100, "symptoms": {"abdominal_pain": 3}},
                "should_succeed": False
            },
            {
                "name": "Invalid days_ahead (negative)",
                "endpoint": "/ml/predict/flareup",
                "data": {"days_ahead": -1, "symptoms": {"abdominal_pain": 3}},
                "should_succeed": False
            },
            {
                "name": "Extreme symptom values",
                "endpoint": "/ml/predict/severity",
                "data": {"symptoms": {"abdominal_pain": 100, "bloating": -50}},
                "should_succeed": True
            }
        ]
        
        for test_case in edge_cases:
            logger.info(f"  Testing: {test_case['name']}")
            
            response = requests.post(
                f"{API_BASE}{test_case['endpoint']}",
                headers=self.headers,
                json=test_case["data"]
            )
            
            success = response.status_code == 200
            passed = success == test_case["should_succeed"]
            
            edge_case_result = {
                "test_name": test_case["name"],
                "endpoint": test_case["endpoint"],
                "input_data": test_case["data"],
                "expected_success": test_case["should_succeed"],
                "actual_success": success,
                "status_code": response.status_code,
                "passed": passed
            }
            
            self.test_results["edge_case_tests"].append(edge_case_result)
            
            status = "✅" if passed else "❌"
            logger.info(f"    {status} Status: {response.status_code}, Expected success: {test_case['should_succeed']}")
    
    def generate_report(self):
        """Generate comprehensive validation report."""
        logger.info("📊 Generating validation report...")
        
        # Calculate summary statistics
        total_tests = 0
        passed_tests = 0
        
        for test_category in self.test_results.values():
            for test in test_category:
                total_tests += 1
                if test.get("passed", True):
                    passed_tests += 1
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "validation_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": success_rate
            },
            "detailed_results": self.test_results,
            "recommendations": self._generate_recommendations()
        }
        
        # Save report
        with open("ml_model_validation_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info("=" * 60)
        logger.info("📊 ML Model Validation Summary:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {passed_tests}")
        logger.info(f"   Failed: {total_tests - passed_tests}")
        logger.info(f"   Success Rate: {success_rate:.1f}%")
        logger.info("📄 Report saved to: ml_model_validation_report.json")
        
        return report
    
    def _generate_recommendations(self):
        """Generate recommendations based on test results."""
        recommendations = []
        
        # Check performance
        perf_tests = self.test_results.get("performance_tests", [])
        for test in perf_tests:
            if test["avg_response_time"] > 2.0:
                recommendations.append(f"Consider optimizing {test['endpoint']} endpoint - avg response time: {test['avg_response_time']:.3f}s")
        
        # Check accuracy
        severity_tests = self.test_results.get("severity_tests", [])
        failed_severity = [t for t in severity_tests if not t.get("passed", True)]
        if failed_severity:
            recommendations.append(f"Review severity prediction logic - {len(failed_severity)} tests failed")
        
        flareup_tests = self.test_results.get("flareup_tests", [])
        failed_flareup = [t for t in flareup_tests if not t.get("passed", True)]
        if failed_flareup:
            recommendations.append(f"Review flareup prediction logic - {len(failed_flareup)} tests failed")
        
        # Check edge cases
        edge_tests = self.test_results.get("edge_case_tests", [])
        failed_edge = [t for t in edge_tests if not t.get("passed", True)]
        if failed_edge:
            recommendations.append(f"Improve error handling - {len(failed_edge)} edge case tests failed")
        
        if not recommendations:
            recommendations.append("All tests passed! Models are performing well.")
        
        return recommendations
    
    def run_validation(self):
        """Run complete ML model validation."""
        logger.info("🚀 Starting ML Model Validation...")
        
        if not self.authenticate():
            return False
        
        try:
            self.test_severity_prediction_logic()
            self.test_flareup_prediction_logic()
            self.test_recommendation_logic()
            self.test_performance()
            self.test_edge_cases()
            
            report = self.generate_report()
            
            logger.info("🎉 Validation completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return False

if __name__ == "__main__":
    validator = MLModelValidator()
    success = validator.run_validation()
    exit(0 if success else 1)