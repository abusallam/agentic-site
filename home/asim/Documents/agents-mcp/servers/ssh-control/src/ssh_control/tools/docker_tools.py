"""
Docker-related tools for the MCP server
"""

import json
from typing import Any, Dict
import mcp.types as types

def register_docker_tools(server, ssh_manager, docker_manager):
    """Register Docker-related tools"""
    # Set SSH manager reference in docker manager
    docker_manager.set_ssh_manager(ssh_manager)
    
    @server.call_tool()
    async def docker_status(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Get Docker system status"""
        connection_name = arguments.get("connection_name", "vps")
        
        try:
            result = await docker_manager.get_docker_status(connection_name)
            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def docker_ps(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """List Docker containers"""
        connection_name = arguments.get("connection_name", "vps")
        all_containers = arguments.get("all", False)
        
        try:
            result = await docker_manager.list_containers(connection_name, all_containers)
            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def docker_logs(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Get Docker container logs"""
        connection_name = arguments.get("connection_name", "vps")
        container_name = arguments.get("container_name")
        lines = arguments.get("lines", 50)
        follow = arguments.get("follow", False)
        
        if not container_name:
            return [types.TextContent(type="text", text="Error: container_name is required")]
        
        try:
            result = await docker_manager.get_container_logs(connection_name, container_name, lines, follow)
            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def docker_start(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Start Docker container"""
        connection_name = arguments.get("connection_name", "vps")
        container_name = arguments.get("container_name")
        
        if not container_name:
            return [types.TextContent(type="text", text="Error: container_name is required")]
        
        try:
            result = await docker_manager.start_container(connection_name, container_name)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def docker_stop(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Stop Docker container"""
        connection_name = arguments.get("connection_name", "vps")
        container_name = arguments.get("container_name")
        
        if not container_name:
            return [types.TextContent(type="text", text="Error: container_name is required")]
        
        try:
            result = await docker_manager.stop_container(connection_name, container_name)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def docker_restart(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Restart Docker container"""
        connection_name = arguments.get("connection_name", "vps")
        container_name = arguments.get("container_name")
        
        if not container_name:
            return [types.TextContent(type="text", text="Error: container_name is required")]
        
        try:
            result = await docker_manager.restart_container(connection_name, container_name)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def docker_exec(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Execute command in Docker container"""
        connection_name = arguments.get("connection_name", "vps")
        container_name = arguments.get("container_name")
        command = arguments.get("command")
        
        if not container_name or not command:
            return [types.TextContent(type="text", text="Error: container_name and command are required")]
        
        try:
            result = await docker_manager.exec_container(connection_name, container_name, command)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def docker_compose_up(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Start Docker Compose services"""
        connection_name = arguments.get("connection_name", "vps")
        compose_file = arguments.get("compose_file", "docker-compose.yml")
        detach = arguments.get("detach", True)
        
        try:
            result = await docker_manager.compose_up(connection_name, compose_file, detach)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def docker_compose_down(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Stop Docker Compose services"""
        connection_name = arguments.get("connection_name", "vps")
        compose_file = arguments.get("compose_file", "docker-compose.yml")
        
        try:
            result = await docker_manager.compose_down(connection_name, compose_file)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    # Register Docker tools
    docker_tools = [
        types.Tool(
            name="docker_status",
            description="Get Docker system status and information",
            inputSchema={
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name (default: vps)"}
                }
            }
        ),
        types.Tool(
            name="docker_ps",
            description="List Docker containers",
            inputSchema={
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name (default: vps)"},
                    "all": {"type": "boolean", "description": "Show all containers including stopped ones"}
                }
            }
        ),
        types.Tool(
            name="docker_logs",
            description="Get Docker container logs",
            inputSchema={
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name (default: vps)"},
                    "container_name": {"type": "string", "description": "Container name or ID"},
                    "lines": {"type": "integer", "description": "Number of lines to show (default: 50)"},
                    "follow": {"type": "boolean", "description": "Follow log output"}
                },
                "required": ["container_name"]
            }
        ),
        types.Tool(
            name="docker_start",
            description="Start Docker container",
            inputSchema={
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name (default: vps)"},
                    "container_name": {"type": "string", "description": "Container name or ID"}
                },
                "required": ["container_name"]
            }
        ),
        types.Tool(
            name="docker_stop",
            description="Stop Docker container",
            inputSchema={
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name (default: vps)"},
                    "container_name": {"type": "string", "description": "Container name or ID"}
                },
                "required": ["container_name"]
            }
        ),
        types.Tool(
            name="docker_restart",
            description="Restart Docker container",
            inputSchema={
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name (default: vps)"},
                    "container_name": {"type": "string", "description": "Container name or ID"}
                },
                "required": ["container_name"]
            }
        ),
        types.Tool(
            name="docker_exec",
            description="Execute command in Docker container",
            inputSchema={
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name (default: vps)"},
                    "container_name": {"type": "string", "description": "Container name or ID"},
                    "command": {"type": "string", "description": "Command to execute"}
                },
                "required": ["container_name", "command"]
            }
        ),
        types.Tool(
            name="docker_compose_up",
            description="Start Docker Compose services",
            inputSchema={
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name (default: vps)"},
                    "compose_file": {"type": "string", "description": "Docker Compose file path (default: docker-compose.yml)"},
                    "detach": {"type": "boolean", "description": "Run in detached mode (default: true)"}
                }
            }
        ),
        types.Tool(
            name="docker_compose_down",
            description="Stop Docker Compose services",
            inputSchema={
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name (default: vps)"},
                    "compose_file": {"type": "string", "description": "Docker Compose file path (default: docker-compose.yml)"}
                }
            }
        )
    ]
    
    for tool in docker_tools:
        server.list_tools().append(tool)