#!/bin/bash
set -e

# Python ADK Agent Development Deployment Script
# This script deploys the Python ADK agent for development

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

echo -e "${BLUE}🚀 Deploying Python ADK Agent to VPS: $VPS_HOST${NC}"

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

# Step 1: Clean up and create agent directory
echo -e "${BLUE}Step 1: Setting up clean agent directory...${NC}"
run_on_vps "rm -rf /opt/agent-dev"
run_on_vps "mkdir -p /opt/agent-dev"

# Step 2: Copy essential files individually to avoid structure issues
echo -e "${BLUE}Step 2: Copying agent files individually...${NC}"

# Copy main Python files
copy_to_vps "backend/agent/requirements.txt" "/opt/agent-dev/"
copy_to_vps "backend/agent/api_server.py" "/opt/agent-dev/"
copy_to_vps "backend/agent/main.py" "/opt/agent-dev/"
copy_to_vps "backend/agent/__init__.py" "/opt/agent-dev/"

# Copy the agent code directory
copy_to_vps "backend/agent/my_adk_agent" "/opt/agent-dev/"

# Copy environment file
copy_to_vps ".env.dev" "/opt/agent-dev/.env"

# Step 3: Stop existing agent container
echo -e "${BLUE}Step 3: Stopping existing agent container...${NC}"
run_on_vps "docker stop agentic-agent-dev 2>/dev/null || true"
run_on_vps "docker rm agentic-agent-dev 2>/dev/null || true"

# Step 4: Create a simple Dockerfile
echo -e "${BLUE}Step 4: Creating agent Dockerfile...${NC}"
run_on_vps "cat > /opt/agent-dev/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \\
    CMD curl -f http://localhost:8001/health || exit 1

# Start the application
CMD [\"python\", \"-m\", \"uvicorn\", \"api_server:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8001\"]
EOF"

# Step 5: Build agent container
echo -e "${BLUE}Step 5: Building agent container...${NC}"
run_on_vps "cd /opt/agent-dev && docker build -t agentic-agent-dev ."

# Step 6: Start agent container
echo -e "${BLUE}Step 6: Starting agent container...${NC}"
run_on_vps "docker run -d --name agentic-agent-dev --restart unless-stopped -p 8001:8001 --env-file /opt/agent-dev/.env agentic-agent-dev"

# Step 7: Wait for agent to start
echo -e "${BLUE}Step 7: Waiting for agent to start...${NC}"
sleep 30

# Step 8: Test agent
echo -e "${BLUE}Step 8: Testing agent...${NC}"
if run_on_vps "curl -f http://localhost:8001/health"; then
    echo -e "${GREEN}✓ Agent is running and healthy${NC}"
else
    echo -e "${YELLOW}⚠ Agent may still be starting up${NC}"
    echo -e "${YELLOW}Checking agent logs...${NC}"
    run_on_vps "docker logs --tail 20 agentic-agent-dev" || echo "Could not get agent logs"
fi

# Step 9: Update server documentation
echo -e "${BLUE}Step 9: Updating server documentation...${NC}"
./infrastructure/scripts/update-server-docs.sh

# Step 10: Display status
echo -e "${GREEN}🎉 Python ADK Agent deployed!${NC}"
echo ""
echo -e "${BLUE}Development Agent Status:${NC}"
echo "- 🐍 Agent API: http://localhost:8001"
echo "- 🏥 Health Check: http://localhost:8001/health"
echo "- 🌐 External Access: https://dev.consulting.sa/backend/"
echo ""
echo -e "${BLUE}Container Status:${NC}"
run_on_vps "docker ps --filter name=agentic-agent-dev"
echo ""
echo -e "${BLUE}All Development Services:${NC}"
run_on_vps "docker ps --filter name=agentic-*-dev"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. ✅ Agent is now running on port 8001"
echo "2. 🌐 Deploy Next.js frontend: ./infrastructure/scripts/deploy-frontend-dev.sh"
echo "3. 🧪 Test full development environment"
echo "4. 📊 Compare with production: https://consulting.sa"

echo -e "${GREEN}✅ Python ADK Agent deployed successfully!${NC}"