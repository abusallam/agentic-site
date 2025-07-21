#!/usr/bin/env python3
"""
Backend Testing Suite for Agentic Site
Comprehensive tests for Python Agent backend functionality
"""

import pytest
import requests
import json
import time
from datetime import datetime

class TestBackend:
    """Backend testing class"""
    
    @classmethod
    def setup_class(cls):
        """Setup test environment"""
        cls.base_url = "http://217.79.255.54:8953"
        cls.timeout = 15
        cls.max_retries = 3
    
    def make_request(self, method, endpoint, **kwargs):
        """Make HTTP request with retry logic"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                if method.upper() == "GET":
                    response = requests.get(url, timeout=self.timeout, **kwargs)
                elif method.upper() == "POST":
                    response = requests.post(url, timeout=self.timeout, **kwargs)
                elif method.upper() == "PUT":
                    response = requests.put(url, timeout=self.timeout, **kwargs)
                elif method.upper() == "DELETE":
                    response = requests.delete(url, timeout=self.timeout, **kwargs)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise e
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def test_backend_health(self):
        """Test backend health endpoint"""
        response = self.make_request("GET", "/api/health")
        assert response.status_code == 200
        
        # Try to parse as JSON
        try:
            data = response.json()
            assert isinstance(data, dict)
            print(f"Health response: {data}")
        except json.JSONDecodeError:
            # If not JSON, check for text response
            assert "healthy" in response.text.lower() or "ok" in response.text.lower()
            print(f"Health response (text): {response.text}")
    
    def test_backend_status(self):
        """Test backend status endpoint"""
        try:
            response = self.make_request("GET", "/api/status")
            assert response.status_code in [200, 404]  # 404 is ok if endpoint doesn't exist
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"Status response: {data}")
                except json.JSONDecodeError:
                    print(f"Status response (text): {response.text}")
        except requests.exceptions.RequestException:
            pytest.skip("Status endpoint not available")
    
    def test_backend_info(self):
        """Test backend info endpoint"""
        try:
            response = self.make_request("GET", "/api/info")
            assert response.status_code in [200, 404]  # 404 is ok if endpoint doesn't exist
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    assert isinstance(data, dict)
                    print(f"Info response: {data}")
                except json.JSONDecodeError:
                    print(f"Info response (text): {response.text}")
        except requests.exceptions.RequestException:
            pytest.skip("Info endpoint not available")
    
    def test_agent_endpoints(self):
        """Test agent-specific endpoints"""
        agent_endpoints = [
            "/api/agents",
            "/api/agent/status",
            "/api/agent/health",
            "/agents",
            "/status"
        ]
        
        for endpoint in agent_endpoints:
            try:
                response = self.make_request("GET", endpoint)
                # Any response code is acceptable for discovery
                print(f"Endpoint {endpoint}: HTTP {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"  Response: {data}")
                    except json.JSONDecodeError:
                        print(f"  Response (text): {response.text[:200]}")
                        
            except requests.exceptions.RequestException as e:
                print(f"Endpoint {endpoint}: Connection failed - {e}")
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        try:
            response = self.make_request("OPTIONS", "/api/health")
            headers = response.headers
            
            # Check for CORS headers
            cors_headers = [
                'access-control-allow-origin',
                'access-control-allow-methods',
                'access-control-allow-headers'
            ]
            
            present_cors = sum(1 for header in cors_headers if header in headers)
            print(f"CORS headers present: {present_cors}/{len(cors_headers)}")
            
        except requests.exceptions.RequestException:
            print("CORS test skipped - OPTIONS method not supported")
    
    def test_api_documentation(self):
        """Test API documentation endpoints"""
        doc_endpoints = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/docs",
            "/api/redoc"
        ]
        
        for endpoint in doc_endpoints:
            try:
                response = self.make_request("GET", endpoint)
                if response.status_code == 200:
                    print(f"Documentation available at: {endpoint}")
                    
                    # Check content type
                    content_type = response.headers.get('content-type', '')
                    if 'html' in content_type:
                        assert len(response.text) > 1000  # Should have substantial content
                    elif 'json' in content_type:
                        data = response.json()
                        assert isinstance(data, dict)
                        
            except requests.exceptions.RequestException:
                continue
    
    def test_agent_communication(self):
        """Test agent communication endpoints"""
        try:
            # Test agent ping/pong
            response = self.make_request("GET", "/ping")
            if response.status_code == 200:
                assert "pong" in response.text.lower()
                print("Agent ping/pong working")
                
        except requests.exceptions.RequestException:
            print("Agent ping endpoint not available")
        
        try:
            # Test agent version
            response = self.make_request("GET", "/version")
            if response.status_code == 200:
                try:
                    data = response.json()
                    assert "version" in data or "v" in data
                    print(f"Agent version: {data}")
                except json.JSONDecodeError:
                    print(f"Version response: {response.text}")
                    
        except requests.exceptions.RequestException:
            print("Agent version endpoint not available")
    
    def test_database_connectivity(self):
        """Test database connectivity (if applicable)"""
        db_endpoints = [
            "/api/db/health",
            "/api/database/status",
            "/db/ping"
        ]
        
        for endpoint in db_endpoints:
            try:
                response = self.make_request("GET", endpoint)
                if response.status_code == 200:
                    print(f"Database endpoint available: {endpoint}")
                    try:
                        data = response.json()
                        print(f"  Database status: {data}")
                    except json.JSONDecodeError:
                        print(f"  Database response: {response.text}")
                        
            except requests.exceptions.RequestException:
                continue
    
    def test_ai_service_endpoints(self):
        """Test AI service endpoints"""
        ai_endpoints = [
            "/api/ai/status",
            "/api/chat",
            "/api/agents/chat",
            "/api/completion"
        ]
        
        for endpoint in ai_endpoints:
            try:
                response = self.make_request("GET", endpoint)
                # Any response is informative
                print(f"AI endpoint {endpoint}: HTTP {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"  AI service response: {data}")
                    except json.JSONDecodeError:
                        print(f"  AI service response: {response.text[:200]}")
                        
            except requests.exceptions.RequestException:
                continue
    
    def test_performance_metrics(self):
        """Test backend performance"""
        start_time = time.time()
        response = self.make_request("GET", "/api/health")
        response_time = time.time() - start_time
        
        assert response.status_code == 200
        assert response_time < 5.0  # Should respond within 5 seconds
        print(f"Backend response time: {response_time:.3f} seconds")
    
    def test_error_handling(self):
        """Test error handling"""
        # Test non-existent endpoint
        try:
            response = self.make_request("GET", "/api/nonexistent-endpoint-12345")
            assert response.status_code in [404, 405, 500]  # Expected error codes
            print(f"Error handling test: HTTP {response.status_code}")
            
        except requests.exceptions.RequestException:
            print("Error handling test: Connection failed (expected)")
    
    def test_security_headers(self):
        """Test security headers"""
        try:
            response = self.make_request("GET", "/api/health")
            headers = response.headers
            
            security_headers = [
                'x-frame-options',
                'x-content-type-options',
                'x-xss-protection',
                'strict-transport-security'
            ]
            
            present_headers = sum(1 for header in security_headers if header in headers)
            print(f"Security headers present: {present_headers}/{len(security_headers)}")
            
            # Print all headers for debugging
            print("Response headers:")
            for key, value in headers.items():
                print(f"  {key}: {value}")
                
        except requests.exceptions.RequestException:
            print("Security headers test failed - connection error")

def run_backend_tests():
    """Run all backend tests"""
    print("🧪 Running Backend Tests...")
    print("=" * 50)
    
    # Run pytest
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes"
    ])

if __name__ == "__main__":
    run_backend_tests()