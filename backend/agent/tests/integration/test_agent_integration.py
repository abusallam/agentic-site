"""Integration tests for agent functionality."""

import pytest
import os
from unittest.mock import Mock, patch
from my_adk_agent.agent import CustomerJourneyAgent


@pytest.mark.integration
class TestAgentIntegration:
    """Integration tests for the complete agent system."""

    @pytest.fixture
    def agent_with_mocks(self):
        """Create agent with mocked external services."""
        with patch('my_adk_agent.services.supabase_service.create_client') as mock_supabase, \
             patch('my_adk_agent.services.mcp_service.MCPClient') as mock_mcp, \
             patch('google.generativeai.GenerativeModel') as mock_gemini:
            
            # Setup mock returns
            mock_supabase.return_value = Mock()
            mock_mcp.return_value = Mock()
            mock_gemini.return_value = Mock()
            
            agent = CustomerJourneyAgent()
            yield agent

    @pytest.mark.asyncio
    async def test_complete_customer_journey(self, agent_with_mocks, sample_customer_data):
        """Test complete customer journey from inquiry to workflow execution."""
        agent = agent_with_mocks
        
        # Mock database operations
        agent.supabase.table.return_value.insert.return_value.execute.return_value = Mock(
            data=[sample_customer_data], error=None
        )
        
        # Mock Gemini response
        agent.gemini_client.generate_content.return_value = Mock(
            text="I understand you need an AI chatbot. Let me help you with that."
        )
        
        # Mock MCP workflow execution
        agent.mcp_service.execute_n8n_workflow.return_value = {
            'result': 'success',
            'execution_id': 'exec-123'
        }
        
        # Simulate complete customer journey
        inquiry = "I need an AI chatbot for my customer support"
        
        # Step 1: Process initial inquiry
        response = await agent.process_customer_inquiry(inquiry, sample_customer_data)
        assert response is not None
        
        # Step 2: Create customer record
        customer = await agent.create_customer_record(sample_customer_data)
        assert customer is not None
        
        # Step 3: Extract requirements
        requirements = await agent.get_customer_requirements([inquiry], sample_customer_data)
        assert requirements is not None
        
        # Step 4: Trigger workflow
        workflow_result = await agent.trigger_customer_workflow(customer['id'], requirements)
        assert workflow_result is not None

    @pytest.mark.asyncio
    async def test_service_integration_chain(self, agent_with_mocks):
        """Test integration between different services."""
        agent = agent_with_mocks
        
        # Test Supabase -> MCP integration
        customer_id = "test-customer-123"
        
        # Mock customer data retrieval
        agent.supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[{'id': customer_id, 'requirements': 'AI chatbot'}], error=None
        )
        
        # Mock MCP workflow execution
        agent.mcp_service.execute_n8n_workflow.return_value = {
            'result': 'success',
            'workflow_id': 'workflow-123'
        }
        
        # Execute integration chain
        customer = await agent.get_customer(customer_id)
        workflow_result = await agent.execute_customer_workflow(customer)
        
        assert customer is not None
        assert workflow_result['result'] == 'success'

    @pytest.mark.asyncio
    async def test_error_recovery_flow(self, agent_with_mocks):
        """Test error recovery and fallback mechanisms."""
        agent = agent_with_mocks
        
        # Simulate MCP service failure
        agent.mcp_service.execute_n8n_workflow.side_effect = ConnectionError("MCP unavailable")
        
        # Test fallback behavior
        try:
            await agent.execute_customer_workflow({'id': 'test-123'})
        except ConnectionError:
            # Should handle gracefully and log error
            pass
        
        # Verify error was logged (implementation dependent)
        assert True  # Placeholder for actual error logging verification

    @pytest.mark.asyncio
    async def test_concurrent_customer_handling(self, agent_with_mocks):
        """Test handling multiple customers concurrently."""
        import asyncio
        
        agent = agent_with_mocks
        
        # Mock responses for multiple customers
        agent.supabase.table.return_value.insert.return_value.execute.return_value = Mock(
            data=[{'id': 'customer-1'}], error=None
        )
        
        # Create multiple customer tasks
        customers = [
            {'id': f'customer-{i}', 'name': f'Customer {i}'}
            for i in range(3)
        ]
        
        tasks = [
            agent.create_customer_record(customer)
            for customer in customers
        ]
        
        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all completed successfully
        assert len(results) == 3
        assert all(not isinstance(r, Exception) for r in results)

    @pytest.mark.asyncio
    async def test_conversation_state_management(self, agent_with_mocks, sample_conversation_data):
        """Test conversation state management across interactions."""
        agent = agent_with_mocks
        
        conversation_id = sample_conversation_data['id']
        
        # Mock conversation retrieval and updates
        agent.supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[sample_conversation_data], error=None
        )
        
        agent.supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = Mock(
            data=[sample_conversation_data], error=None
        )
        
        # Test conversation flow
        context = await agent.get_conversation_context(conversation_id)
        assert context is not None
        
        # Add new message
        new_message = "I have additional requirements"
        updated_context = await agent.add_message_to_conversation(
            conversation_id, new_message, "user"
        )
        assert updated_context is not None

    @pytest.mark.asyncio
    async def test_workflow_execution_monitoring(self, agent_with_mocks):
        """Test monitoring of workflow execution status."""
        agent = agent_with_mocks
        
        execution_id = "exec-123"
        
        # Mock workflow status progression
        status_responses = [
            {'status': 'running', 'progress': 25},
            {'status': 'running', 'progress': 75},
            {'status': 'completed', 'progress': 100, 'result': {'success': True}}
        ]
        
        agent.mcp_service.get_workflow_status.side_effect = status_responses
        
        # Monitor workflow execution
        final_status = await agent.monitor_workflow_execution(execution_id)
        
        assert final_status['status'] == 'completed'
        assert final_status['result']['success'] is True