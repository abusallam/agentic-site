# 🚀 VPS/Docker Management System

## Overview

This comprehensive VPS/Docker management system provides standardized procedures for server deployment, management, and monitoring. It prevents common deployment issues like firewall misconfigurations, port conflicts, and SSL certificate problems through intelligent discovery, automated deployment, and robust error handling.

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph "VPS/Docker Management System"
        A[VPS Discovery Agent] --> B[Server Analysis Engine]
        B --> C[Deployment Orchestrator]
        C --> D[SSL Certificate Manager]
        D --> E[Monitoring & Health Checks]
        E --> F[Documentation Generator]
    end
    
    subgraph "External Services"
        G[Cloudflare API]
        H[VPS Server]
        I[Docker Registry]
        J[SSL Certificate Authority]
    end
    
    subgraph "Configuration Management"
        K[Environment Variables]
        L[Template Files]
        M[Deployment Configs]
    end
    
    A --> H
    D --> G
    C --> I
    D --> J
    C --> K
    C --> L
    C --> M
```

## 📁 Directory Structure

```
VPS/Docker/
├── README.md                    # This file
├── .env.template               # Environment variables template
├── config/                     # Configuration files
│   ├── vps-profiles/          # VPS server profiles
│   ├── deployment-templates/   # Deployment configurations
│   ├── ssl-configs/           # SSL certificate configurations
│   └── monitoring-configs/    # Monitoring configurations
├── scripts/                   # Management scripts
│   ├── core/                  # Core functionality scripts
│   ├── deployment/            # Deployment automation
│   ├── monitoring/            # Health checks and monitoring
│   ├── ssl/                   # SSL certificate management
│   └── maintenance/           # Backup and maintenance
├── templates/                 # Configuration templates
│   ├── docker-compose/        # Docker Compose templates
│   ├── nginx/                 # Nginx configuration templates
│   ├── caddy/                 # Caddy configuration templates
│   └── systemd/               # Systemd service templates
├── docs/                      # Documentation
│   ├── setup-guides/          # Setup and configuration guides
│   ├── troubleshooting/       # Troubleshooting guides
│   ├── architecture/          # Architecture documentation
│   └── examples/              # Usage examples
└── tools/                     # Utility tools
    ├── validators/            # Configuration validators
    ├── generators/            # Configuration generators
    └── diagnostics/           # Diagnostic tools
```

## 🚀 Quick Start

### 1. Initial Setup

```bash
# Copy environment template
cp .env.template .env

# Edit environment variables
nano .env

# Make scripts executable
chmod +x scripts/**/*.sh
```

### 2. Configure VPS Connection

```bash
# Set your VPS details in .env
VPS_IP=217.79.255.54
VPS_USERNAME=root
VPS_PASSWORD=your_password
SSH_KEY_PATH=~/.ssh/your_key
```

### 3. Discover VPS State

```bash
# Analyze current VPS state
./scripts/core/vps-discover.sh --analyze-all

# Check for port conflicts
./scripts/core/vps-discover.sh --check-ports

# List running containers
./scripts/core/vps-discover.sh --list-containers
```

### 4. Deploy Application

```bash
# Deploy to production
./scripts/deployment/deploy.sh --environment production --service myapp

# Deploy to development
./scripts/deployment/deploy.sh --environment development --service myapp
```

## 🔧 Environment Variables

### Required Variables
```bash
# VPS Connection
VPS_IP=217.79.255.54              # VPS server IP address
VPS_USERNAME=root                  # SSH username
VPS_PASSWORD=your_secure_password  # SSH password (backup auth)
SSH_KEY_PATH=~/.ssh/vps_key       # SSH private key path

# Cloudflare Integration
CLOUDFLARE_API_TOKEN=your_token    # Cloudflare API token
CLOUDFLARE_ZONE_ID=your_zone_id    # Cloudflare zone ID
CLOUDFLARE_EMAIL=your@email.com    # Cloudflare account email

# Deployment Configuration
DEFAULT_ENVIRONMENT=production     # Default deployment environment
DOCKER_REGISTRY=your_registry     # Docker registry URL
BACKUP_RETENTION_DAYS=30          # Backup retention period
```

### Optional Variables
```bash
# Monitoring
MONITORING_ENABLED=true           # Enable monitoring stack
ALERTS_WEBHOOK_URL=your_webhook   # Webhook for alerts
METRICS_RETENTION_DAYS=90         # Metrics retention period

# Security
FAIL2BAN_ENABLED=true            # Enable fail2ban
UFW_ENABLED=true                 # Enable UFW firewall
SSL_AUTO_RENEW=true              # Auto-renew SSL certificates
```

## 📋 Available Commands

### Core Management
```bash
# VPS Discovery and Analysis
./scripts/core/vps-discover.sh [--analyze-all|--check-ports|--list-containers|--security-audit]
./scripts/core/analyze-server.sh [--recommend-deployment|--check-conflicts|--optimize-resources]

# Server Provisioning
./scripts/core/provision-vps.sh --ip IP --password PASSWORD --environment ENV
./scripts/core/setup-security.sh --enable-firewall --configure-fail2ban
```

### Deployment Management
```bash
# Application Deployment
./scripts/deployment/deploy.sh --environment ENV --service SERVICE [--domain DOMAIN]
./scripts/deployment/rollback.sh --deployment-id ID
./scripts/deployment/update.sh --service SERVICE --image IMAGE:TAG

# Container Management
./scripts/deployment/start-services.sh --environment ENV
./scripts/deployment/stop-services.sh --environment ENV
./scripts/deployment/restart-services.sh --service SERVICE
```

### SSL Certificate Management
```bash
# SSL Operations
./scripts/ssl/ssl-manager.sh --setup-domain DOMAIN
./scripts/ssl/ssl-manager.sh --renew-certificates
./scripts/ssl/ssl-manager.sh --fix-ssl-issues --domain DOMAIN
./scripts/ssl/cloudflare-integration.sh --configure-dns DOMAIN
```

### Monitoring and Health Checks
```bash
# Health Monitoring
./scripts/monitoring/health-check.sh --check-all-services
./scripts/monitoring/monitor.sh --generate-report
./scripts/monitoring/setup-alerts.sh --webhook-url URL

# Performance Monitoring
./scripts/monitoring/performance-check.sh --detailed
./scripts/monitoring/resource-usage.sh --history 24h
```

### Maintenance and Backup
```bash
# Backup Operations
./scripts/maintenance/backup.sh --create --environment ENV
./scripts/maintenance/backup.sh --restore --backup-id ID
./scripts/maintenance/cleanup.sh --remove-old-backups

# System Maintenance
./scripts/maintenance/update-system.sh --security-only
./scripts/maintenance/optimize-performance.sh
./scripts/maintenance/rotate-logs.sh
```

## 🔍 VPS Discovery Process

The system automatically discovers and analyzes VPS state before deployment:

```mermaid
sequenceDiagram
    participant Agent as Deployment Agent
    participant VPS as VPS Server
    participant Analysis as Analysis Engine
    
    Agent->>VPS: 1. SSH Connect
    VPS->>Agent: 2. Connection Established
    Agent->>VPS: 3. Discover Services
    VPS->>Agent: 4. Service List
    Agent->>VPS: 5. Check Ports
    VPS->>Agent: 6. Port Status
    Agent->>VPS: 7. Analyze Resources
    VPS->>Agent: 8. Resource Info
    Agent->>Analysis: 9. Process Data
    Analysis->>Agent: 10. Recommendations
```

### Discovery Output Example
```json
{
  "server_info": {
    "ip": "217.79.255.54",
    "os": "Debian GNU/Linux 12",
    "memory_gb": 23,
    "disk_gb": 394,
    "cpu_cores": 4
  },
  "running_containers": [
    {
      "name": "agentic-frontend-prod",
      "status": "running",
      "ports": ["3000:3000"],
      "ssl_configured": true,
      "domain": "consulting.sa"
    },
    {
      "name": "tactical-ops-frontend",
      "status": "running", 
      "ports": ["3001:3000"],
      "ssl_configured": false,
      "domain": "tacticalops.console.ts"
    }
  ],
  "available_ports": [3002, 3003, 8001, 8002, 5679, 6380],
  "recommendations": [
    "Configure SSL for tactical-ops-frontend",
    "Port 3001 available for new deployment",
    "Consider load balancing for high traffic"
  ]
}
```

## 🔒 SSL Certificate Management

Automated SSL certificate management with Cloudflare integration:

### SSL Setup Process
```mermaid
graph LR
    A[Domain Request] --> B[DNS Validation]
    B --> C[Cloudflare API]
    C --> D[Certificate Generation]
    D --> E[Nginx Configuration]
    E --> F[SSL Verification]
    F --> G[Auto-Renewal Setup]
```

### SSL Commands
```bash
# Setup SSL for new domain
./scripts/ssl/ssl-manager.sh --setup-domain example.com

# Fix SSL issues for existing domain
./scripts/ssl/ssl-manager.sh --fix-ssl-issues --domain tacticalops.console.ts

# Renew all certificates
./scripts/ssl/ssl-manager.sh --renew-certificates

# Check certificate status
./scripts/ssl/ssl-manager.sh --check-status --domain example.com
```

## 📊 Monitoring and Alerts

Comprehensive monitoring system with health checks and alerting:

### Monitoring Stack
- **Health Checks**: Service availability and response time monitoring
- **Resource Monitoring**: CPU, memory, disk, and network usage
- **Container Monitoring**: Docker container status and performance
- **SSL Monitoring**: Certificate expiration and validity checks
- **Security Monitoring**: Failed login attempts and security events

### Alert Configuration
```yaml
alerts:
  health_check_failure:
    threshold: 3_consecutive_failures
    notification: webhook
    
  high_resource_usage:
    cpu_threshold: 80%
    memory_threshold: 85%
    disk_threshold: 90%
    
  ssl_expiration:
    warning_days: 30
    critical_days: 7
    
  security_events:
    failed_login_threshold: 5
    suspicious_activity: true
```

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### 1. Connection Issues
```bash
# Test VPS connection
./scripts/core/test-connection.sh

# Fix SSH key permissions
chmod 600 ~/.ssh/your_key
chmod 644 ~/.ssh/your_key.pub

# Reset SSH configuration
./scripts/core/reset-ssh-config.sh
```

#### 2. Port Conflicts
```bash
# Check port usage
./scripts/core/check-ports.sh --detailed

# Find alternative ports
./scripts/core/find-available-ports.sh --count 5

# Resolve port conflicts
./scripts/deployment/resolve-conflicts.sh --auto
```

#### 3. SSL Certificate Issues
```bash
# Diagnose SSL problems
./scripts/ssl/diagnose-ssl.sh --domain example.com

# Fix common SSL issues
./scripts/ssl/fix-ssl-issues.sh --domain example.com

# Regenerate certificates
./scripts/ssl/regenerate-cert.sh --domain example.com
```

#### 4. Container Issues
```bash
# Check container health
./scripts/monitoring/container-health.sh

# Restart failed containers
./scripts/deployment/restart-failed.sh

# View container logs
./scripts/monitoring/container-logs.sh --service SERVICE
```

## 📚 Documentation

### Setup Guides
- [Initial VPS Setup](docs/setup-guides/initial-vps-setup.md)
- [SSL Certificate Configuration](docs/setup-guides/ssl-setup.md)
- [Monitoring Setup](docs/setup-guides/monitoring-setup.md)
- [Backup Configuration](docs/setup-guides/backup-setup.md)

### Troubleshooting Guides
- [Connection Problems](docs/troubleshooting/connection-issues.md)
- [SSL Certificate Issues](docs/troubleshooting/ssl-issues.md)
- [Container Problems](docs/troubleshooting/container-issues.md)
- [Performance Issues](docs/troubleshooting/performance-issues.md)

### Architecture Documentation
- [System Architecture](docs/architecture/system-overview.md)
- [Deployment Flow](docs/architecture/deployment-flow.md)
- [Security Model](docs/architecture/security-model.md)
- [Monitoring Architecture](docs/architecture/monitoring-architecture.md)

## 🔄 Deployment Workflow

Standard deployment workflow for any application:

```mermaid
graph TD
    A[Start Deployment] --> B[Load Environment]
    B --> C[Discover VPS State]
    C --> D[Analyze Conflicts]
    D --> E{Conflicts Found?}
    E -->|Yes| F[Resolve Conflicts]
    E -->|No| G[Prepare Deployment]
    F --> G
    G --> H[Deploy Containers]
    H --> I[Configure Proxy]
    I --> J[Setup SSL]
    J --> K[Health Checks]
    K --> L{Health OK?}
    L -->|No| M[Rollback]
    L -->|Yes| N[Update Documentation]
    M --> O[Report Failure]
    N --> P[Deployment Complete]
```

## 🎯 Best Practices

### Security
- Always use SSH keys with password fallback
- Enable UFW firewall with minimal required ports
- Configure fail2ban for intrusion prevention
- Regular security updates and vulnerability scanning
- Encrypt sensitive configuration data

### Deployment
- Always backup before deployment
- Use health checks to verify deployment success
- Implement rollback procedures for failed deployments
- Monitor resource usage and performance
- Document all configuration changes

### Maintenance
- Regular system updates and security patches
- Automated backup and retention policies
- Log rotation and cleanup procedures
- Performance monitoring and optimization
- Certificate renewal and SSL monitoring

## 📞 Support and Maintenance

### Getting Help
1. Check the troubleshooting guides in `docs/troubleshooting/`
2. Run diagnostic scripts in `tools/diagnostics/`
3. Review system logs and monitoring data
4. Contact system administrator with detailed error information

### Maintenance Schedule
- **Daily**: Health checks and monitoring
- **Weekly**: Security updates and log rotation
- **Monthly**: Performance optimization and cleanup
- **Quarterly**: Full system backup and disaster recovery testing

---

**Last Updated**: January 2025  
**Version**: 1.0.0  
**Maintainer**: VPS/Docker Management System  
**Support**: Check documentation and diagnostic tools