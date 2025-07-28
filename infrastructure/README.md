# 🏗️ Infrastructure - Deployment and Operations

## Overview

The infrastructure directory contains all deployment configurations, scripts, and operational tools for the Agentic AI Platform. This includes Docker configurations, deployment scripts, monitoring setup, and SSL certificates.

## 🛠️ Technology Stack

### Core Technologies
- **Containerization**: Docker and Docker Compose
- **Web Server**: Nginx (reverse proxy and load balancer)
- **Monitoring**: Prometheus, Grafana, N8N
- **SSL/TLS**: Cloudflare Origin SSL certificates
- **Orchestration**: Bash scripts for deployment automation

### Infrastructure Components
- **Docker**: Multi-service containerization
- **Nginx**: Reverse proxy and SSL termination
- **Monitoring Stack**: Comprehensive observability
- **Deployment Scripts**: Automated deployment workflows
- **SSL Management**: Certificate management and renewal

## 🏗️ Directory Structure

```
infrastructure/
├── docker/                    # Docker configurations
│   ├── Dockerfile.frontend    # Next.js container
│   ├── Dockerfile.backend     # Python ADK agent container
│   ├── docker-compose.yml     # Development compose
│   ├── docker-compose.staging.yml    # Staging environment
│   ├── docker-compose.production.yml # Production environment
│   └── .dockerignore         # Docker ignore patterns
├── scripts/                  # Deployment and management scripts
│   ├── deploy-organized.sh   # Main deployment script
│   ├── deploy-main-vps.sh    # VPS deployment
│   ├── setup-monitoring.sh   # Monitoring setup
│   ├── health-check.sh       # Health monitoring
│   ├── validate-deployment.sh # Deployment validation
│   └── ci/                   # CI/CD scripts
├── nginx/                    # Nginx configurations
│   ├── production.conf       # Production config
│   └── staging.conf          # Staging config
├── ssl/                      # SSL certificates
│   ├── consulting.sa.crt     # SSL certificate
│   └── consulting.sa.key     # Private key
├── monitoring/               # Monitoring stack
│   ├── prometheus.yml        # Prometheus config
│   ├── alert_rules.yml       # Alert rules
│   ├── docker-compose.monitoring.yml # Monitoring services
│   ├── grafana/             # Grafana dashboards
│   ├── prometheus/          # Prometheus configs
│   ├── alertmanager/        # Alert manager
│   ├── blackbox/            # Blackbox exporter
│   └── n8n/                 # N8N workflows
├── ansible/                  # Ansible playbooks (if used)
│   ├── inventory/           # Server inventory
│   └── playbooks/           # Deployment playbooks
├── cleanup/                  # Project cleanup tools
│   ├── project_analyzer.py  # Project analysis
│   ├── file_mapper.py       # File mapping
│   ├── workspace_setup.py   # Workspace setup
│   └── update_imports.py    # Import updates
├── .gitignore               # Infrastructure gitignore
└── README.md               # This file
```

## 🚀 Deployment Options

### 1. Production VPS Deployment (Recommended)

#### Current Production Status ✅
- **Server**: 217.79.255.54
- **Frontend**: Running on port 3911
- **Backend**: Running on port 8953
- **SSL**: Cloudflare Origin SSL configured
- **Monitoring**: Full stack deployed

#### Deploy to Production VPS
```bash
# Deploy organized structure
./infrastructure/scripts/deploy-organized.sh

# Or deploy to main VPS
./infrastructure/scripts/deploy-main-vps.sh
```

### 2. Docker Compose Deployment

#### Development Environment
```bash
cd infrastructure/docker
docker-compose up --build
```

#### Staging Environment
```bash
cd infrastructure/docker
docker-compose -f docker-compose.staging.yml up -d
```

#### Production Environment
```bash
cd infrastructure/docker
docker-compose -f docker-compose.production.yml up -d
```

### 3. Local Development (No Docker)

#### Frontend Only
```bash
cd frontend
npm run dev
```

#### Backend Only
```bash
cd backend/agent
uv run python main.py
```

#### Full Stack
```bash
# Terminal 1 - Frontend
cd frontend && npm run dev

# Terminal 2 - Backend
cd backend/agent && uv run python main.py
```

## 🐳 Docker Configuration

### Frontend Container (Dockerfile.frontend)
```dockerfile
FROM node:18-alpine AS base
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci --only=production

FROM base AS build
COPY frontend/ .
RUN npm run build

FROM base AS runtime
COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
EXPOSE 3000
CMD ["npm", "start"]
```

### Backend Container (Dockerfile.backend)
```dockerfile
FROM python:3.11-slim AS base
WORKDIR /app

# Install uv
RUN pip install uv

# Copy backend files
COPY backend/ .
COPY .env .env

# Install dependencies with uv
RUN uv sync

# Expose port
EXPOSE 8000

# Start agent
CMD ["uv", "run", "python", "agent/main.py"]
```

### Docker Compose Services
```yaml
# docker-compose.production.yml
version: '3.8'
services:
  frontend:
    build:
      context: ../..
      dockerfile: infrastructure/docker/Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    depends_on:
      - backend

  backend:
    build:
      context: ../..
      dockerfile: infrastructure/docker/Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app/agent
    volumes:
      - ../../.env:/app/.env

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ../nginx/production.conf:/etc/nginx/nginx.conf
      - ../ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
```

## 📊 Monitoring Stack

### Components
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **N8N**: Workflow automation and alerting
- **Alertmanager**: Alert routing and management
- **Blackbox Exporter**: External service monitoring

### Setup Monitoring
```bash
# Deploy monitoring stack
./infrastructure/scripts/setup-monitoring.sh

# Or use Docker Compose
cd infrastructure/monitoring
docker-compose -f docker-compose.monitoring.yml up -d
```

### Access Points
- **Grafana**: http://your-server:3001
- **Prometheus**: http://your-server:9090
- **N8N**: http://your-server:5678
- **Alertmanager**: http://your-server:9093

### Monitoring Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'agentic-frontend'
    static_configs:
      - targets: ['frontend:3000']
    metrics_path: '/api/metrics'

  - job_name: 'agentic-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
```

## 🔒 SSL Configuration

### Cloudflare Origin SSL
- **Certificate**: `/etc/nginx/ssl/consulting.sa.crt`
- **Private Key**: `/etc/nginx/ssl/consulting.sa.key`
- **Validity**: Until 2040-07-17 (15+ years)
- **Domains**: consulting.sa, www.consulting.sa

### Nginx SSL Configuration
```nginx
# production.conf
server {
    listen 443 ssl http2;
    server_name consulting.sa www.consulting.sa;

    ssl_certificate /etc/nginx/ssl/consulting.sa.crt;
    ssl_certificate_key /etc/nginx/ssl/consulting.sa.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/agent/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📜 Deployment Scripts

### Main Deployment Script
```bash
# deploy-organized.sh
#!/bin/bash
set -e

echo "🚀 Deploying Agentic AI Platform..."

# Build and deploy frontend
echo "📱 Building frontend..."
cd frontend
npm run build
cd ..

# Sync backend dependencies
echo "🤖 Syncing backend dependencies..."
cd backend
uv sync
cd agent
uv sync
cd ../..

# Deploy with Docker Compose
echo "🐳 Deploying with Docker..."
cd infrastructure/docker
docker-compose -f docker-compose.production.yml up -d --build

echo "✅ Deployment completed!"
```

### Health Check Script
```bash
# health-check.sh
#!/bin/bash

echo "🏥 Performing health checks..."

# Check frontend
if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "✅ Frontend: Healthy"
else
    echo "❌ Frontend: Unhealthy"
fi

# Check backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend: Healthy"
else
    echo "❌ Backend: Unhealthy"
fi

# Check monitoring
if curl -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo "✅ Prometheus: Healthy"
else
    echo "❌ Prometheus: Unhealthy"
fi
```

## 🔧 Environment Configuration

### Production Environment Variables
```env
# Core Application
NODE_ENV=production
PYTHONPATH=/app/agent

# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_production_anon_key
SUPABASE_SERVICE_KEY=your_production_service_key

# Domain Configuration
DOMAIN=consulting.sa
NEXT_PUBLIC_DOMAIN=consulting.sa
NEXT_PUBLIC_SITE_URL=https://consulting.sa

# SSL Configuration
FORCE_HTTPS=true

# Monitoring
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3001
N8N_URL=http://n8n:5678
```

### Docker Environment
```env
# Docker Configuration
COMPOSE_PROJECT_NAME=agentic-platform
COMPOSE_HTTP_TIMEOUT=120
DOCKER_BUILDKIT=1
```

## 🧪 Testing and Validation

### Deployment Validation
```bash
# Validate deployment
./infrastructure/scripts/validate-deployment.sh

# Check service health
./infrastructure/scripts/health-check.sh

# Test organized structure
./test-organized-structure.sh
```

### Manual Testing
```bash
# Test frontend
curl -I http://localhost:3000

# Test backend
curl -I http://localhost:8000/health

# Test SSL
curl -I https://consulting.sa

# Test monitoring
curl -I http://localhost:9090/-/healthy
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Docker Build Failures
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache

# Check Docker logs
docker-compose logs -f
```

#### 2. SSL Certificate Issues
```bash
# Check certificate validity
openssl x509 -in infrastructure/ssl/consulting.sa.crt -text -noout

# Test SSL connection
openssl s_client -connect consulting.sa:443

# Verify certificate chain
curl -I https://consulting.sa
```

#### 3. Service Connection Issues
```bash
# Check service status
docker-compose ps

# Check service logs
docker-compose logs service-name

# Test internal connectivity
docker-compose exec frontend ping backend
```

#### 4. Monitoring Issues
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check Grafana datasources
curl http://admin:admin@localhost:3001/api/datasources

# Restart monitoring stack
cd infrastructure/monitoring
docker-compose restart
```

## 📊 Performance Optimization

### Docker Optimization
- Multi-stage builds for smaller images
- Layer caching for faster builds
- Resource limits for containers
- Health checks for reliability

### Nginx Optimization
- Gzip compression enabled
- Static file caching
- Connection pooling
- Rate limiting

### Monitoring Optimization
- Efficient metric collection
- Alert rule optimization
- Dashboard performance tuning
- Data retention policies

## 🔒 Security Best Practices

### Container Security
- Non-root user execution
- Minimal base images
- Security scanning
- Regular updates

### Network Security
- Internal network isolation
- Firewall configuration
- SSL/TLS encryption
- Access control

### Secrets Management
- Environment variable encryption
- Secret rotation
- Access logging
- Audit trails

## 🚀 Scaling Considerations

### Horizontal Scaling
- Load balancer configuration
- Database connection pooling
- Session management
- Cache distribution

### Vertical Scaling
- Resource monitoring
- Performance profiling
- Capacity planning
- Auto-scaling policies

## 📚 Related Documentation

- [Main README](../README.md) - Project overview
- [Frontend README](../frontend/README.md) - Frontend documentation
- [Backend README](../backend/README.md) - Backend documentation
- [LOCAL_TESTING_GUIDE.md](../LOCAL_TESTING_GUIDE.md) - Local testing guide

## 📞 Support

For infrastructure-related issues:
- Check deployment logs
- Verify environment configuration
- Test individual services
- Review monitoring dashboards

For general support, contact: asim@consulting.sa