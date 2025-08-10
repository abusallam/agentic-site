"""
Unit tests for base agent framework interface
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from agentic_core.agents.base_agent import (
    BaseAgent, 
    AgentFrameworkInterface, 
    AgentConfig, 
    AgentType, 
    ServiceType,
    AgentResponse,
    CustomerIntent
)


class TestAgentConfig:
    """Test AgentConfig data class"""
    
    def test_agent_config_creation(self):
        """Test creating agent configuration"""
        config = AgentConfig(
            agent_type=AgentType.WELCOMING,
            framework="ADK",
            model_name="gemini-pro",
            temperature=0.7,
            max_tokens=1000,
            system_prompt="Test prompt",
            capabilities=["routing", "analysis"]
        )
        
        assert config.agent_type == AgentType.WELCOMING
        assert config.framework == "ADK"
        assert config.model_name == "gemini-pro"
        assert config.temperature == 0.7
        assert config.max_tokens == 1000
        assert config.system_prompt == "Test prompt"
        assert config.capabilities == ["routing", "analysis"]
    
    def test_agent_config_defaults(self):
        """Test agent configuration with defaults"""
        config = AgentConfig(
            agent_type=AgentType.WORKFLOW,
            framework="LangGraph",
            model_name="gpt-4"
        )
        
        assert config.temperature == 0.7
        assert config.max_tokens == 1000
        assert config.system_prompt == ""
        assert config.capabilities is None


class TestAgentResponse:
    """Test AgentResponse data class"""
    
    def test_agent_response_creation(self):
        """Test creating agent response"""
        response = AgentResponse(
            message="Hello, how can I help you?",
            confidence=0.9,
            next_action="gather_requirements",
            context={"user_id": "123"},
            metadata={"processing_time": 1.5}
        )
        
        assert response.message == "Hello, how can I help you?"
        assert response.confidence == 0.9
        assert response.next_action == "gather_requirements"
        assert response.context == {"user_id": "123"}
        assert response.metadata == {"processing_time": 1.5}


class TestCustomerIntent:
    """Test CustomerIntent data class"""
    
    def test_customer_intent_creation(self):
        """Test creating customer intent"""
        intent = CustomerIntent(
            service_type=ServiceType.FAST_SOLUTION,
            confidence=0.8,
            requirements={"type": "chatbot", "platform": "website"},
            urgency="high"
        )
        
        assert intent.service_type == ServiceType.FAST_SOLUTION
        assert intent.confidence == 0.8
        assert intent.requirements == {"type": "chatbot", "platform": "website"}
        assert intent.urgency == "high"
    
    def test_customer_intent_defaults(self):
        """Test customer intent with defaults"""
        intent = CustomerIntent(
            service_type=ServiceType.CONSULTATION,
            confidence=0.7,
            requirements={}
        )
        
        assert intent.urgency == "normal"


class MockAgent(BaseAgent):
    """Mock agent for testing BaseAgent functionality"""
    
    def process_message(self, message: str, context=None):
        return AgentResponse(
            message=f"Processed: {message}",
            confidence=0.8
        )
    
    def get_system_prompt(self):
        return "Mock agent system prompt"


class TestBaseAgent:
    """Test BaseAgent abstract class"""
    
    def test_base_agent_initialization(self):
        """Test base agent initialization"""
        config = AgentConfig(
            agent_type=AgentType.WELCOMING,
            framework="ADK",
            model_name="gemini-pro"
        )
        
        agent = MockAgent(config)
        
        assert agent.config == config
        assert agent.agent_type == AgentType.WELCOMING
        assert agent.framework == "ADK"
        assert agent.conversation_history == []
        assert agent.context == {}
    
    def test_update_context(self):
        """Test updating agent context"""
        config = AgentConfig(
            agent_type=AgentType.WORKFLOW,
            framework="ADK",
            model_name="gemini-pro"
        )
        
        agent = MockAgent(config)
        agent.update_context("user_id", "123")
        agent.update_context("session_id", "abc")
        
        assert agent.context["user_id"] == "123"
        assert agent.context["session_id"] == "abc"
    
    def test_get_context(self):
        """Test getting values from agent context"""
        config = AgentConfig(
            agent_type=AgentType.PROFESSIONAL,
            framework="ADK",
            model_name="gemini-pro"
        )
        
        agent = MockAgent(config)
        agent.update_context("test_key", "test_value")
        
        assert agent.get_context("test_key") == "test_value"
        assert agent.get_context("nonexistent_key") is None
        assert agent.get_context("nonexistent_key", "default") == "default"
    
    def test_add_to_history(self):
        """Test adding messages to conversation history"""
        config = AgentConfig(
            agent_type=AgentType.CONSULTING,
            framework="ADK",
            model_name="gemini-pro"
        )
        
        agent = MockAgent(config)
        
        with patch.object(agent, '_get_timestamp', return_value="2024-01-01T00:00:00Z"):
            agent.add_to_history("user", "Hello")
            agent.add_to_history("assistant", "Hi there!")
        
        assert len(agent.conversation_history) == 2
        assert agent.conversation_history[0]["role"] == "user"
        assert agent.conversation_history[0]["message"] == "Hello"
        assert agent.conversation_history[0]["timestamp"] == "2024-01-01T00:00:00Z"
        assert agent.conversation_history[1]["role"] == "assistant"
        assert agent.conversation_history[1]["message"] == "Hi there!"
    
    def test_clear_history(self):
        """Test clearing conversation history"""
        config = AgentConfig(
            agent_type=AgentType.WELCOMING,
            framework="ADK",
            model_name="gemini-pro"
        )
        
        agent = MockAgent(config)
        agent.add_to_history("user", "Test message")
        
        assert len(agent.conversation_history) == 1
        
        agent.clear_history()
        
        assert len(agent.conversation_history) == 0
    
    def test_get_capabilities(self):
        """Test getting agent capabilities"""
        config = AgentConfig(
            agent_type=AgentType.WORKFLOW,
            framework="ADK",
            model_name="gemini-pro",
            capabilities=["workflow_creation", "automation"]
        )
        
        agent = MockAgent(config)
        capabilities = agent.get_capabilities()
        
        assert capabilities == ["workflow_creation", "automation"]
    
    def test_get_capabilities_empty(self):
        """Test getting capabilities when none are set"""
        config = AgentConfig(
            agent_type=AgentType.PROFESSIONAL,
            framework="ADK",
            model_name="gemini-pro"
        )
        
        agent = MockAgent(config)
        capabilities = agent.get_capabilities()
        
        assert capabilities == []
    
    def test_process_message(self):
        """Test processing message through agent"""
        config = AgentConfig(
            agent_type=AgentType.WELCOMING,
            framework="ADK",
            model_name="gemini-pro"
        )
        
        agent = MockAgent(config)
        response = agent.process_message("Hello, I need help")
        
        assert isinstance(response, AgentResponse)
        assert response.message == "Processed: Hello, I need help"
        assert response.confidence == 0.8
    
    def test_get_system_prompt(self):
        """Test getting system prompt"""
        config = AgentConfig(
            agent_type=AgentType.CONSULTING,
            framework="ADK",
            model_name="gemini-pro"
        )
        
        agent = MockAgent(config)
        prompt = agent.get_system_prompt()
        
        assert prompt == "Mock agent system prompt"


class MockFramework(AgentFrameworkInterface):
    """Mock framework for testing AgentFrameworkInterface"""
    
    def initialize_agent(self, config):
        return MockAgent(config)
    
    def process_message(self, message, context):
        return AgentResponse(
            message=f"Framework processed: {message}",
            confidence=0.9
        )
    
    def get_capabilities(self):
        return ["mock_capability_1", "mock_capability_2"]


class TestAgentFrameworkInterface:
    """Test AgentFrameworkInterface abstract class"""
    
    def test_framework_interface_implementation(self):
        """Test framework interface implementation"""
        framework = MockFramework()
        
        # Test initialize_agent
        config = AgentConfig(
            agent_type=AgentType.WELCOMING,
            framework="Mock",
            model_name="test-model"
        )
        
        agent = framework.initialize_agent(config)
        assert isinstance(agent, MockAgent)
        assert agent.config == config
        
        # Test process_message
        response = framework.process_message("Test message", {})
        assert isinstance(response, AgentResponse)
        assert response.message == "Framework processed: Test message"
        assert response.confidence == 0.9
        
        # Test get_capabilities
        capabilities = framework.get_capabilities()
        assert capabilities == ["mock_capability_1", "mock_capability_2"]


class TestEnums:
    """Test enum classes"""
    
    def test_agent_type_enum(self):
        """Test AgentType enum values"""
        assert AgentType.WELCOMING.value == "welcoming"
        assert AgentType.WORKFLOW.value == "workflow"
        assert AgentType.PROFESSIONAL.value == "professional"
        assert AgentType.CONSULTING.value == "consulting"
    
    def test_service_type_enum(self):
        """Test ServiceType enum values"""
        assert ServiceType.FAST_SOLUTION.value == "fast_solution"
        assert ServiceType.CUSTOM_SOLUTION.value == "custom_solution"
        assert ServiceType.CONSULTATION.value == "consultation"


if __name__ == "__main__":
    pytest.main([__file__])