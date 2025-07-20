#!/usr/bin/env python3
"""
Coolify MCP Server - Self-hosting platform management
"""

import asyncio
import os
from typing import Any, Dict, List
from mcp.server import Server
import mcp.server.stdio
import mcp.types as types
import requests

# Initialize the MCP server
server = Server("coolify-tools")

def get_coolify_config():
    """Get Coolify configuration from environment."""
    base_url = os.getenv('COOLIFY_BASE_URL', 'http://localhost:8000')
    api_token = os.getenv('COOLIFY_API_TOKEN')
    
    if not api_token:
        raise ValueError("COOLIFY_API_TOKEN environment variable is required")
    
    return {
        'base_url': base_url,
        'headers': {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    }

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="list_applications",
            description="List all applications in Coolify",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {
                        "type": "string",
                        "description": "Team ID to filter applications (optional)"
                    }
                }
            }
        ),
        types.Tool(
            name="get_application",
            description="Get details of a specific application",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_uuid": {
                        "type": "string",
                        "description": "Application UUID"
                    }
                },
                "required": ["app_uuid"]
            }
        ),
        types.Tool(
            name="deploy_application",
            description="Deploy an application",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_uuid": {
                        "type": "string",
                        "description": "Application UUID to deploy"
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Force deployment",
                        "default": False
                    }
                },
                "required": ["app_uuid"]
            }
        ),
        types.Tool(
            name="stop_application",
            description="Stop a running application",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_uuid": {
                        "type": "string",
                        "description": "Application UUID to stop"
                    }
                },
                "required": ["app_uuid"]
            }
        ),
        types.Tool(
            name="restart_application",
            description="Restart an application",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_uuid": {
                        "type": "string",
                        "description": "Application UUID to restart"
                    }
                },
                "required": ["app_uuid"]
            }
        ),
        types.Tool(
            name="list_servers",
            description="List all servers in Coolify",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="get_server_resources",
            description="Get server resource usage",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_uuid": {
                        "type": "string",
                        "description": "Server UUID"
                    }
                },
                "required": ["server_uuid"]
            }
        ),
        types.Tool(
            name="create_application",
            description="Create a new application from Git repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Application name"
                    },
                    "git_repository": {
                        "type": "string",
                        "description": "Git repository URL"
                    },
                    "git_branch": {
                        "type": "string",
                        "description": "Git branch",
                        "default": "main"
                    },
                    "server_uuid": {
                        "type": "string",
                        "description": "Server UUID to deploy on"
                    },
                    "project_uuid": {
                        "type": "string",
                        "description": "Project UUID"
                    }
                },
                "required": ["name", "git_repository", "server_uuid", "project_uuid"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """Handle tool calls."""
    
    try:
        config = get_coolify_config()
        base_url = config['base_url']
        headers = config['headers']
        
        if name == "list_applications":
            team_id = arguments.get("team_id")
            
            url = f"{base_url}/api/v1/applications"
            if team_id:
                url += f"?team_id={team_id}"
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            applications = response.json()
            
            app_list = []
            for app in applications:
                status = app.get('status', 'unknown')
                status_emoji = "🟢" if status == "running" else "🔴" if status == "stopped" else "🟡"
                app_list.append(f"{status_emoji} {app.get('name', 'Unknown')} - {app.get('uuid', 'No UUID')}")
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Coolify Applications:\n\n" + "\n".join(app_list)
                )
            ]
        
        elif name == "get_application":
            app_uuid = arguments.get("app_uuid")
            
            response = requests.get(f"{base_url}/api/v1/applications/{app_uuid}", headers=headers)
            response.raise_for_status()
            
            app = response.json()
            
            info = f"""Application: {app.get('name', 'Unknown')}
UUID: {app.get('uuid', 'Unknown')}
Status: {app.get('status', 'Unknown')}
Git Repository: {app.get('git_repository', 'Unknown')}
Git Branch: {app.get('git_branch', 'Unknown')}
Build Pack: {app.get('build_pack', 'Unknown')}
Domain: {app.get('fqdn', 'Not set')}
Created: {app.get('created_at', 'Unknown')}
Updated: {app.get('updated_at', 'Unknown')}"""
            
            return [
                types.TextContent(
                    type="text",
                    text=info
                )
            ]
        
        elif name == "deploy_application":
            app_uuid = arguments.get("app_uuid")
            force = arguments.get("force", False)
            
            payload = {"force_rebuild": force}
            
            response = requests.post(
                f"{base_url}/api/v1/applications/{app_uuid}/deploy",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Deployment started for application {app_uuid}. Deployment UUID: {result.get('uuid', 'Unknown')}"
                )
            ]
        
        elif name == "stop_application":
            app_uuid = arguments.get("app_uuid")
            
            response = requests.post(f"{base_url}/api/v1/applications/{app_uuid}/stop", headers=headers)
            response.raise_for_status()
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Application {app_uuid} has been stopped"
                )
            ]
        
        elif name == "restart_application":
            app_uuid = arguments.get("app_uuid")
            
            response = requests.post(f"{base_url}/api/v1/applications/{app_uuid}/restart", headers=headers)
            response.raise_for_status()
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Application {app_uuid} has been restarted"
                )
            ]
        
        elif name == "list_servers":
            response = requests.get(f"{base_url}/api/v1/servers", headers=headers)
            response.raise_for_status()
            
            servers = response.json()
            
            server_list = []
            for server in servers:
                status = "🟢 Online" if server.get('is_reachable', False) else "🔴 Offline"
                server_list.append(f"{server.get('name', 'Unknown')} - {server.get('ip', 'Unknown IP')} ({status})")
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Coolify Servers:\n\n" + "\n".join(server_list)
                )
            ]
        
        elif name == "get_server_resources":
            server_uuid = arguments.get("server_uuid")
            
            response = requests.get(f"{base_url}/api/v1/servers/{server_uuid}/resources", headers=headers)
            response.raise_for_status()
            
            resources = response.json()
            
            info = f"""Server Resources:
CPU Usage: {resources.get('cpu_usage', 'Unknown')}%
Memory Usage: {resources.get('memory_usage', 'Unknown')}%
Disk Usage: {resources.get('disk_usage', 'Unknown')}%
Load Average: {resources.get('load_average', 'Unknown')}
Uptime: {resources.get('uptime', 'Unknown')}"""
            
            return [
                types.TextContent(
                    type="text",
                    text=info
                )
            ]
        
        elif name == "create_application":
            name = arguments.get("name")
            git_repository = arguments.get("git_repository")
            git_branch = arguments.get("git_branch", "main")
            server_uuid = arguments.get("server_uuid")
            project_uuid = arguments.get("project_uuid")
            
            payload = {
                "name": name,
                "git_repository": git_repository,
                "git_branch": git_branch,
                "server_uuid": server_uuid,
                "project_uuid": project_uuid,
                "build_pack": "nixpacks"
            }
            
            response = requests.post(
                f"{base_url}/api/v1/applications",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            app = response.json()
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Created application '{name}' (UUID: {app.get('uuid', 'Unknown')})"
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