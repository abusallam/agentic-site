# 🚀 Agentic AI Platform - Complete Deployment Guide

This guide provides a systematic approach to deploying your agentic AI platform with CI/CD pipeline, incorporating all lessons learned from production deployments.

## 📋 Prerequisites

- **VPS Server**: 217.79.255.54 (configured and accessible)
- **Domain**: consulting.sa (DNS configured to point to VPS)
- **Local Machine**: Linux/macOS with sshpass, Docker, Node.js, Python
- **Required Keys**: Supabase, Gemini API, GitHub token
- **SSL Certificates**: Valid SSL certificate and key files

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Main VPS (217.79.255.54)                │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Nginx     │  │  Frontend   │  │   Backend   │        │
│  │   (443)     │  │   (3000)    │  │   (8000)    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │     n8n     │  │  Grafana    │  │ Prometheus  │        │
│  │   (5678)    │  │   (3001)    │  │   (9090)    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Systematic Deployment Process

### Option 1: Improved Systematic Deployment (Recommended)

```bash
# Run the improved deployment script with all lessons learned
./scripts/deploy-main-vps-improved.sh
```

This systematic approach includes:
1. ✅ **Prerequisites Validation** - Verify all requirements
2. ✅ **Infrastructure Setup** - Configure VPS with proper error handling
3. ✅ **File Deployment** - Robust file transfer with exclusions
4. ✅ **Container Management** - Build and start with context fixes
5. ✅ **SSL & Nginx Configuration** - Proper certificate and config setup
6. ✅ **Deployment Validation** - Comprehensive health checks
7. ✅ **Monitoring Setup** - Status scripts and monitoring tools

### Option 2: Quick Deployment (Legacy)

```bash
# Run the original deployment script
./scripts/deploy-main-vps.sh
```

### Step 3: Validate Deployment

```bash
# Run comprehensive validation (28 automated tests)
./scripts/validate-deployment.sh
```

This validation script tests:
- Infrastructure components (Docker, Nginx, Firewall)
- Container health and status
- SSL certificates and security
- Application health endpoints
- Network connectivity
- File permissions and directories
- Performance and resource usage
- Security configurations

### Step 4: Set Up Monitoring (Phase 2)

```bash
# Install n8n, Grafana, and monitoring
./scripts/setup-monitoring.sh
```

## 📁 Project Structure

```
agentic-platform/
├── 🌐 Frontend (Next.js)
│   ├── app/                    # Next.js app directory
│   ├── components/             # React components
│   └── Dockerfile.frontend     # Frontend container
│
├── 🤖 Backend (Python ADK Agent)
│   ├── agent/
│   │   ├── my_adk_agent/      # Main agent code
│   │   │   ├── services/      # Service integrations
│   │   │   └── tools/         # ADK tools
│   │   ├── api_server.py      # FastAPI server
│   │   └── requirements.txt   # Python dependencies
│   └── Dockerfile.backend     # Backend container
│
├── 🔧 Infrastructure
│   ├── nginx/                 # Nginx configurations
│   ├── monitoring/            # Prometheus, Grafana
│   └── scripts/               # Deployment scripts
│
├── 🚀 CI/CD
│   ├── .github/workflows/     # GitHub Actions
│   └── docker-compose.*.yml   # Container orchestration
│
└── 📝 Configuration
    ├── .env                   # Environment variables
    └── .env.example          # Template
```

## 🔑 Environment Variables

### Required Variables
```bash
# VPS Configuration
VPS_HOST=217.79.255.54
VPS_USER=root
VPS_PASSWORD=xxXNCpx9Cz
DOMAIN=consulting.sa

# Database (Supabase)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# AI Services
GEMINI_API_KEY=your_gemini_key
```

### Optional Variables
```bash
# GitHub CI/CD
GITHUB_TOKEN=your_github_token
GITHUB_REPOSITORY=username/repo-name

# Additional Services
LIVEKIT_URL=your_livekit_url
STRIPE_SECRET_KEY=your_stripe_key
```

## 🌐 Service Access URLs

After deployment, you can access:

### Main Application
- **Website**: https://consulting.sa
- **API**: https://consulting.sa/api
- **Health Check**: https://consulting.sa/api/health

### Monitoring & Tools (Phase 2)
- **n8n Workflows**: http://217.79.255.54:5678
- **Grafana Dashboards**: http://217.79.255.54:3001
- **Prometheus Metrics**: http://217.79.255.54:9090

### Default Credentials
- **n8n**: admin / admin123
- **Grafana**: admin / admin123

## 🛠️ Management Commands

### Check Status
```bash
# Check deployment status
./scripts/check-deployment.sh

# Check all services on VPS
sshpass -p 'gt5qXy22aJ' ssh root@217.79.255.54 '/opt/check-all-services.sh'
```

### View Logs
```bash
# View application logs
sshpass -p 'gt5qXy22aJ' ssh root@217.79.255.54 'cd /opt/agentic-platform && docker-compose -f docker-compose.production.yml logs -f'

# View specific service logs
sshpass -p 'gt5qXy22aJ' ssh root@217.79.255.54 'cd /opt/agentic-platform && docker-compose -f docker-compose.production.yml logs -f frontend'
```

### Restart Services
```bash
# Restart all services
sshpass -p 'gt5qXy22aJ' ssh root@217.79.255.54 'cd /opt/agentic-platform && docker-compose -f docker-compose.production.yml restart'

# Restart specific service
sshpass -p 'gt5qXy22aJ' ssh root@217.79.255.54 'cd /opt/agentic-platform && docker-compose -f docker-compose.production.yml restart backend'
```

### Update Deployment
```bash
# Redeploy with latest changes
./scripts/deploy-main-vps.sh
```

## 🔒 Security Features

- ✅ **SSL/TLS**: Automatic Let's Encrypt certificates
- ✅ **Firewall**: UFW configured with minimal ports
- ✅ **Rate Limiting**: Nginx rate limiting
- ✅ **Security Scanning**: Automated vulnerability checks
- ✅ **Container Security**: Non-root users, health checks
- ✅ **Fail2ban**: Protection against brute force attacks

## 📊 Monitoring & Alerts

### Built-in Monitoring
- **Health Checks**: Automatic service health monitoring
- **Metrics Collection**: Prometheus metrics
- **Log Aggregation**: Centralized logging
- **Performance Monitoring**: Response time tracking

### Custom Dashboards
- **System Resources**: CPU, memory, disk usage
- **Application Metrics**: Request rates, error rates
- **Agent Performance**: Workflow execution stats
- **Database Health**: Connection status, query performance

## 🔄 CI/CD Pipeline

### Automated Testing
- **Frontend Tests**: Jest, Playwright
- **Backend Tests**: Pytest, integration tests
- **Security Scans**: CodeQL, dependency checks
- **Container Scans**: Trivy vulnerability scanning

### Deployment Stages
1. **Code Push** → GitHub
2. **Automated Testing** → CI pipeline
3. **Security Scanning** → Vulnerability checks
4. **Build Containers** → Docker images
5. **Deploy to VPS** → Production deployment
6. **Health Validation** → Post-deployment checks

## 🐛 Troubleshooting

### Common Issues

#### 1. VPS Connection Failed
```bash
# Test connection
sshpass -p 'gt5qXy22aJ' ssh root@217.79.255.54 'echo "Connection test"'

# Check firewall
sshpass -p 'gt5qXy22aJ' ssh root@217.79.255.54 'ufw status'
```

#### 2. SSL Certificate Issues
```bash
# Check certificate status
sshpass -p 'gt5qXy22aJ' ssh root@217.79.255.54 'certbot certificates'

# Renew certificate
sshpass -p 'gt5qXy22aJ' ssh root@217.79.255.54 'certbot renew'
```

#### 3. Service Not Starting
```bash
# Check container status
sshpass -p 'gt5qXy22aJ' ssh root@217.79.255.54 'cd /opt/agentic-platform && docker-compose -f docker-compose.production.yml ps'

# View container logs
sshpass -p 'gt5qXy22aJ' ssh root@217.79.255.54 'cd /opt/agentic-platform && docker-compose -f docker-compose.production.yml logs backend'
```

#### 4. DNS Not Resolving
- Update your domain DNS to point to: `217.79.255.54`
- Wait for DNS propagation (up to 24 hours)
- Test with: `nslookup consulting.sa`

### Log Locations
- **Application Logs**: `/opt/agentic-platform/`
- **Nginx Logs**: `/var/log/nginx/`
- **System Logs**: `/var/log/syslog`

## 📞 Support

### Quick Commands Reference
```bash
# Update configuration
./scripts/update-config.sh

# Full deployment
./scripts/test-and-deploy.sh

# Check status
./scripts/check-deployment.sh

# Setup monitoring
./scripts/setup-monitoring.sh

# View logs
sshpass -p 'gt5qXy22aJ' ssh root@217.79.255.54 'cd /opt/agentic-platform && docker-compose -f docker-compose.production.yml logs -f'
```

### Next Steps After Deployment
1. ✅ Update DNS settings
2. ✅ Test all functionality
3. ✅ Configure n8n workflows
4. ✅ Set up monitoring dashboards
5. ✅ Configure alerts and notifications
6. ✅ Create backup procedures

---

## 🎉 Congratulations!

Your Agentic AI platform is now deployed with:
- ✅ **Production-ready infrastructure**
- ✅ **Automated CI/CD pipeline**
- ✅ **Comprehensive monitoring**
- ✅ **Security best practices**
- ✅ **Scalable architecture**

Your platform is ready to serve customers and handle AI-powered workflows! 🚀