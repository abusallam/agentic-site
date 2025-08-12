"""
Mock Google ADK implementation for development and testing
This simulates the Google Agent Development Kit functionality
"""

import asyncio
import json
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MockGenerativeModel:
    """Mock Google Generative AI model"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
    
    async def generate_content_async(self, prompt: str) -> 'MockResponse':
        """Generate mock response based on prompt"""
        # Simple mock responses based on prompt content
        if "مرحبا" in prompt or "hello" in prompt.lower():
            content = "مرحباً! أنا مساعدك الذكي. كيف يمكنني مساعدتك اليوم؟" if "مرحبا" in prompt else "Hello! I'm your AI assistant. How can I help you today?"
        elif "workflow" in prompt.lower() or "سير العمل" in prompt:
            content = "يمكنني مساعدتك في إنشاء وإدارة سير العمل. ما نوع الأتمتة التي تحتاجها؟" if "سير العمل" in prompt else "I can help you create and manage workflows. What type of automation do you need?"
        elif "code" in prompt.lower() or "كود" in prompt:
            content = "سأساعدك في إنشاء كود مخصص. اخبرني عن متطلبات مشروعك." if "كود" in prompt else "I'll help you generate custom code. Tell me about your project requirements."
        elif "consult" in prompt.lower() or "استشارة" in prompt:
            content = "أقدم استشارات متخصصة في الذكاء الاصطناعي. ما نوع الاستشارة التي تحتاجها؟" if "استشارة" in prompt else "I provide specialized AI consulting. What type of consultation do you need?"
        else:
            content = "شكراً لرسالتك. كيف يمكنني مساعدتك؟" if any(arabic_char in prompt for arabic_char in "أإآابتثجحخدذرزسشصضطظعغفقكلمنهوي") else "Thank you for your message. How can I help you?"
        
        return MockResponse(content)

class MockResponse:
    """Mock response from generative model"""
    
    def __init__(self, content: str):
        self.content = content
        self.text = content

def tool(*args, **kwargs):
    """Mock tool decorator that can handle various usage patterns"""
    def decorator(func):
        func._is_tool = True
        return func
    
    # If called with a function directly (@tool)
    if len(args) == 1 and callable(args[0]) and not kwargs:
        return decorator(args[0])
    
    # If called with parameters (@tool(...))
    return decorator

class Agent:
    """Mock Google ADK Agent base class"""
    
    def __init__(self, name: str, description: str, model: MockGenerativeModel, system_prompt: str):
        self.name = name
        self.description = description
        self.model = model
        self.system_prompt = system_prompt
        logger.info(f"Mock Agent initialized: {name}")
    
    async def run(self, prompt: str) -> Dict[str, Any]:
        """Run the agent with a prompt"""
        response = await self.model.generate_content_async(f"{self.system_prompt}\n\n{prompt}")
        return {
            "content": response.content,
            "agent": self.name,
            "timestamp": datetime.now().isoformat()
        }

# Mock the google.adk module structure
class MockGoogleADK:
    Agent = Agent
    tool = tool
    
    class GenerativeModel:
        def __init__(self, model_name: str):
            return MockGenerativeModel(model_name)

# Create mock modules
import sys
sys.modules['google'] = type('MockGoogle', (), {})()
sys.modules['google.adk'] = MockGoogleADK()
sys.modules['google.generativeai'] = type('MockGenerativeAI', (), {
    'GenerativeModel': MockGenerativeModel
})()