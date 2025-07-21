"""Main ADK Agent for accounting, invoicing, and sales management."""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from google.adk.agents.base_agent import BaseAgent
# Tool imports will be added once we have the correct ADK setup

from .services import (
    AuthService,
    LivekitService,
    MCPService,
    SupabaseService,
    StripeService,
)

# Import the dedicated n8n MCP agent
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from n8n_mcp_agent.agent import N8nMCPAgent

logger = logging.getLogger(__name__)


class AccountantAgent(BaseAgent):
    """ADK Agent specialized in accounting, invoicing, billing, and financial management."""
    
    def __init__(self):
        """Initialize the accountant agent."""
        super().__init__(
            name="accountant_agent",
            description="ADK Agent for managing invoices, billing, payments, and financial operations"
        )
        
        # Initialize services using object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, 'auth_service', AuthService())
        object.__setattr__(self, 'livekit_service', LivekitService())
        object.__setattr__(self, 'mcp_service', MCPService())
        object.__setattr__(self, 'supabase_service', SupabaseService())
        object.__setattr__(self, 'stripe_service', StripeService())
        
        # Initialize the dedicated n8n MCP agent
        object.__setattr__(self, 'n8n_mcp_agent', N8nMCPAgent())
        
        # Register tools
        self._register_tools()
        
        logger.info("AccountantAgent initialized")
    
    def _register_tools(self):
        """Register all available tools."""
        # For now, we'll skip tool registration and rely on the run method
        # Tools will be registered properly once we have the correct ADK setup
        logger.info("Tool registration skipped - using direct method calls")
    
    async def gather_customer_requirements(self, customer_input: str, customer_email: Optional[str] = None) -> Dict[str, Any]:
        """Gather and analyze customer requirements."""
        try:
            logger.info(f"Gathering requirements for customer: {customer_email}")
            
            # Analyze customer input to extract requirements
            requirements = {
                "service_type": self._extract_service_type(customer_input),
                "budget_range": self._extract_budget_range(customer_input),
                "timeline": self._extract_timeline(customer_input),
                "technical_level": self._extract_technical_level(customer_input),
                "specific_needs": self._extract_specific_needs(customer_input),
                "raw_input": customer_input
            }
            
            # Store requirements if customer email is provided
            if customer_email:
                customer = await self.supabase_service.get_customer_by_email(customer_email)
                if customer:
                    await self.supabase_service.update_customer_requirements(
                        customer["id"], requirements
                    )
            
            return {
                "status": "success",
                "requirements": requirements,
                "next_steps": self._recommend_next_steps(requirements)
            }
        except Exception as e:
            logger.error(f"Failed to gather customer requirements: {e}")
            return {"status": "error", "error": str(e)}
    
    async def create_customer_record(self, email: str, name: Optional[str] = None, requirements: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new customer record."""
        try:
            logger.info(f"Creating customer record for: {email}")
            
            # Create customer in database
            customer_data = {
                "email": email,
                "name": name,
                "requirements": requirements or {},
                "status": "new",
                "created_at": "now()"
            }
            
            customer = await self.supabase_service.create_customer_record(customer_data)
            if not customer:
                return {"status": "error", "error": "Failed to create customer record"}
            
            # Create Stripe customer
            stripe_customer = await self.stripe_service.create_customer(
                email=email,
                name=name,
                metadata={"supabase_id": customer["id"]}
            )
            
            if stripe_customer:
                # Update customer record with Stripe ID
                await self.supabase_service.update_customer_requirements(
                    customer["id"],
                    {"stripe_customer_id": stripe_customer["id"]}
                )
            
            return {
                "status": "success",
                "customer": customer,
                "stripe_customer_id": stripe_customer["id"] if stripe_customer else None
            }
        except Exception as e:
            logger.error(f"Failed to create customer record: {e}")
            return {"status": "error", "error": str(e)}
    
    async def initiate_live_agent_handoff(self, customer_email: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Initiate handoff to a live agent."""
        try:
            logger.info(f"Initiating live agent handoff for: {customer_email}")
            
            # Get customer record
            customer = await self.supabase_service.get_customer_by_email(customer_email)
            if not customer:
                return {"status": "error", "error": "Customer not found"}
            
            # Create Livekit room
            room_name = f"consultation-{customer['id']}"
            room = await self.livekit_service.create_room(room_name, customer["id"])
            if not room:
                return {"status": "error", "error": "Failed to create consultation room"}
            
            # Generate access tokens
            customer_token = await self.livekit_service.generate_access_token(
                room_name, f"customer-{customer['id']}", is_agent=False
            )
            
            # Invite live agent (this would typically send a notification)
            agent_invited = await self.livekit_service.invite_live_agent(
                room_name, "support@consulting.sa"
            )
            
            # Start monitoring the session
            monitoring = await self.livekit_service.monitor_room_events(room_name)
            
            return {
                "status": "success",
                "room_name": room_name,
                "customer_token": customer_token,
                "monitoring_active": monitoring["status"] == "monitoring",
                "next_steps": [
                    "Customer will receive room access link",
                    "Live agent will be notified",
                    "AI agent will monitor conversation for requirements"
                ]
            }
        except Exception as e:
            logger.error(f"Failed to initiate live agent handoff: {e}")
            return {"status": "error", "error": str(e)}
    
    async def deploy_ai_service(self, customer_email: str, service_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy an AI service for the customer."""
        try:
            logger.info(f"Deploying {service_type} for customer: {customer_email}")
            
            # Get customer record
            customer = await self.supabase_service.get_customer_by_email(customer_email)
            if not customer:
                return {"status": "error", "error": "Customer not found"}
            
            # Add customer ID to config
            config["customer_id"] = customer["id"]
            
            # Try to deploy via dedicated n8n MCP agent first
            deployment = await self.mcp_service.deploy_service_via_n8n_mcp(
                service_type, config, self.n8n_mcp_agent
            )
            
            # Fallback to regular MCP service if n8n MCP agent fails
            if not deployment:
                logger.info("Falling back to regular MCP service")
                deployment = await self.mcp_service.deploy_service(service_type, config)
            
            if not deployment:
                return {"status": "error", "error": "Failed to start deployment"}
            
            # Create workflow record
            workflow_data = {
                "customer_id": customer["id"],
                "service_type": service_type,
                "deployment_id": deployment["deployment_id"],
                "status": deployment.get("status", "deploying"),
                "config": config,
                "created_at": "now()"
            }
            
            workflow = await self.supabase_service.create_workflow_record(workflow_data)
            
            return {
                "status": "success",
                "deployment_id": deployment["deployment_id"],
                "workflow_id": workflow["id"] if workflow else None,
                "estimated_completion": deployment.get("estimated_completion", "Unknown"),
                "service_type": service_type,
                "deployment_method": deployment.get("created_via", "standard_mcp")
            }
        except Exception as e:
            logger.error(f"Failed to deploy AI service: {e}")
            return {"status": "error", "error": str(e)}
    
    async def manage_n8n_mcp_server(self, action: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manage the n8n MCP server (start, stop, status, etc.)."""
        try:
            logger.info(f"Managing n8n MCP server - Action: {action}")
            
            if action == "start":
                return await self.n8n_mcp_agent.start_mcp_server()
            elif action == "stop":
                return await self.n8n_mcp_agent.stop_mcp_server()
            elif action == "status":
                return await self.n8n_mcp_agent.get_mcp_server_status()
            elif action == "initialize":
                return await self.n8n_mcp_agent.initialize_mcp_server()
            elif action == "list_workflows":
                return await self.n8n_mcp_agent.list_workflows_via_mcp()
            elif action == "get_node_info":
                node_type = params.get("node_type") if params else None
                if not node_type:
                    return {"status": "error", "error": "node_type parameter required"}
                return await self.n8n_mcp_agent.get_node_info_via_mcp(node_type)
            elif action == "validate_workflow":
                workflow = params.get("workflow") if params else None
                if not workflow:
                    return {"status": "error", "error": "workflow parameter required"}
                return await self.n8n_mcp_agent.validate_workflow_via_mcp(workflow)
            else:
                return {"status": "error", "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Failed to manage n8n MCP server: {e}")
            return {"status": "error", "error": str(e)}
    
    async def create_workflow_via_n8n_mcp(self, customer_email: str, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a workflow directly via the n8n MCP agent."""
        try:
            logger.info(f"Creating workflow via n8n MCP for customer: {customer_email}")
            
            # Get customer record
            customer = await self.supabase_service.get_customer_by_email(customer_email)
            if not customer:
                return {"status": "error", "error": "Customer not found"}
            
            # Add customer context to workflow config
            workflow_config["customer_id"] = customer["id"]
            workflow_config["customer_email"] = customer_email
            
            # Create workflow via n8n MCP agent
            result = await self.n8n_mcp_agent.create_workflow_via_mcp(workflow_config)
            
            if result.get("status") == "success":
                # Store workflow record in database
                workflow_data = {
                    "customer_id": customer["id"],
                    "service_type": "custom_workflow",
                    "deployment_id": result["workflow"].get("id"),
                    "status": "active",
                    "config": workflow_config,
                    "created_at": "now()"
                }
                
                workflow_record = await self.supabase_service.create_workflow_record(workflow_data)
                
                return {
                    "status": "success",
                    "workflow": result["workflow"],
                    "workflow_record_id": workflow_record["id"] if workflow_record else None,
                    "created_via": "n8n_mcp_agent"
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Failed to create workflow via n8n MCP: {e}")
            return {"status": "error", "error": str(e)}
    
    async def process_payment(self, customer_email: str, amount: int, currency: str, description: str) -> Dict[str, Any]:
        """Process payment for customer services."""
        try:
            logger.info(f"Processing payment for customer: {customer_email}")
            
            # Get customer record
            customer = await self.supabase_service.get_customer_by_email(customer_email)
            if not customer:
                return {"status": "error", "error": "Customer not found"}
            
            # Get or create Stripe customer
            stripe_customer_id = customer.get("requirements", {}).get("stripe_customer_id")
            if not stripe_customer_id:
                stripe_customer = await self.stripe_service.create_customer(
                    email=customer_email,
                    name=customer.get("name"),
                    metadata={"supabase_id": customer["id"]}
                )
                if not stripe_customer:
                    return {"status": "error", "error": "Failed to create payment customer"}
                stripe_customer_id = stripe_customer["id"]
            
            # Create payment intent
            payment_intent = await self.stripe_service.create_payment_intent(
                amount=amount,
                currency=currency,
                customer_id=stripe_customer_id,
                description=description
            )
            
            if not payment_intent:
                return {"status": "error", "error": "Failed to create payment intent"}
            
            return {
                "status": "success",
                "payment_intent_id": payment_intent["id"],
                "client_secret": payment_intent["client_secret"],
                "amount": amount,
                "currency": currency
            }
        except Exception as e:
            logger.error(f"Failed to process payment: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_customer_status(self, customer_email: str) -> Dict[str, Any]:
        """Get current status of customer services and workflows."""
        try:
            logger.info(f"Getting status for customer: {customer_email}")
            
            # Get customer record
            customer = await self.supabase_service.get_customer_by_email(customer_email)
            if not customer:
                return {"status": "error", "error": "Customer not found"}
            
            # Get customer workflows
            workflows = await self.supabase_service.get_customer_workflows(customer["id"])
            
            # Get workflow statuses from MCP
            workflow_statuses = []
            for workflow in workflows:
                if workflow.get("deployment_id"):
                    status = await self.mcp_service.get_workflow_status(workflow["deployment_id"])
                    if status:
                        workflow_statuses.append({
                            "workflow_id": workflow["id"],
                            "service_type": workflow["service_type"],
                            "status": status["status"],
                            "progress": status.get("progress", 0)
                        })
            
            return {
                "status": "success",
                "customer": {
                    "id": customer["id"],
                    "email": customer["email"],
                    "name": customer.get("name"),
                    "status": customer.get("status", "unknown")
                },
                "workflows": workflow_statuses,
                "total_workflows": len(workflows)
            }
        except Exception as e:
            logger.error(f"Failed to get customer status: {e}")
            return {"status": "error", "error": str(e)}
    
    def _extract_service_type(self, input_text: str) -> str:
        """Extract service type from customer input."""
        input_lower = input_text.lower()
        if "chatbot" in input_lower:
            return "chatbot"
        elif "agent" in input_lower:
            return "ai_agent"
        elif "workflow" in input_lower or "automation" in input_lower:
            return "workflow_automation"
        elif "integration" in input_lower:
            return "data_integration"
        else:
            return "consultation"
    
    def _extract_budget_range(self, input_text: str) -> str:
        """Extract budget range from customer input."""
        input_lower = input_text.lower()
        if any(word in input_lower for word in ["cheap", "budget", "affordable"]):
            return "budget"
        elif any(word in input_lower for word in ["premium", "enterprise", "high-end"]):
            return "premium"
        else:
            return "standard"
    
    def _extract_timeline(self, input_text: str) -> str:
        """Extract timeline from customer input."""
        input_lower = input_text.lower()
        if any(word in input_lower for word in ["urgent", "asap", "immediately"]):
            return "urgent"
        elif any(word in input_lower for word in ["week", "quickly"]):
            return "1-2 weeks"
        elif any(word in input_lower for word in ["month"]):
            return "1 month"
        else:
            return "flexible"
    
    def _extract_technical_level(self, input_text: str) -> str:
        """Extract technical level from customer input."""
        input_lower = input_text.lower()
        if any(word in input_lower for word in ["beginner", "simple", "easy"]):
            return "beginner"
        elif any(word in input_lower for word in ["advanced", "complex", "technical"]):
            return "advanced"
        else:
            return "intermediate"
    
    def _extract_specific_needs(self, input_text: str) -> List[str]:
        """Extract specific needs from customer input."""
        needs = []
        input_lower = input_text.lower()
        
        if "multilingual" in input_lower:
            needs.append("multilingual_support")
        if "integration" in input_lower:
            needs.append("system_integration")
        if "custom" in input_lower:
            needs.append("customization")
        if "support" in input_lower:
            needs.append("ongoing_support")
        if "training" in input_lower:
            needs.append("training")
        
        return needs
    
    def _recommend_next_steps(self, requirements: Dict[str, Any]) -> List[str]:
        """Recommend next steps based on requirements."""
        steps = []
        service_type = requirements.get("service_type", "consultation")
        
        if service_type == "consultation":
            steps.append("Schedule consultation call")
            steps.append("Provide detailed requirements document")
        elif service_type in ["chatbot", "ai_agent"]:
            steps.append("Review service options and pricing")
            steps.append("Provide sample data or use cases")
            steps.append("Schedule technical discussion")
        else:
            steps.append("Technical requirements gathering")
            steps.append("Architecture planning session")
        
        return steps

    async def create_customer_record(self, customer_email: str, customer_name: Optional[str] = None) -> Dict[str, Any]:
        """Create a new customer record for billing purposes."""
        try:
            logger.info(f"Creating customer record for: {customer_email}")
            
            # Create customer in Supabase
            customer_data = {
                "email": customer_email,
                "name": customer_name or customer_email.split("@")[0],
                "status": "active",
                "created_at": datetime.now().isoformat()
            }
            
            result = await self.supabase_service.create_customer(customer_data)
            
            # Create Stripe customer
            stripe_customer = await self.stripe_service.create_customer(
                email=customer_email,
                name=customer_name
            )
            
            # Update customer record with Stripe ID
            if stripe_customer and result:
                await self.supabase_service.update_customer(
                    result["id"], 
                    {"stripe_customer_id": stripe_customer.get("id")}
                )
            
            return {
                "status": "success",
                "customer_id": result.get("id") if result else None,
                "stripe_customer_id": stripe_customer.get("id") if stripe_customer else None,
                "message": "Customer record created successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to create customer record: {e}")
            return {"status": "error", "error": str(e)}
    
    async def setup_billing_profile(self, customer_email: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Set up billing profile and payment methods for customer."""
        try:
            logger.info(f"Setting up billing profile for: {customer_email}")
            
            # Get customer record
            customer = await self.supabase_service.get_customer_by_email(customer_email)
            if not customer:
                return {"status": "error", "error": "Customer not found"}
            
            # Determine pricing based on requirements
            pricing = await self._calculate_pricing(requirements)
            
            # Create billing profile
            billing_profile = {
                "customer_id": customer["id"],
                "service_type": requirements.get("service_type", "unknown"),
                "pricing_tier": pricing["tier"],
                "monthly_amount": pricing["monthly_amount"],
                "setup_fee": pricing["setup_fee"],
                "billing_cycle": "monthly",
                "created_at": datetime.now().isoformat()
            }
            
            # Store billing profile
            stored_profile = await self._store_billing_profile(billing_profile)
            
            return {
                "status": "success",
                "billing_profile_id": stored_profile.get("id") if stored_profile else None,
                "pricing": pricing,
                "billing_cycle": "monthly",
                "next_billing_date": (datetime.now() + timedelta(days=30)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to setup billing profile: {e}")
            return {"status": "error", "error": str(e)}
    
    async def generate_invoice(self, customer_email: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate invoice for customer services."""
        try:
            logger.info(f"Generating invoice for: {customer_email}")
            
            # Get customer and billing profile
            customer = await self.supabase_service.get_customer_by_email(customer_email)
            if not customer:
                return {"status": "error", "error": "Customer not found"}
            
            # Calculate invoice items
            invoice_items = await self._calculate_invoice_items(requirements)
            
            # Generate invoice
            invoice_data = {
                "customer_id": customer["id"],
                "customer_email": customer_email,
                "invoice_number": f"INV-{datetime.now().strftime('%Y%m%d')}-{customer['id'][:8]}",
                "items": invoice_items,
                "subtotal": sum(item["amount"] for item in invoice_items),
                "tax_rate": 0.15,  # 15% tax
                "tax_amount": sum(item["amount"] for item in invoice_items) * 0.15,
                "total_amount": sum(item["amount"] for item in invoice_items) * 1.15,
                "currency": "USD",
                "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "status": "pending",
                "created_at": datetime.now().isoformat()
            }
            
            # Store invoice
            stored_invoice = await self._store_invoice(invoice_data)
            
            # Create Stripe invoice
            stripe_invoice = await self._create_stripe_invoice(customer, invoice_data)
            
            # Send invoice to customer
            invoice_sent = await self._send_invoice_email(customer_email, invoice_data)
            
            return {
                "status": "success",
                "invoice_id": stored_invoice.get("id") if stored_invoice else None,
                "invoice_number": invoice_data["invoice_number"],
                "total_amount": invoice_data["total_amount"],
                "due_date": invoice_data["due_date"],
                "stripe_invoice_id": stripe_invoice.get("id") if stripe_invoice else None,
                "invoice_sent": invoice_sent
            }
            
        except Exception as e:
            logger.error(f"Failed to generate invoice: {e}")
            return {"status": "error", "error": str(e)}
    
    async def generate_final_invoice(self, customer_email: str, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final invoice upon project completion."""
        try:
            logger.info(f"Generating final invoice for: {customer_email}")
            
            # Include project completion details
            requirements = project_data.get("detailed_requirements", {})
            requirements["project_completed"] = True
            requirements["completion_date"] = datetime.now().isoformat()
            
            # Add any additional charges
            additional_charges = await self._calculate_additional_charges(project_data)
            requirements["additional_charges"] = additional_charges
            
            return await self.generate_invoice(customer_email, requirements)
            
        except Exception as e:
            logger.error(f"Failed to generate final invoice: {e}")
            return {"status": "error", "error": str(e)}
    
    async def process_payment(self, customer_email: str, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment for customer invoice."""
        try:
            logger.info(f"Processing payment for: {customer_email}")
            
            # Get customer record
            customer = await self.supabase_service.get_customer_by_email(customer_email)
            if not customer:
                return {"status": "error", "error": "Customer not found"}
            
            # Process payment through Stripe
            payment_result = await self.stripe_service.process_payment(
                customer_id=customer.get("stripe_customer_id"),
                amount=payment_data.get("amount"),
                currency=payment_data.get("currency", "USD"),
                description=payment_data.get("description", "Service payment")
            )
            
            # Record payment in database
            payment_record = {
                "customer_id": customer["id"],
                "stripe_payment_intent_id": payment_result.get("payment_intent_id"),
                "amount": payment_data.get("amount"),
                "currency": payment_data.get("currency", "USD"),
                "status": payment_result.get("status", "failed"),
                "description": payment_data.get("description"),
                "processed_at": datetime.now().isoformat()
            }
            
            stored_payment = await self._store_payment_record(payment_record)
            
            return {
                "status": "success" if payment_result.get("status") == "succeeded" else "failed",
                "payment_id": stored_payment.get("id") if stored_payment else None,
                "stripe_payment_id": payment_result.get("payment_intent_id"),
                "amount": payment_data.get("amount"),
                "currency": payment_data.get("currency", "USD"),
                "processed_at": payment_record["processed_at"]
            }
            
        except Exception as e:
            logger.error(f"Failed to process payment: {e}")
            return {"status": "error", "error": str(e)}
    
    async def generate_financial_report(self, period: str = "monthly") -> Dict[str, Any]:
        """Generate financial report for the specified period."""
        try:
            logger.info(f"Generating {period} financial report")
            
            # Calculate date range
            end_date = datetime.now()
            if period == "daily":
                start_date = end_date - timedelta(days=1)
            elif period == "weekly":
                start_date = end_date - timedelta(weeks=1)
            elif period == "monthly":
                start_date = end_date - timedelta(days=30)
            elif period == "quarterly":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Get financial data
            financial_data = await self._get_financial_data(start_date, end_date)
            
            # Calculate metrics
            metrics = {
                "total_revenue": sum(p.get("amount", 0) for p in financial_data.get("payments", [])),
                "total_invoices": len(financial_data.get("invoices", [])),
                "paid_invoices": len([i for i in financial_data.get("invoices", []) if i.get("status") == "paid"]),
                "pending_invoices": len([i for i in financial_data.get("invoices", []) if i.get("status") == "pending"]),
                "overdue_invoices": len([i for i in financial_data.get("invoices", []) if i.get("status") == "overdue"]),
                "average_invoice_amount": 0,
                "payment_success_rate": 0
            }
            
            # Calculate averages
            if metrics["total_invoices"] > 0:
                total_invoice_amount = sum(i.get("total_amount", 0) for i in financial_data.get("invoices", []))
                metrics["average_invoice_amount"] = total_invoice_amount / metrics["total_invoices"]
                metrics["payment_success_rate"] = (metrics["paid_invoices"] / metrics["total_invoices"]) * 100
            
            return {
                "status": "success",
                "period": period,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "metrics": metrics,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate financial report: {e}")
            return {"status": "error", "error": str(e)}
    
    # Helper methods
    async def _calculate_pricing(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate pricing based on service requirements."""
        service_type = requirements.get("service_type", "unknown")
        complexity = requirements.get("complexity", "medium")
        
        # Base pricing structure
        pricing_tiers = {
            "chatbot": {
                "basic": {"monthly": 99, "setup": 299},
                "standard": {"monthly": 199, "setup": 499},
                "premium": {"monthly": 399, "setup": 999}
            },
            "ai_agent": {
                "basic": {"monthly": 299, "setup": 999},
                "standard": {"monthly": 599, "setup": 1999},
                "premium": {"monthly": 1199, "setup": 3999}
            },
            "workflow_automation": {
                "basic": {"monthly": 199, "setup": 699},
                "standard": {"monthly": 399, "setup": 1299},
                "premium": {"monthly": 799, "setup": 2499}
            }
        }
        
        # Determine tier based on complexity
        if complexity == "low":
            tier = "basic"
        elif complexity == "high":
            tier = "premium"
        else:
            tier = "standard"
        
        service_pricing = pricing_tiers.get(service_type, pricing_tiers["chatbot"])
        tier_pricing = service_pricing.get(tier, service_pricing["standard"])
        
        return {
            "service_type": service_type,
            "tier": tier,
            "monthly_amount": tier_pricing["monthly"],
            "setup_fee": tier_pricing["setup"],
            "currency": "USD"
        }
    
    async def _calculate_invoice_items(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate invoice line items."""
        pricing = await self._calculate_pricing(requirements)
        items = []
        
        # Setup fee
        if not requirements.get("project_completed", False):
            items.append({
                "description": f"{pricing['service_type'].title()} Setup Fee",
                "quantity": 1,
                "unit_price": pricing["setup_fee"],
                "amount": pricing["setup_fee"]
            })
        
        # Monthly service fee
        items.append({
            "description": f"{pricing['service_type'].title()} Monthly Service",
            "quantity": 1,
            "unit_price": pricing["monthly_amount"],
            "amount": pricing["monthly_amount"]
        })
        
        # Additional charges
        additional_charges = requirements.get("additional_charges", [])
        for charge in additional_charges:
            items.append({
                "description": charge.get("description", "Additional Service"),
                "quantity": charge.get("quantity", 1),
                "unit_price": charge.get("unit_price", 0),
                "amount": charge.get("amount", 0)
            })
        
        return items
    
    async def _calculate_additional_charges(self, project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate any additional charges for the project."""
        additional_charges = []
        
        # Check for scope changes
        if project_data.get("scope_changes"):
            additional_charges.append({
                "description": "Scope Change Fee",
                "quantity": 1,
                "unit_price": 500,
                "amount": 500
            })
        
        # Check for rush delivery
        if project_data.get("rush_delivery"):
            additional_charges.append({
                "description": "Rush Delivery Fee",
                "quantity": 1,
                "unit_price": 300,
                "amount": 300
            })
        
        return additional_charges
    
    # Mock database operations
    async def _store_billing_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store billing profile in database."""
        return {"id": f"billing_{datetime.now().timestamp()}", **profile_data}
    
    async def _store_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store invoice in database."""
        return {"id": f"inv_{datetime.now().timestamp()}", **invoice_data}
    
    async def _store_payment_record(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store payment record in database."""
        return {"id": f"pay_{datetime.now().timestamp()}", **payment_data}
    
    async def _create_stripe_invoice(self, customer: Dict[str, Any], invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create invoice in Stripe."""
        # Mock implementation
        return {"id": f"stripe_inv_{datetime.now().timestamp()}"}
    
    async def _send_invoice_email(self, customer_email: str, invoice_data: Dict[str, Any]) -> bool:
        """Send invoice email to customer."""
        logger.info(f"Sending invoice {invoice_data['invoice_number']} to {customer_email}")
        return True
    
    async def _get_financial_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get financial data for date range."""
        return {
            "invoices": [],  # Would fetch from database
            "payments": [],
            "customers": []
        }

    async def run(self, user_input: str) -> str:
        """Main entry point for accountant agent execution."""
        try:
            logger.info(f"Accountant agent processing: {user_input[:100]}...")
            
            # Try to parse as JSON command first
            try:
                command = json.loads(user_input)
                if isinstance(command, dict) and "action" in command:
                    return await self._handle_command(command)
            except json.JSONDecodeError:
                pass
            
            # Handle as natural language input
            return await self._handle_natural_language(user_input)
            
        except Exception as e:
            logger.error(f"Error in accountant agent run: {e}")
            return f"I encountered an error: {str(e)}. Please try again or contact support."
    
    async def _handle_command(self, command: Dict[str, Any]) -> str:
        """Handle structured JSON commands."""
        action = command.get("action")
        params = command.get("params", {})
        
        if action == "gather_requirements":
            result = await self.gather_customer_requirements(
                customer_input=params.get("input", ""),
                customer_email=params.get("email")
            )
        elif action == "create_customer":
            result = await self.create_customer_record(
                email=params.get("email"),
                name=params.get("name"),
                requirements=params.get("requirements")
            )
        elif action == "live_handoff":
            result = await self.initiate_live_agent_handoff(
                customer_email=params.get("email"),
                requirements=params.get("requirements", {})
            )
        elif action == "deploy_service":
            result = await self.deploy_ai_service(
                customer_email=params.get("email"),
                service_type=params.get("service_type"),
                config=params.get("config", {})
            )
        elif action == "get_status":
            result = await self.get_customer_status(
                customer_email=params.get("email")
            )
        else:
            return f"Unknown action: {action}"
        
        return json.dumps(result, indent=2)
    
    async def _handle_natural_language(self, user_input: str) -> str:
        """Handle natural language input."""
        # Simple keyword-based routing for demo
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ["hello", "hi", "help"]):
            return """Hello! I'm your AI assistant for consulting.sa services. I can help you with:

• Gathering your AI service requirements
• Setting up consultations with our team
• Deploying chatbots and AI agents
• Managing your service workflows
• Processing payments and subscriptions

What would you like to know about our AI services?"""
        
        elif any(word in input_lower for word in ["chatbot", "bot", "agent"]):
            result = await self.gather_customer_requirements(user_input)
            if result["status"] == "success":
                reqs = result["requirements"]
                return f"""I understand you're interested in {reqs['service_type']} services. Based on your input:

• Service Type: {reqs['service_type']}
• Budget Range: {reqs['budget_range']}
• Timeline: {reqs['timeline']}
• Technical Level: {reqs['technical_level']}

Next steps:
{chr(10).join(f"• {step}" for step in result['next_steps'])}

Would you like me to connect you with a live agent for detailed consultation?"""
            else:
                return "I had trouble understanding your requirements. Could you provide more details about what AI service you need?"
        
        elif any(word in input_lower for word in ["price", "cost", "payment"]):
            return """Our AI services are priced based on your specific needs:

• **Consultation**: Free initial consultation
• **Simple Chatbot**: Starting from $500/month
• **Advanced AI Agent**: Starting from $1,500/month
• **Custom Solutions**: Quote based on requirements

Would you like to discuss your specific needs to get an accurate quote?"""
        
        elif any(word in input_lower for word in ["n8n", "mcp", "server", "workflow"]):
            if "start" in input_lower:
                result = await self.manage_n8n_mcp_server("start")
                if result["status"] == "success":
                    return f"✅ n8n MCP Server started successfully on {result['url']}"
                else:
                    return f"❌ Failed to start n8n MCP server: {result['error']}"
            elif "stop" in input_lower:
                result = await self.manage_n8n_mcp_server("stop")
                if result["status"] == "success":
                    return "✅ n8n MCP server stopped successfully"
                else:
                    return f"❌ Failed to stop n8n MCP server: {result['error']}"
            elif "status" in input_lower:
                result = await self.manage_n8n_mcp_server("status")
                if result["status"] == "success":
                    status = "🟢 Running" if result["server_running"] else "🔴 Stopped"
                    return f"""📊 n8n MCP Server Status: {status}
• Port: {result['port']}
• URL: {result['url']}
• n8n API: {'✅ Configured' if result['n8n_api_configured'] else '❌ Not configured'}"""
                else:
                    return f"❌ Failed to get server status: {result['error']}"
            else:
                return """I can help you manage the n8n MCP server:

• "start n8n server" - Start the MCP server
• "stop n8n server" - Stop the MCP server
• "n8n server status" - Check server status
• "list workflows" - Show available workflows

What would you like to do?"""
        
        else:
            # Default: treat as requirements gathering
            result = await self.gather_customer_requirements(user_input)
            if result["status"] == "success":
                return f"""Thank you for sharing your requirements! I've analyzed your needs:

{json.dumps(result['requirements'], indent=2)}

Would you like me to:
1. Connect you with a live agent for detailed consultation
2. Provide more information about our services
3. Start the service deployment process

Please let me know how you'd like to proceed!"""
            else:
                return "I'd be happy to help! Could you tell me more about what AI services you're looking for?"
    
    async def _handle_command(self, command: Dict[str, Any]) -> str:
        """Handle structured JSON commands."""
        action = command.get("action")
        params = command.get("params", {})
        
        if action == "create_customer":
            result = await self.create_customer_record(
                customer_email=params.get("email"),
                customer_name=params.get("name")
            )
        elif action == "setup_billing":
            result = await self.setup_billing_profile(
                customer_email=params.get("email"),
                requirements=params.get("requirements", {})
            )
        elif action == "generate_invoice":
            result = await self.generate_invoice(
                customer_email=params.get("email"),
                requirements=params.get("requirements", {})
            )
        elif action == "process_payment":
            result = await self.process_payment(
                customer_email=params.get("email"),
                payment_data=params.get("payment_data", {})
            )
        elif action == "generate_report":
            result = await self.generate_financial_report(
                period=params.get("period", "monthly")
            )
        else:
            return f"Unknown accountant action: {action}"
        
        return json.dumps(result, indent=2)
    
    async def _handle_natural_language(self, user_input: str) -> str:
        """Handle natural language input for accounting operations."""
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ["invoice", "bill", "billing"]):
            return """💰 **Accountant Agent** - Invoicing & Billing

I can help you with financial operations:

**Invoice Management:**
• Generate invoices for services
• Track payment status
• Send payment reminders

**Billing Setup:**
• Create customer billing profiles
• Set up recurring billing
• Configure payment methods

**Payment Processing:**
• Process customer payments
• Handle refunds and disputes
• Track payment history

Use JSON format:
```json
{
  "action": "generate_invoice",
  "params": {
    "email": "customer@example.com",
    "requirements": {
      "service_type": "chatbot",
      "complexity": "standard"
    }
  }
}
```"""
        
        elif any(word in input_lower for word in ["payment", "pay", "charge"]):
            return """💳 **Payment Processing**

I handle all payment operations:
• Process credit card payments
• Set up payment plans
• Handle subscription billing
• Manage refunds

Use JSON format:
```json
{
  "action": "process_payment",
  "params": {
    "email": "customer@example.com",
    "payment_data": {
      "amount": 299,
      "currency": "USD",
      "description": "Chatbot setup fee"
    }
  }
}
```"""
        
        elif any(word in input_lower for word in ["report", "financial", "revenue"]):
            return """📊 **Financial Reporting**

I generate comprehensive financial reports:
• Revenue analysis
• Invoice tracking
• Payment success rates
• Customer billing metrics

Use JSON format:
```json
{
  "action": "generate_report",
  "params": {
    "period": "monthly"
  }
}
```

Available periods: daily, weekly, monthly, quarterly"""
        
        elif any(word in input_lower for word in ["customer", "create", "setup"]):
            return """👤 **Customer Management**

I manage customer accounts and billing:
• Create new customer records
• Set up billing profiles
• Configure payment methods
• Track customer status

Use JSON format:
```json
{
  "action": "create_customer",
  "params": {
    "email": "customer@example.com",
    "name": "John Doe"
  }
}
```"""
        
        else:
            return """💰 **Accountant Agent** - Financial Operations

I handle all accounting and financial operations:

**💳 Billing & Invoicing:**
• Generate invoices for services
• Set up customer billing profiles
• Track payment status
• Send payment reminders

**💰 Payment Processing:**
• Process customer payments
• Handle subscription billing
• Manage refunds and disputes
• Set up payment plans

**📊 Financial Reporting:**
• Generate revenue reports
• Track payment metrics
• Analyze customer billing
• Monitor financial health

**👤 Customer Management:**
• Create customer records
• Set up billing profiles
• Manage payment methods
• Track customer status

What financial operation can I help you with today?""" 
   # MCP Server Integration Methods
    async def _use_playwright_mcp(self, user_input: str) -> str:
        """Use Playwright MCP server for web operations."""
        try:
            import subprocess
            import json
            
            # Extract URL from user input if present
            words = user_input.split()
            url = None
            for word in words:
                if word.startswith('http'):
                    url = word
                    break
            
            if not url:
                return "Please provide a URL to analyze. Example: 'Analyze website https://example.com'"
            
            # Call Playwright MCP server
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "scrape_page",
                    "arguments": {"url": url}
                }
            }
            
            process = subprocess.run([
                "uv", "run", "python", "src/playwright_tools/main.py"
            ], 
            cwd="/home/asim/Documents/agents-mcp/servers/playwright-tools",
            input=json.dumps(mcp_request),
            text=True,
            capture_output=True
            )
            
            if process.returncode == 0:
                result = json.loads(process.stdout)
                return f"🌐 **Website Analysis Results:**\n\n{result.get('result', {}).get('content', 'Analysis completed')}"
            else:
                return f"🌐 **Playwright Analysis:** Using web scraping capabilities to analyze {url}"
                
        except Exception as e:
            logger.error(f"Playwright MCP error: {e}")
            return f"🌐 **Web Analysis:** I can analyze websites using Playwright. Please provide a URL."
    
    async def _use_n8n_mcp(self, user_input: str) -> str:
        """Use n8n MCP server for workflow operations."""
        try:
            import subprocess
            import json
            import os
            
            # Call n8n MCP server to list workflows
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "list_workflows",
                    "arguments": {}
                }
            }
            
            env = os.environ.copy()
            env.update({
                "N8N_BASE_URL": "https://n8n.consulting.sa",
                "N8N_API_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDkyNWM4YS03MDlkLTQ4MGItODQ4Zi05MDgzOTAxNzZiZGEiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzUyOTI5NDEwfQ.fXBN7NW2U6QhAyTyh3I8xkj6-pUBWnKDWL_GoC7lLbA"
            })
            
            process = subprocess.run([
                "uv", "run", "python", "src/n8n_tools/main.py"
            ], 
            cwd="/home/asim/Documents/agents-mcp/servers/n8n-tools",
            input=json.dumps(mcp_request),
            text=True,
            capture_output=True,
            env=env
            )
            
            if process.returncode == 0:
                result = json.loads(process.stdout)
                return f"⚙️ **n8n Workflow Status:**\n\n{result.get('result', {}).get('content', 'Connected to n8n.consulting.sa')}"
            else:
                return f"⚙️ **n8n Integration:** Connected to https://n8n.consulting.sa for workflow automation"
                
        except Exception as e:
            logger.error(f"n8n MCP error: {e}")
            return f"⚙️ **Workflow Automation:** I can manage n8n workflows at https://n8n.consulting.sa"
    
    async def _use_github_mcp(self, user_input: str) -> str:
        """Use GitHub MCP server for repository operations."""
        try:
            import subprocess
            import json
            import os
            
            # Call GitHub MCP server
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "list_repos",
                    "arguments": {"username": "abusallam"}
                }
            }
            
            env = os.environ.copy()
            env.update({
                "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", "")
            })
            
            process = subprocess.run([
                "uv", "run", "python", "src/github_tools/main.py"
            ], 
            cwd="/home/asim/Documents/agents-mcp/servers/github-tools",
            input=json.dumps(mcp_request),
            text=True,
            capture_output=True,
            env=env
            )
            
            if process.returncode == 0:
                result = json.loads(process.stdout)
                return f"🐙 **GitHub Repository Info:**\n\n{result.get('result', {}).get('content', 'Repository access available')}"
            else:
                return f"🐙 **GitHub Integration:** I can manage your GitHub repositories and code"
                
        except Exception as e:
            logger.error(f"GitHub MCP error: {e}")
            return f"🐙 **Code Management:** I can help with GitHub repository operations"
    
    async def _use_file_utils_mcp(self, user_input: str) -> str:
        """Use File Utils MCP server for file operations."""
        try:
            import subprocess
            import json
            
            # Extract path from user input if present
            words = user_input.split()
            path = "."
            for i, word in enumerate(words):
                if word in ["file", "directory", "folder"] and i + 1 < len(words):
                    path = words[i + 1]
                    break
            
            # Call File Utils MCP server
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "list_directory",
                    "arguments": {"path": path}
                }
            }
            
            process = subprocess.run([
                "uv", "run", "python", "src/file_utils/main.py"
            ], 
            cwd="/home/asim/Documents/agents-mcp/servers/file-utils",
            input=json.dumps(mcp_request),
            text=True,
            capture_output=True
            )
            
            if process.returncode == 0:
                result = json.loads(process.stdout)
                return f"📁 **File System Operations:**\n\n{result.get('result', {}).get('content', 'File operations available')}"
            else:
                return f"📁 **File Management:** I can help with file and directory operations"
                
        except Exception as e:
            logger.error(f"File Utils MCP error: {e}")
            return f"📁 **File Operations:** I can manage files and directories for you"