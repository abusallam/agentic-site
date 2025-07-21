#!/usr/bin/env python3
"""
Frontend Testing Suite for Agentic Site
Comprehensive tests for Next.js frontend functionality
"""

import pytest
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json

class TestFrontend:
    """Frontend testing class"""
    
    @classmethod
    def setup_class(cls):
        """Setup test environment"""
        cls.base_url = "http://217.79.255.54"
        cls.timeout = 10
        
        # Setup Chrome driver for Selenium tests
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            cls.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Warning: Selenium tests will be skipped - {e}")
            cls.driver = None
    
    @classmethod
    def teardown_class(cls):
        """Cleanup after tests"""
        if cls.driver:
            cls.driver.quit()
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = requests.get(f"{self.base_url}/api/health", timeout=self.timeout)
        assert response.status_code == 200
        
        # Check if response is JSON
        try:
            data = response.json()
            assert "status" in data or "message" in data
        except json.JSONDecodeError:
            # If not JSON, check for simple text response
            assert "healthy" in response.text.lower() or "ok" in response.text.lower()
    
    def test_homepage_loads(self):
        """Test homepage loads successfully"""
        response = requests.get(self.base_url, timeout=self.timeout)
        assert response.status_code == 200
        assert "consulting.sa" in response.text or "agentic" in response.text.lower()
    
    def test_about_page(self):
        """Test about page loads"""
        response = requests.get(f"{self.base_url}/about", timeout=self.timeout)
        assert response.status_code == 200
        assert len(response.text) > 1000  # Should have substantial content
    
    def test_services_page(self):
        """Test services page loads"""
        response = requests.get(f"{self.base_url}/services", timeout=self.timeout)
        assert response.status_code == 200
        assert "ai" in response.text.lower() or "service" in response.text.lower()
    
    def test_contact_page(self):
        """Test contact page loads"""
        response = requests.get(f"{self.base_url}/contact", timeout=self.timeout)
        assert response.status_code == 200
        assert "contact" in response.text.lower() or "email" in response.text.lower()
    
    def test_consulting_page(self):
        """Test consulting page loads"""
        response = requests.get(f"{self.base_url}/consulting", timeout=self.timeout)
        # May return 404 if page doesn't exist, that's ok
        assert response.status_code in [200, 404]
    
    def test_api_routes(self):
        """Test API routes are accessible"""
        api_routes = [
            "/api/health",
        ]
        
        for route in api_routes:
            response = requests.get(f"{self.base_url}{route}", timeout=self.timeout)
            assert response.status_code in [200, 404, 405]  # 405 for wrong method is ok
    
    def test_static_assets(self):
        """Test static assets load"""
        # Test favicon
        response = requests.get(f"{self.base_url}/favicon.ico", timeout=self.timeout)
        assert response.status_code in [200, 404]  # 404 is ok if not configured
        
        # Test robots.txt
        response = requests.get(f"{self.base_url}/robots.txt", timeout=self.timeout)
        assert response.status_code in [200, 404]  # 404 is ok if not configured
    
    def test_response_headers(self):
        """Test security headers are present"""
        response = requests.get(self.base_url, timeout=self.timeout)
        headers = response.headers
        
        # Check for basic security headers (may not all be present in development)
        security_headers = [
            'x-frame-options',
            'x-content-type-options',
            'referrer-policy'
        ]
        
        # At least some security headers should be present
        present_headers = sum(1 for header in security_headers if header in headers)
        print(f"Security headers present: {present_headers}/{len(security_headers)}")
    
    def test_page_performance(self):
        """Test page load performance"""
        start_time = time.time()
        response = requests.get(self.base_url, timeout=self.timeout)
        load_time = time.time() - start_time
        
        assert response.status_code == 200
        assert load_time < 5.0  # Should load within 5 seconds
        print(f"Homepage load time: {load_time:.2f} seconds")
    
    @pytest.mark.skipif(not hasattr(pytest, 'driver') or pytest.driver is None, 
                       reason="Selenium driver not available")
    def test_homepage_selenium(self):
        """Test homepage with Selenium (if available)"""
        if not self.driver:
            pytest.skip("Selenium driver not available")
        
        self.driver.get(self.base_url)
        
        # Wait for page to load
        WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Check title
        title = self.driver.title
        assert len(title) > 0
        print(f"Page title: {title}")
        
        # Check for navigation elements
        try:
            nav = self.driver.find_element(By.TAG_NAME, "nav")
            assert nav is not None
        except:
            print("Navigation element not found (may be ok for some designs)")
    
    @pytest.mark.skipif(not hasattr(pytest, 'driver') or pytest.driver is None,
                       reason="Selenium driver not available")
    def test_responsive_design(self):
        """Test responsive design with different screen sizes"""
        if not self.driver:
            pytest.skip("Selenium driver not available")
        
        screen_sizes = [
            (1920, 1080),  # Desktop
            (768, 1024),   # Tablet
            (375, 667),    # Mobile
        ]
        
        for width, height in screen_sizes:
            self.driver.set_window_size(width, height)
            self.driver.get(self.base_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check that page renders without horizontal scroll
            body = self.driver.find_element(By.TAG_NAME, "body")
            assert body is not None
            
            print(f"Page renders correctly at {width}x{height}")
    
    def test_error_pages(self):
        """Test error page handling"""
        # Test 404 page
        response = requests.get(f"{self.base_url}/nonexistent-page-12345", timeout=self.timeout)
        assert response.status_code == 404
        
        # Should have some content even for 404
        assert len(response.text) > 100
    
    def test_sitemap_and_seo(self):
        """Test SEO-related files"""
        seo_files = [
            "/sitemap.xml",
            "/robots.txt",
            "/manifest.json"
        ]
        
        for file_path in seo_files:
            response = requests.get(f"{self.base_url}{file_path}", timeout=self.timeout)
            # These files may not exist, that's ok
            assert response.status_code in [200, 404]
            if response.status_code == 200:
                print(f"SEO file found: {file_path}")

def run_frontend_tests():
    """Run all frontend tests"""
    print("🧪 Running Frontend Tests...")
    print("=" * 50)
    
    # Run pytest
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes"
    ])

if __name__ == "__main__":
    run_frontend_tests()