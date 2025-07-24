# 🔧 Deployment Lessons Learned & Troubleshooting Guide

## 📋 Overview

This document captures all the issues encountered during the actual deployment of the agentic CI/CD pipeline and their solutions. This serves as a comprehensive troubleshooting guide for future deployments.

## 🚨 Critical Issues Encountered & Solutions

### 1. **Docker Installation Issues**

**Problem**: Initial Docker installation script failed due to incorrect GPG handling in non-interactive environment.

**Error**:
```bash
gpg: cannot open '/dev/tty': No such device or address
curl: (23) Failed writing body
```

**Root Cause**: The original script tried to use Ubuntu Docker repository on a Debian system and GPG couldn't handle non-interactive mode.

**Solution Applied**:
```bash
# Changed from Ubuntu-specific to Debian-specific installation
# OLD (Failed):
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# NEW (Working):
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
```

**Prevention**: Always use the universal Docker installation script for cross-platform compatibility.

---

### 2. **File Transfer Issues with .venv Directory**

**Problem**: SCP failed when trying to copy the entire project due to symbolic links in Python virtual environment.

**Error**:
```bash
scp: local "./.venv/lib64" is not a regular file
scp: upload "./.venv/lib64" to "/opt/agentic-platform/.venv/lib64" failed
```

**Root Cause**: Python virtual environments contain symbolic links that SCP cannot handle properly.

**Solution Applied**:
```bash
# Create tarball excluding problematic directories
tar --exclude='.venv' --exclude='node_modules' --exclude='.git' --exclude='.next' --exclude='n8n-mcp/node_modules' --exclude='n8n-mcp/dist' -czf /tmp/agentic-platform.tar.gz .

# Transfer and extract
sshpass -p "$VPS_PASSWORD" scp -o StrictHostKeyChecking=no /tmp/agentic-platform.tar.gz root@$VPS_HOST:/opt/
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no root@$VPS_HOST "cd /opt && tar -xzf agentic-platform.tar.gz -C agentic-platform && rm agentic-platform.tar.gz"
```

**Prevention**: Always exclude virtual environments and build artifacts from deployment transfers.

---

### 3. **Docker Build Context Issues**

**Problem**: Backend Docker build failed because Dockerfile.backend was not in the correct context directory.

**Error**:
```bash
failed to solve: failed to read dockerfile: open Dockerfile.backend: no such file or directory
```

**Root Cause**: Docker Compose configuration specified `context: ./agent` but Dockerfile.backend was in the root directory.

**Solution Applied**:
```bash
# Copy Dockerfile to correct location
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no root@$VPS_HOST "cp /opt/agentic-platform/Dockerfile.backend /opt/agentic-platform/agent/"
```

**Prevention**: Ensure Docker build context and Dockerfile locations are properly aligned in docker-compose.yml.

---

### 4. **Frontend Build Failures Due to TypeScript Errors**

**Problem**: Next.js build failed due to TypeScript errors in n8n-mcp directory.

**Error**:
```bash
Type error: Cannot find module 'axios' or its corresponding type declarations.
./n8n-mcp/scripts/test-security.ts:2:19
```

**Root Cause**: The n8n-mcp directory contained TypeScript files that were being included in the Next.js build process.

**Solution Applied**:
```bash
# Add n8n-mcp to .dockerignore
echo 'n8n-mcp/' >> .dockerignore
```

**Prevention**: Properly configure .dockerignore to exclude non-essential directories from Docker builds.

---

### 5. **Nginx Configuration Syntax Errors**

**Problem**: Nginx configuration test failed due to invalid gzip_proxied directive value.

**Error**:
```bash
nginx: [emerg] invalid value "must-revalidate" in /etc/nginx/sites-enabled/agentic-platform:63
```

**Root Cause**: The `must-revalidate` value is not valid for the `gzip_proxied` directive.

**Solution Applied**:
```bash
# Fixed gzip_proxied directive
sed -i 's/gzip_proxied expired no-cache no-store private must-revalidate auth;/gzip_proxied expired no-cache no-store private auth;/' /etc/nginx/sites-available/agentic-platform
```

**Prevention**: Validate Nginx configurations before deployment and use only valid directive values.

---

### 6. **Missing SSL Certificates**

**Problem**: Nginx failed to start due to missing SSL certificate files.

**Error**:
```bash
cannot load certificate "/etc/nginx/ssl/consulting.sa.crt": BIO_new_file() failed
```

**Root Cause**: SSL certificate files were not copied to the expected location.

**Solution Applied**:
```bash
# Create SSL directory and copy certificates
mkdir -p /etc/nginx/ssl
cp /opt/agentic-platform/ssl/consulting.sa.crt /etc/nginx/ssl/
cp /opt/agentic-platform/ssl/consulting.sa.key /etc/nginx/ssl/
chmod 600 /etc/nginx/ssl/consulting.sa.key
chmod 644 /etc/nginx/ssl/consulting.sa.crt
```

**Prevention**: Ensure SSL certificate deployment is part of the automated deployment script.

---

## 🔄 Improved Deployment Process

### Updated Deployment Script Structure

```bash
#!/bin/bash
set -e

# 1. Pre-deployment Validation
validate_environment() {
    # Check required tools
    command -v sshpass >/dev/null 2>&1 || install_sshpass
    
    # Test VPS connection
    test_vps_connection || exit 1
    
    # Validate environment variables
    validate_env_vars || exit 1
}

# 2. Robust File Transfer
deploy_files() {
    echo "Creating deployment package..."
    tar --exclude='.venv' \
        --exclude='node_modules' \
        --exclude='.git' \
        --exclude='.next' \
        --exclude='n8n-mcp/node_modules' \
        --exclude='n8n-mcp/dist' \
        --exclude='infrastructure/cleanup/backups' \
        -czf /tmp/agentic-platform.tar.gz .
    
    echo "Transferring files to VPS..."
    sshpass -p "$VPS_PASSWORD" scp -o StrictHostKeyChecking=no \
        /tmp/agentic-platform.tar.gz root@$VPS_HOST:/opt/
    
    echo "Extracting files on VPS..."
    run_on_vps "cd /opt && tar -xzf agentic-platform.tar.gz -C agentic-platform && rm agentic-platform.tar.gz"
}

# 3. Docker Build with Error Handling
build_containers() {
    echo "Preparing Docker build context..."
    run_on_vps "cp /opt/agentic-platform/Dockerfile.backend /opt/agentic-platform/agent/"
    run_on_vps "echo 'n8n-mcp/' >> /opt/agentic-platform/.dockerignore"
    
    echo "Building containers..."
    run_on_vps "cd /opt/agentic-platform && docker compose -f docker-compose.production.yml build --no-cache"
}

# 4. Nginx Configuration with Validation
configure_nginx() {
    echo "Setting up SSL certificates..."
    run_on_vps "mkdir -p /etc/nginx/ssl"
    run_on_vps "cp /opt/agentic-platform/ssl/consulting.sa.crt /etc/nginx/ssl/"
    run_on_vps "cp /opt/agentic-platform/ssl/consulting.sa.key /etc/nginx/ssl/"
    run_on_vps "chmod 600 /etc/nginx/ssl/consulting.sa.key"
    run_on_vps "chmod 644 /etc/nginx/ssl/consulting.sa.crt"
    
    echo "Configuring Nginx..."
    run_on_vps "cp /opt/agentic-platform/nginx/production.conf /etc/nginx/sites-available/agentic-platform"
    
    # Fix known configuration issues
    run_on_vps "sed -i 's/gzip_proxied expired no-cache no-store private must-revalidate auth;/gzip_proxied expired no-cache no-store private auth;/' /etc/nginx/sites-available/agentic-platform"
    
    echo "Testing Nginx configuration..."
    run_on_vps "nginx -t" || {
        echo "Nginx configuration test failed!"
        exit 1
    }
    
    run_on_vps "ln -sf /etc/nginx/sites-available/agentic-platform /etc/nginx/sites-enabled/"
    run_on_vps "systemctl reload nginx"
}

# 5. Health Check Validation
validate_deployment() {
    echo "Waiting for services to start..."
    sleep 30
    
    echo "Running health checks..."
    
    # Check containers
    run_on_vps "docker ps --format 'table {{.Names}}\t{{.Status}}'"
    
    # Check frontend health
    if run_on_vps "curl -s -k -H 'Host: consulting.sa' https://localhost/api/health | grep -q 'ok'"; then
        echo "✅ Frontend health check passed"
    else
        echo "❌ Frontend health check failed"
        return 1
    fi
    
    # Check backend health
    if run_on_vps "curl -s http://localhost:8000/health | grep -q 'status'"; then
        echo "✅ Backend health check passed"
    else
        echo "❌ Backend health check failed"
        return 1
    fi
}
```

---

## 📋 Pre-Deployment Checklist

### Environment Preparation
- [ ] **VPS Access**: Verify SSH access with password/key
- [ ] **Domain DNS**: Ensure domain points to VPS IP
- [ ] **SSL Certificates**: Verify certificate files exist
- [ ] **Environment Variables**: All required vars in .env file
- [ ] **Local Tools**: sshpass, docker, docker-compose installed

### Code Preparation
- [ ] **Clean Build**: Remove node_modules, .venv, build artifacts
- [ ] **Docker Context**: Ensure Dockerfiles are in correct locations
- [ ] **Ignore Files**: Update .dockerignore with exclusions
- [ ] **Configuration**: Validate nginx configs locally
- [ ] **Dependencies**: Ensure all package.json/requirements.txt are updated

### Infrastructure Preparation
- [ ] **VPS Resources**: Sufficient disk space, memory
- [ ] **Firewall Rules**: Required ports open (80, 443, 3000, 8000)
- [ ] **System Updates**: VPS system packages updated
- [ ] **Docker Installation**: Docker and Docker Compose installed

---

## 🛠️ Systematic Deployment Process

### Phase 1: Validation & Preparation (5 minutes)
1. **Environment Check**: Validate all prerequisites
2. **Connection Test**: Verify VPS connectivity
3. **Resource Check**: Ensure sufficient VPS resources
4. **Backup Current**: Create backup of existing deployment

### Phase 2: File Deployment (3 minutes)
1. **Package Creation**: Create clean deployment package
2. **File Transfer**: Upload to VPS via secure transfer
3. **Extraction**: Extract and organize files on VPS
4. **Permission Setup**: Set correct file permissions

### Phase 3: Container Build (10 minutes)
1. **Context Preparation**: Fix Docker build contexts
2. **Configuration Update**: Apply necessary config fixes
3. **Image Building**: Build all container images
4. **Build Validation**: Verify successful builds

### Phase 4: Service Configuration (5 minutes)
1. **SSL Setup**: Deploy SSL certificates
2. **Nginx Configuration**: Configure reverse proxy
3. **Configuration Test**: Validate all configurations
4. **Service Restart**: Restart affected services

### Phase 5: Deployment Validation (5 minutes)
1. **Container Status**: Verify all containers running
2. **Health Checks**: Test all service endpoints
3. **Integration Test**: Verify service communication
4. **Performance Check**: Basic performance validation

### Phase 6: Post-Deployment (2 minutes)
1. **Status Documentation**: Record deployment status
2. **Monitoring Setup**: Ensure monitoring active
3. **Cleanup**: Remove temporary files
4. **Documentation Update**: Update deployment logs

---

## 🔍 Monitoring & Maintenance

### Daily Checks
```bash
# Quick status check
/opt/agentic-platform/check-status.sh

# Container health
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Disk usage
df -h

# Memory usage
free -h
```

### Weekly Maintenance
```bash
# Update system packages
apt update && apt upgrade -y

# Clean Docker images
docker system prune -f

# Check SSL certificate expiry
certbot certificates

# Review logs for errors
journalctl --since "1 week ago" | grep -i error
```

### Monthly Tasks
- **Security Updates**: Apply security patches
- **Backup Verification**: Test backup restoration
- **Performance Review**: Analyze performance metrics
- **Capacity Planning**: Review resource usage trends

---

## 🚨 Emergency Procedures

### Service Down Recovery
```bash
# 1. Check container status
docker ps -a

# 2. Restart failed containers
docker compose -f docker-compose.production.yml restart

# 3. Check logs for errors
docker compose -f docker-compose.production.yml logs --tail=100

# 4. If persistent, rebuild and redeploy
docker compose -f docker-compose.production.yml down
docker compose -f docker-compose.production.yml up -d --build
```

### Rollback Procedure
```bash
# 1. Stop current deployment
docker compose -f docker-compose.production.yml down

# 2. Restore from backup
cp -r /opt/backups/latest/* /opt/agentic-platform/

# 3. Start previous version
docker compose -f docker-compose.production.yml up -d

# 4. Verify rollback success
curl -k https://consulting.sa/api/health
```

### SSL Certificate Issues
```bash
# 1. Check certificate status
certbot certificates

# 2. Renew if needed
certbot renew --force-renewal

# 3. Restart nginx
systemctl restart nginx

# 4. Verify SSL
curl -I https://consulting.sa
```

---

## 📈 Performance Optimizations Applied

### Docker Optimizations
- **Multi-stage builds**: Reduced image sizes
- **Layer caching**: Optimized build times
- **Health checks**: Proper container monitoring
- **Resource limits**: Prevented resource exhaustion

### Nginx Optimizations
- **Gzip compression**: Reduced bandwidth usage
- **Static file caching**: Improved response times
- **Rate limiting**: Protected against abuse
- **Connection pooling**: Better resource utilization

### Application Optimizations
- **Production builds**: Optimized Next.js builds
- **Environment separation**: Proper env configuration
- **Dependency optimization**: Minimal production dependencies
- **Error handling**: Comprehensive error management

---

## 🎯 Success Metrics

### Deployment Success Criteria
- [ ] **All containers healthy**: No failed containers
- [ ] **Health endpoints responding**: 200 OK responses
- [ ] **SSL certificate valid**: HTTPS working properly
- [ ] **Performance acceptable**: Response times < 2s
- [ ] **No critical errors**: Clean application logs
- [ ] **Monitoring active**: All metrics being collected

### Performance Benchmarks
- **Frontend Response Time**: < 1.5s average
- **Backend API Response**: < 500ms average
- **Container Memory Usage**: < 80% of allocated
- **Disk Usage**: < 70% of available space
- **SSL Certificate**: Valid for > 30 days

---

## 📚 Additional Resources

### Documentation References
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Nginx Configuration Guide](https://nginx.org/en/docs/)
- [Next.js Production Deployment](https://nextjs.org/docs/deployment)
- [FastAPI Production Guide](https://fastapi.tiangolo.com/deployment/)

### Useful Commands Reference
```bash
# System monitoring
htop                    # System resources
iotop                   # Disk I/O
netstat -tulpn         # Network connections
ss -tulpn              # Socket statistics

# Docker management
docker stats           # Container resource usage
docker system df       # Docker disk usage
docker logs -f <container>  # Follow container logs

# Nginx management
nginx -t               # Test configuration
nginx -s reload        # Reload configuration
tail -f /var/log/nginx/error.log  # Monitor errors
```

This comprehensive guide ensures that future deployments will be smooth, systematic, and well-documented. All the pain points we encountered have been addressed with specific solutions and preventive measures.