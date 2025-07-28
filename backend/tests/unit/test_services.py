"""Unit tests for service integrations."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from my_adk_agent.services.supabase_service import SupabaseService
from my_adk_agent.services.mcp_service import MCPService


class TestSupabaseService:
    """Test cases for SupabaseService."""

    @pytest.fixture
    def supabase_service(self, mock_supabase_client):
        """Create SupabaseService instance for testing."""
        with patch('my_adk_agent.services.supabase_service.create_client', return_value=mock_supabase_client):
            return SupabaseService()

    @pytest.mark.asyncio
    async def test_create_customer(self, supabase_service, sample_customer_data):
        """Test creating a customer record."""
        # Mock successful insert
        supabase_service.client.table.return_value.insert.return_value.execute.return_value = Mock(
            data=[sample_customer_data], error=None
        )
        
        result = await supabase_service.create_customer(sample_customer_data)
        
        assert result is not None
        assert result['id'] == sample_customer_data['id']

    @pytest.mark.asyncio
    async def test_get_customer(self, supabase_service, sample_customer_data):
        """Test retrieving a customer record."""
        customer_id = sample_customer_data['id']
        
        # Mock successful select
        supabase_service.client.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[sample_customer_data], error=None
        )
        
        result = await supabase_service.get_customer(customer_id)
        
        assert result is not None
        assert result['id'] == customer_id

    @pytest.mark.asyncio
    async def test_update_customer(self, supabase_service, sample_customer_data):
        """Test updating a customer record."""
        customer_id = sample_customer_data['id']
        updates = {'name': 'Updated Name'}
        
        # Mock successful update
        updated_data = {**sample_customer_data, **updates}
        supabase_service.client.table.return_value.update.return_value.eq.return_value.execute.return_value = Mock(
            data=[updated_data], error=None
        )
        
        result = await supabase_service.update_customer(customer_id, updates)
        
        assert result is not None
        assert result['name'] == 'Updated Name'

    @pytest.mark.asyncio
    async def test_create_conversation(self, supabase_service, sample_conversation_data):
        """Test creating a conversation record."""
        # Mock successful insert
        supabase_service.client.table.return_value.insert.return_value.execute.return_value = Mock(
            data=[sample_conversation_data], error=None
        )
        
        result = await supabase_service.create_conversation(sample_conversation_data)
        
        assert result is not None
        assert result['id'] == sample_conversation_data['id']

    @pytest.mark.asyncio
    async def test_database_error_handling(self, supabase_service):
        """Test database error handling."""
        # Mock database error
        supabase_service.client.table.return_value.insert.return_value.execute.return_value = Mock(
            data=None, error=Mock(message="Database connection failed")
        )
        
        with pytest.raises(Exception):
            await supabase_service.create_customer({'invalid': 'data'})


class TestMCPService:
    """Test cases for MCPService."""

    @pytest.fixture
    def mcp_service(self, mock_mcp_client):
        """Create MCPService instance for testing."""
        with patch('my_adk_agent.services.mcp_service.MCPClient', return_value=mock_mcp_client):
            return MCPService()

    @pytest.mark.asyncio
    async def test_list_available_tools(self, mcp_service):
        """Test listing available MCP tools."""
        mock_tools = [
            {'name': 'n8n_workflow_execute', 'description': 'Execute n8n workflow'},
            {'name': 'n8n_workflow_list', 'description': 'List n8n workflows'}
        ]
        
        mcp_service.client.list_tools.return_value = mock_tools
        
        tools = await mcp_service.list_available_tools()
        
        assert tools is not None
        assert len(tools) == 2
        assert tools[0]['name'] == 'n8n_workflow_execute'

    @pytest.mark.asyncio
    async def test_execute_n8n_workflow(self, mcp_service, sample_workflow_data):
        """Test executing n8n workflow via MCP."""
        workflow_id = sample_workflow_data['id']
        workflow_data = {'customer_id': 'test-123'}
        
        # Mock successful workflow execution
        mcp_service.client.call_tool.return_value = {
            'result': 'success',
            'execution_id': 'exec-123'
        }
        
        result = await mcp_service.execute_n8n_workflow(workflow_id, workflow_data)
        
        assert result is not None
        assert result['result'] == 'success'
        mcp_service.client.call_tool.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_workflow_status(self, mcp_service):
        """Test getting workflow execution status."""
        execution_id = 'exec-123'
        
        # Mock workflow status response
        mcp_service.client.call_tool.return_value = {
            'status': 'completed',
            'result': {'success': True}
        }
        
        status = await mcp_service.get_workflow_status(execution_id)
        
        assert status is not None
        assert status['status'] == 'completed'

    @pytest.mark.asyncio
    async def test_mcp_connection_error(self, mcp_service):
        """Test MCP connection error handling."""
        # Mock connection error
        mcp_service.client.call_tool.side_effect = ConnectionError("MCP server unavailable")
        
        with pytest.raises(ConnectionError):
            await mcp_service.execute_n8n_workflow('workflow-123', {})

    @pytest.mark.asyncio
    async def test_validate_workflow_data(self, mcp_service):
        """Test workflow data validation."""
        valid_data = {
            'customer_id': 'test-123',
            'workflow_type': 'onboarding'
        }
        
        invalid_data = {
            'invalid_field': 'value'
        }
        
        assert mcp_service.validate_workflow_data(valid_data) is True
        assert mcp_service.validate_workflow_data(invalid_data) is False