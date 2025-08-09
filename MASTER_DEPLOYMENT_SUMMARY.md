# 🚀 Master Deployment Guide - consulting.sa
## Complete Knowledge Base from Production Experience

**Status**: ✅ Production Ready  
**Last Updated**: January 8, 2025  
**Experience**: 2+ weeks of real-world deployment challenges solved  

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Critical Lessons Learned](#critical-lessons-learned)
4. [Step-by-Step Deployment Process](#step-by-step-deployment-process)
5. [Container Management](#container-management)
6. [Nginx Configuration](#nginx-configuration)
7. [Domain and SSL Setup](#domain-and-ssl-setup)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Scripts and Automation](#scripts-and-automation)
10. [Future VPS Deployment Checklist](#future-vps-deployment-checklist)

---

## Executive Summary

This guide documents the complete process of deploying a production-ready Next.js + Python ADK application with proper separation of production and development environments. It includes all the mistakes, solutions, and best practices learned through real-world deployment experience.

### What We Built
- **Production Stack**: consulting.sa, www.consulting.sa, main.consulting.sa
- **Development Stack**: dev.consulting.sa
- **Separated Containers**: Clear naming and port separation
- **Professional Nginx**: SSL, security headers, proper routing
- **Automated Scripts**: Deployment, troubleshooting, and maintenance

### Key Achievements
- ✅ Fixed Next.js SSR errors in production
- ✅ Separated production and development environments
- ✅ Proper container naming and networking
- ✅ Multiple domain support with SSL
- ✅ Comprehensive documentation and scripts

---

## Architecture Overview

### Final Working Architecture

```
Internet
    ↓ (HTTPS)
Nginx Reverse Proxy (SSL Termination)
    ↓
┌─────────────────────┬─────────────────────┐
│   Production Stack  │  Development Stack  │
│   (Port 3000, 8000) │  (Port 3001, 8001)  │
├─────────────────────┼─────────────────────┤
│ consulting-frontend-│ consulting-frontend-│
│ prod                │ dev                 │
│ consulting-backend- │ consulting-backend- │
│ prod                │ dev                 │
│ consulting-redis-   │ consulting-redis-   │
│ prod                │ dev                 │
│ consulting-n8n-prod │ consulting-n8n-dev  │
└─────────────────────┴─────────────────────┘
```

### Domain Mapping
- **consulting.sa** → Production Frontend (Port 3000)
- **www.consulting.sa** → Production Frontend (Port 3000)
- **main.consulting.sa** → Production Frontend (Port 3000)
- **dev.consulting.sa** → Development Frontend (Port 3001)

### Port Allocation
```
Production Stack:
- Frontend: 3000 (internal) → 443 (nginx)
- Backend: 8000 (internal) → 443/api (nginx)
- Redis: 6379
- N8N: 5678

Development Stack:
- Frontend: 3001 (internal) → 443 (nginx)
- Backend: 8001 (internal) → 443/api (nginx)
- Redis: 6380
- N8N: 5679
```

---

## Critical Lessons Learned

### 🚨 Major Issues We Solved

#### 1. Next.js SSR Error
**Problem**: `ssr: false` is not allowed with `next/dynamic` in Server Components
**Solution**: Create proper client component wrapper
```typescript
// ❌ Wrong (in Server Component)
const ChatbotWidget = dynamic(() => import('./ChatbotWidget'), {
  ssr: false,
  loading: () => null
})

// ✅ Correct (separate client component)
'use client'
const ChatbotWidget = dynamic(() => import('./ChatbotWidget'), {
  ssr: false,
  loading: () => null
})
```

#### 2. Container Naming Conflicts
**Problem**: Both prod and dev containers had same names
**Solution**: Proper naming convention
```yaml
# ❌ Wrong
container_name: agentic-frontend-prod  # Conflicts with dev

# ✅ Correct
container_name: consulting-frontend-prod  # Clear separation
container_name: consulting-frontend-dev
```

#### 3. Directory Structure Confusion
**Problem**: Nested directory structures causing build failures
**Solution**: Understand the actual VPS structure
```bash
# Actual structure on VPS
/opt/docker-apps/production/agentic-site/agentic-site/
                                        ↑ nested structure
```

#### 4. Manual File Copying Issues
**Problem**: Manual copying leads to inconsistencies and errors
**Solution**: Automated GitHub-based deployment (next step)

### 🎯 Best Practices Established

1. **Always use proper container naming**: `service-component-environment`
2. **Separate networks**: Different Docker networks for prod/dev
3. **Port consistency**: Maintain clear port allocation strategy
4. **Health checks**: Implement proper container health monitoring
5. **Backup before changes**: Always backup before major changes
6. **Test locally first**: Build and test containers locally when possible

---

## Step-by-Step Deployment Process

### Phase 1: VPS Preparation

#### 1.1 Initial Server Setup
```bash
# Update system
apt-get update && apt-get upgrade -y

# Install required packages
apt-get install -y docker.io docker-compose-v2 nginx certbot python3-certbot-nginx sshpass curl wget git

# Enable Docker
systemctl enable docker && systemctl start docker

# Create directory structure
mkdir -p /opt/docker-apps/{production,development,shared}
mkdir -p /opt/backups
mkdir -p /var/log/deployments
```

#### 1.2 SSL Certificate Setup
```bash
# Get SSL certificates for all domains
certbot --nginx -d consulting.sa -d www.consulting.sa -d main.consulting.sa -d dev.consulting.sa --non-interactive --agree-tos --email admin@consulting.sa
```

### Phase 2: Container Configuration

#### 2.1 Production Docker Compose
```yaml
# /opt/docker-apps/production/agentic-site/docker-compose.production-separated.yml
version: '3.8'

services:
  frontend-prod:
    build:
      context: ./agentic-site/frontend
      dockerfile: ../Dockerfile.frontend
    container_name: consulting-frontend-prod
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_SITE_URL=https://www.consulting.sa
    networks:
      - consulting-production
    restart: unless-stopped

  backend-prod:
    build:
      context: ./agentic-site/agent
      dockerfile: ../Dockerfile.backend
    container_name: consulting-backend-prod
    ports:
      - "8000:8000"
    networks:
      - consulting-production
    restart: unless-stopped

networks:
  consulting-production:
    driver: bridge
```

#### 2.2 Development Docker Compose
```yaml
# Similar structure but with:
# - Different container names (consulting-*-dev)
# - Different ports (3001, 8001, 6380, 5679)
# - Different network (consulting-development)
# - Development environment variables
```

### Phase 3: Nginx Configuration

#### 3.1 Production Nginx Config
```nginx
# /etc/nginx/sites-available/production.conf
server {
    listen 443 ssl http2;
    server_name consulting.sa www.consulting.sa main.consulting.sa;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/consulting.sa/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/consulting.sa/privkey.pem;

    # Security Headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    # Frontend (Production - Port 3000)
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API (Production - Port 8000)
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 3.2 Development Nginx Config
```nginx
# /etc/nginx/sites-available/development.conf
server {
    listen 443 ssl http2;
    server_name dev.consulting.sa;

    # Same SSL config as production

    # Frontend (Development - Port 3001)
    location / {
        proxy_pass http://127.0.0.1:3001;
        # Same proxy headers
    }

    # Backend API (Development - Port 8001)
    location /api/ {
        proxy_pass http://127.0.0.1:8001/;
        # Same proxy headers
    }
}
```

### Phase 4: Deployment Execution

#### 4.1 Deploy Production Stack
```bash
cd /opt/docker-apps/production/agentic-site
docker compose -f docker-compose.production-separated.yml up -d --build
```

#### 4.2 Deploy Development Stack
```bash
cd /opt/docker-apps/development/agentic-site
docker compose -f docker-compose.development-separated.yml up -d --build
```

#### 4.3 Verify Deployment
```bash
# Check container status
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

# Test endpoints
curl -I https://www.consulting.sa
curl -I https://dev.consulting.sa
curl -I http://localhost:3000/
curl -I http://localhost:8000/health
```

---

## Container Management

### Container Naming Convention
```
Format: {service}-{component}-{environment}

Production:
- consulting-frontend-prod
- consulting-backend-prod
- consulting-redis-prod
- consulting-n8n-prod

Development:
- consulting-frontend-dev
- consulting-backend-dev
- consulting-redis-dev
- consulting-n8n-dev
```

### Common Container Commands
```bash
# View all containers
docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

# Stop production stack
docker stop consulting-frontend-prod consulting-backend-prod consulting-redis-prod consulting-n8n-prod

# Remove containers
docker rm consulting-frontend-prod consulting-backend-prod consulting-redis-prod consulting-n8n-prod

# View logs
docker logs consulting-frontend-prod --tail 50
docker logs consulting-backend-prod --tail 50

# Execute commands in container
docker exec -it consulting-frontend-prod sh
docker exec -it consulting-backend-prod bash
```

### Health Monitoring
```bash
# Check container health
docker inspect consulting-frontend-prod | grep -A 10 "Health"

# Monitor resource usage
docker stats consulting-frontend-prod consulting-backend-prod

# View container processes
docker top consulting-frontend-prod
```

---

## Nginx Configuration

### Configuration Files Structure
```
/etc/nginx/
├── sites-available/
│   ├── production.conf     # Production domains
│   └── development.conf    # Development domain
├── sites-enabled/
│   ├── production.conf -> ../sites-available/production.conf
│   └── development.conf -> ../sites-available/development.conf
└── nginx.conf             # Main configuration
```

### SSL Certificate Management
```bash
# Check certificate status
certbot certificates

# Renew certificates
certbot renew

# Test renewal
certbot renew --dry-run

# Add new domain to existing certificate
certbot --nginx -d consulting.sa -d www.consulting.sa -d main.consulting.sa -d dev.consulting.sa --expand
```

### Nginx Management Commands
```bash
# Test configuration
nginx -t

# Reload configuration
systemctl reload nginx

# Restart nginx
systemctl restart nginx

# Check status
systemctl status nginx

# View error logs
tail -f /var/log/nginx/error.log

# View access logs
tail -f /var/log/nginx/access.log
```

---

## Domain and SSL Setup

### Domain Configuration
1. **DNS Records** (Configure in your domain provider):
   ```
   A     consulting.sa        → 217.79.255.54
   CNAME www.consulting.sa    → consulting.sa
   CNAME main.consulting.sa   → consulting.sa
   CNAME dev.consulting.sa    → consulting.sa
   ```

2. **SSL Certificate** (Let's Encrypt):
   ```bash
   certbot --nginx -d consulting.sa -d www.consulting.sa -d main.consulting.sa -d dev.consulting.sa
   ```

3. **Nginx Configuration**:
   - Production: consulting.sa, www.consulting.sa, main.consulting.sa
   - Development: dev.consulting.sa

### SSL Best Practices
- Use strong cipher suites
- Enable HSTS headers
- Set up automatic renewal
- Monitor certificate expiration
- Use HTTP/2 for better performance

---

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue 1: Container Won't Start
**Symptoms**: Container exits immediately or restarts continuously
**Diagnosis**:
```bash
docker logs container-name --tail 50
docker inspect container-name
```
**Solutions**:
- Check environment variables
- Verify port conflicts
- Check file permissions
- Review Dockerfile syntax

#### Issue 2: Nginx 502 Bad Gateway
**Symptoms**: Website shows 502 error
**Diagnosis**:
```bash
curl -I http://localhost:3000/  # Test direct container access
nginx -t                        # Test nginx config
tail -f /var/log/nginx/error.log
```
**Solutions**:
- Verify container is running and healthy
- Check port mapping in nginx config
- Verify proxy_pass URLs
- Check firewall rules

#### Issue 3: SSL Certificate Issues
**Symptoms**: SSL warnings or connection errors
**Diagnosis**:
```bash
certbot certificates
openssl s_client -connect consulting.sa:443
```
**Solutions**:
- Renew certificates: `certbot renew`
- Check certificate paths in nginx
- Verify domain DNS resolution
- Check certificate permissions

#### Issue 4: Next.js Build Errors
**Symptoms**: Frontend container fails to build
**Diagnosis**:
```bash
docker logs consulting-frontend-prod --tail 100
```
**Solutions**:
- Check Node.js version compatibility
- Clear npm cache
- Fix TypeScript errors
- Update dependencies
- Check for SSR issues

#### Issue 5: Container Name Conflicts
**Symptoms**: "Container name already in use"
**Diagnosis**:
```bash
docker ps -a | grep container-name
```
**Solutions**:
```bash
docker stop container-name
docker rm container-name
# Or use different names in docker-compose
```

### Emergency Procedures

#### Quick Recovery Steps
1. **Stop all containers**:
   ```bash
   docker stop $(docker ps -q)
   ```

2. **Restore from backup**:
   ```bash
   cp -r /opt/backups/latest/* /opt/docker-apps/production/
   ```

3. **Restart services**:
   ```bash
   cd /opt/docker-apps/production/agentic-site
   docker compose up -d
   ```

#### Health Check Script
```bash
#!/bin/bash
# Quick health check for all services

echo "🔍 Checking container status..."
docker ps --format 'table {{.Names}}\t{{.Status}}'

echo "🔍 Testing endpoints..."
curl -s -o /dev/null -w "Production Frontend: %{http_code}\n" https://www.consulting.sa
curl -s -o /dev/null -w "Development Frontend: %{http_code}\n" https://dev.consulting.sa
curl -s -o /dev/null -w "Production Backend: %{http_code}\n" http://localhost:8000/health
curl -s -o /dev/null -w "Development Backend: %{http_code}\n" http://localhost:8001/health

echo "🔍 Checking SSL certificates..."
certbot certificates | grep -E "(Certificate Name|Expiry Date)"
```

---

## Scripts and Automation

### Essential Scripts Created

#### 1. fix-separated-stacks.sh
**Purpose**: Properly separate production and development environments
**Location**: `infrastructure/scripts/fix-separated-stacks.sh`
**Usage**: `./infrastructure/scripts/fix-separated-stacks.sh`

#### 2. deploy-manual-fix.sh
**Purpose**: Manual deployment for immediate fixes
**Location**: `infrastructure/scripts/deploy-manual-fix.sh`
**Usage**: `./infrastructure/scripts/deploy-manual-fix.sh`

#### 3. setup-github-integration.sh
**Purpose**: Set up GitHub-based CI/CD deployment
**Location**: `infrastructure/scripts/setup-github-integration.sh`
**Usage**: `./infrastructure/scripts/setup-github-integration.sh`

### Script Best Practices
1. **Always include error handling**: `set -e`
2. **Provide clear output**: Use echo statements with status
3. **Create backups**: Before making changes
4. **Test configurations**: Before applying
5. **Log everything**: For troubleshooting

### Automation Checklist
- [ ] Automated backups before deployment
- [ ] Health checks after deployment
- [ ] SSL certificate renewal
- [ ] Log rotation
- [ ] Container restart policies
- [ ] Monitoring and alerting

---

## Future VPS Deployment Checklist

### Pre-Deployment Checklist
- [ ] VPS specifications meet requirements (RAM, CPU, Storage)
- [ ] Domain DNS configured correctly
- [ ] SSL certificates ready
- [ ] Environment variables prepared
- [ ] Backup strategy planned

### Deployment Steps
1. **Server Preparation**
   - [ ] Update system packages
   - [ ] Install Docker and Docker Compose
   - [ ] Install Nginx
   - [ ] Create directory structure
   - [ ] Set up SSL certificates

2. **Application Deployment**
   - [ ] Copy application files
   - [ ] Configure environment variables
   - [ ] Build and start containers
   - [ ] Configure Nginx
   - [ ] Test all endpoints

3. **Post-Deployment**
   - [ ] Set up monitoring
   - [ ] Configure backups
   - [ ] Document access credentials
   - [ ] Create maintenance procedures

### Validation Tests
```bash
# Container health
docker ps --format 'table {{.Names}}\t{{.Status}}'

# Endpoint tests
curl -I https://www.consulting.sa
curl -I https://dev.consulting.sa
curl -I http://localhost:3000/
curl -I http://localhost:8000/health

# SSL tests
openssl s_client -connect consulting.sa:443 -servername consulting.sa

# Performance tests
curl -w "@curl-format.txt" -o /dev/null -s https://www.consulting.sa
```

---

## Maintenance Procedures

### Daily Tasks
- [ ] Check container status
- [ ] Review error logs
- [ ] Monitor resource usage
- [ ] Verify SSL certificate status

### Weekly Tasks
- [ ] Update system packages
- [ ] Review backup integrity
- [ ] Check disk space usage
- [ ] Update documentation

### Monthly Tasks
- [ ] Security updates
- [ ] Performance review
- [ ] Backup cleanup
- [ ] SSL certificate renewal check

---

## Knowledge Base Summary

### What We Learned
1. **Next.js 15+ requires careful handling of SSR and client components**
2. **Container naming is critical for environment separation**
3. **Nginx configuration must match exact container ports**
4. **SSL certificates need proper domain coverage**
5. **Manual deployment is error-prone - automation is essential**
6. **Proper documentation saves hours of troubleshooting**

### Best Practices Established
1. **Use descriptive container names**: `service-component-environment`
2. **Separate networks for different environments**
3. **Always backup before major changes**
4. **Test configurations before applying**
5. **Document everything immediately**
6. **Use health checks for all containers**

### Tools and Commands Mastered
- Docker and Docker Compose management
- Nginx configuration and testing
- SSL certificate management with Certbot
- SSH and SCP for remote deployment
- Curl for endpoint testing
- Log analysis and troubleshooting

---

## Next Steps

### Immediate (GitHub Integration)
1. Set up GitHub repository
2. Configure webhook deployment
3. Implement automated CI/CD
4. Test automated deployment process

### Short Term (Enhancement)
1. Implement monitoring and alerting
2. Set up automated backups
3. Performance optimization
4. Security hardening

### Long Term (Scaling)
1. Load balancer setup
2. Database clustering
3. CDN integration
4. Multi-region deployment

---

**This document represents 2+ weeks of real-world deployment experience and should serve as the definitive guide for future VPS deployments of similar applications.**

**Status**: ✅ Production Ready  
**Confidence Level**: High (Battle-tested)  
**Maintenance**: Update as new issues are discovered and solved