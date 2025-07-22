"""
Tools registration for SSH Control MCP Server
"""

from .ssh_tools import register_ssh_tools
from .docker_tools import register_docker_tools
from .system_tools import register_system_tools

def register_all_tools(server, ssh_manager, docker_manager):
    """Register all available tools"""
    # Set up manager references
    docker_manager.set_ssh_manager(ssh_manager)
    
    # Register tool categories
    register_ssh_tools(server, ssh_manager)
    register_docker_tools(server, docker_manager)
    register_system_tools(server, ssh_manager)