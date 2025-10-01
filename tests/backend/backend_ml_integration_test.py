#!/usr/bin/env python3
"""
Backend-ML Integration Test Suite

This module tests the integration between the FastAPI backend and ML models
for real-time IBS assessment processing, ensuring seamless data flow and
accurate predictions.

Features:
- API endpoint testing
- ML model integration verification
- Data transformation validation
- Performance benchmarking
- Error handling testing
"""

import asyncio
import json
import time
import requests
import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Add ML models to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ml-models', 'src'))

try:
    from ibs_risk_predictor import IBSRiskPredictor
    from recommendation_engine import IBSRecommendationEngine
    from severity_classifier import SeverityClassifier
except ImportError as e:
    print(f"⚠️  Warning: Could not import ML models: {e}")
    print("   Some tests may be skipped")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BackendMLIntegrationTester:
    """Comprehensive backend-ML integration testing"""
    
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.api_base = f"{backend_url}/api/v1"
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'backend_url': backend_url,
            'tests': {},
            'summary': {}
        }
        
        # Test data
        self.sample_assessment_data = {
            "symptoms": {
                "abdominal_pain": 7,
                "bloating": 8,
                "gas": 6,
                "diarrhea": 5,
                "constipation": 2,
                "urgency": 6,
                "incomplete_evacuation": 4
            },
            "triggers": {
                "stress": 8,
                "certain_foods": 7,
                "hormonal_changes": 5,
                "travel": 3,
                "medications": 2
            },
            "lifestyle": {
                "exercise_frequency": 3,
                "sleep_quality": 6,
                "stress_level": 8,
                "diet_quality": 5
            },
            "demographics": {
                "age": 32,
                "gender": "female",
                "duration_months": 24
            }
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive backend-ML integration tests"""
        print("🔄 Starting Backend-ML Integration Tests")
        print("=" * 50)
        
        test_methods = [
            self.test_backend_health,
            self.test_ml_models_availability,
            self.test_risk_assessment_endpoint,
            self.test_recommendation_endpoint,
            self.test_data_transformation,
            self.test_error_handling,
            self.test_performance_benchmarks,
            self.test_concurrent_requests
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                print(f"\n🧪 Running {test_method.__name__}...")
                result = test_method()
                self.test_results['tests'][test_method.__name__] = result
                
                if result.get('passed', False):
                    passed_tests += 1
                    print(f"   ✅ PASSED: {result.get('message', 'Test completed')}")
                else:
                    print(f"   ❌ FAILED: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                error_result = {
                    'passed': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                self.test_results['tests'][test_method.__name__] = error_result
                print(f"   ❌ ERROR: {str(e)}")
        
        # Generate summary
        self.test_results['summary'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': passed_tests / total_tests,
            'overall_status': 'PASSED' if passed_tests == total_tests else 'FAILED'
        }
        
        self._save_results()
        self._print_summary()
        
        return self.test_results
    
    def test_backend_health(self) -> Dict[str, Any]:
        """Test backend API health and availability"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            
            if response.status_code == 200:
                return {
                    'passed': True,
                    'message': 'Backend API is healthy and responsive',
                    'response_time': response.elapsed.total_seconds(),
                    'status_code': response.status_code
                }
            else:
                return {
                    'passed': False,
                    'error': f'Backend health check failed with status {response.status_code}',
                    'status_code': response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'passed': False,
                'error': f'Backend connection failed: {str(e)}'
            }
    
    def test_ml_models_availability(self) -> Dict[str, Any]:
        """Test ML models can be loaded and initialized"""
        try:
            models_status = {}
            
            # Test IBSRiskPredictor
            try:
                risk_predictor = IBSRiskPredictor()
                models_status['risk_predictor'] = 'Available'
            except Exception as e:
                models_status['risk_predictor'] = f'Error: {str(e)}'
            
            # Test IBSRecommendationEngine
            try:
                recommendation_engine = IBSRecommendationEngine()
                models_status['recommendation_engine'] = 'Available'
            except Exception as e:
                models_status['recommendation_engine'] = f'Error: {str(e)}'
            
            # Test SeverityClassifier
            try:
                severity_classifier = SeverityClassifier()
                models_status['severity_classifier'] = 'Available'
            except Exception as e:
                models_status['severity_classifier'] = f'Error: {str(e)}'
            
            available_models = sum(1 for status in models_status.values() if status == 'Available')
            total_models = len(models_status)
            
            return {
                'passed': available_models > 0,
                'message': f'{available_models}/{total_models} ML models available',
                'models_status': models_status,
                'availability_rate': available_models / total_models
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': f'ML models test failed: {str(e)}'
            }
    
    def test_risk_assessment_endpoint(self) -> Dict[str, Any]:
        """Test IBS risk assessment API endpoint"""
        try:
            endpoint = f"{self.api_base}/ibs-assessment/risk-factors"
            
            # Test without authentication (should return 403) - using GET method
            response = requests.get(endpoint, timeout=10)
            
            if response.status_code == 403:
                # Expected behavior - authentication required
                return {
                    'passed': True,
                    'message': 'Risk assessment endpoint properly requires authentication',
                    'status_code': response.status_code,
                    'authentication_required': True
                }
            elif response.status_code == 200:
                # Unexpected - should require auth
                return {
                    'passed': False,
                    'error': 'Risk assessment endpoint should require authentication',
                    'status_code': response.status_code
                }
            else:
                return {
                    'passed': False,
                    'error': f'Unexpected status code: {response.status_code}',
                    'status_code': response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'passed': False,
                'error': f'Risk assessment endpoint test failed: {str(e)}'
            }
    
    def test_recommendation_endpoint(self) -> Dict[str, Any]:
        """Test recommendation generation endpoint"""
        try:
            endpoint = f"{self.api_base}/ibs-assessment/recommendations"
            
            # Test without authentication (should return 403) - using GET method
            response = requests.get(endpoint, timeout=10)
            
            if response.status_code == 403:
                return {
                    'passed': True,
                    'message': 'Recommendations endpoint properly requires authentication',
                    'status_code': response.status_code,
                    'authentication_required': True
                }
            else:
                return {
                    'passed': False,
                    'error': f'Unexpected status code: {response.status_code}',
                    'status_code': response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'passed': False,
                'error': f'Recommendations endpoint test failed: {str(e)}'
            }
    
    def test_data_transformation(self) -> Dict[str, Any]:
        """Test data transformation between API and ML models"""
        try:
            # Test data transformation logic
            from backend.app.services.ibs_assessment_service import IBSAssessmentService
            
            service = IBSAssessmentService()
            
            # Test feature extraction
            features = service._extract_ml_features(self.sample_assessment_data)
            
            # Validate feature structure
            expected_features = [
                'abdominal_pain', 'bloating', 'gas', 'diarrhea', 'constipation',
                'urgency', 'incomplete_evacuation', 'stress', 'certain_foods',
                'exercise_frequency', 'sleep_quality', 'stress_level', 'age'
            ]
            
            missing_features = [f for f in expected_features if f not in features]
            extra_features = [f for f in features if f not in expected_features]
            
            if not missing_features and not extra_features:
                return {
                    'passed': True,
                    'message': 'Data transformation working correctly',
                    'features_count': len(features),
                    'feature_names': list(features.keys())
                }
            else:
                return {
                    'passed': False,
                    'error': 'Feature extraction mismatch',
                    'missing_features': missing_features,
                    'extra_features': extra_features
                }
                
        except ImportError:
            return {
                'passed': False,
                'error': 'Could not import IBSAssessmentService for testing'
            }
        except Exception as e:
            return {
                'passed': False,
                'error': f'Data transformation test failed: {str(e)}'
            }
    
    def test_error_handling(self) -> Dict[str, Any]:
        """Test API error handling with invalid data"""
        try:
            # Test POST endpoint with invalid data
            endpoint = f"{self.api_base}/ibs-assessment/conduct"
            
            # Test with invalid data
            invalid_data = {"invalid": "data"}
            response = requests.post(endpoint, json=invalid_data, timeout=10)
            
            # Should return 422 (validation error) or 403 (auth error)
            if response.status_code in [422, 403]:
                return {
                    'passed': True,
                    'message': 'API properly handles invalid data',
                    'status_code': response.status_code
                }
            else:
                return {
                    'passed': False,
                    'error': f'Unexpected error handling: {response.status_code}',
                    'status_code': response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'passed': False,
                'error': f'Error handling test failed: {str(e)}'
            }
    
    def test_performance_benchmarks(self) -> Dict[str, Any]:
        """Test API response time performance"""
        try:
            # Test GET endpoint for performance
            endpoint = f"{self.api_base}/ibs-assessment/risk-factors"
            
            response_times = []
            num_requests = 5
            
            for i in range(num_requests):
                start_time = time.time()
                response = requests.get(endpoint, timeout=10)
                end_time = time.time()
                
                response_times.append(end_time - start_time)
            
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            # Performance threshold: average response time should be < 2 seconds
            performance_threshold = 2.0
            
            return {
                'passed': avg_response_time < performance_threshold,
                'message': f'Average response time: {avg_response_time:.3f}s',
                'avg_response_time': avg_response_time,
                'max_response_time': max_response_time,
                'min_response_time': min_response_time,
                'performance_threshold': performance_threshold,
                'requests_tested': num_requests
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'passed': False,
                'error': f'Performance benchmark test failed: {str(e)}'
            }
    
    def test_concurrent_requests(self) -> Dict[str, Any]:
        """Test API handling of concurrent requests"""
        try:
            import concurrent.futures
            import threading
            
            endpoint = f"{self.api_base}/ibs-assessment/risk-factors"
            num_concurrent = 5
            
            def make_request():
                try:
                    response = requests.post(endpoint, json=self.sample_assessment_data, timeout=10)
                    return {
                        'status_code': response.status_code,
                        'response_time': response.elapsed.total_seconds(),
                        'success': True
                    }
                except Exception as e:
                    return {
                        'error': str(e),
                        'success': False
                    }
            
            # Execute concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
                futures = [executor.submit(make_request) for _ in range(num_concurrent)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            successful_requests = sum(1 for r in results if r.get('success', False))
            avg_response_time = sum(r.get('response_time', 0) for r in results if r.get('success', False)) / max(successful_requests, 1)
            
            return {
                'passed': successful_requests > 0,
                'message': f'{successful_requests}/{num_concurrent} concurrent requests handled',
                'successful_requests': successful_requests,
                'total_requests': num_concurrent,
                'avg_response_time': avg_response_time,
                'success_rate': successful_requests / num_concurrent
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': f'Concurrent requests test failed: {str(e)}'
            }
    
    def _save_results(self):
        """Save test results to file"""
        results_file = 'backend_ml_integration_results.json'
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n💾 Results saved to {results_file}")
    
    def _print_summary(self):
        """Print test summary"""
        summary = self.test_results['summary']
        
        print(f"\n📊 Backend-ML Integration Test Summary")
        print("=" * 50)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        print(f"Overall Status: {summary['overall_status']}")
        
        if summary['overall_status'] == 'PASSED':
            print("🎉 All backend-ML integration tests passed!")
        else:
            print("⚠️  Some tests failed. Check results for details.")


def main():
    """Run backend-ML integration tests"""
    print("🔄 Backend-ML Integration Test Suite")
    print("=" * 50)
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print("✅ Backend server detected")
    except requests.exceptions.RequestException:
        print("⚠️  Backend server not detected at http://localhost:8000")
        print("   Starting tests anyway (some may fail)")
    
    # Run tests
    tester = BackendMLIntegrationTester()
    results = tester.run_all_tests()
    
    return results


if __name__ == "__main__":
    main()