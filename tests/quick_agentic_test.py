#!/usr/bin/env python3
"""
Quick Agentic Test Suite
Tests the current deployed system with real endpoints
"""

import requests
import time
import json
from datetime import datetime

class QuickAgenticTest:
    def __init__(self):
        self.base_url = "http://217.79.255.54"
        self.backend_url = f"{self.base_url}:8001"
        self.frontend_url = f"{self.base_url}:3001"
        self.n8n_url = f"{self.base_url}:5680"
        self.results = []
    
    def test_service_health(self):
        """Test all service health endpoints."""
        print("🔍 Testing Service Health...")
        
        services = {
            "Backend": f"{self.backend_url}/health",
            "Frontend": f"{self.frontend_url}",
            "N8N": f"{self.n8n_url}/healthz"
        }
        
        for service, url in services.items():
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    print(f"  ✅ {service}: HEALTHY ({duration:.2f}s)")
                    self.results.append({"test": f"{service} Health", "status": "PASSED", "duration": duration})
                else:
                    print(f"  ❌ {service}: UNHEALTHY (HTTP {response.status_code})")
                    self.results.append({"test": f"{service} Health", "status": "FAILED", "error": f"HTTP {response.status_code}"})
            except Exception as e:
                print(f"  ❌ {service}: ERROR ({str(e)})")
                self.results.append({"test": f"{service} Health", "status": "FAILED", "error": str(e)})
    
    def test_n8n_functionality(self):
        """Test N8N functionality."""
        print("\n🔧 Testing N8N Functionality...")
        
        # Test N8N UI accessibility
        try:
            response = requests.get(f"{self.n8n_url}", timeout=10)
            if response.status_code == 200 and 'n8n' in response.text:
                print("  ✅ N8N UI: ACCESSIBLE")
                self.results.append({"test": "N8N UI Access", "status": "PASSED"})
            else:
                print("  ❌ N8N UI: NOT ACCESSIBLE")
                self.results.append({"test": "N8N UI Access", "status": "FAILED"})
        except Exception as e:
            print(f"  ❌ N8N UI: ERROR ({str(e)})")
            self.results.append({"test": "N8N UI Access", "status": "FAILED", "error": str(e)})
        
        # Test N8N Health
        try:
            response = requests.get(f"{self.n8n_url}/healthz", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                print(f"  ✅ N8N Health: {health_data.get('status', 'OK')}")
                self.results.append({"test": "N8N Health Check", "status": "PASSED", "health": health_data})
            else:
                print("  ❌ N8N Health: FAILED")
                self.results.append({"test": "N8N Health Check", "status": "FAILED"})
        except Exception as e:
            print(f"  ❌ N8N Health: ERROR ({str(e)})")
            self.results.append({"test": "N8N Health Check", "status": "FAILED", "error": str(e)})
        
        # Test N8N API (without auth for now)
        try:
            response = requests.get(f"{self.n8n_url}/rest/workflows", timeout=10)
            if response.status_code == 401:
                print("  ✅ N8N API: PROTECTED (Authentication required)")
                self.results.append({"test": "N8N API Protection", "status": "PASSED"})
            elif response.status_code == 200:
                print("  ⚠️  N8N API: ACCESSIBLE (No auth required)")
                self.results.append({"test": "N8N API Protection", "status": "WARNING"})
            else:
                print(f"  ❌ N8N API: UNEXPECTED ({response.status_code})")
                self.results.append({"test": "N8N API Protection", "status": "FAILED"})
        except Exception as e:
            print(f"  ❌ N8N API: ERROR ({str(e)})")
            self.results.append({"test": "N8N API Protection", "status": "FAILED", "error": str(e)})
    
    def test_backend_functionality(self):
        """Test backend functionality."""
        print("\n🤖 Testing Backend Functionality...")
        
        # Test health endpoint
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                print(f"  ✅ Backend Health: {health_data.get('status', 'OK')}")
                self.results.append({"test": "Backend Health", "status": "PASSED", "health": health_data})
                
                # Check service configurations
                services = health_data.get('services', {})
                for service, status in services.items():
                    if status == 'configured':
                        print(f"    ✅ {service.title()}: CONFIGURED")
                    else:
                        print(f"    ⚠️  {service.title()}: {status}")
            else:
                print("  ❌ Backend Health: FAILED")
                self.results.append({"test": "Backend Health", "status": "FAILED"})
        except Exception as e:
            print(f"  ❌ Backend Health: ERROR ({str(e)})")
            self.results.append({"test": "Backend Health", "status": "FAILED", "error": str(e)})
        
        # Test API endpoints
        endpoints = [
            "/",
            "/api/test",
            "/docs"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    print(f"  ✅ {endpoint}: ACCESSIBLE")
                    self.results.append({"test": f"Backend {endpoint}", "status": "PASSED"})
                else:
                    print(f"  ❌ {endpoint}: HTTP {response.status_code}")
                    self.results.append({"test": f"Backend {endpoint}", "status": "FAILED"})
            except Exception as e:
                print(f"  ❌ {endpoint}: ERROR ({str(e)})")
                self.results.append({"test": f"Backend {endpoint}", "status": "FAILED", "error": str(e)})
    
    def test_frontend_functionality(self):
        """Test frontend functionality."""
        print("\n🎨 Testing Frontend Functionality...")
        
        # Test main pages
        pages = [
            "/",
            "/about",
            "/services", 
            "/contact",
            "/consulting"
        ]
        
        for page in pages:
            try:
                response = requests.get(f"{self.frontend_url}{page}", timeout=10)
                if response.status_code == 200:
                    print(f"  ✅ {page}: ACCESSIBLE")
                    self.results.append({"test": f"Frontend {page}", "status": "PASSED"})
                else:
                    print(f"  ❌ {page}: HTTP {response.status_code}")
                    self.results.append({"test": f"Frontend {page}", "status": "FAILED"})
            except Exception as e:
                print(f"  ❌ {page}: ERROR ({str(e)})")
                self.results.append({"test": f"Frontend {page}", "status": "FAILED", "error": str(e)})
    
    def test_language_support(self):
        """Test Arabic/English language support."""
        print("\n🌐 Testing Language Support...")
        
        # Test if pages contain Arabic content
        try:
            response = requests.get(f"{self.frontend_url}", timeout=10)
            if response.status_code == 200:
                content = response.text
                
                # Check for Arabic characters
                has_arabic = any('\u0600' <= char <= '\u06FF' for char in content)
                
                # Check for English content
                has_english = any(word in content.lower() for word in ['consulting', 'services', 'about', 'contact'])
                
                if has_arabic and has_english:
                    print("  ✅ Bilingual Support: DETECTED (Arabic + English)")
                    self.results.append({"test": "Bilingual Support", "status": "PASSED"})
                elif has_english:
                    print("  ⚠️  Language Support: ENGLISH ONLY")
                    self.results.append({"test": "Bilingual Support", "status": "WARNING"})
                else:
                    print("  ❌ Language Support: UNCLEAR")
                    self.results.append({"test": "Bilingual Support", "status": "FAILED"})
            else:
                print("  ❌ Language Support: CANNOT TEST")
                self.results.append({"test": "Bilingual Support", "status": "FAILED"})
        except Exception as e:
            print(f"  ❌ Language Support: ERROR ({str(e)})")
            self.results.append({"test": "Bilingual Support", "status": "FAILED", "error": str(e)})
    
    def test_performance(self):
        """Test basic performance metrics."""
        print("\n⚡ Testing Performance...")
        
        # Test response times
        endpoints = [
            ("Frontend", f"{self.frontend_url}"),
            ("Backend", f"{self.backend_url}/health"),
            ("N8N", f"{self.n8n_url}/healthz")
        ]
        
        for name, url in endpoints:
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    if duration < 2.0:
                        print(f"  ✅ {name} Response Time: {duration:.2f}s (GOOD)")
                        self.results.append({"test": f"{name} Performance", "status": "PASSED", "duration": duration})
                    elif duration < 5.0:
                        print(f"  ⚠️  {name} Response Time: {duration:.2f}s (ACCEPTABLE)")
                        self.results.append({"test": f"{name} Performance", "status": "WARNING", "duration": duration})
                    else:
                        print(f"  ❌ {name} Response Time: {duration:.2f}s (SLOW)")
                        self.results.append({"test": f"{name} Performance", "status": "FAILED", "duration": duration})
                else:
                    print(f"  ❌ {name} Performance: HTTP {response.status_code}")
                    self.results.append({"test": f"{name} Performance", "status": "FAILED"})
            except Exception as e:
                print(f"  ❌ {name} Performance: ERROR ({str(e)})")
                self.results.append({"test": f"{name} Performance", "status": "FAILED", "error": str(e)})
    
    def test_integration(self):
        """Test system integration."""
        print("\n🔗 Testing System Integration...")
        
        # Test if all services are running together
        all_services_up = True
        service_count = 0
        
        services = [
            ("Frontend", f"{self.frontend_url}"),
            ("Backend", f"{self.backend_url}/health"),
            ("N8N", f"{self.n8n_url}/healthz")
        ]
        
        for name, url in services:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    service_count += 1
                else:
                    all_services_up = False
            except:
                all_services_up = False
        
        if service_count == len(services):
            print("  ✅ All Services: RUNNING")
            self.results.append({"test": "Service Integration", "status": "PASSED", "services_up": service_count})
        elif service_count > 0:
            print(f"  ⚠️  Partial Services: {service_count}/{len(services)} RUNNING")
            self.results.append({"test": "Service Integration", "status": "WARNING", "services_up": service_count})
        else:
            print("  ❌ No Services: RUNNING")
            self.results.append({"test": "Service Integration", "status": "FAILED", "services_up": service_count})
    
    def generate_report(self):
        """Generate test report."""
        print("\n" + "="*70)
        print("📊 QUICK AGENTIC TEST REPORT")
        print("="*70)
        
        passed = sum(1 for result in self.results if result.get("status") == "PASSED")
        warnings = sum(1 for result in self.results if result.get("status") == "WARNING")
        failed = sum(1 for result in self.results if result.get("status") == "FAILED")
        total = len(self.results)
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"📈 OVERALL RESULTS:")
        print(f"   Total Tests: {total}")
        print(f"   Passed: {passed}")
        print(f"   Warnings: {warnings}")
        print(f"   Failed: {failed}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Timestamp: {datetime.now().isoformat()}")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.results:
            status_icon = "✅" if result["status"] == "PASSED" else "⚠️" if result["status"] == "WARNING" else "❌"
            test_name = result["test"]
            status = result["status"]
            duration = f" ({result['duration']:.2f}s)" if "duration" in result else ""
            print(f"   {status_icon} {test_name}: {status}{duration}")
            
            if "error" in result:
                print(f"      Error: {result['error']}")
        
        print(f"\n🎯 RECOMMENDATIONS:")
        if success_rate >= 90:
            print("   🎉 Excellent! System is working very well.")
        elif success_rate >= 80:
            print("   ✅ Good! System is mostly functional with minor issues.")
        elif success_rate >= 70:
            print("   ⚠️  Acceptable! System is working but needs attention.")
        elif success_rate >= 50:
            print("   🔧 Issues detected! System needs significant fixes.")
        else:
            print("   🚨 Major problems! System requires immediate attention.")
        
        # Save results
        report_file = f"quick_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": total,
                    "passed": passed,
                    "warnings": warnings,
                    "failed": failed,
                    "success_rate": success_rate
                },
                "results": self.results
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {report_file}")
        
        return success_rate >= 70
    
    def run_all_tests(self):
        """Run all tests."""
        print("🚀 QUICK AGENTIC TEST SUITE")
        print("="*70)
        print(f"Target System: {self.base_url}")
        print(f"Test Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        self.test_service_health()
        self.test_n8n_functionality()
        self.test_backend_functionality()
        self.test_frontend_functionality()
        self.test_language_support()
        self.test_performance()
        self.test_integration()
        
        return self.generate_report()

def main():
    """Main test execution."""
    tester = QuickAgenticTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 TESTS COMPLETED SUCCESSFULLY!")
        exit(0)
    else:
        print("\n⚠️ TESTS COMPLETED WITH ISSUES!")
        exit(1)

if __name__ == "__main__":
    main()