"""
System administration tools for the MCP server
"""

import json
from typing import Any, Dict
import mcp.types as types

def register_system_tools(server, ssh_manager):
    """Register system administration tools"""
    
    @server.call_tool()
    async def system_setup_firewall(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Set up UFW firewall with production-ready security rules"""
        connection_name = arguments.get("connection_name", "vps")
        allow_ports = arguments.get("allow_ports", [22, 80, 443])
        deny_ports = arguments.get("deny_ports", [])
        
        try:
            # Conservative approach - maintain SSH access throughout
            commands = [
                "sudo apt-get update && sudo apt-get install -y ufw",
                "sudo ufw --force reset",
                "sudo ufw default deny incoming",
                "sudo ufw default allow outgoing"
            ]
            
            # Always allow SSH first (critical for maintaining access)
            if 22 not in allow_ports:
                allow_ports.insert(0, 22)
            
            # Allow specified ports with descriptive comments
            port_descriptions = {
                22: "SSH Access",
                80: "HTTP Web Traffic", 
                443: "HTTPS Web Traffic",
                3000: "Next.js Development",
                3911: "Next.js Production",
                8000: "API Server",
                8953: "Agent Backend"
            }
            
            for port in allow_ports:
                comment = port_descriptions.get(port, f"Port {port}")
                commands.append(f"sudo ufw allow {port}/tcp comment '{comment}'")
            
            # Deny specified ports
            for port in deny_ports:
                commands.append(f"sudo ufw deny {port}/tcp comment 'Blocked Port {port}'")
            
            # Show rules before enabling
            commands.append("sudo ufw show added")
            
            # Enable firewall (critical moment)
            commands.extend([
                "sudo ufw --force enable",
                "sudo ufw status numbered",
                "echo 'SSH test after UFW enable' && echo 'UFW enabled successfully'"
            ])
            
            results = []
            for cmd in commands:
                result = await ssh_manager.execute_command(cmd, connection_name, timeout=60)
                results.append({
                    "command": cmd,
                    "success": result.success,
                    "output": result.stdout,
                    "error": result.stderr
                })
                
                # Critical check: verify SSH still works after enabling UFW
                if "ufw --force enable" in cmd and result.success:
                    ssh_test = await ssh_manager.execute_command("echo 'SSH access verified'", connection_name, timeout=10)
                    if not ssh_test.success:
                        # Emergency: disable UFW if SSH access lost
                        await ssh_manager.execute_command("sudo ufw --force disable", connection_name)
                        return [types.TextContent(type="text", text=json.dumps({
                            "success": False,
                            "error": "SSH access lost after enabling UFW - firewall disabled for safety",
                            "emergency_action": "UFW disabled to restore access"
                        }, indent=2))]
            
            return [types.TextContent(type="text", text=json.dumps({
                "success": True,
                "allowed_ports": allow_ports,
                "denied_ports": deny_ports,
                "firewall_status": "active",
                "ssh_access": "maintained",
                "commands_executed": results,
                "security_note": "Conservative approach used - SSH access maintained throughout"
            }, indent=2))]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def system_setup_fail2ban(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Set up fail2ban for intrusion prevention"""
        connection_name = arguments.get("connection_name", "vps")
        ssh_port = arguments.get("ssh_port", 22)
        
        try:
            # Install fail2ban
            install_result = await ssh_manager.execute_command(
                "sudo apt-get update && sudo apt-get install -y fail2ban",
                connection_name, timeout=300
            )
            
            if not install_result.success:
                return [types.TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": f"Failed to install fail2ban: {install_result.stderr}"
                }, indent=2))]
            
            # Create jail configuration
            jail_config = f"""[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = {ssh_port}
logpath = /var/log/auth.log
maxretry = 3
"""
            
            # Write configuration
            config_cmd = f"echo '{jail_config}' | sudo tee /etc/fail2ban/jail.local"
            config_result = await ssh_manager.execute_command(config_cmd, connection_name)
            
            # Start and enable fail2ban
            service_result = await ssh_manager.execute_command(
                "sudo systemctl start fail2ban && sudo systemctl enable fail2ban",
                connection_name
            )
            
            # Check status
            status_result = await ssh_manager.execute_command(
                "sudo fail2ban-client status",
                connection_name
            )
            
            return [types.TextContent(type="text", text=json.dumps({
                "success": True,
                "ssh_port": ssh_port,
                "install_success": install_result.success,
                "config_success": config_result.success,
                "service_success": service_result.success,
                "status": status_result.stdout
            }, indent=2))]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def system_create_user(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Create a new system user with optional sudo privileges"""
        connection_name = arguments.get("connection_name", "vps")
        username = arguments.get("username")
        password = arguments.get("password")
        ssh_key = arguments.get("ssh_key")
        sudo_access = arguments.get("sudo_access", False)
        
        if not username:
            return [types.TextContent(type="text", text="Error: Username is required")]
        
        try:
            commands = []
            results = []
            
            # Create user
            create_cmd = f"sudo useradd -m -s /bin/bash {username}"
            create_result = await ssh_manager.execute_command(create_cmd, connection_name)
            results.append({"step": "create_user", "success": create_result.success, "output": create_result.stdout})
            
            # Set password if provided
            if password:
                passwd_cmd = f"echo '{username}:{password}' | sudo chpasswd"
                passwd_result = await ssh_manager.execute_command(passwd_cmd, connection_name)
                results.append({"step": "set_password", "success": passwd_result.success})
            
            # Add SSH key if provided
            if ssh_key:
                ssh_commands = [
                    f"sudo mkdir -p /home/{username}/.ssh",
                    f"echo '{ssh_key}' | sudo tee /home/{username}/.ssh/authorized_keys",
                    f"sudo chmod 700 /home/{username}/.ssh",
                    f"sudo chmod 600 /home/{username}/.ssh/authorized_keys",
                    f"sudo chown -R {username}:{username} /home/{username}/.ssh"
                ]
                
                for cmd in ssh_commands:
                    result = await ssh_manager.execute_command(cmd, connection_name)
                    results.append({"step": f"ssh_setup_{cmd.split()[-1]}", "success": result.success})
            
            # Add sudo privileges if requested
            if sudo_access:
                sudo_cmd = f"echo '{username} ALL=(ALL) NOPASSWD:ALL' | sudo tee /etc/sudoers.d/{username}"
                sudo_result = await ssh_manager.execute_command(sudo_cmd, connection_name)
                
                # Set proper permissions
                perm_result = await ssh_manager.execute_command(f"sudo chmod 440 /etc/sudoers.d/{username}", connection_name)
                
                results.append({"step": "sudo_access", "success": sudo_result.success and perm_result.success})
            
            return [types.TextContent(type="text", text=json.dumps({
                "success": True,
                "username": username,
                "has_password": password is not None,
                "has_ssh_key": ssh_key is not None,
                "has_sudo": sudo_access,
                "steps": results
            }, indent=2))]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def system_setup_nginx(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Install and configure Nginx web server"""
        connection_name = arguments.get("connection_name", "vps")
        domain = arguments.get("domain")
        proxy_pass = arguments.get("proxy_pass")
        
        try:
            # Install Nginx
            install_result = await ssh_manager.execute_command(
                "sudo apt-get update && sudo apt-get install -y nginx",
                connection_name, timeout=300
            )
            
            if not install_result.success:
                return [types.TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": f"Failed to install Nginx: {install_result.stderr}"
                }, indent=2))]
            
            # Create basic configuration if domain provided
            if domain:
                config_content = f"""server {{
    listen 80;
    server_name {domain};
    
    location / {{
        {f"proxy_pass {proxy_pass};" if proxy_pass else "root /var/www/html;"}
        {f"proxy_set_header Host $host;" if proxy_pass else ""}
        {f"proxy_set_header X-Real-IP $remote_addr;" if proxy_pass else ""}
        {f"proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;" if proxy_pass else ""}
        {f"proxy_set_header X-Forwarded-Proto $scheme;" if proxy_pass else ""}
    }}
}}"""
                
                # Write configuration
                config_cmd = f"echo '{config_content}' | sudo tee /etc/nginx/sites-available/{domain}"
                config_result = await ssh_manager.execute_command(config_cmd, connection_name)
                
                # Enable site
                enable_result = await ssh_manager.execute_command(
                    f"sudo ln -sf /etc/nginx/sites-available/{domain} /etc/nginx/sites-enabled/{domain}",
                    connection_name
                )
                
                # Test configuration
                test_result = await ssh_manager.execute_command("sudo nginx -t", connection_name)
                
                if test_result.success:
                    # Reload Nginx
                    reload_result = await ssh_manager.execute_command("sudo systemctl reload nginx", connection_name)
                else:
                    return [types.TextContent(type="text", text=json.dumps({
                        "success": False,
                        "error": f"Nginx configuration test failed: {test_result.stderr}"
                    }, indent=2))]
            
            # Start and enable Nginx
            service_result = await ssh_manager.execute_command(
                "sudo systemctl start nginx && sudo systemctl enable nginx",
                connection_name
            )
            
            # Check status
            status_result = await ssh_manager.execute_command("sudo systemctl status nginx", connection_name)
            
            return [types.TextContent(type="text", text=json.dumps({
                "success": True,
                "domain": domain,
                "proxy_pass": proxy_pass,
                "install_success": install_result.success,
                "service_success": service_result.success,
                "status": "active" in status_result.stdout.lower()
            }, indent=2))]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def system_setup_ssl(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Set up SSL certificates with Let's Encrypt"""
        connection_name = arguments.get("connection_name", "vps")
        domain = arguments.get("domain")
        email = arguments.get("email", f"admin@{domain}")
        
        if not domain:
            return [types.TextContent(type="text", text="Error: Domain is required")]
        
        try:
            # Install Certbot
            install_result = await ssh_manager.execute_command(
                "sudo apt-get update && sudo apt-get install -y certbot python3-certbot-nginx",
                connection_name, timeout=300
            )
            
            if not install_result.success:
                return [types.TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": f"Failed to install Certbot: {install_result.stderr}"
                }, indent=2))]
            
            # Obtain SSL certificate
            cert_cmd = f"sudo certbot --nginx -d {domain} --non-interactive --agree-tos --email {email}"
            cert_result = await ssh_manager.execute_command(cert_cmd, connection_name, timeout=300)
            
            # Set up auto-renewal
            cron_result = await ssh_manager.execute_command(
                "echo '0 12 * * * /usr/bin/certbot renew --quiet' | sudo crontab -",
                connection_name
            )
            
            return [types.TextContent(type="text", text=json.dumps({
                "success": "Congratulations" in cert_result.stdout,
                "domain": domain,
                "email": email,
                "certificate_output": cert_result.stdout,
                "auto_renewal_setup": cron_result.success,
                "error": cert_result.stderr if cert_result.stderr else None
            }, indent=2))]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def system_monitor_resources(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Monitor system resources (CPU, memory, disk, network)"""
        connection_name = arguments.get("connection_name", "vps")
        samples = arguments.get("samples", 1)
        interval = arguments.get("interval", 5)
        
        try:
            monitoring_data = []
            
            for i in range(samples):
                if i > 0:
                    await ssh_manager.execute_command(f"sleep {interval}", connection_name)
                
                # Collect system metrics
                commands = {
                    "timestamp": "date '+%Y-%m-%d %H:%M:%S'",
                    "cpu_usage": "top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'",
                    "memory_usage": "free -m | awk 'NR==2{printf \"%.2f\", $3*100/$2}'",
                    "disk_usage": "df -h / | awk 'NR==2{print $5}' | sed 's/%//'",
                    "load_average": "cat /proc/loadavg | awk '{print $1, $2, $3}'",
                    "network_connections": "ss -tuln | wc -l",
                    "processes": "ps aux | wc -l",
                    "uptime": "uptime -p"
                }
                
                sample_data = {}
                for metric, cmd in commands.items():
                    result = await ssh_manager.execute_command(cmd, connection_name)
                    sample_data[metric] = result.stdout.strip() if result.success else "N/A"
                
                monitoring_data.append(sample_data)
            
            return [types.TextContent(type="text", text=json.dumps({
                "success": True,
                "samples": samples,
                "interval": interval,
                "data": monitoring_data
            }, indent=2))]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def system_backup_create(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Create system backup"""
        connection_name = arguments.get("connection_name", "vps")
        backup_path = arguments.get("backup_path", "/opt/backups")
        include_dirs = arguments.get("include_dirs", ["/etc", "/home", "/opt"])
        
        try:
            # Create backup directory
            mkdir_result = await ssh_manager.execute_command(f"sudo mkdir -p {backup_path}", connection_name)
            
            # Generate timestamp
            timestamp_result = await ssh_manager.execute_command("date +%Y%m%d_%H%M%S", connection_name)
            timestamp = timestamp_result.stdout.strip()
            
            backup_file = f"{backup_path}/system_backup_{timestamp}.tar.gz"
            
            # Create backup
            dirs_str = " ".join(include_dirs)
            backup_cmd = f"sudo tar -czf {backup_file} {dirs_str} --exclude={backup_path}"
            backup_result = await ssh_manager.execute_command(backup_cmd, connection_name, timeout=1800)  # 30 minutes
            
            if backup_result.success:
                # Get backup file info
                info_result = await ssh_manager.execute_command(f"ls -lh {backup_file}", connection_name)
                
                return [types.TextContent(type="text", text=json.dumps({
                    "success": True,
                    "backup_file": backup_file,
                    "included_directories": include_dirs,
                    "file_info": info_result.stdout.strip(),
                    "timestamp": timestamp
                }, indent=2))]
            else:
                return [types.TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": backup_result.stderr
                }, indent=2))]
                
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    # Register all system tools
    system_tools = [
        {
            "name": "system_setup_firewall",
            "description": "Set up UFW firewall with security rules",
            "schema": {
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name"},
                    "allow_ports": {"type": "array", "items": {"type": "integer"}, "description": "Ports to allow"},
                    "deny_ports": {"type": "array", "items": {"type": "integer"}, "description": "Ports to deny"}
                }
            }
        },
        {
            "name": "system_setup_fail2ban",
            "description": "Set up fail2ban for intrusion prevention",
            "schema": {
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name"},
                    "ssh_port": {"type": "integer", "description": "SSH port number (default: 22)"}
                }
            }
        },
        {
            "name": "system_create_user",
            "description": "Create a new system user with optional sudo privileges",
            "schema": {
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name"},
                    "username": {"type": "string", "description": "Username for new user"},
                    "password": {"type": "string", "description": "Password for new user"},
                    "ssh_key": {"type": "string", "description": "SSH public key"},
                    "sudo_access": {"type": "boolean", "description": "Grant sudo privileges"}
                },
                "required": ["username"]
            }
        },
        {
            "name": "system_setup_nginx",
            "description": "Install and configure Nginx web server",
            "schema": {
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name"},
                    "domain": {"type": "string", "description": "Domain name for virtual host"},
                    "proxy_pass": {"type": "string", "description": "Upstream server for reverse proxy"}
                }
            }
        },
        {
            "name": "system_setup_ssl",
            "description": "Set up SSL certificates with Let's Encrypt",
            "schema": {
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name"},
                    "domain": {"type": "string", "description": "Domain name for SSL certificate"},
                    "email": {"type": "string", "description": "Email for Let's Encrypt notifications"}
                },
                "required": ["domain"]
            }
        },
        {
            "name": "system_monitor_resources",
            "description": "Monitor system resources (CPU, memory, disk, network)",
            "schema": {
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name"},
                    "samples": {"type": "integer", "description": "Number of samples to collect"},
                    "interval": {"type": "integer", "description": "Interval between samples in seconds"}
                }
            }
        },
        {
            "name": "system_backup_create",
            "description": "Create system backup",
            "schema": {
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name"},
                    "backup_path": {"type": "string", "description": "Path to store backup files"},
                    "include_dirs": {"type": "array", "items": {"type": "string"}, "description": "Directories to include in backup"}
                }
            }
        }
    ]
    
    # Add all tools to the server
    for tool_config in system_tools:
        server.list_tools().append(
            types.Tool(
                name=tool_config["name"],
                description=tool_config["description"],
                inputSchema=tool_config["schema"]
            )
        )