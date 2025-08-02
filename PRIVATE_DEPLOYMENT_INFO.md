# 🔐 Private Deployment Information

**⚠️ CONFIDENTIAL - Private Repository Only**

This file contains sensitive deployment information including passwords, API keys, and server details. Keep this secure and only in private repositories.

## 🖥️ VPS Server Information

### Development Server
- **IP Address**: 217.79.255.54
- **Username**: root
- **Password**: gt5qXy22aJ
- **Domain**: dev.consulting.sa
- **Environment**: development
- **SSH Alias**: agentic-217-79-255-54
- **Deploy Path**: /opt/docker-apps/development/agentic-site

### Server Specifications
- **OS**: Debian 12 (Bookworm)
- **RAM**: 23GB
- **Storage**: 394GB
- **CPU**: Multi-core x86_64
- **Network**: 1Gbps connection

## 🔑 SSH Key Information

### SSH Key Locations
- **Private Key**: ~/.ssh/agentic-217-79-255-54
- **Public Key**: ~/.ssh/agentic-217-79-255-54.pub
- **SSH Config Entry**: agentic-217-79-255-54

### SSH Connection Commands
```bash
# Direct connection
ssh agentic-217-79-255-54

# Or using full details
ssh -i ~/.ssh/agentic-217-79-255-54 root@217.79.255.54
```

## 🌐 Service URLs and Ports

### Development Environment
- **Main Website**: https://dev.consulting.sa/
- **API Health Check**: https://dev.consulting.sa/health
- **Backend Admin**: https://dev.consulting.sa/backend/
- **n8n Workflow**: https://dev.consulting.sa/n8n/

### Direct Port Access (for debugging)
- **Frontend**: http://217.79.255.54:3001/
- **Backend**: http://217.79.255.54:8001/
- **n8n**: http://217.79.255.54:5679/
- **Redis**: 217.79.255.54:6380

### Production Environment (when set up)
- **Main Website**: https://consulting.sa/
- **API Health Check**: https://consulting.sa/health
- **Backend Admin**: https://consulting.sa/backend/
- **n8n Workflow**: https://consulting.sa/n8n/

## 🔐 API Keys and Credentials

### Database (Supabase)
```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
```

### AI Services
```env
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### Payment Integration (Stripe)
```env
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
```

### Communication Services (Livekit)
```env
LIVEKIT_URL=your_livekit_server_url
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
```

### Workflow Automation (n8n)
```env
N8N_USER=admin
N8N_PASSWORD=admin123
N8N_URL=http://localhost:5679
N8N_BASE_URL=http://localhost:5679
N8N_API_KEY=your_n8n_api_key
```

### GitHub Integration
```env
GITHUB_TOKEN=your_github_personal_access_token
```

## 🛠️ Management Commands

### VPS Management
```bash
# Check overall status
ssh agentic-217-79-255-54 '/usr/local/bin/agentic-development-status.sh'

# View application logs
ssh agentic-217-79-255-54 '/usr/local/bin/agentic-development-logs.sh'

# Restart all services
ssh agentic-217-79-255-54 '/usr/local/bin/agentic-development-restart.sh'
```

### Docker Management
```bash
# Check container status
ssh agentic-217-79-255-54 'cd /opt/docker-apps/development/agentic-site && docker-compose ps'

# View specific container logs
ssh agentic-217-79-255-54 'cd /opt/docker-apps/development/agentic-site && docker-compose logs -f frontend'
ssh agentic-217-79-255-54 'cd /opt/docker-apps/development/agentic-site && docker-compose logs -f backend'

# Restart specific service
ssh agentic-217-79-255-54 'cd /opt/docker-apps/development/agentic-site && docker-compose restart frontend'
```

### System Monitoring
```bash
# Check system resources
ssh agentic-217-79-255-54 'htop'

# Check disk usage
ssh agentic-217-79-255-54 'df -h'

# Check memory usage
ssh agentic-217-79-255-54 'free -h'

# Check network connections
ssh agentic-217-79-255-54 'netstat -tlnp'
```

## 📁 Important File Locations

### On VPS
- **Application**: /opt/docker-apps/development/agentic-site/
- **Nginx Config**: /etc/nginx/sites-available/agentic-development
- **SSL Certificates**: /opt/docker-apps/shared/ssl/
- **Backups**: /opt/docker-apps/shared/backups/
- **Logs**: /var/log/agentic-site/

### Local Development
- **SSH Keys**: ~/.ssh/agentic-217-79-255-54*
- **SSH Config**: ~/.ssh/config
- **Environment Files**: .env.development, .env.production
- **Build Directory**: .build-development/

## 🔄 Deployment Process

### Initial Setup (One-time)
```bash
./infrastructure/scripts/setup-new-vps.sh 217.79.255.54 root gt5qXy22aJ development
```

### Regular Deployment
```bash
./infrastructure/scripts/deploy-to-vps.sh agentic-217-79-255-54 development
```

### Testing Deployment
```bash
./infrastructure/scripts/test-dev-deployment.sh
```

## 🚨 Emergency Procedures

### If SSH Access is Lost
1. Use VPS provider's console access
2. Reset SSH configuration:
   ```bash
   systemctl restart ssh
   ufw allow 22/tcp
   ```

### If Containers Won't Start
1. Check Docker daemon: `systemctl status docker`
2. Check disk space: `df -h`
3. Check logs: `docker-compose logs`
4. Restart Docker: `systemctl restart docker`

### If Website is Down
1. Check Nginx: `systemctl status nginx`
2. Check containers: `docker-compose ps`
3. Check ports: `netstat -tlnp | grep -E ':(3001|8001)'`
4. Restart services: `/usr/local/bin/agentic-development-restart.sh`

## 📊 Monitoring and Health Checks

### Health Check URLs
- **Frontend**: http://217.79.255.54:3001/
- **Backend**: http://217.79.255.54:8001/health
- **API**: http://217.79.255.54:8001/api/health
- **n8n**: http://217.79.255.54:5679/

### Expected Container Status
```
NAME                    STATUS
agentic-frontend-dev    Up (healthy)
agentic-backend-dev     Up (healthy)  
agentic-redis-dev       Up (healthy)
agentic-n8n-dev         Up
```

## 🔧 Troubleshooting Common Issues

### Frontend Not Loading
1. Check container: `docker logs agentic-frontend-dev`
2. Check port: `curl http://localhost:3001/`
3. Check Nginx: `nginx -t && systemctl reload nginx`

### Backend API Errors
1. Check container: `docker logs agentic-backend-dev`
2. Check port: `curl http://localhost:8001/health`
3. Check environment variables in docker-compose.yml

### Database Connection Issues
1. Verify Supabase credentials in .env file
2. Check network connectivity from container
3. Test connection manually

## 📝 Notes and Updates

### Last Updated
- **Date**: February 8, 2025
- **Updated By**: Development Team
- **Changes**: Initial VPS setup and deployment scripts created

### Known Issues
- None currently

### Planned Improvements
- SSL certificate automation
- Automated backups
- Enhanced monitoring
- CI/CD pipeline integration

---

**🔒 SECURITY REMINDER**: This file contains sensitive information. Keep it secure and only in private repositories. Never commit this to public repositories or share with unauthorized personnel.