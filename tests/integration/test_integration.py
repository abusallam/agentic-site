#!/usr/bin/env python3
"""
Integration Testing Suite for Agentic Site
End-to-end tests for full application functionality
"""

import pytest
import requests
import json
import time
from datetime import datetime
import concurrent.futures

class TestIntegration:
    """Integration testing class"""
    
    @classmethod
    def setup_class(cls):
        """Setup test environment"""
        cls.frontend_url = "http://217.79.255.54"
        cls.backend_url = "http://217.79.255.54:8953"
        cls.timeout = 20
    
    def test_full_stack_health(self):
        """Test both frontend and backend health"""
        # Test frontend
        frontend_response = requests.get(f"{self.frontend_url}/api/health", timeout=self.timeout)
        frontend_healthy = frontend_response.status_code == 200
        
        # Test backend
        try:
            backend_response = requests.get(f"{self.backend_url}/api/health", timeout=self.timeout)
            backend_healthy = backend_response.status_code == 200
        except requests.exceptions.RequestException:
            backend_healthy = False
        
        print(f"Frontend health: {'✅' if frontend_healthy else '❌'}")
        print(f"Backend health: {'✅' if backend_healthy else '❌'}")
        
        # At least frontend should be healthy
        assert frontend_healthy, "Frontend health check failed"
    
    def test_frontend_backend_communication(self):
        """Test communication between frontend and backend"""
        # Test if frontend can reach backend through proxy
        try:
            # This would test the /api/agent/ proxy route
            response = requests.get(f"{self.frontend_url}/api/agent/health", timeout=self.timeout)
            if response.status_code == 200:
                print("✅ Frontend-Backend communication working")
            else:
                print(f"⚠️ Frontend-Backend communication: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Frontend-Backend communication failed: {e}")
    
    def test_concurrent_requests(self):
        """Test system under concurrent load"""
        def make_request(url):
            try:
                response = requests.get(url, timeout=self.timeout)
                return response.status_code == 200
            except:
                return False
        
        # Test concurrent requests to frontend
        urls = [f"{self.frontend_url}/" for _ in range(10)]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(make_request, urls))
        
        success_rate = sum(results) / len(results)
        print(f"Concurrent request success rate: {success_rate:.2%}")
        
        # Should handle at least 70% of concurrent requests successfully
        assert success_rate >= 0.7, f"Concurrent request success rate too low: {success_rate:.2%}"
    
    def test_page_navigation_flow(self):
        """Test navigation between pages"""
        pages = [
            "/",
            "/about",
            "/services", 
            "/contact",
            "/consulting"
        ]
        
        navigation_results = {}
        
        for page in pages:
            try:
                response = requests.get(f"{self.frontend_url}{page}", timeout=self.timeout)
                navigation_results[page] = response.status_code
                
                # Check for basic HTML structure
                if response.status_code == 200:
                    assert "<html" in response.text.lower()
                    assert "</html>" in response.text.lower()
                    
            except requests.exceptions.RequestException as e:
                navigation_results[page] = f"Error: {e}"
        
        print("Page navigation results:")
        for page, result in navigation_results.items():
            status = "✅" if result == 200 else "❌" if isinstance(result, int) else "⚠️"
            print(f"  {page}: {status} {result}")
        
        # At least homepage should work
        assert navigation_results["/"] == 200, "Homepage navigation failed"
    
    def test_api_integration(self):
        """Test API integration between services"""
        api_tests = []
        
        # Test frontend API routes
        frontend_apis = [
            "/api/health",
        ]
        
        for api in frontend_apis:
            try:
                response = requests.get(f"{self.frontend_url}{api}", timeout=self.timeout)
                api_tests.append({
                    "endpoint": f"Frontend{api}",
                    "status": response.status_code,
                    "success": response.status_code == 200
                })
            except requests.exceptions.RequestException as e:
                api_tests.append({
                    "endpoint": f"Frontend{api}",
                    "status": f"Error: {e}",
                    "success": False
                })
        
        # Test backend API routes
        backend_apis = [
            "/api/health",
            "/api/status"
        ]
        
        for api in backend_apis:
            try:
                response = requests.get(f"{self.backend_url}{api}", timeout=self.timeout)
                api_tests.append({
                    "endpoint": f"Backend{api}",
                    "status": response.status_code,
                    "success": response.status_code == 200
                })
            except requests.exceptions.RequestException as e:
                api_tests.append({
                    "endpoint": f"Backend{api}",
                    "status": f"Error: {e}",
                    "success": False
                })
        
        print("API Integration Results:")
        for test in api_tests:
            status = "✅" if test["success"] else "❌"
            print(f"  {test['endpoint']}: {status} {test['status']}")
        
        # At least one API should work
        successful_apis = sum(1 for test in api_tests if test["success"])
        assert successful_apis > 0, "No APIs are working"
    
    def test_docker_container_health(self):
        """Test Docker container health (if accessible)"""
        # This test would require SSH access to check container status
        # For now, we'll test the application endpoints as a proxy for container health
        
        services = {
            "frontend": f"{self.frontend_url}/api/health",
            "backend": f"{self.backend_url}/api/health"
        }
        
        container_health = {}
        
        for service, url in services.items():
            try:
                response = requests.get(url, timeout=self.timeout)
                container_health[service] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds()
                }
            except requests.exceptions.RequestException:
                container_health[service] = {
                    "status": "unreachable",
                    "response_time": None
                }
        
        print("Container Health Status:")
        for service, health in container_health.items():
            status_icon = "✅" if health["status"] == "healthy" else "❌"
            response_time = f" ({health['response_time']:.3f}s)" if health["response_time"] else ""
            print(f"  {service}: {status_icon} {health['status']}{response_time}")
        
        # At least frontend container should be healthy
        assert container_health["frontend"]["status"] == "healthy", "Frontend container is not healthy"
    
    def test_error_handling_integration(self):
        """Test error handling across the stack"""
        error_scenarios = [
            # Non-existent pages
            {"url": f"{self.frontend_url}/nonexistent-page", "expected": [404]},
            {"url": f"{self.backend_url}/nonexistent-api", "expected": [404, 405]},
            
            # Invalid API calls
            {"url": f"{self.frontend_url}/api/invalid", "expected": [404, 405]},
        ]
        
        error_results = []
        
        for scenario in error_scenarios:
            try:
                response = requests.get(scenario["url"], timeout=self.timeout)
                success = response.status_code in scenario["expected"]
                error_results.append({
                    "url": scenario["url"],
                    "expected": scenario["expected"],
                    "actual": response.status_code,
                    "success": success
                })
            except requests.exceptions.RequestException as e:
                error_results.append({
                    "url": scenario["url"],
                    "expected": scenario["expected"],
                    "actual": f"Connection Error: {e}",
                    "success": False
                })
        
        print("Error Handling Results:")
        for result in error_results:
            status = "✅" if result["success"] else "❌"
            print(f"  {result['url']}: {status} Expected {result['expected']}, Got {result['actual']}")
    
    def test_performance_integration(self):
        """Test overall system performance"""
        performance_tests = [
            {"name": "Homepage Load", "url": f"{self.frontend_url}/"},
            {"name": "API Health Check", "url": f"{self.frontend_url}/api/health"},
            {"name": "About Page Load", "url": f"{self.frontend_url}/about"},
        ]
        
        performance_results = []
        
        for test in performance_tests:
            start_time = time.time()
            try:
                response = requests.get(test["url"], timeout=self.timeout)
                load_time = time.time() - start_time
                
                performance_results.append({
                    "name": test["name"],
                    "load_time": load_time,
                    "status_code": response.status_code,
                    "success": response.status_code == 200 and load_time < 10.0
                })
            except requests.exceptions.RequestException as e:
                load_time = time.time() - start_time
                performance_results.append({
                    "name": test["name"],
                    "load_time": load_time,
                    "status_code": f"Error: {e}",
                    "success": False
                })
        
        print("Performance Test Results:")
        for result in performance_results:
            status = "✅" if result["success"] else "❌"
            print(f"  {result['name']}: {status} {result['load_time']:.3f}s - {result['status_code']}")
        
        # At least homepage should load quickly
        homepage_result = next((r for r in performance_results if "Homepage" in r["name"]), None)
        if homepage_result:
            assert homepage_result["success"], f"Homepage performance test failed: {homepage_result}"
    
    def test_data_flow_integration(self):
        """Test data flow between components"""
        # Test if frontend can display data from backend
        try:
            # Get data from backend
            backend_response = requests.get(f"{self.backend_url}/api/health", timeout=self.timeout)
            
            if backend_response.status_code == 200:
                # Check if frontend can access this data through proxy
                frontend_proxy_response = requests.get(f"{self.frontend_url}/api/agent/health", timeout=self.timeout)
                
                if frontend_proxy_response.status_code == 200:
                    print("✅ Data flow integration working")
                else:
                    print(f"⚠️ Data flow integration issue: {frontend_proxy_response.status_code}")
            else:
                print("⚠️ Backend not available for data flow test")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Data flow integration test failed: {e}")

def run_integration_tests():
    """Run all integration tests"""
    print("🧪 Running Integration Tests...")
    print("=" * 50)
    
    # Run pytest
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes"
    ])

if __name__ == "__main__":
    run_integration_tests()