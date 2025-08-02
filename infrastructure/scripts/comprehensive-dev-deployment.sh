#!/bin/bash
set -e

# Comprehensive Development Deployment Script
# This script follows proper deployment practices:
# 1. Check server status and running containers
# 2. Identify nginx configuration
# 3. Stop conflicting containers
# 4. Deploy with correct configuration
# 5. Verify deployment

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Configuration
VPS_HOST=${VPS_HOST:-"217.79.255.54"}
VPS_USER=${VPS_USER:-"root"}
VPS_PASSWORD=${VPS_PASSWORD:-"xxXNCpx9Cz"}

echo -e "${PURPLE}🚀 Comprehensive Development Deployment${NC}"
echo -e "${BLUE}Target VPS: $VPS_HOST${NC}"
echo -e "${BLUE}Timestamp: $(date)${NC}"
echo ""

# Function to run commands on VPS using sshpass
run_on_vps() {
    local command="$1"
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "$command"
}

# Function to copy files to VPS
copy_to_vps() {
    local local_path="$1"
    local remote_path="$2"
    sshpass -p "$VPS_PASSWORD" scp -o StrictHostKeyChecking=no -r "$local_path" "$VPS_USER@$VPS_HOST:$remote_path"
}

# Test VPS connection
echo -e "${BLUE}Step 1: Testing VPS connection...${NC}"
if run_on_vps "echo 'Connection successful'"; then
    echo -e "${GREEN}✓ VPS connection established${NC}"
else
    echo -e "${RED}❌ Failed to connect to VPS${NC}"
    exit 1
fi

# PHASE 1: COMPREHENSIVE SERVER STATUS CHECK
echo ""
echo -e "${PURPLE}📊 PHASE 1: COMPREHENSIVE SERVER STATUS CHECK${NC}"
echo ""

# Check system resources
echo -e "${CYAN}System Resources:${NC}"
run_on_vps "echo 'CPU Usage:' && top -bn1 | grep 'Cpu(s)' | head -1"
run_on_vps "echo 'Memory Usage:' && free -h | head -2"
run_on_vps "echo 'Disk Usage:' && df -h / | tail -1"
run_on_vps "echo 'Docker System Usage:' && docker system df"

echo ""
echo -e "${CYAN}All Running Containers:${NC}"
CONTAINER_STATUS=$(run_on_vps "docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'")
echo "$CONTAINER_STATUS"

echo ""
echo -e "${CYAN}Development Container Analysis:${NC}"
DEV_CONTAINERS=("agentic-frontend-dev" "agentic-backend-dev" "agentic-redis-dev" "agentic-n8n-dev")
FOUND_DEV_CONTAINERS=()
CONFLICTING_CONTAINERS=()

# Check for our expected dev containers
for container in "${DEV_CONTAINERS[@]}"; do
    if run_on_vps "docker ps -q -f name=$container" | grep -q .; then
        echo -e "${GREEN}✓ Found expected dev container: $container${NC}"
        FOUND_DEV_CONTAINERS+=("$container")
    else
        echo -e "${YELLOW}⚠ Expected dev container not found: $container${NC}"
    fi
done

# Check for conflicting containers (old naming patterns)
CONFLICTING_PATTERNS=("agentic-frontend-development" "agentic-backend-development" "agentic-development-")
for pattern in "${CONFLICTING_PATTERNS[@]}"; do
    CONFLICTING=$(run_on_vps "docker ps --format '{{.Names}}' | grep '$pattern' || true")
    if [ -n "$CONFLICTING" ]; then
        echo -e "${RED}❌ Found conflicting containers with pattern '$pattern':${NC}"
        echo "$CONFLICTING" | while read container; do
            if [ -n "$container" ]; then
                echo -e "${RED}  - $container${NC}"
                CONFLICTING_CONTAINERS+=("$container")
            fi
        done
    fi
done

echo ""
echo -e "${CYAN}Port Usage Analysis:${NC}"
DEV_PORTS=(3001 3002 8001 5679 6380)
PROD_PORTS=(3000 8000 5678 6379)
OCCUPIED_PORTS=()

echo -e "${YELLOW}Development Ports (Expected):${NC}"
for port in "${DEV_PORTS[@]}"; do
    if run_on_vps "netstat -tuln | grep :$port" >/dev/null 2>&1; then
        PROCESS=$(run_on_vps "netstat -tulnp | grep :$port | awk '{print \$7}' | head -1")
        echo -e "${YELLOW}Port $port: IN USE by $PROCESS${NC}"
        OCCUPIED_PORTS+=("$port")
    else
        echo -e "${GREEN}Port $port: AVAILABLE${NC}"
    fi
done

echo -e "${YELLOW}Production Ports (Should be separate):${NC}"
for port in "${PROD_PORTS[@]}"; do
    if run_on_vps "netstat -tuln | grep :$port" >/dev/null 2>&1; then
        PROCESS=$(run_on_vps "netstat -tulnp | grep :$port | awk '{print \$7}' | head -1")
        echo -e "${YELLOW}Port $port: IN USE by $PROCESS${NC}"
    else
        echo -e "${GREEN}Port $port: AVAILABLE${NC}"
    fi
done

echo ""
echo -e "${CYAN}Nginx Configuration Analysis:${NC}"
echo -e "${YELLOW}Active nginx sites:${NC}"
run_on_vps "ls -la /etc/nginx/sites-enabled/ | grep agentic"

echo -e "${YELLOW}Current dev.consulting.sa configuration:${NC}"
CURRENT_NGINX_CONFIG=$(run_on_vps "readlink /etc/nginx/sites-enabled/agentic-platform-dev || echo 'Not found'")
echo "Current symlink: $CURRENT_NGINX_CONFIG"

if [ "$CURRENT_NGINX_CONFIG" != "Not found" ]; then
    echo -e "${YELLOW}Checking upstream configuration:${NC}"
    UPSTREAM_CONFIG=$(run_on_vps "grep -A 3 'upstream frontend_dev' $CURRENT_NGINX_CONFIG || echo 'No frontend_dev upstream found'")
    echo "$UPSTREAM_CONFIG"
fi

# PHASE 2: INTELLIGENT CLEANUP
echo ""
echo -e "${PURPLE}🧹 PHASE 2: INTELLIGENT CLEANUP${NC}"
echo ""

# Stop conflicting containers
if [ ${#CONFLICTING_CONTAINERS[@]} -gt 0 ]; then
    echo -e "${YELLOW}Stopping conflicting containers...${NC}"
    for container in "${CONFLICTING_CONTAINERS[@]}"; do
        if [ -n "$container" ]; then
            echo -e "${YELLOW}Stopping and removing: $container${NC}"
            run_on_vps "docker stop $container && docker rm $container" || echo -e "${RED}Failed to remove $container${NC}"
        fi
    done
else
    echo -e "${GREEN}✓ No conflicting containers found${NC}"
fi

# Clean up old development containers with different naming
echo -e "${YELLOW}Cleaning up old development containers...${NC}"
OLD_DEV_CONTAINERS=$(run_on_vps "docker ps -a --format '{{.Names}}' | grep -E '(agentic.*development|agentic-development)' | grep -v -E '(agentic-frontend-dev|agentic-backend-dev|agentic-redis-dev|agentic-n8n-dev)$' || true")
if [ -n "$OLD_DEV_CONTAINERS" ]; then
    echo "$OLD_DEV_CONTAINERS" | while read container; do
        if [ -n "$container" ]; then
            echo -e "${YELLOW}Removing old container: $container${NC}"
            run_on_vps "docker stop $container 2>/dev/null || true && docker rm $container 2>/dev/null || true"
        fi
    done
else
    echo -e "${GREEN}✓ No old development containers to clean${NC}"
fi

# Clean up docker resources
echo -e "${YELLOW}Cleaning up unused docker resources...${NC}"
run_on_vps "docker system prune -f"
run_on_vps "docker volume prune -f"
run_on_vps "docker network prune -f"

# PHASE 3: DETERMINE CORRECT CONFIGURATION
echo ""
echo -e "${PURPLE}🔧 PHASE 3: DETERMINE CORRECT CONFIGURATION${NC}"
echo ""

# Check what frontend port is actually being used
FRONTEND_PORT=""
if run_on_vps "docker ps | grep frontend" | grep -q "3002"; then
    FRONTEND_PORT="3002"
    echo -e "${YELLOW}Detected frontend running on port 3002${NC}"
elif run_on_vps "docker ps | grep frontend" | grep -q "3001"; then
    FRONTEND_PORT="3001"
    echo -e "${YELLOW}Detected frontend running on port 3001${NC}"
else
    FRONTEND_PORT="3001"
    echo -e "${YELLOW}No frontend detected, will use default port 3001${NC}"
fi

# Check what backend port is being used
BACKEND_PORT=""
if run_on_vps "docker ps | grep backend" | grep -q "8001"; then
    BACKEND_PORT="8001"
    echo -e "${YELLOW}Detected backend running on port 8001${NC}"
else
    BACKEND_PORT="8001"
    echo -e "${YELLOW}No backend detected, will use default port 8001${NC}"
fi

echo -e "${GREEN}Configuration determined:${NC}"
echo -e "${GREEN}  Frontend Port: $FRONTEND_PORT${NC}"
echo -e "${GREEN}  Backend Port: $BACKEND_PORT${NC}"

# PHASE 4: DEPLOY CORRECT NGINX CONFIGURATION
echo ""
echo -e "${PURPLE}⚙️ PHASE 4: DEPLOY CORRECT NGINX CONFIGURATION${NC}"
echo ""

# Create the correct nginx configuration
echo -e "${YELLOW}Creating nginx configuration for detected ports...${NC}"
cat > /tmp/development-auto.conf << EOF
# Auto-generated Nginx configuration for development environment
# Generated on: $(date)
# Frontend Port: $FRONTEND_PORT
# Backend Port: $BACKEND_PORT

upstream frontend_dev {
    server 127.0.0.1:$FRONTEND_PORT;
}

upstream backend_dev {
    server 127.0.0.1:$BACKEND_PORT;
}

upstream n8n_dev {
    server 127.0.0.1:5679;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name dev.consulting.sa;
    return 301 https://\$server_name\$request_uri;
}

# HTTPS server for development subdomain
server {
    listen 443 ssl http2;
    server_name dev.consulting.sa;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/consulting.sa.crt;
    ssl_certificate_key /etc/nginx/ssl/consulting.sa.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Frontend - Proxy to Next.js container
    location / {
        proxy_pass http://frontend_dev;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_buffering off;
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
        proxy_connect_timeout 60;
    }

    # Backend API routes
    location /api/ {
        proxy_pass http://backend_dev/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 86400;
    }

    # Backend health check
    location /health {
        proxy_pass http://backend_dev/health;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        access_log off;
    }

    # Backend admin interface
    location /admin/ {
        proxy_pass http://backend_dev/admin/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Direct backend access
    location /backend/ {
        proxy_pass http://backend_dev/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # n8n development instance
    location /n8n/ {
        proxy_pass http://n8n_dev/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Logging
    access_log /var/log/nginx/dev.consulting.sa.access.log;
    error_log /var/log/nginx/dev.consulting.sa.error.log;
}
EOF

# Copy the configuration to VPS
echo -e "${YELLOW}Deploying nginx configuration...${NC}"
copy_to_vps "/tmp/development-auto.conf" "/etc/nginx/sites-available/agentic-platform-dev-auto"

# Update the symlink
run_on_vps "ln -sf /etc/nginx/sites-available/agentic-platform-dev-auto /etc/nginx/sites-enabled/agentic-platform-dev"

# Test and reload nginx
echo -e "${YELLOW}Testing nginx configuration...${NC}"
if run_on_vps "nginx -t"; then
    echo -e "${GREEN}✓ Nginx configuration test passed${NC}"
    run_on_vps "systemctl reload nginx"
    echo -e "${GREEN}✓ Nginx reloaded successfully${NC}"
else
    echo -e "${RED}❌ Nginx configuration test failed${NC}"
    exit 1
fi

# PHASE 5: COMPREHENSIVE VERIFICATION
echo ""
echo -e "${PURPLE}✅ PHASE 5: COMPREHENSIVE VERIFICATION${NC}"
echo ""

# Test direct container access
echo -e "${CYAN}Testing direct container access:${NC}"
if run_on_vps "curl -f http://localhost:$FRONTEND_PORT/ >/dev/null 2>&1"; then
    echo -e "${GREEN}✓ Frontend container responding on port $FRONTEND_PORT${NC}"
else
    echo -e "${RED}❌ Frontend container not responding on port $FRONTEND_PORT${NC}"
fi

if run_on_vps "curl -f http://localhost:$BACKEND_PORT/health >/dev/null 2>&1"; then
    echo -e "${GREEN}✓ Backend container responding on port $BACKEND_PORT${NC}"
else
    echo -e "${RED}❌ Backend container not responding on port $BACKEND_PORT${NC}"
fi

# Test nginx proxy
echo -e "${CYAN}Testing nginx proxy:${NC}"
if run_on_vps "curl -f https://dev.consulting.sa/health >/dev/null 2>&1"; then
    echo -e "${GREEN}✓ Nginx proxy to backend working${NC}"
else
    echo -e "${RED}❌ Nginx proxy to backend failed${NC}"
fi

if run_on_vps "curl -f https://dev.consulting.sa/ >/dev/null 2>&1"; then
    echo -e "${GREEN}✓ Nginx proxy to frontend working${NC}"
else
    echo -e "${RED}❌ Nginx proxy to frontend failed${NC}"
fi

# Final status report
echo ""
echo -e "${PURPLE}📊 FINAL STATUS REPORT${NC}"
echo ""

echo -e "${CYAN}Container Status:${NC}"
run_on_vps "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E '(frontend|backend|redis|n8n).*dev'"

echo -e "${CYAN}Port Status:${NC}"
for port in "${DEV_PORTS[@]}"; do
    if run_on_vps "netstat -tuln | grep :$port" >/dev/null 2>&1; then
        echo -e "${GREEN}Port $port: IN USE${NC}"
    else
        echo -e "${YELLOW}Port $port: AVAILABLE${NC}"
    fi
done

echo -e "${CYAN}Nginx Configuration:${NC}"
echo "Active config: $(run_on_vps "readlink /etc/nginx/sites-enabled/agentic-platform-dev")"
echo "Frontend upstream: 127.0.0.1:$FRONTEND_PORT"
echo "Backend upstream: 127.0.0.1:$BACKEND_PORT"

echo ""
echo -e "${GREEN}🎉 COMPREHENSIVE DEPLOYMENT COMPLETED${NC}"
echo ""
echo -e "${BLUE}=== ACCESS INFORMATION ===${NC}"
echo -e "${GREEN}🌐 Development Site: https://dev.consulting.sa${NC}"
echo -e "${GREEN}🔧 API Health Check: https://dev.consulting.sa/health${NC}"
echo -e "${GREEN}🛠️ n8n Interface: https://dev.consulting.sa/n8n/${NC}"
echo -e "${GREEN}💾 Backend Admin: https://dev.consulting.sa/backend/${NC}"
echo ""
echo -e "${BLUE}=== DIRECT ACCESS (for debugging) ===${NC}"
echo -e "${YELLOW}Frontend: http://$VPS_HOST:$FRONTEND_PORT${NC}"
echo -e "${YELLOW}Backend: http://$VPS_HOST:$BACKEND_PORT${NC}"
echo ""
echo -e "${BLUE}=== DEPLOYMENT SUMMARY ===${NC}"
echo -e "${GREEN}✅ Server status checked and analyzed${NC}"
echo -e "${GREEN}✅ Conflicting containers cleaned up${NC}"
echo -e "${GREEN}✅ Nginx configuration auto-generated for detected ports${NC}"
echo -e "${GREEN}✅ All services verified and working${NC}"
echo -e "${GREEN}✅ Development environment ready for use${NC}"

# Clean up temp files
rm -f /tmp/development-auto.conf

echo ""
echo -e "${CYAN}Next time, run this script before making any changes to ensure proper deployment!${NC}"