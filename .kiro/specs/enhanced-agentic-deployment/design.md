# Enhanced Agentic Site Deployment Design

## Architecture Overview

### Current VPS State
- **Server**: 217.79.255.54 (ssdnode-11723579473)
- **Health Score**: 100/100 - Excellent condition
- **Existing Deployments**: 
  - `tacticalops-redis` (tac.consulting.sa stack)
- **Available Resources**: 23GB RAM, 394GB disk, low CPU usage

### Container Stack Architecture

```
VPS Server (217.79.255.54)
├── Production Stack (consulting.sa)
│   ├── agentic-frontend-prod (port 3000)
│   ├── agentic-backend-prod (port 8000)
│   ├── agentic-redis-prod (port 6379)
│   └── agentic-n8n-prod (port 5678)
├── Development Stack (dev.consulting.sa)
│   ├── agentic-frontend-dev (port 3001)
│   ├── agentic-backend-dev (port 8001)
│   ├── agentic-redis-dev (port 6380)
│   └── agentic-n8n-dev (port 5679)
└── TacticalOps Stack (tac.consulting.sa)
    └── tacticalops-redis (port 6382) [EXISTING - DO NOT TOUCH]
```

### Network Isolation

```yaml
Networks:
  agentic-prod-network: 172.20.0.0/16
  agentic-dev-network: 172.21.0.0/16
  tacticalops_tacticalops-network: [EXISTING - PRESERVE]
```

## Deployment Strategy

### Phase 1: Production Stack Deployment
1. **Build and Deploy Production Containers**
   - Use existing VPS deployment scripts
   - Deploy to `agentic-prod-network`
   - Configure consulting.sa domain
   - Validate SSL certificates

### Phase 2: Development Stack Deployment
1. **Build and Deploy Development Containers**
   - Use offset ports (3001, 8001, 6380, 5679)
   - Deploy to `agentic-dev-network`
   - Configure dev.consulting.sa domain
   - Validate SSL certificates

### Phase 3: Enhanced Features Testing
1. **Five-Agent System Validation**
   - Test all agent routing and responses
   - Validate Arabic/English language support
   - Test voice interaction capabilities
   - Validate file upload processing
   - Test billing system with Saudi VAT

### Phase 4: Domain and SSL Configuration
1. **Nginx Configuration**
   - Update production.conf for consulting.sa
   - Create development.conf for dev.consulting.sa
   - Preserve existing tac.conf configuration
   - Validate SSL certificate routing

## Technical Implementation

### Container Configuration

#### Production Stack
```yaml
services:
  agentic-frontend-prod:
    image: agentic/frontend:latest
    container_name: agentic-frontend-prod
    ports: ["3000:3000"]
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_DOMAIN=consulting.sa
    networks: [agentic-prod-network]
    
  agentic-backend-prod:
    image: agentic/backend:latest
    container_name: agentic-backend-prod
    ports: ["8000:8000"]
    environment:
      - PYTHONPATH=/app
      - ENVIRONMENT=production
    networks: [agentic-prod-network]
    
  agentic-redis-prod:
    image: redis:7-alpine
    container_name: agentic-redis-prod
    ports: ["6379:6379"]
    networks: [agentic-prod-network]
    
  agentic-n8n-prod:
    image: n8nio/n8n:latest
    container_name: agentic-n8n-prod
    ports: ["5678:5678"]
    networks: [agentic-prod-network]
```

#### Development Stack
```yaml
services:
  agentic-frontend-dev:
    image: agentic/frontend:latest
    container_name: agentic-frontend-dev
    ports: ["3001:3000"]
    environment:
      - NODE_ENV=development
      - NEXT_PUBLIC_DOMAIN=dev.consulting.sa
    networks: [agentic-dev-network]
    
  agentic-backend-dev:
    image: agentic/backend:latest
    container_name: agentic-backend-dev
    ports: ["8001:8000"]
    environment:
      - PYTHONPATH=/app
      - ENVIRONMENT=development
    networks: [agentic-dev-network]
    
  agentic-redis-dev:
    image: redis:7-alpine
    container_name: agentic-redis-dev
    ports: ["6380:6379"]
    networks: [agentic-dev-network]
    
  agentic-n8n-dev:
    image: n8nio/n8n:latest
    container_name: agentic-n8n-dev
    ports: ["5679:5678"]
    networks: [agentic-dev-network]
```

### Nginx Configuration

#### Production Domain (consulting.sa)
```nginx
server {
    listen 80;
    server_name consulting.sa www.consulting.sa;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name consulting.sa www.consulting.sa;
    
    ssl_certificate /opt/ssl/certificates/consulting.sa.crt;
    ssl_certificate_key /opt/ssl/private/consulting.sa.key;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Development Domain (dev.consulting.sa)
```nginx
server {
    listen 80;
    server_name dev.consulting.sa;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name dev.consulting.sa;
    
    ssl_certificate /opt/ssl/certificates/consulting.sa.crt;
    ssl_certificate_key /opt/ssl/private/consulting.sa.key;
    
    location / {
        proxy_pass http://localhost:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Testing Strategy

### Automated Testing Suite
1. **System Health Validation**
   - Container health checks
   - Network connectivity tests
   - Resource usage monitoring

2. **Five-Agent System Tests**
   - Initial Customer Agent (Arabic/English greeting)
   - N8N Workflow Agent (automation requests)
   - Code Generation Agent (development requests)
   - Consulting Agent (strategic advice)
   - Billing Agent (pricing and VAT calculations)

3. **Enhanced Features Tests**
   - Voice interaction (speech-to-text/text-to-speech)
   - File upload processing
   - Multi-language support
   - Context preservation
   - Agent handoff scenarios

4. **Domain and SSL Tests**
   - HTTPS redirect validation
   - SSL certificate verification
   - Domain routing accuracy
   - Cross-environment isolation

### Performance Benchmarks
- Response time < 1.5s for frontend
- API response time < 500ms
- Agent processing < 2s
- Concurrent user handling (10+ users)

## Security Considerations

### Container Security
- Non-root user execution
- Resource limits and quotas
- Network isolation between stacks
- Health check endpoints

### SSL/TLS Configuration
- Cloudflare Origin certificates
- HTTPS-only communication
- Certificate auto-renewal
- Strong cipher suites

### Access Control
- Firewall rules for required ports only
- Fail2ban protection for SSH
- Container-to-container communication restrictions
- Environment variable security

## Monitoring and Alerting

### Health Monitoring
- Container health status
- Application endpoint monitoring
- Resource usage tracking
- SSL certificate expiration alerts

### Performance Monitoring
- Response time metrics
- Error rate tracking
- Agent performance analytics
- User interaction patterns

### Alert Configuration
- Critical service failures
- Resource threshold breaches
- Security event notifications
- SSL certificate expiration warnings

## Rollback Strategy

### Backup Procedures
- Pre-deployment container snapshots
- Configuration file backups
- Database state preservation
- Network configuration backup

### Recovery Process
1. Stop new deployment containers
2. Restore previous container images
3. Revert configuration changes
4. Validate system functionality
5. Update DNS if necessary

### Rollback Triggers
- Health check failures
- Performance degradation
- Security vulnerabilities
- User-reported critical issues

## Success Metrics

### Technical Metrics
- 99.9% uptime target
- < 1.5s page load time
- < 500ms API response time
- Zero security incidents

### Business Metrics
- All five agents operational
- Multi-language support functional
- Voice features working
- Billing system accurate
- Customer satisfaction maintained