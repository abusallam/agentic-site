#!/usr/bin/env python3
"""
Comprehensive UI testing for the deployed agentic-site
"""

import requests
import time
import json
from datetime import datetime
import re

def test_url(url, description, expected_status=200, timeout=30):
    """Test URL accessibility with detailed analysis"""
    print(f"🌐 Testing {description}: {url}")
    try:
        response = requests.get(url, timeout=timeout, verify=False)
        
        # Basic status check
        if response.status_code == expected_status:
            print(f"✅ {description} - Status: {response.status_code}")
            status = True
        else:
            print(f"⚠️ {description} - Status: {response.status_code}")
            status = False
        
        # Content analysis
        if response.text:
            content = response.text.lower()
            content_length = len(response.text)
            
            # Check for key elements
            checks = {
                "Brand Name": "consulting.sa" in content or "المستشار" in content,
                "AI Content": "ai" in content or "artificial intelligence" in content or "ذكاء اصطناعي" in content,
                "Navigation": "nav" in content or "menu" in content,
                "Footer": "footer" in content or "copyright" in content,
                "Contact Info": "contact" in content or "email" in content,
                "Services": "service" in content or "خدمات" in content,
                "No Errors": "error" not in content and "404" not in content and "500" not in content
            }
            
            print(f"  📊 Content Length: {content_length} characters")
            
            for check_name, passed in checks.items():
                icon = "✅" if passed else "❌"
                print(f"  {icon} {check_name}")
            
            # Performance check
            load_time = response.elapsed.total_seconds()
            if load_time < 2:
                print(f"  ⚡ Fast load time: {load_time:.2f}s")
            elif load_time < 5:
                print(f"  ⏱️ Acceptable load time: {load_time:.2f}s")
            else:
                print(f"  🐌 Slow load time: {load_time:.2f}s")
        
        return status, response
        
    except Exception as e:
        print(f"❌ {description} failed: {str(e)}")
        return False, None

def test_responsive_design(base_url):
    """Test responsive design by checking different viewport sizes"""
    print("\n📱 TESTING RESPONSIVE DESIGN")
    print("-" * 40)
    
    # Simulate different devices with User-Agent headers
    devices = {
        "Desktop": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mobile": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
        "Tablet": "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
    }
    
    for device, user_agent in devices.items():
        try:
            headers = {"User-Agent": user_agent}
            response = requests.get(base_url, headers=headers, timeout=30, verify=False)
            
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for responsive elements
                responsive_checks = {
                    "Viewport Meta": "viewport" in content,
                    "Responsive Classes": "responsive" in content or "sm:" in content or "md:" in content,
                    "Mobile Menu": "mobile" in content or "hamburger" in content,
                    "Flexible Layout": "flex" in content or "grid" in content
                }
                
                print(f"  📱 {device} Device:")
                for check, passed in responsive_checks.items():
                    icon = "✅" if passed else "❌"
                    print(f"    {icon} {check}")
            else:
                print(f"  ❌ {device} - Status: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ {device} failed: {str(e)}")

def test_accessibility(base_url):
    """Test basic accessibility features"""
    print("\n♿ TESTING ACCESSIBILITY")
    print("-" * 40)
    
    try:
        response = requests.get(base_url, timeout=30, verify=False)
        
        if response.status_code == 200:
            content = response.text.lower()
            
            accessibility_checks = {
                "Alt Text": 'alt=' in content,
                "ARIA Labels": 'aria-' in content,
                "Semantic HTML": any(tag in content for tag in ['<header>', '<nav>', '<main>', '<footer>', '<section>', '<article>']),
                "Skip Links": 'skip' in content,
                "Focus Management": 'tabindex' in content or 'focus' in content,
                "Language Declaration": 'lang=' in content,
                "Heading Structure": '<h1>' in content and '<h2>' in content
            }
            
            for check, passed in accessibility_checks.items():
                icon = "✅" if passed else "❌"
                print(f"  {icon} {check}")
        else:
            print(f"  ❌ Failed to load page for accessibility testing")
            
    except Exception as e:
        print(f"  ❌ Accessibility test failed: {str(e)}")

def test_seo_elements(base_url):
    """Test SEO elements"""
    print("\n🔍 TESTING SEO ELEMENTS")
    print("-" * 40)
    
    try:
        response = requests.get(base_url, timeout=30, verify=False)
        
        if response.status_code == 200:
            content = response.text
            
            seo_checks = {
                "Title Tag": '<title>' in content,
                "Meta Description": 'name="description"' in content,
                "Open Graph": 'property="og:' in content,
                "Twitter Cards": 'name="twitter:' in content,
                "Canonical URL": 'rel="canonical"' in content,
                "Structured Data": 'application/ld+json' in content or 'schema.org' in content,
                "Robots Meta": 'name="robots"' in content
            }
            
            for check, passed in seo_checks.items():
                icon = "✅" if passed else "❌"
                print(f"  {icon} {check}")
                
            # Extract and show title
            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
            if title_match:
                print(f"  📝 Page Title: {title_match.group(1)}")
                
        else:
            print(f"  ❌ Failed to load page for SEO testing")
            
    except Exception as e:
        print(f"  ❌ SEO test failed: {str(e)}")

def test_performance(base_url):
    """Test performance metrics"""
    print("\n⚡ TESTING PERFORMANCE")
    print("-" * 40)
    
    # Test multiple requests to get average
    times = []
    for i in range(3):
        try:
            start_time = time.time()
            response = requests.get(base_url, timeout=30, verify=False)
            end_time = time.time()
            
            if response.status_code == 200:
                load_time = end_time - start_time
                times.append(load_time)
                print(f"  🔄 Request {i+1}: {load_time:.2f}s")
            else:
                print(f"  ❌ Request {i+1} failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Request {i+1} failed: {str(e)}")
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"  📊 Average Load Time: {avg_time:.2f}s")
        print(f"  📊 Fastest Load Time: {min_time:.2f}s")
        print(f"  📊 Slowest Load Time: {max_time:.2f}s")
        
        if avg_time < 2:
            print("  ✅ Excellent performance")
        elif avg_time < 4:
            print("  ⚠️ Good performance")
        else:
            print("  ❌ Poor performance")

def main():
    base_url = "http://217.79.255.54"
    https_url = "https://217.79.255.54"
    
    print("🧪 COMPREHENSIVE UI TESTING FOR AGENTIC-SITE")
    print("=" * 60)
    print(f"Base URL: {base_url}")
    print(f"HTTPS URL: {https_url}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test main pages
    print("\n📄 TESTING MAIN PAGES")
    print("-" * 40)
    
    pages_to_test = [
        ("/", "Homepage"),
        ("/about", "About Page"),
        ("/services", "Services Page"),
        ("/contact", "Contact Page"),
        ("/consulting", "Consulting Page"),
        ("/docs", "Documentation Page"),
        ("/privacy-policy", "Privacy Policy"),
        ("/api/health", "Health Endpoint")
    ]
    
    test_results = []
    
    for path, description in pages_to_test:
        url = base_url + path
        success, response = test_url(url, description)
        test_results.append((description, success))
        print()  # Add spacing between tests
    
    # Test HTTPS
    print("\n🔒 TESTING HTTPS")
    print("-" * 40)
    
    success, response = test_url(https_url, "HTTPS Homepage")
    test_results.append(("HTTPS Homepage", success))
    
    # Test responsive design
    test_responsive_design(base_url)
    
    # Test accessibility
    test_accessibility(base_url)
    
    # Test SEO
    test_seo_elements(base_url)
    
    # Test performance
    test_performance(base_url)
    
    # Test API endpoints
    print("\n🔌 TESTING API ENDPOINTS")
    print("-" * 40)
    
    api_endpoints = [
        ("/api/health", "Frontend Health API"),
        ("/api/customer/dashboard", "Customer Dashboard API"),
        ("/api/admin/stats", "Admin Stats API")
    ]
    
    for path, description in api_endpoints:
        url = base_url + path
        success, response = test_url(url, description, expected_status=[200, 401, 403, 404])  # Accept various statuses
        test_results.append((description, success))
    
    # Generate final report
    print("\n📊 FINAL TEST REPORT")
    print("=" * 60)
    
    passed_tests = sum(1 for _, success in test_results if success)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    print()
    
    print("📋 DETAILED RESULTS:")
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n🔗 ACCESS INFORMATION")
    print("-" * 40)
    print(f"🌐 Website: {base_url}")
    print(f"🔒 HTTPS: {https_url}")
    print(f"📱 Mobile: {base_url} (responsive)")
    print(f"🖥️ Desktop: {base_url}")
    
    print("\n📋 RECOMMENDATIONS")
    print("-" * 40)
    
    if success_rate >= 90:
        print("🎉 Excellent! The website is performing very well.")
    elif success_rate >= 75:
        print("✅ Good! The website is working well with minor issues.")
        print("💡 Consider fixing the failed tests for better performance.")
    elif success_rate >= 50:
        print("⚠️ Acceptable! The website is functional but needs improvements.")
        print("🔧 Focus on fixing the critical failed tests.")
    else:
        print("❌ Poor! The website has significant issues that need attention.")
        print("🚨 Immediate action required to fix critical problems.")
    
    # Save detailed report
    report = {
        "test_time": datetime.now().isoformat(),
        "base_url": base_url,
        "https_url": https_url,
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "success_rate": success_rate,
        "test_results": [{"name": name, "passed": success} for name, success in test_results]
    }
    
    with open("ui_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: ui_test_report.json")
    
    return success_rate >= 75

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)