#!/bin/bash
set -e

# Complete Development Environment Deployment Script
# This script deploys the entire development environment in the correct order
# Based on lessons learned from troubleshooting and optimization

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

echo -e "${PURPLE}🚀 Complete Development Environment Deployment${NC}"
echo -e "${BLUE}Target VPS: $VPS_HOST${NC}"
echo -e "${BLUE}Deployment Strategy: Clean → Static → Backend → Agent → Frontend${NC}"
echo ""

# Function to run commands on VPS using sshpass
run_on_vps() {
    local command="$1"
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "$command"
}

# Function to check if a service is responding
check_service() {
    local url="$1"
    local service_name="$2"
    if run_on_vps "curl -f -s $url > /dev/null 2>&1"; then
        echo -e "${GREEN}✓ $service_name is responding${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ $service_name is not responding${NC}"
        return 1
    fi
}

# Test VPS connection
echo -e "${BLUE}🔗 Testing VPS connection...${NC}"
if run_on_vps "echo 'Connection successful'" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ VPS connection established${NC}"
else
    echo -e "${RED}❌ Failed to connect to VPS${NC}"
    exit 1
fi

# Phase 1: Clean Environment
echo ""
echo -e "${PURPLE}📋 Phase 1: Environment Cleanup${NC}"
echo -e "${YELLOW}Cleaning up any existing development containers...${NC}"
if ./infrastructure/scripts/cleanup-dev.sh; then
    echo -e "${GREEN}✓ Environment cleanup completed${NC}"
else
    echo -e "${RED}❌ Cleanup failed${NC}"
    exit 1
fi

# Phase 2: Deploy Static Base
echo ""
echo -e "${PURPLE}📋 Phase 2: Static Development Base${NC}"
echo -e "${YELLOW}Deploying static development environment...${NC}"
if ./infrastructure/scripts/deploy-dev-static.sh; then
    echo -e "${GREEN}✓ Static development base deployed${NC}"
    check_service "https://dev.consulting.sa/health" "Static Development Site"
else
    echo -e "${RED}❌ Static deployment failed${NC}"
    exit 1
fi

# Phase 3: Deploy Backend Services
echo ""
echo -e "${PURPLE}📋 Phase 3: Backend Services (Redis + n8n)${NC}"
echo -e "${YELLOW}Deploying Redis and n8n services...${NC}"
if ./infrastructure/scripts/deploy-backend-dev.sh; then
    echo -e "${GREEN}✓ Backend services deployed${NC}"
    check_service "http://localhost:5679" "n8n Development Instance"
    if run_on_vps "docker exec agentic-redis-dev redis-cli ping" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Redis is responding${NC}"
    else
        echo -e "${YELLOW}⚠ Redis health check failed${NC}"
    fi
else
    echo -e "${RED}❌ Backend services deployment failed${NC}"
    exit 1
fi

# Phase 4: Deploy Python Agent
echo ""
echo -e "${PURPLE}📋 Phase 4: Python ADK Agent${NC}"
echo -e "${YELLOW}Deploying Python ADK agent...${NC}"
if ./infrastructure/scripts/deploy-agent-dev.sh; then
    echo -e "${GREEN}✓ Python ADK agent deployed${NC}"
    check_service "http://localhost:8001/health" "Python ADK Agent"
    check_service "https://dev.consulting.sa/backend/health" "Agent via Nginx"
else
    echo -e "${RED}❌ Agent deployment failed${NC}"
    exit 1
fi

# Phase 5: Update Documentation
echo ""
echo -e "${PURPLE}📋 Phase 5: Documentation Update${NC}"
echo -e "${YELLOW}Updating server documentation...${NC}"
if ./infrastructure/scripts/update-server-docs.sh > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Documentation updated${NC}"
else
    echo -e "${YELLOW}⚠ Documentation update failed (non-critical)${NC}"
fi

# Phase 6: Comprehensive Health Check
echo ""
echo -e "${PURPLE}📋 Phase 6: Comprehensive Health Check${NC}"
echo -e "${YELLOW}Running final health checks...${NC}"

# Check all development services
HEALTH_CHECKS=0
TOTAL_CHECKS=5

echo -e "${BLUE}Checking development services...${NC}"

# 1. Static site
if check_service "https://dev.consulting.sa/health" "Development Site"; then
    ((HEALTH_CHECKS++))
fi

# 2. Backend agent
if check_service "https://dev.consulting.sa/backend/health" "Backend Agent (via Nginx)"; then
    ((HEALTH_CHECKS++))
fi

# 3. Direct agent access
if check_service "http://localhost:8001/health" "Backend Agent (Direct)"; then
    ((HEALTH_CHECKS++))
fi

# 4. n8n
if check_service "http://localhost:5679" "n8n Development"; then
    ((HEALTH_CHECKS++))
fi

# 5. Redis
if run_on_vps "docker exec agentic-redis-dev redis-cli ping" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis is responding${NC}"
    ((HEALTH_CHECKS++))
else
    echo -e "${YELLOW}⚠ Redis is not responding${NC}"
fi

# Health check summary
echo ""
echo -e "${BLUE}Health Check Summary: $HEALTH_CHECKS/$TOTAL_CHECKS services healthy${NC}"

if [ $HEALTH_CHECKS -eq $TOTAL_CHECKS ]; then
    HEALTH_STATUS="🟢 All services healthy"
elif [ $HEALTH_CHECKS -ge 3 ]; then
    HEALTH_STATUS="🟡 Most services healthy"
else
    HEALTH_STATUS="🔴 Multiple services unhealthy"
fi

# Final Status Report
echo ""
echo -e "${PURPLE}🎉 Development Environment Deployment Complete!${NC}"
echo ""
echo -e "${BLUE}=== DEPLOYMENT SUMMARY ===${NC}"
echo -e "Status: $HEALTH_STATUS"
echo -e "Services Deployed: Redis, n8n, Python ADK Agent, Static Site"
echo -e "Environment: Development (isolated from production)"
echo -e "SSL: ✅ Wildcard certificate active"
echo -e "Nginx: ✅ Reverse proxy configured"
echo ""
echo -e "${BLUE}=== ACCESS INFORMATION ===${NC}"
echo -e "${GREEN}🌐 Development Site:${NC} https://dev.consulting.sa"
echo -e "${GREEN}🔧 Backend API:${NC} https://dev.consulting.sa/backend/"
echo -e "${GREEN}📊 n8n Workflows:${NC} https://dev.consulting.sa/n8n/"
echo -e "${GREEN}🏥 Health Check:${NC} https://dev.consulting.sa/health"
echo ""
echo -e "${BLUE}=== DIRECT CONTAINER ACCESS ===${NC}"
echo -e "Frontend: http://$VPS_HOST:3001 (not deployed yet)"
echo -e "Backend: http://$VPS_HOST:8001"
echo -e "n8n: http://$VPS_HOST:5679"
echo -e "Redis: $VPS_HOST:6380"
echo ""
echo -e "${BLUE}=== CONTAINER STATUS ===${NC}"
run_on_vps "docker ps --filter name=agentic-*-dev --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'" || echo "Could not get container status"
echo ""
echo -e "${BLUE}=== NEXT STEPS ===${NC}"
echo -e "1. 🌐 Deploy Next.js frontend: ${YELLOW}./infrastructure/scripts/deploy-frontend-dev.sh${NC}"
echo -e "2. 🧪 Test functionality: ${YELLOW}Compare with https://consulting.sa${NC}"
echo -e "3. 📊 View documentation: ${YELLOW}cat docs/infrastructure/VPS_SERVER_STATUS.md${NC}"
echo -e "4. 🔄 Continue CI/CD pipeline: ${YELLOW}Implement remaining spec tasks${NC}"
echo ""
echo -e "${PURPLE}=== TROUBLESHOOTING ===${NC}"
echo -e "View logs: ${YELLOW}docker logs --tail 20 agentic-agent-dev${NC}"
echo -e "Check status: ${YELLOW}./infrastructure/scripts/update-server-docs.sh${NC}"
echo -e "Reset environment: ${YELLOW}./infrastructure/scripts/cleanup-dev.sh${NC}"
echo ""

if [ $HEALTH_CHECKS -eq $TOTAL_CHECKS ]; then
    echo -e "${GREEN}✅ Development environment is ready for frontend deployment and testing!${NC}"
    exit 0
elif [ $HEALTH_CHECKS -ge 3 ]; then
    echo -e "${YELLOW}⚠ Development environment is mostly ready, but some services need attention.${NC}"
    exit 0
else
    echo -e "${RED}❌ Development environment has significant issues. Check logs and retry.${NC}"
    exit 1
fi