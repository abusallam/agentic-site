# 🤖 Agent MCP Servers Documentation

## 📋 Overview

This document provides comprehensive documentation for all MCP (Model Context Protocol) servers available in the agent ecosystem. Each server provides specialized tools and capabilities for different aspects of system administration, development, and automation.

**Last Updated**: 2025-07-21  
**Maintained By**: Kiro AI Assistant  

---

## 🖥️ SSH Control Server

**Location**: `servers/ssh-control/`  
**Purpose**: Remote server administration, deployment, and management  
**Status**: ✅ Production Ready  

### 🔧 Server Configuration

```json
{
  "name": "ssh-control",
  "command": "uv",
  "args": ["run", "python", "-m", "ssh_control"],
  "cwd": "servers/ssh-control",
  "env": {
    "PYTHONPATH": "src"
  }
}
```

### 🛠️ Available Tools

#### System Administration Tools

##### `system_setup_firewall`
**Purpose**: Configure UFW firewall with production-ready security rules  
**Usage**: Set up secure firewall configuration with conservative approach  

**Parameters**:
- `connection_name` (string): SSH connection identifier (default: "vps")
- `allow_ports` (array): List of ports to allow (default: [22, 80, 443])
- `deny_ports` (array): List of ports to explicitly deny

**Example**:
```json
{
  "connection_name": "main-vps",
  "allow_ports": [22, 80, 443, 3911, 8953],
  "deny_ports": [3306, 5432]
}
```

**Features**:
- ✅ Conservative approach - maintains SSH access throughout
- ✅ Descriptive port comments for documentation
- ✅ Emergency SSH access verification
- ✅ Automatic rollback if SSH access lost

##### `system_setup_fail2ban`
**Purpose**: Install and configure fail2ban for intrusion prevention  
**Usage**: Protect SSH and other services from brute force attacks  

**Parameters**:
- `connection_name` (string): SSH connection identifier
- `ssh_port` (integer): SSH port number (default: 22)

**Example**:
```json
{
  "connection_name": "main-vps",
  "ssh_port": 22
}
```

**Features**:
- ✅ SSH brute force protection
- ✅ Configurable ban times and retry limits
- ✅ Automatic service startup and monitoring

##### `system_create_user`
**Purpose**: Create system users with optional sudo privileges  
**Usage**: Set up additional admin users with secure access  

**Parameters**:
- `connection_name` (string): SSH connection identifier
- `username` (string, required): Username for new user
- `password` (string): Password for new user
- `ssh_key` (string): SSH public key for key-based authentication
- `sudo_access` (boolean): Grant sudo privileges (default: false)

**Example**:
```json
{
  "connection_name": "main-vps",
  "username": "admin",
  "password": "secure_password",
  "ssh_key": "ssh-rsa AAAAB3NzaC1yc2E...",
  "sudo_access": true
}
```

##### `system_setup_nginx`
**Purpose**: Install and configure Nginx web server  
**Usage**: Set up reverse proxy and web server configuration  

**Parameters**:
- `connection_name` (string): SSH connection identifier
- `domain` (string): Domain name for virtual host
- `proxy_pass` (string): Upstream server for reverse proxy

**Example**:
```json
{
  "connection_name": "main-vps",
  "domain": "consulting.sa",
  "proxy_pass": "http://localhost:3911"
}
```

##### `system_setup_ssl`
**Purpose**: Set up SSL certificates with Let's Encrypt  
**Usage**: Configure HTTPS with automatic certificate renewal  

**Parameters**:
- `connection_name` (string): SSH connection identifier
- `domain` (string, required): Domain name for SSL certificate
- `email` (string): Email for Let's Encrypt notifications

**Example**:
```json
{
  "connection_name": "main-vps",
  "domain": "consulting.sa",
  "email": "admin@consulting.sa"
}
```

##### `system_monitor_resources`
**Purpose**: Monitor system resources (CPU, memory, disk, network)  
**Usage**: Collect system performance metrics and monitoring data  

**Parameters**:
- `connection_name` (string): SSH connection identifier
- `samples` (integer): Number of samples to collect (default: 1)
- `interval` (integer): Interval between samples in seconds (default: 5)

**Example**:
```json
{
  "connection_name": "main-vps",
  "samples": 5,
  "interval": 10
}
```

##### `system_backup_create`
**Purpose**: Create comprehensive system backups  
**Usage**: Backup critical system directories and configurations  

**Parameters**:
- `connection_name` (string): SSH connection identifier
- `backup_path` (string): Path to store backup files (default: "/opt/backups")
- `include_dirs` (array): Directories to include in backup (default: ["/etc", "/home", "/opt"])

**Example**:
```json
{
  "connection_name": "main-vps",
  "backup_path": "/opt/backups",
  "include_dirs": ["/etc", "/home", "/opt", "/var/www"]
}
```

#### Docker Management Tools

##### `docker_install`
**Purpose**: Install Docker with production-ready security configuration  
**Usage**: Set up Docker environment with security best practices  

**Parameters**:
- `connection_name` (string): SSH connection identifier

**Example**:
```json
{
  "connection_name": "main-vps"
}
```

**Features**:
- ✅ Production-optimized daemon configuration
- ✅ Security hardening applied
- ✅ Organized directory structure
- ✅ Management scripts installation

##### `docker_status`
**Purpose**: Get comprehensive Docker status and information  
**Usage**: Monitor Docker system health and container status  

**Parameters**:
- `connection_name` (string): SSH connection identifier

##### `docker_list_containers`
**Purpose**: List Docker containers with detailed information  
**Usage**: View running and stopped containers  

**Parameters**:
- `connection_name` (string): SSH connection identifier
- `all` (boolean): Show all containers including stopped (default: true)

##### `docker_create_container`
**Purpose**: Create new Docker container with configuration  
**Usage**: Deploy applications in Docker containers  

**Parameters**:
- `connection_name` (string): SSH connection identifier
- `image` (string, required): Docker image name
- `name` (string): Container name
- `ports` (object): Port mappings (host:container)
- `volumes` (object): Volume mappings (host:container)
- `environment` (object): Environment variables
- `network` (string): Network name
- `restart` (string): Restart policy
- `command` (string): Command to run

**Example**:
```json
{
  "connection_name": "main-vps",
  "image": "nginx:latest",
  "name": "web-server",
  "ports": {"80": "80", "443": "443"},
  "volumes": {"/opt/www": "/usr/share/nginx/html"},
  "environment": {"ENV": "production"},
  "restart": "unless-stopped"
}
```

##### `docker_compose_up`
**Purpose**: Deploy multi-service applications with Docker Compose  
**Usage**: Start complex applications with multiple containers  

**Parameters**:
- `connection_name` (string): SSH connection identifier
- `compose_file` (string, required): Path to docker-compose.yml file
- `detach` (boolean): Run in detached mode (default: true)

**Example**:
```json
{
  "connection_name": "main-vps",
  "compose_file": "/opt/docker-apps/production/agentic-site/docker-compose.yml",
  "detach": true
}
```

##### `docker_compose_down`
**Purpose**: Stop Docker Compose applications  
**Usage**: Gracefully stop multi-service applications  

**Parameters**:
- `connection_name` (string): SSH connection identifier
- `compose_file` (string, required): Path to docker-compose.yml file

#### SSH Connection Tools

##### `ssh_connect`
**Purpose**: Establish SSH connections to remote servers  
**Usage**: Connect to VPS instances for administration  

##### `ssh_execute_command`
**Purpose**: Execute commands on remote servers  
**Usage**: Run administrative commands remotely  

##### `ssh_upload_file`
**Purpose**: Upload files to remote servers  
**Usage**: Transfer configuration files and applications  

##### `ssh_download_file`
**Purpose**: Download files from remote servers  
**Usage**: Retrieve logs, backups, and configuration files  

### 🏗️ Client Management System

#### Client Directory Structure
```
clients/
├── README.md                    # Client management overview
├── main-vps/                   # Main production VPS
│   ├── README.md               # Complete client documentation
│   ├── deployment-history.md   # Chronological deployment log
│   ├── configurations/         # Environment files and configs
│   ├── scripts/               # Custom management scripts
│   ├── monitoring/            # Health checks and monitoring
│   └── backups/               # Backup configurations
└── [future-clients]/          # Additional VPS instances
```

#### Current Clients

##### Main VPS (main-vps)
- **IP**: 217.79.255.54
- **Domain**: consulting.sa
- **Status**: 🟢 Production Ready
- **Applications**: Agentic Site (AI SaaS Platform)
- **Services**: Next.js Frontend, Python Agent Backend
- **Security**: UFW + Fail2ban active
- **Docker**: Production-ready with security hardening

### 🌐 Domain Management Integration

#### Cloudflare Configuration
- **Primary Domain**: consulting.sa
- **Future Subdomain**: agent.consulting.sa
- **DNS Management**: Cloudflare
- **SSL**: Cloudflare + Let's Encrypt

#### Domain Mapping
```
consulting.sa → main-vps (217.79.255.54)
agent.consulting.sa → future agent-vps (planned)
```

### 📊 Lessons Learned & Best Practices

#### Successful Strategies
1. **Conservative Security Approach**: Always maintain SSH access during changes
2. **Comprehensive Documentation**: Log every action and configuration
3. **Docker Compose**: Reliable multi-service orchestration
4. **Health Checks**: Essential for production monitoring
5. **Management Scripts**: Automated tools for common operations

#### Common Pitfalls to Avoid
1. **Never change SSH port without proper testing**
2. **Always maintain root access as backup**
3. **Test firewall changes before enabling**
4. **Document every configuration change**
5. **Use staging environments for testing**

#### Production Deployment Checklist
- [ ] Security hardening (UFW + Fail2ban)
- [ ] Docker installation with security configuration
- [ ] Application deployment via Docker Compose
- [ ] Health checks and monitoring setup
- [ ] Management scripts installation
- [ ] SSL certificate configuration
- [ ] Domain DNS configuration
- [ ] Backup system setup

---

## 🔮 Future MCP Servers

### Planned Servers

#### Database Management Server
**Purpose**: Database administration, backup, and monitoring  
**Status**: 📋 Planned  
**Tools**: PostgreSQL, MySQL, MongoDB management  

#### Monitoring Server
**Purpose**: System monitoring, alerting, and performance tracking  
**Status**: 📋 Planned  
**Tools**: Prometheus, Grafana, log aggregation  

#### CI/CD Server
**Purpose**: Continuous integration and deployment automation  
**Status**: 📋 Planned  
**Tools**: GitHub Actions, deployment pipelines  

#### Security Server
**Purpose**: Security scanning, vulnerability assessment  
**Status**: 📋 Planned  
**Tools**: Security audits, compliance checking  

---

## 🚀 Usage Examples

### Complete VPS Setup Example
```python
# 1. Set up firewall
await mcp_client.call_tool("system_setup_firewall", {
    "connection_name": "main-vps",
    "allow_ports": [22, 80, 443, 3911, 8953]
})

# 2. Install fail2ban
await mcp_client.call_tool("system_setup_fail2ban", {
    "connection_name": "main-vps",
    "ssh_port": 22
})

# 3. Install Docker
await mcp_client.call_tool("docker_install", {
    "connection_name": "main-vps"
})

# 4. Deploy application
await mcp_client.call_tool("docker_compose_up", {
    "connection_name": "main-vps",
    "compose_file": "/opt/docker-apps/production/agentic-site/docker-compose.yml"
})

# 5. Set up Nginx reverse proxy
await mcp_client.call_tool("system_setup_nginx", {
    "connection_name": "main-vps",
    "domain": "consulting.sa",
    "proxy_pass": "http://localhost:3911"
})

# 6. Configure SSL
await mcp_client.call_tool("system_setup_ssl", {
    "connection_name": "main-vps",
    "domain": "consulting.sa",
    "email": "admin@consulting.sa"
})
```

### Monitoring and Maintenance Example
```python
# Monitor system resources
await mcp_client.call_tool("system_monitor_resources", {
    "connection_name": "main-vps",
    "samples": 5,
    "interval": 60
})

# Check Docker status
await mcp_client.call_tool("docker_status", {
    "connection_name": "main-vps"
})

# Create system backup
await mcp_client.call_tool("system_backup_create", {
    "connection_name": "main-vps",
    "backup_path": "/opt/backups",
    "include_dirs": ["/etc", "/opt/docker-apps", "/home"]
})
```

---

## 📞 Support & Troubleshooting

### Common Issues

#### SSH Connection Problems
- Verify connection credentials
- Check firewall rules
- Ensure SSH service is running
- Use console access if needed

#### Docker Issues
- Check container status with `docker_status`
- Review container logs
- Verify Docker daemon configuration
- Restart containers if needed

#### Application Deployment Issues
- Verify Docker Compose file syntax
- Check environment variables
- Ensure all required ports are open
- Monitor container health checks

### Emergency Procedures
1. **SSH Access Lost**: Use hosting provider console
2. **Firewall Locked Out**: Disable UFW via console
3. **Service Down**: Use automated restart scripts
4. **Data Loss**: Restore from backups

---

## 📈 Performance & Monitoring

### Key Metrics to Monitor
- **System Resources**: CPU, memory, disk usage
- **Container Health**: Docker container status
- **Network**: Port availability and connectivity
- **Security**: Failed login attempts, firewall logs
- **Application**: Response times, error rates

### Automated Monitoring
- Health checks for all services
- Resource usage alerts
- Security event notifications
- Backup completion status

---

*MCP Servers Documentation maintained by Kiro AI Assistant*  
*Last Updated: 2025-07-21*  
*Version: 1.0.0*