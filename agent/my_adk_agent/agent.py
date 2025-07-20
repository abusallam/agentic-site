"""Main ADK Agent for customer journey orchestration."""

import json
import logging
from typing import Dict, Any, Optional, List
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


class CustomerJourneyAgent(BaseAgent):
    """ADK Agent that orchestrates the complete customer journey."""
    
    def __init__(self):
        """Initialize the customer journey agent."""
        super().__init__(
            name="customer_journey_agent",
            description="ADK Agent for orchestrating customer journey from initial contact to service delivery"
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
        
        logger.info("CustomerJourneyAgent initialized")
    
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

    async def run(self, user_input: str) -> str:
        """Main entry point for agent execution."""
        try:
            logger.info(f"Processing user input: {user_input[:100]}...")
            
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
            logger.error(f"Error in agent run: {e}")
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