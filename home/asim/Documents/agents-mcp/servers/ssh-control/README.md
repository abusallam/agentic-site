# 🚀 Enhanced SSH Control MCP Server with Docker Integration

A comprehensive Model Context Protocol (MCP) server that combines SSH-based remote administration with full Docker management capabilities for Debian 12 servers.

## 🌟 Key Features

### 🔌 SSH Connection Management
- **ssh_connect**: Connect to remote servers (password/key authentication)
- **ssh_disconnect**: Safely disconnect from servers
- **ssh_list_connections**: View all connection statuses
- **Multi-server support**: Manage multiple servers simultaneously

### 💻 System Administration
- **ssh_execute**: Execute any command on remote servers
- **ssh_get_system_info**: Comprehensive system information
- **ssh_get_security_status**: Security configuration analysis
- **ssh_install_package**: Install packages via apt
- **system_monitor_resources**: Real-time resource monitoring
- **system_backup_create**: Automated system backups

### 🐳 Complete Docker Management
- **docker_install**: Install Docker with security best practices
- **docker_status**: Comprehensive Docker system status
- **Container Management**:
  - `docker_list_containers`: List all containers
  - `docker_create_container`: Create new containers
  - `docker_start_container` / `docker_stop_container`: Control containers
  - `docker_remove_container`: Remove containers
  - `docker_get_logs`: Retrieve container logs
- **Image Management**:
  - `docker_list_images`: List Docker images
  - `docker_pull_image`: Pull images from registries
  - `docker_remove_image`: Remove unused images
- **Network Management**:
  - `docker_list_networks`: List Docker networks
  - `docker_create_network` / `docker_remove_network`: Manage networks
- **Volume Management**:
  - `docker_list_volumes`: List Docker volumes
  - `docker_create_volume` / `docker_remove_volume`: Manage volumes
- **Docker Compose**:
  - `docker_compose_up` / `docker_compose_down`: Manage multi-container applications

### 🛡️ Advanced Security & System Setup
- **system_setup_firewall**: Configure UFW with custom rules
- **system_setup_fail2ban**: Intrusion prevention system
- **system_create_user**: Create users with SSH keys and sudo access
- **system_setup_nginx**: Install and configure Nginx reverse proxy
- **system_setup_ssl**: Automated SSL certificates with Let's Encrypt

### 📁 File Management
- **ssh_upload_file** / **ssh_download_file**: Secure file transfers via SFTP
- **Automated backups**: Compressed system backups with scheduling

## 🎯 Intelligent Prompts

### 🔒 VPS Security Setup
```
Prompt: vps_security_setup
- Complete security hardening guide
- User management and SSH configuration
- Firewall and intrusion prevention
- Docker security implementation
- Monitoring and logging setup
```

### 🐳 Docker Compose Deployment
```
Prompt: docker_compose_deploy
- Application deployment planning
- Security configuration
- Service architecture design
- SSL and reverse proxy setup
- Health checks and monitoring
```

### 📊 System Monitoring
```
Prompt: system_monitoring
- Comprehensive monitoring stack
- Alerting and notifications
- Performance optimization
- Security monitoring
```

## 📊 Real-time Resources

- **System Info**: Live system metrics and status
- **Docker Status**: Container and service health
- **Security Status**: Security configuration monitoring

## 🚀 Quick Start

### Installation
```bash
cd /home/asim/Documents/agents-mcp/servers/ssh-control
uv sync
```

### Configuration
Server automatically loads VPS credentials from environment:
- `VPS_HOST=217.79.255.54`
- `VPS_USER=root`
- `VPS_PASSWORD=SeZ7cc5uiy`
- `VPS_PORT=22`

### Example Workflows

#### 🔧 Complete VPS Setup
1. **Connect**: `ssh_connect`
2. **Security Hardening**: `system_setup_firewall`, `system_setup_fail2ban`
3. **Docker Installation**: `docker_install`
4. **Web Server**: `system_setup_nginx`, `system_setup_ssl`
5. **Monitoring**: `system_monitor_resources`

#### 🐳 Docker Application Deployment
1. **Prepare Environment**: `docker_create_network`
2. **Deploy Database**: `docker_create_container` (PostgreSQL/MySQL)
3. **Deploy Application**: `docker_compose_up`
4. **Configure Proxy**: `system_setup_nginx` with reverse proxy
5. **Monitor**: `docker_status`, `docker_get_logs`

#### 🛡️ Security Management
1. **User Management**: `system_create_user` with SSH keys
2. **Firewall Rules**: `system_setup_firewall` with custom ports
3. **Intrusion Prevention**: `system_setup_fail2ban`
4. **SSL Certificates**: `system_setup_ssl` for domains
5. **Security Audit**: `ssh_get_security_status`

## 🔧 Advanced Capabilities

### Docker Container Creation
```python
# Example: Deploy a web application
docker_create_container(
    image="nginx:alpine",
    name="web-server",
    ports={"80": "80", "443": "443"},
    volumes={"/opt/web": "/usr/share/nginx/html"},
    environment={"ENV": "production"},
    network="app-network",
    restart="unless-stopped"
)
```

### System User Creation
```python
# Example: Create admin user with SSH key
system_create_user(
    username="admin",
    ssh_key="ssh-rsa AAAAB3NzaC1yc2E...",
    sudo_access=True
)
```

### Nginx Reverse Proxy
```python
# Example: Set up reverse proxy
system_setup_nginx(
    domain="app.example.com",
    proxy_pass="http://localhost:3000"
)
```

## 🛡️ Security Features

- **Multi-layer Security**: Firewall, fail2ban, SSH hardening
- **Container Security**: Non-root users, resource limits, network isolation
- **SSL Automation**: Let's Encrypt integration with auto-renewal
- **Secure Secrets**: Environment-based credential management
- **Audit Logging**: Comprehensive activity tracking

## 📋 Monitoring & Maintenance

- **Real-time Metrics**: CPU, memory, disk, network monitoring
- **Container Health**: Docker service status and logs
- **Security Monitoring**: Failed logins, intrusion attempts
- **Automated Backups**: Scheduled system and data backups
- **Alert System**: Configurable notifications and thresholds

## 🔗 Integration

- **MCP Protocol**: Full Model Context Protocol compliance
- **Multi-server**: Manage multiple VPS instances
- **Environment Variables**: Secure credential storage
- **Docker Compose**: Full multi-container application support
- **Let's Encrypt**: Automated SSL certificate management

## 📚 Documentation

- **VPS_SECURITY_SETUP.md**: Complete security hardening guide
- **DOCKER_APP_DEPLOYMENT.md**: Application deployment templates
- **VPS_ADMINISTRATION_LOG.md**: Activity tracking and logging

## 🚨 Production Ready

This MCP server is designed for production use with:
- ✅ Comprehensive error handling
- ✅ Security best practices
- ✅ Resource monitoring
- ✅ Automated backups
- ✅ SSL certificate management
- ✅ Container orchestration
- ✅ Multi-server support

Perfect for managing production VPS instances, deploying containerized applications, and maintaining secure, scalable infrastructure.