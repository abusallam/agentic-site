# 🐳 Docker Compose Deployment Guide - AI SaaS Platform

This guide will help you deploy the AI SaaS Platform using Docker Compose on Coolify for better service management and scalability.

## 🏗️ Architecture Overview

The Docker Compose setup separates the application into distinct services:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Migration     │
│   (Next.js)     │◄──►│  (Python Agent) │    │  (Database)     │
│   Port: 3000    │    │   Port: 8080    │    │   (One-time)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Services:
- **Frontend**: Next.js application with UI and API routes
- **Backend**: Python agent system with FastAPI server
- **Migration**: Database setup and schema migration (runs once)

## 📁 Docker Compose Files

### Core Files:
- `docker-compose.yml` - Main service definitions
- `docker-compose.coolify.yml` - Coolify-specific overrides
- `Dockerfile.frontend` - Next.js application container
- `Dockerfile.backend` - Python agent container
- `Dockerfile.migrate` - Database migration container

## 🚀 Quick Deployment

### 1. Prepare for Deployment

```bash
# Run the deployment preparation script
./scripts/deploy-docker-compose.sh

# Optional: Test build locally
./scripts/deploy-docker-compose.sh --test-build
```

### 2. Push to Git Repository

```bash
git add .
git commit -m "Docker Compose deployment ready"
git push origin main
```

### 3. Deploy on Coolify

#### Step 1: Create New Application
1. Login to Coolify Dashboard
2. Click "New Resource" → "Application"
3. Select "Docker Compose" as deployment type
4. Connect your Git repository: `https://github.com/abusallam/agentic-site`

#### Step 2: Configure Deployment
- **Branch**: `main`
- **Compose File**: `docker-compose.yml`
- **Override File**: `docker-compose.coolify.yml` (optional)

#### Step 3: Set Environment Variables

**Required Variables:**
```env
# Core Configuration
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1

# Supabase Database
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# AI Services
GEMINI_API_KEY=your_gemini_api_key

# Contact Information
NEXT_PUBLIC_CONTACT_EMAIL=asim@consulting.sa
```

**Optional Variables:**
```env
# Additional AI Services
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Payment Processing
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret

# Real-time Communication
LIVEKIT_URL=wss://your-livekit-url
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret

# Workflow Automation
N8N_URL=https://n8n.consulting.sa
N8N_BASE_URL=https://n8n.consulting.sa
N8N_API_KEY=your_n8n_api_key

# GitHub Integration (for MCP tools)
GITHUB_TOKEN=your_github_token

# Custom Ports (Coolify will override)
PORT=3000
BACKEND_PORT=8080
```

#### Step 4: Configure Domains
1. Go to **Domains** tab
2. Add your domains:
   - `consulting.sa` (primary)
   - `www.consulting.sa` (redirect)
3. Enable **SSL/TLS**
4. Enable **HTTP to HTTPS redirect**

#### Step 5: Deploy
1. Click **Deploy** button
2. Monitor build logs for all services
3. Wait for all health checks to pass

## 🔍 Service Health Checks

Each service has comprehensive health monitoring:

### Frontend Health Check
- **Endpoint**: `http://frontend:3000/api/health`
- **Response**:
```json
{
  "status": "healthy",
  "service": "ai-saas-platform",
  "version": "2.0.0",
  "services": {
    "frontend": { "status": "healthy", "port": 3000 },
    "backend": { "status": "healthy", "port": 8080 }
  }
}
```

### Backend Health Check
- **Endpoint**: `http://backend:8080/api/health`
- **Response**:
```json
{
  "status": "healthy",
  "agent_initialized": true,
  "services": {
    "supabase": "connected",
    "n8n_mcp": "available",
    "stripe": "configured"
  }
}
```

## 🌐 Access Points

After successful deployment:

### Public URLs
- **Main Website**: `https://consulting.sa`
- **Health Check**: `https://consulting.sa/api/health`
- **Admin Dashboard**: `https://consulting.sa/admin/dashboard`
- **Customer Portal**: `https://consulting.sa/customer/dashboard`

### Admin Access
- **URL**: `https://consulting.sa/admin/dashboard`
- **Password**: `admin123`
- **Features**: Agent monitoring, customer sessions, system analytics

### Customer Access
- **URL**: `https://consulting.sa/customer/dashboard`
- **Login**: Any email address (demo mode)
- **Features**: Personal agents, usage analytics, agent controls

## 🔧 Local Development

### Start All Services
```bash
# Start in detached mode
docker-compose up -d

# Start with logs
docker-compose up
```

### Monitor Services
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f db-migrate
```

### Service Management
```bash
# Stop all services
docker-compose down

# Restart specific service
docker-compose restart frontend

# Rebuild services
docker-compose build --no-cache

# Scale services (if needed)
docker-compose up -d --scale frontend=2
```

### Development Workflow
```bash
# 1. Make changes to code
# 2. Rebuild affected service
docker-compose build frontend

# 3. Restart service
docker-compose up -d frontend

# 4. Check logs
docker-compose logs -f frontend
```

## 📊 Monitoring & Debugging

### Service Status
```bash
# Check running services
docker-compose ps

# Check service health
curl http://localhost:3000/api/health
curl http://localhost:8080/api/health
```

### Resource Usage
```bash
# View resource usage
docker stats

# View service-specific stats
docker stats $(docker-compose ps -q)
```

### Debugging Issues
```bash
# Enter service container
docker-compose exec frontend sh
docker-compose exec backend bash

# View service configuration
docker-compose config

# Validate compose file
docker-compose config --quiet
```

## 🔄 Updates & Maintenance

### Rolling Updates
1. **Update code** in repository
2. **Push changes** to main branch
3. **Coolify auto-deploys** (if enabled)
4. **Zero-downtime** deployment with health checks

### Manual Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart services
docker-compose build --no-cache
docker-compose up -d

# Verify health
curl https://consulting.sa/api/health
```

### Database Migrations
The migration service runs automatically on deployment:
```bash
# Manual migration (if needed)
docker-compose run --rm db-migrate
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Service Won't Start
```bash
# Check logs
docker-compose logs service-name

# Common fixes:
- Check environment variables
- Verify port conflicts
- Check resource limits
```

#### 2. Health Check Failures
```bash
# Test health endpoints
curl -v http://localhost:3000/api/health
curl -v http://localhost:8080/api/health

# Check service connectivity
docker-compose exec frontend ping backend
```

#### 3. Database Connection Issues
```bash
# Check migration logs
docker-compose logs db-migrate

# Verify Supabase credentials
docker-compose exec backend env | grep SUPABASE
```

#### 4. Build Failures
```bash
# Clean build
docker-compose build --no-cache --pull

# Check Dockerfile syntax
docker build -f Dockerfile.frontend .
docker build -f Dockerfile.backend .
```

### Debug Commands
```bash
# Service inspection
docker-compose exec frontend env
docker-compose exec backend ps aux

# Network debugging
docker network ls
docker network inspect ai-saas-network

# Volume inspection
docker volume ls
docker-compose exec frontend df -h
```

## 📈 Performance Optimization

### Resource Limits
Configure in `docker-compose.yml`:
```yaml
services:
  frontend:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.1'
```

### Scaling Services
```bash
# Scale frontend for high traffic
docker-compose up -d --scale frontend=3

# Use load balancer (Coolify handles this)
```

### Caching Strategies
- **Frontend**: Static asset caching via Next.js
- **Backend**: API response caching
- **Database**: Connection pooling via Supabase

## 🔐 Security Considerations

### Environment Variables
- All secrets stored in Coolify environment
- No hardcoded credentials in containers
- Environment-specific configurations

### Network Security
- Internal service communication
- Frontend-only public exposure
- Secure inter-service communication

### Container Security
- Non-root users in all containers
- Minimal base images
- Regular security updates

## 📞 Support & Maintenance

### Monitoring
- **Health Checks**: Automated via Coolify
- **Logs**: Centralized via Docker Compose
- **Metrics**: Available through Coolify dashboard

### Backup Strategy
- **Database**: Supabase automated backups
- **Code**: Git repository
- **Configuration**: Environment variables in Coolify

### Support Contacts
- **Technical Issues**: Check logs and health endpoints
- **Deployment Issues**: Verify environment variables
- **Performance Issues**: Monitor resource usage

---

## 🎉 Deployment Complete!

Your AI SaaS Platform is now running with Docker Compose on Coolify:

✅ **Multi-service architecture**  
✅ **Automated health monitoring**  
✅ **Zero-downtime deployments**  
✅ **Scalable service management**  
✅ **Comprehensive logging**  
✅ **Production-ready security**  

**Main URL**: https://consulting.sa  
**Admin Panel**: https://consulting.sa/admin/dashboard  
**Customer Portal**: https://consulting.sa/customer/dashboard  
**Health Status**: https://consulting.sa/api/health  

Enjoy your production-ready AI SaaS platform with Docker Compose! 🚀