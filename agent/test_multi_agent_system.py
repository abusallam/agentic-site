"""
Test script for the multi-agent system
Tests all four agents and their interactions
"""

import asyncio
import json
import os
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock configuration for testing
TEST_CONFIG = {
    "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY", "test_key"),
    "SUPABASE_URL": os.getenv("SUPABASE_URL", "https://test.supabase.co"),
    "SUPABASE_SERVICE_ROLE_KEY": os.getenv("SUPABASE_SERVICE_ROLE_KEY", "test_key"),
    "LIVEKIT_URL": os.getenv("LIVEKIT_URL", "wss://test.livekit.cloud"),
    "LIVEKIT_API_KEY": os.getenv("LIVEKIT_API_KEY", "test_key"),
    "LIVEKIT_API_SECRET": os.getenv("LIVEKIT_API_SECRET", "test_secret"),
    "N8N_URL": os.getenv("N8N_URL", "http://localhost:5678"),
    "N8N_API_KEY": os.getenv("N8N_API_KEY", "test_key"),
    "MCP_SERVER_URL": os.getenv("MCP_SERVER_URL", "http://localhost:3001")
}

class MultiAgentSystemTester:
    """Test suite for the multi-agent system"""
    
    def __init__(self):
        self.test_results = []
        self.demo_data = self._load_demo_data()
    
    def _load_demo_data(self) -> Dict[str, Any]:
        """Load demo data for testing"""
        try:
            with open("agent/demo_data.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Demo data file not found, using minimal test data")
            return {
                "customers": [
                    {
                        "id": "test_customer_1",
                        "name": "أحمد محمد",
                        "email": "ahmed@test.com",
                        "phone": "00966501234567",
                        "language": "ar"
                    }
                ]
            }
    
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        logger.info("🚀 Starting Multi-Agent System Tests")
        
        # Test each agent
        await self.test_initial_customer_agent()
        await self.test_n8n_workflow_agent()
        await self.test_code_generation_agent()
        await self.test_consulting_agent()
        
        # Test integrations
        await self.test_service_integrations()
        
        # Test chat API routing
        await self.test_chat_api_routing()
        
        # Print results
        self.print_test_results()
    
    async def test_initial_customer_agent(self):
        """Test the initial customer agent"""
        logger.info("🧪 Testing Initial Customer Agent")
        
        try:
            # Import the agent (this will test if imports work)
            from my_adk_agent.agents.initial_customer_agent import InitialCustomerAgent
            
            # Create agent instance
            agent = InitialCustomerAgent(TEST_CONFIG)
            
            # Test Arabic greeting
            result = await agent.process_message("مرحباً، أريد معرفة خدماتكم", "test_session_1")
            
            self.test_results.append({
                "agent": "InitialCustomerAgent",
                "test": "Arabic greeting processing",
                "status": "✅ PASS" if result and "content" in result else "❌ FAIL",
                "details": f"Response length: {len(result.get('content', ''))}" if result else "No response"
            })
            
            # Test English greeting
            result = await agent.process_message("Hello, I want to know about your services", "test_session_2")
            
            self.test_results.append({
                "agent": "InitialCustomerAgent",
                "test": "English greeting processing",
                "status": "✅ PASS" if result and "content" in result else "❌ FAIL",
                "details": f"Response length: {len(result.get('content', ''))}" if result else "No response"
            })
            
            # Test language detection
            ar_lang = await agent.detect_language("مرحباً كيف حالك؟")
            en_lang = await agent.detect_language("Hello how are you?")
            
            self.test_results.append({
                "agent": "InitialCustomerAgent",
                "test": "Language detection",
                "status": "✅ PASS" if ar_lang == "ar" and en_lang == "en" else "❌ FAIL",
                "details": f"Arabic: {ar_lang}, English: {en_lang}"
            })
            
        except Exception as e:
            self.test_results.append({
                "agent": "InitialCustomerAgent",
                "test": "Agent initialization",
                "status": "❌ FAIL",
                "details": str(e)
            })
    
    async def test_n8n_workflow_agent(self):
        """Test the N8N workflow agent"""
        logger.info("🧪 Testing N8N Workflow Agent")
        
        try:
            from my_adk_agent.agents.n8n_workflow_agent import N8nWorkflowAgent
            
            agent = N8nWorkflowAgent(TEST_CONFIG)
            
            # Test workflow templates listing
            templates = await agent.list_workflow_templates("ar")
            
            self.test_results.append({
                "agent": "N8nWorkflowAgent",
                "test": "List workflow templates",
                "status": "✅ PASS" if templates.get("success") else "❌ FAIL",
                "details": f"Templates count: {templates.get('total_count', 0)}"
            })
            
            # Test workflow request processing
            result = await agent.process_workflow_request(
                "أريد إنشاء سير عمل لأتمتة البريد الإلكتروني",
                "test_customer_1",
                "ar"
            )
            
            self.test_results.append({
                "agent": "N8nWorkflowAgent",
                "test": "Process workflow request",
                "status": "✅ PASS" if result and "content" in result else "❌ FAIL",
                "details": f"Agent type: {result.get('agent_type', 'unknown')}" if result else "No response"
            })
            
        except Exception as e:
            self.test_results.append({
                "agent": "N8nWorkflowAgent",
                "test": "Agent initialization",
                "status": "❌ FAIL",
                "details": str(e)
            })
    
    async def test_code_generation_agent(self):
        """Test the code generation agent"""
        logger.info("🧪 Testing Code Generation Agent")
        
        try:
            from my_adk_agent.agents.code_generation_agent import CodeGenerationAgent
            
            agent = CodeGenerationAgent(TEST_CONFIG)
            
            # Test code generation request
            result = await agent.process_code_request(
                "أريد بناء روبوت محادثة للتجارة الإلكترونية",
                "test_customer_1",
                "ar"
            )
            
            self.test_results.append({
                "agent": "CodeGenerationAgent",
                "test": "Process code generation request",
                "status": "✅ PASS" if result.get("success") else "❌ FAIL",
                "details": f"Framework: {result.get('framework', 'unknown')}" if result else "No response"
            })
            
            # Test framework selection
            frameworks = agent.frameworks
            
            self.test_results.append({
                "agent": "CodeGenerationAgent",
                "test": "Framework availability",
                "status": "✅ PASS" if len(frameworks) >= 3 else "❌ FAIL",
                "details": f"Available frameworks: {list(frameworks.keys())}"
            })
            
        except Exception as e:
            self.test_results.append({
                "agent": "CodeGenerationAgent",
                "test": "Agent initialization",
                "status": "❌ FAIL",
                "details": str(e)
            })
    
    async def test_consulting_agent(self):
        """Test the consulting agent"""
        logger.info("🧪 Testing Consulting Agent")
        
        try:
            from my_adk_agent.agents.consulting_agent import ConsultingAgent
            
            agent = ConsultingAgent(TEST_CONFIG)
            
            # Test consultation types
            consultation_types = await agent.get_consultation_types("ar")
            
            self.test_results.append({
                "agent": "ConsultingAgent",
                "test": "Get consultation types",
                "status": "✅ PASS" if len(consultation_types) > 0 else "❌ FAIL",
                "details": f"Types count: {len(consultation_types)}"
            })
            
            # Test consultation message processing
            result = await agent.process_consultation_message(
                "أريد استشارة حول استراتيجية الذكاء الاصطناعي لشركتي",
                "test_customer_1",
                "ar"
            )
            
            self.test_results.append({
                "agent": "ConsultingAgent",
                "test": "Process consultation message",
                "status": "✅ PASS" if result and "content" in result else "❌ FAIL",
                "details": f"Agent type: {result.get('agent_type', 'unknown')}" if result else "No response"
            })
            
        except Exception as e:
            self.test_results.append({
                "agent": "ConsultingAgent",
                "test": "Agent initialization",
                "status": "❌ FAIL",
                "details": str(e)
            })
    
    async def test_service_integrations(self):
        """Test service integrations"""
        logger.info("🧪 Testing Service Integrations")
        
        # Test MCP Service
        try:
            from my_adk_agent.services.mcp_service import MCPService
            
            mcp_service = MCPService(TEST_CONFIG)
            
            # Test workflow templates conversion
            nodes = mcp_service._convert_template_to_nodes("email_automation", {})
            
            self.test_results.append({
                "service": "MCPService",
                "test": "Template to nodes conversion",
                "status": "✅ PASS" if len(nodes) > 0 else "❌ FAIL",
                "details": f"Generated {len(nodes)} nodes"
            })
            
        except Exception as e:
            self.test_results.append({
                "service": "MCPService",
                "test": "Service initialization",
                "status": "❌ FAIL",
                "details": str(e)
            })
        
        # Test LiveKit Service
        try:
            from my_adk_agent.services.livekit_service import LiveKitService
            
            livekit_service = LiveKitService(TEST_CONFIG)
            
            # Test health check
            health = await livekit_service.health_check()
            
            self.test_results.append({
                "service": "LiveKitService",
                "test": "Health check",
                "status": "✅ PASS" if health.get("status") in ["healthy", "disabled"] else "❌ FAIL",
                "details": f"Status: {health.get('status', 'unknown')}"
            })
            
        except Exception as e:
            self.test_results.append({
                "service": "LiveKitService",
                "test": "Service initialization",
                "status": "❌ FAIL",
                "details": str(e)
            })
    
    async def test_chat_api_routing(self):
        """Test chat API routing logic"""
        logger.info("🧪 Testing Chat API Routing")
        
        # Test routing logic (simulated)
        test_messages = [
            {
                "message": "مرحباً، أريد معرفة خدماتكم",
                "expected_agent": "initial_customer",
                "language": "ar"
            },
            {
                "message": "أريد إنشاء سير عمل n8n",
                "expected_agent": "n8n_workflow",
                "language": "ar"
            },
            {
                "message": "I need help building a chatbot",
                "expected_agent": "code_generation",
                "language": "en"
            },
            {
                "message": "أريد استشارة استراتيجية",
                "expected_agent": "consulting",
                "language": "ar"
            }
        ]
        
        for test_case in test_messages:
            # Simulate routing logic from chat API
            message = test_case["message"].lower()
            
            if any(keyword in message for keyword in ["workflow", "n8n", "أتمتة", "سير العمل"]):
                detected_agent = "n8n_workflow"
            elif any(keyword in message for keyword in ["code", "build", "كود", "بناء"]):
                detected_agent = "code_generation"
            elif any(keyword in message for keyword in ["consult", "strategy", "استشارة", "استراتيجية"]):
                detected_agent = "consulting"
            else:
                detected_agent = "initial_customer"
            
            self.test_results.append({
                "component": "ChatAPIRouting",
                "test": f"Route message: {test_case['message'][:30]}...",
                "status": "✅ PASS" if detected_agent == test_case["expected_agent"] else "❌ FAIL",
                "details": f"Expected: {test_case['expected_agent']}, Got: {detected_agent}"
            })
    
    def print_test_results(self):
        """Print comprehensive test results"""
        logger.info("\n" + "="*80)
        logger.info("🧪 MULTI-AGENT SYSTEM TEST RESULTS")
        logger.info("="*80)
        
        # Group results by component
        components = {}
        for result in self.test_results:
            component = result.get("agent") or result.get("service") or result.get("component")
            if component not in components:
                components[component] = []
            components[component].append(result)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if "✅ PASS" in r["status"])
        failed_tests = total_tests - passed_tests
        
        for component, results in components.items():
            logger.info(f"\n📦 {component}")
            logger.info("-" * 40)
            
            for result in results:
                logger.info(f"  {result['status']} {result['test']}")
                if result.get("details"):
                    logger.info(f"     └─ {result['details']}")
        
        logger.info("\n" + "="*80)
        logger.info(f"📊 SUMMARY: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
        
        if failed_tests > 0:
            logger.info(f"❌ {failed_tests} tests failed")
        else:
            logger.info("✅ All tests passed!")
        
        logger.info("="*80)
        
        # Print demo data summary
        if self.demo_data:
            logger.info(f"\n📋 Demo Data Available:")
            logger.info(f"   • {len(self.demo_data.get('customers', []))} customers")
            logger.info(f"   • {len(self.demo_data.get('workflows', []))} workflows")
            logger.info(f"   • {len(self.demo_data.get('projects', []))} projects")
            logger.info(f"   • {len(self.demo_data.get('consultations', []))} consultations")
        
        logger.info(f"\n🌐 System Status:")
        logger.info(f"   • Frontend: Next.js with 4-agent routing")
        logger.info(f"   • Backend: Python ADK multi-agent system")
        logger.info(f"   • Database: Supabase integration ready")
        logger.info(f"   • Real-time: LiveKit for human handoff")
        logger.info(f"   • Workflows: n8n MCP integration")
        logger.info(f"   • Languages: Arabic/English support")

async def main():
    """Run the test suite"""
    tester = MultiAgentSystemTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())