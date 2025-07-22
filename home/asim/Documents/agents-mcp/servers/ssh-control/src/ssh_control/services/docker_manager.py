"""
Docker Manager for SSH Control MCP Server
Handles Docker operations on remote servers via SSH
"""

import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..utils.logger import Logger

class DockerManager:
    """Manages Docker operations on remote servers via SSH"""
    
    def __init__(self):
        self.ssh_manager = None  # Will be injected
    
    def set_ssh_manager(self, ssh_manager):
        """Set SSH manager reference"""
        self.ssh_manager = ssh_manager
    
    async def get_docker_status(self, connection_name: str = "vps") -> str:
        """Get comprehensive Docker status"""
        if not self.ssh_manager:
            return json.dumps({"error": "SSH manager not initialized"})
        
        commands = {
            "docker_version": "docker --version 2>/dev/null || echo 'Docker not installed'",
            "docker_info": "docker info --format json 2>/dev/null || echo '{}'",
            "containers": "docker ps -a --format json 2>/dev/null || echo '[]'",
            "images": "docker images --format json 2>/dev/null || echo '[]'",
            "networks": "docker network ls --format json 2>/dev/null || echo '[]'",
            "volumes": "docker volume ls --format json 2>/dev/null || echo '[]'",
            "compose_projects": "docker compose ls --format json 2>/dev/null || echo '[]'"
        }
        
        docker_data = {}
        for key, cmd in commands.items():
            result = await self.ssh_manager.execute_command(cmd, connection_name)
            if result.success:
                try:
                    # Try to parse JSON output
                    if key in ["docker_info", "containers", "images", "networks", "volumes", "compose_projects"]:
                        docker_data[key] = json.loads(result.stdout) if result.stdout.strip() else {}
                    else:
                        docker_data[key] = result.stdout.strip()
                except json.JSONDecodeError:
                    docker_data[key] = result.stdout.strip()
            else:
                docker_data[key] = f"Error: {result.stderr}"
        
        return json.dumps(docker_data, indent=2)
    
    async def install_docker(self, connection_name: str = "vps") -> Dict[str, Any]:
        """Install Docker with production-ready security configuration"""
        if not self.ssh_manager:
            return {"success": False, "error": "SSH manager not initialized"}
        
        try:
            Logger.info(f"Installing Docker with production security on {connection_name}")
            
            # Clean up any broken repositories first
            cleanup_result = await self.ssh_manager.execute_command("sudo rm -f /etc/apt/sources.list.d/docker.list", connection_name)
            
            # Update system
            update_result = await self.ssh_manager.execute_command("sudo apt-get update", connection_name, timeout=300)
            if not update_result.success:
                return {"success": False, "error": f"Failed to update system: {update_result.stderr}"}
            
            # Install prerequisites
            prereq_cmd = "sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release software-properties-common"
            prereq_result = await self.ssh_manager.execute_command(prereq_cmd, connection_name, timeout=300)
            if not prereq_result.success:
                return {"success": False, "error": f"Failed to install prerequisites: {prereq_result.stderr}"}
            
            # Add Docker GPG key
            gpg_cmd = "curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg"
            gpg_result = await self.ssh_manager.execute_command(gpg_cmd, connection_name, timeout=120)
            if not gpg_result.success:
                return {"success": False, "error": f"Failed to add Docker GPG key: {gpg_result.stderr}"}
            
            # Add Docker repository
            repo_cmd = 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null'
            repo_result = await self.ssh_manager.execute_command(repo_cmd, connection_name)
            if not repo_result.success:
                return {"success": False, "error": f"Failed to add Docker repository: {repo_result.stderr}"}
            
            # Update package lists again
            update2_result = await self.ssh_manager.execute_command("sudo apt-get update", connection_name, timeout=300)
            if not update2_result.success:
                return {"success": False, "error": f"Failed to update after adding repo: {update2_result.stderr}"}
            
            # Install Docker
            install_cmd = "sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin"
            install_result = await self.ssh_manager.execute_command(install_cmd, connection_name, timeout=600)
            if not install_result.success:
                return {"success": False, "error": f"Failed to install Docker: {install_result.stderr}"}
            
            # Create production Docker daemon configuration
            daemon_config = """{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": true,
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ],
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64000,
      "Soft": 64000
    }
  }
}"""
            
            # Create Docker config directory and daemon.json
            config_cmd = f"sudo mkdir -p /etc/docker && echo '{daemon_config}' | sudo tee /etc/docker/daemon.json"
            config_result = await self.ssh_manager.execute_command(config_cmd, connection_name)
            
            # Create Docker group
            group_result = await self.ssh_manager.execute_command("sudo groupadd docker || true", connection_name)
            
            # Start and enable Docker
            start_result = await self.ssh_manager.execute_command("sudo systemctl start docker && sudo systemctl enable docker", connection_name)
            if not start_result.success:
                return {"success": False, "error": f"Failed to start Docker service: {start_result.stderr}"}
            
            # Create directory structure for Docker applications
            dirs_cmd = "sudo mkdir -p /opt/docker-apps/{production,staging,development} /opt/docker-data /opt/docker-backups /opt/docker-configs /opt/docker-logs"
            dirs_result = await self.ssh_manager.execute_command(dirs_cmd, connection_name)
            
            # Set proper permissions
            perms_result = await self.ssh_manager.execute_command("sudo chown -R root:docker /opt/docker-apps && sudo chmod -R 755 /opt/docker-apps", connection_name)
            
            # Create Docker maintenance script
            maintenance_script = """#!/bin/bash
# Docker Maintenance Script
echo "🧹 Docker System Maintenance - $(date)"
echo "====================================="

echo "📊 Before cleanup:"
docker system df

echo ""
echo "🗑️ Cleaning up unused Docker resources..."

# Remove unused containers
echo "Removing stopped containers..."
docker container prune -f

# Remove unused images
echo "Removing unused images..."
docker image prune -f

# Remove unused volumes
echo "Removing unused volumes..."
docker volume prune -f

# Remove unused networks
echo "Removing unused networks..."
docker network prune -f

echo ""
echo "📊 After cleanup:"
docker system df

echo ""
echo "🔍 Current Docker status:"
docker ps -a
echo ""
docker images

echo "====================================="
echo "✅ Docker maintenance completed!"
"""
            
            # Install maintenance script
            maintenance_cmd = f"echo '{maintenance_script}' | sudo tee /usr/local/bin/docker-maintenance.sh && sudo chmod +x /usr/local/bin/docker-maintenance.sh"
            maintenance_result = await self.ssh_manager.execute_command(maintenance_cmd, connection_name)
            
            # Create Docker security check script
            security_script = """#!/bin/bash
# Docker Security Status Check
echo "🛡️ Docker Security Status Check - $(date)"
echo "=================================="

echo "📊 Docker System Info:"
docker system info | grep -E "(Security Options|Kernel Version|Operating System|Architecture)"

echo ""
echo "🔒 Docker Daemon Configuration:"
if [ -f /etc/docker/daemon.json ]; then
    echo "✅ Custom daemon.json exists"
    cat /etc/docker/daemon.json | jq . 2>/dev/null || cat /etc/docker/daemon.json
else
    echo "⚠️ No custom daemon.json found"
fi

echo ""
echo "🐳 Running Containers:"
docker ps --format "table {{.Names}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}"

echo ""
echo "💾 Docker Storage Usage:"
docker system df

echo "=================================="
"""
            
            # Install security check script
            security_cmd = f"echo '{security_script}' | sudo tee /usr/local/bin/docker-security-check.sh && sudo chmod +x /usr/local/bin/docker-security-check.sh"
            security_result = await self.ssh_manager.execute_command(security_cmd, connection_name)
            
            # Verify installation
            verify_result = await self.ssh_manager.execute_command("sudo docker --version && sudo docker compose version", connection_name)
            
            # Test Docker with hello-world
            test_result = await self.ssh_manager.execute_command("sudo docker run --rm hello-world", connection_name, timeout=120)
            
            if verify_result.success:
                return {
                    "success": True,
                    "docker_version": verify_result.stdout.strip(),
                    "test_successful": "Hello from Docker" in test_result.stdout if test_result.success else False,
                    "installation_steps": {
                        "cleanup": cleanup_result.success,
                        "update": update_result.success,
                        "prerequisites": prereq_result.success,
                        "gpg_key": gpg_result.success,
                        "repository": repo_result.success,
                        "install": install_result.success,
                        "security_config": config_result.success,
                        "service": start_result.success,
                        "directories": dirs_result.success,
                        "permissions": perms_result.success,
                        "maintenance_script": maintenance_result.success,
                        "security_script": security_result.success
                    },
                    "directories_created": [
                        "/opt/docker-apps/production",
                        "/opt/docker-apps/staging", 
                        "/opt/docker-apps/development",
                        "/opt/docker-data",
                        "/opt/docker-backups",
                        "/opt/docker-configs",
                        "/opt/docker-logs"
                    ],
                    "scripts_installed": [
                        "/usr/local/bin/docker-maintenance.sh",
                        "/usr/local/bin/docker-security-check.sh"
                    ],
                    "message": "Docker installed successfully with production security configuration"
                }
            else:
                return {"success": False, "error": "Docker installation verification failed"}
                
        except Exception as e:
            Logger.error(f"Docker installation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def list_containers(self, connection_name: str = "vps", all_containers: bool = True) -> Dict[str, Any]:
        """List Docker containers"""
        if not self.ssh_manager:
            return {"success": False, "error": "SSH manager not initialized"}
        
        cmd = "docker ps -a --format json" if all_containers else "docker ps --format json"
        result = await self.ssh_manager.execute_command(cmd, connection_name)
        
        if result.success:
            try:
                # Parse JSON lines
                containers = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        containers.append(json.loads(line))
                
                return {
                    "success": True,
                    "containers": containers,
                    "count": len(containers)
                }
            except json.JSONDecodeError as e:
                return {"success": False, "error": f"Failed to parse container list: {e}"}
        else:
            return {"success": False, "error": result.stderr}
    
    async def create_container(self, connection_name: str = "vps", **kwargs) -> Dict[str, Any]:
        """Create a new Docker container"""
        if not self.ssh_manager:
            return {"success": False, "error": "SSH manager not initialized"}
        
        # Build docker run command
        cmd_parts = ["docker", "run", "-d"]
        
        # Add common options
        if kwargs.get("name"):
            cmd_parts.extend(["--name", kwargs["name"]])
        
        if kwargs.get("ports"):
            for host_port, container_port in kwargs["ports"].items():
                cmd_parts.extend(["-p", f"{host_port}:{container_port}"])
        
        if kwargs.get("volumes"):
            for host_path, container_path in kwargs["volumes"].items():
                cmd_parts.extend(["-v", f"{host_path}:{container_path}"])
        
        if kwargs.get("environment"):
            for key, value in kwargs["environment"].items():
                cmd_parts.extend(["-e", f"{key}={value}"])
        
        if kwargs.get("network"):
            cmd_parts.extend(["--network", kwargs["network"]])
        
        if kwargs.get("restart"):
            cmd_parts.extend(["--restart", kwargs["restart"]])
        
        # Add image
        if not kwargs.get("image"):
            return {"success": False, "error": "Image name is required"}
        
        cmd_parts.append(kwargs["image"])
        
        # Add command if specified
        if kwargs.get("command"):
            cmd_parts.extend(kwargs["command"].split())
        
        cmd = " ".join(cmd_parts)
        result = await self.ssh_manager.execute_command(cmd, connection_name, timeout=300)
        
        if result.success:
            container_id = result.stdout.strip()
            return {
                "success": True,
                "container_id": container_id,
                "message": f"Container created successfully: {container_id[:12]}"
            }
        else:
            return {"success": False, "error": result.stderr}
    
    async def start_container(self, container_id: str, connection_name: str = "vps") -> Dict[str, Any]:
        """Start a Docker container"""
        if not self.ssh_manager:
            return {"success": False, "error": "SSH manager not initialized"}
        
        cmd = f"docker start {container_id}"
        result = await self.ssh_manager.execute_command(cmd, connection_name)
        
        if result.success:
            return {
                "success": True,
                "container_id": container_id,
                "message": f"Container started: {container_id}"
            }
        else:
            return {"success": False, "error": result.stderr}
    
    async def stop_container(self, container_id: str, connection_name: str = "vps") -> Dict[str, Any]:
        """Stop a Docker container"""
        if not self.ssh_manager:
            return {"success": False, "error": "SSH manager not initialized"}
        
        cmd = f"docker stop {container_id}"
        result = await self.ssh_manager.execute_command(cmd, connection_name, timeout=30)
        
        if result.success:
            return {
                "success": True,
                "container_id": container_id,
                "message": f"Container stopped: {container_id}"
            }
        else:
            return {"success": False, "error": result.stderr}
    
    async def remove_container(self, container_id: str, connection_name: str = "vps", force: bool = False) -> Dict[str, Any]:
        """Remove a Docker container"""
        if not self.ssh_manager:
            return {"success": False, "error": "SSH manager not initialized"}
        
        cmd = f"docker rm {'-f ' if force else ''}{container_id}"
        result = await self.ssh_manager.execute_command(cmd, connection_name)
        
        if result.success:
            return {
                "success": True,
                "container_id": container_id,
                "message": f"Container removed: {container_id}"
            }
        else:
            return {"success": False, "error": result.stderr}
    
    async def get_container_logs(self, container_id: str, connection_name: str = "vps", lines: int = 100) -> Dict[str, Any]:
        """Get container logs"""
        if not self.ssh_manager:
            return {"success": False, "error": "SSH manager not initialized"}
        
        cmd = f"docker logs --tail {lines} {container_id}"
        result = await self.ssh_manager.execute_command(cmd, connection_name)
        
        if result.success:
            return {
                "success": True,
                "container_id": container_id,
                "logs": result.stdout,
                "message": f"Retrieved {lines} lines of logs for {container_id}"
            }
        else:
            return {"success": False, "error": result.stderr}
    
    async def list_images(self, connection_name: str = "vps") -> Dict[str, Any]:
        """List Docker images"""
        if not self.ssh_manager:
            return {"success": False, "error": "SSH manager not initialized"}
        
        cmd = "docker images --format json"
        result = await self.ssh_manager.execute_command(cmd, connection_name)
        
        if result.success:
            try:
                images = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        images.append(json.loads(line))
                
                return {
                    "success": True,
                    "images": images,
                    "count": len(images)
                }
            except json.JSONDecodeError as e:
                return {"success": False, "error": f"Failed to parse image list: {e}"}
        else:
            return {"success": False, "error": result.stderr}
    
    async def pull_image(self, image_name: str, connection_name: str = "vps") -> Dict[str, Any]:
        """Pull Docker image"""
        if not self.ssh_manager:
            return {"success": False, "error": "SSH manager not initialized"}
        
        cmd = f"docker pull {image_name}"
        result = await self.ssh_manager.execute_command(cmd, connection_name, timeout=600)
        
        if result.success:
            return {
                "success": True,
                "image": image_name,
                "message": f"Successfully pulled image: {image_name}"
            }
        else:
            return {"success": False, "error": result.stderr}
    
    async def remove_image(self, image_id: str, connection_name: str = "vps", force: bool = False) -> Dict[str, Any]:
        """Remove Docker image"""
        if not self.ssh_manager:
            return {"success": False, "error": "SSH manager not initialized"}
        
        cmd = f"docker rmi {'-f ' if force else ''}{image_id}"
        result = await self.ssh_manager.execute_command(cmd, connection_name)
        
        if result.success:
            return {
                "success": True,
                "image_id": image_id,
                "message": f"Image removed: {image_id}"
            }
        else:
            return {"success": False, "error": result.stderr}
    
    async def list_networks(self, connection_name: str = "vps") -> Dict[str, Any]:
        """List Docker networks"""
        if not self.ssh_manager:
            return {"success": False, "error": "SSH manager not initialized"}
        
        cmd = "docker network ls --format json"
        result = await self.ssh_manager.execute_command(cmd, connection_name)
        
        if result.success:
            try:
                networks = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        networks.append(json.loads(line))
                
                return {
                    "success": True,
                    "networks": networks,
                    "count": len(networks)
                }
            except json.JSONDecodeError as e:
                return {"success": False, "error": f"Failed to parse network list: {e}"}
        else:
            return {"success": False, "error": result.stderr}
    
    async def create_network(self, network_name: str, connection_name: str = "vps", driver: str = "bridge") -> Dict[str, Any]:
        """Create Docker network"""
        if not self.ssh_manager:
            return {"success": False, "error": "SSH manager not initialized"}
        
        cmd = f"docker network create --driver {driver} {network_name}"
        result = await self.ssh_manager.execute_command(cmd, connection_name)
        
        if result.success:
            return {
                "success": True,
                "network_name": network_name,
                "network_id": result.stdout.strip(),
                "message": f"Network created: {network_name}"
            }
        else:
            return {"success": False, "error": result.stderr}
    
    async def remove_network(self, network_name: str, connection_name: str = "vps") -> Dict[str, Any]:
        """Remove Docker network"""
        if not self.ssh_manager:
            return {"success": False, "error": "SSH manager not initialized"}
        
        cmd = f"docker network rm {network_name}"
        result = await self.ssh_manager.execute_command(cmd, connection_name)
        
        if result.success:
            return {
                "success": True,
                "network_name": network_name,
                "message": f"Network removed: {network_name}"
            }
        else:
            return {"success": False, "error": result.stderr}
    
    async def list_volumes(self, connection_name: str = "vps") -> Dict[str, Any]:
        """List Docker volumes"""
        if not self.ssh_manager:
            return {"success": False, "error": "SSH manager not initialized"}
        
        cmd = "docker volume ls --format json"
        result = await self.ssh_manager.execute_command(cmd, connection_name)
        
        if result.success:
            try:
                volumes = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        volumes.append(json.loads(line))
                
                return {
                    "success": True,
                    "volumes": volumes,
                    "count": len(volumes)
                }
            except json.JSONDecodeError as e:
                return {"success": False, "error": f"Failed to parse volume list: {e}"}
        else:
            return {"success": False, "error": result.stderr}
    
    async def create_volume(self, volume_name: str, connection_name: str = "vps") -> Dict[str, Any]:
        """Create Docker volume"""
        if not self.ssh_manager:
            return {"success": False, "error": "SSH manager not initialized"}
        
        cmd = f"docker volume create {volume_name}"
        result = await self.ssh_manager.execute_command(cmd, connection_name)
        
        if result.success:
            return {
                "success": True,
                "volume_name": volume_name,
                "message": f"Volume created: {volume_name}"
            }
        else:
            return {"success": False, "error": result.stderr}
    
    async def remove_volume(self, volume_name: str, connection_name: str = "vps") -> Dict[str, Any]:
        """Remove Docker volume"""
        if not self.ssh_manager:
            return {"success": False, "error": "SSH manager not initialized"}
        
        cmd = f"docker volume rm {volume_name}"
        result = await self.ssh_manager.execute_command(cmd, connection_name)
        
        if result.success:
            return {
                "success": True,
                "volume_name": volume_name,
                "message": f"Volume removed: {volume_name}"
            }
        else:
            return {"success": False, "error": result.stderr}
    
    async def docker_compose_up(self, compose_file: str, connection_name: str = "vps", detach: bool = True) -> Dict[str, Any]:
        """Run docker compose up"""
        if not self.ssh_manager:
            return {"success": False, "error": "SSH manager not initialized"}
        
        cmd = f"docker compose -f {compose_file} up {'-d' if detach else ''}"
        result = await self.ssh_manager.execute_command(cmd, connection_name, timeout=600)
        
        if result.success:
            return {
                "success": True,
                "compose_file": compose_file,
                "output": result.stdout,
                "message": f"Docker Compose up completed for {compose_file}"
            }
        else:
            return {"success": False, "error": result.stderr}
    
    async def docker_compose_down(self, compose_file: str, connection_name: str = "vps") -> Dict[str, Any]:
        """Run docker compose down"""
        if not self.ssh_manager:
            return {"success": False, "error": "SSH manager not initialized"}
        
        cmd = f"docker compose -f {compose_file} down"
        result = await self.ssh_manager.execute_command(cmd, connection_name, timeout=300)
        
        if result.success:
            return {
                "success": True,
                "compose_file": compose_file,
                "output": result.stdout,
                "message": f"Docker Compose down completed for {compose_file}"
            }
        else:
            return {"success": False, "error": result.stderr}