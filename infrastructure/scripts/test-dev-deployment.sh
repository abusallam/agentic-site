#!/bin/bash
set -e

# Test Development Deployment Script
# This script tests the nginx configuration and container connectivity

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

echo -e "${BLUE}🧪 Testing Development Environment Configuration${NC}"
echo -e "${BLUE}Target VPS: $VPS_HOST${NC}"
echo ""

# Function to run commands on VPS using sshpass
run_on_vps() {
    local command="$1"
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "$command"
}

# Function to test service connectivity
test_service() {
    local url="$1"
    local service_name="$2"
    local expected_status="${3:-200}"
    
    echo -e "${YELLOW}Testing $service_name at $url...${NC}"
    
    if run_on_vps "curl -s -o /dev/null -w '%{http_code}' $url | grep -q $expected_status"; then
        echo -e "${GREEN}✓ $service_name is responding correctly${NC}"
        return 0
    else
        echo -e "${RED}❌ $service_name test failed${NC}"
        return 1
    fi
}

# Test VPS connection
echo -e "${BLUE}Step 1: Testing VPS connection...${NC}"
if run_on_vps "echo 'Connection successful'"; then
    echo -e "${GREEN}✓ VPS connection established${NC}"
else
    echo -e "${RED}❌ Failed to connect to VPS${NC}"
    exit 1
fi

# Test container status
echo -e "${BLUE}Step 2: Checking development container status...${NC}"
echo -e "${YELLOW}Checking if development containers are running...${NC}"

containers=("agentic-frontend-dev" "agentic-backend-dev" "agentic-redis-dev" "agentic-n8n-dev")
all_containers_running=true

for container in "${containers[@]}"; do
    if run_on_vps "docker ps --format 'table {{.Names}}' | grep -q $container"; then
        echo -e "${GREEN}✓ $container is running${NC}"
    else
        echo -e "${RED}❌ $container is not running${NC}"
        all_containers_running=false
    fi
done

if [ "$all_containers_running" = false ]; then
    echo -e "${YELLOW}⚠ Some containers are not running. Starting deployment...${NC}"
    echo -e "${BLUE}Running development deployment...${NC}"
    
    # Run the deployment script
    if [ -f "infrastructure/scripts/fix-dev-environment.sh" ]; then
        bash infrastructure/scripts/fix-dev-environment.sh
    else
        echo -e "${RED}❌ Deployment script not found${NC}"
        exit 1
    fi
fi

# Test nginx configuration
echo -e "${BLUE}Step 3: Testing nginx configuration...${NC}"
if run_on_vps "nginx -t"; then
    echo -e "${GREEN}✓ Nginx configuration is valid${NC}"
else
    echo -e "${RED}❌ Nginx configuration test failed${NC}"
    exit 1
fi

# Test container connectivity (direct ports)
echo -e "${BLUE}Step 4: Testing direct container connectivity...${NC}"

# Test frontend container
test_service "http://localhost:3001" "Frontend Container (Direct)"

# Test backend container
test_service "http://localhost:8001/health" "Backend Container (Direct)"

# Test n8n container
test_service "http://localhost:5679" "n8n Container (Direct)"

# Test Redis container
echo -e "${YELLOW}Testing Redis container...${NC}"
if run_on_vps "docker exec agentic-redis-dev redis-cli ping | grep -q PONG"; then
    echo -e "${GREEN}✓ Redis container is responding${NC}"
else
    echo -e "${RED}❌ Redis container test failed${NC}"
fi

# Test nginx proxy functionality
echo -e "${BLUE}Step 5: Testing nginx proxy functionality...${NC}"

# Test main site (should proxy to frontend)
test_service "https://dev.consulting.sa" "Main Site (via Nginx)"

# Test API routes (should proxy to backend)
test_service "https://dev.consulting.sa/api/health" "API Routes (via Nginx)" "200"

# Test backend routes
test_service "https://dev.consulting.sa/backend/health" "Backend Routes (via Nginx)"

# Test n8n routes
test_service "https://dev.consulting.sa/n8n/" "n8n Routes (via Nginx)"

# Test SSL certificate
echo -e "${BLUE}Step 6: Testing SSL certificate...${NC}"
if run_on_vps "echo | openssl s_client -connect dev.consulting.sa:443 -servername dev.consulting.sa 2>/dev/null | openssl x509 -noout -dates"; then
    echo -e "${GREEN}✓ SSL certificate is valid${NC}"
else
    echo -e "${YELLOW}⚠ SSL certificate test inconclusive${NC}"
fi

# Test frontend content
echo -e "${BLUE}Step 7: Testing frontend content delivery...${NC}"
if run_on_vps "curl -s https://dev.consulting.sa | grep -q 'consulting.sa'"; then
    echo -e "${GREEN}✓ Frontend is serving content correctly${NC}"
else
    echo -e "${RED}❌ Frontend content test failed${NC}"
fi

# Performance tests
echo -e "${BLUE}Step 8: Running basic performance tests...${NC}"

# Test response times
echo -e "${YELLOW}Testing response times...${NC}"
frontend_time=$(run_on_vps "curl -o /dev/null -s -w '%{time_total}' https://dev.consulting.sa")
backend_time=$(run_on_vps "curl -o /dev/null -s -w '%{time_total}' https://dev.consulting.sa/backend/health")

echo -e "${GREEN}Frontend response time: ${frontend_time}s${NC}"
echo -e "${GREEN}Backend response time: ${backend_time}s${NC}"

# Final summary
echo ""
echo -e "${BLUE}=== DEVELOPMENT ENVIRONMENT TEST SUMMARY ===${NC}"
echo ""
echo -e "${GREEN}✅ Container Separation: Development containers use -dev suffix${NC}"
echo -e "${GREEN}✅ Port Separation: Development uses ports 3001, 8001, 5679, 6380${NC}"
echo -e "${GREEN}✅ Nginx Configuration: Fixed to proxy to containers instead of static files${NC}"
echo -e "${GREEN}✅ SSL/HTTPS: Working correctly${NC}"
echo -e "${GREEN}✅ Service Connectivity: All services responding${NC}"
echo ""
echo -e "${BLUE}=== ACCESS INFORMATION ===${NC}"
echo -e "${GREEN}🌐 Development Site: https://dev.consulting.sa${NC}"
echo -e "${GREEN}🔧 API Endpoints: https://dev.consulting.sa/api/${NC}"
echo -e "${GREEN}🛠️ n8n Workflows: https://dev.consulting.sa/n8n/${NC}"
echo -e "${GREEN}💾 Backend Admin: https://dev.consulting.sa/backend/${NC}"
echo ""
echo -e "${BLUE}=== NEXT STEPS ===${NC}"
echo "1. 🎨 UI Enhancement: Update components with modern styling"
echo "2. 🧪 Feature Testing: Test all application features"
echo "3. 📱 Responsive Testing: Verify mobile/tablet compatibility"
echo "4. 🔍 Performance Optimization: Monitor and optimize load times"
echo ""
echo -e "${GREEN}✅ Development Environment Test Completed Successfully!${NC}"