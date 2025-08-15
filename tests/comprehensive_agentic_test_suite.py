#!/usr/bin/env python3
"""
Comprehensive Agentic Test Suite
Tests all agents, LLM integration, N8N workflows, and system functionality
"""

import asyncio
import json
import time
import requests
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result data structure"""
    name: str
    status: str  # "passed", "failed", "skipped"
    duration: float
    details: Dict[str, Any]
    error: Optional[str] = None

@dataclass
class AgentTestResults:
    """Agent-specific test results"""
    agent_name: str
    arabic_tests: List[TestResult]
    english_tests: List[TestResult]
    llm_integration: List[TestResult]
    workflow_tests: List[TestResult]
    overall_score: float

@dataclass
class ComprehensiveTestResults:
    """Complete test suite results"""
    timestamp: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    success_rate: float
    agent_results: List[AgentTestResults]
    n8n_tests: List[TestResult]
    e2e_tests: List[TestResult]
    performance_tests: List[TestResult]
    security_tests: List[TestResult]

class AgenticTestFramework:
    """Main testing framework for agentic system"""
    
    def __init__(self):
        self.base_url = "http://217.79.255.54"
        self.backend_url = f"{self.base_url}:8001"
        self.frontend_url = f"{self.base_url}:3001"
        self.n8n_url = f"{self.base_url}:5680"
        self.results = ComprehensiveTestResults(
            timestamp=datetime.now().isoformat(),
            total_tests=0,
            passed_tests=0,
            failed_tests=0,
            success_rate=0.0,
            agent_results=[],
            n8n_tests=[],
            e2e_tests=[],
            performance_tests=[],
            security_tests=[]
        )
    
    async def run_comprehensive_tests(self) -> ComprehensiveTestResults:
        """Run all test suites"""
        print("🚀 Starting Comprehensive Agentic Test Suite")
        print("=" * 70)
        
        # Test N8N deployment first
        await self.test_n8n_deployment()
        
        # Test all agents
        await self.test_all_agents()
        
        # Test LLM integration
        await self.test_llm_integration()
        
        # Test system integration
        await self.test_system_integration()
        
        # Test performance
        await self.test_performance()
        
        # Test security
        await self.test_security()
        
        # Generate final report
        self.calculate_final_results()
        return self.results
    
    async def test_n8n_deployment(self):
        """Test N8N deployment and integration"""
        print("\n🔧 Testing N8N Deployment and Integration")
        print("-" * 50)
        
        # Test N8N accessibility
        result = await self.test_n8n_accessibility()
        self.results.n8n_tests.append(result)
        
        # Test N8N authentication
        result = await self.test_n8n_authentication()
        self.results.n8n_tests.append(result)
        
        # Test N8N API endpoints
        result = await self.test_n8n_api_endpoints()
        self.results.n8n_tests.append(result)
        
        # Test workflow creation
        result = await self.test_n8n_workflow_creation()
        self.results.n8n_tests.append(result)
        
        # Test MCP integration
        result = await self.test_mcp_n8n_integration()
        self.results.n8n_tests.append(result)
    
    async def test_n8n_accessibility(self) -> TestResult:
        """Test if N8N is accessible"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.n8n_url}", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200 and 'n8n' in response.text:
                return TestResult(
                    name="N8N Accessibility",
                    status="passed",
                    duration=duration,
                    details={"status_code": response.status_code, "response_size": len(response.text)}
                )
            else:
                return TestResult(
                    name="N8N Accessibility",
                    status="failed",
                    duration=duration,
                    details={"status_code": response.status_code},
                    error="N8N UI not accessible or invalid response"
                )
        except Exception as e:
            return TestResult(
                name="N8N Accessibility",
                status="failed",
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    async def test_n8n_authentication(self) -> TestResult:
        """Test N8N authentication"""
        start_time = time.time()
        try:
            response = requests.get(
                f"{self.n8n_url}/rest/workflows",
                auth=('admin', 'admin123'),
                timeout=10
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                workflows = response.json()
                return TestResult(
                    name="N8N Authentication",
                    status="passed",
                    duration=duration,
                    details={"workflow_count": len(workflows) if isinstance(workflows, list) else 0}
                )
            else:
                return TestResult(
                    name="N8N Authentication",
                    status="failed",
                    duration=duration,
                    details={"status_code": response.status_code},
                    error="Authentication failed"
                )
        except Exception as e:
            return TestResult(
                name="N8N Authentication",
                status="failed",
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    async def test_n8n_api_endpoints(self) -> TestResult:
        """Test N8N API endpoints"""
        start_time = time.time()
        endpoints = [
            "/rest/workflows",
            "/rest/credentials", 
            "/rest/executions"
        ]
        
        results = {}
        for endpoint in endpoints:
            try:
                response = requests.get(
                    f"{self.n8n_url}{endpoint}",
                    auth=('admin', 'admin123'),
                    timeout=10
                )
                results[endpoint] = {
                    "status_code": response.status_code,
                    "accessible": response.status_code == 200
                }
            except Exception as e:
                results[endpoint] = {
                    "status_code": 0,
                    "accessible": False,
                    "error": str(e)
                }
        
        duration = time.time() - start_time
        accessible_count = sum(1 for r in results.values() if r.get("accessible", False))
        
        if accessible_count == len(endpoints):
            status = "passed"
            error = None
        elif accessible_count > 0:
            status = "failed"
            error = f"Only {accessible_count}/{len(endpoints)} endpoints accessible"
        else:
            status = "failed"
            error = "No endpoints accessible"
        
        return TestResult(
            name="N8N API Endpoints",
            status=status,
            duration=duration,
            details={"endpoints": results, "accessible_count": accessible_count},
            error=error
        )
    
    async def test_n8n_workflow_creation(self) -> TestResult:
        """Test N8N workflow creation"""
        start_time = time.time()
        try:
            workflow_data = {
                "name": f"Test Workflow {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "nodes": [
                    {
                        "id": "start-node",
                        "name": "Start",
                        "type": "n8n-nodes-base.start",
                        "position": [250, 300],
                        "parameters": {}
                    }
                ],
                "connections": {},
                "active": False
            }
            
            response = requests.post(
                f"{self.n8n_url}/rest/workflows",
                auth=('admin', 'admin123'),
                json=workflow_data,
                timeout=15
            )
            
            duration = time.time() - start_time
            
            if response.status_code in [200, 201]:
                workflow = response.json()
                return TestResult(
                    name="N8N Workflow Creation",
                    status="passed",
                    duration=duration,
                    details={"workflow_id": workflow.get("id"), "workflow_name": workflow.get("name")}
                )
            else:
                return TestResult(
                    name="N8N Workflow Creation",
                    status="failed",
                    duration=duration,
                    details={"status_code": response.status_code, "response": response.text[:200]},
                    error="Failed to create workflow"
                )
        except Exception as e:
            return TestResult(
                name="N8N Workflow Creation",
                status="failed",
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    async def test_mcp_n8n_integration(self) -> TestResult:
        """Test MCP to N8N integration"""
        start_time = time.time()
        try:
            # Test backend MCP service
            response = requests.post(
                f"{self.backend_url}/api/test-mcp-n8n",
                json={"test": "mcp_integration"},
                timeout=15
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                return TestResult(
                    name="MCP N8N Integration",
                    status="passed",
                    duration=duration,
                    details=result
                )
            else:
                return TestResult(
                    name="MCP N8N Integration",
                    status="failed",
                    duration=duration,
                    details={"status_code": response.status_code},
                    error="MCP integration test failed"
                )
        except Exception as e:
            return TestResult(
                name="MCP N8N Integration",
                status="failed",
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    async def test_all_agents(self):
        """Test all specialized agents"""
        print("\n🤖 Testing All Specialized Agents")
        print("-" * 50)
        
        agents = [
            "InitialCustomerAgent",
            "N8nWorkflowAgent", 
            "CodeGenerationAgent",
            "ConsultingAgent"
        ]
        
        for agent_name in agents:
            agent_results = await self.test_agent_comprehensive(agent_name)
            self.results.agent_results.append(agent_results)
    
    async def test_agent_comprehensive(self, agent_name: str) -> AgentTestResults:
        """Comprehensive testing for a specific agent"""
        print(f"\n🧪 Testing {agent_name}")
        
        # Test Arabic responses
        arabic_tests = await self.test_agent_arabic_responses(agent_name)
        
        # Test English responses
        english_tests = await self.test_agent_english_responses(agent_name)
        
        # Test LLM integration
        llm_tests = await self.test_agent_llm_integration(agent_name)
        
        # Test workflow integration
        workflow_tests = await self.test_agent_workflow_integration(agent_name)
        
        # Calculate overall score
        all_tests = arabic_tests + english_tests + llm_tests + workflow_tests
        passed_tests = sum(1 for test in all_tests if test.status == "passed")
        overall_score = (passed_tests / len(all_tests)) * 100 if all_tests else 0
        
        return AgentTestResults(
            agent_name=agent_name,
            arabic_tests=arabic_tests,
            english_tests=english_tests,
            llm_integration=llm_tests,
            workflow_tests=workflow_tests,
            overall_score=overall_score
        )
    
    async def test_agent_arabic_responses(self, agent_name: str) -> List[TestResult]:
        """Test agent Arabic language responses"""
        arabic_prompts = [
            "مرحبا، أحتاج مساعدة في إنشاء موقع إلكتروني",
            "ما هي خدماتكم في مجال الذكاء الاصطناعي؟",
            "أريد تطوير تطبيق جوال للتجارة الإلكترونية",
            "كيف يمكنني أتمتة العمليات التجارية؟",
            "أحتاج استشارة تقنية لمشروعي الجديد"
        ]
        
        results = []
        for prompt in arabic_prompts:
            result = await self.test_agent_response(agent_name, prompt, "arabic")
            results.append(result)
        
        return results
    
    async def test_agent_english_responses(self, agent_name: str) -> List[TestResult]:
        """Test agent English language responses"""
        english_prompts = [
            "Hello, I need help creating a website",
            "What are your AI services?",
            "I want to develop a mobile e-commerce app",
            "How can I automate my business processes?",
            "I need technical consulting for my new project"
        ]
        
        results = []
        for prompt in english_prompts:
            result = await self.test_agent_response(agent_name, prompt, "english")
            results.append(result)
        
        return results
    
    async def test_agent_response(self, agent_name: str, prompt: str, language: str) -> TestResult:
        """Test individual agent response"""
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.backend_url}/api/agent-test",
                json={
                    "agent": agent_name,
                    "prompt": prompt,
                    "language": language
                },
                timeout=30
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Validate response quality
                response_text = result.get("response", "")
                quality_score = self.evaluate_response_quality(response_text, language)
                
                return TestResult(
                    name=f"{agent_name} {language.title()} Response",
                    status="passed" if quality_score > 0.7 else "failed",
                    duration=duration,
                    details={
                        "prompt": prompt[:50] + "...",
                        "response_length": len(response_text),
                        "quality_score": quality_score,
                        "language_detected": self.detect_language(response_text)
                    },
                    error=None if quality_score > 0.7 else "Low quality response"
                )
            else:
                return TestResult(
                    name=f"{agent_name} {language.title()} Response",
                    status="failed",
                    duration=duration,
                    details={"status_code": response.status_code},
                    error="Agent response failed"
                )
        except Exception as e:
            return TestResult(
                name=f"{agent_name} {language.title()} Response",
                status="failed",
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    def evaluate_response_quality(self, response: str, language: str) -> float:
        """Evaluate response quality (0.0 to 1.0)"""
        if not response or len(response) < 10:
            return 0.0
        
        score = 0.0
        
        # Length check
        if 50 <= len(response) <= 1000:
            score += 0.3
        
        # Language appropriateness
        if language == "arabic":
            arabic_chars = sum(1 for char in response if '\u0600' <= char <= '\u06FF')
            if arabic_chars > len(response) * 0.3:
                score += 0.4
        else:
            english_chars = sum(1 for char in response if char.isascii())
            if english_chars > len(response) * 0.7:
                score += 0.4
        
        # Content quality indicators
        quality_indicators = [
            "help", "assist", "service", "solution", "project",
            "مساعدة", "خدمة", "حل", "مشروع", "تطوير"
        ]
        
        if any(indicator in response.lower() for indicator in quality_indicators):
            score += 0.3
        
        return min(score, 1.0)
    
    def detect_language(self, text: str) -> str:
        """Simple language detection"""
        arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
        if arabic_chars > len(text) * 0.3:
            return "arabic"
        return "english"
    
    async def test_agent_llm_integration(self, agent_name: str) -> List[TestResult]:
        """Test agent LLM integration"""
        results = []
        
        # Test Gemini integration
        result = await self.test_gemini_integration(agent_name)
        results.append(result)
        
        # Test response generation speed
        result = await self.test_response_speed(agent_name)
        results.append(result)
        
        return results
    
    async def test_gemini_integration(self, agent_name: str) -> TestResult:
        """Test Gemini Flash integration"""
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.backend_url}/api/test-gemini",
                json={
                    "agent": agent_name,
                    "prompt": "Test Gemini integration"
                },
                timeout=20
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                return TestResult(
                    name=f"{agent_name} Gemini Integration",
                    status="passed",
                    duration=duration,
                    details=result
                )
            else:
                return TestResult(
                    name=f"{agent_name} Gemini Integration",
                    status="failed",
                    duration=duration,
                    details={"status_code": response.status_code},
                    error="Gemini integration failed"
                )
        except Exception as e:
            return TestResult(
                name=f"{agent_name} Gemini Integration",
                status="failed",
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    async def test_response_speed(self, agent_name: str) -> TestResult:
        """Test agent response speed"""
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.backend_url}/api/agent-speed-test",
                json={"agent": agent_name},
                timeout=10
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200 and duration < 5.0:
                return TestResult(
                    name=f"{agent_name} Response Speed",
                    status="passed",
                    duration=duration,
                    details={"response_time": duration}
                )
            else:
                return TestResult(
                    name=f"{agent_name} Response Speed",
                    status="failed",
                    duration=duration,
                    details={"response_time": duration},
                    error="Response too slow" if duration >= 5.0 else "Speed test failed"
                )
        except Exception as e:
            return TestResult(
                name=f"{agent_name} Response Speed",
                status="failed",
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    async def test_agent_workflow_integration(self, agent_name: str) -> List[TestResult]:
        """Test agent workflow integration"""
        results = []
        
        if agent_name == "N8nWorkflowAgent":
            # Test workflow creation
            result = await self.test_workflow_creation_via_agent()
            results.append(result)
            
            # Test workflow execution
            result = await self.test_workflow_execution_via_agent()
            results.append(result)
        else:
            # Test general workflow integration
            result = await self.test_general_workflow_integration(agent_name)
            results.append(result)
        
        return results
    
    async def test_workflow_creation_via_agent(self) -> TestResult:
        """Test workflow creation via N8nWorkflowAgent"""
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.backend_url}/api/create-workflow",
                json={
                    "workflow_name": "Agent Test Workflow",
                    "workflow_type": "test"
                },
                timeout=20
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                return TestResult(
                    name="Workflow Creation via Agent",
                    status="passed",
                    duration=duration,
                    details=result
                )
            else:
                return TestResult(
                    name="Workflow Creation via Agent",
                    status="failed",
                    duration=duration,
                    details={"status_code": response.status_code},
                    error="Workflow creation failed"
                )
        except Exception as e:
            return TestResult(
                name="Workflow Creation via Agent",
                status="failed",
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    async def test_workflow_execution_via_agent(self) -> TestResult:
        """Test workflow execution via N8nWorkflowAgent"""
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.backend_url}/api/execute-workflow",
                json={
                    "workflow_id": "test-workflow",
                    "parameters": {"test": True}
                },
                timeout=20
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                return TestResult(
                    name="Workflow Execution via Agent",
                    status="passed",
                    duration=duration,
                    details=result
                )
            else:
                return TestResult(
                    name="Workflow Execution via Agent",
                    status="failed",
                    duration=duration,
                    details={"status_code": response.status_code},
                    error="Workflow execution failed"
                )
        except Exception as e:
            return TestResult(
                name="Workflow Execution via Agent",
                status="failed",
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    async def test_general_workflow_integration(self, agent_name: str) -> TestResult:
        """Test general workflow integration for non-workflow agents"""
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.backend_url}/api/test-workflow-integration",
                json={"agent": agent_name},
                timeout=15
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                return TestResult(
                    name=f"{agent_name} Workflow Integration",
                    status="passed",
                    duration=duration,
                    details=response.json()
                )
            else:
                return TestResult(
                    name=f"{agent_name} Workflow Integration",
                    status="failed",
                    duration=duration,
                    details={"status_code": response.status_code},
                    error="Workflow integration test failed"
                )
        except Exception as e:
            return TestResult(
                name=f"{agent_name} Workflow Integration",
                status="failed",
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    async def test_llm_integration(self):
        """Test LLM integration comprehensively"""
        print("\n🧠 Testing LLM Integration")
        print("-" * 50)
        
        # Test Gemini Flash API
        result = await self.test_gemini_api_direct()
        self.results.performance_tests.append(result)
        
        # Test response quality
        result = await self.test_llm_response_quality()
        self.results.performance_tests.append(result)
        
        # Test Arabic language processing
        result = await self.test_arabic_llm_processing()
        self.results.performance_tests.append(result)
    
    async def test_gemini_api_direct(self) -> TestResult:
        """Test direct Gemini API integration"""
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.backend_url}/api/test-gemini-direct",
                json={"prompt": "Test direct Gemini API call"},
                timeout=15
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                return TestResult(
                    name="Direct Gemini API Test",
                    status="passed",
                    duration=duration,
                    details=result
                )
            else:
                return TestResult(
                    name="Direct Gemini API Test",
                    status="failed",
                    duration=duration,
                    details={"status_code": response.status_code},
                    error="Direct Gemini API test failed"
                )
        except Exception as e:
            return TestResult(
                name="Direct Gemini API Test",
                status="failed",
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    async def test_llm_response_quality(self) -> TestResult:
        """Test LLM response quality"""
        start_time = time.time()
        try:
            test_prompts = [
                "Explain artificial intelligence in simple terms",
                "What are the benefits of workflow automation?",
                "How can AI help small businesses?"
            ]
            
            quality_scores = []
            for prompt in test_prompts:
                response = requests.post(
                    f"{self.backend_url}/api/test-llm-quality",
                    json={"prompt": prompt},
                    timeout=20
                )
                
                if response.status_code == 200:
                    result = response.json()
                    quality_score = self.evaluate_response_quality(result.get("response", ""), "english")
                    quality_scores.append(quality_score)
            
            duration = time.time() - start_time
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            return TestResult(
                name="LLM Response Quality",
                status="passed" if avg_quality > 0.7 else "failed",
                duration=duration,
                details={
                    "average_quality": avg_quality,
                    "quality_scores": quality_scores,
                    "test_count": len(test_prompts)
                },
                error=None if avg_quality > 0.7 else "Low average quality score"
            )
        except Exception as e:
            return TestResult(
                name="LLM Response Quality",
                status="failed",
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    async def test_arabic_llm_processing(self) -> TestResult:
        """Test Arabic language processing"""
        start_time = time.time()
        try:
            arabic_prompts = [
                "اشرح الذكاء الاصطناعي بطريقة بسيطة",
                "ما هي فوائد أتمتة سير العمل؟",
                "كيف يمكن للذكاء الاصطناعي مساعدة الشركات الصغيرة؟"
            ]
            
            arabic_scores = []
            for prompt in arabic_prompts:
                response = requests.post(
                    f"{self.backend_url}/api/test-arabic-llm",
                    json={"prompt": prompt},
                    timeout=20
                )
                
                if response.status_code == 200:
                    result = response.json()
                    quality_score = self.evaluate_response_quality(result.get("response", ""), "arabic")
                    arabic_scores.append(quality_score)
            
            duration = time.time() - start_time
            avg_arabic_quality = sum(arabic_scores) / len(arabic_scores) if arabic_scores else 0
            
            return TestResult(
                name="Arabic LLM Processing",
                status="passed" if avg_arabic_quality > 0.7 else "failed",
                duration=duration,
                details={
                    "average_arabic_quality": avg_arabic_quality,
                    "arabic_scores": arabic_scores,
                    "test_count": len(arabic_prompts)
                },
                error=None if avg_arabic_quality > 0.7 else "Low Arabic processing quality"
            )
        except Exception as e:
            return TestResult(
                name="Arabic LLM Processing",
                status="failed",
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    async def test_system_integration(self):
        """Test system integration"""
        print("\n🔗 Testing System Integration")
        print("-" * 50)
        
        # Test frontend-backend integration
        result = await self.test_frontend_backend_integration()
        self.results.e2e_tests.append(result)
        
        # Test database connectivity
        result = await self.test_database_connectivity()
        self.results.e2e_tests.append(result)
        
        # Test service health
        result = await self.test_service_health()
        self.results.e2e_tests.append(result)
    
    async def test_frontend_backend_integration(self) -> TestResult:
        """Test frontend-backend integration"""
        start_time = time.time()
        try:
            # Test frontend accessibility
            frontend_response = requests.get(f"{self.frontend_url}", timeout=10)
            
            # Test backend API
            backend_response = requests.get(f"{self.backend_url}/health", timeout=10)
            
            duration = time.time() - start_time
            
            if frontend_response.status_code == 200 and backend_response.status_code == 200:
                return TestResult(
                    name="Frontend-Backend Integration",
                    status="passed",
                    duration=duration,
                    details={
                        "frontend_status": frontend_response.status_code,
                        "backend_status": backend_response.status_code
                    }
                )
            else:
                return TestResult(
                    name="Frontend-Backend Integration",
                    status="failed",
                    duration=duration,
                    details={
                        "frontend_status": frontend_response.status_code,
                        "backend_status": backend_response.status_code
                    },
                    error="Frontend or backend not accessible"
                )
        except Exception as e:
            return TestResult(
                name="Frontend-Backend Integration",
                status="failed",
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    async def test_database_connectivity(self) -> TestResult:
        """Test database connectivity"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.backend_url}/api/test-database", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                return TestResult(
                    name="Database Connectivity",
                    status="passed",
                    duration=duration,
                    details=result
                )
            else:
                return TestResult(
                    name="Database Connectivity",
                    status="failed",
                    duration=duration,
                    details={"status_code": response.status_code},
                    error="Database connectivity test failed"
                )
        except Exception as e:
            return TestResult(
                name="Database Connectivity",
                status="failed",
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    async def test_service_health(self) -> TestResult:
        """Test overall service health"""
        start_time = time.time()
        try:
            services = {
                "frontend": f"{self.frontend_url}",
                "backend": f"{self.backend_url}/health",
                "n8n": f"{self.n8n_url}"
            }
            
            health_results = {}
            for service, url in services.items():
                try:
                    response = requests.get(url, timeout=5)
                    health_results[service] = {
                        "status": "healthy" if response.status_code == 200 else "unhealthy",
                        "status_code": response.status_code
                    }
                except Exception as e:
                    health_results[service] = {
                        "status": "unhealthy",
                        "error": str(e)
                    }
            
            duration = time.time() - start_time
            healthy_services = sum(1 for result in health_results.values() if result.get("status") == "healthy")
            
            return TestResult(
                name="Service Health Check",
                status="passed" if healthy_services == len(services) else "failed",
                duration=duration,
                details={
                    "services": health_results,
                    "healthy_count": healthy_services,
                    "total_count": len(services)
                },
                error=None if healthy_services == len(services) else f"Only {healthy_services}/{len(services)} services healthy"
            )
        except Exception as e:
            return TestResult(
                name="Service Health Check",
                status="failed",
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    async def test_performance(self):
        """Test system performance"""
        print("\n⚡ Testing System Performance")
        print("-" * 50)
        
        # Test response times
        result = await self.test_response_times()
        self.results.performance_tests.append(result)
        
        # Test concurrent requests
        result = await self.test_concurrent_requests()
        self.results.performance_tests.append(result)
    
    async def test_response_times(self) -> TestResult:
        """Test system response times"""
        start_time = time.time()
        try:
            endpoints = [
                f"{self.frontend_url}",
                f"{self.backend_url}/health",
                f"{self.backend_url}/api/test",
                f"{self.n8n_url}/rest/workflows"
            ]
            
            response_times = {}
            for endpoint in endpoints:
                endpoint_start = time.time()
                try:
                    if "n8n" in endpoint:
                        response = requests.get(endpoint, auth=('admin', 'admin123'), timeout=10)
                    else:
                        response = requests.get(endpoint, timeout=10)
                    
                    response_time = time.time() - endpoint_start
                    response_times[endpoint] = {
                        "response_time": response_time,
                        "status_code": response.status_code,
                        "meets_target": response_time < 2.0
                    }
                except Exception as e:
                    response_times[endpoint] = {
                        "response_time": time.time() - endpoint_start,
                        "error": str(e),
                        "meets_target": False
                    }
            
            duration = time.time() - start_time
            meeting_targets = sum(1 for result in response_times.values() if result.get("meets_target", False))
            
            return TestResult(
                name="Response Times",
                status="passed" if meeting_targets == len(endpoints) else "failed",
                duration=duration,
                details={
                    "response_times": response_times,
                    "meeting_targets": meeting_targets,
                    "total_endpoints": len(endpoints)
                },
                error=None if meeting_targets == len(endpoints) else f"Only {meeting_targets}/{len(endpoints)} endpoints meet response time targets"
            )
        except Exception as e:
            return TestResult(
                name="Response Times",
                status="failed",
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    async def test_concurrent_requests(self) -> TestResult:
        """Test concurrent request handling"""
        start_time = time.time()
        try:
            import concurrent.futures
            import threading
            
            def make_request():
                try:
                    response = requests.get(f"{self.backend_url}/health", timeout=10)
                    return {"status_code": response.status_code, "success": response.status_code == 200}
                except Exception as e:
                    return {"error": str(e), "success": False}
            
            # Test with 10 concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(10)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            duration = time.time() - start_time
            successful_requests = sum(1 for result in results if result.get("success", False))
            
            return TestResult(
                name="Concurrent Requests",
                status="passed" if successful_requests >= 8 else "failed",
                duration=duration,
                details={
                    "total_requests": len(results),
                    "successful_requests": successful_requests,
                    "success_rate": successful_requests / len(results)
                },
                error=None if successful_requests >= 8 else f"Only {successful_requests}/10 concurrent requests succeeded"
            )
        except Exception as e:
            return TestResult(
                name="Concurrent Requests",
                status="failed",
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    async def test_security(self):
        """Test security features"""
        print("\n🔒 Testing Security Features")
        print("-" * 50)
        
        # Test input validation
        result = await self.test_input_validation()
        self.results.security_tests.append(result)
        
        # Test authentication
        result = await self.test_authentication_security()
        self.results.security_tests.append(result)
        
        # Test RROC framework
        result = await self.test_rroc_framework()
        self.results.security_tests.append(result)
    
    async def test_input_validation(self) -> TestResult:
        """Test input validation"""
        start_time = time.time()
        try:
            malicious_inputs = [
                "<script>alert('xss')</script>",
                "'; DROP TABLE users; --",
                "../../../etc/passwd",
                "{{7*7}}",
                "javascript:alert('xss')"
            ]
            
            validation_results = {}
            for malicious_input in malicious_inputs:
                response = requests.post(
                    f"{self.backend_url}/api/test-input-validation",
                    json={"input": malicious_input},
                    timeout=10
                )
                
                validation_results[malicious_input] = {
                    "status_code": response.status_code,
                    "blocked": response.status_code in [400, 403, 422]
                }
            
            duration = time.time() - start_time
            blocked_count = sum(1 for result in validation_results.values() if result.get("blocked", False))
            
            return TestResult(
                name="Input Validation",
                status="passed" if blocked_count >= len(malicious_inputs) * 0.8 else "failed",
                duration=duration,
                details={
                    "validation_results": validation_results,
                    "blocked_count": blocked_count,
                    "total_tests": len(malicious_inputs)
                },
                error=None if blocked_count >= len(malicious_inputs) * 0.8 else f"Only {blocked_count}/{len(malicious_inputs)} malicious inputs blocked"
            )
        except Exception as e:
            return TestResult(
                name="Input Validation",
                status="failed",
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    async def test_authentication_security(self) -> TestResult:
        """Test authentication security"""
        start_time = time.time()
        try:
            # Test unauthorized access
            response = requests.get(f"{self.backend_url}/api/admin-only", timeout=10)
            unauthorized_blocked = response.status_code in [401, 403]
            
            # Test N8N authentication
            n8n_response = requests.get(f"{self.n8n_url}/rest/workflows", timeout=10)
            n8n_auth_required = n8n_response.status_code in [401, 403]
            
            duration = time.time() - start_time
            
            return TestResult(
                name="Authentication Security",
                status="passed" if unauthorized_blocked and n8n_auth_required else "failed",
                duration=duration,
                details={
                    "unauthorized_blocked": unauthorized_blocked,
                    "n8n_auth_required": n8n_auth_required
                },
                error=None if unauthorized_blocked and n8n_auth_required else "Authentication security issues detected"
            )
        except Exception as e:
            return TestResult(
                name="Authentication Security",
                status="failed",
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    async def test_rroc_framework(self) -> TestResult:
        """Test RROC (Request-Response-Output Control) framework"""
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.backend_url}/api/test-rroc",
                json={"test": "rroc_framework"},
                timeout=15
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                return TestResult(
                    name="RROC Framework",
                    status="passed",
                    duration=duration,
                    details=result
                )
            else:
                return TestResult(
                    name="RROC Framework",
                    status="failed",
                    duration=duration,
                    details={"status_code": response.status_code},
                    error="RROC framework test failed"
                )
        except Exception as e:
            return TestResult(
                name="RROC Framework",
                status="failed",
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    def calculate_final_results(self):
        """Calculate final test results"""
        all_tests = []
        
        # Collect all tests
        all_tests.extend(self.results.n8n_tests)
        all_tests.extend(self.results.e2e_tests)
        all_tests.extend(self.results.performance_tests)
        all_tests.extend(self.results.security_tests)
        
        # Add agent tests
        for agent_result in self.results.agent_results:
            all_tests.extend(agent_result.arabic_tests)
            all_tests.extend(agent_result.english_tests)
            all_tests.extend(agent_result.llm_integration)
            all_tests.extend(agent_result.workflow_tests)
        
        # Calculate totals
        self.results.total_tests = len(all_tests)
        self.results.passed_tests = sum(1 for test in all_tests if test.status == "passed")
        self.results.failed_tests = self.results.total_tests - self.results.passed_tests
        self.results.success_rate = (self.results.passed_tests / self.results.total_tests * 100) if self.results.total_tests > 0 else 0
    
    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        report = f"""
🚀 COMPREHENSIVE AGENTIC TEST SUITE REPORT
{'=' * 70}

📊 OVERALL RESULTS:
   Total Tests: {self.results.total_tests}
   Passed: {self.results.passed_tests}
   Failed: {self.results.failed_tests}
   Success Rate: {self.results.success_rate:.1f}%
   Timestamp: {self.results.timestamp}

🔧 N8N DEPLOYMENT TESTS:
"""
        
        for test in self.results.n8n_tests:
            status_icon = "✅" if test.status == "passed" else "❌"
            report += f"   {status_icon} {test.name}: {test.status.upper()} ({test.duration:.2f}s)\n"
            if test.error:
                report += f"      Error: {test.error}\n"
        
        report += f"\n🤖 AGENT TESTS:\n"
        for agent_result in self.results.agent_results:
            report += f"   Agent: {agent_result.agent_name} (Score: {agent_result.overall_score:.1f}%)\n"
            report += f"      Arabic Tests: {len([t for t in agent_result.arabic_tests if t.status == 'passed'])}/{len(agent_result.arabic_tests)} passed\n"
            report += f"      English Tests: {len([t for t in agent_result.english_tests if t.status == 'passed'])}/{len(agent_result.english_tests)} passed\n"
            report += f"      LLM Integration: {len([t for t in agent_result.llm_integration if t.status == 'passed'])}/{len(agent_result.llm_integration)} passed\n"
            report += f"      Workflow Tests: {len([t for t in agent_result.workflow_tests if t.status == 'passed'])}/{len(agent_result.workflow_tests)} passed\n"
        
        report += f"\n🔗 INTEGRATION TESTS:\n"
        for test in self.results.e2e_tests:
            status_icon = "✅" if test.status == "passed" else "❌"
            report += f"   {status_icon} {test.name}: {test.status.upper()} ({test.duration:.2f}s)\n"
        
        report += f"\n⚡ PERFORMANCE TESTS:\n"
        for test in self.results.performance_tests:
            status_icon = "✅" if test.status == "passed" else "❌"
            report += f"   {status_icon} {test.name}: {test.status.upper()} ({test.duration:.2f}s)\n"
        
        report += f"\n🔒 SECURITY TESTS:\n"
        for test in self.results.security_tests:
            status_icon = "✅" if test.status == "passed" else "❌"
            report += f"   {status_icon} {test.name}: {test.status.upper()} ({test.duration:.2f}s)\n"
        
        report += f"\n🎯 RECOMMENDATIONS:\n"
        if self.results.success_rate >= 90:
            report += "   🎉 Excellent! System is production-ready.\n"
        elif self.results.success_rate >= 80:
            report += "   ✅ Good! Minor issues to address before production.\n"
        elif self.results.success_rate >= 70:
            report += "   ⚠️  Moderate issues detected. Requires attention.\n"
        else:
            report += "   🚨 Significant issues detected. Not ready for production.\n"
        
        return report
    
    def save_results(self, filename: str = None):
        """Save test results to JSON file"""
        if not filename:
            filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(asdict(self.results), f, indent=2, default=str)
        
        print(f"\n📄 Test results saved to: {filename}")

async def main():
    """Main test execution function"""
    framework = AgenticTestFramework()
    
    try:
        results = await framework.run_comprehensive_tests()
        
        # Generate and display report
        report = framework.generate_report()
        print(report)
        
        # Save results
        framework.save_results()
        
        # Exit with appropriate code
        sys.exit(0 if results.success_rate >= 70 else 1)
        
    except KeyboardInterrupt:
        print("\n🛑 Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())