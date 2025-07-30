# VPS Server Main - Infrastructure Documentation

## 🖥️ **Server Information**

### **Basic Details**
- **Server Name**: VPS Main (Primary Server)
- **IP Address**: 217.79.255.54
- **Provider**: [Provider Name]
- **OS**: Ubuntu/Linux
- **SSH Access**: root@217.79.255.54
- **SSH Password**: xxXNCpx9Cz (stored in environment variables)

### **Server Specifications**
- **CPU**: [CPU Details]
- **RAM**: [RAM Amount]
- **Storage**: [Storage Details]
- **Network**: [Network Configuration]

## 🐳 **Docker Containers Status**

### **Production Containers** (Port Range: 3000-8999)
```
CONTAINER NAME                STATUS      PORTS                    PURPOSE
agentic-frontend-prod        Running     3000:3000               Production Next.js Frontend
agentic-backend-prod         Running     8000:8000               Production Python Backend
agentic-redis-prod           Running     6379:6379               Production Redis Cache
agentic-n8n-monitoring       Running     5678:5678               Production n8n Workflows
```

### **Development Containers** (Port Range: 3001-8001, 6380, 5679)
```
CONTAINER NAME                STATUS      PORTS                    PURPOSE
agentic-redis-dev            Running     6380:6379               Development Redis Cache
agentic-n8n-dev              Running     5679:5678               Development n8n Instance
agentic-agent-dev            Planned     8001:8001               Development Python Agent
agentic-frontend-dev         Planned     3001:3000               Development Next.js Frontend
```

### **Monitoring Containers** (Port Range: 9000-9999)
```
CONTAINER NAME                STATUS      PORTS                    PURPOSE
agentic-prometheus           Running     9090:9090               Metrics Collection
agentic-grafana              Restarting  3000:3000               Metrics Visualization
agentic-alertmanager         Restarting  9093:9093               Alert Management
agentic-node-exporter        Running     9100:9100               Node Metrics
agentic-redis-exporter       Running     9121:9121               Redis Metrics
agentic-blackbox-exporter    Running     9115:9115               Endpoint Monitoring
agentic-cadvisor             Running     8080:8080               Container Metrics
```

## 📁 **Directory Structure**

### **Production Environment**
```
/opt/agentic-platform/
├── frontend/                 # Production Next.js application
├── backend/                  # Production Python backend
├── infrastructure/           # Docker, nginx, scripts
├── .env                     # Production environment variables
└── docker-compose.yml       # Production container orchestration
```

### **Development Environment**
```
/opt/agentic-platform-dev/
├── frontend/                 # Development Next.js application
├── backend/                  # Development Python backend
├── infrastructure/           # Development Docker configs
├── .env.dev                 # Development environment variables
└── [mixed files]            # Currently has mixed structure (NEEDS FIXING)
```

### **Agent Development**
```
/opt/agent-dev/
├── agent/                   # Python ADK agent code
├── requirements.txt         # Python dependencies
├── Dockerfile              # Agent container build
└── .env                    # Agent environment variables
```

### **Static Development**
```
/var/www/dev-consulting/
└── dev-test.html           # Static development test page
```

### **Nginx Configuration**
```
/etc/nginx/sites-available/
├── agentic-platform-prod           # Production site config
├── agentic-platform-dev-static     # Development static config
└── agentic-platform-dev-full       # Development full stack config

/etc/nginx/sites-enabled/
└── agentic-platform-dev -> ../sites-available/agentic-platform-dev-static
```

### **SSL Certificates**
```
/etc/nginx/ssl/
├── consulting.sa.crt        # Wildcard SSL certificate
└── consulting.sa.key        # SSL private key
```

## 🌐 **Domain Configuration**

### **Production Domains**
- **Main Site**: https://consulting.sa → agentic-frontend-prod (port 3000)
- **API**: https://consulting.sa/api → agentic-backend-prod (port 8000)

### **Development Domains**
- **Dev Site**: https://dev.consulting.sa → Static HTML (currently)
- **Dev API**: https://dev.consulting.sa/api → agentic-agent-dev (port 8001)
- **Dev n8n**: https://dev.consulting.sa/n8n → agentic-n8n-dev (port 5679)

### **Monitoring Domains**
- **Prometheus**: http://217.79.255.54:9090
- **Grafana**: http://217.79.255.54:3000 (when working)

## 🔧 **Services Status**

### **Web Server**
- **Nginx**: ✅ Running
- **SSL**: ✅ Wildcard certificate for *.consulting.sa
- **HTTP → HTTPS**: ✅ Automatic redirect

### **Database Services**
- **Production Redis**: ✅ Running (port 6379)
- **Development Redis**: ✅ Running (port 6380)
- **Supabase**: ✅ External service (cloud)

### **Workflow Automation**
- **Production n8n**: ✅ Running (port 5678)
- **Development n8n**: ✅ Running (port 5679)

### **Monitoring Stack**
- **Prometheus**: ✅ Running
- **Grafana**: ⚠️ Restarting (needs attention)
- **Alertmanager**: ⚠️ Restarting (needs attention)

## 🚨 **Current Issues**

### **High Priority**
1. **Development Directory Structure**: Files are mixed up, needs reorganization
2. **Container Name Conflicts**: agentic-redis-dev already exists
3. **Grafana/Alertmanager**: Containers restarting, need debugging
4. **Frontend Development**: Container not running

### **Medium Priority**
1. **Environment Variables**: Some missing in development
2. **Health Checks**: Backend containers showing unhealthy
3. **Log Management**: Need centralized logging

### **Low Priority**
1. **Resource Monitoring**: Check CPU/RAM usage
2. **Backup Strategy**: Implement automated backups
3. **Security Hardening**: Review access controls

## 📋 **Deployment History**

### **2025-07-29**
- ✅ Updated VPS password across all scripts
- ✅ Deployed static development environment
- ✅ Started Redis and n8n development containers
- ⚠️ Encountered container name conflicts
- 📝 Created this documentation

### **Previous Deployments**
- Production environment deployed and running
- Monitoring stack deployed (partially working)
- SSL certificates configured

## 🔄 **Maintenance Tasks**

### **Daily**
- [ ] Check container health status
- [ ] Monitor disk space usage
- [ ] Review application logs

### **Weekly**
- [ ] Update container images
- [ ] Check SSL certificate expiry
- [ ] Review security logs

### **Monthly**
- [ ] Full system backup
- [ ] Security updates
- [ ] Performance review

## 📞 **Emergency Contacts**

### **Access Information**
- **SSH**: `ssh root@217.79.255.54`
- **Password**: Available in .env files
- **Backup Access**: [Backup method]

### **Service Contacts**
- **Domain Provider**: [Contact info]
- **VPS Provider**: [Contact info]
- **SSL Provider**: [Contact info]

---

**Last Updated**: 2025-07-29  
**Updated By**: Development Team  
**Next Review**: 2025-08-05# Development Environment Cleanup - 2025-07-29 21:44:44

## Actions Performed:
- Stopped all development containers
- Removed all development containers  
- Cleaned up development directories
- Pruned unused Docker images

## Status: Ready for fresh deployment


