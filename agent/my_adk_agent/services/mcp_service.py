"""
MCP Service - Model Context Protocol integration for n8n workflow automation
Handles communication with self-hosted n8n instance via MCP server
"""

import asyncio
import json
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MCPService:
    """
    Service for interacting with n8n via MCP (Model Context Protocol)
    Provides workflow creation, execution, and monitoring capabilities
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        # n8n MCP Server (Model Context Protocol)
        self.n8n_mcp_server_url = config.get("N8N_MCP_SERVER_URL", "http://localhost:3002")
        # n8n Server (Workflow Automation Platform)
        self.n8n_server_url = config.get("N8N_SERVER_URL", "http://localhost:5679")
        self.n8n_api_key = config.get("N8N_API_KEY")
        
        # HTTP client for API calls
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Content-Type": "application/json",
                "X-N8N-API-KEY": self.n8n_api_key
            } if self.n8n_api_key else {"Content-Type": "application/json"}
        )
    
    async def create_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new n8n workflow via MCP
        
        Args:
            workflow_data: Workflow configuration and nodes
            
        Returns:
            Creation result with workflow ID
        """
        try:
            # Prepare workflow payload for n8n
            n8n_workflow = {
                "name": workflow_data["name"],
                "active": True,
                "nodes": self._convert_template_to_nodes(
                    workflow_data["template_id"],
                    workflow_data.get("custom_config", {})
                ),
                "connections": self._generate_connections(workflow_data["template_id"]),
                "settings": {
                    "executionOrder": "v1"
                },
                "tags": [
                    {"name": f"customer_{workflow_data['customer_id']}"},
                    {"name": f"template_{workflow_data['template_id']}"}
                ]
            }
            
            # Create workflow via n8n Server API
            response = await self.client.post(
                f"{self.n8n_server_url}/api/v1/workflows",
                json=n8n_workflow
            )
            
            if response.status_code == 201:
                workflow_result = response.json()
                
                logger.info(f"Workflow created successfully: {workflow_result['id']}")
                
                return {
                    "success": True,
                    "workflow_id": workflow_result["id"],
                    "name": workflow_result["name"],
                    "active": workflow_result["active"],
                    "created_at": datetime.now().isoformat()
                }
            else:
                logger.error(f"Failed to create workflow: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Failed to create workflow: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute an existing n8n workflow
        
        Args:
            workflow_id: N8N workflow identifier
            input_data: Input data for workflow execution
            
        Returns:
            Execution result
        """
        try:
            # Prepare execution payload
            execution_payload = {
                "workflowData": {
                    "id": workflow_id
                }
            }
            
            if input_data:
                execution_payload["inputData"] = input_data
            
            # Execute workflow via n8n Server API
            response = await self.client.post(
                f"{self.n8n_server_url}/api/v1/workflows/{workflow_id}/execute",
                json=execution_payload
            )
            
            if response.status_code == 200:
                execution_result = response.json()
                
                logger.info(f"Workflow executed successfully: {execution_result.get('id')}")
                
                return {
                    "success": True,
                    "execution_id": execution_result.get("id"),
                    "status": "running",
                    "started_at": datetime.now().isoformat(),
                    "estimated_duration": "2-5 minutes"  # Default estimate
                }
            else:
                logger.error(f"Failed to execute workflow: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Failed to execute workflow: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get workflow status and recent executions
        
        Args:
            workflow_id: N8N workflow identifier
            
        Returns:
            Workflow status information
        """
        try:
            # Get workflow details
            workflow_response = await self.client.get(
                f"{self.n8n_server_url}/api/v1/workflows/{workflow_id}"
            )
            
            if workflow_response.status_code != 200:
                return {
                    "success": False,
                    "error": "Workflow not found"
                }
            
            workflow_data = workflow_response.json()
            
            # Get recent executions
            executions_response = await self.client.get(
                f"{self.n8n_server_url}/api/v1/executions",
                params={
                    "filter": json.dumps({"workflowId": workflow_id}),
                    "limit": 10
                }
            )
            
            executions_data = []
            if executions_response.status_code == 200:
                executions_data = executions_response.json().get("data", [])
            
            return {
                "success": True,
                "workflow": {
                    "id": workflow_data["id"],
                    "name": workflow_data["name"],
                    "active": workflow_data["active"],
                    "nodes_count": len(workflow_data.get("nodes", [])),
                    "updated_at": workflow_data.get("updatedAt")
                },
                "recent_executions": [
                    {
                        "id": exec_data["id"],
                        "status": exec_data.get("finished") and "success" or "running",
                        "started_at": exec_data.get("startedAt"),
                        "finished_at": exec_data.get("stoppedAt"),
                        "mode": exec_data.get("mode")
                    }
                    for exec_data in executions_data
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting workflow status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_workflow_metrics(self, workflow_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Get workflow performance metrics
        
        Args:
            workflow_id: N8N workflow identifier
            days: Number of days to analyze
            
        Returns:
            Performance metrics
        """
        try:
            # Get executions for the specified period
            executions_response = await self.client.get(
                f"{self.n8n_server_url}/api/v1/executions",
                params={
                    "filter": json.dumps({
                        "workflowId": workflow_id,
                        "startedAfter": (datetime.now() - timedelta(days=days)).isoformat()
                    }),
                    "limit": 1000
                }
            )
            
            if executions_response.status_code != 200:
                return {
                    "success": False,
                    "error": "Failed to fetch execution data"
                }
            
            executions = executions_response.json().get("data", [])
            
            # Calculate metrics
            total_executions = len(executions)
            successful_executions = sum(1 for exec in executions if exec.get("finished"))
            failed_executions = total_executions - successful_executions
            
            # Calculate average duration
            durations = []
            for exec in executions:
                if exec.get("startedAt") and exec.get("stoppedAt"):
                    start = datetime.fromisoformat(exec["startedAt"].replace("Z", "+00:00"))
                    stop = datetime.fromisoformat(exec["stoppedAt"].replace("Z", "+00:00"))
                    duration = (stop - start).total_seconds()
                    durations.append(duration)
            
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            return {
                "success": True,
                "metrics": {
                    "total_executions": total_executions,
                    "successful_executions": successful_executions,
                    "failed_executions": failed_executions,
                    "success_rate": successful_executions / total_executions if total_executions > 0 else 0,
                    "average_duration_seconds": avg_duration,
                    "period_days": days
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting workflow metrics: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _convert_template_to_nodes(self, template_id: str, custom_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert workflow template to n8n nodes"""
        
        # Template definitions with actual n8n node structures
        templates = {
            "email_automation": [
                {
                    "id": "start",
                    "name": "Start",
                    "type": "n8n-nodes-base.start",
                    "position": [240, 300],
                    "parameters": {}
                },
                {
                    "id": "email_trigger",
                    "name": "Email Trigger",
                    "type": "n8n-nodes-base.emailReadImap",
                    "position": [460, 300],
                    "parameters": {
                        "host": custom_config.get("email_host", "imap.gmail.com"),
                        "port": 993,
                        "secure": True,
                        "user": custom_config.get("email_user", ""),
                        "password": custom_config.get("email_password", "")
                    }
                },
                {
                    "id": "send_response",
                    "name": "Send Response",
                    "type": "n8n-nodes-base.emailSend",
                    "position": [680, 300],
                    "parameters": {
                        "fromEmail": custom_config.get("from_email", ""),
                        "toEmail": "={{ $json.from }}",
                        "subject": "Re: {{ $json.subject }}",
                        "text": custom_config.get("response_template", "Thank you for your email.")
                    }
                }
            ],
            "data_processing": [
                {
                    "id": "start",
                    "name": "Start",
                    "type": "n8n-nodes-base.start",
                    "position": [240, 300],
                    "parameters": {}
                },
                {
                    "id": "http_request",
                    "name": "Fetch Data",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [460, 300],
                    "parameters": {
                        "url": custom_config.get("data_url", ""),
                        "method": "GET",
                        "responseFormat": "json"
                    }
                },
                {
                    "id": "data_transform",
                    "name": "Transform Data",
                    "type": "n8n-nodes-base.function",
                    "position": [680, 300],
                    "parameters": {
                        "functionCode": custom_config.get("transform_code", "return items;")
                    }
                },
                {
                    "id": "save_data",
                    "name": "Save to Database",
                    "type": "n8n-nodes-base.postgres",
                    "position": [900, 300],
                    "parameters": {
                        "host": custom_config.get("db_host", "localhost"),
                        "database": custom_config.get("db_name", ""),
                        "user": custom_config.get("db_user", ""),
                        "password": custom_config.get("db_password", ""),
                        "operation": "insert",
                        "table": custom_config.get("db_table", "data")
                    }
                }
            ],
            "notifications": [
                {
                    "id": "start",
                    "name": "Start",
                    "type": "n8n-nodes-base.start",
                    "position": [240, 300],
                    "parameters": {}
                },
                {
                    "id": "schedule",
                    "name": "Schedule",
                    "type": "n8n-nodes-base.cron",
                    "position": [460, 300],
                    "parameters": {
                        "triggerTimes": {
                            "item": [
                                {
                                    "mode": "everyMinute"
                                }
                            ]
                        }
                    }
                },
                {
                    "id": "check_condition",
                    "name": "Check Condition",
                    "type": "n8n-nodes-base.if",
                    "position": [680, 300],
                    "parameters": {
                        "conditions": {
                            "string": [
                                {
                                    "value1": custom_config.get("condition_field", "status"),
                                    "operation": "equal",
                                    "value2": custom_config.get("condition_value", "alert")
                                }
                            ]
                        }
                    }
                },
                {
                    "id": "send_notification",
                    "name": "Send Notification",
                    "type": "n8n-nodes-base.slack",
                    "position": [900, 300],
                    "parameters": {
                        "channel": custom_config.get("slack_channel", "#general"),
                        "text": custom_config.get("notification_message", "Alert triggered!")
                    }
                }
            ]
        }
        
        return templates.get(template_id, templates["notifications"])
    
    def _generate_connections(self, template_id: str) -> Dict[str, Any]:
        """Generate node connections for template"""
        
        connections = {
            "email_automation": {
                "Start": {
                    "main": [
                        [
                            {
                                "node": "Email Trigger",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                "Email Trigger": {
                    "main": [
                        [
                            {
                                "node": "Send Response",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                }
            },
            "data_processing": {
                "Start": {
                    "main": [
                        [
                            {
                                "node": "Fetch Data",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                "Fetch Data": {
                    "main": [
                        [
                            {
                                "node": "Transform Data",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                "Transform Data": {
                    "main": [
                        [
                            {
                                "node": "Save to Database",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                }
            },
            "notifications": {
                "Start": {
                    "main": [
                        [
                            {
                                "node": "Schedule",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                "Schedule": {
                    "main": [
                        [
                            {
                                "node": "Check Condition",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                "Check Condition": {
                    "main": [
                        [
                            {
                                "node": "Send Notification",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                }
            }
        }
        
        return connections.get(template_id, connections["notifications"])
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()