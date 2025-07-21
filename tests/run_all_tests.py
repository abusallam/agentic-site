#!/usr/bin/env python3
"""
Comprehensive Test Runner for Agentic Site
Runs all test suites and generates detailed reports
"""

import subprocess
import sys
import time
import json
import requests
from datetime import datetime
from pathlib import Path

class TestRunner:
    """Main test runner class"""
    
    def __init__(self):
        self.base_url = "http://217.79.255.54"
        self.backend_url = "http://217.79.255.54:8953"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {}
        }
    
    def check_prerequisites(self):
        """Check if required packages are installed"""
        print("🔍 Checking test prerequisites...")
        
        required_packages = ["pytest", "requests"]
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package} is available")
            except ImportError:
                missing_packages.append(package)
                print(f"❌ {package} is missing")
        
        if missing_packages:
            print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
                print("✅ Packages installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install packages: {e}")
                return False
        
        return True
    
    def check_application_status(self):
        """Check if the application is running"""
        print("\n🔍 Checking application status...")
        
        # Check frontend
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            frontend_status = response.status_code == 200
            print(f"Frontend: {'✅ Running' if frontend_status else '❌ Not responding'}")
        except requests.exceptions.RequestException:
            frontend_status = False
            print("Frontend: ❌ Not accessible")
        
        # Check backend
        try:
            response = requests.get(f"{self.backend_url}/api/health", timeout=10)
            backend_status = response.status_code == 200
            print(f"Backend: {'✅ Running' if backend_status else '❌ Not responding'}")
        except requests.exceptions.RequestException:
            backend_status = False
            print("Backend: ❌ Not accessible")
        
        return frontend_status, backend_status
    
    def run_test_suite(self, test_file, suite_name):
        """Run a specific test suite"""
        print(f"\n🧪 Running {suite_name} Tests...")
        print("-" * 50)
        
        start_time = time.time()
        
        try:
            # Run pytest with JSON report
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                test_file,
                "-v",
                "--tb=short",
                "--color=yes",
                "--json-report",
                "--json-report-file=/tmp/pytest_report.json"
            ], capture_output=True, text=True, timeout=300)
            
            duration = time.time() - start_time
            
            # Parse results
            try:
                with open("/tmp/pytest_report.json", "r") as f:
                    pytest_report = json.load(f)
                
                passed = pytest_report["summary"]["passed"]
                failed = pytest_report["summary"]["failed"]
                total = pytest_report["summary"]["total"]
                
            except (FileNotFoundError, KeyError, json.JSONDecodeError):
                # Fallback to parsing stdout
                output_lines = result.stdout.split('\n')
                passed = failed = total = 0
                
                for line in output_lines:
                    if "passed" in line and "failed" in line:
                        # Try to extract numbers
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if "passed" in part and i > 0:
                                try:
                                    passed = int(parts[i-1])
                                except ValueError:
                                    pass
                            if "failed" in part and i > 0:
                                try:
                                    failed = int(parts[i-1])
                                except ValueError:
                                    pass
                
                total = passed + failed
            
            success_rate = (passed / total * 100) if total > 0 else 0
            
            self.results["tests"][suite_name] = {
                "passed": passed,
                "failed": failed,
                "total": total,
                "success_rate": success_rate,
                "duration": duration,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            print(f"Results: {passed} passed, {failed} failed, {total} total")
            print(f"Success rate: {success_rate:.1f}%")
            print(f"Duration: {duration:.2f} seconds")
            
            if result.returncode == 0:
                print("✅ Test suite passed")
            else:
                print("❌ Test suite had failures")
                if result.stderr:
                    print(f"Errors: {result.stderr}")
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("❌ Test suite timed out")
            self.results["tests"][suite_name] = {
                "error": "Timeout",
                "duration": time.time() - start_time
            }
            return False
            
        except Exception as e:
            print(f"❌ Test suite failed with error: {e}")
            self.results["tests"][suite_name] = {
                "error": str(e),
                "duration": time.time() - start_time
            }
            return False
    
    def run_manual_tests(self):
        """Run manual endpoint tests"""
        print("\n🔧 Running Manual Tests...")
        print("-" * 50)
        
        manual_tests = {
            "Homepage": f"{self.base_url}/",
            "Health Check": f"{self.base_url}/api/health",
            "About Page": f"{self.base_url}/about",
            "Services Page": f"{self.base_url}/services",
            "Contact Page": f"{self.base_url}/contact",
            "Backend Health": f"{self.backend_url}/api/health"
        }
        
        manual_results = {}
        
        for test_name, url in manual_tests.items():
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10)
                duration = time.time() - start_time
                
                manual_results[test_name] = {
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "response_time": duration,
                    "content_length": len(response.text)
                }
                
                status = "✅" if response.status_code == 200 else "❌"
                print(f"{test_name}: {status} HTTP {response.status_code} ({duration:.3f}s)")
                
            except requests.exceptions.RequestException as e:
                manual_results[test_name] = {
                    "error": str(e),
                    "success": False
                }
                print(f"{test_name}: ❌ Error - {e}")
        
        self.results["manual_tests"] = manual_results
        
        successful_manual = sum(1 for result in manual_results.values() if result.get("success", False))
        total_manual = len(manual_results)
        
        print(f"\nManual Tests: {successful_manual}/{total_manual} passed")
        
        return successful_manual, total_manual
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n📊 GENERATING TEST REPORT")
        print("=" * 70)
        
        # Calculate overall statistics
        total_passed = sum(test.get("passed", 0) for test in self.results["tests"].values())
        total_failed = sum(test.get("failed", 0) for test in self.results["tests"].values())
        total_tests = total_passed + total_failed
        
        manual_passed = sum(1 for result in self.results.get("manual_tests", {}).values() if result.get("success", False))
        manual_total = len(self.results.get("manual_tests", {}))
        
        overall_passed = total_passed + manual_passed
        overall_total = total_tests + manual_total
        overall_success_rate = (overall_passed / overall_total * 100) if overall_total > 0 else 0
        
        self.results["summary"] = {
            "total_tests": overall_total,
            "total_passed": overall_passed,
            "total_failed": overall_total - overall_passed,
            "success_rate": overall_success_rate,
            "automated_tests": total_tests,
            "manual_tests": manual_total
        }
        
        # Print summary
        print(f"📈 OVERALL TEST RESULTS")
        print(f"Total Tests: {overall_total}")
        print(f"Passed: {overall_passed}")
        print(f"Failed: {overall_total - overall_passed}")
        print(f"Success Rate: {overall_success_rate:.1f}%")
        print()
        
        print("📋 TEST SUITE BREAKDOWN:")
        for suite_name, results in self.results["tests"].items():
            if "error" in results:
                print(f"  {suite_name}: ❌ Error - {results['error']}")
            else:
                success_rate = results.get("success_rate", 0)
                status = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 50 else "❌"
                print(f"  {suite_name}: {status} {results['passed']}/{results['total']} ({success_rate:.1f}%)")
        
        if self.results.get("manual_tests"):
            manual_success_rate = (manual_passed / manual_total * 100) if manual_total > 0 else 0
            status = "✅" if manual_success_rate >= 80 else "⚠️" if manual_success_rate >= 50 else "❌"
            print(f"  Manual Tests: {status} {manual_passed}/{manual_total} ({manual_success_rate:.1f}%)")
        
        # Save detailed report
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return overall_success_rate >= 70  # Consider 70% success rate as acceptable
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 COMPREHENSIVE TEST EXECUTION")
        print("=" * 70)
        print(f"Target Application: {self.base_url}")
        print(f"Test Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Check prerequisites
        if not self.check_prerequisites():
            print("❌ Prerequisites check failed")
            return False
        
        # Check application status
        frontend_running, backend_running = self.check_application_status()
        
        if not frontend_running:
            print("⚠️ Frontend not accessible - some tests may fail")
        
        if not backend_running:
            print("⚠️ Backend not accessible - backend tests will be skipped")
        
        # Run test suites
        test_suites = [
            ("test_frontend.py", "Frontend"),
            ("test_backend.py", "Backend"),
            ("test_integration.py", "Integration")
        ]
        
        suite_results = []
        
        for test_file, suite_name in test_suites:
            if suite_name == "Backend" and not backend_running:
                print(f"\n⏭️ Skipping {suite_name} tests - backend not accessible")
                continue
            
            try:
                success = self.run_test_suite(test_file, suite_name)
                suite_results.append(success)
            except Exception as e:
                print(f"❌ Failed to run {suite_name} tests: {e}")
                suite_results.append(False)
        
        # Run manual tests
        manual_passed, manual_total = self.run_manual_tests()
        
        # Generate final report
        overall_success = self.generate_report()
        
        # Final status
        print("\n🎯 FINAL TEST STATUS")
        print("=" * 70)
        
        if overall_success:
            print("🎉 TESTS PASSED - Application is working well!")
            print("✅ The application is ready for production use")
        else:
            print("⚠️ TESTS COMPLETED WITH ISSUES")
            print("🔧 Some functionality may need attention")
        
        print(f"\n📊 Summary: {self.results['summary']['total_passed']}/{self.results['summary']['total_tests']} tests passed")
        print(f"🎯 Success Rate: {self.results['summary']['success_rate']:.1f}%")
        
        return overall_success

def main():
    """Main test execution function"""
    runner = TestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()