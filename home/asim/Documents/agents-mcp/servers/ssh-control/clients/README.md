# 🖥️ VPS Client Management System

## 📋 Overview

This directory contains detailed documentation and configuration for each VPS client managed through the MCP SSH Control Server. Each client has its own subdirectory with comprehensive documentation of deployments, configurations, and operational procedures.

## 🏗️ Client Structure

Each client directory contains:
- **README.md**: Complete client documentation
- **deployment-history.md**: Chronological deployment log
- **configurations/**: Environment files and configs
- **scripts/**: Custom management scripts
- **monitoring/**: Health checks and monitoring setup
- **backups/**: Backup configurations and schedules

## 📁 Current Clients

### 🚀 main-vps (217.79.255.54)
- **Status**: Production Ready ✅
- **Primary Domain**: consulting.sa
- **Applications**: Agentic Site (AI SaaS Platform)
- **Last Updated**: 2025-07-21
- **Documentation**: [main-vps/README.md](./main-vps/README.md)

### 🔮 Future Clients
- **agent-vps**: For agent.consulting.sa (Planned)
- **Additional VPS instances** as needed

## 🌐 Domain Management

### Cloudflare Configuration
- **Primary Domain**: consulting.sa
- **Subdomain**: agent.consulting.sa (Planned)
- **DNS Management**: Cloudflare
- **SSL**: Cloudflare + Let's Encrypt

### Domain Mapping
```
consulting.sa → main-vps (217.79.255.54)
agent.consulting.sa → future agent-vps
```

## 🔧 Management Tools

### MCP SSH Server Integration
- **Connection Management**: Secure SSH connections
- **Deployment Automation**: Docker Compose deployments
- **Monitoring**: Real-time health checks
- **Security**: UFW + Fail2ban management
- **Backup**: Automated backup systems

### Standard Operating Procedures
1. **Initial Setup**: Security hardening, Docker installation
2. **Application Deployment**: Docker Compose with health checks
3. **Domain Configuration**: Cloudflare DNS + SSL setup
4. **Monitoring Setup**: Health checks and alerting
5. **Backup Configuration**: Automated backup schedules

## 📊 Lessons Learned

### Key Success Factors
- **Conservative Security Approach**: Maintain SSH access throughout
- **Docker Compose**: Reliable multi-service orchestration
- **Health Checks**: Essential for production monitoring
- **Documentation**: Comprehensive logging of all changes
- **Testing**: Automated test suites for verification

### Common Pitfalls to Avoid
- **Never change SSH port without proper testing**
- **Always maintain root access as backup**
- **Test firewall changes before enabling**
- **Document every configuration change**
- **Use staging environments for testing**

## 🚀 Quick Start for New Clients

1. **Create client directory**: `mkdir clients/new-client`
2. **Copy template**: Use main-vps as template
3. **Update documentation**: Customize for new client
4. **Configure MCP connection**: Add to server config
5. **Deploy and document**: Follow standard procedures

## 📞 Support & Maintenance

### Regular Tasks
- **Weekly**: Health check reviews
- **Monthly**: Security updates and patches
- **Quarterly**: Full system backups and disaster recovery tests
- **Annually**: Security audit and configuration review

### Emergency Procedures
- **SSH Access Lost**: Console access via hosting provider
- **Service Down**: Automated restart procedures
- **Security Breach**: Incident response protocols
- **Data Loss**: Backup restoration procedures

---

*Managed by Kiro AI Assistant - MCP SSH Control Server*  
*Last Updated: 2025-07-21*