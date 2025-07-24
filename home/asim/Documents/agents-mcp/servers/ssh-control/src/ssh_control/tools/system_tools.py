"""
System administration tools for the MCP server
"""

import json
from typing import Any, Dict
import mcp.types as types

def register_system_tools(server, ssh_manager):
    """Register system administration tools"""
    
    @server.call_tool()
    async def monitor_logs(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Monitor system log files"""
        connection_name = arguments.get("connection_name", "vps")
        log_file = arguments.get("log_file", "/var/log/syslog")
        lines = arguments.get("lines", 50)
        follow = arguments.get("follow", False)
        
        try:
            result = await _monitor_log_file(ssh_manager, connection_name, log_file, lines, follow)
            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def tail_logs(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Tail multiple log files"""
        connection_name = arguments.get("connection_name", "vps")
        log_files = arguments.get("log_files", ["/var/log/syslog", "/var/log/auth.log"])
        lines = arguments.get("lines", 20)
        
        try:
            result = await _tail_multiple_logs(ssh_manager, connection_name, log_files, lines)
            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def search_logs(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Search in log files"""
        connection_name = arguments.get("connection_name", "vps")
        pattern = arguments.get("pattern")
        log_file = arguments.get("log_file", "/var/log/syslog")
        lines = arguments.get("lines", 100)
        
        if not pattern:
            return [types.TextContent(type="text", text="Error: pattern is required")]
        
        try:
            result = await _search_log_file(ssh_manager, connection_name, log_file, pattern, lines)
            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def system_status(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Get comprehensive system status"""
        connection_name = arguments.get("connection_name", "vps")
        
        try:
            result = await _get_system_status(ssh_manager, connection_name)
            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def process_monitor(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Monitor system processes"""
        connection_name = arguments.get("connection_name", "vps")
        process_name = arguments.get("process_name")
        
        try:
            result = await _monitor_processes(ssh_manager, connection_name, process_name)
            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def disk_usage(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Check disk usage and space"""
        connection_name = arguments.get("connection_name", "vps")
        path = arguments.get("path", "/")
        
        try:
            result = await _check_disk_usage(ssh_manager, connection_name, path)
            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def service_status(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Check systemd service status"""
        connection_name = arguments.get("connection_name", "vps")
        service_name = arguments.get("service_name")
        
        if not service_name:
            return [types.TextContent(type="text", text="Error: service_name is required")]
        
        try:
            result = await _check_service_status(ssh_manager, connection_name, service_name)
            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    # Register system tools
    system_tools = [
        types.Tool(
            name="monitor_logs",
            description="Monitor system log files with tail functionality",
            inputSchema={
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name (default: vps)"},
                    "log_file": {"type": "string", "description": "Log file path (default: /var/log/syslog)"},
                    "lines": {"type": "integer", "description": "Number of lines to show (default: 50)"},
                    "follow": {"type": "boolean", "description": "Follow log output in real-time"}
                }
            }
        ),
        types.Tool(
            name="tail_logs",
            description="Tail multiple log files simultaneously",
            inputSchema={
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name (default: vps)"},
                    "log_files": {"type": "array", "items": {"type": "string"}, "description": "List of log file paths"},
                    "lines": {"type": "integer", "description": "Number of lines per file (default: 20)"}
                }
            }
        ),
        types.Tool(
            name="search_logs",
            description="Search for patterns in log files",
            inputSchema={
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name (default: vps)"},
                    "pattern": {"type": "string", "description": "Search pattern (regex supported)"},
                    "log_file": {"type": "string", "description": "Log file path (default: /var/log/syslog)"},
                    "lines": {"type": "integer", "description": "Max lines to return (default: 100)"}
                },
                "required": ["pattern"]
            }
        ),
        types.Tool(
            name="system_status",
            description="Get comprehensive system status including CPU, memory, disk",
            inputSchema={
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name (default: vps)"}
                }
            }
        ),
        types.Tool(
            name="process_monitor",
            description="Monitor system processes",
            inputSchema={
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name (default: vps)"},
                    "process_name": {"type": "string", "description": "Process name to filter (optional)"}
                }
            }
        ),
        types.Tool(
            name="disk_usage",
            description="Check disk usage and available space",
            inputSchema={
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name (default: vps)"},
                    "path": {"type": "string", "description": "Path to check (default: /)"}
                }
            }
        ),
        types.Tool(
            name="service_status",
            description="Check systemd service status",
            inputSchema={
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name (default: vps)"},
                    "service_name": {"type": "string", "description": "Service name to check"}
                },
                "required": ["service_name"]
            }
        )
    ]
    
    for tool in system_tools:
        server.list_tools().append(tool)

# Helper functions for system tools

async def _monitor_log_file(ssh_manager, connection_name: str, log_file: str, lines: int, follow: bool) -> str:
    """Monitor a single log file"""
    cmd = f"tail -{lines}"
    if follow:
        cmd += " -f"
    cmd += f" {log_file}"
    
    # Use shorter timeout for follow mode
    timeout = 10 if follow else 30
    
    result = await ssh_manager.execute_command(cmd, connection_name, timeout=timeout)
    
    if result.success:
        return f"=== {log_file} ===\n{result.stdout}"
    else:
        return f"Error reading {log_file}: {result.stderr}"

async def _tail_multiple_logs(ssh_manager, connection_name: str, log_files: list, lines: int) -> str:
    """Tail multiple log files"""
    output = []
    
    for log_file in log_files:
        cmd = f"tail -{lines} {log_file}"
        result = await ssh_manager.execute_command(cmd, connection_name)
        
        if result.success:
            output.append(f"=== {log_file} ===")
            output.append(result.stdout)
            output.append("")
        else:
            output.append(f"=== {log_file} (ERROR) ===")
            output.append(f"Error: {result.stderr}")
            output.append("")
    
    return "\n".join(output)

async def _search_log_file(ssh_manager, connection_name: str, log_file: str, pattern: str, lines: int) -> str:
    """Search for pattern in log file"""
    cmd = f"grep -n '{pattern}' {log_file} | tail -{lines}"
    result = await ssh_manager.execute_command(cmd, connection_name)
    
    if result.success:
        if result.stdout.strip():
            return f"=== Search results for '{pattern}' in {log_file} ===\n{result.stdout}"
        else:
            return f"No matches found for '{pattern}' in {log_file}"
    else:
        return f"Error searching {log_file}: {result.stderr}"

async def _get_system_status(ssh_manager, connection_name: str) -> str:
    """Get comprehensive system status"""
    commands = {
        "uptime": "uptime",
        "load_average": "cat /proc/loadavg",
        "memory": "free -h",
        "disk_usage": "df -h",
        "cpu_info": "top -bn1 | grep 'Cpu(s)' | head -1",
        "running_processes": "ps aux --sort=-%cpu | head -10",
        "network_connections": "netstat -tuln | head -10",
        "last_logins": "last -n 5"
    }
    
    output = ["=== SYSTEM STATUS ===\n"]
    
    for section, cmd in commands.items():
        result = await ssh_manager.execute_command(cmd, connection_name)
        output.append(f"--- {section.upper().replace('_', ' ')} ---")
        if result.success:
            output.append(result.stdout)
        else:
            output.append(f"Error: {result.stderr}")
        output.append("")
    
    return "\n".join(output)

async def _monitor_processes(ssh_manager, connection_name: str, process_name: str = None) -> str:
    """Monitor system processes"""
    if process_name:
        cmd = f"ps aux | grep '{process_name}' | grep -v grep"
    else:
        cmd = "ps aux --sort=-%cpu | head -20"
    
    result = await ssh_manager.execute_command(cmd, connection_name)
    
    if result.success:
        if process_name:
            return f"=== Processes matching '{process_name}' ===\n{result.stdout}"
        else:
            return f"=== Top Processes by CPU Usage ===\n{result.stdout}"
    else:
        return f"Error monitoring processes: {result.stderr}"

async def _check_disk_usage(ssh_manager, connection_name: str, path: str) -> str:
    """Check disk usage for specified path"""
    commands = {
        "disk_space": f"df -h {path}",
        "inode_usage": f"df -i {path}",
        "largest_files": f"du -h {path}/* 2>/dev/null | sort -hr | head -10",
        "disk_io": "iostat -x 1 1 2>/dev/null || echo 'iostat not available'"
    }
    
    output = [f"=== DISK USAGE FOR {path} ===\n"]
    
    for section, cmd in commands.items():
        result = await ssh_manager.execute_command(cmd, connection_name)
        output.append(f"--- {section.upper().replace('_', ' ')} ---")
        if result.success:
            output.append(result.stdout)
        else:
            output.append(f"Error: {result.stderr}")
        output.append("")
    
    return "\n".join(output)

async def _check_service_status(ssh_manager, connection_name: str, service_name: str) -> str:
    """Check systemd service status"""
    commands = {
        "status": f"systemctl status {service_name}",
        "is_active": f"systemctl is-active {service_name}",
        "is_enabled": f"systemctl is-enabled {service_name}",
        "recent_logs": f"journalctl -u {service_name} -n 20 --no-pager"
    }
    
    output = [f"=== SERVICE STATUS: {service_name} ===\n"]
    
    for section, cmd in commands.items():
        result = await ssh_manager.execute_command(cmd, connection_name)
        output.append(f"--- {section.upper().replace('_', ' ')} ---")
        if result.success:
            output.append(result.stdout)
        else:
            output.append(f"Error: {result.stderr}")
        output.append("")
    
    return "\n".join(output)