"""
N8N Workflow Agent - Fast agentic chatbots using N8N platform with Composio integration
Handles workflow automation with sub-agents, knowledge bases, and OAuth management
"""
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentResponse, AgentConfig
from dataclasses import dataclass
import logging
import json
import requests

logger = logging.getLogger(__name__)


@dataclass
class WorkflowDefinition:
    """N8N workflow definition with Composio integration"""
    name: str
    description: str
    nodes: List[Dict[str, Any]]
    connections: Dict[str, Any]
    settings: Dict[str, Any]
    composio_apps: List[str] = None  # Apps requiring OAuth via Composio
    oauth_requirements: Dict[str, Any] = None


@dataclass
class SubAgent:
    """Sub-agent definition for workflows"""
    name: str
    role: str
    capabilities: List[str]
    knowledge_base: str
    composio_tools: List[str] = None


@dataclass
class ComposioIntegration:
    """Composio OAuth and tool integration"""
    app_name: str
    auth_scheme: str
    required_scopes: List[str]
    setup_instructions: str
    connection_status: str = "pending"


class N8NWorkflowAgent(BaseAgent):
    """Agent for N8N-based workflow automation with Composio integration"""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.n8n_client = N8NClient()
        self.composio_client = ComposioClient()
        self.sub_agents = {}
        self.knowledge_bases = {}
        self.workflow_templates = self._load_workflow_templates()
        self.composio_integrations = self._load_composio_integrations()
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the N8N workflow agent"""
        return """
        You are an N8N Workflow Agent specializing in fast, template-based automation solutions.
        
        Your capabilities include:
        1. Creating N8N workflows from templates
        2. Deploying specialized sub-agents for specific tasks
        3. Managing knowledge bases for workflow context
        4. Providing quick automation solutions using pre-built components
        
        Focus on:
        - Speed and efficiency
        - Template-based solutions
        - Sub-agent coordination
        - Knowledge base integration
        
        Always provide practical, implementable workflow solutions.
        """
    
    def process_message(self, message: str, context: Dict[str, Any] = None) -> AgentResponse:
        """Process workflow automation request"""
        self.add_to_history("user", message)
        
        # Analyze workflow requirements
        requirements = self._analyze_workflow_requirements(message, context)
        
        # Find matching templates
        templates = self._find_matching_templates(requirements)
        
        # Generate workflow recommendation
        response_message = self._generate_workflow_response(requirements, templates)
        
        # Prepare workflow creation if requested
        next_action = self._determine_workflow_action(requirements)
        
        response = AgentResponse(
            message=response_message,
            confidence=0.8,  # High confidence for template-based solutions
            next_action=next_action,
            context={
                "requirements": requirements,
                "templates": templates,
                "workflow_type": "n8n_automation"
            }
        )
        
        self.add_to_history("assistant", response_message)
        return response
    
    def _analyze_workflow_requirements(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze workflow requirements from customer message"""
        requirements = {
            "type": "unknown",
            "complexity": "simple",
            "integrations": [],
            "triggers": [],
            "actions": [],
            "data_sources": []
        }
        
        message_lower = message.lower()
        
        # Detect workflow type
        if any(word in message_lower for word in ["chatbot", "chat", "conversation"]):
            requirements["type"] = "chatbot"
        elif any(word in message_lower for word in ["email", "notification", "alert"]):
            requirements["type"] = "notification"
        elif any(word in message_lower for word in ["data", "sync", "integration"]):
            requirements["type"] = "data_sync"
        elif any(word in message_lower for word in ["form", "submission", "lead"]):
            requirements["type"] = "form_processing"
        
        # Detect integrations
        integrations_map = {
            "slack": "slack",
            "discord": "discord",
            "email": "email",
            "webhook": "webhook",
            "database": "database",
            "api": "http_request",
            "google": "google_sheets",
            "sheets": "google_sheets"
        }
        
        for keyword, integration in integrations_map.items():
            if keyword in message_lower:
                requirements["integrations"].append(integration)
        
        # Detect triggers
        if any(word in message_lower for word in ["when", "trigger", "schedule"]):
            if "schedule" in message_lower:
                requirements["triggers"].append("schedule")
            if "webhook" in message_lower:
                requirements["triggers"].append("webhook")
            if "email" in message_lower:
                requirements["triggers"].append("email")
        
        return requirements
    
    def _find_matching_templates(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find matching workflow templates"""
        workflow_type = requirements.get("type", "unknown")
        templates = self.workflow_templates.get(workflow_type, [])
        
        # Filter templates based on integrations
        if requirements.get("integrations"):
            filtered_templates = []
            for template in templates:
                template_integrations = set(template.get("integrations", []))
                required_integrations = set(requirements["integrations"])
                if template_integrations.intersection(required_integrations):
                    filtered_templates.append(template)
            return filtered_templates
        
        return templates
    
    def _generate_workflow_response(self, requirements: Dict[str, Any], templates: List[Dict[str, Any]]) -> str:
        """Generate workflow response based on requirements and templates"""
        workflow_type = requirements.get("type", "automation")
        
        if not templates:
            return (f"I can help you create a custom {workflow_type} workflow. "
                   f"Based on your requirements, I'll need to build a solution that includes "
                   f"{', '.join(requirements.get('integrations', ['basic automation']))}. "
                   f"Would you like me to proceed with creating this workflow?")
        
        template_names = [t["name"] for t in templates[:3]]  # Show top 3 templates
        
        return (f"Great! I found {len(templates)} template(s) for {workflow_type} automation. "
               f"The best matches are: {', '.join(template_names)}. "
               f"I can deploy any of these templates and customize them for your needs. "
               f"I'll also set up specialized sub-agents to handle specific tasks within the workflow. "
               f"Which template would you like to start with, or shall I recommend the best one?")
    
    def _determine_workflow_action(self, requirements: Dict[str, Any]) -> str:
        """Determine next action for workflow creation"""
        if requirements.get("type") != "unknown":
            return "create_workflow"
        else:
            return "clarify_requirements"
    
    def create_workflow(self, requirements: Dict[str, Any]) -> WorkflowDefinition:
        """Create N8N workflow based on requirements"""
        workflow_type = requirements.get("type", "basic")
        
        # Get base template
        templates = self._find_matching_templates(requirements)
        base_template = templates[0] if templates else self._get_default_template()
        
        # Create workflow definition
        workflow = WorkflowDefinition(
            name=f"{workflow_type}_workflow_{self._generate_id()}",
            description=f"Automated {workflow_type} workflow",
            nodes=base_template.get("nodes", []),
            connections=base_template.get("connections", {}),
            settings=base_template.get("settings", {})
        )
        
        # Customize based on requirements
        workflow = self._customize_workflow(workflow, requirements)
        
        return workflow
    
    def deploy_sub_agents(self, workflow: WorkflowDefinition) -> List[SubAgent]:
        """Deploy specialized sub-agents for workflow"""
        sub_agents = []
        
        # Analyze workflow to determine needed sub-agents
        for node in workflow.nodes:
            node_type = node.get("type", "")
            
            if "chat" in node_type.lower():
                sub_agents.append(SubAgent(
                    name="ChatHandler",
                    role="conversation_management",
                    capabilities=["natural_language_processing", "response_generation"],
                    knowledge_base="chat_responses"
                ))
            
            elif "email" in node_type.lower():
                sub_agents.append(SubAgent(
                    name="EmailProcessor",
                    role="email_automation",
                    capabilities=["email_parsing", "template_processing"],
                    knowledge_base="email_templates"
                ))
            
            elif "data" in node_type.lower():
                sub_agents.append(SubAgent(
                    name="DataProcessor",
                    role="data_transformation",
                    capabilities=["data_validation", "format_conversion"],
                    knowledge_base="data_schemas"
                ))
        
        # Deploy sub-agents
        for sub_agent in sub_agents:
            self._deploy_sub_agent(sub_agent)
        
        return sub_agents
    
    def _deploy_sub_agent(self, sub_agent: SubAgent):
        """Deploy individual sub-agent"""
        self.sub_agents[sub_agent.name] = sub_agent
        logger.info(f"Deployed sub-agent: {sub_agent.name} with role: {sub_agent.role}")
    
    def _load_workflow_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load workflow templates"""
        return {
            "chatbot": [
                {
                    "name": "Basic Chatbot",
                    "description": "Simple Q&A chatbot",
                    "integrations": ["webhook", "http_request"],
                    "nodes": [],
                    "connections": {},
                    "settings": {}
                },
                {
                    "name": "Support Chatbot",
                    "description": "Customer support chatbot with ticket creation",
                    "integrations": ["webhook", "email", "database"],
                    "nodes": [],
                    "connections": {},
                    "settings": {}
                }
            ],
            "notification": [
                {
                    "name": "Email Alerts",
                    "description": "Automated email notification system",
                    "integrations": ["email", "webhook"],
                    "nodes": [],
                    "connections": {},
                    "settings": {}
                }
            ],
            "data_sync": [
                {
                    "name": "Database Sync",
                    "description": "Sync data between systems",
                    "integrations": ["database", "api", "webhook"],
                    "nodes": [],
                    "connections": {},
                    "settings": {}
                }
            ]
        }
    
    def _get_default_template(self) -> Dict[str, Any]:
        """Get default workflow template"""
        return {
            "name": "Basic Workflow",
            "nodes": [],
            "connections": {},
            "settings": {}
        }
    
    def _customize_workflow(self, workflow: WorkflowDefinition, requirements: Dict[str, Any]) -> WorkflowDefinition:
        """Customize workflow based on specific requirements"""
        # Add integration-specific nodes
        for integration in requirements.get("integrations", []):
            if integration not in [node.get("type") for node in workflow.nodes]:
                workflow.nodes.append({
                    "type": integration,
                    "name": f"{integration}_node",
                    "parameters": {}
                })
        
        return workflow
    
    def _generate_id(self) -> str:
        """Generate unique ID for workflow"""
        import uuid
        return str(uuid.uuid4())[:8]    

    def get_system_prompt(self) -> str:
        """Enhanced system prompt for N8N workflow agent with Composio integration"""
        return """
        You are an advanced N8N Workflow Agent specializing in fast, automated solutions with seamless OAuth integration.
        
        Your enhanced capabilities include:
        1. Creating N8N workflows with Composio OAuth integration for popular services
        2. Managing customer authentication for Gmail, Calendar, Facebook, Slack, and 100+ other apps
        3. Deploying specialized sub-agents with knowledge bases
        4. Acting as a system administrator for N8N workflows with monitoring capabilities
        5. Providing automated OAuth setup and credential management through Composio
        
        Composio Integration Powers:
        - Automated OAuth flows for customer applications
        - Secure credential storage and management
        - Pre-built integrations for popular services
        - Real-time connection status monitoring
        
        Your workflow process:
        1. Analyze customer requirements and identify needed integrations
        2. Set up Composio OAuth for required services (Gmail, Calendar, Facebook, etc.)
        3. Create N8N workflow with proper authentication nodes
        4. Deploy sub-agents for specialized tasks
        5. Monitor and maintain workflows as system admin
        
        Always guide customers through OAuth setup and provide clear instructions for accessing their workflows.
        """
    
    def setup_composio_oauth(self, customer_id: str, required_apps: List[str]) -> Dict[str, Any]:
        """Set up Composio OAuth for required applications"""
        oauth_setup = {
            "customer_id": customer_id,
            "apps": {},
            "setup_instructions": [],
            "auth_urls": {}
        }
        
        for app in required_apps:
            if app in self.composio_integrations:
                integration = self.composio_integrations[app]
                
                # Generate OAuth URL through Composio
                auth_url = self.composio_client.get_auth_url(
                    app_name=app,
                    customer_id=customer_id,
                    scopes=integration.required_scopes
                )
                
                oauth_setup["apps"][app] = {
                    "status": "pending_auth",
                    "auth_url": auth_url,
                    "scopes": integration.required_scopes,
                    "instructions": integration.setup_instructions
                }
                
                oauth_setup["auth_urls"][app] = auth_url
                oauth_setup["setup_instructions"].append(
                    f"For {app}: {integration.setup_instructions}"
                )
        
        return oauth_setup
    
    def create_workflow_with_oauth(self, requirements: Dict[str, Any], customer_id: str) -> Dict[str, Any]:
        """Create N8N workflow with Composio OAuth integration"""
        workflow_type = requirements.get("type", "basic")
        required_apps = self._extract_required_apps(requirements)
        
        # Set up OAuth for required apps
        oauth_setup = self.setup_composio_oauth(customer_id, required_apps)
        
        # Create base workflow
        workflow = self.create_workflow(requirements)
        workflow.composio_apps = required_apps
        workflow.oauth_requirements = oauth_setup
        
        # Add Composio authentication nodes to workflow
        workflow = self._add_composio_auth_nodes(workflow, required_apps)
        
        # Deploy to N8N with OAuth configuration
        deployment_result = self.n8n_client.deploy_workflow(workflow)
        
        return {
            "workflow": workflow,
            "oauth_setup": oauth_setup,
            "deployment": deployment_result,
            "next_steps": [
                "Complete OAuth authentication for required apps",
                "Test workflow with authenticated connections",
                "Monitor workflow execution"
            ]
        }
    
    def _extract_required_apps(self, requirements: Dict[str, Any]) -> List[str]:
        """Extract required apps from workflow requirements"""
        required_apps = []
        integrations = requirements.get("integrations", [])
        
        # Map integrations to Composio apps
        app_mapping = {
            "gmail": "gmail",
            "google_sheets": "googlesheets",
            "calendar": "googlecalendar",
            "slack": "slack",
            "facebook": "facebook",
            "twitter": "twitter",
            "linkedin": "linkedin",
            "hubspot": "hubspot",
            "salesforce": "salesforce"
        }
        
        for integration in integrations:
            if integration in app_mapping:
                required_apps.append(app_mapping[integration])
        
        return required_apps
    
    def _add_composio_auth_nodes(self, workflow: WorkflowDefinition, required_apps: List[str]) -> WorkflowDefinition:
        """Add Composio authentication nodes to workflow"""
        for app in required_apps:
            auth_node = {
                "id": f"composio_auth_{app}",
                "name": f"Composio {app.title()} Auth",
                "type": "n8n-nodes-base.composio",
                "parameters": {
                    "app": app,
                    "operation": "authenticate",
                    "useComposioAuth": True
                },
                "position": [200, 300 + (len(workflow.nodes) * 100)]
            }
            workflow.nodes.append(auth_node)
        
        return workflow
    
    def monitor_workflow_execution(self, workflow_id: str) -> Dict[str, Any]:
        """Monitor N8N workflow execution as system admin"""
        execution_data = self.n8n_client.get_execution_data(workflow_id)
        
        monitoring_report = {
            "workflow_id": workflow_id,
            "status": execution_data.get("status", "unknown"),
            "executions_today": execution_data.get("executions_today", 0),
            "success_rate": execution_data.get("success_rate", 0),
            "last_execution": execution_data.get("last_execution"),
            "errors": execution_data.get("errors", []),
            "oauth_status": self._check_oauth_status(workflow_id),
            "recommendations": self._generate_monitoring_recommendations(execution_data)
        }
        
        return monitoring_report
    
    def _check_oauth_status(self, workflow_id: str) -> Dict[str, str]:
        """Check OAuth connection status for workflow"""
        workflow = self.n8n_client.get_workflow(workflow_id)
        oauth_status = {}
        
        if hasattr(workflow, 'composio_apps'):
            for app in workflow.composio_apps:
                status = self.composio_client.check_connection_status(app, workflow_id)
                oauth_status[app] = status
        
        return oauth_status
    
    def _generate_monitoring_recommendations(self, execution_data: Dict[str, Any]) -> List[str]:
        """Generate monitoring recommendations based on execution data"""
        recommendations = []
        
        success_rate = execution_data.get("success_rate", 100)
        if success_rate < 90:
            recommendations.append("Consider reviewing error logs and optimizing workflow nodes")
        
        executions = execution_data.get("executions_today", 0)
        if executions == 0:
            recommendations.append("Workflow hasn't executed today - check triggers and scheduling")
        
        errors = execution_data.get("errors", [])
        if errors:
            recommendations.append(f"Address {len(errors)} recent errors to improve reliability")
        
        return recommendations
    
    def _load_composio_integrations(self) -> Dict[str, ComposioIntegration]:
        """Load available Composio integrations"""
        return {
            "gmail": ComposioIntegration(
                app_name="gmail",
                auth_scheme="oauth2",
                required_scopes=["https://www.googleapis.com/auth/gmail.send", "https://www.googleapis.com/auth/gmail.readonly"],
                setup_instructions="Click the link to authorize Gmail access for your workflow"
            ),
            "googlecalendar": ComposioIntegration(
                app_name="googlecalendar",
                auth_scheme="oauth2",
                required_scopes=["https://www.googleapis.com/auth/calendar"],
                setup_instructions="Authorize Google Calendar access to manage your events"
            ),
            "slack": ComposioIntegration(
                app_name="slack",
                auth_scheme="oauth2",
                required_scopes=["chat:write", "channels:read"],
                setup_instructions="Connect your Slack workspace to send messages and read channels"
            ),
            "facebook": ComposioIntegration(
                app_name="facebook",
                auth_scheme="oauth2",
                required_scopes=["pages_manage_posts", "pages_read_engagement"],
                setup_instructions="Authorize Facebook access to manage your pages and posts"
            )
        }


class N8NClient:
    """Client for N8N API interactions"""
    
    def __init__(self):
        self.base_url = "http://n8n:5678/api/v1"
        self.headers = {"Content-Type": "application/json"}
    
    def deploy_workflow(self, workflow: WorkflowDefinition) -> Dict[str, Any]:
        """Deploy workflow to N8N instance"""
        workflow_data = {
            "name": workflow.name,
            "nodes": workflow.nodes,
            "connections": workflow.connections,
            "settings": workflow.settings,
            "active": True
        }
        
        # Mock deployment - in production, make actual API call
        return {
            "id": f"workflow_{workflow.name.lower().replace(' ', '_')}",
            "status": "deployed",
            "webhook_url": f"{self.base_url}/webhook/{workflow.name}",
            "deployed_at": "2024-01-01T00:00:00Z"
        }
    
    def get_execution_data(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow execution data"""
        # Mock execution data - in production, make actual API call
        return {
            "status": "active",
            "executions_today": 5,
            "success_rate": 95.0,
            "last_execution": "2024-01-01T12:00:00Z",
            "errors": []
        }
    
    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow configuration"""
        # Mock workflow data - in production, make actual API call
        return {
            "id": workflow_id,
            "name": "Sample Workflow",
            "active": True
        }


class ComposioClient:
    """Client for Composio OAuth and integration management"""
    
    def __init__(self):
        self.base_url = "https://api.composio.dev/v1"
        self.api_key = "your_composio_api_key"  # Should be from environment
    
    def get_auth_url(self, app_name: str, customer_id: str, scopes: List[str]) -> str:
        """Generate OAuth URL for app authentication"""
        # Mock OAuth URL - in production, make actual API call to Composio
        return f"https://composio.dev/oauth/{app_name}?customer_id={customer_id}&scopes={','.join(scopes)}"
    
    def check_connection_status(self, app_name: str, customer_id: str) -> str:
        """Check OAuth connection status"""
        # Mock status check - in production, make actual API call
        return "connected"  # or "disconnected", "expired", "pending"