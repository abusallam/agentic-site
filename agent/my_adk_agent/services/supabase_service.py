"""Supabase service for database operations."""

import os
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)


class SupabaseService:
    """Service for interacting with Supabase database."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        self.key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
        
        if not self.url or not self.key:
            logger.warning("Supabase credentials not found, using mock mode")
            self.client = None
        else:
            self.client: Client = create_client(self.url, self.key)
    
    async def create_customer_record(self, customer_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new customer record."""
        if not self.client:
            logger.info("Mock: Creating customer record")
            return {"id": "mock-customer-id", **customer_data}
        
        try:
            result = self.client.table("customers").insert(customer_data).execute()
            logger.info(f"Created customer record: {result.data[0]['id']}")
            return result.data[0]
        except Exception as e:
            logger.error(f"Failed to create customer record: {e}")
            return None
    
    async def get_customer_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get customer by email address."""
        if not self.client:
            logger.info(f"Mock: Getting customer by email {email}")
            return {"id": "mock-customer-id", "email": email}
        
        try:
            result = self.client.table("customers").select("*").eq("email", email).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to get customer by email: {e}")
            return None
    
    async def update_customer_requirements(self, customer_id: str, requirements: Dict[str, Any]) -> bool:
        """Update customer requirements."""
        if not self.client:
            logger.info(f"Mock: Updating requirements for customer {customer_id}")
            return True
        
        try:
            result = self.client.table("customers").update({
                "requirements": requirements,
                "updated_at": "now()"
            }).eq("id", customer_id).execute()
            logger.info(f"Updated requirements for customer {customer_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update customer requirements: {e}")
            return False
    
    async def create_workflow_record(self, workflow_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a workflow record."""
        if not self.client:
            logger.info("Mock: Creating workflow record")
            return {"id": "mock-workflow-id", **workflow_data}
        
        try:
            result = self.client.table("workflows").insert(workflow_data).execute()
            logger.info(f"Created workflow record: {result.data[0]['id']}")
            return result.data[0]
        except Exception as e:
            logger.error(f"Failed to create workflow record: {e}")
            return None
    
    async def update_workflow_status(self, workflow_id: str, status: str, details: Optional[Dict[str, Any]] = None) -> bool:
        """Update workflow status."""
        if not self.client:
            logger.info(f"Mock: Updating workflow {workflow_id} status to {status}")
            return True
        
        try:
            update_data = {
                "status": status,
                "updated_at": "now()"
            }
            if details:
                update_data["details"] = details
            
            result = self.client.table("workflows").update(update_data).eq("id", workflow_id).execute()
            logger.info(f"Updated workflow {workflow_id} status to {status}")
            return True
        except Exception as e:
            logger.error(f"Failed to update workflow status: {e}")
            return False
    
    async def get_customer_workflows(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get all workflows for a customer."""
        if not self.client:
            logger.info(f"Mock: Getting workflows for customer {customer_id}")
            return [{"id": "mock-workflow-id", "customer_id": customer_id, "status": "active"}]
        
        try:
            result = self.client.table("workflows").select("*").eq("customer_id", customer_id).execute()
            return result.data
        except Exception as e:
            logger.error(f"Failed to get customer workflows: {e}")
            return []