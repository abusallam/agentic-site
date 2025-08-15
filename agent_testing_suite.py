#!/usr/bin/env python3
"""
Comprehensive Agent Testing Suite
Tests all agents and iterates on prompts to achieve 90% success rate
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.my_adk_agent.agents.initial_customer_agent import InitialCustomerAgent
from agent.my_adk_agent.agents.n8n_workflow_agent import N8nWorkflowAgent
from agent.my_adk_agent.agents.code_generation_agent import CodeGenerationAgent
from agent.my_adk_agent.agents.consulting_agent import ConsultingAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentTestingSuite:
    """Comprehensive testing suite for all agents"""
    
    def __init__(self):
        self.config = self._load_config()
        self.test_results = {}
        self.iteration_count = 0
        self.max_iterations = 5
        self.target_success_rate = 0.90
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration for testing"""
        return {
            "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY", "mock_key"),
            "SUPABASE_URL": os.getenv("SUPABASE_URL", "mock_url"),
            "SUPABASE_ANON_KEY": os.getenv("SUPABASE_ANON_KEY", "mock_key"),
            "N8N_URL": os.getenv("N8N_URL", "http://localhost:5678"),
            "LIVEKIT_API_KEY": os.getenv("LIVEKIT_API_KEY", "mock_key"),
            "LIVEKIT_API_SECRET": os.getenv("LIVEKIT_API_SECRET", "mock_secret")
        }
    
    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run comprehensive tests on all agents"""
        logger.info("🚀 Starting Comprehensive Agent Testing Suite")
        
        while self.iteration_count < self.max_iterations:
            self.iteration_count += 1
            logger.info(f"📊 Iteration {self.iteration_count}/{self.max_iterations}")
            
            # Test all agents
            results = await self._test_all_agents()
            
            # Calculate overall success rate
            overall_success_rate = self._calculate_success_rate(results)
            
            logger.info(f"📈 Overall Success Rate: {overall_success_rate:.2%}")
            
            if overall_success_rate >= self.target_success_rate:
                logger.info(f"🎯 Target success rate achieved: {overall_success_rate:.2%}")
                break
            
            # Analyze failures and improve prompts
            await self._improve_prompts(results)
        
        return self._generate_final_report()
    
    async def _test_all_agents(self) -> Dict[str, Any]:
        """Test all agents with various scenarios"""
        results = {
            "initial_customer": await self._test_initial_customer_agent(),
            "n8n_workflow": await self._test_n8n_workflow_agent(),
            "code_generation": await self._test_code_generation_agent(),
            "consulting": await self._test_consulting_agent()
        }
        
        self.test_results[f"iteration_{self.iteration_count}"] = results
        return results    

    async def _test_initial_customer_agent(self) -> Dict[str, Any]:
        """Test Initial Customer Agent with various scenarios"""
        logger.info("🧪 Testing Initial Customer Agent")
        
        test_cases = [
            {
                "name": "Arabic Greeting",
                "message": "مرحباً، أريد معرفة خدماتكم في الذكاء الاصطناعي",
                "expected_actions": ["collect_info", "provide_services"],
                "language": "ar"
            },
            {
                "name": "English Inquiry",
                "message": "Hello, I'm interested in your AI services for my business",
                "expected_actions": ["collect_info", "provide_services"],
                "language": "en"
            },
            {
                "name": "Contact Information Provided",
                "message": "اسمي أحمد محمد، بريدي ahmed@example.com ورقمي 0501234567",
                "expected_actions": ["collect_email", "collect_phone"],
                "language": "ar"
            },
            {
                "name": "Human Agent Request",
                "message": "أريد التحدث مع شخص من فريقكم",
                "expected_actions": ["offer_human_handoff"],
                "language": "ar"
            },
            {
                "name": "Service Specific Question",
                "message": "What's the difference between AI agents and chatbots?",
                "expected_actions": ["provide_services"],
                "language": "en"
            }
        ]
        
        results = []
        
        try:
            agent = InitialCustomerAgent(self.config)
            
            for test_case in test_cases:
                try:
                    response = await agent.process_message(
                        test_case["message"], 
                        f"test_session_{self.iteration_count}"
                    )
                    
                    success = self._evaluate_response(response, test_case)
                    
                    results.append({
                        "test_name": test_case["name"],
                        "success": success,
                        "response": response,
                        "expected": test_case["expected_actions"],
                        "actual_actions": response.get("actions", [])
                    })
                    
                except Exception as e:
                    logger.error(f"Error in test {test_case['name']}: {e}")
                    results.append({
                        "test_name": test_case["name"],
                        "success": False,
                        "error": str(e)
                    })
        
        except Exception as e:
            logger.error(f"Failed to initialize Initial Customer Agent: {e}")
            return {"success_rate": 0.0, "results": [], "error": str(e)}
        
        success_rate = sum(1 for r in results if r.get("success", False)) / len(results)
        
        return {
            "success_rate": success_rate,
            "results": results,
            "total_tests": len(test_cases)
        }
    
    async def _test_n8n_workflow_agent(self) -> Dict[str, Any]:
        """Test N8N Workflow Agent"""
        logger.info("🧪 Testing N8N Workflow Agent")
        
        test_cases = [
            {
                "name": "List Templates Arabic",
                "message": "أريد رؤية قوالب سير العمل المتاحة",
                "expected_actions": ["show_templates"],
                "language": "ar"
            },
            {
                "name": "Create Workflow English",
                "message": "I want to create an email automation workflow",
                "expected_actions": ["create_workflow"],
                "language": "en"
            },
            {
                "name": "Execute Workflow",
                "message": "تشغيل سير العمل الخاص بمعالجة البيانات",
                "expected_actions": ["execute_workflow"],
                "language": "ar"
            },
            {
                "name": "Check Status",
                "message": "What's the status of my workflow?",
                "expected_actions": ["check_status"],
                "language": "en"
            },
            {
                "name": "Performance Monitoring",
                "message": "أريد تقرير عن أداء سير العمل",
                "expected_actions": ["check_status"],
                "language": "ar"
            }
        ]
        
        results = []
        
        try:
            agent = N8nWorkflowAgent(self.config)
            
            for test_case in test_cases:
                try:
                    response = await agent.process_workflow_request(
                        test_case["message"],
                        "test_customer_123",
                        test_case["language"]
                    )
                    
                    success = self._evaluate_response(response, test_case)
                    
                    results.append({
                        "test_name": test_case["name"],
                        "success": success,
                        "response": response,
                        "expected": test_case["expected_actions"],
                        "actual_actions": response.get("actions", [])
                    })
                    
                except Exception as e:
                    logger.error(f"Error in test {test_case['name']}: {e}")
                    results.append({
                        "test_name": test_case["name"],
                        "success": False,
                        "error": str(e)
                    })
        
        except Exception as e:
            logger.error(f"Failed to initialize N8N Workflow Agent: {e}")
            return {"success_rate": 0.0, "results": [], "error": str(e)}
        
        success_rate = sum(1 for r in results if r.get("success", False)) / len(results)
        
        return {
            "success_rate": success_rate,
            "results": results,
            "total_tests": len(test_cases)
        }
    
    async def _test_code_generation_agent(self) -> Dict[str, Any]:
        """Test Code Generation Agent"""
        logger.info("🧪 Testing Code Generation Agent")
        
        test_cases = [
            {
                "name": "Simple Chatbot Request",
                "message": "أريد بناء شات بوت بسيط للعملاء",
                "expected_framework": "pydantic",
                "complexity": "low",
                "language": "ar"
            },
            {
                "name": "Complex Multi-Agent System",
                "message": "I need a complex multi-agent system for workflow automation",
                "expected_framework": "langgraph",
                "complexity": "high",
                "language": "en"
            },
            {
                "name": "Production Ready Agent",
                "message": "بناء وكيل ذكي جاهز للإنتاج مع تكامل قاعدة البيانات",
                "expected_framework": "google_adk",
                "complexity": "medium",
                "language": "ar"
            },
            {
                "name": "Data Processing Agent",
                "message": "Create an agent for automated data processing and validation",
                "expected_framework": "pydantic",
                "complexity": "medium",
                "language": "en"
            }
        ]
        
        results = []
        
        try:
            agent = CodeGenerationAgent(self.config)
            
            for test_case in test_cases:
                try:
                    response = await agent.process_code_request(
                        test_case["message"],
                        "test_customer_456",
                        test_case["language"]
                    )
                    
                    # For code generation, we check if the workflow completes
                    success = response.get("agent_type") == "code_generation" and "content" in response
                    
                    results.append({
                        "test_name": test_case["name"],
                        "success": success,
                        "response": response,
                        "expected_framework": test_case["expected_framework"],
                        "expected_complexity": test_case["complexity"]
                    })
                    
                except Exception as e:
                    logger.error(f"Error in test {test_case['name']}: {e}")
                    results.append({
                        "test_name": test_case["name"],
                        "success": False,
                        "error": str(e)
                    })
        
        except Exception as e:
            logger.error(f"Failed to initialize Code Generation Agent: {e}")
            return {"success_rate": 0.0, "results": [], "error": str(e)}
        
        success_rate = sum(1 for r in results if r.get("success", False)) / len(results)
        
        return {
            "success_rate": success_rate,
            "results": results,
            "total_tests": len(test_cases)
        }
    
    async def _test_consulting_agent(self) -> Dict[str, Any]:
        """Test Consulting Agent"""
        logger.info("🧪 Testing Consulting Agent")
        
        test_cases = [
            {
                "name": "AI Strategy Request",
                "message": "أحتاج استشارة في وضع استراتيجية الذكاء الاصطناعي لشركتي",
                "expected_actions": ["suggest_consultation_type"],
                "consultation_type": "ai_strategy",
                "language": "ar"
            },
            {
                "name": "Feasibility Study",
                "message": "I need a feasibility study for implementing AI in my retail business",
                "expected_actions": ["suggest_consultation_type"],
                "consultation_type": "feasibility_study",
                "language": "en"
            },
            {
                "name": "Quick Question",
                "message": "سؤال سريع عن تكلفة تطبيق الذكاء الاصطناعي",
                "expected_actions": ["suggest_consultation_type"],
                "consultation_type": "quick_consultation",
                "language": "ar"
            },
            {
                "name": "Urgent Consultation",
                "message": "I need urgent consultation about AI implementation",
                "expected_actions": ["offer_immediate_consultation"],
                "language": "en"
            },
            {
                "name": "Schedule Request",
                "message": "أريد حجز موعد للاستشارة",
                "expected_actions": ["offer_scheduling"],
                "language": "ar"
            }
        ]
        
        results = []
        
        try:
            agent = ConsultingAgent(self.config)
            
            for test_case in test_cases:
                try:
                    response = await agent.process_consultation_message(
                        test_case["message"],
                        "test_customer_789",
                        test_case["language"]
                    )
                    
                    success = self._evaluate_response(response, test_case)
                    
                    results.append({
                        "test_name": test_case["name"],
                        "success": success,
                        "response": response,
                        "expected": test_case["expected_actions"],
                        "actual_actions": response.get("actions", [])
                    })
                    
                except Exception as e:
                    logger.error(f"Error in test {test_case['name']}: {e}")
                    results.append({
                        "test_name": test_case["name"],
                        "success": False,
                        "error": str(e)
                    })
        
        except Exception as e:
            logger.error(f"Failed to initialize Consulting Agent: {e}")
            return {"success_rate": 0.0, "results": [], "error": str(e)}
        
        success_rate = sum(1 for r in results if r.get("success", False)) / len(results)
        
        return {
            "success_rate": success_rate,
            "results": results,
            "total_tests": len(test_cases)
        } 
   
    def _evaluate_response(self, response: Dict[str, Any], test_case: Dict[str, Any]) -> bool:
        """Evaluate if response meets expectations"""
        if not response or "content" not in response:
            return False
        
        expected_actions = test_case.get("expected_actions", [])
        actual_actions = response.get("actions", [])
        
        if not expected_actions:
            return True  # No specific actions expected
        
        # Check if any expected action is present
        for expected_action in expected_actions:
            for actual_action in actual_actions:
                if expected_action in actual_action.get("type", ""):
                    return True
        
        return False
    
    def _calculate_success_rate(self, results: Dict[str, Any]) -> float:
        """Calculate overall success rate across all agents"""
        total_tests = 0
        successful_tests = 0
        
        for agent_name, agent_results in results.items():
            if "results" in agent_results:
                total_tests += len(agent_results["results"])
                successful_tests += sum(1 for r in agent_results["results"] if r.get("success", False))
        
        return successful_tests / total_tests if total_tests > 0 else 0.0
    
    async def _improve_prompts(self, results: Dict[str, Any]):
        """Analyze failures and improve prompts"""
        logger.info("🔧 Analyzing failures and improving prompts...")
        
        for agent_name, agent_results in results.items():
            if agent_results.get("success_rate", 0) < self.target_success_rate:
                await self._improve_agent_prompts(agent_name, agent_results)
    
    async def _improve_agent_prompts(self, agent_name: str, agent_results: Dict[str, Any]):
        """Improve prompts for specific agent based on failures"""
        logger.info(f"🎯 Improving prompts for {agent_name}")
        
        failed_tests = [r for r in agent_results.get("results", []) if not r.get("success", False)]
        
        if not failed_tests:
            return
        
        # Analyze common failure patterns
        failure_patterns = self._analyze_failure_patterns(failed_tests)
        
        # Generate improved prompts based on patterns
        improvements = self._generate_prompt_improvements(agent_name, failure_patterns)
        
        # Apply improvements (this would modify the agent classes)
        logger.info(f"📝 Generated {len(improvements)} prompt improvements for {agent_name}")
        
        for improvement in improvements:
            logger.info(f"  - {improvement}")
    
    def _analyze_failure_patterns(self, failed_tests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in failed tests"""
        patterns = {
            "language_issues": 0,
            "action_detection": 0,
            "response_quality": 0,
            "error_handling": 0
        }
        
        for test in failed_tests:
            if "error" in test:
                patterns["error_handling"] += 1
            elif not test.get("actual_actions"):
                patterns["action_detection"] += 1
            elif len(test.get("response", {}).get("content", "")) < 50:
                patterns["response_quality"] += 1
            else:
                patterns["language_issues"] += 1
        
        return patterns
    
    def _generate_prompt_improvements(self, agent_name: str, patterns: Dict[str, Any]) -> List[str]:
        """Generate specific prompt improvements"""
        improvements = []
        
        if patterns["action_detection"] > 0:
            improvements.append("Enhance action detection keywords and patterns")
            improvements.append("Add more explicit action triggers in system prompt")
        
        if patterns["response_quality"] > 0:
            improvements.append("Improve response structure and detail requirements")
            improvements.append("Add examples of high-quality responses")
        
        if patterns["language_issues"] > 0:
            improvements.append("Strengthen bilingual response capabilities")
            improvements.append("Add language-specific response templates")
        
        if patterns["error_handling"] > 0:
            improvements.append("Improve error handling and fallback responses")
            improvements.append("Add graceful degradation for missing dependencies")
        
        return improvements
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive final report"""
        logger.info("📊 Generating Final Test Report")
        
        final_results = self.test_results.get(f"iteration_{self.iteration_count}", {})
        overall_success_rate = self._calculate_success_rate(final_results)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "iterations_completed": self.iteration_count,
            "target_success_rate": self.target_success_rate,
            "achieved_success_rate": overall_success_rate,
            "target_achieved": overall_success_rate >= self.target_success_rate,
            "agent_results": {},
            "recommendations": []
        }
        
        # Detailed agent results
        for agent_name, agent_results in final_results.items():
            report["agent_results"][agent_name] = {
                "success_rate": agent_results.get("success_rate", 0),
                "total_tests": agent_results.get("total_tests", 0),
                "successful_tests": sum(1 for r in agent_results.get("results", []) if r.get("success", False)),
                "failed_tests": sum(1 for r in agent_results.get("results", []) if not r.get("success", False))
            }
        
        # Generate recommendations
        if overall_success_rate < self.target_success_rate:
            report["recommendations"].extend([
                "Continue iterating on prompt improvements",
                "Focus on agents with lowest success rates",
                "Consider adding more training examples",
                "Implement better error handling"
            ])
        else:
            report["recommendations"].extend([
                "Deploy agents to production environment",
                "Monitor performance in real-world scenarios",
                "Set up continuous testing pipeline",
                "Document successful prompt patterns"
            ])
        
        return report
    
    def print_results(self, report: Dict[str, Any]):
        """Print formatted test results"""
        print("\n" + "="*80)
        print("🧪 COMPREHENSIVE AGENT TESTING RESULTS")
        print("="*80)
        
        print(f"\n📊 Overall Results:")
        print(f"   Target Success Rate: {report['target_success_rate']:.1%}")
        print(f"   Achieved Success Rate: {report['achieved_success_rate']:.1%}")
        print(f"   Target Achieved: {'✅ YES' if report['target_achieved'] else '❌ NO'}")
        print(f"   Iterations Completed: {report['iterations_completed']}")
        
        print(f"\n🤖 Agent Performance:")
        for agent_name, results in report["agent_results"].items():
            status = "✅" if results["success_rate"] >= self.target_success_rate else "❌"
            print(f"   {status} {agent_name.replace('_', ' ').title()}: {results['success_rate']:.1%} ({results['successful_tests']}/{results['total_tests']})")
        
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"   {i}. {rec}")
        
        print("\n" + "="*80)

async def main():
    """Main testing function"""
    suite = AgentTestingSuite()
    
    try:
        report = await suite.run_comprehensive_tests()
        suite.print_results(report)
        
        # Save detailed report
        with open(f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report["achieved_success_rate"] >= suite.target_success_rate
        
    except Exception as e:
        logger.error(f"Testing suite failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)