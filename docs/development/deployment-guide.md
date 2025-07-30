# Deployment Process Guide

## Overview

This comprehensive guide covers all deployment processes for the Agentic AI Platform, including development and production environments, automated scripts, and troubleshooting procedures.

## Environment Architecture

### Production Environment
```
URL: https://consulting.sa
Directory: /opt/agentic-platform
Branch: main
Services:
├── Frontend: Port 3000
├── Backend: Port 8000
├── Redis: Port 6379
├── n8n: Port 5678
└── Nginx: Port 80/443 (SSL)
```

### Development Environment
```
URL: https://dev.consulting.sa
Directory: /opt/agentic-platform-dev
Branch: develop
Services:
├── Frontend: Port 3001
├── Backend: Port 8001
├── Redis: Port 6380
├── n8n: Port 5679
└── Nginx: Port 80/443 (SSL)
```

## Deployment Scripts

### Development Deployment

#### Script: `./infrastructure/scripts/deploy-dev-vps.sh`

**Purpose**: Deploy development environment to VPS
**Usage**: 
```bash
chmod +x infrastructure/scripts/deploy-dev-vps.sh
./infrastructure/scripts/deploy-dev-vps.sh
```

**What it does**:
1. Tests VPS connection
2. Creates development directory structure
3. Stops existing development containers
4. Copies application files via rsync
5. Sets up development environment variables
6. Builds and starts development containers
7. Configures nginx for dev.consulting.sa
8. Runs health checks
9. Creates management scripts

**Environment Variables Required**:
```bash
VPS_HOST=217.79.255.54
VPS_USER=root
VPS_PASSWORD=your_password
DOMAIN=consulting.sa
DEV_BRANCH=develop
```

### Production Deployment

#### Script: `./infrastructure/scripts/deploy.sh`

**Purpose**: Deploy production environment to VPS
**Usage**:
```bash
chmod +x infrastructure/scripts/deploy.sh
./infrastructure/scripts/deploy.sh
```

**What it does**:
1. Validates production readiness
2. Creates backup of current production
3. Stops production services gracefully
4. Copies new code to production directory
5. Builds production containers
6. Starts production services
7. Runs comprehensive health checks
8. Validates deployment success

## Pre-Deployment Checklist

### Development Deployment Checklist
- [ ] **Code committed** to develop branch
- [ ] **Local tests pass** (npm test, pytest)
- [ ] **Build succeeds** locally (npm run build)
- [ ] **Environment variables** configured
- [ ] **VPS access** confirmed
- [ ] **No breaking changes** in develop branch

### Production Deployment Checklist
- [ ] **Development testing** completed successfully
- [ ] **All tests pass** in development environment
- [ ] **Performance validated** in development
- [ ] **Security review** completed
- [ ] **Database migrations** prepared (if any)
- [ ] **Backup strategy** confirmed
- [ ] **Rollback plan** prepared
- [ ] **Monitoring** alerts configured
- [ ] **Team notification** sent
- [ ] **Maintenance window** scheduled (if needed)

## Step-by-Step Deployment Process

### Development Environment Deployment

#### Step 1: Prepare Local Environment
```bash
# Ensure you're on develop branch
git checkout develop
git pull origin develop

# Run local tests
cd frontend && npm test
cd ../backend/agent && pytest

# Build locally to check for errors
cd ../../frontend && npm run build
```

#### Step 2: Execute Deployment
```bash
# From project root
./infrastructure/scripts/deploy-dev-vps.sh
```

#### Step 3: Monitor Deployment
The script will show real-time progress:
```
🚀 Deploying Development Environment to VPS: 217.79.255.54
📋 Branch: develop
✓ VPS connection established
Step 1: Setting up development environment...
Step 2: Stopping existing development containers...
Step 3: Copying application files...
Step 4: Setting up development environment variables...
Step 5: Building and starting development containers...
Step 6: Setting up development subdomain (dev.consulting.sa)...
Step 7: Running health checks...
🎉 Development deployment completed!
```

#### Step 4: Validate Deployment
```bash
# Check service status
curl -f https://dev.consulting.sa/api/health

# Access development environment
open https://dev.consulting.sa

# Check logs if needed
ssh root@217.79.255.54 'cd /opt/agentic-platform-dev && ./dev-manage.sh logs'
```

### Production Environment Deployment

#### Step 1: Final Validation
```bash
# Ensure development is working perfectly
curl -f https://dev.consulting.sa/api/health
curl -f https://dev.consulting.sa

# Run comprehensive tests
cd frontend && npm run test:coverage
cd ../backend/agent && pytest --cov=my_adk_agent
```

#### Step 2: Merge to Main
```bash
# Switch to main branch
git checkout main
git pull origin main

# Merge develop (after PR approval)
git merge develop
git push origin main
```

#### Step 3: Execute Production Deployment
```bash
# Deploy to production
./infrastructure/scripts/deploy.sh
```

#### Step 4: Post-Deployment Validation
```bash
# Check production health
curl -f https://consulting.sa/api/health
curl -f https://consulting.sa

# Monitor logs
ssh root@217.79.255.54 'cd /opt/agentic-platform && docker-compose logs -f'

# Verify all services
curl -f https://consulting.sa/api/status
```

## Environment Variable Management

### Development Environment Variables

The development environment inherits from production `.env` and adds overrides:

```bash
# Development-specific overrides added automatically
NODE_ENV=development
DEBUG=true
VERBOSE_LOGGING=true
ADK_LOG_LEVEL=DEBUG

# Development URLs
DEV_SITE_URL=https://dev.consulting.sa
DEV_ADMIN_URL=https://dev.consulting.sa/api
NEXT_PUBLIC_SITE_URL=https://dev.consulting.sa
NEXT_PUBLIC_ADMIN_URL=https://dev.consulting.sa/api

# Development ports
FRONTEND_DEV_PORT=3001
BACKEND_DEV_PORT=8001
REDIS_DEV_PORT=6380
N8N_DEV_PORT=5679

# Development database settings
DEV_TABLE_PREFIX=dev_
DEV_SCHEMA=development
```

### Production Environment Variables

Production uses the main `.env` file with production settings:

```bash
# Production configuration
NODE_ENV=production
DEBUG=false
ADK_LOG_LEVEL=INFO

# Production URLs
NEXT_PUBLIC_SITE_URL=https://consulting.sa
NEXT_PUBLIC_ADMIN_URL=https://consulting.sa/api

# Production ports
FRONTEND_PORT=3000
BACKEND_PORT=8000
REDIS_PORT=6379
N8N_PORT=5678
```

## Docker Container Management

### Development Containers

#### Container Names
- `agentic-frontend-dev`: Next.js development server
- `agentic-backend-dev`: Python ADK agent
- `agentic-redis-dev`: Redis cache
- `agentic-n8n-dev`: n8n workflow automation
- `agentic-nginx-dev`: Nginx reverse proxy

#### Management Commands
```bash
# SSH to VPS
ssh root@217.79.255.54

# Navigate to development directory
cd /opt/agentic-platform-dev

# Use management script
./dev-manage.sh status     # Check container status
./dev-manage.sh logs       # View all logs
./dev-manage.sh logs frontend-dev  # View specific service logs
./dev-manage.sh restart    # Restart all services
./dev-manage.sh rebuild    # Rebuild containers
./dev-manage.sh stop       # Stop all services
./dev-manage.sh start      # Start all services
```

### Production Containers

#### Container Names
- `agentic-frontend-prod`: Next.js production server
- `agentic-backend-prod`: Python ADK agent
- `agentic-redis-prod`: Redis cache

#### Management Commands
```bash
# SSH to VPS
ssh root@217.79.255.54

# Navigate to production directory
cd /opt/agentic-platform

# Docker Compose commands
docker-compose -f infrastructure/docker/docker-compose.production.yml ps
docker-compose -f infrastructure/docker/docker-compose.production.yml logs -f
docker-compose -f infrastructure/docker/docker-compose.production.yml restart
```

## Health Checks and Monitoring

### Automated Health Checks

#### Development Health Endpoints
```bash
# Frontend health check
curl -f https://dev.consulting.sa/api/health

# Backend health check  
curl -f https://dev.consulting.sa:8001/health

# Direct container access (for debugging)
curl -f http://217.79.255.54:3001/api/health
curl -f http://217.79.255.54:8001/health
```

#### Production Health Endpoints
```bash
# Frontend health check
curl -f https://consulting.sa/api/health

# Backend health check
curl -f https://consulting.sa:8000/health

# Comprehensive status check
curl -f https://consulting.sa/api/status
```

### Health Check Scripts

#### Automated Health Monitoring
```bash
#!/bin/bash
# health-check.sh

check_service() {
    local url=$1
    local name=$2
    
    if curl -f -s "$url" > /dev/null; then
        echo "✅ $name: OK"
        return 0
    else
        echo "❌ $name: FAIL"
        return 1
    fi
}

echo "=== Development Environment Health Check ==="
check_service "https://dev.consulting.sa/api/health" "Dev Frontend"
check_service "https://dev.consulting.sa:8001/health" "Dev Backend"

echo "=== Production Environment Health Check ==="
check_service "https://consulting.sa/api/health" "Prod Frontend"
check_service "https://consulting.sa:8000/health" "Prod Backend"
```

### Log Monitoring

#### Development Logs
```bash
# Real-time log monitoring
ssh root@217.79.255.54 'cd /opt/agentic-platform-dev && ./dev-manage.sh logs -f'

# Specific service logs
ssh root@217.79.255.54 'cd /opt/agentic-platform-dev && ./dev-manage.sh logs frontend-dev'
ssh root@217.79.255.54 'cd /opt/agentic-platform-dev && ./dev-manage.sh logs backend-dev'

# Error log filtering
ssh root@217.79.255.54 'cd /opt/agentic-platform-dev && ./dev-manage.sh logs | grep ERROR'
```

#### Production Logs
```bash
# Production log monitoring
ssh root@217.79.255.54 'cd /opt/agentic-platform && docker-compose -f infrastructure/docker/docker-compose.production.yml logs -f'

# Specific service logs
ssh root@217.79.255.54 'cd /opt/agentic-platform && docker-compose -f infrastructure/docker/docker-compose.production.yml logs frontend'
ssh root@217.79.255.54 'cd /opt/agentic-platform && docker-compose -f infrastructure/docker/docker-compose.production.yml logs backend'
```

## SSL Certificate Management

### Wildcard SSL Certificate

The platform uses a wildcard SSL certificate for `*.consulting.sa`:

#### Certificate Location
```
/etc/ssl/certs/consulting.sa.crt
/etc/ssl/private/consulting.sa.key
```

#### Nginx SSL Configuration
```nginx
# /etc/nginx/sites-available/agentic-platform
server {
    listen 443 ssl http2;
    server_name consulting.sa;
    
    ssl_certificate /etc/ssl/certs/consulting.sa.crt;
    ssl_certificate_key /etc/ssl/private/consulting.sa.key;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
}

# Development subdomain
server {
    listen 443 ssl http2;
    server_name dev.consulting.sa;
    
    ssl_certificate /etc/ssl/certs/consulting.sa.crt;
    ssl_certificate_key /etc/ssl/private/consulting.sa.key;
    
    # Same SSL configuration
}
```

#### SSL Certificate Renewal
```bash
# Check certificate expiration
openssl x509 -in /etc/ssl/certs/consulting.sa.crt -noout -dates

# Test SSL configuration
nginx -t

# Reload nginx after certificate update
systemctl reload nginx
```

## Troubleshooting Deployment Issues

### Common Issues and Solutions

#### 1. VPS Connection Failed
**Symptoms**: `Failed to connect to VPS`
**Solutions**:
```bash
# Test SSH connection
ssh root@217.79.255.54

# Check if sshpass is installed
which sshpass || brew install hudochenkov/sshpass/sshpass

# Verify VPS credentials in .env
grep VPS_ .env
```

#### 2. Container Build Failures
**Symptoms**: Docker build errors
**Solutions**:
```bash
# Check Docker daemon
docker info

# Clear Docker cache
docker system prune -f

# Rebuild without cache
./dev-manage.sh rebuild

# Check available disk space
df -h
```

#### 3. Port Conflicts
**Symptoms**: `Port already in use`
**Solutions**:
```bash
# Check what's using the port
lsof -i :3001
lsof -i :8001

# Stop conflicting services
./dev-manage.sh stop

# Kill processes if needed
sudo kill -9 $(lsof -t -i:3001)
```

#### 4. SSL Certificate Issues
**Symptoms**: HTTPS not working
**Solutions**:
```bash
# Check certificate validity
openssl x509 -in /etc/ssl/certs/consulting.sa.crt -noout -dates

# Test nginx configuration
nginx -t

# Check certificate permissions
ls -la /etc/ssl/certs/consulting.sa.crt
ls -la /etc/ssl/private/consulting.sa.key

# Restart nginx
systemctl restart nginx
```

#### 5. Health Check Failures
**Symptoms**: Health endpoints returning errors
**Solutions**:
```bash
# Check container status
docker ps

# Check service logs
./dev-manage.sh logs backend-dev

# Test internal connectivity
docker exec -it agentic-backend-dev curl localhost:8001/health

# Verify environment variables
docker exec -it agentic-backend-dev env | grep -E "(NODE_ENV|DEBUG)"
```

### Emergency Procedures

#### Rollback Development Environment
```bash
# SSH to VPS
ssh root@217.79.255.54

# Stop development environment
cd /opt/agentic-platform-dev
./dev-manage.sh stop

# Restore from backup (if available)
# Or redeploy from last known good commit
git checkout develop
git reset --hard HEAD~1
./infrastructure/scripts/deploy-dev-vps.sh
```

#### Rollback Production Environment
```bash
# SSH to VPS
ssh root@217.79.255.54

# Stop production services
cd /opt/agentic-platform
docker-compose -f infrastructure/docker/docker-compose.production.yml down

# Restore from backup
# Or redeploy from previous version
git checkout main
git reset --hard HEAD~1
./infrastructure/scripts/deploy.sh
```

## Performance Optimization

### Deployment Performance

#### Optimization Strategies
1. **Parallel Builds**: Build containers in parallel when possible
2. **Layer Caching**: Use Docker layer caching
3. **Incremental Sync**: Use rsync for efficient file copying
4. **Health Check Optimization**: Reduce health check intervals during deployment

#### Build Time Optimization
```dockerfile
# Use multi-stage builds
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:20-alpine AS runtime
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
```

### Runtime Performance

#### Container Resource Limits
```yaml
# docker-compose.yml
services:
  frontend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

#### Monitoring Resource Usage
```bash
# Monitor container resources
docker stats

# Check system resources
htop
df -h
free -h
```

## Automated Deployment (CI/CD)

### GitHub Actions Workflow

#### Development Auto-Deploy
```yaml
# .github/workflows/deploy-dev.yml
name: Deploy to Development
on:
  push:
    branches: [develop]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Development
        run: |
          chmod +x infrastructure/scripts/deploy-dev-vps.sh
          ./infrastructure/scripts/deploy-dev-vps.sh
        env:
          VPS_HOST: ${{ secrets.VPS_HOST }}
          VPS_USER: ${{ secrets.VPS_USER }}
          VPS_PASSWORD: ${{ secrets.VPS_PASSWORD }}
```

#### Production Deploy (Manual)
```yaml
# .github/workflows/deploy-prod.yml
name: Deploy to Production
on:
  workflow_dispatch:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Production
        run: |
          chmod +x infrastructure/scripts/deploy.sh
          ./infrastructure/scripts/deploy.sh
```

## Best Practices

### Deployment Best Practices

#### ✅ Do's
- Always test in development first
- Use automated health checks
- Monitor logs during deployment
- Have a rollback plan ready
- Document all changes
- Use environment-specific configurations
- Validate SSL certificates
- Check resource usage

#### ❌ Don'ts
- Never deploy directly to production without testing
- Don't skip health checks
- Never deploy with failing tests
- Don't ignore warning messages
- Never commit sensitive credentials
- Don't deploy during peak hours without notice
- Never skip backups before major deployments

### Security Best Practices

#### Deployment Security
- Use SSH keys instead of passwords when possible
- Rotate deployment credentials regularly
- Limit VPS access to necessary personnel
- Monitor deployment logs for suspicious activity
- Use secure environment variable management
- Implement proper firewall rules
- Keep SSL certificates up to date

## Conclusion

This deployment guide provides comprehensive coverage of all deployment scenarios for the Agentic AI Platform. Following these procedures ensures:

- **Reliable Deployments**: Consistent and predictable deployment process
- **Environment Isolation**: Clear separation between development and production
- **Quick Recovery**: Efficient troubleshooting and rollback procedures
- **Security**: Secure deployment practices and credential management
- **Monitoring**: Comprehensive health checking and log monitoring
- **Performance**: Optimized deployment and runtime performance

Always remember: **Test thoroughly in development before deploying to production!**