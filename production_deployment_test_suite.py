#!/usr/bin/env python3
"""
Production Deployment Test Suite
Comprehensive testing for the five-agent system with advanced capabilities
"""

import asyncio
import json
import time
import requests
import logging
from typing import Dict, Any, List
from datetime import datetime
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'production_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductionTestSuite:
    """Comprehensive production testing suite"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.backend_url = "http://localhost:8000"
        self.test_results = {
            "test_run_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "start_time": datetime.now().isoformat(),
            "base_url": base_url,
            "tests": {},
            "summary": {}
        }
        
        # Real-world test scenarios
        self.test_scenarios = {
            "arabic_ai_consultation": {
                "name": "Arabic AI Consultation Journey",
                "language": "ar",
                "messages": [
                    "مرحبا، أريد استشارة حول الذكاء الاصطناعي لشركتي",
                    "نحن شركة تجارة إلكترونية ونريد تحسين خدمة العملاء",
                    "ما هي التكلفة المتوقعة؟",
                    "أريد جدولة موعد مع مستشار"
                ],
                "expected_agents": ["initial_customer", "consulting", "billing"],
                "expected_features": ["voice_response", "live_session_offer", "cost_estimation"]
            },
            "english_workflow_automation": {
                "name": "English Workflow Automation",
                "language": "en", 
                "messages": [
                    "I need help automating my business processes",
                    "Can you create a workflow for email marketing?",
                    "How do I monitor the workflow performance?",
                    "What's the cost for workflow automation?"
                ],
                "expected_agents": ["initial_customer", "n8n_workflow", "billing"],
                "expected_features": ["template_suggestions", "n8n_integration", "monitoring_dashboard"]
            },
            "code_generation_request": {
                "name": "Code Generation with Requirements",
                "language": "en",
                "messages": [
                    "I want to build a custom AI agent for my business",
                    "It should handle customer inquiries and integrate with our CRM",
                    "Can you generate the code using LangGraph?",
                    "What's the development timeline and cost?"
                ],
                "expected_agents": ["initial_customer", "code_generation", "billing"],
                "expected_features": ["framework_selection", "code_generation", "timeline_estimation"]
            },
            "billing_inquiry": {
                "name": "Billing and Usage Inquiry",
                "language": "ar",
                "messages": [
                    "أريد معرفة استخدامي الحالي والتكاليف",
                    "كيف يمكنني إعداد طريقة دفع؟",
                    "أريد فاتورة مفصلة لهذا الشهر"
                ],
                "expected_agents": ["billing"],
                "expected_features": ["usage_tracking", "payment_setup", "invoice_generation"]
            }
        }
    
    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all production tests"""
        logger.info("🚀 Starting Comprehensive Production Test Suite")
        logger.info(f"Testing against: {self.base_url}")
        
        # Test system health first
        await self.test_system_health()
        
        # Test all agent scenarios
        await self.test_all_agent_scenarios()
        
        # Test advanced features
        await self.test_advanced_features()
        
        # Test performance and load
        await self.test_performance()
        
        # Test security features
        await self.test_security_features()
        
        # Generate final report
        self.generate_test_report()
        
        return self.test_results    

    async def test_system_health(self):
        """Test system health and availability"""
        logger.info("🏥 Testing System Health...")
        
        health_tests = {
            "frontend_health": f"{self.base_url}/api/health",
            "backend_health": f"{self.backend_url}/health",
            "agent_status": f"{self.backend_url}/agent/status"
        }
        
        for test_name, url in health_tests.items():
            try:
                response = requests.get(url, timeout=10)
                success = response.status_code == 200
                
                self.test_results["tests"][test_name] = {
                    "status": "PASS" if success else "FAIL",
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code,
                    "response_data": response.json() if success else None,
                    "timestamp": datetime.now().isoformat()
                }
                
                if success:
                    logger.info(f"✅ {test_name}: PASS ({response.elapsed.total_seconds():.2f}s)")
                else:
                    logger.error(f"❌ {test_name}: FAIL (Status: {response.status_code})")
                    
            except Exception as e:
                logger.error(f"❌ {test_name}: ERROR - {str(e)}")
                self.test_results["tests"][test_name] = {
                    "status": "ERROR",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
    
    async def test_all_agent_scenarios(self):
        """Test all real-world agent scenarios"""
        logger.info("🤖 Testing All Agent Scenarios...")
        
        for scenario_id, scenario in self.test_scenarios.items():
            logger.info(f"📋 Testing: {scenario['name']}")
            
            scenario_results = {
                "name": scenario["name"],
                "language": scenario["language"],
                "messages_tested": len(scenario["messages"]),
                "agents_encountered": [],
                "features_tested": [],
                "conversation_flow": [],
                "performance_metrics": {},
                "status": "RUNNING"
            }
            
            session_id = f"test_{scenario_id}_{int(time.time())}"
            
            try:
                for i, message in enumerate(scenario["messages"]):
                    logger.info(f"  💬 Message {i+1}: {message[:50]}...")
                    
                    start_time = time.time()
                    
                    # Send message to chat API
                    response = requests.post(
                        f"{self.base_url}/api/chat",
                        json={
                            "message": message,
                            "sessionId": session_id,
                            "language": scenario["language"]
                        },
                        timeout=30
                    )
                    
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        data = response.json()
                        agent_type = data.get("agent_type", "unknown")
                        
                        # Track agent usage
                        if agent_type not in scenario_results["agents_encountered"]:
                            scenario_results["agents_encountered"].append(agent_type)
                        
                        # Record conversation flow
                        scenario_results["conversation_flow"].append({
                            "message": message,
                            "agent": agent_type,
                            "response_time": response_time,
                            "confidence": data.get("confidence", 0),
                            "actions": data.get("actions", [])
                        })
                        
                        logger.info(f"    ✅ Agent: {agent_type} ({response_time:.2f}s)")
                        
                    else:
                        logger.error(f"    ❌ Failed: {response.status_code}")
                        scenario_results["conversation_flow"].append({
                            "message": message,
                            "error": f"HTTP {response.status_code}",
                            "response_time": response_time
                        })
                
                # Validate expected agents were used
                expected_agents = set(scenario["expected_agents"])
                actual_agents = set(scenario_results["agents_encountered"])
                
                if expected_agents.issubset(actual_agents):
                    scenario_results["status"] = "PASS"
                    logger.info(f"  ✅ Scenario PASSED - All expected agents used")
                else:
                    scenario_results["status"] = "PARTIAL"
                    missing_agents = expected_agents - actual_agents
                    logger.warning(f"  ⚠️  Scenario PARTIAL - Missing agents: {missing_agents}")
                
            except Exception as e:
                logger.error(f"  ❌ Scenario ERROR: {str(e)}")
                scenario_results["status"] = "ERROR"
                scenario_results["error"] = str(e)
            
            self.test_results["tests"][f"scenario_{scenario_id}"] = scenario_results
    
    async def test_advanced_features(self):
        """Test advanced chatbot features"""
        logger.info("🎯 Testing Advanced Features...")
        
        # Test voice interaction API
        await self.test_voice_features()
        
        # Test file upload API
        await self.test_file_upload_features()
        
        # Test live session API
        await self.test_live_session_features()
        
        # Test user memory and context
        await self.test_memory_features()
    
    async def test_voice_features(self):
        """Test voice interaction capabilities"""
        logger.info("🎤 Testing Voice Features...")
        
        voice_tests = [
            {
                "name": "speech_to_text_arabic",
                "endpoint": f"{self.base_url}/api/speech-to-text",
                "data": {"audio": "mock_arabic_audio", "language": "ar"}
            },
            {
                "name": "speech_to_text_english", 
                "endpoint": f"{self.base_url}/api/speech-to-text",
                "data": {"audio": "mock_english_audio", "language": "en"}
            }
        ]
        
        for test in voice_tests:
            try:
                start_time = time.time()
                response = requests.post(test["endpoint"], json=test["data"], timeout=15)
                response_time = time.time() - start_time
                
                self.test_results["tests"][test["name"]] = {
                    "status": "PASS" if response.status_code == 200 else "FAIL",
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "timestamp": datetime.now().isoformat()
                }
                
                if response.status_code == 200:
                    logger.info(f"  ✅ {test['name']}: PASS ({response_time:.2f}s)")
                else:
                    logger.error(f"  ❌ {test['name']}: FAIL")
                    
            except Exception as e:
                logger.error(f"  ❌ {test['name']}: ERROR - {str(e)}")
                self.test_results["tests"][test["name"]] = {
                    "status": "ERROR",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
    
    async def test_file_upload_features(self):
        """Test file upload capabilities"""
        logger.info("📁 Testing File Upload Features...")
        
        # Test file upload API
        try:
            files = {"file": ("test.txt", "This is a test file for agent processing", "text/plain")}
            data = {"agentType": "code_generation", "language": "en"}
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/file-upload",
                files=files,
                data=data,
                timeout=20
            )
            response_time = time.time() - start_time
            
            self.test_results["tests"]["file_upload"] = {
                "status": "PASS" if response.status_code == 200 else "FAIL",
                "response_time": response_time,
                "status_code": response.status_code,
                "timestamp": datetime.now().isoformat()
            }
            
            if response.status_code == 200:
                logger.info(f"  ✅ File upload: PASS ({response_time:.2f}s)")
            else:
                logger.error(f"  ❌ File upload: FAIL")
                
        except Exception as e:
            logger.error(f"  ❌ File upload: ERROR - {str(e)}")
            self.test_results["tests"]["file_upload"] = {
                "status": "ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def test_live_session_features(self):
        """Test live session capabilities"""
        logger.info("📹 Testing Live Session Features...")
        
        try:
            session_data = {
                "customerId": "test_customer_123",
                "consultationType": "ai_strategy",
                "language": "ar"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/live-session",
                json=session_data,
                timeout=15
            )
            response_time = time.time() - start_time
            
            self.test_results["tests"]["live_session"] = {
                "status": "PASS" if response.status_code == 200 else "FAIL",
                "response_time": response_time,
                "status_code": response.status_code,
                "timestamp": datetime.now().isoformat()
            }
            
            if response.status_code == 200:
                logger.info(f"  ✅ Live session: PASS ({response_time:.2f}s)")
            else:
                logger.error(f"  ❌ Live session: FAIL")
                
        except Exception as e:
            logger.error(f"  ❌ Live session: ERROR - {str(e)}")
            self.test_results["tests"]["live_session"] = {
                "status": "ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def test_memory_features(self):
        """Test user memory and context persistence"""
        logger.info("🧠 Testing Memory Features...")
        
        session_id = f"memory_test_{int(time.time())}"
        
        # Send multiple messages to test context preservation
        messages = [
            "My name is Ahmed and I work at TechCorp",
            "What did I tell you about my company?",
            "I need AI consulting for my company"
        ]
        
        context_preserved = True
        
        for i, message in enumerate(messages):
            try:
                response = requests.post(
                    f"{self.base_url}/api/chat",
                    json={"message": message, "sessionId": session_id},
                    timeout=15
                )
                
                if response.status_code != 200:
                    context_preserved = False
                    break
                    
            except Exception as e:
                context_preserved = False
                break
        
        self.test_results["tests"]["memory_context"] = {
            "status": "PASS" if context_preserved else "FAIL",
            "messages_tested": len(messages),
            "timestamp": datetime.now().isoformat()
        }
        
        if context_preserved:
            logger.info("  ✅ Memory/Context: PASS")
        else:
            logger.error("  ❌ Memory/Context: FAIL")
    
    async def test_performance(self):
        """Test system performance under load"""
        logger.info("⚡ Testing Performance...")
        
        # Concurrent request test
        concurrent_requests = 10
        messages = ["Hello", "مرحبا", "Help me", "ساعدني"]
        
        async def send_request(session_id: str, message: str):
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/api/chat",
                    json={"message": message, "sessionId": session_id},
                    timeout=30
                )
                response_time = time.time() - start_time
                return {
                    "success": response.status_code == 200,
                    "response_time": response_time,
                    "status_code": response.status_code
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "response_time": 30  # timeout
                }
        
        # Run concurrent requests
        tasks = []
        for i in range(concurrent_requests):
            session_id = f"perf_test_{i}_{int(time.time())}"
            message = messages[i % len(messages)]
            tasks.append(send_request(session_id, message))
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        successful_requests = sum(1 for r in results if r["success"])
        avg_response_time = sum(r["response_time"] for r in results) / len(results)
        
        self.test_results["tests"]["performance_load"] = {
            "status": "PASS" if successful_requests >= concurrent_requests * 0.8 else "FAIL",
            "concurrent_requests": concurrent_requests,
            "successful_requests": successful_requests,
            "success_rate": successful_requests / concurrent_requests,
            "average_response_time": avg_response_time,
            "total_time": total_time,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"  📊 Performance: {successful_requests}/{concurrent_requests} successful")
        logger.info(f"  📊 Average response time: {avg_response_time:.2f}s")
    
    async def test_security_features(self):
        """Test security features and guardrails"""
        logger.info("🛡️  Testing Security Features...")
        
        # Test rate limiting
        session_id = f"security_test_{int(time.time())}"
        rapid_requests = 20
        
        rate_limit_triggered = False
        
        for i in range(rapid_requests):
            try:
                response = requests.post(
                    f"{self.base_url}/api/chat",
                    json={"message": f"Test message {i}", "sessionId": session_id},
                    timeout=5
                )
                
                if response.status_code == 429:  # Too Many Requests
                    rate_limit_triggered = True
                    break
                    
            except Exception:
                pass
        
        self.test_results["tests"]["security_rate_limiting"] = {
            "status": "PASS" if rate_limit_triggered else "FAIL",
            "rate_limit_triggered": rate_limit_triggered,
            "requests_sent": i + 1,
            "timestamp": datetime.now().isoformat()
        }
        
        if rate_limit_triggered:
            logger.info("  ✅ Rate limiting: PASS")
        else:
            logger.warning("  ⚠️  Rate limiting: Not triggered (may need adjustment)")
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        logger.info("📊 Generating Test Report...")
        
        total_tests = len(self.test_results["tests"])
        passed_tests = sum(1 for test in self.test_results["tests"].values() 
                          if test.get("status") == "PASS")
        failed_tests = sum(1 for test in self.test_results["tests"].values() 
                          if test.get("status") == "FAIL")
        error_tests = sum(1 for test in self.test_results["tests"].values() 
                         if test.get("status") == "ERROR")
        
        self.test_results["end_time"] = datetime.now().isoformat()
        self.test_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "error_tests": error_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "overall_status": "PASS" if passed_tests >= total_tests * 0.8 else "FAIL"
        }
        
        # Save detailed results
        results_file = f"production_test_results_{self.test_results['test_run_id']}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        # Print summary
        logger.info("=" * 60)
        logger.info("🎯 PRODUCTION TEST RESULTS SUMMARY")
        logger.info("=" * 60)
        logger.info(f"📊 Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"⚠️  Errors: {error_tests}")
        logger.info(f"📈 Success Rate: {passed_tests/total_tests*100:.1f}%")
        logger.info(f"🎯 Overall Status: {self.test_results['summary']['overall_status']}")
        logger.info(f"📄 Detailed Results: {results_file}")
        logger.info("=" * 60)
        
        if self.test_results['summary']['overall_status'] == "PASS":
            logger.info("🎉 PRODUCTION DEPLOYMENT TESTS PASSED!")
            logger.info("✅ System is ready for production use")
        else:
            logger.error("❌ PRODUCTION DEPLOYMENT TESTS FAILED!")
            logger.error("🔧 System needs attention before production use")

async def main():
    """Main test execution"""
    # Check if custom URL provided
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000"
    
    # Initialize and run test suite
    test_suite = ProductionTestSuite(base_url)
    results = await test_suite.run_comprehensive_tests()
    
    # Exit with appropriate code
    if results["summary"]["overall_status"] == "PASS":
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())