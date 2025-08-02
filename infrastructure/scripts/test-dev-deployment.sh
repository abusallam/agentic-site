#!/bin/bash

# Test Development Deployment Script
# Quick script to test if the development environment is working correctly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

VPS_HOST="217.79.255.54"
DEPLOY_PATH="/opt/docker-apps/development/agentic-site"

echo -e "${BLUE}🧪 Testing Development Deployment${NC}"
echo "Target VPS: $VPS_HOST"
echo "Timestamp: $(date)"
echo

# Function to run commands on VPS
run_on_vps() {
    ssh root@$VPS_HOST "$1"
}

echo -e "${YELLOW}Testing container status...${NC}"

run_on_vps "
    cd $DEPLOY_PATH 2>/dev/null || { echo '❌ Deployment directory not found'; exit 1; }
    
    echo 'Container Status:'
    docker-compose ps
    
    echo
    echo 'Expected containers:'
    echo '- agentic-frontend-dev (port 3001)'
    echo '- agentic-backend-dev (port 8001)'  
    echo '- agentic-redis-dev (port 6380)'
    echo '- agentic-n8n-dev (port 5679)'
"

echo -e "${YELLOW}Testing port accessibility...${NC}"

run_on_vps "
    echo 'Port Status:'
    
    # Test each expected port
    for port in 3001 8001 5679 6380; do
        if netstat -tlnp | grep -q \":$port \"; then
            echo \"✓ Port $port is in use\"
        else
            echo \"❌ Port $port is not in use\"
        fi
    done
"

echo -e "${YELLOW}Testing service endpoints...${NC}"

run_on_vps "
    echo 'Service Health Checks:'
    
    # Test backend health
    if curl -s -f --max-time 5 http://localhost:8001/health > /dev/null 2>&1; then
        echo '✓ Backend health check passed'
    else
        echo '❌ Backend health check failed'
    fi
    
    # Test frontend
    if curl -s -f --max-time 5 http://localhost:3001/ > /dev/null 2>&1; then
        echo '✓ Frontend responding'
    else
        echo '❌ Frontend not responding'
    fi
    
    # Test Redis
    if docker exec agentic-redis-dev redis-cli ping > /dev/null 2>&1; then
        echo '✓ Redis responding'
    else
        echo '❌ Redis not responding'
    fi
    
    # Test n8n
    if curl -s -f --max-time 5 http://localhost:5679/ > /dev/null 2>&1; then
        echo '✓ n8n responding'
    else
        echo '❌ n8n not responding'
    fi
"

echo -e "${YELLOW}Testing nginx proxy...${NC}"

run_on_vps "
    echo 'Nginx Proxy Tests:'
    
    # Test main site
    if curl -s -f --max-time 5 -H 'Host: dev.consulting.sa' http://localhost/ > /dev/null 2>&1; then
        echo '✓ Main site proxy working'
    else
        echo '❌ Main site proxy failed'
    fi
    
    # Test API endpoint
    if curl -s -f --max-time 5 -H 'Host: dev.consulting.sa' http://localhost/api/health > /dev/null 2>&1; then
        echo '✓ API proxy working'
    else
        echo '❌ API proxy failed'
    fi
    
    # Test backend admin
    if curl -s -f --max-time 5 -H 'Host: dev.consulting.sa' http://localhost/backend/ > /dev/null 2>&1; then
        echo '✓ Backend admin proxy working'
    else
        echo '❌ Backend admin proxy failed'
    fi
"

echo -e "${YELLOW}Testing external access...${NC}"

echo "External Access Tests:"

# Test main site
if curl -s -f --max-time 10 https://dev.consulting.sa/ > /dev/null 2>&1; then
    echo "✓ https://dev.consulting.sa/ accessible"
else
    echo "❌ https://dev.consulting.sa/ not accessible"
fi

# Test API health
if curl -s -f --max-time 10 https://dev.consulting.sa/health > /dev/null 2>&1; then
    echo "✓ https://dev.consulting.sa/health accessible"
else
    echo "❌ https://dev.consulting.sa/health not accessible"
fi

echo
echo -e "${BLUE}=== QUICK ACCESS LINKS ===${NC}"
echo "🌐 Main Site: https://dev.consulting.sa/"
echo "🔧 Health Check: https://dev.consulting.sa/health"
echo "🛠️ n8n: https://dev.consulting.sa/n8n/"
echo "💾 Backend: https://dev.consulting.sa/backend/"

echo
echo -e "${GREEN}🎯 Development deployment test complete!${NC}"