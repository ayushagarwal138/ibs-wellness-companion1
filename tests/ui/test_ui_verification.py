#!/usr/bin/env python3
"""
UI Verification Test for ML Integration
Tests the visual and functional aspects of ML components in the frontend.
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class UIVerificationTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.session = None
        self.auth_token = None
        
    async def setup_session(self):
        """Setup HTTP session for testing."""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session."""
        if self.session:
            await self.session.close()
            
    async def authenticate_user(self):
        """Authenticate a test user."""
        print("🔐 Setting up authentication...")
        
        # Register test user
        register_data = {
            "email": f"test_ui_{int(time.time())}@example.com",
            "password": "TestPassword123!",
            "confirm_password": "TestPassword123!",
            "first_name": "UI",
            "last_name": "Tester"
        }
        
        try:
            async with self.session.post(f"{self.base_url}/api/v1/auth/register", json=register_data) as response:
                if response.status == 201:
                    print("✓ Test user registered successfully")
                elif response.status == 400:
                    print("ℹ Test user already exists, proceeding with login")
                else:
                    print(f"⚠ Registration status: {response.status}")
                    response_text = await response.text()
                    print(f"  Response: {response_text}")
        except Exception as e:
            print(f"⚠ Registration error: {e}")
        
        # Login
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        
        try:
            async with self.session.post(f"{self.base_url}/api/v1/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    print("✓ Authentication successful")
                    return True
                else:
                    print(f"✗ Login failed with status: {response.status}")
                    response_text = await response.text()
                    print(f"  Response: {response_text}")
                    return False
        except Exception as e:
            print(f"✗ Login error: {e}")
            return False
    
    async def test_ml_data_consistency(self):
        """Test ML data consistency across multiple calls."""
        print("\n📊 Testing ML Data Consistency...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        results = []
        
        # Make multiple calls to check consistency
        for i in range(5):
            try:
                async with self.session.get(f"{self.base_url}/api/v1/ml/realtime-predictions", headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        results.append({
                            'call': i + 1,
                            'risk_level': data.get('current_risk'),  # Use correct field name
                            'confidence': data.get('confidence_score'),  # Use correct field name
                            'timestamp': datetime.now().isoformat(),
                            'full_response': data  # Store full response for debugging
                        })
                    else:
                        print(f"  Call {i + 1} failed with status: {response.status}")
                    await asyncio.sleep(0.5)  # Small delay between calls
            except Exception as e:
                print(f"✗ Error in call {i + 1}: {e}")
        
        if results:
            print(f"✓ Data consistency test completed with {len(results)} successful calls")
            # Check for consistency
            risk_levels = [r['risk_level'] for r in results if r['risk_level'] is not None]
            confidences = [r['confidence'] for r in results if r['confidence'] is not None]
            
            print(f"  - Risk levels: {set(risk_levels) if risk_levels else 'No valid risk levels'}")
            if confidences:
                print(f"  - Confidence range: {min(confidences):.2f} - {max(confidences):.2f}")
            else:
                print(f"  - Confidence range: No valid confidence values")
            
            # Print sample response for debugging
            if results:
                print(f"  - Sample response: {results[0]}")
            
            return len(set(risk_levels)) <= 2 if risk_levels else False  # Allow some variation
        else:
            print("✗ No successful data consistency calls")
            return False
    
    async def test_ml_component_integration(self):
        """Test ML component integration points."""
        print("\n🔗 Testing ML Component Integration...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        integration_tests = {
            'realtime_predictions': False,
            'ml_predictions': False,
            'model_info': False,
            'data_flow': False
        }
        
        # Test real-time predictions
        try:
            async with self.session.get(f"{self.base_url}/api/v1/ml/realtime-predictions", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ['current_risk', 'confidence_score', 'immediate_recommendations']
                    if all(field in data for field in required_fields):
                        integration_tests['realtime_predictions'] = True
                        print("✓ Real-time predictions integration working")
                    else:
                        print(f"⚠ Missing fields in real-time predictions: {[f for f in required_fields if f not in data]}")
                        print(f"  Available fields: {list(data.keys())}")
        except Exception as e:
            print(f"✗ Real-time predictions integration error: {e}")
        
        # Test ML predictions
        try:
            async with self.session.get(f"{self.base_url}/api/v1/ml/predictions", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"  ML predictions response: {data}")
                    # Check for any meaningful data structure
                    if data and (isinstance(data, dict) or isinstance(data, list)):
                        integration_tests['ml_predictions'] = True
                        print("✓ ML predictions integration working")
                    else:
                        print("⚠ ML predictions returned empty or invalid data")
                else:
                    print(f"⚠ ML predictions returned status: {response.status}")
        except Exception as e:
            print(f"✗ ML predictions integration error: {e}")
        
        # Test model info
        try:
            async with self.session.get(f"{self.base_url}/api/v1/ml/models/info", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    integration_tests['model_info'] = True
                    print("✓ Model info integration working")
        except Exception as e:
            print(f"✗ Model info integration error: {e}")
        
        # Test data flow consistency
        integration_tests['data_flow'] = await self.test_ml_data_consistency()
        
        return integration_tests
    
    async def test_performance_metrics(self):
        """Test performance of ML endpoints."""
        print("\n⚡ Testing Performance Metrics...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        performance_results = {}
        
        endpoints = [
            "/api/v1/ml/realtime-predictions",
            "/api/v1/ml/predictions", 
            "/api/v1/ml/models/info"
        ]
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                async with self.session.get(f"{self.base_url}{endpoint}", headers=headers) as response:
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000  # Convert to ms
                    
                    performance_results[endpoint] = {
                        'response_time_ms': response_time,
                        'status_code': response.status,
                        'success': response.status == 200
                    }
                    
                    status_icon = "✓" if response.status == 200 else "✗"
                    print(f"  {status_icon} {endpoint}: {response_time:.2f}ms (HTTP {response.status})")
                    
            except Exception as e:
                performance_results[endpoint] = {
                    'response_time_ms': None,
                    'status_code': None,
                    'success': False,
                    'error': str(e)
                }
                print(f"  ✗ {endpoint}: Error - {e}")
        
        return performance_results
    
    async def test_error_handling(self):
        """Test error handling in ML endpoints."""
        print("\n🛡️ Testing Error Handling...")
        
        error_tests = {
            'unauthorized_access': False,
            'invalid_data': False,
            'missing_auth': False
        }
        
        # Test unauthorized access
        try:
            async with self.session.get(f"{self.base_url}/api/v1/ml/realtime-predictions") as response:
                if response.status == 401:
                    error_tests['unauthorized_access'] = True
                    print("✓ Proper unauthorized access handling")
                else:
                    print(f"⚠ Unexpected status for unauthorized access: {response.status}")
        except Exception as e:
            print(f"✗ Error testing unauthorized access: {e}")
        
        # Test invalid auth token
        try:
            invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
            async with self.session.get(f"{self.base_url}/api/v1/ml/realtime-predictions", headers=invalid_headers) as response:
                if response.status in [401, 403]:
                    error_tests['missing_auth'] = True
                    print("✓ Proper invalid token handling")
                else:
                    print(f"⚠ Unexpected status for invalid token: {response.status}")
        except Exception as e:
            print(f"✗ Error testing invalid token: {e}")
        
        return error_tests
    
    async def generate_verification_report(self, integration_results, performance_results, error_results):
        """Generate a comprehensive verification report."""
        print("\n" + "="*60)
        print("🏁 ML UI Integration Verification Report")
        print("="*60)
        
        # Integration Results
        integration_passed = sum(integration_results.values())
        integration_total = len(integration_results)
        print(f"\n📊 Integration Tests: {integration_passed}/{integration_total} passed")
        for test, result in integration_results.items():
            status = "✓" if result else "✗"
            print(f"  {status} {test.replace('_', ' ').title()}")
        
        # Performance Results
        print(f"\n⚡ Performance Tests:")
        successful_endpoints = sum(1 for r in performance_results.values() if r['success'])
        total_endpoints = len(performance_results)
        print(f"  Successful endpoints: {successful_endpoints}/{total_endpoints}")
        
        avg_response_time = sum(r['response_time_ms'] for r in performance_results.values() if r['response_time_ms']) / len([r for r in performance_results.values() if r['response_time_ms']])
        print(f"  Average response time: {avg_response_time:.2f}ms")
        
        # Error Handling Results
        error_passed = sum(error_results.values())
        error_total = len(error_results)
        print(f"\n🛡️ Error Handling Tests: {error_passed}/{error_total} passed")
        for test, result in error_results.items():
            status = "✓" if result else "✗"
            print(f"  {status} {test.replace('_', ' ').title()}")
        
        # Overall Assessment
        total_tests = integration_total + error_total
        total_passed = integration_passed + error_passed
        success_rate = (total_passed / total_tests) * 100
        
        print(f"\n🎯 Overall Assessment:")
        print(f"  Tests Passed: {total_passed}/{total_tests}")
        print(f"  Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("  Status: ✅ EXCELLENT - ML integration is working optimally")
        elif success_rate >= 75:
            print("  Status: ✅ GOOD - ML integration is working well with minor issues")
        elif success_rate >= 60:
            print("  Status: ⚠️ FAIR - ML integration has some issues that need attention")
        else:
            print("  Status: ❌ POOR - ML integration has significant issues")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if not integration_results['realtime_predictions']:
            print("  - Fix real-time predictions endpoint integration")
        if not integration_results['ml_predictions']:
            print("  - Verify ML predictions data structure")
        if avg_response_time > 100:
            print("  - Optimize API response times (currently averaging {:.2f}ms)".format(avg_response_time))
        if not all(error_results.values()):
            print("  - Improve error handling for edge cases")
        
        return {
            'success_rate': success_rate,
            'integration_results': integration_results,
            'performance_results': performance_results,
            'error_results': error_results
        }

async def main():
    """Main test execution function."""
    print("🚀 Starting ML UI Integration Verification")
    print("="*50)
    
    tester = UIVerificationTester()
    
    try:
        await tester.setup_session()
        
        # Authenticate
        if not await tester.authenticate_user():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
        
        # Run tests
        integration_results = await tester.test_ml_component_integration()
        performance_results = await tester.test_performance_metrics()
        error_results = await tester.test_error_handling()
        
        # Generate report
        report = await tester.generate_verification_report(
            integration_results, performance_results, error_results
        )
        
        # Save report to file
        with open('ml_ui_verification_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: ml_ui_verification_report.json")
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
    finally:
        await tester.cleanup_session()

if __name__ == "__main__":
    asyncio.run(main())