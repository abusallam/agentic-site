#!/bin/bash
set -e

# Server Documentation Update Script
# This script automatically updates the VPS server documentation with current status

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

echo -e "${BLUE}📝 Updating VPS Server Documentation${NC}"

# Function to run commands on VPS using sshpass
run_on_vps() {
    local command="$1"
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "$command"
}

# Get current container status
echo -e "${BLUE}Gathering current server status...${NC}"

# Get all containers
CONTAINERS=$(run_on_vps "docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}'" | tail -n +2)

# Get production containers
PROD_CONTAINERS=$(run_on_vps "docker ps --filter name=agentic-*-prod --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'" | tail -n +2 || echo "No production containers")

# Get development containers  
DEV_CONTAINERS=$(run_on_vps "docker ps --filter name=agentic-*-dev --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'" | tail -n +2 || echo "No development containers")

# Get monitoring containers
MON_CONTAINERS=$(run_on_vps "docker ps --filter name=agentic- --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E '(prometheus|grafana|alert|exporter|cadvisor)'" | tail -n +2 || echo "No monitoring containers")

# Get disk usage
DISK_USAGE=$(run_on_vps "df -h / | tail -1")

# Get memory usage
MEMORY_USAGE=$(run_on_vps "free -h | grep Mem")

# Update the documentation
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

cat > docs/infrastructure/VPS_SERVER_STATUS.md << EOF
# VPS Server Status Report

**Generated**: $TIMESTAMP  
**Server**: $VPS_HOST

## 🐳 Current Container Status

### Production Containers
\`\`\`
$PROD_CONTAINERS
\`\`\`

### Development Containers  
\`\`\`
$DEV_CONTAINERS
\`\`\`

### Monitoring Containers
\`\`\`
$MON_CONTAINERS
\`\`\`

## 💾 System Resources

### Disk Usage
\`\`\`
$DISK_USAGE
\`\`\`

### Memory Usage
\`\`\`
$MEMORY_USAGE
\`\`\`

## 🌐 Service Endpoints

### Production
- **Main Site**: https://consulting.sa
- **API**: https://consulting.sa/api

### Development  
- **Dev Site**: https://dev.consulting.sa
- **Dev API**: https://dev.consulting.sa/api
- **Dev n8n**: https://dev.consulting.sa/n8n

### Monitoring
- **Prometheus**: http://$VPS_HOST:9090
- **Grafana**: http://$VPS_HOST:3000

## 📊 Quick Health Check

EOF

# Test endpoints and add to documentation
echo "### Endpoint Status" >> docs/infrastructure/VPS_SERVER_STATUS.md

# Test production
if run_on_vps "curl -f -s https://consulting.sa/health" > /dev/null 2>&1; then
    echo "- ✅ Production Site: Healthy" >> docs/infrastructure/VPS_SERVER_STATUS.md
else
    echo "- ❌ Production Site: Down" >> docs/infrastructure/VPS_SERVER_STATUS.md
fi

# Test development
if run_on_vps "curl -f -s https://dev.consulting.sa/health" > /dev/null 2>&1; then
    echo "- ✅ Development Site: Healthy" >> docs/infrastructure/VPS_SERVER_STATUS.md
else
    echo "- ❌ Development Site: Down" >> docs/infrastructure/VPS_SERVER_STATUS.md
fi

# Test Prometheus
if run_on_vps "curl -f -s http://localhost:9090/-/healthy" > /dev/null 2>&1; then
    echo "- ✅ Prometheus: Healthy" >> docs/infrastructure/VPS_SERVER_STATUS.md
else
    echo "- ❌ Prometheus: Down" >> docs/infrastructure/VPS_SERVER_STATUS.md
fi

echo "" >> docs/infrastructure/VPS_SERVER_STATUS.md
echo "---" >> docs/infrastructure/VPS_SERVER_STATUS.md
echo "**Last Updated**: $TIMESTAMP" >> docs/infrastructure/VPS_SERVER_STATUS.md

echo -e "${GREEN}✅ Server documentation updated!${NC}"
echo ""
echo -e "${BLUE}Documentation files:${NC}"
echo "- 📋 Main Documentation: docs/infrastructure/VPS_SERVER_MAIN.md"
echo "- 📊 Status Report: docs/infrastructure/VPS_SERVER_STATUS.md"
echo ""
echo -e "${YELLOW}View current status:${NC}"
echo "cat docs/infrastructure/VPS_SERVER_STATUS.md"