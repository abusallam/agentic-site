#!/bin/bash
set -e

# Development Environment Health Check Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VPS_HOST=${VPS_HOST:-"217.79.255.54"}
VPS_USER=${VPS_USER:-"root"}
VPS_PASSWORD=${VPS_PASSWORD:-"xxXNCpx9Cz"}

echo -e "${BLUE}🔍 Checking Development Environment Status${NC}"

# Function to run commands on VPS using sshpass
run_on_vps() {
    local command="$1"
    echo -e "${YELLOW}Running on VPS: $command${NC}"
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "$command"
}

# Check VPS connection
echo -e "${BLUE}Testing VPS connection...${NC}"
if run_on_vps "echo 'Connection successful'"; then
    echo -e "${GREEN}✓ VPS connection established${NC}"
else
    echo -e "${RED}❌ Failed to connect to VPS${NC}"
    exit 1
fi

# Check directory structure
echo -e "${BLUE}Checking directory structure...${NC}"
run_on_vps "ls -la /opt/agentic-platform-dev/"

# Check for Docker compose file
echo -e "${BLUE}Looking for Docker compose files...${NC}"
run_on_vps "find /opt/agentic-platform-dev -name '*docker-compose*' -type f"

# Check running containers
echo -e "${BLUE}Checking running containers...${NC}"
run_on_vps "docker ps --filter name=agentic"

# Check development site
echo -e "${BLUE}Testing development site...${NC}"
if run_on_vps "curl -f https://dev.consulting.sa/health"; then
    echo -e "${GREEN}✓ Development site is accessible${NC}"
else
    echo -e "${YELLOW}⚠ Development site health check failed${NC}"
fi

# Check individual services
echo -e "${BLUE}Checking individual services...${NC}"

# Frontend
if run_on_vps "curl -f http://localhost:3001/"; then
    echo -e "${GREEN}✓ Frontend service is running${NC}"
else
    echo -e "${YELLOW}⚠ Frontend service is not responding${NC}"
fi

# Backend
if run_on_vps "curl -f http://localhost:8001/health"; then
    echo -e "${GREEN}✓ Backend service is running${NC}"
else
    echo -e "${YELLOW}⚠ Backend service is not responding${NC}"
fi

# n8n
if run_on_vps "curl -f http://localhost:5679/"; then
    echo -e "${GREEN}✓ n8n service is running${NC}"
else
    echo -e "${YELLOW}⚠ n8n service is not responding${NC}"
fi

echo -e "${BLUE}✅ Health check completed${NC}"