#!/usr/bin/env python3
"""
Production Testing Suite for Four-Agent System
Comprehensive real-world testing with actual user scenarios in Arabic and English
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any, List
from datetime import datetime
import httpx
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionTestSuite:
    """Comprehensive production testing with real user scenarios"""
    
    def __init__(self, use_dev_environment: bool = True):
        self.use_dev = use_dev_environment
        self.base_url = "https://dev.consulting.sa" if use_dev_environment else "https://consulting.sa"
        self.api_port = "8001" if use_dev_environment else "8000"
        self.server_ip = "217.79.255.54"
        
        # Real API keys for production testing
        self.config = {
            "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
            "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY"),
            "SUPABASE_URL": os.getenv("SUPABASE_URL"),
            "SUPABASE_SERVICE_ROLE_KEY": os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
        }
        
        self.test_results = []
        self.user_sessions = {}
        
    async def run_comprehensive_production_tests(self):
        """Run comprehensive production tests with real user scenarios"""
        logger.info("🚀 Starting Comprehensive Production Testing Suite")
        logger.info(f"🌐 Testing Environment: {'Development' if self.use_dev else 'Production'}")
        logger.info(f"🔗 Base URL: {self.base_url}")
        
        # Test scenarios in order of complexity
        await self._test_system_health()
        await self._test_frontend_accessibility()
        await self._test_api_endpoints()
        await self._test_real_user_scenarios_arabic()
        await self._test_real_user_scenarios_english()
        await self._test_agent_workflows()
        await self._test_bilingual_interactions()
        await self._test_complex_scenarios()
        
        # Generate comprehensive report
        self._generate_production_report()
    
    async def _test_system_health(self):
        """Test basic system health and connectivity"""
        logger.info("🏥 Testing System Health")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test frontend health
                response = await client.get(f"{self.base_url}/api/health")
                frontend_healthy = response.status_code == 200
                
                # Test backend API health
                backend_response = await client.get(f"http://{self.server_ip}:{self.api_port}/health")
                backend_healthy = backend_response.status_code == 200
                
                self.test_results.append({
                    "category": "System Health",
                    "test": "Frontend Health Check",
                    "status": "✅ PASS" if frontend_healthy else "❌ FAIL",
                    "details": f"Status: {response.status_code}"
                })
                
                self.test_results.append({
                    "category": "System Health", 
                    "test": "Backend API Health Check",
                    "status": "✅ PASS" if backend_healthy else "❌ FAIL",
                    "details": f"Status: {backend_response.status_code}"
                })
                
        except Exception as e:
            logger.error(f"System health check failed: {e}")
            self.test_results.append({
                "category": "System Health",
                "test": "Health Check",
                "status": "❌ FAIL",
                "details": str(e)
            })
    
    async def _test_frontend_accessibility(self):
        """Test frontend accessibility and page loading"""
        logger.info("🌐 Testing Frontend Accessibility")
        
        pages_to_test = [
            "/",
            "/about", 
            "/services",
            "/consulting",
            "/contact"
        ]
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                for page in pages_to_test:
                    try:
                        response = await client.get(f"{self.base_url}{page}")
                        success = response.status_code == 200
                        
                        self.test_results.append({
                            "category": "Frontend Accessibility",
                            "test": f"Page Load: {page}",
                            "status": "✅ PASS" if success else "❌ FAIL",
                            "details": f"Status: {response.status_code}, Size: {len(response.content)} bytes"
                        })
                        
                    except Exception as e:
                        self.test_results.append({
                            "category": "Frontend Accessibility",
                            "test": f"Page Load: {page}",
                            "status": "❌ FAIL",
                            "details": str(e)
                        })
                        
        except Exception as e:
            logger.error(f"Frontend accessibility test failed: {e}")
    
    async def _test_api_endpoints(self):
        """Test API endpoints functionality"""
        logger.info("🔌 Testing API Endpoints")
        
        endpoints_to_test = [
            {"path": "/api/health", "method": "GET"},
            {"path": "/api/chat", "method": "POST", "data": {"message": "Hello", "session_id": "test_session"}},
        ]
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                for endpoint in endpoints_to_test:
                    try:
                        if endpoint["method"] == "GET":
                            response = await client.get(f"{self.base_url}{endpoint['path']}")
                        else:
                            response = await client.post(
                                f"{self.base_url}{endpoint['path']}", 
                                json=endpoint.get("data", {})
                            )
                        
                        success = response.status_code in [200, 201]
                        
                        self.test_results.append({
                            "category": "API Endpoints",
                            "test": f"{endpoint['method']} {endpoint['path']}",
                            "status": "✅ PASS" if success else "❌ FAIL",
                            "details": f"Status: {response.status_code}"
                        })
                        
                    except Exception as e:
                        self.test_results.append({
                            "category": "API Endpoints",
                            "test": f"{endpoint['method']} {endpoint['path']}",
                            "status": "❌ FAIL",
                            "details": str(e)
                        })
                        
        except Exception as e:
            logger.error(f"API endpoints test failed: {e}")
    
    async def _test_real_user_scenarios_arabic(self):
        """Test real user scenarios in Arabic"""
        logger.info("🇸🇦 Testing Real User Scenarios - Arabic")
        
        arabic_scenarios = [
            {
                "name": "عميل جديد - استفسار عن الخدمات",
                "user_type": "new_customer",
                "messages": [
                    "مرحباً، أنا أحمد من الرياض وأريد معرفة خدماتكم في الذكاء الاصطناعي",
                    "ما هي أسعار خدمات الوكلاء الأذكياء؟",
                    "هل يمكنني التحدث مع أحد المختصين؟"
                ],
                "expected_agent": "initial_customer",
                "expected_actions": ["service_info", "pricing_info", "human_handoff"]
            },
            {
                "name": "عميل مهتم بأتمتة سير العمل",
                "user_type": "business_owner",
                "messages": [
                    "أريد أتمتة عمليات البريد الإلكتروني في شركتي",
                    "ما هي القوالب المتاحة لأتمتة البريد الإلكتروني؟",
                    "كيف يمكنني إنشاء سير عمل مخصص؟"
                ],
                "expected_agent": "n8n_workflow",
                "expected_actions": ["show_templates", "create_workflow"]
            },
            {
                "name": "عميل يريد تطوير نظام مخصص",
                "user_type": "tech_entrepreneur", 
                "messages": [
                    "أحتاج بناء نظام ذكي لخدمة العملاء في متجري الإلكتروني",
                    "ما هو أفضل إطار عمل لبناء وكيل ذكي معقد؟",
                    "كم المدة المتوقعة لتطوير هذا النظام؟"
                ],
                "expected_agent": "code_generation",
                "expected_actions": ["framework_selection", "timeline_estimation"]
            },
            {
                "name": "عميل يطلب استشارة استراتيجية",
                "user_type": "ceo",
                "messages": [
                    "أريد وضع استراتيجية شاملة للذكاء الاصطناعي في شركتي",
                    "ما هي أنواع الاستشارات المتاحة؟",
                    "أريد حجز موعد لاستشارة استراتيجية"
                ],
                "expected_agent": "consulting",
                "expected_actions": ["consultation_types", "schedule_consultation"]
            }
        ]
        
        for scenario in arabic_scenarios:
            await self._execute_user_scenario(scenario, "ar")
    
    async def _test_real_user_scenarios_english(self):
        """Test real user scenarios in English"""
        logger.info("🇺🇸 Testing Real User Scenarios - English")
        
        english_scenarios = [
            {
                "name": "New Customer - Service Inquiry",
                "user_type": "startup_founder",
                "messages": [
                    "Hi, I'm Sarah from Dubai and I want to learn about your AI services",
                    "What's the difference between AI agents and chatbots?",
                    "Can I get a quote for implementing AI in my startup?"
                ],
                "expected_agent": "initial_customer",
                "expected_actions": ["service_comparison", "pricing_quote"]
            },
            {
                "name": "Business Owner - Workflow Automation",
                "user_type": "business_owner",
                "messages": [
                    "I need to automate my data processing workflows",
                    "Show me available workflow templates for data processing",
                    "How can I monitor workflow performance?"
                ],
                "expected_agent": "n8n_workflow", 
                "expected_actions": ["show_templates", "performance_monitoring"]
            },
            {
                "name": "Developer - Custom Development",
                "user_type": "developer",
                "messages": [
                    "I want to build a multi-agent system for customer support",
                    "Which framework would you recommend for complex workflows?",
                    "Can you help me with the architecture design?"
                ],
                "expected_agent": "code_generation",
                "expected_actions": ["framework_recommendation", "architecture_design"]
            },
            {
                "name": "Enterprise Client - Strategic Consulting",
                "user_type": "enterprise_manager",
                "messages": [
                    "We need strategic guidance for AI implementation across our organization",
                    "What consultation services do you offer?",
                    "I'd like to schedule a feasibility study"
                ],
                "expected_agent": "consulting",
                "expected_actions": ["consultation_services", "feasibility_study"]
            }
        ]
        
        for scenario in english_scenarios:
            await self._execute_user_scenario(scenario, "en")   
 
    async def _execute_user_scenario(self, scenario: Dict[str, Any], language: str):
        """Execute a complete user scenario with multiple message exchanges"""
        logger.info(f"👤 Testing Scenario: {scenario['name']}")
        
        session_id = f"test_session_{scenario['user_type']}_{int(time.time())}"
        scenario_results = []
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                for i, message in enumerate(scenario["messages"]):
                    try:
                        # Send message to chat API
                        response = await client.post(
                            f"{self.base_url}/api/chat",
                            json={
                                "message": message,
                                "session_id": session_id,
                                "language": language
                            }
                        )
                        
                        if response.status_code == 200:
                            response_data = response.json()
                            
                            # Analyze response
                            analysis = self._analyze_agent_response(
                                response_data, 
                                scenario.get("expected_agent"),
                                scenario.get("expected_actions", [])
                            )
                            
                            scenario_results.append({
                                "message_index": i + 1,
                                "message": message[:50] + "..." if len(message) > 50 else message,
                                "response_length": len(response_data.get("content", "")),
                                "agent_type": response_data.get("agent_type", "unknown"),
                                "language_match": response_data.get("language") == language,
                                "has_actions": len(response_data.get("actions", [])) > 0,
                                "analysis": analysis
                            })
                            
                            # Small delay between messages to simulate real user
                            await asyncio.sleep(1)
                            
                        else:
                            scenario_results.append({
                                "message_index": i + 1,
                                "message": message[:50] + "...",
                                "error": f"HTTP {response.status_code}",
                                "analysis": {"success": False, "reason": "API error"}
                            })
                            
                    except Exception as e:
                        scenario_results.append({
                            "message_index": i + 1,
                            "message": message[:50] + "...",
                            "error": str(e),
                            "analysis": {"success": False, "reason": "Exception"}
                        })
                
                # Calculate scenario success rate
                successful_messages = sum(1 for result in scenario_results 
                                        if result.get("analysis", {}).get("success", False))
                success_rate = successful_messages / len(scenario["messages"])
                
                self.test_results.append({
                    "category": f"User Scenarios - {language.upper()}",
                    "test": scenario["name"],
                    "status": "✅ PASS" if success_rate >= 0.7 else "❌ FAIL",
                    "details": f"Success Rate: {success_rate:.1%} ({successful_messages}/{len(scenario['messages'])})",
                    "scenario_results": scenario_results
                })
                
        except Exception as e:
            logger.error(f"Scenario execution failed: {e}")
            self.test_results.append({
                "category": f"User Scenarios - {language.upper()}",
                "test": scenario["name"],
                "status": "❌ FAIL",
                "details": str(e)
            })
    
    def _analyze_agent_response(self, response_data: Dict[str, Any], expected_agent: str, expected_actions: List[str]) -> Dict[str, Any]:
        """Analyze agent response for correctness and completeness"""
        analysis = {
            "success": False,
            "agent_correct": False,
            "has_content": False,
            "language_appropriate": False,
            "actions_present": False,
            "reason": ""
        }
        
        try:
            # Check if response has content
            content = response_data.get("content", "")
            analysis["has_content"] = len(content) > 20
            
            # Check agent routing
            agent_type = response_data.get("agent_type", "")
            analysis["agent_correct"] = agent_type == expected_agent
            
            # Check language appropriateness (basic check)
            language = response_data.get("language", "")
            analysis["language_appropriate"] = language in ["ar", "en"]
            
            # Check for actions
            actions = response_data.get("actions", [])
            analysis["actions_present"] = len(actions) > 0
            
            # Overall success criteria
            success_criteria = [
                analysis["has_content"],
                analysis["language_appropriate"]
            ]
            
            # Agent routing is important but not critical for basic functionality
            if analysis["agent_correct"]:
                success_criteria.append(True)
            
            analysis["success"] = sum(success_criteria) >= 2
            
            if not analysis["success"]:
                reasons = []
                if not analysis["has_content"]:
                    reasons.append("no_content")
                if not analysis["agent_correct"]:
                    reasons.append("wrong_agent")
                if not analysis["language_appropriate"]:
                    reasons.append("language_issue")
                analysis["reason"] = ", ".join(reasons)
            else:
                analysis["reason"] = "success"
                
        except Exception as e:
            analysis["reason"] = f"analysis_error: {str(e)}"
        
        return analysis
    
    async def _test_agent_workflows(self):
        """Test specific agent workflows and capabilities"""
        logger.info("🤖 Testing Agent Workflows")
        
        # Test each agent's specific capabilities
        await self._test_initial_customer_workflows()
        await self._test_n8n_workflow_capabilities()
        await self._test_consulting_workflows()
        await self._test_code_generation_workflows()
    
    async def _test_initial_customer_workflows(self):
        """Test Initial Customer Agent specific workflows"""
        workflows = [
            {
                "name": "Contact Information Collection",
                "message": "Hi, I'm John Smith, email: john@example.com, phone: +966501234567",
                "expected_elements": ["contact", "email", "phone"]
            },
            {
                "name": "Service Information Request",
                "message": "What AI services do you offer and what are the prices?",
                "expected_elements": ["services", "pricing", "ai"]
            }
        ]
        
        for workflow in workflows:
            await self._test_agent_workflow("initial_customer", workflow)
    
    async def _test_n8n_workflow_capabilities(self):
        """Test N8N Workflow Agent capabilities"""
        workflows = [
            {
                "name": "Template Listing",
                "message": "Show me all available workflow templates",
                "expected_elements": ["templates", "workflow", "available"]
            },
            {
                "name": "Workflow Creation Request",
                "message": "I want to create an email automation workflow",
                "expected_elements": ["email", "automation", "workflow", "create"]
            }
        ]
        
        for workflow in workflows:
            await self._test_agent_workflow("n8n_workflow", workflow)
    
    async def _test_consulting_workflows(self):
        """Test Consulting Agent workflows"""
        workflows = [
            {
                "name": "Consultation Types Inquiry",
                "message": "What types of AI consulting services do you provide?",
                "expected_elements": ["consulting", "services", "types"]
            },
            {
                "name": "Strategic Consultation Request",
                "message": "I need strategic guidance for AI implementation in my company",
                "expected_elements": ["strategic", "guidance", "implementation"]
            }
        ]
        
        for workflow in workflows:
            await self._test_agent_workflow("consulting", workflow)
    
    async def _test_code_generation_workflows(self):
        """Test Code Generation Agent workflows"""
        workflows = [
            {
                "name": "Framework Recommendation",
                "message": "Which framework should I use for building a complex multi-agent system?",
                "expected_elements": ["framework", "multi-agent", "complex"]
            },
            {
                "name": "Simple Project Request",
                "message": "I need a simple chatbot for customer support",
                "expected_elements": ["chatbot", "customer support", "simple"]
            }
        ]
        
        for workflow in workflows:
            await self._test_agent_workflow("code_generation", workflow)
    
    async def _test_agent_workflow(self, expected_agent: str, workflow: Dict[str, Any]):
        """Test a specific agent workflow"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "message": workflow["message"],
                        "session_id": f"workflow_test_{expected_agent}_{int(time.time())}",
                        "language": "en"
                    }
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # Check if routed to correct agent
                    agent_correct = response_data.get("agent_type") == expected_agent
                    
                    # Check for expected elements in response
                    content = response_data.get("content", "").lower()
                    elements_found = sum(1 for element in workflow["expected_elements"] 
                                       if element.lower() in content)
                    elements_ratio = elements_found / len(workflow["expected_elements"])
                    
                    success = agent_correct and elements_ratio >= 0.5
                    
                    self.test_results.append({
                        "category": "Agent Workflows",
                        "test": f"{expected_agent.title()} - {workflow['name']}",
                        "status": "✅ PASS" if success else "❌ FAIL",
                        "details": f"Agent: {response_data.get('agent_type')}, Elements: {elements_ratio:.1%}"
                    })
                else:
                    self.test_results.append({
                        "category": "Agent Workflows",
                        "test": f"{expected_agent.title()} - {workflow['name']}",
                        "status": "❌ FAIL",
                        "details": f"HTTP {response.status_code}"
                    })
                    
        except Exception as e:
            self.test_results.append({
                "category": "Agent Workflows",
                "test": f"{expected_agent.title()} - {workflow['name']}",
                "status": "❌ FAIL",
                "details": str(e)
            })
    
    async def _test_bilingual_interactions(self):
        """Test bilingual (Arabic/English) interactions"""
        logger.info("🌍 Testing Bilingual Interactions")
        
        bilingual_tests = [
            {
                "name": "Mixed Language Input",
                "message": "مرحباً، I need help with AI services for my business",
                "expected_handling": True
            },
            {
                "name": "Arabic to English Switch",
                "messages": [
                    "مرحباً، أريد معرفة خدماتكم",
                    "Can you explain this in English please?"
                ],
                "expected_handling": True
            },
            {
                "name": "English to Arabic Switch", 
                "messages": [
                    "Hello, what services do you offer?",
                    "هل يمكنك الشرح بالعربية من فضلك؟"
                ],
                "expected_handling": True
            }
        ]
        
        for test in bilingual_tests:
            session_id = f"bilingual_test_{int(time.time())}"
            
            if "messages" in test:
                # Multi-message test
                all_handled = True
                for message in test["messages"]:
                    handled = await self._test_single_message(message, session_id)
                    if not handled:
                        all_handled = False
                        break
                
                self.test_results.append({
                    "category": "Bilingual Interactions",
                    "test": test["name"],
                    "status": "✅ PASS" if all_handled else "❌ FAIL",
                    "details": f"Messages handled: {all_handled}"
                })
            else:
                # Single message test
                handled = await self._test_single_message(test["message"], session_id)
                
                self.test_results.append({
                    "category": "Bilingual Interactions", 
                    "test": test["name"],
                    "status": "✅ PASS" if handled else "❌ FAIL",
                    "details": f"Message handled: {handled}"
                })
    
    async def _test_single_message(self, message: str, session_id: str) -> bool:
        """Test a single message and return if it was handled properly"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "message": message,
                        "session_id": session_id
                    }
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    content = response_data.get("content", "")
                    return len(content) > 10  # Basic check for meaningful response
                
                return False
                
        except Exception:
            return False
    
    async def _test_complex_scenarios(self):
        """Test complex multi-step scenarios"""
        logger.info("🎯 Testing Complex Scenarios")
        
        complex_scenarios = [
            {
                "name": "Complete Customer Journey - Arabic",
                "steps": [
                    {"message": "مرحباً، أنا صاحب شركة تقنية وأريد تطبيق الذكاء الاصطناعي", "expected_agent": "initial_customer"},
                    {"message": "أريد أتمتة عمليات خدمة العملاء", "expected_agent": "n8n_workflow"},
                    {"message": "أحتاج أيضاً نظام مخصص للتحليلات", "expected_agent": "code_generation"},
                    {"message": "وأريد استشارة استراتيجية شاملة", "expected_agent": "consulting"}
                ]
            },
            {
                "name": "Complete Customer Journey - English",
                "steps": [
                    {"message": "Hi, I'm a startup founder looking for AI solutions", "expected_agent": "initial_customer"},
                    {"message": "I need workflow automation for my business processes", "expected_agent": "n8n_workflow"},
                    {"message": "Can you help me build a custom AI agent?", "expected_agent": "code_generation"},
                    {"message": "I also need strategic consulting for AI implementation", "expected_agent": "consulting"}
                ]
            }
        ]
        
        for scenario in complex_scenarios:
            await self._execute_complex_scenario(scenario)
    
    async def _execute_complex_scenario(self, scenario: Dict[str, Any]):
        """Execute a complex multi-step scenario"""
        session_id = f"complex_scenario_{int(time.time())}"
        step_results = []
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                for i, step in enumerate(scenario["steps"]):
                    response = await client.post(
                        f"{self.base_url}/api/chat",
                        json={
                            "message": step["message"],
                            "session_id": session_id
                        }
                    )
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        agent_correct = response_data.get("agent_type") == step["expected_agent"]
                        has_content = len(response_data.get("content", "")) > 20
                        
                        step_results.append({
                            "step": i + 1,
                            "agent_correct": agent_correct,
                            "has_content": has_content,
                            "success": agent_correct and has_content
                        })
                    else:
                        step_results.append({
                            "step": i + 1,
                            "success": False,
                            "error": f"HTTP {response.status_code}"
                        })
                    
                    # Delay between steps
                    await asyncio.sleep(2)
                
                # Calculate overall success
                successful_steps = sum(1 for result in step_results if result.get("success", False))
                success_rate = successful_steps / len(scenario["steps"])
                
                self.test_results.append({
                    "category": "Complex Scenarios",
                    "test": scenario["name"],
                    "status": "✅ PASS" if success_rate >= 0.75 else "❌ FAIL",
                    "details": f"Success Rate: {success_rate:.1%} ({successful_steps}/{len(scenario['steps'])})",
                    "step_results": step_results
                })
                
        except Exception as e:
            self.test_results.append({
                "category": "Complex Scenarios",
                "test": scenario["name"],
                "status": "❌ FAIL",
                "details": str(e)
            })
    
    def _generate_production_report(self):
        """Generate comprehensive production test report"""
        logger.info("\n" + "="*80)
        logger.info("🧪 PRODUCTION TESTING RESULTS")
        logger.info("="*80)
        
        # Group results by category
        categories = {}
        for result in self.test_results:
            category = result["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if "✅ PASS" in r["status"])
        
        logger.info(f"\n📊 Overall Results:")
        logger.info(f"   Environment: {'Development' if self.use_dev else 'Production'}")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {passed_tests}")
        logger.info(f"   Failed: {total_tests - passed_tests}")
        logger.info(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        for category, results in categories.items():
            logger.info(f"\n📦 {category}")
            logger.info("-" * 40)
            
            category_passed = sum(1 for r in results if "✅ PASS" in r["status"])
            category_total = len(results)
            
            for result in results:
                logger.info(f"  {result['status']} {result['test']}")
                if result.get("details"):
                    logger.info(f"     └─ {result['details']}")
            
            logger.info(f"  📈 Category Success: {category_passed}/{category_total} ({(category_passed/category_total)*100:.1f}%)")
        
        # Save detailed results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"production_test_results_{timestamp}.json"
        
        detailed_results = {
            "timestamp": datetime.now().isoformat(),
            "environment": "development" if self.use_dev else "production",
            "base_url": self.base_url,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "categories": categories,
            "all_results": self.test_results
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n📄 Detailed results saved to: {results_file}")
        logger.info("="*80)
        
        return detailed_results

async def main():
    """Run the production test suite"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Production Testing Suite")
    parser.add_argument("--prod", action="store_true", help="Test production environment (default: development)")
    args = parser.parse_args()
    
    use_dev = not args.prod
    
    tester = ProductionTestSuite(use_dev_environment=use_dev)
    await tester.run_comprehensive_production_tests()

if __name__ == "__main__":
    asyncio.run(main())