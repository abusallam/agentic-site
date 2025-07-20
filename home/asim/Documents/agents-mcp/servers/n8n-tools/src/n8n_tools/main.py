#!/usr/bin/env python3
"""
N8N MCP Server - Workflow automation tools
"""

import asyncio
import os
from typing import Any, Dict, List
from mcp.server import Server
import mcp.server.stdio
import mcp.types as types
import requests
import json

# Initialize the MCP server
server = Server("n8n-tools")

def get_n8n_config():
    """Get N8N configuration from environment."""
    base_url = os.getenv('N8N_BASE_URL', 'http://localhost:5678')
    api_key = os.getenv('N8N_API_KEY')
    
    if not api_key:
        raise ValueError("N8N_API_KEY environment variable is required")
    
    return {
        'base_url': base_url,
        'headers': {
            'X-N8N-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
    }

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="list_workflows",
            description="List all workflows in N8N",
            inputSchema={
                "type": "object",
                "properties": {
                    "active": {
                        "type": "boolean",
                        "description": "Filter by active status (optional)"
                    }
                }
            }
        ),
        types.Tool(
            name="get_workflow",
            description="Get details of a specific workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "Workflow ID"
                    }
                },
                "required": ["workflow_id"]
            }
        ),
        types.Tool(
            name="execute_workflow",
            description="Execute a workflow manually",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "Workflow ID to execute"
                    },
                    "data": {
                        "type": "object",
                        "description": "Input data for the workflow (optional)"
                    }
                },
                "required": ["workflow_id"]
            }
        ),
        types.Tool(
            name="get_executions",
            description="Get workflow execution history",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "Workflow ID (optional, gets all if not specified)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of executions to retrieve",
                        "default": 10
                    }
                }
            }
        ),
        types.Tool(
            name="activate_workflow",
            description="Activate or deactivate a workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "Workflow ID"
                    },
                    "active": {
                        "type": "boolean",
                        "description": "Set workflow active status"
                    }
                },
                "required": ["workflow_id", "active"]
            }
        ),
        types.Tool(
            name="create_webhook_workflow",
            description="Create a simple webhook workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Workflow name"
                    },
                    "webhook_path": {
                        "type": "string",
                        "description": "Webhook path (e.g., 'my-webhook')"
                    },
                    "response_data": {
                        "type": "object",
                        "description": "Data to return from webhook"
                    }
                },
                "required": ["name", "webhook_path"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """Handle tool calls."""
    
    try:
        config = get_n8n_config()
        base_url = config['base_url']
        headers = config['headers']
        
        if name == "list_workflows":
            active_filter = arguments.get("active")
            
            response = requests.get(f"{base_url}/api/v1/workflows", headers=headers)
            response.raise_for_status()
            
            workflows = response.json()['data']
            
            if active_filter is not None:
                workflows = [w for w in workflows if w['active'] == active_filter]
            
            workflow_list = []
            for workflow in workflows:
                status = "🟢 Active" if workflow['active'] else "🔴 Inactive"
                workflow_list.append(f"{workflow['id']} - {workflow['name']} ({status})")
            
            return [
                types.TextContent(
                    type="text",
                    text=f"N8N Workflows:\n\n" + "\n".join(workflow_list)
                )
            ]
        
        elif name == "get_workflow":
            workflow_id = arguments.get("workflow_id")
            
            response = requests.get(f"{base_url}/api/v1/workflows/{workflow_id}", headers=headers)
            response.raise_for_status()
            
            workflow = response.json()['data']
            
            info = f"""Workflow: {workflow['name']}
ID: {workflow['id']}
Active: {workflow['active']}
Created: {workflow.get('createdAt', 'Unknown')}
Updated: {workflow.get('updatedAt', 'Unknown')}
Nodes: {len(workflow.get('nodes', []))}
Connections: {len(workflow.get('connections', {}))}"""
            
            return [
                types.TextContent(
                    type="text",
                    text=info
                )
            ]
        
        elif name == "execute_workflow":
            workflow_id = arguments.get("workflow_id")
            data = arguments.get("data", {})
            
            payload = {"workflowData": data} if data else {}
            
            response = requests.post(
                f"{base_url}/api/v1/workflows/{workflow_id}/execute",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Workflow executed successfully. Execution ID: {result.get('data', {}).get('executionId', 'Unknown')}"
                )
            ]
        
        elif name == "get_executions":
            workflow_id = arguments.get("workflow_id")
            limit = arguments.get("limit", 10)
            
            url = f"{base_url}/api/v1/executions"
            params = {"limit": limit}
            if workflow_id:
                params["workflowId"] = workflow_id
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            executions = response.json()['data']
            
            execution_list = []
            for execution in executions:
                status = execution.get('finished', False)
                status_text = "✅ Success" if status else "❌ Failed"
                execution_list.append(f"{execution['id']} - {execution.get('workflowData', {}).get('name', 'Unknown')} ({status_text})")
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Recent Executions:\n\n" + "\n".join(execution_list)
                )
            ]
        
        elif name == "activate_workflow":
            workflow_id = arguments.get("workflow_id")
            active = arguments.get("active")
            
            response = requests.patch(
                f"{base_url}/api/v1/workflows/{workflow_id}",
                headers=headers,
                json={"active": active}
            )
            response.raise_for_status()
            
            status = "activated" if active else "deactivated"
            return [
                types.TextContent(
                    type="text",
                    text=f"Workflow {workflow_id} has been {status}"
                )
            ]
        
        elif name == "create_webhook_workflow":
            name = arguments.get("name")
            webhook_path = arguments.get("webhook_path")
            response_data = arguments.get("response_data", {"message": "Hello from N8N!"})
            
            workflow_data = {
                "name": name,
                "active": True,
                "nodes": [
                    {
                        "parameters": {
                            "path": webhook_path,
                            "options": {}
                        },
                        "id": "webhook-node",
                        "name": "Webhook",
                        "type": "n8n-nodes-base.webhook",
                        "typeVersion": 1,
                        "position": [250, 300]
                    },
                    {
                        "parameters": {
                            "respondWith": "json",
                            "responseBody": json.dumps(response_data)
                        },
                        "id": "respond-node",
                        "name": "Respond to Webhook",
                        "type": "n8n-nodes-base.respondToWebhook",
                        "typeVersion": 1,
                        "position": [450, 300]
                    }
                ],
                "connections": {
                    "Webhook": {
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
            }
            
            response = requests.post(
                f"{base_url}/api/v1/workflows",
                headers=headers,
                json=workflow_data
            )
            response.raise_for_status()
            
            workflow = response.json()['data']
            webhook_url = f"{base_url}/webhook/{webhook_path}"
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Created webhook workflow '{name}' (ID: {workflow['id']})\nWebhook URL: {webhook_url}"
                )
            ]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )
        ]

async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    asyncio.run(main())