"""
SSH-related tools for the MCP server
"""

import json
from typing import Any, Dict
import mcp.types as types

def register_ssh_tools(server, ssh_manager):
    """Register SSH-related tools"""
    
    @server.call_tool()
    async def ssh_connect(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Connect to SSH server"""
        connection_name = arguments.get("connection_name", "vps")
        
        try:
            result = await ssh_manager.connect(connection_name)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def ssh_disconnect(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Disconnect from SSH server"""
        connection_name = arguments.get("connection_name", "vps")
        
        try:
            result = await ssh_manager.disconnect(connection_name)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def ssh_execute(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Execute command on remote server"""
        command = arguments.get("command")
        connection_name = arguments.get("connection_name", "vps")
        timeout = arguments.get("timeout", 60)
        
        if not command:
            return [types.TextContent(type="text", text="Error: Command is required")]
        
        try:
            result = await ssh_manager.execute_command(command, connection_name, timeout)
            return [types.TextContent(type="text", text=json.dumps(result.dict(), indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def ssh_upload_file(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Upload file to remote server"""
        local_path = arguments.get("local_path")
        remote_path = arguments.get("remote_path")
        connection_name = arguments.get("connection_name", "vps")
        
        if not local_path or not remote_path:
            return [types.TextContent(type="text", text="Error: Both local_path and remote_path are required")]
        
        try:
            result = await ssh_manager.upload_file(local_path, remote_path, connection_name)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def ssh_download_file(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Download file from remote server"""
        remote_path = arguments.get("remote_path")
        local_path = arguments.get("local_path")
        connection_name = arguments.get("connection_name", "vps")
        
        if not remote_path or not local_path:
            return [types.TextContent(type="text", text="Error: Both remote_path and local_path are required")]
        
        try:
            result = await ssh_manager.download_file(remote_path, local_path, connection_name)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def ssh_install_package(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Install package on remote server"""
        package_name = arguments.get("package_name")
        connection_name = arguments.get("connection_name", "vps")
        
        if not package_name:
            return [types.TextContent(type="text", text="Error: Package name is required")]
        
        try:
            result = await ssh_manager.install_package(package_name, connection_name)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def ssh_get_system_info(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Get system information from remote server"""
        connection_name = arguments.get("connection_name", "vps")
        
        try:
            result = await ssh_manager.get_system_info(connection_name)
            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def ssh_get_security_status(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Get security status from remote server"""
        connection_name = arguments.get("connection_name", "vps")
        
        try:
            result = await ssh_manager.get_security_status(connection_name)
            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def ssh_list_connections(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """List all SSH connection statuses"""
        try:
            statuses = await ssh_manager.get_connection_status()
            result = [status.dict() for status in statuses]
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    # Register tools with the server
    server.list_tools().append(
        types.Tool(
            name="ssh_connect",
            description="Connect to SSH server",
            inputSchema={
                "type": "object",
                "properties": {
                    "connection_name": {
                        "type": "string",
                        "description": "Name of the connection (default: vps)"
                    }
                }
            }
        )
    )
    
    server.list_tools().append(
        types.Tool(
            name="ssh_disconnect",
            description="Disconnect from SSH server",
            inputSchema={
                "type": "object",
                "properties": {
                    "connection_name": {
                        "type": "string",
                        "description": "Name of the connection (default: vps)"
                    }
                }
            }
        )
    )
    
    server.list_tools().append(
        types.Tool(
            name="ssh_execute",
            description="Execute command on remote server",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Command to execute"
                    },
                    "connection_name": {
                        "type": "string",
                        "description": "Name of the connection (default: vps)"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Command timeout in seconds (default: 60)"
                    }
                },
                "required": ["command"]
            }
        )
    )
    
    server.list_tools().append(
        types.Tool(
            name="ssh_upload_file",
            description="Upload file to remote server",
            inputSchema={
                "type": "object",
                "properties": {
                    "local_path": {
                        "type": "string",
                        "description": "Local file path"
                    },
                    "remote_path": {
                        "type": "string",
                        "description": "Remote file path"
                    },
                    "connection_name": {
                        "type": "string",
                        "description": "Name of the connection (default: vps)"
                    }
                },
                "required": ["local_path", "remote_path"]
            }
        )
    )
    
    server.list_tools().append(
        types.Tool(
            name="ssh_download_file",
            description="Download file from remote server",
            inputSchema={
                "type": "object",
                "properties": {
                    "remote_path": {
                        "type": "string",
                        "description": "Remote file path"
                    },
                    "local_path": {
                        "type": "string",
                        "description": "Local file path"
                    },
                    "connection_name": {
                        "type": "string",
                        "description": "Name of the connection (default: vps)"
                    }
                },
                "required": ["remote_path", "local_path"]
            }
        )
    )
    
    server.list_tools().append(
        types.Tool(
            name="ssh_install_package",
            description="Install package on remote server using apt",
            inputSchema={
                "type": "object",
                "properties": {
                    "package_name": {
                        "type": "string",
                        "description": "Name of the package to install"
                    },
                    "connection_name": {
                        "type": "string",
                        "description": "Name of the connection (default: vps)"
                    }
                },
                "required": ["package_name"]
            }
        )
    )
    
    server.list_tools().append(
        types.Tool(
            name="ssh_get_system_info",
            description="Get comprehensive system information",
            inputSchema={
                "type": "object",
                "properties": {
                    "connection_name": {
                        "type": "string",
                        "description": "Name of the connection (default: vps)"
                    }
                }
            }
        )
    )
    
    server.list_tools().append(
        types.Tool(
            name="ssh_get_security_status",
            description="Get security configuration and status",
            inputSchema={
                "type": "object",
                "properties": {
                    "connection_name": {
                        "type": "string",
                        "description": "Name of the connection (default: vps)"
                    }
                }
            }
        )
    )
    
    server.list_tools().append(
        types.Tool(
            name="ssh_list_connections",
            description="List all SSH connection statuses",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    )