"""Test configuration and fixtures for the agent tests."""

import os
import pytest
from unittest.mock import Mock, AsyncMock
from typing import AsyncGenerator, Generator

# Set test environment variables
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test_db"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_ANON_KEY"] = "test-anon-key"
os.environ["SUPABASE_SERVICE_KEY"] = "test-service-key"
os.environ["GEMINI_API_KEY"] = "test-gemini-key"
os.environ["N8N_URL"] = "http://localhost:5678"
os.environ["N8N_API_KEY"] = "test-n8n-key"
os.environ["MCP_SERVER_URL"] = "http://localhost:3001"
os.environ["LIVEKIT_URL"] = "ws://localhost:7880"
os.environ["LIVEKIT_API_KEY"] = "test-livekit-key"
os.environ["LIVEKIT_SECRET_KEY"] = "test-livekit-secret"
os.environ["STRIPE_SECRET_KEY"] = "sk_test_123"
os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_test_123"


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing."""
    mock_client = Mock()
    mock_client.table.return_value = mock_client
    mock_client.select.return_value = mock_client
    mock_client.insert.return_value = mock_client
    mock_client.update.return_value = mock_client
    mock_client.delete.return_value = mock_client
    mock_client.eq.return_value = mock_client
    mock_client.execute.return_value = Mock(data=[], error=None)
    return mock_client


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini client for testing."""
    mock_client = Mock()
    mock_client.generate_content = AsyncMock(
        return_value=Mock(text="Test response from Gemini")
    )
    return mock_client


@pytest.fixture
def mock_n8n_client():
    """Mock n8n client for testing."""
    mock_client = Mock()
    mock_client.get_workflows = AsyncMock(return_value=[])
    mock_client.execute_workflow = AsyncMock(return_value={"success": True})
    return mock_client


@pytest.fixture
def mock_mcp_client():
    """Mock MCP client for testing."""
    mock_client = Mock()
    mock_client.call_tool = AsyncMock(return_value={"result": "success"})
    mock_client.list_tools = AsyncMock(return_value=[])
    return mock_client


@pytest.fixture
def mock_livekit_client():
    """Mock Livekit client for testing."""
    mock_client = Mock()
    mock_client.create_room = AsyncMock(return_value=Mock(name="test-room"))
    mock_client.get_room = AsyncMock(return_value=Mock(name="test-room"))
    return mock_client


@pytest.fixture
def mock_stripe_client():
    """Mock Stripe client for testing."""
    mock_client = Mock()
    mock_client.Customer.create = Mock(return_value=Mock(id="cus_test123"))
    mock_client.PaymentIntent.create = Mock(
        return_value=Mock(id="pi_test123", client_secret="pi_test123_secret")
    )
    return mock_client


@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing."""
    return {
        "id": "test-customer-123",
        "email": "test@example.com",
        "name": "Test Customer",
        "phone": "+1234567890",
        "company": "Test Company",
        "requirements": "Need AI chatbot for customer support",
        "budget": 5000,
        "timeline": "2 weeks",
    }


@pytest.fixture
def sample_conversation_data():
    """Sample conversation data for testing."""
    return {
        "id": "conv-123",
        "customer_id": "test-customer-123",
        "messages": [
            {"role": "user", "content": "Hello, I need help with AI chatbots"},
            {"role": "assistant", "content": "I'd be happy to help you with AI chatbots!"},
        ],
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_workflow_data():
    """Sample n8n workflow data for testing."""
    return {
        "id": "workflow-123",
        "name": "Customer Onboarding",
        "active": True,
        "nodes": [
            {
                "name": "Start",
                "type": "n8n-nodes-base.start",
                "position": [250, 300],
            }
        ],
    }


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment after each test."""
    yield
    # Clean up any test-specific environment changes
    pass


class MockADKAgent:
    """Mock ADK Agent for testing."""
    
    def __init__(self):
        self.tools = []
        self.services = {}
    
    async def process_message(self, message: str) -> str:
        return f"Mock response to: {message}"
    
    def add_tool(self, tool):
        self.tools.append(tool)
    
    def add_service(self, name: str, service):
        self.services[name] = service


@pytest.fixture
def mock_adk_agent():
    """Mock ADK agent for testing."""
    return MockADKAgent()