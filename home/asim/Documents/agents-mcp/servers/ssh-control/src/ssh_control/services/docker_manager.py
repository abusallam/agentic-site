"""
Docker Manager for SSH Control MCP Server
Handles Docker operations on remote servers
"""

import json
from typing import Dict, Any
from ..utils.logger import Logger

class DockerManager:
    """Manages Docker operations on remote servers"""
    
    def __init__(self):
        self.ssh_manager = None
    
    def set_ssh_manager(self, ssh_manager):
        """Set SSH manager reference"""
        self.ssh_manager = ssh_manager
    
    async def get_docker_status(self, connection_name: str = "vps") -> str:
        """Get comprehensive Docker status information"""
        if not self.ssh_manager:
            return json.dumps({"error": "SSH manager not initialized"})
        
        commands = {
            "docker_version": "docker --version 2>/dev/null || echo 'Docker not installed'",
            "docker_info": "docker info --format '{{.ServerVersion}} | {{.Architecture}} | {{.OSType}}' 2>/dev/null || echo 'Docker not running'",
            "running_containers": "docker ps --format 'table {{.Names}}\\t{{.Status}}\\t{{.Ports}}' 2>/dev/null || echo 'No containers'",
            "all_containers": "docker ps -a --format 'table {{.Names}}\\t{{.Status}}\\t{{.Image}}' 2>/dev/null || echo 'No containers'",
            "images": "docker images --format 'table {{.Repository}}:{{.Tag}}\\t{{.Size}}\\t{{.CreatedAt}}' 2>/dev/null || echo 'No images'",
            "networks": "docker network ls --format 'table {{.Name}}\\t{{.Driver}}\\t{{.Scope}}' 2>/dev/null || echo 'No networks'",
            "volumes": "docker volume ls --format 'table {{.Name}}\\t{{.Driver}}' 2>/dev/null || echo 'No volumes'",
            "disk_usage": "docker system df 2>/dev/null || echo 'Docker not available'"
        }
        
        docker_data = {}
        for key, cmd in commands.items():
            result = await self.ssh_manager.execute_command(cmd, connection_name)
            if result.success:
                docker_data[key] = result.stdout.strip()
            else:
                docker_data[key] = f"Error: {result.stderr.strip()}"
        
        return json.dumps(docker_data, indent=2)
    
    async def list_containers(self, connection_name: str = "vps", all_containers: bool = False) -> str:
        """List Docker containers"""
        if not self.ssh_manager:
            return json.dumps({"error": "SSH manager not initialized"})
        
        cmd = "docker ps"
        if all_containers:
            cmd += " -a"
        cmd += " --format 'table {{.Names}}\\t{{.Status}}\\t{{.Image}}\\t{{.Ports}}\\t{{.CreatedAt}}'"
        
        result = await self.ssh_manager.execute_command(cmd, connection_name)
        
        if result.success:
            return result.stdout
        else:
            return f"Error listing containers: {result.stderr}"
    
    async def get_container_logs(self, connection_name: str, container_name: str, lines: int = 50, follow: bool = False) -> str:
        """Get Docker container logs"""
        if not self.ssh_manager:
            return "Error: SSH manager not initialized"
        
        cmd = f"docker logs --tail {lines}"
        if follow:
            cmd += " -f"
        cmd += f" {container_name}"
        
        # For follow mode, use shorter timeout
        timeout = 10 if follow else 30
        
        result = await self.ssh_manager.execute_command(cmd, connection_name, timeout=timeout)
        
        if result.success:
            return result.stdout
        else:
            return f"Error getting logs for {container_name}: {result.stderr}"
    
    async def start_container(self, connection_name: str, container_name: str) -> Dict[str, Any]:
        """Start Docker container"""
        if not self.ssh_manager:
            return {"success": False, "error": "SSH manager not initialized"}
        
        cmd = f"docker start {container_name}"
        result = await self.ssh_manager.execute_command(cmd, connection_name)
        
        if result.success:
            # Get container status after starting
            status_cmd = f"docker ps --filter name={container_name} --format '{{{{.Status}}}}'"
            status_result = await self.ssh_manager.execute_command(status_cmd, connection_name)
            
            return {
                "success": True,
                "container": container_name,
                "status": status_result.stdout.strip() if status_result.success else "Unknown",
                "message": f"Container {container_name} started successfully"
            }
        else:
            return {
                "success": False,
                "container": container_name,
                "error": result.stderr,
                "message": f"Failed to start container {container_name}"
            }
    
    async def stop_container(self, connection_name: str, container_name: str) -> Dict[str, Any]:
        """Stop Docker container"""
        if not self.ssh_manager:
            return {"success": False, "error": "SSH manager not initialized"}
        
        cmd = f"docker stop {container_name}"
        result = await self.ssh_manager.execute_command(cmd, connection_name)
        
        if result.success:
            return {
                "success": True,
                "container": container_name,
                "message": f"Container {container_name} stopped successfully"
            }
        else:
            return {
                "success": False,
                "container": container_name,
                "error": result.stderr,
                "message": f"Failed to stop container {container_name}"
            }
    
    async def restart_container(self, connection_name: str, container_name: str) -> Dict[str, Any]:
        """Restart Docker container"""
        if not self.ssh_manager:
            return {"success": False, "error": "SSH manager not initialized"}
        
        cmd = f"docker restart {container_name}"
        result = await self.ssh_manager.execute_command(cmd, connection_name)
        
        if result.success:
            # Get container status after restarting
            status_cmd = f"docker ps --filter name={container_name} --format '{{{{.Status}}}}'"
            status_result = await self.ssh_manager.execute_command(status_cmd, connection_name)
            
            return {
                "success": True,
                "container": container_name,
                "status": status_result.stdout.strip() if status_result.success else "Unknown",
                "message": f"Container {container_name} restarted successfully"
            }
        else:
            return {
                "success": False,
                "container": container_name,
                "error": result.stderr,
                "message": f"Failed to restart container {container_name}"
            }
    
    async def exec_container(self, connection_name: str, container_name: str, command: str) -> Dict[str, Any]:
        """Execute command in Docker container"""
        if not self.ssh_manager:
            return {"success": False, "error": "SSH manager not initialized"}
        
        cmd = f"docker exec {container_name} {command}"
        result = await self.ssh_manager.execute_command(cmd, connection_name)
        
        return {
            "success": result.success,
            "container": container_name,
            "command": command,
            "exit_code": result.exit_code,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "execution_time": result.execution_time
        }
    
    async def compose_up(self, connection_name: str, compose_file: str = "docker-compose.yml", detach: bool = True) -> Dict[str, Any]:
        """Start Docker Compose services"""
        if not self.ssh_manager:
            return {"success": False, "error": "SSH manager not initialized"}
        
        cmd = f"docker-compose -f {compose_file} up"
        if detach:
            cmd += " -d"
        
        result = await self.ssh_manager.execute_command(cmd, connection_name, timeout=120)
        
        if result.success:
            # Get service status
            status_cmd = f"docker-compose -f {compose_file} ps"
            status_result = await self.ssh_manager.execute_command(status_cmd, connection_name)
            
            return {
                "success": True,
                "compose_file": compose_file,
                "services_status": status_result.stdout if status_result.success else "Status unavailable",
                "message": f"Docker Compose services started from {compose_file}"
            }
        else:
            return {
                "success": False,
                "compose_file": compose_file,
                "error": result.stderr,
                "message": f"Failed to start Docker Compose services from {compose_file}"
            }
    
    async def compose_down(self, connection_name: str, compose_file: str = "docker-compose.yml") -> Dict[str, Any]:
        """Stop Docker Compose services"""
        if not self.ssh_manager:
            return {"success": False, "error": "SSH manager not initialized"}
        
        cmd = f"docker-compose -f {compose_file} down"
        result = await self.ssh_manager.execute_command(cmd, connection_name, timeout=60)
        
        if result.success:
            return {
                "success": True,
                "compose_file": compose_file,
                "message": f"Docker Compose services stopped from {compose_file}"
            }
        else:
            return {
                "success": False,
                "compose_file": compose_file,
                "error": result.stderr,
                "message": f"Failed to stop Docker Compose services from {compose_file}"
            }