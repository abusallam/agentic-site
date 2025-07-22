#!/usr/bin/env python3
"""
Simple deployment test to verify the application is working
"""

import requests
import json
from datetime import datetime

def test_endpoint(url, name):
    """Test a single endpoint"""
    try:
        print(f"🔧 Testing {name}: {url}")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ {name}: SUCCESS")
            
            # Try to show some content
            content = response.text[:200]
            if content:
                print(f"📝 Content preview: {content}...")
            
            return True
        else:
            print(f"❌ {name}: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ {name}: ERROR - {str(e)}")
        return False

def main():
    base_url = "http://217.79.255.54"
    
    print("🧪 SIMPLE DEPLOYMENT TEST")
    print("=" * 50)
    print(f"Testing: {base_url}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Test endpoints
    tests = [
        (f"{base_url}/", "Homepage"),
        (f"{base_url}/api/health", "Health Check"),
        (f"{base_url}/about", "About Page"),
        (f"{base_url}/services", "Services Page"),
        (f"{base_url}/contact", "Contact Page"),
        (f"{base_url}:8953/api/health", "Backend Health"),
        (f"{base_url}:3911/", "Frontend Direct"),
        (f"{base_url}:3911/api/health", "Frontend Health Direct"),
    ]
    
    results = []
    for url, name in tests:
        success = test_endpoint(url, name)
        results.append((name, success))
        print()
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    success_rate = (passed / total) * 100
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    print(f"\nResults: {passed}/{total} tests passed ({success_rate:.1f}%)")
    
    if passed >= 2:  # At least homepage and one other endpoint
        print("\n🎉 DEPLOYMENT IS WORKING!")
        print("The application is accessible and functional.")
    else:
        print("\n⚠️ DEPLOYMENT NEEDS ATTENTION")
        print("Some core functionality is not working.")
    
    return passed >= 2

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)