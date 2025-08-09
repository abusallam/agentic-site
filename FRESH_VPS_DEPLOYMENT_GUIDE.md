# 🚀 Fresh VPS Deployment Guide - Professional Setup

This guide provides a complete, secure VPS setup process following server administration best practices.

## 🎯 Overview

Our deployment system provides:
- ✅ **Secure SSH setup** with key authentication + password backup
- ✅ **Professional port management** with admin backup access
- ✅ **Complete container separation** between environments
- ✅ **Production-ready security** with firewall and fail2ban
- ✅ **Automated management scripts** for monitoring and maintenance

## 🔧 Prerequisites

### Local Requirements
- Linux/macOS with bash
- Docker installed locally
- Git repository access
- `sshpass` (will be installed automatically)

### VPS Requirements
- Fresh Debian 12 (Bookworm) installation
- Root access with password
- Minimum 2GB RAM, 20GB storage
- Public IP address

## 🚀 Quick Start

### Step 1: Fresh VPS Setup (One-time)

```bash
./infrastructure/scripts/setup-fresh-vps.sh <IP> <ROOT_PASSWORD> <ENVIRONMENT>
```

**Examples:**
```bash
# Development environment
./infrastructure/scripts/setup-fresh-vps.sh 217.79.255.54 xxXNCpx9Cz development

# Production environment
./infrastructure/scripts/setup-fresh-vps.sh 192.168.1.100 mypassword production
```

**What this does:**
- ✅ Updates system and installs Docker, Nginx, security tools
- ✅ Sets up SSH keys for automation + strong password backup
- ✅ Configures firewall with proper port management
- ✅ Creates deployment directories and management scripts
- ✅ Optimizes system settings for production use

### Step 2: Deploy Application

```bash
./infrastructure/scripts/deploy-to-clean-vps.sh <SSH_ALIAS> <ENVIRONMENT>
```

**Examples:**
```bash
# Deploy to development
./infrastructure/scripts/deploy-to-clean-vps.sh agentic-217-79-255-54-development development

# Deploy to production
./infrastructure/scripts/deploy-to-clean-vps.sh agentic-192-168-1-100-production production
```

**What this does:**
- ✅ Builds optimized containers locally
- ✅ Transfers and deploys complete application stack
- ✅ Configures Nginx with rate limiting and security
- ✅ Sets up health checks and monitoring
- ✅ Tests all endpoints and services

## 🔐 Security Features

### SSH Access Management
- **Primary Access**: SSH keys (automated, secure)
- **Admin Backup**: Password on random high port (emergency access)
- **Port Management**: Standard port 22 + secure admin port

### Example SSH Access:
```bash
# Primary access (automated)
ssh agentic-217-79-255-54-development

# Admin backup access (emergency only)
ssh agentic-217-79-255-54-development-admin -p [ADMIN_PORT]
```

### Firewall Configuration
- **Incoming**: Deny all by default
- **SSH**: Port 22 + random admin port
- **Web**: Ports 80, 443
- **Application**: Environment-specific ports
- **Monitoring**: Prometheus, Grafana ports

### Security Hardening
- **Fail2ban**: Automatic IP blocking for failed attempts
- **Strong passwords**: Auto-generated 25-character admin passwords
- **Rate limiting**: Nginx-level request limiting
- **Security headers**: Complete HTTP security headers
- **Non-root containers**: All application containers run as non-root users

## 📊 What You Get

### Development Environment
- **Domain**: dev.consulting.sa
- **Frontend**: Port 3001
- **Backend**: Port 8001
- **Redis**: Port 6380
- **n8n**: Port 5679

### Production Environment
- **Domain**: consulting.sa
- **Frontend**: Port 3000
- **Backend**: Port 8000
- **Redis**: Port 6379
- **n8n**: Port 5678

### Services Included
- **Frontend**: Next.js with all your fixes (logo, navigation, pages)
- **Backend**: FastAPI with health checks and admin interface
- **Redis**: Optimized caching with persistence
- **n8n**: Workflow automation with web interface
- **Nginx**: Reverse proxy with security and performance optimization

## 🛠️ Management Commands

After setup, manage your VPS with these commands:

```bash
# Check system and application status
ssh <SSH_ALIAS> '/usr/local/bin/agentic-<environment>-status.sh'

# View application logs
ssh <SSH_ALIAS> '/usr/local/bin/agentic-<environment>-logs.sh'

# Restart all services
ssh <SSH_ALIAS> '/usr/local/bin/agentic-<environment>-restart.sh'

# Create backup
ssh <SSH_ALIAS> '/usr/local/bin/agentic-<environment>-backup.sh'

# Direct SSH access
ssh <SSH_ALIAS>
```

## 📁 File Structure Created

### On VPS
```
/opt/docker-apps/
├── development/
│   └── agentic-site/
│       ├── docker-compose.yml
│       └── .env
├── production/
│   └── agentic-site/
│       ├── docker-compose.yml
│       └── .env
└── shared/
    ├── ssl/
    ├── backups/
    └── logs/
```

### Local Files
```
~/.ssh/
├── agentic-217-79-255-54-development      # SSH private key
├── agentic-217-79-255-54-development.pub  # SSH public key
└── config                                 # SSH configuration

.env.development.vps                       # VPS-specific environment
.env.production.vps                        # VPS-specific environment
```

## 🔄 Multiple VPS Setup

You can set up multiple VPS instances:

```bash
# Development server
./infrastructure/scripts/setup-fresh-vps.sh 10.0.0.1 pass1 development

# Staging server
./infrastructure/scripts/setup-fresh-vps.sh 10.0.0.2 pass2 staging

# Production server
./infrastructure/scripts/setup-fresh-vps.sh 10.0.0.3 pass3 production
```

Each gets:
- ✅ Unique SSH alias and keys
- ✅ Separate admin ports
- ✅ Independent configurations
- ✅ Isolated environments

## 🚨 Emergency Procedures

### If SSH Key Access Fails
1. Use admin backup port:
   ```bash
   ssh root@<IP> -p <ADMIN_PORT>
   ```
2. Check SSH service: `systemctl status ssh`
3. Reset SSH config if needed

### If Application Won't Start
1. Check container status:
   ```bash
   ssh <SSH_ALIAS> 'cd /opt/docker-apps/<env>/agentic-site && docker-compose ps'
   ```
2. View logs:
   ```bash
   ssh <SSH_ALIAS> '/usr/local/bin/agentic-<env>-logs.sh'
   ```
3. Restart services:
   ```bash
   ssh <SSH_ALIAS> '/usr/local/bin/agentic-<env>-restart.sh'
   ```

### If Website is Down
1. Check Nginx: `ssh <SSH_ALIAS> 'systemctl status nginx'`
2. Test configuration: `ssh <SSH_ALIAS> 'nginx -t'`
3. Check firewall: `ssh <SSH_ALIAS> 'ufw status'`

## 📈 Monitoring and Health Checks

### Built-in Health Checks
- **Frontend**: HTTP health check on main port
- **Backend**: `/health` endpoint with detailed status
- **Redis**: Redis ping command
- **n8n**: HTTP availability check

### Monitoring URLs
- **Application Health**: https://your-domain/health
- **Backend Admin**: https://your-domain/backend/
- **API Documentation**: https://your-domain/backend/docs
- **n8n Interface**: https://your-domain/n8n/

### Log Management
- **Container logs**: Automatically rotated (10MB, 3 files)
- **System logs**: Standard logrotate configuration
- **Application logs**: Centralized in `/var/log/agentic-site/`

## 🔧 Customization

### Environment Variables
Edit `.env.<environment>.vps` locally, then redeploy:
```bash
# Edit configuration
nano .env.development.vps

# Redeploy with new configuration
./infrastructure/scripts/deploy-to-clean-vps.sh <SSH_ALIAS> <ENVIRONMENT>
```

### Nginx Configuration
The setup creates optimized Nginx configurations with:
- **Rate limiting**: API and general request limits
- **Compression**: Gzip for better performance
- **Security headers**: Complete security header set
- **Caching**: Static file caching with proper headers

### Container Customization
Modify the Dockerfiles in the deployment script for:
- **Additional dependencies**
- **Custom application configuration**
- **Security hardening**
- **Performance optimization**

## 🎯 Best Practices

### Security
- ✅ Always use SSH keys for automation
- ✅ Keep admin password secure and document it
- ✅ Regularly update system packages
- ✅ Monitor fail2ban logs for security events
- ✅ Use strong, unique passwords for all services

### Operations
- ✅ Test deployments in development first
- ✅ Create backups before major changes
- ✅ Monitor application logs regularly
- ✅ Keep deployment scripts updated
- ✅ Document any custom configurations

### Performance
- ✅ Monitor resource usage with status scripts
- ✅ Optimize container resource limits as needed
- ✅ Use Redis for caching where appropriate
- ✅ Monitor and optimize database queries
- ✅ Implement proper logging levels

## 📞 Support

### Troubleshooting Steps
1. **Check status**: Run status script
2. **View logs**: Check application and system logs
3. **Test connectivity**: Verify network and firewall
4. **Restart services**: Use restart script if needed
5. **Check resources**: Monitor CPU, memory, disk usage

### Common Issues
- **Port conflicts**: Check if ports are already in use
- **Permission issues**: Verify file ownership and permissions
- **Network issues**: Check firewall and DNS configuration
- **Container issues**: Verify Docker daemon and image integrity

---

**🔒 SECURITY REMINDER**: This setup creates secure, production-ready deployments. Always save the admin passwords and SSH key locations provided during setup!