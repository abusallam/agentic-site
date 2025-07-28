"""Unit tests for the main agent functionality."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from my_adk_agent.agent import CustomerJourneyAgent


class TestCustomerJourneyAgent:
    """Test cases for CustomerJourneyAgent."""

    @pytest.fixture
    def agent(self, mock_supabase_client, mock_gemini_client):
        """Create agent instance for testing."""
        with patch('my_adk_agent.agent.create_client', return_value=mock_supabase_client):
            agent = CustomerJourneyAgent()
            agent.gemini_client = mock_gemini_client
            return agent

    def test_agent_initialization(self, agent):
        """Test that agent initializes correctly."""
        assert agent is not None
        assert hasattr(agent, 'supabase')
        assert hasattr(agent, 'gemini_client')

    @pytest.mark.asyncio
    async def test_process_customer_inquiry(self, agent, sample_customer_data):
        """Test processing customer inquiry."""
        inquiry = "I need help with AI chatbots for my business"
        
        # Mock the agent's response
        agent.gemini_client.generate_content.return_value = Mock(
            text="I'd be happy to help you with AI chatbots!"
        )
        
        response = await agent.process_customer_inquiry(inquiry, sample_customer_data)
        
        assert response is not None
        assert isinstance(response, str)
        agent.gemini_client.generate_content.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_customer_record(self, agent, sample_customer_data):
        """Test creating customer record."""
        # Mock successful database insert
        agent.supabase.table.return_value.insert.return_value.execute.return_value = Mock(
            data=[sample_customer_data], error=None
        )
        
        result = await agent.create_customer_record(sample_customer_data)
        
        assert result is not None
        agent.supabase.table.assert_called_with('customers')

    @pytest.mark.asyncio
    async def test_get_customer_requirements(self, agent, sample_customer_data):
        """Test extracting customer requirements."""
        conversation_history = [
            "I need an AI chatbot for customer support",
            "My budget is around $5000",
            "I need it completed in 2 weeks"
        ]
        
        requirements = await agent.get_customer_requirements(
            conversation_history, sample_customer_data
        )
        
        assert requirements is not None
        assert isinstance(requirements, dict)
        assert 'budget' in requirements or 'timeline' in requirements

    def test_validate_customer_data(self, agent):
        """Test customer data validation."""
        valid_data = {
            "email": "test@example.com",
            "name": "Test Customer",
            "requirements": "Need AI chatbot"
        }
        
        invalid_data = {
            "email": "invalid-email",
            "name": "",
        }
        
        assert agent.validate_customer_data(valid_data) is True
        assert agent.validate_customer_data(invalid_data) is False

    @pytest.mark.asyncio
    async def test_error_handling(self, agent):
        """Test error handling in agent methods."""
        # Mock database error
        agent.supabase.table.return_value.insert.return_value.execute.return_value = Mock(
            data=None, error=Mock(message="Database error")
        )
        
        with pytest.raises(Exception):
            await agent.create_customer_record({"invalid": "data"})

    def test_agent_tools_registration(self, agent):
        """Test that agent tools are properly registered."""
        # This would test that all required tools are available
        # Implementation depends on how ADK tools are structured
        assert hasattr(agent, 'tools') or hasattr(agent, '_tools')

    @pytest.mark.asyncio
    async def test_conversation_context_management(self, agent, sample_conversation_data):
        """Test conversation context management."""
        conversation_id = sample_conversation_data['id']
        
        # Mock conversation retrieval
        agent.supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[sample_conversation_data], error=None
        )
        
        context = await agent.get_conversation_context(conversation_id)
        
        assert context is not None
        assert 'messages' in context
        agent.supabase.table.assert_called_with('conversations')