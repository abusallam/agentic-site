"""Integration tests for Supabase service."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from my_adk_agent.services.supabase_service import SupabaseService


@pytest.mark.integration
class TestSupabaseIntegration:
    """Integration tests for Supabase service."""

    @pytest.fixture
    def supabase_service(self, mock_supabase_client):
        """Create SupabaseService with mocked client."""
        with patch('my_adk_agent.services.supabase_service.create_client') as mock_create:
            mock_create.return_value = mock_supabase_client
            service = SupabaseService()
            yield service

    @pytest.mark.asyncio
    async def test_health_check_success(self, supabase_service, mock_supabase_client):
        """Test successful health check."""
        mock_supabase_client.table.return_value.select.return_value.limit.return_value.execute.return_value = Mock(
            data=[{"status": "ok"}], error=None
        )
        
        result = await supabase_service.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, supabase_service, mock_supabase_client):
        """Test health check failure."""
        mock_supabase_client.table.return_value.select.return_value.limit.return_value.execute.side_effect = Exception("Connection failed")
        
        result = await supabase_service.health_check()
        assert result is False

    @pytest.mark.asyncio
    async def test_create_customer_success(self, supabase_service, mock_supabase_client, sample_customer_data):
        """Test successful customer creation."""
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = Mock(
            data=[sample_customer_data], error=None
        )
        
        result = await supabase_service.create_customer(sample_customer_data)
        assert result == sample_customer_data
        
        # Verify correct table and method calls
        mock_supabase_client.table.assert_called_with('customers')
        mock_supabase_client.table.return_value.insert.assert_called_with(sample_customer_data)

    @pytest.mark.asyncio
    async def test_create_customer_failure(self, supabase_service, mock_supabase_client, sample_customer_data):
        """Test customer creation failure."""
        mock_supabase_client.table.return_value.insert.return_value.execute.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            await supabase_service.create_customer(sample_customer_data)

    @pytest.mark.asyncio
    async def test_get_customer_success(self, supabase_service, mock_supabase_client, sample_customer_data):
        """Test successful customer retrieval."""
        customer_id = sample_customer_data["id"]
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[sample_customer_data], error=None
        )
        
        result = await supabase_service.get_customer(customer_id)
        assert result == sample_customer_data
        
        # Verify correct query
        mock_supabase_client.table.return_value.select.return_value.eq.assert_called_with('id', customer_id)

    @pytest.mark.asyncio
    async def test_get_customer_not_found(self, supabase_service, mock_supabase_client):
        """Test customer not found."""
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[], error=None
        )
        
        result = await supabase_service.get_customer("nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_update_customer_success(self, supabase_service, mock_supabase_client, sample_customer_data):
        """Test successful customer update."""
        customer_id = sample_customer_data["id"]
        updates = {"name": "Updated Name", "phone": "+9876543210"}
        updated_data = {**sample_customer_data, **updates}
        
        mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value = Mock(
            data=[updated_data], error=None
        )
        
        result = await supabase_service.update_customer(customer_id, updates)
        assert result == updated_data
        
        # Verify correct update call
        mock_supabase_client.table.return_value.update.assert_called_with(updates)
        mock_supabase_client.table.return_value.update.return_value.eq.assert_called_with('id', customer_id)

    @pytest.mark.asyncio
    async def test_create_conversation_success(self, supabase_service, mock_supabase_client, sample_conversation_data):
        """Test successful conversation creation."""
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = Mock(
            data=[sample_conversation_data], error=None
        )
        
        result = await supabase_service.create_conversation(sample_conversation_data)
        assert result == sample_conversation_data
        
        # Verify correct table
        mock_supabase_client.table.assert_called_with('conversations')

    @pytest.mark.asyncio
    async def test_create_deployment_record_success(self, supabase_service, mock_supabase_client):
        """Test successful deployment record creation."""
        deployment_data = {
            "id": "deploy-123",
            "commit_sha": "abc123",
            "branch": "main",
            "environment": "production",
            "status": "success",
            "started_at": "2024-01-01T00:00:00Z",
            "completed_at": "2024-01-01T00:05:00Z"
        }
        
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = Mock(
            data=[deployment_data], error=None
        )
        
        result = await supabase_service.create_deployment_record(deployment_data)
        assert result == deployment_data
        
        # Verify correct table
        mock_supabase_client.table.assert_called_with('deployments')

    @pytest.mark.asyncio
    async def test_store_metrics_success(self, supabase_service, mock_supabase_client):
        """Test successful metrics storage."""
        metrics_data = [
            {"metric": "response_time", "value": 150, "timestamp": "2024-01-01T00:00:00Z"},
            {"metric": "error_rate", "value": 0.01, "timestamp": "2024-01-01T00:00:00Z"}
        ]
        
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = Mock(
            data=metrics_data, error=None
        )
        
        result = await supabase_service.store_metrics(metrics_data)
        assert result is True
        
        # Verify correct table and data
        mock_supabase_client.table.assert_called_with('metrics')
        mock_supabase_client.table.return_value.insert.assert_called_with(metrics_data)

    @pytest.mark.asyncio
    async def test_store_metrics_failure(self, supabase_service, mock_supabase_client):
        """Test metrics storage failure."""
        metrics_data = [{"metric": "test", "value": 1}]
        
        mock_supabase_client.table.return_value.insert.return_value.execute.side_effect = Exception("Storage error")
        
        result = await supabase_service.store_metrics(metrics_data)
        assert result is False

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, supabase_service, mock_supabase_client, sample_customer_data):
        """Test concurrent database operations."""
        # Mock successful responses
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = Mock(
            data=[sample_customer_data], error=None
        )
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[sample_customer_data], error=None
        )
        
        # Create multiple concurrent operations
        tasks = [
            supabase_service.create_customer({**sample_customer_data, "id": f"customer-{i}"})
            for i in range(5)
        ]
        tasks.extend([
            supabase_service.get_customer(f"customer-{i}")
            for i in range(5)
        ])
        
        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all operations completed successfully
        assert len(results) == 10
        assert all(not isinstance(r, Exception) for r in results)

    @pytest.mark.asyncio
    async def test_service_without_client(self):
        """Test service behavior when client is not initialized."""
        with patch.dict('os.environ', {}, clear=True):
            service = SupabaseService()
            
            # Should handle gracefully when client is None
            result = await service.health_check()
            assert result is False
            
            with pytest.raises(ValueError, match="Supabase client not initialized"):
                await service.create_customer({"test": "data"})

    @pytest.mark.asyncio
    async def test_error_handling_and_logging(self, supabase_service, mock_supabase_client, caplog):
        """Test error handling and logging."""
        mock_supabase_client.table.return_value.select.return_value.limit.return_value.execute.side_effect = Exception("Test error")
        
        result = await supabase_service.health_check()
        assert result is False
        
        # Verify error was logged
        assert "Supabase health check failed" in caplog.text