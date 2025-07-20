"""MCP service for communication with n8n workflows."""

import os
import json
from typing import Dict, Optional, Any, List
import logging
import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)


class MCPService:
    """Service for MCP server communication with n8n."""
    
    def __init__(self):
        """Initialize MCP service."""
        self.n8n_url = os.getenv("N8N_URL", "http://localhost:5678")
        self.n8n_api_key = os.getenv("N8N_API_KEY")
        self.mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
        
        if not self.n8n_api_key:
            logger.warning("N8N API key not found, using mock mode")
            self.mock_mode = True
        else:
            self.mock_mode = False
    
    async def trigger_workflow(self, workflow_name: str, customer_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Trigger an n8n workflow via MCP server."""
        if self.mock_mode:
            logger.info(f"Mock: Triggering workflow {workflow_name}")
            return {
                "workflow_id": f"mock-workflow-{workflow_name}",
                "execution_id": "mock-execution-123",
                "status": "running",
                "customer_data": customer_data
            }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.mcp_server_url}/trigger-workflow",
                    json={
                        "workflow_name": workflow_name,
                        "data": customer_data,
                        "n8n_url": self.n8n_url,
                        "api_key": self.n8n_api_key
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Triggered workflow {workflow_name}: {result['execution_id']}")
                    return result
                else:
                    logger.error(f"Failed to trigger workflow: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Failed to trigger workflow via MCP: {e}")
            return None
    
    async def get_workflow_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a workflow execution."""
        if self.mock_mode:
            logger.info(f"Mock: Getting status for execution {execution_id}")
            return {
                "execution_id": execution_id,
                "status": "success",
                "progress": 100,
                "result": {"message": "Workflow completed successfully"}
            }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.mcp_server_url}/workflow-status/{execution_id}",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Retrieved status for execution {execution_id}: {result['status']}")
                    return result
                else:
                    logger.error(f"Failed to get workflow status: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Failed to get workflow status via MCP: {e}")
            return None
    
    async def create_custom_workflow(self, workflow_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a custom workflow based on customer requirements."""
        if self.mock_mode:
            logger.info("Mock: Creating custom workflow")
            return {
                "workflow_id": "mock-custom-workflow-123",
                "name": workflow_config.get("name", "Custom Workflow"),
                "status": "created",
                "config": workflow_config
            }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.mcp_server_url}/create-workflow",
                    json={
                        "config": workflow_config,
                        "n8n_url": self.n8n_url,
                        "api_key": self.n8n_api_key
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Created custom workflow: {result['workflow_id']}")
                    return result
                else:
                    logger.error(f"Failed to create custom workflow: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Failed to create custom workflow via MCP: {e}")
            return None
    
    async def list_available_workflows(self) -> List[Dict[str, Any]]:
        """List all available workflows."""
        if self.mock_mode:
            logger.info("Mock: Listing available workflows")
            return [
                {"id": "chatbot-deployment", "name": "Chatbot Deployment", "description": "Deploy a custom chatbot"},
                {"id": "ai-agent-setup", "name": "AI Agent Setup", "description": "Set up an AI agent"},
                {"id": "workflow-automation", "name": "Workflow Automation", "description": "Create automated workflows"},
                {"id": "data-integration", "name": "Data Integration", "description": "Integrate data sources"}
            ]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.mcp_server_url}/workflows",
                    params={"n8n_url": self.n8n_url, "api_key": self.n8n_api_key},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    workflows = response.json()
                    logger.info(f"Retrieved {len(workflows)} available workflows")
                    return workflows
                else:
                    logger.error(f"Failed to list workflows: {response.status_code}")
                    return []
        except Exception as e:
            logger.error(f"Failed to list workflows via MCP: {e}")
            return []
    
    async def deploy_service(self, service_type: str, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Deploy a service (chatbot, AI agent, etc.) via workflow."""
        if self.mock_mode:
            logger.info(f"Mock: Deploying {service_type} service")
            return {
                "deployment_id": f"mock-deploy-{service_type}-123",
                "service_type": service_type,
                "status": "deploying",
                "config": config,
                "estimated_completion": "5 minutes"
            }
        
        try:
            workflow_name = f"{service_type}-deployment"
            deployment_data = {
                "service_type": service_type,
                "config": config,
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
            result = await self.trigger_workflow(workflow_name, deployment_data)
            if result:
                logger.info(f"Started deployment of {service_type} service")
                return {
                    "deployment_id": result["execution_id"],
                    "service_type": service_type,
                    "status": "deploying",
                    "workflow_id": result["workflow_id"]
                }
            return None
        except Exception as e:
            logger.error(f"Failed to deploy {service_type} service: {e}")
            return None
    
    async def deploy_service_via_n8n_mcp(self, service_type: str, config: Dict[str, Any], n8n_mcp_agent) -> Optional[Dict[str, Any]]:
        """Deploy a service using the dedicated n8n MCP agent."""
        try:
            logger.info(f"Deploying {service_type} service via n8n MCP agent")
            
            # Generate workflow configuration based on service type
            workflow_config = self._generate_service_workflow(service_type, config)
            
            # Use the n8n MCP agent to create the workflow
            result = await n8n_mcp_agent.create_workflow_via_mcp(workflow_config)
            
            if result.get("status") == "success":
                return {
                    "deployment_id": result["workflow"].get("id", f"mcp-{service_type}-{hash(str(config))}"),
                    "service_type": service_type,
                    "status": "deployed",
                    "config": config,
                    "workflow_id": result["workflow"].get("id"),
                    "created_via": "n8n_mcp_agent"
                }
            else:
                logger.error(f"Failed to deploy via n8n MCP: {result.get('error')}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to deploy {service_type} service via n8n MCP: {e}")
            return None
    
    def _generate_service_workflow(self, service_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate n8n workflow configuration for a specific service type."""
        base_workflow = {
            "name": f"{service_type.replace('_', ' ').title()} Service",
            "active": True,
            "nodes": [],
            "connections": {},
            "settings": {
                "executionOrder": "v1"
            },
            "staticData": {},
            "tags": [service_type, "auto-generated"],
            "triggerCount": 0,
            "updatedAt": "2024-01-01T00:00:00.000Z",
            "versionId": "1"
        }
        
        if service_type == "chatbot":
            base_workflow["nodes"] = [
                {
                    "parameters": {
                        "path": f"chatbot/{config.get('customer_id', 'default')}",
                        "options": {}
                    },
                    "id": "webhook-trigger",
                    "name": "Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [240, 300],
                    "webhookId": f"chatbot-{config.get('customer_id', 'default')}"
                },
                {
                    "parameters": {
                        "model": "gpt-3.5-turbo",
                        "messages": {
                            "messageValues": [
                                {
                                    "role": "system",
                                    "message": config.get("system_prompt", "You are a helpful AI assistant.")
                                },
                                {
                                    "role": "user", 
                                    "message": "={{ $json.body.message }}"
                                }
                            ]
                        }
                    },
                    "id": "openai-chat",
                    "name": "OpenAI Chat Model",
                    "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
                    "typeVersion": 1,
                    "position": [460, 300]
                },
                {
                    "parameters": {
                        "respondWith": "json",
                        "responseBody": {
                            "response": "={{ $json.response }}",
                            "timestamp": "={{ $now }}",
                            "customer_id": config.get("customer_id", "default")
                        }
                    },
                    "id": "respond-to-webhook",
                    "name": "Respond to Webhook",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "typeVersion": 1,
                    "position": [680, 300]
                }
            ]
            
            base_workflow["connections"] = {
                "Webhook": {
                    "main": [
                        [
                            {
                                "node": "OpenAI Chat Model",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                "OpenAI Chat Model": {
                    "main": [
                        [
                            {
                                "node": "Respond to Webhook",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                }
            }
            
        elif service_type == "ai_agent":
            base_workflow["nodes"] = [
                {
                    "parameters": {
                        "path": f"agent/{config.get('customer_id', 'default')}",
                        "options": {}
                    },
                    "id": "webhook-trigger",
                    "name": "Agent Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [240, 300]
                },
                {
                    "parameters": {
                        "jsCode": f"""
// AI Agent Logic for {config.get('customer_id', 'default')}
const userMessage = $input.first().json.body.message;
const context = $input.first().json.body.context || {{}};

// Process the message based on configuration
const response = {{
    message: `AI Agent Response: ${{userMessage}}`,
    agent_type: '{service_type}',
    customer_id: '{config.get('customer_id', 'default')}',
    timestamp: new Date().toISOString(),
    context: context
}};

return response;
"""
                    },
                    "id": "agent-logic",
                    "name": "Agent Logic",
                    "type": "n8n-nodes-base.code",
                    "typeVersion": 2,
                    "position": [460, 300]
                },
                {
                    "parameters": {
                        "respondWith": "json",
                        "responseBody": "={{ $json }}"
                    },
                    "id": "respond-to-webhook",
                    "name": "Respond to Webhook",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "typeVersion": 1,
                    "position": [680, 300]
                }
            ]
            
            base_workflow["connections"] = {
                "Agent Webhook": {
                    "main": [
                        [
                            {
                                "node": "Agent Logic",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                "Agent Logic": {
                    "main": [
                        [
                            {
                                "node": "Respond to Webhook",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                }
            }
            
        elif service_type == "workflow_automation":
            base_workflow["nodes"] = [
                {
                    "parameters": {
                        "rule": {
                            "interval": [
                                {
                                    "field": "cronExpression",
                                    "expression": config.get("schedule", "0 9 * * *")
                                }
                            ]
                        }
                    },
                    "id": "schedule-trigger",
                    "name": "Schedule Trigger",
                    "type": "n8n-nodes-base.scheduleTrigger",
                    "typeVersion": 1,
                    "position": [240, 300]
                },
                {
                    "parameters": {
                        "jsCode": f"""
// Workflow Automation Logic
const automationConfig = {json.dumps(config)};

// Execute automation based on configuration
const result = {{
    automation_type: '{service_type}',
    customer_id: '{config.get('customer_id', 'default')}',
    executed_at: new Date().toISOString(),
    config: automationConfig,
    status: 'completed'
}};

return result;
"""
                    },
                    "id": "automation-logic",
                    "name": "Automation Logic",
                    "type": "n8n-nodes-base.code",
                    "typeVersion": 2,
                    "position": [460, 300]
                }
            ]
            
            base_workflow["connections"] = {
                "Schedule Trigger": {
                    "main": [
                        [
                            {
                                "node": "Automation Logic",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                }
            }
        
        return base_workflow