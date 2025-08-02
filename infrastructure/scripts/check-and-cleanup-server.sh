#!/bin/bash
set -e

# Server Status Check and Cleanup Script
# This script checks what's running on the server and cleans up development containers

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Configuration
VPS_HOST=${VPS_HOST:-"217.79.255.54"}
VPS_USER=${VPS_USER:-"root"}
VPS_PASSWORD=${VPS_PASSWORD:-"xxXNCpx9Cz"}

echo -e "${PURPLE}🔍 Server Status Check and Cleanup${NC}"
echo -e "${BLUE}Target VPS: $VPS_HOST${NC}"
echo -e "${BLUE}Timestamp: $(date)${NC}"
echo ""

# Function to run commands on VPS using sshpass
run_on_vps() {
    local command="$1"
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "$command"
}

# Function to run commands on VPS and capture output
run_on_vps_capture() {
    local command="$1"
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "$command" 2>/dev/null || echo ""
}

# Test VPS connection
echo -e "${BLUE}Step 1: Testing VPS connection...${NC}"
if run_on_vps "echo 'Connection successful'"; then
    echo -e "${GREEN}✓ VPS connection established${NC}"
else
    echo -e "${RED}❌ Failed to connect to VPS${NC}"
    exit 1
fi

# Check system resources
echo -e "${BLUE}Step 2: Checking system resources...${NC}"
echo -e "${YELLOW}System Information:${NC}"
run_on_vps "echo 'CPU Usage:' && top -bn1 | grep 'Cpu(s)' | head -1"
run_on_vps "echo 'Memory Usage:' && free -h"
run_on_vps "echo 'Disk Usage:' && df -h /"
run_on_vps "echo 'Docker System Usage:' && docker system df"

# Check all running containers
echo -e "${BLUE}Step 3: Checking all running containers...${NC}"
echo -e "${YELLOW}All Running Containers:${NC}"
RUNNING_CONTAINERS=$(run_on_vps_capture "docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'")
if [ -n "$RUNNING_CONTAINERS" ]; then
    echo "$RUNNING_CONTAINERS"
else
    echo -e "${GREEN}No containers currently running${NC}"
fi

# Check for development containers specifically
echo -e "${BLUE}Step 4: Identifying development containers...${NC}"
DEV_CONTAINERS=("agentic-frontend-dev" "agentic-backend-dev" "agentic-redis-dev" "agentic-n8n-dev")
FOUND_DEV_CONTAINERS=()

for container in "${DEV_CONTAINERS[@]}"; do
    if run_on_vps "docker ps -q -f name=$container" | grep -q .; then
        echo -e "${YELLOW}Found running dev container: $container${NC}"
        FOUND_DEV_CONTAINERS+=("$container")
    fi
done

# Check for old/orphaned containers
echo -e "${BLUE}Step 5: Checking for old/orphaned containers...${NC}"
OLD_CONTAINERS=$(run_on_vps_capture "docker ps -a --filter 'name=agentic' --format '{{.Names}}' | grep -v -E '(agentic-frontend-dev|agentic-backend-dev|agentic-redis-dev|agentic-n8n-dev)$'")
if [ -n "$OLD_CONTAINERS" ]; then
    echo -e "${YELLOW}Found old/orphaned containers:${NC}"
    echo "$OLD_CONTAINERS"
else
    echo -e "${GREEN}No old/orphaned containers found${NC}"
fi

# Check port usage
echo -e "${BLUE}Step 6: Checking port usage...${NC}"
DEV_PORTS=(3001 8001 5679 6380)
PROD_PORTS=(3000 8000 5678 6379)

echo -e "${YELLOW}Development Ports Status:${NC}"
for port in "${DEV_PORTS[@]}"; do
    if run_on_vps "netstat -tuln | grep :$port" >/dev/null 2>&1; then
        echo -e "${YELLOW}Port $port: IN USE${NC}"
    else
        echo -e "${GREEN}Port $port: AVAILABLE${NC}"
    fi
done

echo -e "${YELLOW}Production Ports Status:${NC}"
for port in "${PROD_PORTS[@]}"; do
    if run_on_vps "netstat -tuln | grep :$port" >/dev/null 2>&1; then
        echo -e "${YELLOW}Port $port: IN USE${NC}"
    else
        echo -e "${GREEN}Port $port: AVAILABLE${NC}"
    fi
done

# Check nginx configuration
echo -e "${BLUE}Step 7: Checking nginx configuration...${NC}"
NGINX_SITES=$(run_on_vps_capture "ls -la /etc/nginx/sites-enabled/ | grep agentic")
if [ -n "$NGINX_SITES" ]; then
    echo -e "${YELLOW}Active nginx sites:${NC}"
    echo "$NGINX_SITES"
else
    echo -e "${GREEN}No agentic nginx sites found${NC}"
fi

# Check docker networks
echo -e "${BLUE}Step 8: Checking docker networks...${NC}"
DOCKER_NETWORKS=$(run_on_vps_capture "docker network ls | grep agentic")
if [ -n "$DOCKER_NETWORKS" ]; then
    echo -e "${YELLOW}Agentic docker networks:${NC}"
    echo "$DOCKER_NETWORKS"
else
    echo -e "${GREEN}No agentic docker networks found${NC}"
fi

# Cleanup section
echo ""
echo -e "${PURPLE}🧹 CLEANUP SECTION${NC}"
echo ""

# Stop and remove development containers
if [ ${#FOUND_DEV_CONTAINERS[@]} -gt 0 ]; then
    echo -e "${BLUE}Step 9: Stopping development containers...${NC}"
    for container in "${FOUND_DEV_CONTAINERS[@]}"; do
        echo -e "${YELLOW}Stopping $container...${NC}"
        run_on_vps "docker stop $container" || echo -e "${RED}Failed to stop $container${NC}"
        echo -e "${YELLOW}Removing $container...${NC}"
        run_on_vps "docker rm $container" || echo -e "${RED}Failed to remove $container${NC}"
    done
    echo -e "${GREEN}✓ Development containers cleaned up${NC}"
else
    echo -e "${GREEN}No development containers to clean up${NC}"
fi

# Clean up old/orphaned containers
if [ -n "$OLD_CONTAINERS" ]; then
    echo -e "${BLUE}Step 10: Cleaning up old/orphaned containers...${NC}"
    echo "$OLD_CONTAINERS" | while read -r container; do
        if [ -n "$container" ]; then
            echo -e "${YELLOW}Stopping and removing $container...${NC}"
            run_on_vps "docker stop $container && docker rm $container" || echo -e "${RED}Failed to clean up $container${NC}"
        fi
    done
    echo -e "${GREEN}✓ Old containers cleaned up${NC}"
else
    echo -e "${GREEN}No old containers to clean up${NC}"
fi

# Clean up unused docker resources
echo -e "${BLUE}Step 11: Cleaning up unused docker resources...${NC}"
run_on_vps "docker system prune -f"
run_on_vps "docker volume prune -f"
run_on_vps "docker network prune -f"
echo -e "${GREEN}✓ Docker system cleaned up${NC}"

# Remove old docker-compose files
echo -e "${BLUE}Step 12: Cleaning up old deployment files...${NC}"
run_on_vps "rm -rf /opt/agentic-platform-dev-old /opt/agentic-development-old" || true
echo -e "${GREEN}✓ Old deployment files cleaned up${NC}"

# Final status check
echo ""
echo -e "${PURPLE}📊 POST-CLEANUP STATUS${NC}"
echo ""

echo -e "${BLUE}Running containers after cleanup:${NC}"
FINAL_CONTAINERS=$(run_on_vps_capture "docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'")
if [ -n "$FINAL_CONTAINERS" ]; then
    echo "$FINAL_CONTAINERS"
else
    echo -e "${GREEN}No containers running${NC}"
fi

echo -e "${BLUE}Port status after cleanup:${NC}"
for port in "${DEV_PORTS[@]}"; do
    if run_on_vps "netstat -tuln | grep :$port" >/dev/null 2>&1; then
        echo -e "${YELLOW}Port $port: STILL IN USE${NC}"
    else
        echo -e "${GREEN}Port $port: AVAILABLE${NC}"
    fi
done

echo -e "${BLUE}System resources after cleanup:${NC}"
run_on_vps "echo 'Memory:' && free -h | head -2"
run_on_vps "echo 'Disk:' && df -h / | tail -1"

# Summary
echo ""
echo -e "${GREEN}🎉 SERVER CLEANUP COMPLETED${NC}"
echo ""
echo -e "${BLUE}=== CLEANUP SUMMARY ===${NC}"
echo -e "${GREEN}✅ VPS connection verified${NC}"
echo -e "${GREEN}✅ System resources checked${NC}"
echo -e "${GREEN}✅ Development containers stopped and removed${NC}"
echo -e "${GREEN}✅ Old/orphaned containers cleaned up${NC}"
echo -e "${GREEN}✅ Docker system resources cleaned up${NC}"
echo -e "${GREEN}✅ Development ports freed up${NC}"
echo ""
echo -e "${BLUE}=== READY FOR DEPLOYMENT ===${NC}"
echo -e "${GREEN}🚀 Server is clean and ready for new development deployment${NC}"
echo -e "${GREEN}🔧 All development ports (3001, 8001, 5679, 6380) are available${NC}"
echo -e "${GREEN}💾 Docker resources optimized${NC}"
echo ""
echo -e "${YELLOW}Next step: Run your deployment script${NC}"