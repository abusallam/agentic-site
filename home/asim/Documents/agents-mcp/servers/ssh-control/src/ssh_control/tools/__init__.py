"""
Tools registration for SSH Control MCP Server
"""

from .ssh_tools import register_ssh_tools
from .docker_tools import register_docker_tools
from .system_tools import register_system_tools
from .deployment_tools import register_deployment_tools

def register_all_tools(server, ssh_manager, docker_manager):
    """Register all tools with the MCP server"""
    register_ssh_tools(server, ssh_manager)
    register_docker_tools(server, ssh_manager, docker_manager)
    register_system_tools(server, ssh_manager)
    register_deployment_tools(server, ssh_manager, docker_manager)