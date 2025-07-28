"""Integration tests for MCP service."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import httpx
from my_adk_agent.services.mcp_service import MCPService


@pytest.mark.integration
class TestMCPIntegration:
    """Integration tests for MCP service."""

    @pytest.fixture
    def mcp_service(self):
        """Create MCPService instance."""
        return MCPService()

    @pytest.mark.asyncio
    async def test_health_check_success(self, mcp_service):
        """Test successful MCP health check."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await mcp_service.health_check()
            assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, mcp_service):
        """Test MCP health check failure."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.ConnectError("Connection failed")
            )
            
            result = await mcp_service.health_check()
            assert result is False

    @pytest.mark.asyncio
    async def test_list_available_tools_success(self, mcp_service):
        """Test successful tool listing."""
        expected_tools = [
            {"name": "n8n_workflow_execute", "description": "Execute n8n workflow"},
            {"name": "n8n_workflow_status", "description": "Get workflow status"}
        ]
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"tools": expected_tools}
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await mcp_service.list_available_tools()
            assert result == expected_tools

    @pytest.mark.asyncio
    async def test_list_available_tools_failure(self, mcp_service):
        """Test tool listing failure."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await mcp_service.list_available_tools()
            assert result is None

    @pytest.mark.asyncio
    async def test_call_tool_success(self, mcp_service):
        """Test successful tool call."""
        tool_name = "n8n_workflow_execute"
        parameters = {"workflow_id": "test-workflow", "data": {"key": "value"}}
        expected_result = {"execution_id": "exec-123", "status": "started"}
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_result
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            result = await mcp_service.call_tool(tool_name, parameters)
            assert result == expected_result
            
            # Verify correct API call
            mock_client.return_value.__aenter__.return_value.post.assert_called_once_with(
                f"{mcp_service.server_url}/tools/{tool_name}",
                json={"parameters": parameters},
                timeout=mcp_service.timeout
            )

    @pytest.mark.asyncio
    async def test_call_tool_failure(self, mcp_service):
        """Test tool call failure."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            result = await mcp_service.call_tool("invalid_tool", {})
            assert result is None

    @pytest.mark.asyncio
    async def test_execute_n8n_workflow_via_mcp(self, mcp_service):
        """Test n8n workflow execution via MCP."""
        workflow_id = "customer-onboarding"
        parameters = {"customer_id": "cust-123", "data": {"name": "Test Customer"}}
        expected_result = {"execution_id": "exec-456", "status": "running"}
        
        with patch.object(mcp_service, 'call_tool') as mock_call_tool:
            mock_call_tool.return_value = expected_result
            
            result = await mcp_service.execute_n8n_workflow(workflow_id, parameters)
            assert result == expected_result
            
            # Verify MCP tool was called correctly
            mock_call_tool.assert_called_once_with("n8n_workflow_execute", {
                "workflow_id": workflow_id,
                "parameters": parameters
            })

    @pytest.mark.asyncio
    async def test_execute_n8n_workflow_direct_fallback(self, mcp_service):
        """Test n8n workflow execution with direct API fallback."""
        workflow_id = "customer-onboarding"
        parameters = {"customer_id": "cust-123"}
        expected_result = {"execution_id": "exec-789", "status": "completed"}
        
        with patch.object(mcp_service, 'call_tool') as mock_call_tool, \
             patch.object(mcp_service, '_execute_n8n_workflow_direct') as mock_direct:
            
            # MCP call fails, should fallback to direct
            mock_call_tool.return_value = None
            mock_direct.return_value = expected_result
            
            result = await mcp_service.execute_n8n_workflow(workflow_id, parameters)
            assert result == expected_result
            
            # Verify fallback was used
            mock_direct.assert_called_once_with(workflow_id, parameters)

    @pytest.mark.asyncio
    async def test_direct_n8n_workflow_execution(self, mcp_service):
        """Test direct n8n workflow execution."""
        workflow_id = "test-workflow"
        parameters = {"test": "data"}
        expected_result = {"success": True, "execution_id": "direct-123"}
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_result
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            result = await mcp_service._execute_n8n_workflow_direct(workflow_id, parameters)
            assert result == expected_result
            
            # Verify correct n8n API call
            expected_url = f"{mcp_service.n8n_url}/api/v1/workflows/{workflow_id}/execute"
            mock_client.return_value.__aenter__.return_value.post.assert_called_once_with(
                expected_url,
                json={"parameters": parameters},
                headers={"Content-Type": "application/json"},
                timeout=mcp_service.timeout
            )

    @pytest.mark.asyncio
    async def test_direct_n8n_workflow_with_auth(self, mcp_service):
        """Test direct n8n workflow execution with authentication."""
        mcp_service.n8n_api_key = "test-api-key"
        workflow_id = "auth-workflow"
        parameters = {"auth": "test"}
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True}
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            await mcp_service._execute_n8n_workflow_direct(workflow_id, parameters)
            
            # Verify auth header was included
            expected_headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer test-api-key"
            }
            mock_client.return_value.__aenter__.return_value.post.assert_called_once_with(
                f"{mcp_service.n8n_url}/api/v1/workflows/{workflow_id}/execute",
                json={"parameters": parameters},
                headers=expected_headers,
                timeout=mcp_service.timeout
            )

    @pytest.mark.asyncio
    async def test_get_workflow_status_via_mcp(self, mcp_service):
        """Test workflow status retrieval via MCP."""
        execution_id = "exec-123"
        expected_status = {"status": "completed", "result": {"success": True}}
        
        with patch.object(mcp_service, 'call_tool') as mock_call_tool:
            mock_call_tool.return_value = expected_status
            
            result = await mcp_service.get_workflow_status(execution_id)
            assert result == expected_status
            
            mock_call_tool.assert_called_once_with("n8n_workflow_status", {
                "execution_id": execution_id
            })

    @pytest.mark.asyncio
    async def test_get_workflow_status_direct_fallback(self, mcp_service):
        """Test workflow status with direct API fallback."""
        execution_id = "exec-456"
        expected_status = {"status": "running", "progress": 50}
        
        with patch.object(mcp_service, 'call_tool') as mock_call_tool, \
             patch.object(mcp_service, '_get_workflow_status_direct') as mock_direct:
            
            mock_call_tool.return_value = None
            mock_direct.return_value = expected_status
            
            result = await mcp_service.get_workflow_status(execution_id)
            assert result == expected_status

    @pytest.mark.asyncio
    async def test_list_n8n_workflows_success(self, mcp_service):
        """Test successful n8n workflow listing."""
        expected_workflows = [
            {"id": "workflow-1", "name": "Customer Onboarding"},
            {"id": "workflow-2", "name": "Order Processing"}
        ]
        
        with patch.object(mcp_service, 'call_tool') as mock_call_tool:
            mock_call_tool.return_value = {"workflows": expected_workflows}
            
            result = await mcp_service.list_n8n_workflows()
            assert result == expected_workflows

    @pytest.mark.asyncio
    async def test_list_n8n_workflows_direct_fallback(self, mcp_service):
        """Test n8n workflow listing with direct API fallback."""
        expected_workflows = [{"id": "workflow-3", "name": "Direct Workflow"}]
        
        with patch.object(mcp_service, 'call_tool') as mock_call_tool, \
             patch.object(mcp_service, '_list_n8n_workflows_direct') as mock_direct:
            
            mock_call_tool.return_value = None
            mock_direct.return_value = expected_workflows
            
            result = await mcp_service.list_n8n_workflows()
            assert result == expected_workflows

    @pytest.mark.asyncio
    async def test_validate_workflow_data_success(self, mcp_service):
        """Test successful workflow data validation."""
        valid_data = {
            "customer_id": "cust-123",
            "workflow_type": "onboarding",
            "additional_data": "test"
        }
        
        result = mcp_service.validate_workflow_data(valid_data)
        assert result is True

    @pytest.mark.asyncio
    async def test_validate_workflow_data_failure(self, mcp_service):
        """Test workflow data validation failure."""
        invalid_data = {
            "customer_id": "cust-123",
            # Missing workflow_type
            "additional_data": "test"
        }
        
        result = mcp_service.validate_workflow_data(invalid_data)
        assert result is False

    @pytest.mark.asyncio
    async def test_concurrent_workflow_executions(self, mcp_service):
        """Test concurrent workflow executions."""
        workflows = [
            ("workflow-1", {"customer_id": f"cust-{i}"})
            for i in range(3)
        ]
        
        with patch.object(mcp_service, 'call_tool') as mock_call_tool:
            mock_call_tool.return_value = {"execution_id": "exec-123", "status": "started"}
            
            tasks = [
                mcp_service.execute_n8n_workflow(workflow_id, params)
                for workflow_id, params in workflows
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verify all executions completed successfully
            assert len(results) == 3
            assert all(not isinstance(r, Exception) for r in results)
            assert all(r["status"] == "started" for r in results)

    @pytest.mark.asyncio
    async def test_timeout_handling(self, mcp_service):
        """Test timeout handling in MCP calls."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.TimeoutException("Request timed out")
            )
            
            result = await mcp_service.call_tool("slow_tool", {})
            assert result is None

    @pytest.mark.asyncio
    async def test_error_handling_and_logging(self, mcp_service, caplog):
        """Test error handling and logging."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=Exception("Unexpected error")
            )
            
            result = await mcp_service.health_check()
            assert result is False
            
            # Verify error was logged
            assert "MCP health check failed" in caplog.text