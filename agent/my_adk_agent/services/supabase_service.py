"""Supabase service for database operations."""

import os
import logging
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
import asyncio

logger = logging.getLogger(__name__)


class SupabaseService:
    """Service for Supabase database operations."""
    
    def __init__(self):
        """Initialize Supabase service."""
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_ANON_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not self.url or not self.key:
            logger.warning("Supabase configuration missing")
            self.client = None
        else:
            self.client: Client = create_client(self.url, self.key)
    
    async def health_check(self) -> bool:
        """Check if Supabase connection is healthy."""
        if not self.client:
            return False
        
        try:
            # Simple query to test connection
            result = self.client.table('health_check').select('*').limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase health check failed: {e}")
            return False
    
    async def create_customer(self, customer_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new customer record."""
        if not self.client:
            raise ValueError("Supabase client not initialized")
        
        try:
            result = self.client.table('customers').insert(customer_data).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            raise
    
    async def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get customer by ID."""
        if not self.client:
            raise ValueError("Supabase client not initialized")
        
        try:
            result = self.client.table('customers').select('*').eq('id', customer_id).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting customer: {e}")
            raise
    
    async def update_customer(self, customer_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update customer record."""
        if not self.client:
            raise ValueError("Supabase client not initialized")
        
        try:
            result = self.client.table('customers').update(updates).eq('id', customer_id).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error updating customer: {e}")
            raise
    
    async def create_conversation(self, conversation_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new conversation record."""
        if not self.client:
            raise ValueError("Supabase client not initialized")
        
        try:
            result = self.client.table('conversations').insert(conversation_data).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            raise
    
    async def create_deployment_record(self, deployment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a deployment record."""
        if not self.client:
            raise ValueError("Supabase client not initialized")
        
        try:
            result = self.client.table('deployments').insert(deployment_data).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error creating deployment record: {e}")
            raise
    
    async def update_deployment_record(self, deployment_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update deployment record."""
        if not self.client:
            raise ValueError("Supabase client not initialized")
        
        try:
            result = self.client.table('deployments').update(updates).eq('id', deployment_id).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error updating deployment record: {e}")
            raise
    
    async def get_deployment_record(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Get deployment record by ID."""
        if not self.client:
            raise ValueError("Supabase client not initialized")
        
        try:
            result = self.client.table('deployments').select('*').eq('id', deployment_id).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting deployment record: {e}")
            raise
    
    async def store_metrics(self, metrics_data: List[Dict[str, Any]]) -> bool:
        """Store metrics data."""
        if not self.client:
            raise ValueError("Supabase client not initialized")
        
        try:
            result = self.client.table('metrics').insert(metrics_data).execute()
            return len(result.data) > 0 if result.data else False
        except Exception as e:
            logger.error(f"Error storing metrics: {e}")
            return False