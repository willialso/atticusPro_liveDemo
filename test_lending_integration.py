#!/usr/bin/env python3
"""
Lending Protection Integration Test
Comprehensive validation of the lending protection feature integration
"""

import requests
import json
import time
from datetime import datetime

class LendingIntegrationTest:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        
    def test_health_check(self):
        """Test basic health check"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"Status: {data.get('status')}")
                return True
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Error: {str(e)}")
            return False
    
    def test_market_data(self):
        """Test market data endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/market-data")
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'live':
                    self.log_test("Market Data", True, f"BTC: ${data.get('btc_price', 0):,.2f}")
                    return True
                else:
                    self.log_test("Market Data", False, "Not live data")
                    return False
            else:
                self.log_test("Market Data", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Market Data", False, f"Error: {str(e)}")
            return False
    
    def test_institutional_workflow(self):
        """Test existing institutional workflow (regression test)"""
        try:
            # Test institutional portfolio analysis
            analysis_response = self.session.post(f"{self.base_url}/api/analyze-portfolio", 
                json={'type': 'pension_fund', 'mode': 'institutional'})
            
            if analysis_response.status_code != 200:
                self.log_test("Institutional Analysis", False, f"Status: {analysis_response.status_code}")
                return False
                
            analysis_data = analysis_response.json()
            if not analysis_data.get('success'):
                self.log_test("Institutional Analysis", False, analysis_data.get('error', 'Unknown error'))
                return False
            
            # Test strategy generation
            strategy_response = self.session.post(f"{self.base_url}/api/generate-strategies")
            if strategy_response.status_code != 200:
                self.log_test("Institutional Strategies", False, f"Status: {strategy_response.status_code}")
                return False
                
            strategy_data = strategy_response.json()
            if not strategy_data.get('success'):
                self.log_test("Institutional Strategies", False, strategy_data.get('error', 'Unknown error'))
                return False
            
            self.log_test("Institutional Workflow", True, f"Generated {len(strategy_data.get('strategies', []))} strategies")
            return True
            
        except Exception as e:
            self.log_test("Institutional Workflow", False, f"Error: {str(e)}")
            return False
    
    def test_lending_workflow(self):
        """Test new lending protection workflow"""
        try:
            # Test lending portfolio analysis
            loan_params = {
                'loan_amount': 1000000,
                'loan_term': 90,
                'ltv_ratio': 70,
                'protection_type': 'downside',
                'btc_price': 50000  # Mock price for testing
            }
            
            analysis_response = self.session.post(f"{self.base_url}/api/analyze-portfolio", 
                json={'mode': 'lending', 'loan_params': loan_params})
            
            if analysis_response.status_code != 200:
                self.log_test("Lending Analysis", False, f"Status: {analysis_response.status_code}")
                return False
                
            analysis_data = analysis_response.json()
            if not analysis_data.get('success'):
                self.log_test("Lending Analysis", False, analysis_data.get('error', 'Unknown error'))
                return False
            
            # Verify lending-specific fields
            analysis = analysis_data.get('analysis', {})
            if 'protection_type' not in analysis.get('profile', {}):
                self.log_test("Lending Analysis", False, "Missing protection_type in profile")
                return False
            
            if 'loan_amount' not in analysis.get('positions', {}):
                self.log_test("Lending Analysis", False, "Missing loan_amount in positions")
                return False
            
            # Test lending strategy generation
            strategy_response = self.session.post(f"{self.base_url}/api/generate-strategies")
            if strategy_response.status_code != 200:
                self.log_test("Lending Strategies", False, f"Status: {strategy_response.status_code}")
                return False
                
            strategy_data = strategy_response.json()
            if not strategy_data.get('success'):
                self.log_test("Lending Strategies", False, strategy_data.get('error', 'Unknown error'))
                return False
            
            # Verify lending-specific strategy fields
            strategies = strategy_data.get('strategies', [])
            if not strategies:
                self.log_test("Lending Strategies", False, "No strategies generated")
                return False
            
            first_strategy = strategies[0]
            if not first_strategy.get('lending_protection'):
                self.log_test("Lending Strategies", False, "Missing lending_protection flag")
                return False
            
            if not first_strategy.get('protection_type'):
                self.log_test("Lending Strategies", False, "Missing protection_type")
                return False
            
            self.log_test("Lending Workflow", True, f"Generated {len(strategies)} lending strategies")
            return True
            
        except Exception as e:
            self.log_test("Lending Workflow", False, f"Error: {str(e)}")
            return False
    
    def test_mode_switching(self):
        """Test switching between institutional and lending modes"""
        try:
            # Test institutional mode
            inst_response = self.session.post(f"{self.base_url}/api/analyze-portfolio", 
                json={'type': 'hedge_fund', 'mode': 'institutional'})
            
            if inst_response.status_code != 200:
                self.log_test("Mode Switching - Institutional", False, f"Status: {inst_response.status_code}")
                return False
            
            # Test lending mode
            lending_response = self.session.post(f"{self.base_url}/api/analyze-portfolio", 
                json={'mode': 'lending', 'loan_params': {'loan_amount': 500000, 'ltv_ratio': 80, 'protection_type': 'upside'}})
            
            if lending_response.status_code != 200:
                self.log_test("Mode Switching - Lending", False, f"Status: {lending_response.status_code}")
                return False
            
            self.log_test("Mode Switching", True, "Both modes work independently")
            return True
            
        except Exception as e:
            self.log_test("Mode Switching", False, f"Error: {str(e)}")
            return False
    
    def test_platform_exposure(self):
        """Test platform exposure endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/platform-exposure")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test("Platform Exposure", True, "Exposure data retrieved")
                    return True
                else:
                    self.log_test("Platform Exposure", False, "API returned success=false")
                    return False
            else:
                self.log_test("Platform Exposure", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Platform Exposure", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("🧪 Starting Lending Protection Integration Tests")
        print("=" * 60)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Market Data", self.test_market_data),
            ("Institutional Workflow", self.test_institutional_workflow),
            ("Lending Workflow", self.test_lending_workflow),
            ("Mode Switching", self.test_mode_switching),
            ("Platform Exposure", self.test_platform_exposure)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Testing: {test_name}")
            if test_func():
                passed += 1
            time.sleep(1)  # Brief pause between tests
        
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - Lending Protection Integration Successful!")
        else:
            print("⚠️ Some tests failed - Check implementation")
        
        return passed == total

def main():
    """Main test runner"""
    print("🚀 Lending Protection Integration Test Suite")
    print("Testing seamless integration of lending protection feature")
    print("=" * 60)
    
    # Check if server is running
    test_suite = LendingIntegrationTest()
    
    try:
        # Test if server is accessible
        response = requests.get("http://localhost:8080/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not accessible. Please start the server first:")
            print("   python app.py")
            return False
    except requests.exceptions.RequestException:
        print("❌ Server not running. Please start the server first:")
        print("   python app.py")
        return False
    
    # Run all tests
    success = test_suite.run_all_tests()
    
    if success:
        print("\n✅ Integration validation complete - Ready for production!")
    else:
        print("\n❌ Integration issues detected - Review implementation")
    
    return success

if __name__ == "__main__":
    main()
