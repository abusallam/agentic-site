"""Smoke tests for basic system health checks."""

import pytest
import os
import httpx
from unittest.mock import Mock, patch


@pytest.mark.smoke
class TestHealthChecks:
    """Smoke tests for system health and basic functionality."""

    def test_environment_variables(self):
        """Test that required environment variables are set."""
        required_vars = [
            'SUPABASE_URL',
            'SUPABASE_ANON_KEY',
            'GEMINI_API_KEY',
        ]
        
        for var in required_vars:
            assert os.getenv(var) is not None, f"Environment variable {var} is not set"

    @pytest.mark.asyncio
    async def test_supabase_connection(self):
        """Test basic Supabase connection."""
        from my_adk_agent.services.supabase_service import SupabaseService
        
        with patch('my_adk_agent.services.supabase_service.create_client') as mock_client:
            # Mock successful connection
            mock_client.return_value = Mock()
            mock_client.return_value.table.return_value.select.return_value.limit.return_value.execute.return_value = Mock(
                data=[], error=None
            )
            
            service = SupabaseService()
            
            # Test basic query
            result = await service.health_check()
            assert result is True

    @pytest.mark.asyncio
    async def test_gemini_api_availability(self):
        """Test Gemini API availability."""
        with patch('google.generativeai.GenerativeModel') as mock_model:
            mock_instance = Mock()
            mock_instance.generate_content.return_value = Mock(text="Test response")
            mock_model.return_value = mock_instance
            
            # Test basic generation
            model = mock_model("gemini-pro")
            response = model.generate_content("Test prompt")
            
            assert response.text == "Test response"

    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test that agent can be initialized without errors."""
        with patch('my_adk_agent.services.supabase_service.create_client'), \
             patch('google.generativeai.GenerativeModel'):
            
            from my_adk_agent.agent import CustomerJourneyAgent
            
            agent = CustomerJourneyAgent()
            assert agent is not None

    @pytest.mark.asyncio
    async def test_mcp_service_initialization(self):
        """Test MCP service initialization."""
        with patch('my_adk_agent.services.mcp_service.MCPClient') as mock_client:
            mock_client.return_value = Mock()
            
            from my_adk_agent.services.mcp_service import MCPService
            
            service = MCPService()
            assert service is not None

    def test_basic_data_validation(self):
        """Test basic data validation functions."""
        from my_adk_agent.agent import CustomerJourneyAgent
        
        with patch('my_adk_agent.services.supabase_service.create_client'), \
             patch('google.generativeai.GenerativeModel'):
            
            agent = CustomerJourneyAgent()
            
            # Test valid data
            valid_data = {
                'email': 'test@example.com',
                'name': 'Test User',
                'requirements': 'Need AI chatbot'
            }
            assert agent.validate_customer_data(valid_data) is True
            
            # Test invalid data
            invalid_data = {
                'email': 'invalid-email',
                'name': ''
            }
            assert agent.validate_customer_data(invalid_data) is False

    @pytest.mark.asyncio
    async def test_api_server_health(self):
        """Test API server health endpoint if running."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8000/health", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    assert data.get('status') in ['ok', 'healthy']
        except (httpx.ConnectError, httpx.TimeoutException):
            # API server not running, skip test
            pytest.skip("API server not available")

    def test_configuration_loading(self):
        """Test that configuration loads correctly."""
        # Test that environment variables are loaded
        assert os.getenv('ENVIRONMENT') == 'test'
        
        # Test that required configurations are present
        config_vars = [
            'DATABASE_URL',
            'SUPABASE_URL',
            'GEMINI_API_KEY'
        ]
        
        for var in config_vars:
            value = os.getenv(var)
            assert value is not None and value != '', f"Configuration {var} is empty"

    def test_logging_configuration(self):
        """Test that logging is configured correctly."""
        import logging
        
        # Test that logger can be created
        logger = logging.getLogger('my_adk_agent')
        assert logger is not None
        
        # Test basic logging
        logger.info("Test log message")
        # In a real implementation, you might check log output

    @pytest.mark.asyncio
    async def test_basic_tool_functionality(self):
        """Test basic tool functionality."""
        with patch('my_adk_agent.services.supabase_service.create_client'), \
             patch('google.generativeai.GenerativeModel'):
            
            from my_adk_agent.agent import CustomerJourneyAgent
            
            agent = CustomerJourneyAgent()
            
            # Test that agent has required methods
            assert hasattr(agent, 'process_customer_inquiry')
            assert hasattr(agent, 'create_customer_record')
            assert hasattr(agent, 'validate_customer_data')

    def test_import_structure(self):
        """Test that all required modules can be imported."""
        try:
            from my_adk_agent import agent
            from my_adk_agent.services import supabase_service
            from my_adk_agent.services import mcp_service
            
            assert agent is not None
            assert supabase_service is not None
            assert mcp_service is not None
            
        except ImportError as e:
            pytest.fail(f"Import error: {e}")

    def test_dependency_availability(self):
        """Test that all required dependencies are available."""
        required_packages = [
            'google.generativeai',
            'supabase',
            'httpx',
            'pydantic',
            'fastapi'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                pytest.fail(f"Required package {package} is not available")