"""
SSH Connection Manager
Handles SSH connections and command execution
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any
import paramiko
from datetime import datetime
import os
from dotenv import load_dotenv

from ..models.types import SSHConfig, CommandResult, SystemInfo, ServerStatus
from ..utils.logger import Logger
from ..config.server import DEFAULT_SSH_CONFIGS

# Load environment variables
load_dotenv()

class SSHConnectionManager:
    """Manages SSH connections and operations"""
    
    def __init__(self):
        self.connections: Dict[str, paramiko.SSHClient] = {}
        self.configs: Dict[str, SSHConfig] = {}
        self.last_activity: Dict[str, datetime] = {}
    
    async def initialize_default_connections(self):
        """Initialize default SSH connections from config and environment"""
        # Load from environment variables
        vps_host = os.getenv("VPS_HOST")
        vps_user = os.getenv("VPS_USER") 
        vps_password = os.getenv("VPS_PASSWORD")
        vps_port = int(os.getenv("VPS_PORT", "22"))
        
        if vps_host and vps_user and vps_password:
            config = SSHConfig(
                name="vps",
                host=vps_host,
                port=vps_port,
                username=vps_user,
                password=vps_password,
                auth_type="password"
            )
            self.configs["vps"] = config
            Logger.info(f"Loaded VPS config from environment: {vps_user}@{vps_host}:{vps_port}")
        
        # Load from default configs
        for name, config_data in DEFAULT_SSH_CONFIGS.items():
            if name not in self.configs:
                config = SSHConfig(**config_data)
                self.configs[name] = config
                Logger.info(f"Loaded default SSH config: {name}")
    
    async def connect(self, connection_name: str = "vps") -> Dict[str, Any]:
        """Connect to SSH server"""
        if connection_name not in self.configs:
            return {
                "success": False,
                "error": f"No configuration found for connection: {connection_name}"
            }
        
        config = self.configs[connection_name]
        
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect based on auth type
            if config.auth_type == "password" and config.password:
                client.connect(
                    hostname=config.host,
                    port=config.port,
                    username=config.username,
                    password=config.password,
                    timeout=config.timeout
                )
            elif config.auth_type == "key" and config.private_key_path:
                private_key = paramiko.RSAKey.from_private_key_file(config.private_key_path)
                client.connect(
                    hostname=config.host,
                    port=config.port,
                    username=config.username,
                    pkey=private_key,
                    timeout=config.timeout
                )
            else:
                return {
                    "success": False,
                    "error": "Invalid authentication configuration"
                }
            
            self.connections[connection_name] = client
            self.last_activity[connection_name] = datetime.now()
            
            Logger.info(f"Successfully connected to {config.username}@{config.host}:{config.port}")
            
            return {
                "success": True,
                "connection_id": connection_name,
                "host": config.host,
                "username": config.username,
                "message": f"Connected to {connection_name}"
            }
            
        except Exception as e:
            Logger.error(f"SSH connection failed for {connection_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to connect to {connection_name}"
            }
    
    async def disconnect(self, connection_name: str) -> Dict[str, Any]:
        """Disconnect from SSH server"""
        if connection_name in self.connections:
            try:
                self.connections[connection_name].close()
                del self.connections[connection_name]
                if connection_name in self.last_activity:
                    del self.last_activity[connection_name]
                
                Logger.info(f"Disconnected from {connection_name}")
                return {
                    "success": True,
                    "message": f"Disconnected from {connection_name}"
                }
            except Exception as e:
                Logger.error(f"Error disconnecting from {connection_name}: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        else:
            return {
                "success": False,
                "error": f"No active connection found for {connection_name}"
            }
    
    async def execute_command(self, command: str, connection_name: str = "vps", timeout: int = 60) -> CommandResult:
        """Execute command on remote server"""
        if connection_name not in self.connections:
            # Try to connect if not already connected
            connect_result = await self.connect(connection_name)
            if not connect_result["success"]:
                return CommandResult(
                    success=False,
                    exit_code=-1,
                    stdout="",
                    stderr=f"Connection failed: {connect_result['error']}",
                    command=command,
                    execution_time=0.0
                )
        
        client = self.connections[connection_name]
        start_time = time.time()
        
        try:
            stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
            
            # Read output
            stdout_data = stdout.read().decode('utf-8')
            stderr_data = stderr.read().decode('utf-8')
            exit_code = stdout.channel.recv_exit_status()
            
            execution_time = time.time() - start_time
            self.last_activity[connection_name] = datetime.now()
            
            result = CommandResult(
                success=exit_code == 0,
                exit_code=exit_code,
                stdout=stdout_data,
                stderr=stderr_data,
                command=command,
                execution_time=execution_time
            )
            
            Logger.debug(f"Command executed on {connection_name}: {command} (exit: {exit_code})")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            Logger.error(f"Command execution failed on {connection_name}: {e}")
            
            return CommandResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                command=command,
                execution_time=execution_time
            )
    
    async def get_system_info(self, connection_name: str = "vps") -> str:
        """Get comprehensive system information"""
        commands = {
            "hostname": "hostname",
            "os_info": "cat /etc/os-release | grep PRETTY_NAME | cut -d'=' -f2 | tr -d '\"'",
            "kernel_version": "uname -r",
            "cpu_info": "lscpu | grep 'Model name' | cut -d':' -f2 | xargs",
            "memory_info": "free -h | grep Mem | awk '{print $2\" total, \"$3\" used, \"$4\" available\"}'",
            "disk_info": "df -h / | tail -1 | awk '{print $2\" total, \"$3\" used, \"$4\" available (\"$5\" used)\"}'",
            "network_info": "ip route get 1.1.1.1 | grep -oP 'src \\K\\S+' | head -1",
            "uptime": "uptime -p"
        }
        
        system_data = {}
        for key, cmd in commands.items():
            result = await self.execute_command(cmd, connection_name)
            system_data[key] = result.stdout.strip() if result.success else "N/A"
        
        return json.dumps(system_data, indent=2)
    
    async def get_security_status(self, connection_name: str = "vps") -> str:
        """Get security status information"""
        commands = {
            "ssh_config": "grep -E 'Port|PermitRootLogin|PasswordAuthentication' /etc/ssh/sshd_config | grep -v '^#'",
            "firewall_status": "ufw status 2>/dev/null || echo 'UFW not configured'",
            "fail2ban_status": "fail2ban-client status 2>/dev/null || echo 'Fail2ban not installed'",
            "last_logins": "last -n 5 | head -5",
            "sudo_users": "grep -E '^sudo:' /etc/group | cut -d':' -f4",
            "running_services": "systemctl list-units --type=service --state=running | grep -E '(ssh|docker|nginx|apache)' | awk '{print $1}'"
        }
        
        security_data = {}
        for key, cmd in commands.items():
            result = await self.execute_command(cmd, connection_name)
            security_data[key] = result.stdout.strip() if result.success else result.stderr.strip()
        
        return json.dumps(security_data, indent=2)
    
    async def install_package(self, package_name: str, connection_name: str = "vps") -> Dict[str, Any]:
        """Install package using apt"""
        # Update package lists first
        update_result = await self.execute_command("sudo apt-get update", connection_name)
        if not update_result.success:
            return {
                "success": False,
                "error": f"Failed to update package lists: {update_result.stderr}"
            }
        
        # Install package
        install_cmd = f"sudo DEBIAN_FRONTEND=noninteractive apt-get install -y {package_name}"
        install_result = await self.execute_command(install_cmd, connection_name, timeout=300)
        
        if install_result.success:
            # Verify installation
            verify_result = await self.execute_command(f"dpkg -l | grep {package_name}", connection_name)
            return {
                "success": True,
                "package": package_name,
                "verification": verify_result.stdout,
                "message": f"Successfully installed {package_name}"
            }
        else:
            return {
                "success": False,
                "package": package_name,
                "error": install_result.stderr,
                "message": f"Failed to install {package_name}"
            }
    
    async def upload_file(self, local_path: str, remote_path: str, connection_name: str = "vps") -> Dict[str, Any]:
        """Upload file to remote server"""
        if connection_name not in self.connections:
            connect_result = await self.connect(connection_name)
            if not connect_result["success"]:
                return {
                    "success": False,
                    "error": f"Connection failed: {connect_result['error']}"
                }
        
        try:
            client = self.connections[connection_name]
            sftp = client.open_sftp()
            
            start_time = time.time()
            sftp.put(local_path, remote_path)
            transfer_time = time.time() - start_time
            
            # Get file size
            file_size = os.path.getsize(local_path)
            
            sftp.close()
            self.last_activity[connection_name] = datetime.now()
            
            return {
                "success": True,
                "local_path": local_path,
                "remote_path": remote_path,
                "file_size": file_size,
                "transfer_time": transfer_time,
                "message": f"Successfully uploaded {local_path} to {remote_path}"
            }
            
        except Exception as e:
            Logger.error(f"File upload failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to upload {local_path}"
            }
    
    async def download_file(self, remote_path: str, local_path: str, connection_name: str = "vps") -> Dict[str, Any]:
        """Download file from remote server"""
        if connection_name not in self.connections:
            connect_result = await self.connect(connection_name)
            if not connect_result["success"]:
                return {
                    "success": False,
                    "error": f"Connection failed: {connect_result['error']}"
                }
        
        try:
            client = self.connections[connection_name]
            sftp = client.open_sftp()
            
            start_time = time.time()
            sftp.get(remote_path, local_path)
            transfer_time = time.time() - start_time
            
            # Get file size
            file_size = os.path.getsize(local_path)
            
            sftp.close()
            self.last_activity[connection_name] = datetime.now()
            
            return {
                "success": True,
                "remote_path": remote_path,
                "local_path": local_path,
                "file_size": file_size,
                "transfer_time": transfer_time,
                "message": f"Successfully downloaded {remote_path} to {local_path}"
            }
            
        except Exception as e:
            Logger.error(f"File download failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to download {remote_path}"
            }
    
    def get_active_connections(self) -> List[str]:
        """Get list of active connection names"""
        return list(self.connections.keys())
    
    async def get_connection_status(self) -> List[ServerStatus]:
        """Get status of all configured connections"""
        statuses = []
        
        for name, config in self.configs.items():
            connected = name in self.connections
            last_activity = self.last_activity.get(name)
            
            status = ServerStatus(
                name=name,
                host=config.host,
                port=config.port,
                username=config.username,
                connected=connected,
                last_activity=last_activity.isoformat() if last_activity else None,
                connection_time=last_activity.isoformat() if connected and last_activity else None
            )
            statuses.append(status)
        
        return statuses