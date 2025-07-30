# Troubleshooting Guide

## Overview

This comprehensive troubleshooting guide covers common issues, diagnostic procedures, and solutions for the Agentic AI Platform. It's designed to help developers, AI agents, and system administrators quickly identify and resolve problems.

## Quick Diagnostic Commands

### System Health Check
```bash
# Check all services status
curl -f https://consulting.sa/api/health
curl -f https://dev.consulting.sa/api/health

# Check individual services
curl -f https://consulting.sa:8000/health
curl -f https://dev.consulting.sa:8001/health

# Check container status
ssh root@217.79.255.54 'docker ps'

# Check system resources
ssh root@217.79.255.54 'htop'
ssh root@217.79.255.54 'df -h'
ssh root@217.79.255.54 'free -h'
```

### Log Analysis
```bash
# Development environment logs
ssh root@217.79.255.54 'cd /opt/agentic-platform-dev && ./dev-manage.sh logs'

# Production environment logs
ssh root@217.79.255.54 'cd /opt/agentic-platform && docker-compose logs -f'

# Specific service logs
ssh root@217.79.255.54 'cd /opt/agentic-platform-dev && ./dev-manage.sh logs frontend-dev'
ssh root@217.79.255.54 'cd /opt/agentic-platform-dev && ./dev-manage.sh logs backend-dev'

# Error filtering
ssh root@217.79.255.54 'cd /opt/agentic-platform && docker-compose logs | grep ERROR'
```

## Common Issues and Solutions

### 1. Website Not Loading

#### Symptoms
- Browser shows "This site can't be reached"
- Connection timeout errors
- SSL certificate errors

#### Diagnostic Steps
```bash
# Check if server is responding
ping 217.79.255.54

# Check if ports are open
telnet 217.79.255.54 80
telnet 217.79.255.54 443

# Check nginx status
ssh root@217.79.255.54 'systemctl status nginx'

# Check SSL certificate
openssl s_client -connect consulting.sa:443 -servername consulting.sa
```

#### Solutions

**Solution 1: Restart Nginx**
```bash
ssh root@217.79.255.54 'systemctl restart nginx'
ssh root@217.79.255.54 'systemctl status nginx'
```

**Solution 2: Check Nginx Configuration**
```bash
ssh root@217.79.255.54 'nginx -t'
ssh root@217.79.255.54 'cat /etc/nginx/sites-enabled/agentic-platform'
```

**Solution 3: Verify SSL Certificate**
```bash
ssh root@217.79.255.54 'ls -la /etc/ssl/certs/consulting.sa.crt'
ssh root@217.79.255.54 'openssl x509 -in /etc/ssl/certs/consulting.sa.crt -noout -dates'
```

### 2. Frontend Build Failures

#### Symptoms
- `npm run build` fails
- TypeScript compilation errors
- Missing dependencies errors

#### Diagnostic Steps
```bash
# Check Node.js version
node --version

# Check npm version
npm --version

# Clear cache
npm cache clean --force

# Check for dependency issues
cd frontend && npm ls
cd frontend && npm audit
```

#### Solutions

**Solution 1: Update Dependencies**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

**Solution 2: Fix TypeScript Errors**
```bash
cd frontend
npm run type-check
# Fix reported TypeScript errors
npm run build
```

**Solution 3: Check Environment Variables**
```bash
# Verify required environment variables
grep -E "(NEXT_PUBLIC_|SUPABASE_)" .env
```

### 3. Backend Service Errors

#### Symptoms
- API endpoints returning 500 errors
- Python import errors
- Database connection failures

#### Diagnostic Steps
```bash
# Check Python version
python3 --version

# Check backend logs
ssh root@217.79.255.54 'cd /opt/agentic-platform-dev && ./dev-manage.sh logs backend-dev'

# Check container status
ssh root@217.79.255.54 'docker ps | grep backend'

# Test backend directly
curl -f http://217.79.255.54:8001/health
```

#### Solutions

**Solution 1: Restart Backend Service**
```bash
ssh root@217.79.255.54 'cd /opt/agentic-platform-dev && ./dev-manage.sh restart'
```

**Solution 2: Check Python Dependencies**
```bash
ssh root@217.79.255.54 'docker exec -it agentic-backend-dev pip list'
ssh root@217.79.255.54 'docker exec -it agentic-backend-dev python -c "import my_adk_agent"'
```

**Solution 3: Verify Environment Variables**
```bash
ssh root@217.79.255.54 'docker exec -it agentic-backend-dev env | grep -E "(SUPABASE_|GEMINI_|STRIPE_)"'
```

### 4. Database Connection Issues

#### Symptoms
- "Connection refused" errors
- Supabase authentication failures
- Database timeout errors

#### Diagnostic Steps
```bash
# Test Supabase connection
curl -H "apikey: YOUR_SUPABASE_ANON_KEY" \
     -H "Authorization: Bearer YOUR_SUPABASE_ANON_KEY" \
     "https://YOUR_PROJECT.supabase.co/rest/v1/users?select=*"

# Check environment variables
grep SUPABASE .env

# Test from container
ssh root@217.79.255.54 'docker exec -it agentic-backend-dev python -c "
import os
from supabase import create_client
url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
print(f'URL: {url}')
print(f'Key: {key[:20]}...')
client = create_client(url, key)
print('Connection successful')
"'
```

#### Solutions

**Solution 1: Verify Supabase Credentials**
```bash
# Check if credentials are correct
# Visit Supabase dashboard to verify URL and keys
# Update .env file if needed
```

**Solution 2: Check Network Connectivity**
```bash
ssh root@217.79.255.54 'ping supabase.com'
ssh root@217.79.255.54 'curl -I https://supabase.com'
```

**Solution 3: Restart Services**
```bash
ssh root@217.79.255.54 'cd /opt/agentic-platform-dev && ./dev-manage.sh restart'
```

### 5. SSL Certificate Problems

#### Symptoms
- "Your connection is not private" warnings
- SSL certificate expired errors
- Mixed content warnings

#### Diagnostic Steps
```bash
# Check certificate validity
openssl s_client -connect consulting.sa:443 -servername consulting.sa 2>/dev/null | openssl x509 -noout -dates

# Check certificate chain
openssl s_client -connect consulting.sa:443 -servername consulting.sa -showcerts

# Verify nginx SSL configuration
ssh root@217.79.255.54 'nginx -t'
```

#### Solutions

**Solution 1: Renew SSL Certificate**
```bash
# If using Let's Encrypt
ssh root@217.79.255.54 'certbot renew'
ssh root@217.79.255.54 'systemctl reload nginx'

# If using custom certificate, replace files:
# /etc/ssl/certs/consulting.sa.crt
# /etc/ssl/private/consulting.sa.key
```

**Solution 2: Fix Nginx SSL Configuration**
```bash
ssh root@217.79.255.54 'cat > /etc/nginx/sites-available/agentic-platform << EOF
server {
    listen 443 ssl http2;
    server_name consulting.sa;
    
    ssl_certificate /etc/ssl/certs/consulting.sa.crt;
    ssl_certificate_key /etc/ssl/private/consulting.sa.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF'

ssh root@217.79.255.54 'nginx -t && systemctl reload nginx'
```

### 6. Docker Container Issues

#### Symptoms
- Containers not starting
- Out of memory errors
- Port conflicts

#### Diagnostic Steps
```bash
# Check container status
ssh root@217.79.255.54 'docker ps -a'

# Check container logs
ssh root@217.79.255.54 'docker logs agentic-frontend-dev'
ssh root@217.79.255.54 'docker logs agentic-backend-dev'

# Check system resources
ssh root@217.79.255.54 'docker stats'
ssh root@217.79.255.54 'df -h'
ssh root@217.79.255.54 'free -h'

# Check for port conflicts
ssh root@217.79.255.54 'netstat -tulpn | grep :3001'
ssh root@217.79.255.54 'netstat -tulpn | grep :8001'
```

#### Solutions

**Solution 1: Restart Containers**
```bash
ssh root@217.79.255.54 'cd /opt/agentic-platform-dev && ./dev-manage.sh restart'
```

**Solution 2: Rebuild Containers**
```bash
ssh root@217.79.255.54 'cd /opt/agentic-platform-dev && ./dev-manage.sh rebuild'
```

**Solution 3: Clean Up Docker**
```bash
ssh root@217.79.255.54 'docker system prune -f'
ssh root@217.79.255.54 'docker volume prune -f'
```

**Solution 4: Kill Conflicting Processes**
```bash
# Find process using port
ssh root@217.79.255.54 'lsof -i :3001'

# Kill process
ssh root@217.79.255.54 'kill -9 PID_NUMBER'
```

### 7. Performance Issues

#### Symptoms
- Slow page loading
- High CPU usage
- Memory leaks
- Database query timeouts

#### Diagnostic Steps
```bash
# Check system performance
ssh root@217.79.255.54 'htop'
ssh root@217.79.255.54 'iotop'

# Check container resource usage
ssh root@217.79.255.54 'docker stats'

# Check network performance
curl -w "@curl-format.txt" -o /dev/null -s https://consulting.sa

# Create curl-format.txt
echo "     time_namelookup:  %{time_namelookup}s
        time_connect:  %{time_connect}s
     time_appconnect:  %{time_appconnect}s
    time_pretransfer:  %{time_pretransfer}s
       time_redirect:  %{time_redirect}s
  time_starttransfer:  %{time_starttransfer}s
                     ----------
          time_total:  %{time_total}s" > curl-format.txt
```

#### Solutions

**Solution 1: Optimize Container Resources**
```yaml
# Update docker-compose.yml with resource limits
services:
  frontend-dev:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

**Solution 2: Enable Caching**
```bash
# Check Redis status
ssh root@217.79.255.54 'docker exec -it agentic-redis-dev redis-cli ping'

# Monitor Redis usage
ssh root@217.79.255.54 'docker exec -it agentic-redis-dev redis-cli info memory'
```

**Solution 3: Database Query Optimization**
```bash
# Check slow queries in Supabase dashboard
# Add database indexes for frequently queried fields
# Optimize N+1 query problems
```

### 8. API Integration Failures

#### Symptoms
- Third-party API errors
- Authentication failures
- Rate limiting errors

#### Diagnostic Steps
```bash
# Test API endpoints
curl -H "Authorization: Bearer YOUR_TOKEN" https://api.service.com/endpoint

# Check API key validity
# Verify in respective service dashboards

# Check rate limits
curl -I https://api.service.com/endpoint
```

#### Solutions

**Solution 1: Refresh API Keys**
```bash
# Update API keys in .env file
# Redeploy services
./infrastructure/scripts/deploy-dev-vps.sh
```

**Solution 2: Implement Retry Logic**
```python
import asyncio
from typing import Dict, Any

async def api_call_with_retry(
    url: str, 
    headers: Dict[str, str], 
    max_retries: int = 3
) -> Dict[str, Any]:
    """API call with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:  # Rate limited
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
                continue
            raise
        except httpx.RequestError:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)
    
    raise Exception("Max retries exceeded")
```

## Environment-Specific Troubleshooting

### Development Environment Issues

#### Issue: Development site not accessible
```bash
# Check development containers
ssh root@217.79.255.54 'cd /opt/agentic-platform-dev && ./dev-manage.sh status'

# Check nginx configuration for dev subdomain
ssh root@217.79.255.54 'cat /etc/nginx/sites-enabled/agentic-platform-dev'

# Test internal connectivity
ssh root@217.79.255.54 'curl -f http://localhost:3001'
ssh root@217.79.255.54 'curl -f http://localhost:8001/health'
```

#### Issue: Hot reloading not working
```bash
# Check if volumes are mounted correctly
ssh root@217.79.255.54 'docker inspect agentic-frontend-dev | grep -A 10 Mounts'

# Restart development containers
ssh root@217.79.255.54 'cd /opt/agentic-platform-dev && ./dev-manage.sh restart'
```

### Production Environment Issues

#### Issue: Production deployment failed
```bash
# Check deployment logs
./infrastructure/scripts/deploy.sh 2>&1 | tee deployment.log

# Rollback to previous version
ssh root@217.79.255.54 'cd /opt/agentic-platform && git log --oneline -5'
ssh root@217.79.255.54 'cd /opt/agentic-platform && git reset --hard HEAD~1'
./infrastructure/scripts/deploy.sh
```

#### Issue: High traffic causing issues
```bash
# Check current connections
ssh root@217.79.255.54 'netstat -an | grep :443 | wc -l'

# Monitor resource usage
ssh root@217.79.255.54 'watch "docker stats --no-stream"'

# Scale services if needed (manual scaling)
ssh root@217.79.255.54 'cd /opt/agentic-platform && docker-compose up -d --scale frontend=2'
```

## Monitoring and Alerting

### Health Check Automation
```bash
#!/bin/bash
# health-monitor.sh

ENDPOINTS=(
    "https://consulting.sa/api/health"
    "https://dev.consulting.sa/api/health"
    "https://consulting.sa:8000/health"
    "https://dev.consulting.sa:8001/health"
)

for endpoint in "${ENDPOINTS[@]}"; do
    if curl -f -s "$endpoint" > /dev/null; then
        echo "✅ $endpoint - OK"
    else
        echo "❌ $endpoint - FAILED"
        # Send alert (email, Slack, etc.)
        # curl -X POST -H 'Content-type: application/json' \
        #      --data '{"text":"Alert: '$endpoint' is down"}' \
        #      YOUR_SLACK_WEBHOOK_URL
    fi
done
```

### Log Monitoring
```bash
#!/bin/bash
# log-monitor.sh

# Monitor for errors in logs
ssh root@217.79.255.54 'cd /opt/agentic-platform && docker-compose logs --since=1h | grep -i error' | while read line; do
    echo "ERROR DETECTED: $line"
    # Send alert
done

# Monitor for high memory usage
ssh root@217.79.255.54 'docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}"' | while read line; do
    if [[ $line == *"GiB"* ]]; then
        echo "HIGH MEMORY USAGE: $line"
        # Send alert
    fi
done
```

### Performance Monitoring
```bash
#!/bin/bash
# performance-monitor.sh

# Check response times
response_time=$(curl -o /dev/null -s -w '%{time_total}' https://consulting.sa)
if (( $(echo "$response_time > 3.0" | bc -l) )); then
    echo "SLOW RESPONSE: ${response_time}s"
    # Send alert
fi

# Check SSL certificate expiration
cert_days=$(openssl s_client -connect consulting.sa:443 -servername consulting.sa 2>/dev/null | openssl x509 -noout -checkend 2592000)
if [ $? -ne 0 ]; then
    echo "SSL CERTIFICATE EXPIRING SOON"
    # Send alert
fi
```

## Emergency Procedures

### Complete System Failure

#### Step 1: Assess the Situation
```bash
# Check if server is reachable
ping 217.79.255.54

# Check if SSH is working
ssh root@217.79.255.54 'uptime'

# Check disk space
ssh root@217.79.255.54 'df -h'

# Check memory
ssh root@217.79.255.54 'free -h'
```

#### Step 2: Emergency Recovery
```bash
# Stop all services
ssh root@217.79.255.54 'cd /opt/agentic-platform && docker-compose down'
ssh root@217.79.255.54 'cd /opt/agentic-platform-dev && ./dev-manage.sh stop'

# Clear disk space if needed
ssh root@217.79.255.54 'docker system prune -af'
ssh root@217.79.255.54 'docker volume prune -f'

# Restart essential services
ssh root@217.79.255.54 'systemctl restart nginx'
ssh root@217.79.255.54 'cd /opt/agentic-platform && docker-compose up -d'
```

#### Step 3: Verify Recovery
```bash
# Check all health endpoints
curl -f https://consulting.sa/api/health
curl -f https://consulting.sa:8000/health

# Check logs for errors
ssh root@217.79.255.54 'cd /opt/agentic-platform && docker-compose logs --tail=50'
```

### Database Emergency

#### Step 1: Backup Current State
```bash
# Export current data from Supabase
# Use Supabase dashboard or CLI tools
supabase db dump --db-url "postgresql://..." > emergency_backup.sql
```

#### Step 2: Restore from Backup
```bash
# Restore from latest backup
supabase db reset --db-url "postgresql://..."
psql "postgresql://..." < latest_backup.sql
```

### Security Incident

#### Step 1: Immediate Response
```bash
# Block suspicious IPs (if identified)
ssh root@217.79.255.54 'iptables -A INPUT -s SUSPICIOUS_IP -j DROP'

# Change all API keys immediately
# Update .env file with new keys
# Redeploy all services
```

#### Step 2: Investigation
```bash
# Check access logs
ssh root@217.79.255.54 'tail -1000 /var/log/nginx/access.log | grep -E "(POST|PUT|DELETE)"'

# Check for unusual activity
ssh root@217.79.255.54 'last -n 50'
ssh root@217.79.255.54 'who'
```

## Maintenance Procedures

### Regular Maintenance Tasks

#### Daily Tasks
```bash
#!/bin/bash
# daily-maintenance.sh

# Check system health
curl -f https://consulting.sa/api/health
curl -f https://dev.consulting.sa/api/health

# Check disk space
ssh root@217.79.255.54 'df -h | grep -E "(8[0-9]%|9[0-9]%|100%)"'

# Check for errors in logs
ssh root@217.79.255.54 'cd /opt/agentic-platform && docker-compose logs --since=24h | grep -i error | wc -l'

# Update system packages
ssh root@217.79.255.54 'apt update && apt list --upgradable'
```

#### Weekly Tasks
```bash
#!/bin/bash
# weekly-maintenance.sh

# Clean up Docker
ssh root@217.79.255.54 'docker system prune -f'

# Check SSL certificate expiration
openssl s_client -connect consulting.sa:443 -servername consulting.sa 2>/dev/null | openssl x509 -noout -checkend 2592000

# Update dependencies
cd frontend && npm audit
cd backend/agent && pip list --outdated

# Backup important data
# Run backup scripts
```

#### Monthly Tasks
```bash
#!/bin/bash
# monthly-maintenance.sh

# Full system update
ssh root@217.79.255.54 'apt update && apt upgrade -y'

# Security audit
cd frontend && npm audit --audit-level high
cd backend/agent && safety check

# Performance review
# Analyze logs for performance issues
# Review resource usage trends

# Documentation update
# Update any outdated documentation
# Review and update troubleshooting guides
```

### Backup Procedures

#### Database Backup
```bash
#!/bin/bash
# backup-database.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"

# Create backup directory
ssh root@217.79.255.54 "mkdir -p $BACKUP_DIR"

# Backup Supabase data
supabase db dump --db-url "$SUPABASE_DB_URL" > "backup_${DATE}.sql"

# Upload to secure storage
# aws s3 cp "backup_${DATE}.sql" s3://your-backup-bucket/
```

#### Application Backup
```bash
#!/bin/bash
# backup-application.sh

DATE=$(date +%Y%m%d_%H%M%S)

# Backup application code
ssh root@217.79.255.54 "cd /opt && tar -czf agentic-platform-backup-${DATE}.tar.gz agentic-platform"

# Backup configuration files
ssh root@217.79.255.54 "tar -czf nginx-config-backup-${DATE}.tar.gz /etc/nginx/sites-available/agentic-platform*"

# Store backups securely
# scp root@217.79.255.54:/opt/agentic-platform-backup-${DATE}.tar.gz ./backups/
```

## Best Practices for Troubleshooting

### Systematic Approach
1. **Identify the Problem**: Gather symptoms and error messages
2. **Isolate the Issue**: Determine which component is affected
3. **Check Recent Changes**: Review recent deployments or changes
4. **Test Systematically**: Start with simple tests and progress to complex
5. **Document Solutions**: Record what worked for future reference

### Prevention Strategies
1. **Monitoring**: Implement comprehensive monitoring and alerting
2. **Testing**: Thorough testing before deployment
3. **Backups**: Regular backups of data and configurations
4. **Documentation**: Keep troubleshooting guides updated
5. **Training**: Ensure team knows common procedures

### Communication During Incidents
1. **Status Updates**: Regular updates to stakeholders
2. **Documentation**: Record all actions taken
3. **Post-Mortem**: Analyze incidents to prevent recurrence
4. **Knowledge Sharing**: Share learnings with the team

## Conclusion

This troubleshooting guide provides:

- **Quick Diagnostics**: Fast ways to identify issues
- **Common Solutions**: Proven fixes for frequent problems
- **Emergency Procedures**: Steps for critical situations
- **Maintenance Tasks**: Preventive maintenance procedures
- **Best Practices**: Systematic approach to problem-solving

Keep this guide updated as new issues are discovered and resolved. Regular maintenance and monitoring will prevent most issues from becoming critical problems.