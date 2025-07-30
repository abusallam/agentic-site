#!/bin/bash

# Deployment Validation Script
# This script validates that the deployment is working correctly

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
DOMAIN=${DOMAIN:-"consulting.sa"}

echo -e "${PURPLE}🔍 Agentic AI Platform - Deployment Validation${NC}"
echo -e "${BLUE}Validating deployment on: $VPS_HOST ($DOMAIN)${NC}"
echo ""

# Function to run commands on VPS
run_on_vps() {
    local command="$1"
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "$command"
}

# Function to test HTTP endpoint
test_endpoint() {
    local url="$1"
    local expected="$2"
    local description="$3"
    
    echo -e "${YELLOW}Testing: $description${NC}"
    
    if curl -s -k "$url" | grep -q "$expected"; then
        echo -e "${GREEN}✓ $description - PASSED${NC}"
        return 0
    else
        echo -e "${RED}❌ $description - FAILED${NC}"
        return 1
    fi
}

# Validation counters
TOTAL_TESTS=0
PASSED_TESTS=0

# Function to run test and count results
run_test() {
    local test_command="$1"
    local test_name="$2"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${YELLOW}Test $TOTAL_TESTS: $test_name${NC}"
    
    if eval "$test_command"; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
        echo -e "${GREEN}✓ PASSED${NC}"
    else
        echo -e "${RED}❌ FAILED${NC}"
    fi
    echo ""
}

echo -e "${BLUE}=== Infrastructure Validation ===${NC}"

# Test 1: VPS Connection
run_test "sshpass -p '$VPS_PASSWORD' ssh -o StrictHostKeyChecking=no '$VPS_USER@$VPS_HOST' 'echo \"Connection test\"' > /dev/null 2>&1" "VPS SSH Connection"

# Test 2: Docker Service
run_test "run_on_vps 'systemctl is-active docker' | grep -q 'active'" "Docker Service Status"

# Test 3: Nginx Service
run_test "run_on_vps 'systemctl is-active nginx' | grep -q 'active'" "Nginx Service Status"

# Test 4: Firewall Configuration
run_test "run_on_vps 'ufw status' | grep -q 'Status: active'" "Firewall Status"

echo -e "${BLUE}=== Container Validation ===${NC}"

# Test 5: Frontend Container
run_test "run_on_vps 'docker ps --format \"{{.Names}}\" | grep -q \"agentic-frontend-prod\"'" "Frontend Container Running"

# Test 6: Backend Container
run_test "run_on_vps 'docker ps --format \"{{.Names}}\" | grep -q \"agentic-backend-prod\"'" "Backend Container Running"

# Test 7: Redis Container
run_test "run_on_vps 'docker ps --format \"{{.Names}}\" | grep -q \"agentic-redis-prod\"'" "Redis Container Running"

# Test 8: Container Health
run_test "run_on_vps 'docker ps --filter \"name=agentic-backend-prod\" --format \"{{.Status}}\" | grep -q \"healthy\"'" "Backend Container Health"

echo -e "${BLUE}=== SSL and Certificate Validation ===${NC}"

# Test 9: SSL Certificate Files
run_test "run_on_vps 'test -f /etc/nginx/ssl/consulting.sa.crt'" "SSL Certificate File"

# Test 10: SSL Key File
run_test "run_on_vps 'test -f /etc/nginx/ssl/consulting.sa.key'" "SSL Key File"

# Test 11: SSL Key Permissions
run_test "run_on_vps 'stat -c \"%a\" /etc/nginx/ssl/consulting.sa.key | grep -q \"600\"'" "SSL Key Permissions"

echo -e "${BLUE}=== Application Health Validation ===${NC}"

# Test 12: Frontend Health Endpoint
run_test "run_on_vps 'curl -s -k -H \"Host: consulting.sa\" https://localhost/api/health | grep -q \"ok\"'" "Frontend Health Endpoint"

# Test 13: Backend Health Endpoint
run_test "run_on_vps 'curl -s http://localhost:8000/health | grep -q \"status\"'" "Backend Health Endpoint"

# Test 14: Frontend Direct Access
run_test "run_on_vps 'curl -s http://localhost:3000/api/health | grep -q \"ok\"'" "Frontend Direct Access"

# Test 15: Backend Direct Access
run_test "run_on_vps 'curl -s http://localhost:8000/health | grep -q \"status\"'" "Backend Direct Access"

echo -e "${BLUE}=== Network and Connectivity Validation ===${NC}"

# Test 16: HTTP to HTTPS Redirect
run_test "run_on_vps 'curl -s -I -H \"Host: consulting.sa\" http://localhost/ | grep -q \"301\"'" "HTTP to HTTPS Redirect"

# Test 17: Nginx Configuration Test
run_test "run_on_vps 'nginx -t' > /dev/null 2>&1" "Nginx Configuration Syntax"

# Test 18: Port Accessibility
run_test "run_on_vps 'netstat -tulpn | grep -q \":443\"'" "HTTPS Port (443) Listening"

echo -e "${BLUE}=== File and Directory Validation ===${NC}"

# Test 19: Application Directory
run_test "run_on_vps 'test -d /opt/agentic-platform'" "Application Directory"

# Test 20: Environment File
run_test "run_on_vps 'test -f /opt/agentic-platform/.env'" "Environment File"

# Test 21: Docker Compose File
run_test "run_on_vps 'test -f /opt/agentic-platform/docker-compose.production.yml'" "Docker Compose File"

# Test 22: Status Script
run_test "run_on_vps 'test -x /opt/agentic-platform/check-status.sh'" "Status Check Script"

echo -e "${BLUE}=== Performance and Resource Validation ===${NC}"

# Test 23: Disk Space
run_test "run_on_vps 'df -h / | tail -1 | awk \"{print \$5}\" | sed \"s/%//\" | awk \"{if(\$1 < 80) exit 0; else exit 1}\"'" "Disk Space Usage (<80%)"

# Test 24: Memory Usage
run_test "run_on_vps 'free | grep Mem | awk \"{if(\$3/\$2 < 0.9) exit 0; else exit 1}\"'" "Memory Usage (<90%)"

# Test 25: Load Average
run_test "run_on_vps 'uptime | awk -F\"load average:\" \"{print \$2}\" | awk -F\",\" \"{if(\$1 < 5) exit 0; else exit 1}\"'" "System Load Average (<5)"

echo -e "${BLUE}=== Security Validation ===${NC}"

# Test 26: Fail2ban Service
run_test "run_on_vps 'systemctl is-active fail2ban' | grep -q 'active'" "Fail2ban Service"

# Test 27: UFW Firewall Rules
run_test "run_on_vps 'ufw status numbered | grep -q \"443/tcp\"'" "HTTPS Firewall Rule"

# Test 28: SSH Key Permissions
run_test "run_on_vps 'stat -c \"%a\" /etc/nginx/ssl/consulting.sa.key | grep -q \"600\"'" "SSL Key Security"

echo -e "${PURPLE}=== Validation Summary ===${NC}"
echo ""

# Calculate success rate
SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))

echo -e "${BLUE}Total Tests: $TOTAL_TESTS${NC}"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $((TOTAL_TESTS - PASSED_TESTS))${NC}"
echo -e "${PURPLE}Success Rate: $SUCCESS_RATE%${NC}"
echo ""

# Determine overall status
if [ $SUCCESS_RATE -ge 90 ]; then
    echo -e "${GREEN}🎉 DEPLOYMENT VALIDATION: EXCELLENT${NC}"
    echo -e "${GREEN}✅ Your deployment is working excellently!${NC}"
    exit 0
elif [ $SUCCESS_RATE -ge 80 ]; then
    echo -e "${YELLOW}⚠️  DEPLOYMENT VALIDATION: GOOD${NC}"
    echo -e "${YELLOW}✅ Your deployment is working well with minor issues${NC}"
    exit 0
elif [ $SUCCESS_RATE -ge 70 ]; then
    echo -e "${YELLOW}⚠️  DEPLOYMENT VALIDATION: ACCEPTABLE${NC}"
    echo -e "${YELLOW}⚠️  Your deployment has some issues that should be addressed${NC}"
    exit 1
else
    echo -e "${RED}❌ DEPLOYMENT VALIDATION: FAILED${NC}"
    echo -e "${RED}❌ Your deployment has significant issues that need immediate attention${NC}"
    exit 1
fi