# 🔐 Server Access Information

## VPS Access Credentials

**Server**: 217.79.255.54  
**Username**: root  
**Password**: gnqLG7FDd4  

## Connection Commands

```bash
# SSH Connection
ssh root@217.79.255.54

# SSH with password (using sshpass)
sshpass -p 'gnqLG7FDd4' ssh root@217.79.255.54

# SCP file transfer
sshpass -p 'gnqLG7FDd4' scp file.txt root@217.79.255.54:/path/

# Remote command execution
sshpass -p 'gnqLG7FDd4' ssh root@217.79.255.54 'command'
```

## Container Management Commands

```bash
# Check container status
sshpass -p 'gnqLG7FDd4' ssh root@217.79.255.54 'docker ps'

# Check production containers (DO NOT TOUCH)
sshpass -p 'gnqLG7FDd4' ssh root@217.79.255.54 'docker ps | grep prod'

# Check development containers (Safe to manage)
sshpass -p 'gnqLG7FDd4' ssh root@217.79.255.54 'docker ps | grep dev'

# Stop development containers only
sshpass -p 'gnqLG7FDd4' ssh root@217.79.255.54 'docker stop agentic-frontend-dev agentic-backend-dev agentic-redis-dev agentic-n8n-dev'

# Remove development containers
sshpass -p 'gnqLG7FDd4' ssh root@217.79.255.54 'docker rm agentic-frontend-dev agentic-backend-dev agentic-redis-dev agentic-n8n-dev'
```

## Safety Protocols

### NEVER TOUCH PRODUCTION CONTAINERS
- agentic-frontend-prod (Port 3000)
- agentic-backend-prod (Port 8000) 
- agentic-redis-prod (Port 6379)
- agentic-n8n-prod (Port 5678)

### SAFE TO MANAGE DEV CONTAINERS
- agentic-frontend-dev (Port 3001)
- agentic-backend-dev (Port 8001)
- agentic-redis-dev (Port 6380)
- agentic-n8n-dev (Port 5679)

---

**CRITICAL**: This file contains sensitive information. Keep secure and never commit to public repositories.