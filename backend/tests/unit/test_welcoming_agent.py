"""
Unit tests for Welcoming Agent
"""
import pytest
from unittest.mock import Mock, patch

from agentic_core.agents.welcoming_agent import WelcomingAgent
from agentic_core.agents.base_agent import (
    AgentConfig, 
    AgentType, 
    ServiceType, 
    CustomerIntent,
    AgentResponse
)


class TestWelcomingAgent:
    """Test WelcomingAgent functionality"""
    
    @pytest.fixture
    def agent_config(self):
        """Create agent configuration for testing"""
        return AgentConfig(
            agent_type=AgentType.WELCOMING,
            framework="ADK",
            model_name="gemini-pro",
            temperature=0.7,
            system_prompt="Test welcoming agent"
        )
    
    @pytest.fixture
    def welcoming_agent(self, agent_config):
        """Create welcoming agent instance"""
        return WelcomingAgent(agent_config)
    
    def test_agent_initialization(self, welcoming_agent):
        """Test welcoming agent initialization"""
        assert welcoming_agent.agent_type == AgentType.WELCOMING
        assert welcoming_agent.framework == "ADK"
        assert len(welcoming_agent.routing_rules) == 3
        assert ServiceType.FAST_SOLUTION in welcoming_agent.routing_rules
        assert ServiceType.CUSTOM_SOLUTION in welcoming_agent.routing_rules
        assert ServiceType.CONSULTATION in welcoming_agent.routing_rules
    
    def test_get_system_prompt(self, welcoming_agent):
        """Test getting system prompt"""
        prompt = welcoming_agent.get_system_prompt()
        
        assert "Welcoming Agent" in prompt
        assert "FAST_SOLUTION" in prompt
        assert "CUSTOM_SOLUTION" in prompt
        assert "CONSULTATION" in prompt
        assert "professional" in prompt.lower()
    
    def test_analyze_customer_intent_fast_solution(self, welcoming_agent):
        """Test analyzing customer intent for fast solution"""
        message = "I need a quick chatbot for my website"
        
        intent = welcoming_agent.analyze_customer_intent(message)
        
        assert isinstance(intent, CustomerIntent)
        assert intent.service_type == ServiceType.FAST_SOLUTION
        assert intent.confidence > 0
        assert intent.requirements["original_message"] == message
        assert intent.urgency == "normal"
    
    def test_analyze_customer_intent_custom_solution(self, welcoming_agent):
        """Test analyzing customer intent for custom solution"""
        message = "I need custom development for a complex enterprise integration"
        
        intent = welcoming_agent.analyze_customer_intent(message)
        
        assert intent.service_type == ServiceType.CUSTOM_SOLUTION
        assert intent.confidence > 0
        assert "enterprise" in intent.requirements["extracted_features"]
    
    def test_analyze_customer_intent_consultation(self, welcoming_agent):
        """Test analyzing customer intent for consultation"""
        message = "I'd like to schedule a consultation to discuss my business strategy"
        
        intent = welcoming_agent.analyze_customer_intent(message)
        
        assert intent.service_type == ServiceType.CONSULTATION
        assert intent.confidence > 0
    
    def test_analyze_customer_intent_urgency_detection(self, welcoming_agent):
        """Test urgency detection in customer messages"""
        urgent_message = "I need this urgently, ASAP!"
        high_message = "I need this done quickly"
        normal_message = "I need help with my project"
        
        urgent_intent = welcoming_agent.analyze_customer_intent(urgent_message)
        high_intent = welcoming_agent.analyze_customer_intent(high_message)
        normal_intent = welcoming_agent.analyze_customer_intent(normal_message)
        
        assert urgent_intent.urgency == "urgent"
        assert high_intent.urgency == "high"
        assert normal_intent.urgency == "normal"
    
    def test_pattern_based_scoring(self, welcoming_agent):
        """Test pattern-based scoring for better accuracy"""
        # Test fast solution patterns
        fast_message = "I need a quick and simple bot for automation"
        fast_scores = welcoming_agent._pattern_based_scoring(fast_message.lower())
        assert fast_scores[ServiceType.FAST_SOLUTION] > 0
        
        # Test custom solution patterns
        custom_message = "I need custom development for my specific requirements"
        custom_scores = welcoming_agent._pattern_based_scoring(custom_message.lower())
        assert custom_scores[ServiceType.CUSTOM_SOLUTION] > 0
        
        # Test consultation patterns
        consultation_message = "I want to schedule a meeting for consultation"
        consultation_scores = welcoming_agent._pattern_based_scoring(consultation_message.lower())
        assert consultation_scores[ServiceType.CONSULTATION] > 0
    
    def test_extract_requirements(self, welcoming_agent):
        """Test extracting requirements from customer message"""
        message = "I need a website with API integration and automated workflows"
        
        requirements = welcoming_agent._extract_requirements(message)
        
        assert requirements["original_message"] == message
        assert "website" in requirements["extracted_features"]
        assert "api" in requirements["extracted_features"]
        assert "automate" in requirements["extracted_features"]
    
    def test_generate_welcome_response_fast_solution(self, welcoming_agent):
        """Test generating welcome response for fast solution"""
        intent = CustomerIntent(
            service_type=ServiceType.FAST_SOLUTION,
            confidence=0.8,
            requirements={}
        )
        
        response = welcoming_agent._generate_welcome_response(intent)
        
        assert "N8N Workflow Agent" in response
        assert "quick automation solution" in response
        assert "templates" in response
    
    def test_generate_welcome_response_custom_solution(self, welcoming_agent):
        """Test generating welcome response for custom solution"""
        intent = CustomerIntent(
            service_type=ServiceType.CUSTOM_SOLUTION,
            confidence=0.8,
            requirements={}
        )
        
        response = welcoming_agent._generate_welcome_response(intent)
        
        assert "Professional Agent" in response
        assert "custom solution" in response
        assert "development" in response
    
    def test_generate_welcome_response_consultation(self, welcoming_agent):
        """Test generating welcome response for consultation"""
        intent = CustomerIntent(
            service_type=ServiceType.CONSULTATION,
            confidence=0.8,
            requirements={}
        )
        
        response = welcoming_agent._generate_welcome_response(intent)
        
        assert "Consulting Agent" in response
        assert "consultation services" in response
        assert "schedule" in response
    
    def test_determine_next_action_high_confidence(self, welcoming_agent):
        """Test determining next action with high confidence"""
        intent = CustomerIntent(
            service_type=ServiceType.FAST_SOLUTION,
            confidence=0.8,
            requirements={}
        )
        
        next_action = welcoming_agent._determine_next_action(intent)
        
        assert next_action == "route_to_fast_solution_agent"
    
    def test_determine_next_action_low_confidence(self, welcoming_agent):
        """Test determining next action with low confidence"""
        intent = CustomerIntent(
            service_type=ServiceType.FAST_SOLUTION,
            confidence=0.5,
            requirements={}
        )
        
        next_action = welcoming_agent._determine_next_action(intent)
        
        assert next_action == "request_clarification"
    
    def test_process_message_complete_flow(self, welcoming_agent):
        """Test complete message processing flow"""
        message = "I need a simple chatbot for customer support"
        
        with patch.object(welcoming_agent, 'add_to_history') as mock_add_history:
            response = welcoming_agent.process_message(message)
        
        # Verify response structure
        assert isinstance(response, AgentResponse)
        assert response.message is not None
        assert response.confidence > 0
        assert response.next_action is not None
        assert response.context is not None
        
        # Verify context contains expected data
        assert "intent" in response.context
        assert "service_type" in response.context
        assert "requirements" in response.context
        
        # Verify history was updated
        assert mock_add_history.call_count == 2  # user message + assistant response
    
    def test_routing_methods(self, welcoming_agent):
        """Test routing methods for different service types"""
        intent = CustomerIntent(
            service_type=ServiceType.FAST_SOLUTION,
            confidence=0.8,
            requirements={"test": "data"}
        )
        
        # Test N8N agent routing
        n8n_routing = welcoming_agent._route_to_n8n_agent(intent)
        assert n8n_routing["agent"] == "n8n_workflow"
        assert n8n_routing["handoff_data"]["intent"] == intent
        
        # Test professional agent routing
        professional_routing = welcoming_agent._route_to_professional_agent(intent)
        assert professional_routing["agent"] == "professional"
        assert professional_routing["handoff_data"]["context"] == "custom_solution_routing"
        
        # Test consulting agent routing
        consulting_routing = welcoming_agent._route_to_consulting_agent(intent)
        assert consulting_routing["agent"] == "consulting"
        assert consulting_routing["handoff_data"]["context"] == "consultation_routing"
    
    def test_intent_keywords_coverage(self, welcoming_agent):
        """Test that intent keywords are properly defined"""
        # Verify all service types have keywords
        assert ServiceType.FAST_SOLUTION in welcoming_agent.intent_keywords
        assert ServiceType.CUSTOM_SOLUTION in welcoming_agent.intent_keywords
        assert ServiceType.CONSULTATION in welcoming_agent.intent_keywords
        
        # Verify keywords are not empty
        for service_type, keywords in welcoming_agent.intent_keywords.items():
            assert len(keywords) > 0
            assert all(isinstance(keyword, str) for keyword in keywords)
    
    def test_edge_cases(self, welcoming_agent):
        """Test edge cases and error handling"""
        # Empty message
        empty_response = welcoming_agent.process_message("")
        assert isinstance(empty_response, AgentResponse)
        
        # Very long message
        long_message = "test " * 1000
        long_response = welcoming_agent.process_message(long_message)
        assert isinstance(long_response, AgentResponse)
        
        # Special characters
        special_message = "I need help with @#$%^&*() integration!"
        special_response = welcoming_agent.process_message(special_message)
        assert isinstance(special_response, AgentResponse)


if __name__ == "__main__":
    pytest.main([__file__])