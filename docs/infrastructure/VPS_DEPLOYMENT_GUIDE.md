# VPS Deployment Guide - Complete Infrastructure Overview

## 🖥️ **VPS Host vs Container Architecture**

### **VPS Host System (217.79.255.54)**
**What's Installed Directly on VPS:**
```
Ubuntu/Linux Host System
├── Docker & Docker Compose (Container Runtime)
├── Nginx (Reverse Proxy & SSL Termination)
├── SSL Certificates (/etc/nginx/ssl/)
├── SSH Server (Remote Access)
├── Basic System Tools (curl, wget, etc.)
└── Static File Serving (/var/www/)
```

**VPS Host Responsibilities:**
- ✅ SSL Certificate Management (Wildcard *.consulting.sa)
- ✅ Reverse Proxy (Nginx routes traffic to containers)
- ✅ Container Orchestration (Docker/Docker Compose)
- ✅ Static File Serving (Development test pages)
- ✅ Network Management (Port forwarding, firewall)
- ✅ System Security (SSH access, user management)

### **Container Architecture**
**What's Inside Containers:**
```
Production Containers:
├── agentic-frontend-prod (Next.js app + Node.js)
├── agentic-backend-prod (Python + FastAPI)
├── agentic-redis-prod (Redis cache)
└── agentic-n8n-monitoring (n8n workflows)

Development Containers:
├── agentic-redis-dev (Redis cache)
├── agentic-n8n-dev (n8n workflows)
├── agentic-agent-dev (Python ADK agent)
└── agentic-frontend-dev (Next.js - planned)

Monitoring Containers:
├── agentic-prometheus (Metrics collection)
├── agentic-grafana (Dashboards)
├── agentic-alertmanager (Alerts)
├── agentic-node-exporter (System metrics)
├── agentic-redis-exporter (Redis metrics)
├── agentic-blackbox-exporter (Endpoint monitoring)
└── agentic-cadvisor (Container metrics)
```

**Container Responsibilities:**
- ✅ Application Runtime (Node.js, Python, Redis, etc.)
- ✅ Application Dependencies (npm packages, pip packages)
- ✅ Application Configuration (Environment variables)
- ✅ Application Data (Temporary files, logs)
- ✅ Service-Specific Logic (API endpoints, workflows, caching)

---

## 🚀 **Easiest Deployment Process (Discovered)**

### **1. One-Command Environment Setup**

**For Development Environment:**
```bash
# Complete development deployment (recommended)
./infrastructure/scripts/deploy-dev-complete.sh

# Or step-by-step (for troubleshooting)
./infrastructure/scripts/cleanup-dev.sh          # Clean slate
./infrastructure/scripts/deploy-dev-static.sh    # Static base
./infrastructure/scripts/deploy-backend-dev.sh   # Redis + n8n
./infrastructure/scripts/deploy-agent-dev.sh     # Python agent
./infrastructure/scripts/deploy-frontend-dev.sh  # Next.js (planned)
```

**For Production Environment:**
```bash
# Production deployment
./infrastructure/scripts/deploy-main-vps.sh
```

### **2. Health Check & Status**
```bash
# Quick status check
./infrastructure/scripts/update-server-docs.sh
cat docs/infrastructure/VPS_SERVER_STATUS.md

# Manual health checks
curl -k https://dev.consulting.sa/health
curl -k https://dev.consulting.sa/backend/health
curl -k https://consulting.sa/health
```

### **3. Container Management**
```bash
# View all containers
docker ps --filter name=agentic

# View specific environment
docker ps --filter name=agentic-*-dev    # Development
docker ps --filter name=agentic-*-prod   # Production

# Container logs
docker logs --tail 20 agentic-agent-dev
docker logs -f agentic-frontend-prod      # Follow logs
```

---

## 🔧 **VPS Host Configuration Details**

### **Nginx Configuration Structure**
```
/etc/nginx/
├── nginx.conf (Main configuration)
├── sites-available/
│   ├── agentic-platform-prod (Production site)
│   ├── agentic-platform-dev-static (Dev static)
│   └── agentic-platform-dev-full (Dev full-stack)
├── sites-enabled/
│   ├── agentic-platform-prod -> ../sites-available/agentic-platform-prod
│   └── agentic-platform-dev -> ../sites-available/agentic-platform-dev-*
└── ssl/
    ├── consulting.sa.crt (Wildcard SSL certificate)
    └── consulting.sa.key (Private key)
```

**Nginx Routing Logic:**
```
https://consulting.sa → agentic-frontend-prod:3000
https://consulting.sa/api → agentic-backend-prod:8000

https://dev.consulting.sa → Static files OR agentic-frontend-dev:3001
https://dev.consulting.sa/backend → agentic-agent-dev:8001
https://dev.consulting.sa/n8n → agentic-n8n-dev:5679
```

### **Port Allocation Strategy**
```
Production Ports (3000-8999):
├── 3000: Frontend (agentic-frontend-prod)
├── 8000: Backend (agentic-backend-prod)
├── 6379: Redis (agentic-redis-prod)
└── 5678: n8n (agentic-n8n-monitoring)

Development Ports (3001, 8001, 6380, 5679):
├── 3001: Frontend (agentic-frontend-dev)
├── 8001: Agent (agentic-agent-dev)
├── 6380: Redis (agentic-redis-dev)
└── 5679: n8n (agentic-n8n-dev)

Monitoring Ports (9000-9999):
├── 9090: Prometheus
├── 3000: Grafana (conflicts with frontend - needs fix)
├── 9093: Alertmanager
├── 9100: Node Exporter
├── 9121: Redis Exporter
├── 9115: Blackbox Exporter
└── 8080: cAdvisor
```

### **Directory Structure on VPS**
```
/opt/
├── agentic-platform/ (Production deployment)
├── agentic-platform-dev/ (Development deployment)
├── agent-dev/ (Python agent development)
└── frontend-dev/ (Frontend development - planned)

/var/www/
├── html/ (Default nginx root)
└── dev-consulting/ (Development static files)
    └── dev-test.html

/etc/nginx/
├── sites-available/ (Nginx configurations)
├── sites-enabled/ (Active configurations)
└── ssl/ (SSL certificates)
```

---

## 🛠️ **Container Management Best Practices**

### **Environment Separation**
```bash
# Production containers (never touch during development)
docker ps --filter name=agentic-*-prod

# Development containers (safe to restart/rebuild)
docker ps --filter name=agentic-*-dev

# Monitoring containers (shared between environments)
docker ps --filter name=agentic- | grep -E "(prometheus|grafana|alert|exporter|cadvisor)"
```

### **Safe Container Operations**
```bash
# Safe development operations
docker stop agentic-agent-dev
docker rm agentic-agent-dev
docker rmi agentic-agent-dev

# NEVER do this to production containers
# docker stop agentic-frontend-prod  # ❌ DON'T DO THIS

# Safe monitoring restart
docker restart agentic-prometheus
```

### **Container Health Monitoring**
```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Check specific container logs
docker logs --tail 50 agentic-agent-dev

# Check container resource usage
docker stats --no-stream
```

---

## 🔐 **Security & Access Control**

### **SSH Access**
```bash
# Standard SSH access
ssh root@217.79.255.54

# Using environment variables (recommended)
ssh $VPS_USER@$VPS_HOST

# SCP file transfer
scp file.txt root@217.79.255.54:/opt/destination/
```

### **SSL Certificate Management**
```bash
# Check certificate validity
openssl x509 -in /etc/nginx/ssl/consulting.sa.crt -text -noout

# Test SSL configuration
curl -I https://consulting.sa
curl -I https://dev.consulting.sa
```

### **Firewall & Network Security**
```bash
# Check open ports
netstat -tulpn | grep LISTEN

# Check nginx status
systemctl status nginx
nginx -t  # Test configuration
```

---

## 📊 **Monitoring & Maintenance**

### **Automated Documentation Updates**
```bash
# Update server documentation automatically
./infrastructure/scripts/update-server-docs.sh

# View current status
cat docs/infrastructure/VPS_SERVER_STATUS.md
```

### **Regular Maintenance Tasks**
```bash
# Daily checks
docker ps --filter name=agentic  # Container status
df -h                            # Disk usage
free -h                          # Memory usage

# Weekly maintenance
docker system prune -f           # Clean unused images
docker volume prune -f           # Clean unused volumes
systemctl reload nginx           # Reload nginx config
```

### **Backup Procedures**
```bash
# Configuration backup
tar -czf nginx-config-backup.tar.gz /etc/nginx/
tar -czf ssl-backup.tar.gz /etc/nginx/ssl/

# Container data backup
docker exec agentic-redis-prod redis-cli BGSAVE
docker exec agentic-redis-dev redis-cli BGSAVE
```

---

## 🚨 **Troubleshooting Quick Reference**

### **Common Issues & Solutions**

**Container won't start:**
```bash
docker logs container_name
docker inspect container_name
# Check port conflicts: netstat -tulpn | grep :8001
```

**Nginx issues:**
```bash
nginx -t                    # Test configuration
systemctl reload nginx      # Reload configuration
tail -f /var/log/nginx/error.log  # Check error logs
```

**SSL certificate issues:**
```bash
openssl x509 -in /etc/nginx/ssl/consulting.sa.crt -text -noout
curl -I https://dev.consulting.sa  # Test SSL
```

**Environment variable issues:**
```bash
docker exec container_name env | grep API_KEY
docker exec container_name cat /opt/path/.env
```

### **Emergency Procedures**

**Reset development environment:**
```bash
./infrastructure/scripts/cleanup-dev.sh
./infrastructure/scripts/deploy-dev-static.sh
./infrastructure/scripts/deploy-backend-dev.sh
./infrastructure/scripts/deploy-agent-dev.sh
```

**Restart all services:**
```bash
systemctl restart nginx
docker restart $(docker ps -q --filter name=agentic-*-dev)
```

---

## 🎯 **Deployment Workflow Summary**

### **The Easiest Process We Discovered:**

1. **Preparation:**
   ```bash
   # Ensure environment variables are set
   source .env
   # Clean any conflicts
   ./infrastructure/scripts/cleanup-dev.sh
   ```

2. **Deployment:**
   ```bash
   # Deploy in order (each script waits for previous to complete)
   ./infrastructure/scripts/deploy-dev-static.sh    # Base infrastructure
   ./infrastructure/scripts/deploy-backend-dev.sh   # Redis + n8n
   ./infrastructure/scripts/deploy-agent-dev.sh     # Python agent
   # ./infrastructure/scripts/deploy-frontend-dev.sh # Next.js (next step)
   ```

3. **Verification:**
   ```bash
   # Automated status check
   ./infrastructure/scripts/update-server-docs.sh
   # Manual verification
   curl -k https://dev.consulting.sa/health
   curl -k https://dev.consulting.sa/backend/health
   ```

4. **Documentation:**
   ```bash
   # Documentation is automatically updated after each deployment
   cat docs/infrastructure/VPS_SERVER_STATUS.md
   ```

### **Key Success Factors:**
- ✅ **Separation of Concerns:** VPS handles networking/SSL, containers handle applications
- ✅ **Environment Isolation:** Different ports and names for dev/prod
- ✅ **Automated Cleanup:** Always clean before deploying
- ✅ **Health Checks:** Every service has health endpoints
- ✅ **Documentation:** Automatically updated after deployments
- ✅ **Incremental Deployment:** Deploy services one by one, not all at once

---

**Document Version:** 1.0  
**Last Updated:** 2025-07-29  
**Status:** ✅ Production & Development Environments Working  
**Next:** Complete frontend deployment and functionality testing