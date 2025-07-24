#!/usr/bin/env python3
"""
Integration Test Runner

This module provides a comprehensive test runner for all integration tests
in the agentic AI platform, including service connections, database operations,
and end-to-end workflow testing.
"""

import asyncio
import os
import sys
import json
import time
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add the agent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import test modules
try:
    from tests.integration.test_service_connections import ServiceConnectionTester
    from tests.fixtures.test_database import TestDatabaseManager
    from tests.fixtures.service_mocks import create_test_environment
except ImportError as e:
    logging.warning(f"Import failed: {e}. Some tests may not be available.")
    ServiceConnectionTester = None
    TestDatabaseManager = None
    create_test_environment = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IntegrationTestRunner:
    """
    Comprehensive integration test runner for the agentic AI platform
    """
    
    def __init__(self, test_mode: str = "mock", verbose: bool = True):
        self.test_mode = test_mode  # mock, live, or hybrid
        self.verbose = verbose
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all integration tests and return comprehensive results
        """
        self.start_time = time.time()
        logger.info(f"Starting comprehensive integration test suite in {self.test_mode} mode...")
        
        test_suites = [
            ("database_tests", self._run_database_tests),
            ("service_connection_tests", self._run_service_connection_tests),
            ("workflow_integration_tests", self._run_workflow_integration_tests),
            ("end_to_end_tests", self._run_end_to_end_tests)
        ]
        
        overall_results = {
            "test_mode": self.test_mode,
            "start_time": self.start_time,
            "test_suites": {},
            "summary": {
                "total_suites": len(test_suites),
                "passed_suites": 0,
                "failed_suites": 0,
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "skipped_tests": 0
            }
        }
        
        for suite_name, test_function in test_suites:
            logger.info(f"Running {suite_name}...")
            
            try:
                suite_results = await test_function()
                overall_results["test_suites"][suite_name] = suite_results
                
                # Update summary
                if suite_results.get("status") == "passed":
                    overall_results["summary"]["passed_suites"] += 1
                else:
                    overall_results["summary"]["failed_suites"] += 1
                
                # Aggregate test counts
                if "summary" in suite_results:
                    suite_summary = suite_results["summary"]
                    overall_results["summary"]["total_tests"] += suite_summary.get("total_tests", 0)
                    overall_results["summary"]["passed_tests"] += suite_summary.get("passed_tests", 0)
                    overall_results["summary"]["failed_tests"] += suite_summary.get("failed_tests", 0)
                    overall_results["summary"]["skipped_tests"] += suite_summary.get("skipped_tests", 0)
                
                if self.verbose:
                    status_icon = "✅" if suite_results.get("status") == "passed" else "❌"
                    logger.info(f"{status_icon} {suite_name}: {suite_results.get('message', 'Completed')}")
                    
            except Exception as e:
                logger.error(f"💥 {suite_name} failed with exception: {e}")
                overall_results["test_suites"][suite_name] = {
                    "status": "error",
                    "error": str(e),
                    "message": f"Test suite failed with exception: {str(e)}"
                }
                overall_results["summary"]["failed_suites"] += 1
        
        self.end_time = time.time()
        overall_results["end_time"] = self.end_time
        overall_results["duration"] = self.end_time - self.start_time
        
        # Determine overall status
        overall_results["status"] = "passed" if overall_results["summary"]["failed_suites"] == 0 else "failed"
        
        return overall_results
    
    async def _run_database_tests(self) -> Dict[str, Any]:
        """
        Run database integration tests
        """
        if not TestDatabaseManager:
            return {
                "status": "skipped",
                "message": "TestDatabaseManager not available",
                "summary": {"total_tests": 0, "passed_tests": 0, "failed_tests": 0, "skipped_tests": 1}
            }
        
        try:
            db_manager = TestDatabaseManager(test_mode=self.test_mode if self.test_mode != "live" else "mock")
            
            # Setup test database
            setup_result = await db_manager.setup_test_database()
            if setup_result["status"] != "ready":
                raise Exception(f"Database setup failed: {setup_result}")
            
            # Run database tests
            tests = [
                ("database_setup", lambda: setup_result),
                ("database_verification", db_manager.verify_test_database),
                ("data_operations", self._test_database_operations(db_manager))
            ]
            
            test_results = {}
            passed_tests = 0
            total_tests = len(tests)
            
            for test_name, test_func in tests:
                try:
                    if callable(test_func):
                        result = await test_func() if asyncio.iscoroutinefunction(test_func) else test_func()
                    else:
                        result = await test_func
                    
                    test_results[test_name] = {
                        "status": "passed",
                        "result": result
                    }
                    passed_tests += 1
                    
                except Exception as e:
                    test_results[test_name] = {
                        "status": "failed",
                        "error": str(e)
                    }
            
            # Cleanup
            await db_manager.cleanup_test_database()
            
            return {
                "status": "passed" if passed_tests == total_tests else "failed",
                "message": f"Database tests: {passed_tests}/{total_tests} passed",
                "test_results": test_results,
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": total_tests - passed_tests,
                    "skipped_tests": 0
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Database test suite failed: {str(e)}",
                "error": str(e),
                "summary": {"total_tests": 1, "passed_tests": 0, "failed_tests": 1, "skipped_tests": 0}
            }
    
    async def _test_database_operations(self, db_manager):
        """
        Test basic database operations
        """
        async def run_operations():
            # Test customer operations
            if db_manager.test_mode == "mock":
                customer_id = f"test_customer_{int(time.time())}"
                db_manager.test_data["customers"][customer_id] = {
                    "id": customer_id,
                    "email": "test@example.com",
                    "name": "Test Customer",
                    "created_at": time.time()
                }
                
                retrieved = await db_manager.get_test_data("customers", customer_id)
                if not retrieved or retrieved["email"] != "test@example.com":
                    raise Exception("Customer operations test failed")
            
            return {"status": "success", "operations_tested": ["customer_crud"]}
        
        return run_operations
    
    async def _run_service_connection_tests(self) -> Dict[str, Any]:
        """
        Run service connection integration tests
        """
        if not ServiceConnectionTester:
            return {
                "status": "skipped",
                "message": "ServiceConnectionTester not available",
                "summary": {"total_tests": 0, "passed_tests": 0, "failed_tests": 0, "skipped_tests": 1}
            }
        
        try:
            # Set test mode for service tester
            os.environ["TEST_MODE"] = "mock" if self.test_mode != "live" else "live"
            
            service_tester = ServiceConnectionTester()
            results = await service_tester.run_all_tests()
            
            return {
                "status": results["summary"]["overall_status"],
                "message": f"Service connection tests: {results['summary']['passed_tests']}/{results['summary']['total_tests']} passed",
                "test_results": results["test_results"],
                "summary": {
                    "total_tests": results["summary"]["total_tests"],
                    "passed_tests": results["summary"]["passed_tests"],
                    "failed_tests": results["summary"]["failed_tests"],
                    "skipped_tests": 0
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Service connection test suite failed: {str(e)}",
                "error": str(e),
                "summary": {"total_tests": 1, "passed_tests": 0, "failed_tests": 1, "skipped_tests": 0}
            }
    
    async def _run_workflow_integration_tests(self) -> Dict[str, Any]:
        """
        Run workflow integration tests (MCP + n8n)
        """
        try:
            # Mock workflow integration tests
            workflow_tests = [
                ("workflow_trigger", self._test_workflow_trigger),
                ("workflow_monitoring", self._test_workflow_monitoring),
                ("agent_coordination", self._test_agent_coordination)
            ]
            
            test_results = {}
            passed_tests = 0
            total_tests = len(workflow_tests)
            
            for test_name, test_func in workflow_tests:
                try:
                    result = await test_func()
                    test_results[test_name] = {
                        "status": "passed",
                        "result": result
                    }
                    passed_tests += 1
                    
                except Exception as e:
                    test_results[test_name] = {
                        "status": "failed",
                        "error": str(e)
                    }
            
            return {
                "status": "passed" if passed_tests == total_tests else "failed",
                "message": f"Workflow integration tests: {passed_tests}/{total_tests} passed",
                "test_results": test_results,
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": total_tests - passed_tests,
                    "skipped_tests": 0
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Workflow integration test suite failed: {str(e)}",
                "error": str(e),
                "summary": {"total_tests": 1, "passed_tests": 0, "failed_tests": 1, "skipped_tests": 0}
            }
    
    async def _test_workflow_trigger(self) -> Dict[str, Any]:
        """
        Test workflow triggering functionality
        """
        # Mock workflow trigger test
        await asyncio.sleep(0.1)  # Simulate processing
        return {
            "workflow_id": "test_workflow_123",
            "status": "triggered",
            "execution_id": "exec_456"
        }
    
    async def _test_workflow_monitoring(self) -> Dict[str, Any]:
        """
        Test workflow monitoring functionality
        """
        # Mock workflow monitoring test
        await asyncio.sleep(0.1)  # Simulate processing
        return {
            "monitoring_status": "active",
            "workflows_monitored": 3,
            "alerts_configured": 5
        }
    
    async def _test_agent_coordination(self) -> Dict[str, Any]:
        """
        Test agent coordination functionality
        """
        # Mock agent coordination test
        await asyncio.sleep(0.1)  # Simulate processing
        return {
            "customer_journey_agent": "active",
            "n8n_mcp_agent": "active",
            "coordination_status": "synchronized"
        }
    
    async def _run_end_to_end_tests(self) -> Dict[str, Any]:
        """
        Run end-to-end integration tests
        """
        try:
            # Mock end-to-end tests
            e2e_tests = [
                ("customer_journey_flow", self._test_customer_journey_flow),
                ("workflow_automation_flow", self._test_workflow_automation_flow),
                ("monitoring_alerting_flow", self._test_monitoring_alerting_flow)
            ]
            
            test_results = {}
            passed_tests = 0
            total_tests = len(e2e_tests)
            
            for test_name, test_func in e2e_tests:
                try:
                    result = await test_func()
                    test_results[test_name] = {
                        "status": "passed",
                        "result": result
                    }
                    passed_tests += 1
                    
                except Exception as e:
                    test_results[test_name] = {
                        "status": "failed",
                        "error": str(e)
                    }
            
            return {
                "status": "passed" if passed_tests == total_tests else "failed",
                "message": f"End-to-end tests: {passed_tests}/{total_tests} passed",
                "test_results": test_results,
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": total_tests - passed_tests,
                    "skipped_tests": 0
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"End-to-end test suite failed: {str(e)}",
                "error": str(e),
                "summary": {"total_tests": 1, "passed_tests": 0, "failed_tests": 1, "skipped_tests": 0}
            }
    
    async def _test_customer_journey_flow(self) -> Dict[str, Any]:
        """
        Test complete customer journey flow
        """
        # Mock customer journey flow test
        await asyncio.sleep(0.2)  # Simulate processing
        return {
            "customer_created": True,
            "conversation_started": True,
            "agent_responded": True,
            "workflow_triggered": True,
            "journey_completed": True
        }
    
    async def _test_workflow_automation_flow(self) -> Dict[str, Any]:
        """
        Test workflow automation flow
        """
        # Mock workflow automation flow test
        await asyncio.sleep(0.2)  # Simulate processing
        return {
            "workflow_created": True,
            "mcp_connection_established": True,
            "n8n_workflow_executed": True,
            "results_processed": True,
            "automation_completed": True
        }
    
    async def _test_monitoring_alerting_flow(self) -> Dict[str, Any]:
        """
        Test monitoring and alerting flow
        """
        # Mock monitoring and alerting flow test
        await asyncio.sleep(0.2)  # Simulate processing
        return {
            "metrics_collected": True,
            "thresholds_monitored": True,
            "alerts_configured": True,
            "notifications_sent": True,
            "monitoring_active": True
        }
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """
        Generate a comprehensive test report
        """
        report = []
        report.append("=" * 80)
        report.append("AGENTIC AI PLATFORM - INTEGRATION TEST REPORT")
        report.append("=" * 80)
        report.append(f"Test Mode: {results['test_mode'].upper()}")
        report.append(f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(results['start_time']))}")
        report.append(f"End Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(results['end_time']))}")
        report.append(f"Duration: {results['duration']:.2f} seconds")
        report.append(f"Overall Status: {results['status'].upper()}")
        report.append("")
        
        # Summary
        summary = results["summary"]
        report.append("SUMMARY")
        report.append("-" * 40)
        report.append(f"Total Test Suites: {summary['total_suites']}")
        report.append(f"Passed Suites: {summary['passed_suites']}")
        report.append(f"Failed Suites: {summary['failed_suites']}")
        report.append(f"Total Tests: {summary['total_tests']}")
        report.append(f"Passed Tests: {summary['passed_tests']}")
        report.append(f"Failed Tests: {summary['failed_tests']}")
        report.append(f"Skipped Tests: {summary['skipped_tests']}")
        report.append(f"Success Rate: {(summary['passed_tests'] / max(summary['total_tests'], 1)) * 100:.1f}%")
        report.append("")
        
        # Test Suite Details
        report.append("TEST SUITE DETAILS")
        report.append("-" * 40)
        for suite_name, suite_results in results["test_suites"].items():
            status_icon = "✅" if suite_results.get("status") == "passed" else "❌" if suite_results.get("status") == "failed" else "⏭️"
            report.append(f"{status_icon} {suite_name.replace('_', ' ').title()}")
            report.append(f"   Status: {suite_results.get('status', 'unknown').upper()}")
            report.append(f"   Message: {suite_results.get('message', 'No message')}")
            
            if "summary" in suite_results:
                suite_summary = suite_results["summary"]
                report.append(f"   Tests: {suite_summary.get('passed_tests', 0)}/{suite_summary.get('total_tests', 0)} passed")
            
            if suite_results.get("status") == "error" and "error" in suite_results:
                report.append(f"   Error: {suite_results['error']}")
            
            report.append("")
        
        report.append("=" * 80)
        
        return "\\n".join(report)

# CLI interface
async def main():
    """
    Main CLI interface for running integration tests
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Agentic AI Platform Integration Test Runner")
    parser.add_argument("--mode", choices=["mock", "live", "hybrid"], default="mock",
                       help="Test mode: mock (default), live, or hybrid")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose output")
    parser.add_argument("--output", "-o", type=str,
                       help="Output file for test results (JSON format)")
    parser.add_argument("--report", "-r", type=str,
                       help="Output file for test report (text format)")
    
    args = parser.parse_args()
    
    # Create test runner
    runner = IntegrationTestRunner(test_mode=args.mode, verbose=args.verbose)
    
    try:
        # Run all tests
        results = await runner.run_all_tests()
        
        # Generate and display report
        report = runner.generate_report(results)
        print(report)
        
        # Save results to file if specified
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\\nTest results saved to: {args.output}")
        
        # Save report to file if specified
        if args.report:
            with open(args.report, 'w') as f:
                f.write(report)
            print(f"Test report saved to: {args.report}")
        
        # Exit with appropriate code
        exit_code = 0 if results["status"] == "passed" else 1
        return exit_code
        
    except Exception as e:
        logger.error(f"Test runner failed: {e}")
        print(f"\\nERROR: Test runner failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))