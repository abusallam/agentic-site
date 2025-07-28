#!/bin/bash

# Deployment Status Check Script
# This script checks the status of your deployment on the main VPS

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

VPS_HOST=${VPS_HOST:-"217.79.255.54"}
VPS_USER=${VPS_USER:-"root"}
VPS_PASSWORD=${VPS_PASSWORD:-"gt5qXy22aJ"}
DOMAIN=${DOMAIN:-"consulting.sa"}

echo -e "${BLUE}🔍 Checking Deployment Status${NC}"
echo "VPS: $VPS_HOST"
echo "Domain: $DOMAIN"
echo ""

# Function to run commands on VPS
run_on_vps() {
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "$1"
}

# Check VPS connection
echo -e "${BLUE}1. Testing VPS Connection...${NC}"
if run_on_vps "echo 'Connection successful'" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ VPS connection is working${NC}"
else
    echo -e "${RED}❌ Cannot connect to VPS${NC}"
    exit 1
fi

# Check Docker containers
echo -e "\n${BLUE}2. Checking Docker Containers...${NC}"
run_on_vps "cd /opt/agentic-platform && docker-compose -f docker-compose.production.yml ps"

# Check service health
echo -e "\n${BLUE}3. Checking Service Health...${NC}"

# Frontend health
echo -n "Frontend: "
if run_on_vps "curl -f http://localhost:3000/api/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}❌ Unhealthy${NC}"
fi

# Backend health
echo -n "Backend: "
if run_on_vps "curl -f http://localhost:8000/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}❌ Unhealthy${NC}"
fi

# Nginx status
echo -n "Nginx: "
if run_on_vps "systemctl is-active nginx" | grep -q "active"; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}❌ Not running${NC}"
fi

# Check external access
echo -e "\n${BLUE}4. Checking External Access...${NC}"

# Test HTTP redirect
echo -n "HTTP redirect: "
if curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN" | grep -q "301"; then
    echo -e "${GREEN}✓ Working${NC}"
else
    echo -e "${YELLOW}⚠ May not be working${NC}"
fi

# Test HTTPS
echo -n "HTTPS access: "
if curl -f "https://$DOMAIN" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Working${NC}"
else
    echo -e "${YELLOW}⚠ May not be working (check DNS/SSL)${NC}"
fi

# Test API endpoints
echo -n "API health: "
if curl -f "https://$DOMAIN/api/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Working${NC}"
else
    echo -e "${YELLOW}⚠ May not be working${NC}"
fi

# Check system resources
echo -e "\n${BLUE}5. System Resources...${NC}"
run_on_vps "echo 'CPU and Memory:' && top -bn1 | head -5"
run_on_vps "echo 'Disk Usage:' && df -h /"

# Check logs for errors
echo -e "\n${BLUE}6. Recent Logs (last 10 lines)...${NC}"
echo -e "${YELLOW}Frontend logs:${NC}"
run_on_vps "cd /opt/agentic-platform && docker-compose -f docker-compose.production.yml logs --tail=10 frontend" 2>/dev/null || echo "No frontend logs"

echo -e "${YELLOW}Backend logs:${NC}"
run_on_vps "cd /opt/agentic-platform && docker-compose -f docker-compose.production.yml logs --tail=10 backend" 2>/dev/null || echo "No backend logs"

# SSL certificate status
echo -e "\n${BLUE}7. SSL Certificate Status...${NC}"
run_on_vps "certbot certificates" 2>/dev/null | grep -A 5 "$DOMAIN" || echo "SSL certificate info not available"

echo -e "\n${BLUE}📊 Status Summary${NC}"
echo "================================"
echo "Deployment location: /opt/agentic-platform"
echo "Docker compose file: docker-compose.production.yml"
echo "Nginx config: /etc/nginx/sites-enabled/agentic-platform"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "View all logs: sshpass -p '$VPS_PASSWORD' ssh $VPS_USER@$VPS_HOST 'cd /opt/agentic-platform && docker-compose -f docker-compose.production.yml logs -f'"
echo "Restart services: sshpass -p '$VPS_PASSWORD' ssh $VPS_USER@$VPS_HOST 'cd /opt/agentic-platform && docker-compose -f docker-compose.production.yml restart'"
echo "Update deployment: ./scripts/deploy-main-vps.sh"
echo ""
echo -e "${GREEN}✅ Status check completed${NC}"