"""
Type definitions for SSH Control MCP Server
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class SSHConfig:
    """SSH connection configuration"""
    name: str
    host: str
    port: int
    username: str
    password: Optional[str] = None
    private_key_path: Optional[str] = None
    auth_type: str = "password"  # "password" or "key"
    timeout: int = 30

@dataclass
class CommandResult:
    """Result of command execution"""
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    command: str
    execution_time: float
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "command": self.command,
            "execution_time": self.execution_time
        }

@dataclass
class SystemInfo:
    """System information"""
    hostname: str
    os_info: str
    kernel_version: str
    cpu_info: str
    memory_info: str
    disk_info: str
    network_info: str
    uptime: str

@dataclass
class ServerStatus:
    """Server connection status"""
    name: str
    host: str
    port: int
    username: str
    connected: bool
    last_activity: Optional[str] = None
    connection_time: Optional[str] = None
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "connected": self.connected,
            "last_activity": self.last_activity,
            "connection_time": self.connection_time
        }