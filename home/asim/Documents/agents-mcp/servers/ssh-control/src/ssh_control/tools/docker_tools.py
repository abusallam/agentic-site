"""
Docker-related tools for the MCP server
"""

import json
from typing import Any, Dict
import mcp.types as types

def register_docker_tools(server, docker_manager):
    """Register Docker-related tools"""
    
    @server.call_tool()
    async def docker_install(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Install Docker on remote server"""
        connection_name = arguments.get("connection_name", "vps")
        
        try:
            result = await docker_manager.install_docker(connection_name)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def docker_status(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Get Docker status and information"""
        connection_name = arguments.get("connection_name", "vps")
        
        try:
            result = await docker_manager.get_docker_status(connection_name)
            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def docker_list_containers(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """List Docker containers"""
        connection_name = arguments.get("connection_name", "vps")
        all_containers = arguments.get("all", True)
        
        try:
            result = await docker_manager.list_containers(connection_name, all_containers)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def docker_create_container(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Create a new Docker container"""
        connection_name = arguments.get("connection_name", "vps")
        
        # Remove connection_name from kwargs before passing to docker_manager
        kwargs = {k: v for k, v in arguments.items() if k != "connection_name"}
        
        try:
            result = await docker_manager.create_container(connection_name, **kwargs)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def docker_start_container(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Start a Docker container"""
        container_id = arguments.get("container_id")
        connection_name = arguments.get("connection_name", "vps")
        
        if not container_id:
            return [types.TextContent(type="text", text="Error: Container ID is required")]
        
        try:
            result = await docker_manager.start_container(container_id, connection_name)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def docker_stop_container(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Stop a Docker container"""
        container_id = arguments.get("container_id")
        connection_name = arguments.get("connection_name", "vps")
        
        if not container_id:
            return [types.TextContent(type="text", text="Error: Container ID is required")]
        
        try:
            result = await docker_manager.stop_container(container_id, connection_name)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def docker_remove_container(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Remove a Docker container"""
        container_id = arguments.get("container_id")
        connection_name = arguments.get("connection_name", "vps")
        force = arguments.get("force", False)
        
        if not container_id:
            return [types.TextContent(type="text", text="Error: Container ID is required")]
        
        try:
            result = await docker_manager.remove_container(container_id, connection_name, force)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def docker_get_logs(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Get Docker container logs"""
        container_id = arguments.get("container_id")
        connection_name = arguments.get("connection_name", "vps")
        lines = arguments.get("lines", 100)
        
        if not container_id:
            return [types.TextContent(type="text", text="Error: Container ID is required")]
        
        try:
            result = await docker_manager.get_container_logs(container_id, connection_name, lines)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def docker_list_images(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """List Docker images"""
        connection_name = arguments.get("connection_name", "vps")
        
        try:
            result = await docker_manager.list_images(connection_name)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def docker_pull_image(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Pull Docker image"""
        image_name = arguments.get("image_name")
        connection_name = arguments.get("connection_name", "vps")
        
        if not image_name:
            return [types.TextContent(type="text", text="Error: Image name is required")]
        
        try:
            result = await docker_manager.pull_image(image_name, connection_name)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def docker_remove_image(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Remove Docker image"""
        image_id = arguments.get("image_id")
        connection_name = arguments.get("connection_name", "vps")
        force = arguments.get("force", False)
        
        if not image_id:
            return [types.TextContent(type="text", text="Error: Image ID is required")]
        
        try:
            result = await docker_manager.remove_image(image_id, connection_name, force)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def docker_list_networks(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """List Docker networks"""
        connection_name = arguments.get("connection_name", "vps")
        
        try:
            result = await docker_manager.list_networks(connection_name)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def docker_create_network(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Create Docker network"""
        network_name = arguments.get("network_name")
        connection_name = arguments.get("connection_name", "vps")
        driver = arguments.get("driver", "bridge")
        
        if not network_name:
            return [types.TextContent(type="text", text="Error: Network name is required")]
        
        try:
            result = await docker_manager.create_network(network_name, connection_name, driver)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def docker_remove_network(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Remove Docker network"""
        network_name = arguments.get("network_name")
        connection_name = arguments.get("connection_name", "vps")
        
        if not network_name:
            return [types.TextContent(type="text", text="Error: Network name is required")]
        
        try:
            result = await docker_manager.remove_network(network_name, connection_name)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def docker_list_volumes(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """List Docker volumes"""
        connection_name = arguments.get("connection_name", "vps")
        
        try:
            result = await docker_manager.list_volumes(connection_name)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def docker_create_volume(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Create Docker volume"""
        volume_name = arguments.get("volume_name")
        connection_name = arguments.get("connection_name", "vps")
        
        if not volume_name:
            return [types.TextContent(type="text", text="Error: Volume name is required")]
        
        try:
            result = await docker_manager.create_volume(volume_name, connection_name)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def docker_remove_volume(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Remove Docker volume"""
        volume_name = arguments.get("volume_name")
        connection_name = arguments.get("connection_name", "vps")
        
        if not volume_name:
            return [types.TextContent(type="text", text="Error: Volume name is required")]
        
        try:
            result = await docker_manager.remove_volume(volume_name, connection_name)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def docker_compose_up(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Run docker compose up"""
        compose_file = arguments.get("compose_file")
        connection_name = arguments.get("connection_name", "vps")
        detach = arguments.get("detach", True)
        
        if not compose_file:
            return [types.TextContent(type="text", text="Error: Compose file path is required")]
        
        try:
            result = await docker_manager.docker_compose_up(compose_file, connection_name, detach)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def docker_compose_down(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Run docker compose down"""
        compose_file = arguments.get("compose_file")
        connection_name = arguments.get("connection_name", "vps")
        
        if not compose_file:
            return [types.TextContent(type="text", text="Error: Compose file path is required")]
        
        try:
            result = await docker_manager.docker_compose_down(compose_file, connection_name)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    # Register all Docker tools with their schemas
    docker_tools = [
        {
            "name": "docker_install",
            "description": "Install Docker on remote server",
            "schema": {
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name"}
                }
            }
        },
        {
            "name": "docker_status",
            "description": "Get Docker status and comprehensive information",
            "schema": {
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name"}
                }
            }
        },
        {
            "name": "docker_list_containers",
            "description": "List Docker containers",
            "schema": {
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name"},
                    "all": {"type": "boolean", "description": "Show all containers (default: true)"}
                }
            }
        },
        {
            "name": "docker_create_container",
            "description": "Create a new Docker container",
            "schema": {
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name"},
                    "image": {"type": "string", "description": "Docker image name"},
                    "name": {"type": "string", "description": "Container name"},
                    "ports": {"type": "object", "description": "Port mappings (host:container)"},
                    "volumes": {"type": "object", "description": "Volume mappings (host:container)"},
                    "environment": {"type": "object", "description": "Environment variables"},
                    "network": {"type": "string", "description": "Network name"},
                    "restart": {"type": "string", "description": "Restart policy"},
                    "command": {"type": "string", "description": "Command to run"}
                },
                "required": ["image"]
            }
        },
        {
            "name": "docker_start_container",
            "description": "Start a Docker container",
            "schema": {
                "type": "object",
                "properties": {
                    "container_id": {"type": "string", "description": "Container ID or name"},
                    "connection_name": {"type": "string", "description": "SSH connection name"}
                },
                "required": ["container_id"]
            }
        },
        {
            "name": "docker_stop_container",
            "description": "Stop a Docker container",
            "schema": {
                "type": "object",
                "properties": {
                    "container_id": {"type": "string", "description": "Container ID or name"},
                    "connection_name": {"type": "string", "description": "SSH connection name"}
                },
                "required": ["container_id"]
            }
        },
        {
            "name": "docker_remove_container",
            "description": "Remove a Docker container",
            "schema": {
                "type": "object",
                "properties": {
                    "container_id": {"type": "string", "description": "Container ID or name"},
                    "connection_name": {"type": "string", "description": "SSH connection name"},
                    "force": {"type": "boolean", "description": "Force removal"}
                },
                "required": ["container_id"]
            }
        },
        {
            "name": "docker_get_logs",
            "description": "Get Docker container logs",
            "schema": {
                "type": "object",
                "properties": {
                    "container_id": {"type": "string", "description": "Container ID or name"},
                    "connection_name": {"type": "string", "description": "SSH connection name"},
                    "lines": {"type": "integer", "description": "Number of lines to retrieve"}
                },
                "required": ["container_id"]
            }
        },
        {
            "name": "docker_list_images",
            "description": "List Docker images",
            "schema": {
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name"}
                }
            }
        },
        {
            "name": "docker_pull_image",
            "description": "Pull Docker image from registry",
            "schema": {
                "type": "object",
                "properties": {
                    "image_name": {"type": "string", "description": "Image name to pull"},
                    "connection_name": {"type": "string", "description": "SSH connection name"}
                },
                "required": ["image_name"]
            }
        },
        {
            "name": "docker_remove_image",
            "description": "Remove Docker image",
            "schema": {
                "type": "object",
                "properties": {
                    "image_id": {"type": "string", "description": "Image ID or name"},
                    "connection_name": {"type": "string", "description": "SSH connection name"},
                    "force": {"type": "boolean", "description": "Force removal"}
                },
                "required": ["image_id"]
            }
        },
        {
            "name": "docker_list_networks",
            "description": "List Docker networks",
            "schema": {
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name"}
                }
            }
        },
        {
            "name": "docker_create_network",
            "description": "Create Docker network",
            "schema": {
                "type": "object",
                "properties": {
                    "network_name": {"type": "string", "description": "Network name"},
                    "connection_name": {"type": "string", "description": "SSH connection name"},
                    "driver": {"type": "string", "description": "Network driver (default: bridge)"}
                },
                "required": ["network_name"]
            }
        },
        {
            "name": "docker_remove_network",
            "description": "Remove Docker network",
            "schema": {
                "type": "object",
                "properties": {
                    "network_name": {"type": "string", "description": "Network name"},
                    "connection_name": {"type": "string", "description": "SSH connection name"}
                },
                "required": ["network_name"]
            }
        },
        {
            "name": "docker_list_volumes",
            "description": "List Docker volumes",
            "schema": {
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name"}
                }
            }
        },
        {
            "name": "docker_create_volume",
            "description": "Create Docker volume",
            "schema": {
                "type": "object",
                "properties": {
                    "volume_name": {"type": "string", "description": "Volume name"},
                    "connection_name": {"type": "string", "description": "SSH connection name"}
                },
                "required": ["volume_name"]
            }
        },
        {
            "name": "docker_remove_volume",
            "description": "Remove Docker volume",
            "schema": {
                "type": "object",
                "properties": {
                    "volume_name": {"type": "string", "description": "Volume name"},
                    "connection_name": {"type": "string", "description": "SSH connection name"}
                },
                "required": ["volume_name"]
            }
        },
        {
            "name": "docker_compose_up",
            "description": "Run docker compose up",
            "schema": {
                "type": "object",
                "properties": {
                    "compose_file": {"type": "string", "description": "Path to docker-compose.yml file"},
                    "connection_name": {"type": "string", "description": "SSH connection name"},
                    "detach": {"type": "boolean", "description": "Run in detached mode"}
                },
                "required": ["compose_file"]
            }
        },
        {
            "name": "docker_compose_down",
            "description": "Run docker compose down",
            "schema": {
                "type": "object",
                "properties": {
                    "compose_file": {"type": "string", "description": "Path to docker-compose.yml file"},
                    "connection_name": {"type": "string", "description": "SSH connection name"}
                },
                "required": ["compose_file"]
            }
        }
    ]
    
    # Add all tools to the server
    for tool_config in docker_tools:
        server.list_tools().append(
            types.Tool(
                name=tool_config["name"],
                description=tool_config["description"],
                inputSchema=tool_config["schema"]
            )
        )