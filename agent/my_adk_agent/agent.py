"""Main ADK agent implementation for customer journey orchestration."""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio

# Import services
from .services.supabase_service import SupabaseService
from .services.mcp_service import MCPService
from .services.monitoring_service import MonitoringService
from .services.cicd_service import CICDService

logger = logging.getLogger(__name__)


class CustomerJourneyAgent:
    """Main agent for customer journey orchestration."""
    
    def __init__(self):
        """Initialize the customer journey agent."""
        self.supabase_service = SupabaseService()
        self.mcp_service = MCPService()
        self.monitoring_service = MonitoringService(self.supabase_service)
        self.cicd_service = CICDService(self.mcp_service, self.supabase_service)
        
        # Initialize Gemini client
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_client = None
        
        if self.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_client = genai.GenerativeModel('gemini-pro')
            except ImportError:
                logger.warning("Google Generative AI not available")
        
        logger.info("CustomerJourneyAgent initialized")
    
    async def process_customer_inquiry(self, inquiry: str, customer_data: Dict[str, Any]) -> str:
        """Process customer inquiry and generate response."""
        try:
            await self.monitoring_service.increment_counter("agent_requests_total")
            start_time = datetime.now()
            
            if self.gemini_client:
                # Use Gemini for response generation
                prompt = f"""
                You are an AI consultant helping customers with their AI and automation needs.
                
                Customer inquiry: {inquiry}
                Customer context: {customer_data}
                
                Provide a helpful, professional response that addresses their needs and guides them toward appropriate solutions.
                """
                
                response = self.gemini_client.generate_content(prompt)
                result = response.text
            else:
                # Fallback response
                result = f"Thank you for your inquiry: '{inquiry}'. Our team will review your requirements and get back to you soon."
            
            # Record response time
            duration = (datetime.now() - start_time).total_seconds()
            await self.monitoring_service.record_duration("agent_response_time", duration)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing customer inquiry: {e}")
            await self.monitoring_service.increment_counter("agent_workflow_failures_total")
            raise
    
    async def create_customer_record(self, customer_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new customer record."""
        try:
            if not self.validate_customer_data(customer_data):
                raise ValueError("Invalid customer data")
            
            # Add timestamp
            customer_data["created_at"] = datetime.now().isoformat()
            
            # Create customer record
            customer = await self.supabase_service.create_customer(customer_data)
            
            if customer:
                logger.info(f"Created customer record: {customer['id']}")
                
                # Trigger customer onboarding workflow
                await self.trigger_customer_workflow(customer['id'], {
                    "type": "onboarding",
                    "customer_data": customer_data
                })
            
            return customer
            
        except Exception as e:
            logger.error(f"Error creating customer record: {e}")
            raise
    
    async def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get customer by ID."""
        try:
            return await self.supabase_service.get_customer(customer_id)
        except Exception as e:
            logger.error(f"Error getting customer {customer_id}: {e}")
            raise
    
    async def get_customer_requirements(self, conversation_history: List[str], customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract customer requirements from conversation."""
        try:
            if self.gemini_client:
                prompt = f"""
                Analyze the following conversation and customer data to extract key requirements:
                
                Conversation: {conversation_history}
                Customer Data: {customer_data}
                
                Extract and return the following information in JSON format:
                - budget: estimated budget range
                - timeline: project timeline
                - requirements: list of specific requirements
                - priority: high/medium/low
                - services_needed: list of services they need
                """
                
                response = self.gemini_client.generate_content(prompt)
                
                # Parse response (simplified - would need proper JSON parsing)
                return {
                    "budget": customer_data.get("budget", "unknown"),
                    "timeline": customer_data.get("timeline", "unknown"),
                    "requirements": customer_data.get("requirements", ""),
                    "priority": "medium",
                    "services_needed": ["ai_chatbot"]
                }
            else:
                # Fallback extraction
                return {
                    "budget": customer_data.get("budget", "unknown"),
                    "timeline": customer_data.get("timeline", "unknown"),
                    "requirements": " ".join(conversation_history),
                    "priority": "medium",
                    "services_needed": ["consultation"]
                }
                
        except Exception as e:
            logger.error(f"Error extracting requirements: {e}")
            return {}
    
    async def trigger_customer_workflow(self, customer_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger customer-specific workflow."""
        try:
            await self.monitoring_service.increment_counter("agent_workflow_executions_total")
            
            # Execute workflow via MCP
            result = await self.mcp_service.execute_n8n_workflow(
                "customer-onboarding",
                {
                    "customer_id": customer_id,
                    **workflow_data
                }
            )
            
            logger.info(f"Triggered workflow for customer {customer_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error triggering workflow for customer {customer_id}: {e}")
            await self.monitoring_service.increment_counter("agent_workflow_failures_total")
            raise
    
    async def execute_customer_workflow(self, customer: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow for a customer."""
        try:
            workflow_data = {
                "customer_id": customer["id"],
                "customer_data": customer,
                "timestamp": datetime.now().isoformat()
            }
            
            return await self.trigger_customer_workflow(customer["id"], workflow_data)
            
        except Exception as e:
            logger.error(f"Error executing customer workflow: {e}")
            raise
    
    async def get_conversation_context(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation context."""
        try:
            # This would typically fetch from conversations table
            # For now, return a mock context
            return {
                "id": conversation_id,
                "messages": [],
                "status": "active",
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            return None
    
    async def add_message_to_conversation(self, conversation_id: str, message: str, role: str) -> Optional[Dict[str, Any]]:
        """Add message to conversation."""
        try:
            # This would typically update the conversation in the database
            # For now, return a mock response
            return {
                "conversation_id": conversation_id,
                "message": message,
                "role": role,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error adding message to conversation: {e}")
            return None
    
    async def monitor_workflow_execution(self, execution_id: str) -> Dict[str, Any]:
        """Monitor workflow execution status."""
        try:
            max_attempts = 30
            attempt = 0
            
            while attempt < max_attempts:
                status = await self.mcp_service.get_workflow_status(execution_id)
                
                if status.get("status") in ["completed", "failed", "error"]:
                    return status
                
                await asyncio.sleep(10)  # Wait 10 seconds between checks
                attempt += 1
            
            return {"status": "timeout", "message": "Workflow monitoring timed out"}
            
        except Exception as e:
            logger.error(f"Error monitoring workflow execution: {e}")
            return {"status": "error", "error": str(e)}
    
    def validate_customer_data(self, data: Dict[str, Any]) -> bool:
        """Validate customer data."""
        required_fields = ["email", "name"]
        
        # Check required fields
        for field in required_fields:
            if field not in data or not data[field]:
                return False
        
        # Validate email format (basic)
        email = data["email"]
        if "@" not in email or "." not in email:
            return False
        
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform agent health check."""
        try:
            health_status = {
                "agent": "healthy",
                "services": {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Check Supabase
            supabase_healthy = await self.supabase_service.health_check()
            health_status["services"]["supabase"] = "healthy" if supabase_healthy else "unhealthy"
            
            # Check MCP
            mcp_healthy = await self.mcp_service.health_check()
            health_status["services"]["mcp"] = "healthy" if mcp_healthy else "unhealthy"
            
            # Check Gemini
            health_status["services"]["gemini"] = "configured" if self.gemini_client else "missing"
            
            return health_status
            
        except Exception as e:
            logger.error(f"Agent health check failed: {e}")
            return {
                "agent": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }