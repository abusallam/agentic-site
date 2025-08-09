# 🏗️ Deployment Foundation Guide
## Complete VPS Setup and Container Management

**Purpose**: Establish the foundation for any VPS deployment with proper container separation, domain management, and automation.

**Status**: ✅ Production Tested  
**Last Updated**: January 8, 2025  

---

## 📋 Table of Contents

1. [Foundation Overview](#foundation-overview)
2. [VPS Initial Setup](#vps-initial-setup)
3. [Container Architecture](#container-architecture)
4. [Domain and SSL Management](#domain-and-ssl-management)
5. [Nginx Configuration](#nginx-configuration)
6. [Environment Management](#environment-management)
7. [Deployment Scripts](#deployment-scripts)
8. [Monitoring and Health Checks](#monitoring-and-health-checks)
9. [Troubleshooting Procedures](#troubleshooting-procedures)
10. [Future VPS Checklist](#future-vps-checklist)

---

## Foundation Overview

This guide establishes the complete foundation for deploying containerized applications on any VPS with proper separation of production and development environments.

### Core Principles
1. **Environment Separation**: Clear isolation between prod and dev
2. **Container Naming**: Consistent, descriptive naming convention
3. **Port Management**: Systematic port allocation
4. **Domain Management**: Multi-domain support with SSL
5. **Automation**: Scripts for all common operations
6. **Documentation**: Comprehensive knowledge base

### Architecture Summary
```
Internet (HTTPS) → Nginx (SSL Termination) → Docker Containers
                                           ├── Production Stack (3000, 8000, 6379, 5678)
                                           └── Development Stack (3001, 8001, 6380, 5679)
```

---

## VPS Initial Setup

### System Requirements
- **OS**: Ubuntu 20.04+ or Debian 11+
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 50GB minimum, 100GB recommended
- **Network**: Public IP with domain access

### Initial Server Configuration

#### 1. System Update and Package Installation
```bash
#!/bin/bash
# Initial VPS setup script

# Update system
apt-get update && apt-get upgrade -y

# Install essential packages
apt-get install -y \
    curl \
    wget \
    git \
    nginx \
    certbot \
    python3-certbot-nginx \
    docker.io \
    docker-compose-v2 \
    sshpass \
    htop \
    ufw \
    fail2ban

# Enable and start services
systemctl enable docker nginx
systemctl start docker nginx

# Add user to docker group (if not root)
# usermod -aG docker $USER

echo "✅ System packages installed and services started"
```

#### 2. Directory Structure Creation
```bash
#!/bin/bash
# Create standardized directory structure

# Main application directories
mkdir -p /opt/docker-apps/{production,development,shared}
mkdir -p /opt/backups/{manual,automated}
mkdir -p /opt/deployments/{scripts,configs,logs}
mkdir -p /var/log/deployments

# Set proper permissions
chown -R root:root /opt/docker-apps
chown -R root:root /opt/deployments
chmod -R 755 /opt/docker-apps
chmod -R 755 /opt/deployments

echo "✅ Directory structure created"
```

#### 3. Basic Security Setup
```bash
#!/bin/bash
# Basic security configuration

# Configure UFW firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Configure fail2ban
systemctl enable fail2ban
systemctl start fail2ban

echo "✅ Basic security configured"
```

---

## Container Architecture

### Naming Convention
```
Format: {service}-{component}-{environment}

Examples:
- consulting-frontend-prod
- consulting-backend-prod
- consulting-redis-prod
- consulting-n8n-prod
- consulting-frontend-dev
- consulting-backend-dev
```

### Network Separation
```yaml
# Production Network
networks:
  consulting-production:
    driver: bridge
    name: consulting-production

# Development Network  
networks:
  consulting-development:
    driver: bridge
    name: consulting-development
```

### Port Allocation Strategy
```
Production Stack:
- Frontend: 3000 (internal) → 443 (nginx)
- Backend: 8000 (internal) → 443/api (nginx)
- Redis: 6379 (internal)
- N8N: 5678 (internal) → 443/workflows (nginx)

Development Stack:
- Frontend: 3001 (internal) → 443 (nginx)
- Backend: 8001 (internal) → 443/api (nginx)
- Redis: 6380 (internal)
- N8N: 5679 (internal) → 443/workflows (nginx)
```

### Docker Compose Templates

#### Production Stack Template
```yaml
# docker-compose.production.yml
version: '3.8'

services:
  frontend-prod:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: ${PROJECT_NAME}-frontend-prod
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_SITE_URL=https://www.${DOMAIN}
      - NEXT_PUBLIC_API_URL=https://www.${DOMAIN}/api
    env_file:
      - .env.production
    restart: unless-stopped
    networks:
      - ${PROJECT_NAME}-production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  backend-prod:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: ${PROJECT_NAME}-backend-prod
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
    env_file:
      - .env.production
    restart: unless-stopped
    networks:
      - ${PROJECT_NAME}-production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis-prod:
    image: redis:7-alpine
    container_name: ${PROJECT_NAME}-redis-prod
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_prod_data:/data
    restart: unless-stopped
    networks:
      - ${PROJECT_NAME}-production

volumes:
  redis_prod_data:
    driver: local

networks:
  ${PROJECT_NAME}-production:
    driver: bridge
```

#### Development Stack Template
```yaml
# docker-compose.development.yml
version: '3.8'

services:
  frontend-dev:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: ${PROJECT_NAME}-frontend-dev
    ports:
      - "3001:3000"
    environment:
      - NODE_ENV=development
      - NEXT_PUBLIC_SITE_URL=https://dev.${DOMAIN}
      - NEXT_PUBLIC_API_URL=https://dev.${DOMAIN}/api
    env_file:
      - .env.development
    restart: unless-stopped
    networks:
      - ${PROJECT_NAME}-development

  backend-dev:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: ${PROJECT_NAME}-backend-dev
    ports:
      - "8001:8000"
    environment:
      - ENVIRONMENT=development
    env_file:
      - .env.development
    restart: unless-stopped
    networks:
      - ${PROJECT_NAME}-development

  redis-dev:
    image: redis:7-alpine
    container_name: ${PROJECT_NAME}-redis-dev
    ports:
      - "6380:6379"
    volumes:
      - redis_dev_data:/data
    restart: unless-stopped
    networks:
      - ${PROJECT_NAME}-development

volumes:
  redis_dev_data:
    driver: local

networks:
  ${PROJECT_NAME}-development:
    driver: bridge
```

---

## Domain and SSL Management

### DNS Configuration
```
Required DNS Records:
A     domain.com        → VPS_IP
CNAME www.domain.com    → domain.com
CNAME main.domain.com   → domain.com
CNAME dev.domain.com    → domain.com
```

### SSL Certificate Setup
```bash
#!/bin/bash
# SSL certificate setup script

DOMAIN="consulting.sa"  # Replace with your domain
EMAIL="admin@${DOMAIN}"

# Get SSL certificates for all domains
certbot --nginx \
    -d ${DOMAIN} \
    -d www.${DOMAIN} \
    -d main.${DOMAIN} \
    -d dev.${DOMAIN} \
    --non-interactive \
    --agree-tos \
    --email ${EMAIL} \
    --expand

# Set up automatic renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -

echo "✅ SSL certificates configured with auto-renewal"
```

### Certificate Management Commands
```bash
# Check certificate status
certbot certificates

# Test renewal
certbot renew --dry-run

# Manual renewal
certbot renew

# Add new domain to existing certificate
certbot --nginx -d domain.com -d www.domain.com -d new.domain.com --expand
```

---

## Nginx Configuration

### Production Configuration Template
```nginx
# /etc/nginx/sites-available/production.conf
server {
    listen 80;
    server_name domain.com www.domain.com main.domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name domain.com www.domain.com main.domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Frontend (Production - Port 3000)
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }

    # Backend API (Production - Port 8000)
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
```

### Development Configuration Template
```nginx
# /etc/nginx/sites-available/development.conf
server {
    listen 80;
    server_name dev.domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name dev.domain.com;

    # Same SSL configuration as production
    ssl_certificate /etc/letsencrypt/live/domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    # Development-specific headers
    add_header X-Environment "development" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;

    # Frontend (Development - Port 3001)
    location / {
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }

    # Backend API (Development - Port 8001)
    location /api/ {
        proxy_pass http://127.0.0.1:8001/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

### Nginx Management Commands
```bash
# Test configuration
nginx -t

# Reload configuration
systemctl reload nginx

# Restart nginx
systemctl restart nginx

# Enable site
ln -sf /etc/nginx/sites-available/production.conf /etc/nginx/sites-enabled/
ln -sf /etc/nginx/sites-available/development.conf /etc/nginx/sites-enabled/

# Disable default site
rm -f /etc/nginx/sites-enabled/default
```

---

## Environment Management

### Environment File Templates

#### Production Environment
```bash
# .env.production
NODE_ENV=production
NEXT_PUBLIC_SITE_URL=https://www.domain.com
NEXT_PUBLIC_API_URL=https://www.domain.com/api

# Database Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_key

# AI Services
GOOGLE_API_KEY=your_google_api_key
GEMINI_API_KEY=your_google_api_key

# Payment Processing
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_SECRET_KEY=your_stripe_secret_key

# Security
JWT_SECRET=your_jwt_secret
WEBHOOK_SECRET=your_webhook_secret

# Infrastructure
REDIS_URL=redis://redis-prod:6379
DATABASE_URL=your_production_database_url

# Project Configuration
PROJECT_NAME=consulting
DOMAIN=consulting.sa
```

#### Development Environment
```bash
# .env.development
NODE_ENV=development
NEXT_PUBLIC_SITE_URL=https://dev.domain.com
NEXT_PUBLIC_API_URL=https://dev.domain.com/api

# Same structure as production but with:
# - Development/test API keys
# - Development database URLs
# - Debug flags enabled
# - Different service endpoints

DEBUG=true
NEXT_TELEMETRY_DISABLED=1
```

---

## Deployment Scripts

### Master Deployment Script
```bash
#!/bin/bash
# master-deploy.sh - Complete deployment automation

set -e

PROJECT_NAME="consulting"
DOMAIN="consulting.sa"
VPS_IP="217.79.255.54"
VPS_USER="root"
VPS_PASS="your_password"

# Function to run SSH command
ssh_run() {
    sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_IP" "$1"
}

# Function to copy file to server
scp_file() {
    sshpass -p "$VPS_PASS" scp -o StrictHostKeyChecking=no "$1" "$VPS_USER@$VPS_IP:$2"
}

echo "🚀 MASTER DEPLOYMENT STARTING"
echo "Project: $PROJECT_NAME"
echo "Domain: $DOMAIN"
echo "VPS: $VPS_IP"
echo ""

# Step 1: Backup current deployment
echo "📦 Creating backup..."
ssh_run "mkdir -p /opt/backups/$(date +%Y%m%d_%H%M%S)"
ssh_run "cp -r /opt/docker-apps /opt/backups/$(date +%Y%m%d_%H%M%S)/" || echo "No existing deployment to backup"

# Step 2: Copy application files
echo "📁 Copying application files..."
# Add your file copying logic here

# Step 3: Deploy production stack
echo "🏭 Deploying production stack..."
ssh_run "cd /opt/docker-apps/production && docker compose -f docker-compose.production.yml down || true"
ssh_run "cd /opt/docker-apps/production && docker compose -f docker-compose.production.yml up -d --build"

# Step 4: Deploy development stack
echo "🧪 Deploying development stack..."
ssh_run "cd /opt/docker-apps/development && docker compose -f docker-compose.development.yml down || true"
ssh_run "cd /opt/docker-apps/development && docker compose -f docker-compose.development.yml up -d --build"

# Step 5: Health checks
echo "🔍 Running health checks..."
sleep 30

if ssh_run "curl -f -s https://www.$DOMAIN > /dev/null"; then
    echo "✅ Production frontend is healthy"
else
    echo "❌ Production frontend health check failed"
fi

if ssh_run "curl -f -s https://dev.$DOMAIN > /dev/null"; then
    echo "✅ Development frontend is healthy"
else
    echo "❌ Development frontend health check failed"
fi

echo "✅ DEPLOYMENT COMPLETED"
```

### Health Check Script
```bash
#!/bin/bash
# health-check.sh - Comprehensive system health check

PROJECT_NAME="consulting"
DOMAIN="consulting.sa"

echo "🔍 SYSTEM HEALTH CHECK"
echo "====================="

# Container status
echo "📦 Container Status:"
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

echo ""
echo "🌐 Endpoint Tests:"

# Test production endpoints
if curl -f -s https://www.$DOMAIN > /dev/null; then
    echo "✅ Production Frontend: https://www.$DOMAIN"
else
    echo "❌ Production Frontend: https://www.$DOMAIN"
fi

if curl -f -s https://dev.$DOMAIN > /dev/null; then
    echo "✅ Development Frontend: https://dev.$DOMAIN"
else
    echo "❌ Development Frontend: https://dev.$DOMAIN"
fi

# Test backend health endpoints
if curl -f -s http://localhost:8000/health > /dev/null; then
    echo "✅ Production Backend: http://localhost:8000/health"
else
    echo "❌ Production Backend: http://localhost:8000/health"
fi

if curl -f -s http://localhost:8001/health > /dev/null; then
    echo "✅ Development Backend: http://localhost:8001/health"
else
    echo "❌ Development Backend: http://localhost:8001/health"
fi

echo ""
echo "🔒 SSL Certificate Status:"
certbot certificates | grep -E "(Certificate Name|Expiry Date)" || echo "No certificates found"

echo ""
echo "💾 Disk Usage:"
df -h | grep -E "(Filesystem|/dev/)"

echo ""
echo "🧠 Memory Usage:"
free -h

echo ""
echo "⚡ System Load:"
uptime
```

---

## Monitoring and Health Checks

### Container Health Monitoring
```yaml
# Health check configuration for Docker Compose
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### System Monitoring Script
```bash
#!/bin/bash
# system-monitor.sh - Continuous system monitoring

LOG_FILE="/var/log/deployments/system-monitor.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

while true; do
    # Check container health
    UNHEALTHY=$(docker ps --filter "health=unhealthy" --format "{{.Names}}" | wc -l)
    if [ "$UNHEALTHY" -gt 0 ]; then
        log "⚠️  WARNING: $UNHEALTHY unhealthy containers detected"
        docker ps --filter "health=unhealthy" --format "table {{.Names}}\t{{.Status}}" | tee -a "$LOG_FILE"
    fi
    
    # Check disk space
    DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$DISK_USAGE" -gt 80 ]; then
        log "⚠️  WARNING: Disk usage is ${DISK_USAGE}%"
    fi
    
    # Check memory usage
    MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [ "$MEMORY_USAGE" -gt 90 ]; then
        log "⚠️  WARNING: Memory usage is ${MEMORY_USAGE}%"
    fi
    
    sleep 300  # Check every 5 minutes
done
```

---

## Troubleshooting Procedures

### Common Issues and Solutions

#### 1. Container Won't Start
```bash
# Diagnosis
docker logs container-name --tail 50
docker inspect container-name

# Common solutions
docker stop container-name
docker rm container-name
docker system prune -f
docker compose up -d --build
```

#### 2. Nginx 502 Bad Gateway
```bash
# Check container accessibility
curl -I http://localhost:3000/
curl -I http://localhost:8000/health

# Check nginx configuration
nginx -t
systemctl status nginx

# Check logs
tail -f /var/log/nginx/error.log
```

#### 3. SSL Certificate Issues
```bash
# Check certificate status
certbot certificates
openssl s_client -connect domain.com:443

# Renew certificates
certbot renew
systemctl reload nginx
```

#### 4. Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :3000
lsof -i :3000

# Kill process using port
kill -9 $(lsof -t -i:3000)
```

### Emergency Recovery Procedures
```bash
#!/bin/bash
# emergency-recovery.sh - Emergency system recovery

echo "🚨 EMERGENCY RECOVERY STARTING"

# Stop all containers
docker stop $(docker ps -q) || true

# Remove problematic containers
docker rm $(docker ps -aq) || true

# Clean up Docker system
docker system prune -af

# Restore from latest backup
LATEST_BACKUP=$(ls -t /opt/backups/ | head -1)
if [ -n "$LATEST_BACKUP" ]; then
    echo "📦 Restoring from backup: $LATEST_BACKUP"
    cp -r /opt/backups/$LATEST_BACKUP/* /opt/docker-apps/
fi

# Restart services
systemctl restart docker nginx

# Redeploy containers
cd /opt/docker-apps/production && docker compose up -d
cd /opt/docker-apps/development && docker compose up -d

echo "✅ EMERGENCY RECOVERY COMPLETED"
```

---

## Future VPS Checklist

### Pre-Deployment Checklist
- [ ] VPS meets minimum requirements (4GB RAM, 50GB storage)
- [ ] Domain DNS configured correctly
- [ ] SSL certificate plan established
- [ ] Environment variables prepared
- [ ] Backup strategy planned
- [ ] Monitoring approach defined

### Deployment Execution Checklist
- [ ] Run initial VPS setup script
- [ ] Create directory structure
- [ ] Configure SSL certificates
- [ ] Set up Nginx configurations
- [ ] Deploy Docker containers
- [ ] Configure environment variables
- [ ] Test all endpoints
- [ ] Set up monitoring
- [ ] Create backup procedures
- [ ] Document access credentials

### Post-Deployment Checklist
- [ ] All endpoints responding correctly
- [ ] SSL certificates valid and auto-renewing
- [ ] Containers healthy and restarting properly
- [ ] Monitoring and alerting configured
- [ ] Backup procedures tested
- [ ] Documentation updated
- [ ] Team access configured
- [ ] Emergency procedures documented

### Validation Commands
```bash
# Complete system validation
./health-check.sh

# Container validation
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

# Endpoint validation
curl -I https://www.domain.com
curl -I https://dev.domain.com
curl -I http://localhost:3000/
curl -I http://localhost:8000/health

# SSL validation
openssl s_client -connect domain.com:443 -servername domain.com

# Performance validation
curl -w "@curl-format.txt" -o /dev/null -s https://www.domain.com
```

---

## Summary

This foundation guide provides everything needed to establish a professional, production-ready deployment on any VPS with:

- ✅ **Proper Environment Separation**: Clear prod/dev isolation
- ✅ **Container Management**: Systematic naming and networking
- ✅ **Domain and SSL**: Multi-domain support with automation
- ✅ **Nginx Configuration**: Professional reverse proxy setup
- ✅ **Deployment Automation**: Scripts for all common operations
- ✅ **Monitoring and Health Checks**: Comprehensive system monitoring
- ✅ **Troubleshooting Procedures**: Battle-tested solutions
- ✅ **Documentation**: Complete knowledge base

**This foundation has been battle-tested in production and provides a solid base for any containerized application deployment.**