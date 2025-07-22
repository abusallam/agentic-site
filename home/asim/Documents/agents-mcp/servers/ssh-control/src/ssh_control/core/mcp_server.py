"""
Enhanced SSH Control MCP Server with Docker Integration
Main MCP server implementation combining SSH and Docker capabilities
"""

import asyncio
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

from ..services.ssh_connection_manager import SSHConnectionManager
from ..services.docker_manager import DockerManager
from ..config.server import SERVER_CONFIG
from ..utils.logger import Logger
from ..tools import register_all_tools

class SSHMCPServer:
    """Enhanced SSH MCP Server with Docker integration"""
    
    def __init__(self):
        self.server = Server(
            name=SERVER_CONFIG["name"],
            version=SERVER_CONFIG["version"]
        )
        self.ssh_manager = SSHConnectionManager()
        self.docker_manager = DockerManager()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up MCP request handlers"""
        
        @self.server.list_prompts()
        async def list_prompts() -> List[types.Prompt]:
            """List available prompts"""
            return [
                types.Prompt(
                    name="vps_security_setup",
                    description="Complete VPS security hardening and setup guide",
                    arguments=[
                        types.PromptArgument(
                            name="server_type",
                            description="Type of server setup (production, development, staging)",
                            required=False
                        )
                    ]
                ),
                types.Prompt(
                    name="docker_compose_deploy",
                    description="Deploy applications using Docker Compose with security best practices",
                    arguments=[
                        types.PromptArgument(
                            name="app_name",
                            description="Name of the application to deploy",
                            required=True
                        ),
                        types.PromptArgument(
                            name="services",
                            description="Description of services to deploy",
                            required=True
                        )
                    ]
                ),
                types.Prompt(
                    name="system_monitoring",
                    description="Set up comprehensive system monitoring and alerting",
                    arguments=[
                        types.PromptArgument(
                            name="monitoring_type",
                            description="Type of monitoring (basic, advanced, enterprise)",
                            required=False
                        )
                    ]
                )
            ]
        
        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: Dict[str, Any]) -> types.GetPromptResult:
            """Get prompt content"""
            if name == "vps_security_setup":
                return await self._get_security_setup_prompt(arguments)
            elif name == "docker_compose_deploy":
                return await self._get_docker_deploy_prompt(arguments)
            elif name == "system_monitoring":
                return await self._get_monitoring_prompt(arguments)
            else:
                raise ValueError(f"Unknown prompt: {name}")
        
        @self.server.list_resources()
        async def list_resources() -> List[types.Resource]:
            """List available resources"""
            resources = []
            
            # Add server status resources
            for connection_id in self.ssh_manager.get_active_connections():
                resources.extend([
                    types.Resource(
                        uri=f"ssh://{connection_id}/system-info",
                        name=f"System Info - {connection_id}",
                        description=f"Real-time system information for {connection_id}",
                        mimeType="application/json"
                    ),
                    types.Resource(
                        uri=f"ssh://{connection_id}/docker-status",
                        name=f"Docker Status - {connection_id}",
                        description=f"Docker containers and services status for {connection_id}",
                        mimeType="application/json"
                    ),
                    types.Resource(
                        uri=f"ssh://{connection_id}/security-status",
                        name=f"Security Status - {connection_id}",
                        description=f"Security configuration and status for {connection_id}",
                        mimeType="application/json"
                    )
                ])
            
            return resources
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read resource content"""
            if uri.startswith("ssh://"):
                parts = uri.replace("ssh://", "").split("/")
                connection_id = parts[0]
                resource_type = parts[1] if len(parts) > 1 else "system-info"
                
                if resource_type == "system-info":
                    return await self._get_system_info_resource(connection_id)
                elif resource_type == "docker-status":
                    return await self._get_docker_status_resource(connection_id)
                elif resource_type == "security-status":
                    return await self._get_security_status_resource(connection_id)
            
            raise ValueError(f"Unknown resource: {uri}")
        
        # Register all tools
        register_all_tools(self.server, self.ssh_manager, self.docker_manager)
    
    async def _get_security_setup_prompt(self, arguments: Dict[str, Any]) -> types.GetPromptResult:
        """Get VPS security setup prompt"""
        server_type = arguments.get("server_type", "production")
        
        content = f"""
# 🔒 VPS Security Setup Guide - {server_type.title()} Environment

## Phase 1: Initial Security Assessment
1. Connect to your VPS and assess current security status
2. Update system packages and install essential security tools
3. Review current user accounts and permissions

## Phase 2: User Management & SSH Security
1. Create non-root administrative user
2. Configure SSH key authentication
3. Disable root login and password authentication
4. Change SSH port from default (22)

## Phase 3: Firewall Configuration
1. Install and configure UFW (Uncomplicated Firewall)
2. Set default policies (deny incoming, allow outgoing)
3. Allow only necessary ports (SSH, HTTP, HTTPS)
4. Configure fail2ban for intrusion prevention

## Phase 4: Docker Security Setup
1. Install Docker with security best practices
2. Configure Docker daemon security settings
3. Set up Docker networks for application isolation
4. Implement container security policies

## Phase 5: Monitoring & Logging
1. Set up system monitoring (Prometheus/Grafana)
2. Configure log aggregation and analysis
3. Set up automated backup system
4. Implement security alerting

Use the SSH control tools to execute each step systematically.
"""
        
        return types.GetPromptResult(
            description=f"Complete VPS security setup for {server_type} environment",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=content)
                )
            ]
        )
    
    async def _get_docker_deploy_prompt(self, arguments: Dict[str, Any]) -> types.GetPromptResult:
        """Get Docker deployment prompt"""
        app_name = arguments.get("app_name", "myapp")
        services = arguments.get("services", "web application")
        
        content = f"""
# 🐳 Docker Compose Deployment: {app_name}

## Services to Deploy: {services}

## Deployment Plan:
1. **Prepare Environment**
   - Create application directory structure
   - Set up environment variables securely
   - Configure Docker networks

2. **Security Configuration**
   - Use non-root users in containers
   - Implement proper secrets management
   - Configure container resource limits

3. **Service Architecture**
   - Set up reverse proxy (Traefik/Nginx)
   - Configure SSL certificates (Let's Encrypt)
   - Implement health checks and monitoring

4. **Data Persistence**
   - Configure Docker volumes for data
   - Set up backup strategies
   - Implement database security

5. **Deployment & Testing**
   - Deploy services with docker-compose
   - Verify service connectivity
   - Test SSL certificates and security

Use the Docker management tools to implement this deployment plan.
"""
        
        return types.GetPromptResult(
            description=f"Docker Compose deployment guide for {app_name}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=content)
                )
            ]
        )
    
    async def _get_monitoring_prompt(self, arguments: Dict[str, Any]) -> types.GetPromptResult:
        """Get system monitoring setup prompt"""
        monitoring_type = arguments.get("monitoring_type", "basic")
        
        content = f"""
# 📊 System Monitoring Setup - {monitoring_type.title()} Level

## Monitoring Components:
1. **System Metrics**
   - CPU, Memory, Disk usage
   - Network traffic and connections
   - Process monitoring

2. **Application Monitoring**
   - Docker container health
   - Service availability checks
   - Application-specific metrics

3. **Security Monitoring**
   - Failed login attempts
   - Unusual network activity
   - File system changes

4. **Alerting System**
   - Email/SMS notifications
   - Threshold-based alerts
   - Incident response automation

## Implementation Steps:
1. Install monitoring stack (Prometheus, Grafana, AlertManager)
2. Configure data collection agents
3. Set up dashboards and visualizations
4. Configure alerting rules and notifications
5. Test monitoring and alert systems

Use the system monitoring tools to implement comprehensive observability.
"""
        
        return types.GetPromptResult(
            description=f"{monitoring_type.title()} system monitoring setup",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=content)
                )
            ]
        )
    
    async def _get_system_info_resource(self, connection_id: str) -> str:
        """Get system information resource"""
        try:
            system_info = await self.ssh_manager.get_system_info(connection_id)
            return system_info
        except Exception as e:
            Logger.error(f"Failed to get system info for {connection_id}: {e}")
            return f"Error retrieving system info: {str(e)}"
    
    async def _get_docker_status_resource(self, connection_id: str) -> str:
        """Get Docker status resource"""
        try:
            docker_status = await self.docker_manager.get_docker_status(connection_id)
            return docker_status
        except Exception as e:
            Logger.error(f"Failed to get Docker status for {connection_id}: {e}")
            return f"Error retrieving Docker status: {str(e)}"
    
    async def _get_security_status_resource(self, connection_id: str) -> str:
        """Get security status resource"""
        try:
            security_status = await self.ssh_manager.get_security_status(connection_id)
            return security_status
        except Exception as e:
            Logger.error(f"Failed to get security status for {connection_id}: {e}")
            return f"Error retrieving security status: {str(e)}"
    
    async def run(self):
        """Run the MCP server"""
        Logger.info("Starting Enhanced SSH Control MCP Server...")
        
        # Initialize connections
        await self.ssh_manager.initialize_default_connections()
        
        # Start the server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )