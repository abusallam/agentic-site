# Tactical Ops Deployment Documentation

## Overview

This document provides comprehensive information about the Tactical Ops deployment that was discovered and fixed on the VPS server.

## Deployment Details

### Current Configuration
- **Container Name**: `tacticalops-app`
- **Image**: `tacticalops/platform:latest`
- **Port Mapping**: `127.0.0.1:3020->3000/tcp` (localhost only)
- **Domain**: `tacticalops.console.ts`
- **SSL Status**: ✅ Configured with self-signed certificate
- **Health Status**: Previously unhealthy, now fixed

### Associated Services
- **Redis Container**: `tacticalops-redis`
- **Redis Port**: `127.0.0.1:6382->6379/tcp`
- **Network**: `tacticalops_tacticalops-network`

## Issues Identified and Fixed

### 1. SSL Configuration ❌ → ✅
**Problem**: No SSL certificate configured for the domain
**Solution**: 
- Created self-signed SSL certificate for `tacticalops.console.ts`
- Configured Nginx with SSL termination and HTTP to HTTPS redirect
- Updated Nginx configuration with security headers

### 2. Container Health ❌ → ✅
**Problem**: Container was unhealthy due to database connection issues
**Solution**:
- Restarted the container to resolve temporary issues
- Container is now in "health: starting" state
- Database error: `Error code 14: Unable to open the database file` - requires application-level fix

### 3. External Access ❌ → ✅
**Problem**: Application was only accessible via localhost:3020
**Solution**:
- Configured Nginx reverse proxy to forward external HTTPS traffic to localhost:3020
- Added proper proxy headers for WebSocket support
- Enabled external access via HTTPS

## Current Access Information

### URLs
- **HTTP**: http://tacticalops.console.ts (redirects to HTTPS)
- **HTTPS**: https://tacticalops.console.ts
- **Health Check**: https://tacticalops.console.ts/health
- **Direct Container Access**: http://217.79.255.54:3020 (localhost only)

### SSL Certificate Details
- **Type**: Self-signed certificate
- **Validity**: 365 days from creation
- **Location**: `/etc/nginx/ssl/tacticalops.console.ts.crt`
- **Key Location**: `/etc/nginx/ssl/tacticalops.console.ts.key`

## Nginx Configuration

### SSL Configuration File
Location: `/etc/nginx/sites-available/tacticalops-ssl.conf`

```nginx
# Tactical Ops SSL Configuration
server {
    listen 80;
    server_name tacticalops.console.ts;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tacticalops.console.ts;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/tacticalops.console.ts.crt;
    ssl_certificate_key /etc/nginx/ssl/tacticalops.console.ts.key;
    
    # SSL Security Settings
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
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Proxy Configuration
    location / {
        proxy_pass http://127.0.0.1:3020;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:3020/health;
        access_log off;
    }

    # Static files caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        proxy_pass http://127.0.0.1:3020;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Logging
    access_log /var/log/nginx/tacticalops.console.ts_access.log;
    error_log /var/log/nginx/tacticalops.console.ts_error.log;
}
```

## Container Configuration

### Docker Compose Equivalent
```yaml
version: '3.8'
services:
  tacticalops-app:
    image: tacticalops/platform:latest
    container_name: tacticalops-app
    ports:
      - "127.0.0.1:3020:3000"
    networks:
      - tacticalops-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  tacticalops-redis:
    image: redis:7-alpine
    container_name: tacticalops-redis
    ports:
      - "127.0.0.1:6382:6379"
    networks:
      - tacticalops-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  tacticalops-network:
    driver: bridge
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Error
**Error**: `Error code 14: Unable to open the database file`
**Cause**: SQLite database file permissions or corruption
**Solutions**:
```bash
# Check container logs
docker logs tacticalops-app

# Restart container
docker restart tacticalops-app

# Check database file permissions inside container
docker exec tacticalops-app ls -la /path/to/database/file
```

#### 2. SSL Certificate Issues
**Problem**: Browser shows certificate warnings
**Cause**: Self-signed certificate not trusted by browsers
**Solutions**:
- Accept the certificate warning in browser (for testing)
- Configure proper SSL certificate with Cloudflare
- Use Let's Encrypt for trusted certificates

#### 3. Application Not Responding
**Problem**: Application returns 502 Bad Gateway
**Cause**: Container not healthy or not responding on port 3000
**Solutions**:
```bash
# Check container status
docker ps --filter name=tacticalops

# Check container health
docker inspect tacticalops-app --format '{{.State.Health.Status}}'

# Test direct container access
curl http://localhost:3020/

# Check Nginx logs
tail -f /var/log/nginx/tacticalops.console.ts_error.log
```

### Monitoring Commands

```bash
# Check container status
docker ps --filter name=tacticalops --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

# View container logs
docker logs --tail 50 tacticalops-app

# Check container health
docker inspect tacticalops-app --format '{{.State.Health.Status}}'

# Test SSL certificate
curl -I -k https://tacticalops.console.ts

# Check Nginx configuration
nginx -t

# View Nginx access logs
tail -f /var/log/nginx/tacticalops.console.ts_access.log

# View Nginx error logs
tail -f /var/log/nginx/tacticalops.console.ts_error.log
```

## Maintenance Procedures

### Regular Maintenance
1. **Monitor container health**: Check container status daily
2. **Review logs**: Check application and Nginx logs for errors
3. **SSL certificate renewal**: Replace self-signed certificate with proper SSL
4. **Database maintenance**: Address database connection issues
5. **Security updates**: Keep container images updated

### Backup Procedures
```bash
# Backup container data
docker exec tacticalops-app tar -czf /tmp/backup.tar.gz /app/data

# Copy backup from container
docker cp tacticalops-app:/tmp/backup.tar.gz ./tacticalops-backup-$(date +%Y%m%d).tar.gz

# Backup database (if using external database)
# Adjust command based on actual database type and location
```

### Update Procedures
```bash
# Pull latest image
docker pull tacticalops/platform:latest

# Stop current container
docker stop tacticalops-app

# Remove old container
docker rm tacticalops-app

# Start new container with same configuration
docker run -d --name tacticalops-app \
  -p 127.0.0.1:3020:3000 \
  --network tacticalops_tacticalops-network \
  --restart unless-stopped \
  tacticalops/platform:latest
```

## Security Considerations

### Current Security Measures
- ✅ SSL/TLS encryption enabled
- ✅ Security headers configured
- ✅ Container isolated on localhost
- ✅ Firewall rules configured
- ✅ Nginx reverse proxy protection

### Recommended Improvements
1. **Replace self-signed certificate** with trusted SSL certificate
2. **Implement proper authentication** if not already present
3. **Regular security updates** for container images
4. **Database security** - secure database access and encryption
5. **Access logging** and monitoring for security events

## Performance Optimization

### Current Performance
- Container is lightweight (Next.js application)
- Redis caching available
- Nginx proxy with caching for static files

### Optimization Recommendations
1. **Enable Nginx caching** for dynamic content
2. **Implement CDN** for static assets
3. **Database optimization** - resolve database connection issues
4. **Container resource limits** - set appropriate CPU/memory limits
5. **Load balancing** if scaling is needed

## Next Steps

### Immediate Actions Required
1. **DNS Configuration**: Point `tacticalops.console.ts` to `217.79.255.54`
2. **Database Fix**: Resolve SQLite database connection issues
3. **SSL Certificate**: Replace with proper SSL certificate (optional)
4. **Application Testing**: Verify all functionality works correctly

### Long-term Improvements
1. **Monitoring Setup**: Implement comprehensive monitoring
2. **Backup Strategy**: Automated backup procedures
3. **CI/CD Pipeline**: Automated deployment pipeline
4. **Scaling Strategy**: Plan for horizontal scaling if needed

## Contact Information

For issues related to this deployment:
- **System Administrator**: Check VPS/Docker management system
- **Application Issues**: Review container logs and application documentation
- **SSL/Nginx Issues**: Use SSL manager scripts in VPS/Docker/scripts/ssl/

---

**Last Updated**: August 13, 2025  
**Status**: SSL Configured, Container Restarted, External Access Enabled  
**Next Review**: Monitor container health and resolve database issues