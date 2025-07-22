"""
Deployment automation tools for the MCP server
Based on lessons learned from production deployments
"""

import json
from typing import Any, Dict
import mcp.types as types

def register_deployment_tools(server, ssh_manager):
    """Register deployment automation tools"""
    
    @server.call_tool()
    async def deploy_agentic_site(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Deploy Agentic Site with production-ready configuration"""
        connection_name = arguments.get("connection_name", "main-vps")
        domain = arguments.get("domain", "consulting.sa")
        repository_url = arguments.get("repository_url", "https://github.com/abusallam/agentic-site.git")
        environment = arguments.get("environment", "production")
        
        try:
            deployment_steps = []
            
            # Step 1: Prepare deployment directory
            prep_commands = [
                f"mkdir -p /opt/docker-apps/{environment}",
                f"cd /opt/docker-apps/{environment} && rm -rf agentic-site-backup && mv agentic-site agentic-site-backup || true"
            ]
            
            for cmd in prep_commands:
                result = await ssh_manager.execute_command(cmd, connection_name)
                deployment_steps.append({
                    "step": "preparation",
                    "command": cmd,
                    "success": result.success,
                    "output": result.stdout
                })
            
            # Step 2: Clone repository
            clone_result = await ssh_manager.execute_command(
                f"cd /opt/docker-apps/{environment} && git clone {repository_url}",
                connection_name, timeout=120
            )
            deployment_steps.append({
                "step": "repository_clone",
                "success": clone_result.success,
                "output": clone_result.stdout
            })
            
            if not clone_result.success:
                return [types.TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": "Failed to clone repository",
                    "details": clone_result.stderr
                }, indent=2))]
            
            # Step 3: Create production environment
            env_config = f"""# Production Environment Configuration
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1
NEXT_PUBLIC_SITE_URL=https://{domain}
NEXT_PUBLIC_ADMIN_URL=https://admin.{domain}
NEXT_PUBLIC_CONTACT_EMAIL=asim@{domain}

# Backend Configuration
ADK_AGENT_PORT=8953
ADK_LOG_LEVEL=INFO
PYTHONPATH=/app/agent

# Domain Configuration
DOMAIN={domain}
FORCE_HTTPS=true

# Docker Configuration
COMPOSE_PROJECT_NAME=agentic-site
COMPOSE_HTTP_TIMEOUT=120

# Health Check Configuration
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_INTERVAL=30
"""
            
            env_result = await ssh_manager.execute_command(
                f"cd /opt/docker-apps/{environment}/agentic-site && echo '{env_config}' > .env",
                connection_name
            )
            deployment_steps.append({
                "step": "environment_config",
                "success": env_result.success
            })
            
            # Step 4: Build and deploy with Docker Compose
            build_result = await ssh_manager.execute_command(
                f"cd /opt/docker-apps/{environment}/agentic-site && docker compose build --no-cache",
                connection_name, timeout=600
            )
            deployment_steps.append({
                "step": "docker_build",
                "success": build_result.success,
                "output": build_result.stdout[:500] if build_result.stdout else ""
            })
            
            if build_result.success:
                # Stop existing containers
                await ssh_manager.execute_command(
                    f"cd /opt/docker-apps/{environment}/agentic-site && docker compose down || true",
                    connection_name
                )
                
                # Start new containers
                deploy_result = await ssh_manager.execute_command(
                    f"cd /opt/docker-apps/{environment}/agentic-site && docker compose up -d",
                    connection_name, timeout=300
                )
                deployment_steps.append({
                    "step": "docker_deploy",
                    "success": deploy_result.success,
                    "output": deploy_result.stdout
                })
                
                # Wait for services to start
                await ssh_manager.execute_command("sleep 30", connection_name)
                
                # Check container status
                status_result = await ssh_manager.execute_command(
                    f"cd /opt/docker-apps/{environment}/agentic-site && docker compose ps",
                    connection_name
                )
                deployment_steps.append({
                    "step": "container_status",
                    "success": status_result.success,
                    "output": status_result.stdout
                })
            
            # Step 5: Configure Nginx reverse proxy
            nginx_config = f"""server {{
    listen 80;
    server_name {domain} www.{domain};
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}}

server {{
    listen 443 ssl http2;
    server_name {domain} www.{domain};
    
    # SSL configuration will be added by Certbot
    
    # Frontend (Next.js)
    location / {{
        proxy_pass http://localhost:3911;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }}
    
    # Backend API
    location /api/agent/ {{
        proxy_pass http://localhost:8953/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }}
    
    # Health check
    location /health {{
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }}
}}"""
            
            nginx_result = await ssh_manager.execute_command(
                f"echo '{nginx_config}' | sudo tee /etc/nginx/sites-available/{domain}",
                connection_name
            )
            
            if nginx_result.success:
                # Enable site and test configuration
                enable_result = await ssh_manager.execute_command(
                    f"sudo ln -sf /etc/nginx/sites-available/{domain} /etc/nginx/sites-enabled/ && sudo nginx -t",
                    connection_name
                )
                
                if enable_result.success:
                    # Reload Nginx
                    await ssh_manager.execute_command("sudo systemctl reload nginx", connection_name)
                
                deployment_steps.append({
                    "step": "nginx_config",
                    "success": enable_result.success,
                    "output": enable_result.stdout
                })
            
            return [types.TextContent(type="text", text=json.dumps({
                "success": True,
                "domain": domain,
                "environment": environment,
                "deployment_steps": deployment_steps,
                "next_steps": [
                    "Configure DNS in Cloudflare",
                    "Install SSL certificates",
                    "Test all endpoints",
                    "Set up monitoring"
                ]
            }, indent=2))]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Deployment error: {str(e)}")]
    
    @server.call_tool()
    async def configure_cloudflare_dns(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Generate Cloudflare DNS configuration instructions"""
        domain = arguments.get("domain", "consulting.sa")
        server_ip = arguments.get("server_ip", "217.79.255.54")
        subdomain = arguments.get("subdomain")
        
        try:
            dns_records = [
                {
                    "type": "A",
                    "name": "@",
                    "content": server_ip,
                    "ttl": 300,
                    "comment": f"Main domain - {domain}"
                },
                {
                    "type": "A", 
                    "name": "www",
                    "content": server_ip,
                    "ttl": 300,
                    "comment": f"WWW subdomain"
                }
            ]
            
            if subdomain:
                dns_records.append({
                    "type": "A",
                    "name": subdomain,
                    "content": server_ip,
                    "ttl": 300,
                    "comment": f"Subdomain - {subdomain}.{domain}"
                })
            
            # Additional recommended records
            additional_records = [
                {
                    "type": "CNAME",
                    "name": "api",
                    "content": domain,
                    "ttl": 300,
                    "comment": "API subdomain"
                },
                {
                    "type": "CNAME",
                    "name": "admin", 
                    "content": domain,
                    "ttl": 300,
                    "comment": "Admin subdomain"
                }
            ]
            
            instructions = f"""
# Cloudflare DNS Configuration for {domain}

## Required DNS Records:
{json.dumps(dns_records, indent=2)}

## Optional Additional Records:
{json.dumps(additional_records, indent=2)}

## Cloudflare Settings Recommendations:
1. SSL/TLS Mode: Full (strict)
2. Always Use HTTPS: On
3. Automatic HTTPS Rewrites: On
4. Security Level: Medium
5. Browser Cache TTL: 4 hours
6. Edge Cache TTL: 2 hours

## Steps to Configure:
1. Log into Cloudflare Dashboard
2. Select domain: {domain}
3. Go to DNS > Records
4. Add the A records above
5. Configure SSL/TLS settings
6. Enable security features
7. Test DNS propagation: dig {domain}
"""
            
            return [types.TextContent(type="text", text=json.dumps({
                "success": True,
                "domain": domain,
                "server_ip": server_ip,
                "dns_records": dns_records,
                "additional_records": additional_records,
                "instructions": instructions
            }, indent=2))]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"DNS configuration error: {str(e)}")]
    
    @server.call_tool()
    async def setup_ssl_certificates(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Set up SSL certificates for domain with Cloudflare"""
        connection_name = arguments.get("connection_name", "main-vps")
        domain = arguments.get("domain", "consulting.sa")
        email = arguments.get("email", f"admin@{domain}")
        
        try:
            setup_steps = []
            
            # Step 1: Install Certbot
            install_result = await ssh_manager.execute_command(
                "sudo apt-get update && sudo apt-get install -y certbot python3-certbot-nginx",
                connection_name, timeout=300
            )
            setup_steps.append({
                "step": "certbot_install",
                "success": install_result.success,
                "output": install_result.stdout
            })
            
            if not install_result.success:
                return [types.TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": "Failed to install Certbot",
                    "details": install_result.stderr
                }, indent=2))]
            
            # Step 2: Obtain SSL certificate
            cert_domains = f"{domain},www.{domain}"
            cert_cmd = f"sudo certbot --nginx -d {cert_domains} --non-interactive --agree-tos --email {email}"
            
            cert_result = await ssh_manager.execute_command(cert_cmd, connection_name, timeout=300)
            setup_steps.append({
                "step": "certificate_obtain",
                "success": cert_result.success,
                "output": cert_result.stdout,
                "error": cert_result.stderr if cert_result.stderr else None
            })
            
            # Step 3: Set up auto-renewal
            cron_cmd = "echo '0 12 * * * /usr/bin/certbot renew --quiet' | sudo crontab -"
            cron_result = await ssh_manager.execute_command(cron_cmd, connection_name)
            setup_steps.append({
                "step": "auto_renewal",
                "success": cron_result.success
            })
            
            # Step 4: Test certificate
            test_result = await ssh_manager.execute_command(
                f"sudo certbot certificates | grep {domain}",
                connection_name
            )
            setup_steps.append({
                "step": "certificate_test",
                "success": test_result.success,
                "output": test_result.stdout
            })
            
            # Step 5: Test HTTPS
            https_test = await ssh_manager.execute_command(
                f"curl -I https://{domain} | head -1",
                connection_name
            )
            setup_steps.append({
                "step": "https_test",
                "success": https_test.success,
                "output": https_test.stdout
            })
            
            return [types.TextContent(type="text", text=json.dumps({
                "success": cert_result.success,
                "domain": domain,
                "email": email,
                "setup_steps": setup_steps,
                "certificate_status": "active" if cert_result.success else "failed",
                "auto_renewal": cron_result.success,
                "next_steps": [
                    f"Test HTTPS: https://{domain}",
                    "Update application URLs to use HTTPS",
                    "Configure HSTS headers",
                    "Test certificate renewal: sudo certbot renew --dry-run"
                ]
            }, indent=2))]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"SSL setup error: {str(e)}")]
    
    @server.call_tool()
    async def deployment_health_check(arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Comprehensive health check for deployed applications"""
        connection_name = arguments.get("connection_name", "main-vps")
        domain = arguments.get("domain", "consulting.sa")
        environment = arguments.get("environment", "production")
        
        try:
            health_results = {}
            
            # Check system resources
            resource_commands = {
                "cpu_load": "uptime | awk '{print $(NF-2), $(NF-1), $NF}'",
                "memory_usage": "free -m | awk 'NR==2{printf \"%.2f%%\", $3*100/$2}'",
                "disk_usage": "df -h / | awk 'NR==2{print $5}'",
                "docker_status": "systemctl is-active docker"
            }
            
            for check, cmd in resource_commands.items():
                result = await ssh_manager.execute_command(cmd, connection_name)
                health_results[check] = {
                    "status": "healthy" if result.success else "unhealthy",
                    "value": result.stdout.strip() if result.success else "N/A"
                }
            
            # Check Docker containers
            container_result = await ssh_manager.execute_command(
                f"cd /opt/docker-apps/{environment}/agentic-site && docker compose ps --format json",
                connection_name
            )
            
            if container_result.success:
                try:
                    containers = []
                    for line in container_result.stdout.strip().split('\n'):
                        if line.strip():
                            containers.append(json.loads(line))
                    health_results["containers"] = containers
                except json.JSONDecodeError:
                    health_results["containers"] = {"error": "Failed to parse container status"}
            
            # Check service endpoints
            endpoint_tests = [
                {"name": "frontend", "url": "http://localhost:3911/", "expected": "html"},
                {"name": "backend", "url": "http://localhost:8953/api/health", "expected": "json"},
                {"name": "main_site", "url": f"http://localhost/", "expected": "any"}
            ]
            
            endpoint_results = {}
            for test in endpoint_tests:
                result = await ssh_manager.execute_command(
                    f"curl -s -o /dev/null -w '%{{http_code}}' {test['url']}",
                    connection_name, timeout=10
                )
                endpoint_results[test["name"]] = {
                    "status": "healthy" if result.success and "200" in result.stdout else "unhealthy",
                    "http_code": result.stdout.strip() if result.success else "N/A"
                }
            
            health_results["endpoints"] = endpoint_results
            
            # Check security services
            security_checks = {
                "ufw_status": "ufw status | head -1",
                "fail2ban_status": "fail2ban-client status | head -1",
                "nginx_status": "systemctl is-active nginx"
            }
            
            security_results = {}
            for check, cmd in security_checks.items():
                result = await ssh_manager.execute_command(cmd, connection_name)
                security_results[check] = {
                    "status": "active" if result.success and ("active" in result.stdout or "Status" in result.stdout) else "inactive",
                    "output": result.stdout.strip()
                }
            
            health_results["security"] = security_results
            
            # Overall health assessment
            overall_health = "healthy"
            issues = []
            
            if health_results["docker_status"]["status"] != "healthy":
                overall_health = "degraded"
                issues.append("Docker service not running")
            
            unhealthy_endpoints = [name for name, status in endpoint_results.items() if status["status"] != "healthy"]
            if unhealthy_endpoints:
                overall_health = "degraded"
                issues.append(f"Unhealthy endpoints: {', '.join(unhealthy_endpoints)}")
            
            if security_results["ufw_status"]["status"] != "active":
                overall_health = "degraded"
                issues.append("Firewall not active")
            
            return [types.TextContent(type="text", text=json.dumps({
                "success": True,
                "overall_health": overall_health,
                "issues": issues,
                "timestamp": await self._get_timestamp(connection_name),
                "health_results": health_results,
                "recommendations": self._generate_health_recommendations(health_results)
            }, indent=2))]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Health check error: {str(e)}")]
    
    async def _get_timestamp(self, connection_name):
        """Get current timestamp from server"""
        result = await ssh_manager.execute_command("date '+%Y-%m-%d %H:%M:%S'", connection_name)
        return result.stdout.strip() if result.success else "N/A"
    
    def _generate_health_recommendations(self, health_results):
        """Generate health recommendations based on results"""
        recommendations = []
        
        # Check CPU load
        if "cpu_load" in health_results:
            try:
                load_1min = float(health_results["cpu_load"]["value"].split()[0])
                if load_1min > 2.0:
                    recommendations.append("High CPU load detected - consider scaling or optimization")
            except (ValueError, IndexError):
                pass
        
        # Check memory usage
        if "memory_usage" in health_results:
            try:
                memory_pct = float(health_results["memory_usage"]["value"].replace('%', ''))
                if memory_pct > 80:
                    recommendations.append("High memory usage - consider adding more RAM or optimizing applications")
            except ValueError:
                pass
        
        # Check disk usage
        if "disk_usage" in health_results:
            try:
                disk_pct = int(health_results["disk_usage"]["value"].replace('%', ''))
                if disk_pct > 80:
                    recommendations.append("High disk usage - consider cleanup or adding storage")
            except ValueError:
                pass
        
        if not recommendations:
            recommendations.append("System is running optimally")
        
        return recommendations
    
    # Register deployment tools
    deployment_tools = [
        {
            "name": "deploy_agentic_site",
            "description": "Deploy Agentic Site with production configuration",
            "schema": {
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name"},
                    "domain": {"type": "string", "description": "Domain name for deployment"},
                    "repository_url": {"type": "string", "description": "Git repository URL"},
                    "environment": {"type": "string", "description": "Deployment environment (production/staging)"}
                }
            }
        },
        {
            "name": "configure_cloudflare_dns",
            "description": "Generate Cloudflare DNS configuration instructions",
            "schema": {
                "type": "object",
                "properties": {
                    "domain": {"type": "string", "description": "Domain name"},
                    "server_ip": {"type": "string", "description": "Server IP address"},
                    "subdomain": {"type": "string", "description": "Additional subdomain to configure"}
                }
            }
        },
        {
            "name": "setup_ssl_certificates",
            "description": "Set up SSL certificates with Let's Encrypt",
            "schema": {
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name"},
                    "domain": {"type": "string", "description": "Domain name for SSL certificate"},
                    "email": {"type": "string", "description": "Email for certificate notifications"}
                }
            }
        },
        {
            "name": "deployment_health_check",
            "description": "Comprehensive health check for deployed applications",
            "schema": {
                "type": "object",
                "properties": {
                    "connection_name": {"type": "string", "description": "SSH connection name"},
                    "domain": {"type": "string", "description": "Domain name to check"},
                    "environment": {"type": "string", "description": "Environment to check (production/staging)"}
                }
            }
        }
    ]
    
    # Add all tools to the server
    for tool_config in deployment_tools:
        server.list_tools().append(
            types.Tool(
                name=tool_config["name"],
                description=tool_config["description"],
                inputSchema=tool_config["schema"]
            )
        )