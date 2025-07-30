#!/bin/bash
set -e

# Backend Development Deployment Script
# This script deploys only the backend services for development

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Configuration
VPS_HOST=${VPS_HOST:-"217.79.255.54"}
VPS_USER=${VPS_USER:-"root"}
VPS_PASSWORD=${VPS_PASSWORD:-"xxXNCpx9Cz"}

echo -e "${BLUE}🚀 Deploying Backend Development Services to VPS: $VPS_HOST${NC}"

# Function to run commands on VPS using sshpass
run_on_vps() {
    local command="$1"
    echo -e "${YELLOW}Running on VPS: $command${NC}"
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "$command"
}

# Function to copy files to VPS
copy_to_vps() {
    local local_path="$1"
    local remote_path="$2"
    echo -e "${YELLOW}Copying $local_path to VPS:$remote_path${NC}"
    sshpass -p "$VPS_PASSWORD" scp -o StrictHostKeyChecking=no -r "$local_path" "$VPS_USER@$VPS_HOST:$remote_path"
}

# Test VPS connection
echo -e "${BLUE}Testing VPS connection...${NC}"
if run_on_vps "echo 'Connection successful'"; then
    echo -e "${GREEN}✓ VPS connection established${NC}"
else
    echo -e "${RED}❌ Failed to connect to VPS${NC}"
    exit 1
fi

# Step 1: Stop existing development containers
echo -e "${BLUE}Step 1: Stopping existing development containers...${NC}"
run_on_vps "docker stop agentic-backend-dev agentic-redis-dev agentic-n8n-dev 2>/dev/null || true"
run_on_vps "docker rm agentic-backend-dev agentic-redis-dev agentic-n8n-dev 2>/dev/null || true"

# Step 2: Start Redis (simple and reliable)
echo -e "${BLUE}Step 2: Starting Redis development container...${NC}"
run_on_vps "docker run -d --name agentic-redis-dev --restart unless-stopped -p 6380:6379 redis:7-alpine"

# Step 3: Start n8n (simple configuration)
echo -e "${BLUE}Step 3: Starting n8n development container...${NC}"
run_on_vps "docker run -d --name agentic-n8n-dev --restart unless-stopped -p 5679:5678 -e N8N_BASIC_AUTH_ACTIVE=true -e N8N_BASIC_AUTH_USER=admin -e N8N_BASIC_AUTH_PASSWORD=devpassword n8nio/n8n:latest"

# Step 4: Wait for services to start
echo -e "${BLUE}Step 4: Waiting for services to start...${NC}"
sleep 15

# Step 5: Test services
echo -e "${BLUE}Step 5: Testing backend services...${NC}"

# Test Redis
if run_on_vps "docker exec agentic-redis-dev redis-cli ping"; then
    echo -e "${GREEN}✓ Redis is running${NC}"
else
    echo -e "${RED}❌ Redis failed to start${NC}"
fi

# Test n8n
if run_on_vps "curl -f http://localhost:5679/"; then
    echo -e "${GREEN}✓ n8n is running${NC}"
else
    echo -e "${YELLOW}⚠ n8n may still be starting up${NC}"
fi

# Step 6: Display status
echo -e "${GREEN}🎉 Backend development services deployed!${NC}"
echo ""
echo -e "${BLUE}Development Backend Services:${NC}"
echo "- 🔴 Redis: localhost:6380"
echo "- 🔄 n8n: http://localhost:5679 (admin/devpassword)"
echo ""
echo -e "${BLUE}Container Status:${NC}"
run_on_vps "docker ps --filter name=agentic-*-dev"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Backend services are now running"
echo "2. Deploy Python ADK agent: ./infrastructure/scripts/deploy-agent-dev.sh"
echo "3. Deploy Next.js frontend: ./infrastructure/scripts/deploy-frontend-dev.sh"
echo "4. Test full development environment"

echo -e "${GREEN}✅ Backend development services deployed successfully!${NC}"