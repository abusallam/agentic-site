#!/bin/bash

# 🚀 Pre-Deployment Comprehensive Check Script
# This script validates the entire deployment environment before deploying to VPS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
VPS_HOST="217.79.255.54"
VPS_USER="root"
VPS_PASS="xxXNCpx9Cz"
PROJECT_NAME="agentic-site"

echo -e "${BLUE}🚀 Pre-Deployment Comprehensive Check${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Function to print section headers
print_section() {
    echo -e "${PURPLE}📋 $1${NC}"
    echo -e "${PURPLE}$(printf '=%.0s' {1..50})${NC}"
}

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        if [ "$3" != "" ]; then
            echo -e "${YELLOW}   Details: $3${NC}"
        fi
    fi
}

# Function to check command exists
check_command() {
    if command -v $1 &> /dev/null; then
        print_status 0 "$1 is available"
        return 0
    else
        print_status 1 "$1 is not available"
        return 1
    fi
}

# Function to get version
get_version() {
    local cmd=$1
    local version_flag=$2
    if command -v $cmd &> /dev/null; then
        local version=$($cmd $version_flag 2>/dev/null | head -n1)
        echo "$version"
    else
        echo "Not installed"
    fi
}

print_section "Phase 1: Local Environment Validation"

echo -e "${CYAN}🔍 Checking required tools...${NC}"
check_command "node"
check_command "npm"
check_command "git"
check_command "docker"
check_command "docker-compose"
check_command "sshpass"

echo ""
echo -e "${CYAN}📊 Checking versions...${NC}"
echo -e "Node.js: $(get_version 'node' '--version')"
echo -e "npm: $(get_version 'npm' '--version')"
echo -e "Git: $(get_version 'git' '--version')"
echo -e "Docker: $(get_version 'docker' '--version')"
echo -e "Docker Compose: $(get_version 'docker-compose' '--version')"

echo ""
echo -e "${CYAN}📦 Checking package.json consistency...${NC}"
if [ -f "package.json" ] && [ -f "frontend/package.json" ]; then
    ROOT_NODE=$(node -p "require('./package.json').engines.node")
    FRONTEND_NODE=$(node -p "require('./frontend/package.json').engines.node")
    ROOT_NEXT=$(node -p "require('./package.json').dependencies.next")
    FRONTEND_NEXT=$(node -p "require('./frontend/package.json').dependencies.next")
    
    if [ "$ROOT_NODE" = "$FRONTEND_NODE" ]; then
        print_status 0 "Node.js engine versions match"
    else
        print_status 1 "Node.js engine versions mismatch: Root=$ROOT_NODE, Frontend=$FRONTEND_NODE"
    fi
    
    if [ "$ROOT_NEXT" = "$FRONTEND_NEXT" ]; then
        print_status 0 "Next.js versions match"
    else
        print_status 1 "Next.js versions mismatch: Root=$ROOT_NEXT, Frontend=$FRONTEND_NEXT"
    fi
else
    print_status 1 "Missing package.json files"
fi

echo ""
echo -e "${CYAN}🔒 Checking lock files...${NC}"
if [ -f "package-lock.json" ]; then
    print_status 0 "Root package-lock.json exists (workspace setup)"
else
    print_status 1 "Root package-lock.json missing"
fi

if [ -f "uv.lock" ]; then
    print_status 0 "uv.lock exists"
else
    print_status 1 "uv.lock missing"
fi

print_section "Phase 2: Frontend Validation"

echo -e "${CYAN}🔍 Checking frontend dependencies...${NC}"
cd frontend
if npm ci --dry-run &>/dev/null; then
    print_status 0 "Frontend dependencies are consistent"
else
    print_status 1 "Frontend dependencies have issues"
fi

echo ""
echo -e "${CYAN}🔧 Running frontend type check...${NC}"
if npm run type-check &>/dev/null; then
    print_status 0 "TypeScript compilation successful"
else
    print_status 1 "TypeScript compilation failed"
fi

echo ""
echo -e "${CYAN}🎨 Running frontend linting...${NC}"
if npm run lint &>/dev/null; then
    print_status 0 "ESLint passed"
else
    print_status 1 "ESLint failed"
fi

echo ""
echo -e "${CYAN}🏗️ Testing frontend build...${NC}"
if npm run build &>/dev/null; then
    print_status 0 "Frontend build successful"
else
    print_status 1 "Frontend build failed"
fi

cd ..

print_section "Phase 3: Backend Validation"

echo -e "${CYAN}🐍 Checking Python environment...${NC}"
if [ -f "backend/pyproject.toml" ]; then
    print_status 0 "Backend pyproject.toml exists"
else
    print_status 1 "Backend pyproject.toml missing"
fi

if [ -f "backend/agent/pyproject.toml" ]; then
    print_status 0 "Agent pyproject.toml exists"
else
    print_status 1 "Agent pyproject.toml missing"
fi

echo ""
echo -e "${CYAN}📦 Checking backend dependencies...${NC}"
if command -v uv &> /dev/null; then
    cd backend
    if uv sync --dry-run &>/dev/null; then
        print_status 0 "Backend dependencies are consistent"
    else
        print_status 1 "Backend dependencies have issues"
    fi
    cd ..
else
    print_status 1 "uv package manager not available"
fi

print_section "Phase 4: Docker Validation"

echo -e "${CYAN}🐳 Checking Docker images...${NC}"
if docker images | grep -q "agentic-development"; then
    print_status 0 "Development Docker images exist"
else
    print_status 1 "Development Docker images missing"
fi

echo ""
echo -e "${CYAN}📋 Checking Docker Compose files...${NC}"
if [ -f "infrastructure/docker/docker-compose.development.yml" ]; then
    print_status 0 "Development docker-compose.yml exists"
else
    print_status 1 "Development docker-compose.yml missing"
fi

if [ -f "infrastructure/docker/Dockerfile.frontend" ]; then
    print_status 0 "Frontend Dockerfile exists"
else
    print_status 1 "Frontend Dockerfile missing"
fi

if [ -f "infrastructure/docker/Dockerfile.backend" ]; then
    print_status 0 "Backend Dockerfile exists"
else
    print_status 1 "Backend Dockerfile missing"
fi

print_section "Phase 5: VPS Connection & Environment Check"

echo -e "${CYAN}🔗 Testing VPS connection...${NC}"
if sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 $VPS_USER@$VPS_HOST "echo 'Connection successful'" &>/dev/null; then
    print_status 0 "VPS connection successful"
else
    print_status 1 "VPS connection failed"
    exit 1
fi

echo ""
echo -e "${CYAN}📊 Checking VPS system information...${NC}"
VPS_INFO=$(sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST "
echo '=== System Info ==='
uname -a
echo '=== Memory ==='
free -h
echo '=== Disk Space ==='
df -h /
echo '=== Docker Version ==='
docker --version
echo '=== Docker Compose Version ==='
docker-compose --version
echo '=== Node Version ==='
node --version 2>/dev/null || echo 'Node not installed'
echo '=== npm Version ==='
npm --version 2>/dev/null || echo 'npm not installed'
")

echo "$VPS_INFO"

echo ""
echo -e "${CYAN}🔍 Checking running containers...${NC}"
RUNNING_CONTAINERS=$(sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'")
echo "$RUNNING_CONTAINERS"

echo ""
echo -e "${CYAN}🌐 Checking port usage...${NC}"
PORT_USAGE=$(sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST "
echo '=== Port 80 ==='
netstat -tlnp | grep :80 || echo 'Port 80: Available'
echo '=== Port 443 ==='
netstat -tlnp | grep :443 || echo 'Port 443: Available'
echo '=== Port 3000-3010 ==='
netstat -tlnp | grep :300[0-9] || echo 'Ports 3000-3010: Available'
echo '=== Port 8000-8010 ==='
netstat -tlnp | grep :800[0-9] || echo 'Ports 8000-8010: Available'
echo '=== Port 5678-5680 ==='
netstat -tlnp | grep :567[8-9] || netstat -tlnp | grep :5680 || echo 'Ports 5678-5680: Available'
echo '=== Port 6379-6381 ==='
netstat -tlnp | grep :637[9] || netstat -tlnp | grep :638[0-1] || echo 'Ports 6379-6381: Available'
")

echo "$PORT_USAGE"

print_section "Phase 6: Development Environment Status"

echo -e "${CYAN}📁 Checking development directory...${NC}"
DEV_DIR_STATUS=$(sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST "
if [ -d '/opt/agentic-development' ]; then
    echo 'Development directory exists'
    ls -la /opt/agentic-development/
    echo '=== Docker Compose Status ==='
    cd /opt/agentic-development && docker-compose -f docker-compose.development.yml ps 2>/dev/null || echo 'No development containers running'
else
    echo 'Development directory does not exist'
fi
")

echo "$DEV_DIR_STATUS"

echo ""
echo -e "${CYAN}📋 Checking development container logs...${NC}"
DEV_LOGS=$(sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST "
cd /opt/agentic-development 2>/dev/null && docker-compose -f docker-compose.development.yml logs --tail=20 2>/dev/null || echo 'No development logs available'
")

echo "$DEV_LOGS"

print_section "Phase 7: Health Checks"

echo -e "${CYAN}🏥 Checking service health...${NC}"
HEALTH_CHECKS=$(sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST "
echo '=== Frontend Health ==='
curl -f http://localhost:3002/ 2>/dev/null && echo 'Frontend: Healthy' || echo 'Frontend: Unhealthy'
echo '=== Backend Health ==='
curl -f http://localhost:8002/health 2>/dev/null && echo 'Backend: Healthy' || echo 'Backend: Unhealthy'
echo '=== n8n Health ==='
curl -f http://localhost:5680/ 2>/dev/null && echo 'n8n: Healthy' || echo 'n8n: Unhealthy'
echo '=== Redis Health ==='
redis-cli -p 6381 ping 2>/dev/null && echo 'Redis: Healthy' || echo 'Redis: Unhealthy'
")

echo "$HEALTH_CHECKS"

print_section "Phase 8: Security & Configuration"

echo -e "${CYAN}🔐 Checking SSL certificate...${NC}"
SSL_STATUS=$(sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST "
if [ -f '/etc/letsencrypt/live/dev.consulting.sa/fullchain.pem' ]; then
    echo 'SSL certificate exists'
    openssl x509 -in /etc/letsencrypt/live/dev.consulting.sa/fullchain.pem -text -noout | grep -A2 'Validity'
else
    echo 'SSL certificate missing'
fi
")

echo "$SSL_STATUS"

echo ""
echo -e "${CYAN}🌐 Checking Nginx configuration...${NC}"
NGINX_STATUS=$(sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST "
if command -v nginx &> /dev/null; then
    nginx -t 2>&1 && echo 'Nginx configuration: Valid' || echo 'Nginx configuration: Invalid'
    systemctl is-active nginx 2>/dev/null && echo 'Nginx service: Active' || echo 'Nginx service: Inactive'
else
    echo 'Nginx not installed'
fi
")

echo "$NGINX_STATUS"

print_section "Phase 9: Deployment Readiness Summary"

echo -e "${CYAN}📊 Generating deployment readiness report...${NC}"

# Count issues
ISSUES=0
WARNINGS=0

# Check critical issues
if ! sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 $VPS_USER@$VPS_HOST "echo 'test'" &>/dev/null; then
    echo -e "${RED}❌ CRITICAL: Cannot connect to VPS${NC}"
    ISSUES=$((ISSUES + 1))
fi

if [ ! -f "package-lock.json" ]; then
    echo -e "${RED}❌ CRITICAL: Missing root package-lock.json${NC}"
    ISSUES=$((ISSUES + 1))
fi

if ! cd frontend && npm run build &>/dev/null; then
    echo -e "${RED}❌ CRITICAL: Frontend build fails${NC}"
    ISSUES=$((ISSUES + 1))
fi

cd ..

# Check warnings
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}⚠️  WARNING: uv package manager not available${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""
echo -e "${BLUE}📋 Deployment Readiness Summary${NC}"
echo -e "${BLUE}==============================${NC}"
echo -e "Critical Issues: ${RED}$ISSUES${NC}"
echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}🎉 Deployment environment is READY!${NC}"
    echo -e "${GREEN}You can proceed with deployment.${NC}"
    exit 0
else
    echo -e "${RED}🚫 Deployment environment has issues that need to be resolved.${NC}"
    echo -e "${YELLOW}Please fix the critical issues before deploying.${NC}"
    exit 1
fi 