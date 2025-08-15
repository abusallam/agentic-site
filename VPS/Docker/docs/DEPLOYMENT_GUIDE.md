# VPS/Docker Management System - Deployment Guide

## Overview

This comprehensive guide covers the complete VPS/Docker management system designed to standardize server deployments, prevent configuration errors, and provide robust management tools for any VPS deployment.

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph "Local Development"
        A[Developer] --> B[VPS/Docker Scripts]
        B --> C[Environment Configuration]
    end
    
    subgraph "VPS Server (217.79.255.54)"
        D[Debian 12 Server]
        E[Docker Engine]
        F[Nginx Proxy]
        G[SSL Certificates]
        H[Application Containers]
        I[Monitoring Stack]
    end
    
    subgraph "Management Tools"
        J[VPS Discovery]
        K[Server Analysis]
        L[Deployment Orchestrator]
        M[SSL Manager]
        N[Health Monitor]
        O[Backup System]
    end
    
    B --> D
    J --> D
    K --> D
    L --> E
    M --> F
    M --> G
    N --> H
    O --> H
    
    E --> H
    F --> H
    G --> F
```

## 🚀 Quick Start

### 1. Initial Setup

```bash
# Navigate to VPS/Docker directory
cd VPS/Docker

# Copy environment template
cp .env.template .env

# Edit environment variables
nano .env
```

### 2. Configure Environment Variables

Edit `.env` file with your VPS details:

```bash
# VPS Connection
VPS_IP=217.79.255.54
VPS_USERNAME=root
VPS_PASSWORD=your_secure_password

# SSH Configuration (optional)
SSH_KEY_PATH=~/.ssh/vps_key

# Cloudflare Integration (optional)
CLOUDFLARE_API_TOKEN=your_token
CLOUDFLARE_ZONE_ID=your_zone_id
```

### 3. Discover VPS State

```bash
# Run comprehensive VPS discovery
./scripts/core/vps-discover.sh --analyze-all

# Analyze server for deployment recommendations
./scripts/core/analyze-server.sh --comprehensive
```

### 4. Deploy Your Application

```bash
# Deploy to production
./scripts/deployment/deploy.sh --environment production --service myapp --domain myapp.com

# Deploy to development
./scripts/deployment/deploy.sh --environment development --service myapp
```

## 📋 Available Scripts

### Core Management Scripts

#### VPS Discovery (`scripts/core/vps-discover.sh`)
Intelligent server state analysis before deployment.

```bash
# Full analysis
./scripts/core/vps-discover.sh --analyze-all

# Check available ports
./scripts/core/vps-discover.sh --check-ports

# List running containers
./scripts/core/vps-discover.sh --list-containers

# Security audit
./scripts/core/vps-discover.sh --security-audit
```

#### Server Analysis (`scripts/core/analyze-server.sh`)
Process discovery data and provide deployment recommendations.

```bash
# Comprehensive analysis
./scripts/core/analyze-server.sh --comprehensive

# Check port conflicts
./scripts/core/analyze-server.sh --check-conflicts

# Resource optimization
./scripts/core/analyze-server.sh --optimize-resources
```

### Deployment Scripts

#### Deployment Orchestrator (`scripts/deployment/deploy.sh`)
Standardized container deployment with conflict resolution.

```bash
# Production deployment
./scripts/deployment/deploy.sh --environment production --service myapp --domain myapp.com

# Development deployment
./scripts/deployment/deploy.sh --environment development --service testapp

# Staging deployment
./scripts/deployment/deploy.sh --environment staging --service myapp --domain staging.myapp.com
```

### SSL Management Scripts

#### SSL Manager (`scripts/ssl/ssl-manager.sh`)
Automated SSL certificate management and proxy configuration.

```bash
# Setup SSL for domain
./scripts/ssl/ssl-manager.sh --setup-domain example.com

# Fix SSL issues
./scripts/ssl/ssl-manager.sh --fix-ssl-issues --domain example.com

# Test SSL configuration
./scripts/ssl/ssl-manager.sh --test-ssl example.com
```

### Monitoring Scripts

#### Health Check (`scripts/monitoring/health-check.sh`)
Comprehensive system and application health monitoring.

```bash
# Full health check
./scripts/monitoring/health-check.sh --check-all-services

# Generate health report
./scripts/monitoring/health-check.sh --generate-report

# Setup automated alerts
./scripts/monitoring/health-check.sh --setup-alerts
```

### Maintenance Scripts

#### Backup System (`scripts/maintenance/backup.sh`)
Automated backup and restore operations.

```bash
# Create backup
./scripts/maintenance/backup.sh --create

# List backups
./scripts/maintenance/backup.sh --list

# Restore from backup
./scripts/maintenance/backup.sh --restore backup-name.tar.gz

# Setup automated backups
./scripts/maintenance/backup.sh --setup-automated
```

## 🔧 Configuration Management

### Environment-Specific Configurations

The system supports multiple environments with automatic port allocation:

- **Production**: Ports 3000, 8000, 6379, 5678
- **Development**: Ports 3001, 8001, 6380, 5679  
- **Staging**: Ports 3002, 8002, 6381, 5680

### Docker Compose Templates

The system automatically generates Docker Compose configurations:

```yaml
version: '3.8'
services:
  myapp-frontend:
    image: myapp/frontend:latest
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    networks:
      - myapp-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  myapp-backend:
    image: myapp/backend:latest
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
    networks:
      - myapp-network
    restart: unless-stopped

networks:
  myapp-network:
    driver: bridge
```

## 🔒 SSL Certificate Management

### Automatic SSL Configuration

The SSL manager provides:

- Self-signed certificate generation for testing
- Nginx configuration with security headers
- HTTP to HTTPS redirects
- WebSocket support
- Static file caching

### Cloudflare Integration

Configure Cloudflare API credentials for:

- Automatic DNS management
- Origin SSL certificates
- CDN and DDoS protection

## 📊 Monitoring and Health Checks

### System Monitoring

The health check system monitors:

- **System Resources**: CPU, memory, disk usage
- **Container Health**: Docker container status and health checks
- **Application Health**: HTTP endpoint testing
- **Security Status**: Firewall, fail2ban, SSH security
- **SSL Certificates**: Certificate validity and expiration

### Automated Alerts

Setup automated alerts for:

- High resource usage
- Container failures
- Security events
- SSL certificate expiration

## 💾 Backup and Recovery

### Automated Backups

The backup system includes:

- **Docker Volumes**: All container data
- **Configurations**: Nginx, deployment configs
- **SSL Certificates**: All SSL certificates
- **System Configs**: Firewall, security settings

### Backup Schedule

- **Daily Backups**: Automated at 2 AM
- **Retention**: 30 days (configurable)
- **Compression**: Gzip compression for space efficiency
- **Integrity Checks**: Automatic backup verification

## 🛠️ Troubleshooting

### Common Issues

#### Connection Problems
```bash
# Test VPS connection
./scripts/core/vps-discover.sh --test-connection

# Check SSH configuration
ssh -v root@217.79.255.54
```

#### Port Conflicts
```bash
# Check port usage
./scripts/core/vps-discover.sh --check-ports

# Find available ports
./scripts/core/analyze-server.sh --check-conflicts
```

#### SSL Issues
```bash
# Test SSL configuration
./scripts/ssl/ssl-manager.sh --test-ssl domain.com

# Fix SSL problems
./scripts/ssl/ssl-manager.sh --fix-ssl-issues --domain domain.com
```

#### Container Problems
```bash
# Check container health
./scripts/monitoring/health-check.sh --container-health

# View container logs
ssh root@217.79.255.54 'docker logs container-name'
```

### Log Locations

- **Discovery Logs**: `logs/vps-discovery.log`
- **Deployment Logs**: `logs/deployment.log`
- **SSL Manager Logs**: `logs/ssl-manager.log`
- **Health Check Logs**: `logs/health-check.log`
- **Backup Logs**: `logs/backup.log`

## 📚 Advanced Usage

### Custom Deployments

For custom deployment scenarios:

1. **Modify Environment Variables**: Adjust ports and configurations
2. **Custom Docker Compose**: Create custom templates in `templates/docker-compose/`
3. **Custom Nginx Config**: Create templates in `templates/nginx/`
4. **Custom SSL Setup**: Integrate with different certificate providers

### Multi-VPS Management

To manage multiple VPS servers:

1. **Create Environment Files**: `.env.server1`, `.env.server2`
2. **Use Environment Variables**: `VPS_IP`, `VPS_USERNAME`, `VPS_PASSWORD`
3. **Switch Configurations**: Copy appropriate `.env` file

### Integration with CI/CD

Integrate with CI/CD pipelines:

```bash
# In your CI/CD pipeline
export VPS_IP=your-server-ip
export VPS_USERNAME=root
export VPS_PASSWORD=your-password

# Deploy from CI/CD
./VPS/Docker/scripts/deployment/deploy.sh --environment production --service myapp
```

## 🔐 Security Best Practices

### Server Security

- **Firewall Configuration**: UFW with minimal required ports
- **Fail2ban Protection**: Intrusion prevention system
- **SSH Security**: Key-based authentication preferred
- **Regular Updates**: Automated security updates

### Container Security

- **Resource Limits**: CPU and memory limits for containers
- **Health Checks**: Comprehensive health monitoring
- **Network Isolation**: Docker networks for service communication
- **Image Security**: Regular image updates and scanning

### SSL Security

- **Strong Ciphers**: Modern TLS protocols and ciphers
- **Security Headers**: HSTS, CSP, and other security headers
- **Certificate Management**: Automated renewal and monitoring

## 📈 Performance Optimization

### Resource Optimization

- **Container Limits**: Appropriate CPU and memory limits
- **Nginx Caching**: Static file caching and compression
- **Database Optimization**: Connection pooling and indexing
- **Monitoring**: Resource usage tracking and alerts

### Scaling Strategies

- **Horizontal Scaling**: Load balancer configuration
- **Vertical Scaling**: Resource monitoring and upgrades
- **Container Orchestration**: Docker Swarm or Kubernetes migration
- **CDN Integration**: Cloudflare or other CDN services

## 🎯 Best Practices

### Development Workflow

1. **Local Testing**: Test configurations locally first
2. **Staging Deployment**: Deploy to staging before production
3. **Health Monitoring**: Monitor deployment health
4. **Backup Before Changes**: Always backup before major changes

### Maintenance Schedule

- **Daily**: Health checks and monitoring
- **Weekly**: Security updates and log review
- **Monthly**: Performance optimization and cleanup
- **Quarterly**: Full system audit and backup testing

## 📞 Support and Maintenance

### Getting Help

1. **Check Logs**: Review relevant log files
2. **Run Diagnostics**: Use health check and discovery scripts
3. **Review Documentation**: Check specific component documentation
4. **Test Configurations**: Use test commands to verify setup

### Maintenance Tasks

- **Regular Backups**: Ensure automated backups are working
- **Security Updates**: Keep system and containers updated
- **Certificate Renewal**: Monitor SSL certificate expiration
- **Performance Monitoring**: Track resource usage trends
- **Log Rotation**: Manage log file sizes and retention

---

**Last Updated**: August 13, 2025  
**Version**: 1.0.0  
**Status**: Production Ready  
**Next Review**: Monthly system assessment