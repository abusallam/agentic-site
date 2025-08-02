#!/bin/bash

# Fix Development Environment Script
# This script will properly deploy the development environment with correct container naming

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VPS_HOST="217.79.255.54"
DEPLOY_PATH="/opt/docker-apps/development/agentic-site"

echo -e "${BLUE}🔧 Fixing Development Environment${NC}"
echo "Target VPS: $VPS_HOST"
echo "Deploy Path: $DEPLOY_PATH"
echo "Timestamp: $(date)"
echo

# Function to run commands on VPS
run_on_vps() {
    ssh root@$VPS_HOST "$1"
}

echo -e "${YELLOW}Step 1: Stopping and removing conflicting containers...${NC}"

# Stop and remove any conflicting containers
run_on_vps "
    # Stop containers that might conflict
    docker stop agentic-frontend-development 2>/dev/null || true
    docker rm agentic-frontend-development 2>/dev/null || true
    
    # Stop any other development containers that might be running
    docker stop agentic-frontend-dev 2>/dev/null || true
    docker stop agentic-backend-dev 2>/dev/null || true
    docker rm agentic-frontend-dev 2>/dev/null || true
    docker rm agentic-backend-dev 2>/dev/null || true
    
    echo '✓ Conflicting containers removed'
"

echo -e "${YELLOW}Step 2: Ensuring deployment directory exists...${NC}"

run_on_vps "
    mkdir -p $DEPLOY_PATH
    cd $DEPLOY_PATH
    echo '✓ Deployment directory ready'
"

echo -e "${YELLOW}Step 3: Deploying development docker-compose configuration...${NC}"

# Copy the development docker-compose file to the server
scp infrastructure/docker/docker-compose.development.yml root@$VPS_HOST:$DEPLOY_PATH/docker-compose.yml

echo -e "${YELLOW}Step 4: Copying environment configuration...${NC}"

# Copy environment file if it exists
if [ -f ".env.development" ]; then
    scp .env.development root@$VPS_HOST:$DEPLOY_PATH/.env
    echo "✓ Environment file copied"
else
    echo "⚠ No .env.development file found, using default environment"
    run_on_vps "
        cd $DEPLOY_PATH
        cat > .env << 'EOF'
# Development Environment Configuration
NODE_ENV=development
COMPOSE_PROJECT_NAME=agentic-dev

# Frontend Configuration
FRONTEND_IMAGE=ghcr.io/consulting-sa/agentic-frontend:development

# Backend Configuration  
BACKEND_IMAGE=ghcr.io/consulting-sa/agentic-backend:development

# Database Configuration (use your actual values)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# AI Services (optional for development)
GEMINI_API_KEY=your_gemini_key

# n8n Configuration
N8N_USER=admin
N8N_PASSWORD=admin123

# Logging
ADK_LOG_LEVEL=DEBUG
EOF
        echo '✓ Default environment file created'
    "
fi

echo -e "${YELLOW}Step 5: Building and starting development containers...${NC}"

run_on_vps "
    cd $DEPLOY_PATH
    
    # Pull latest images
    echo 'Pulling latest development images...'
    docker-compose pull || echo 'Pull failed, will build locally'
    
    # Start the development environment
    echo 'Starting development environment...'
    docker-compose up -d
    
    echo '✓ Development containers started'
"

echo -e "${YELLOW}Step 6: Waiting for containers to be healthy...${NC}"

run_on_vps "
    cd $DEPLOY_PATH
    
    # Wait for containers to start
    sleep 10
    
    # Check container status
    echo 'Container Status:'
    docker-compose ps
    
    # Wait for health checks
    echo 'Waiting for health checks...'
    for i in {1..30}; do
        if docker-compose ps | grep -q 'healthy'; then
            echo '✓ Containers are healthy'
            break
        fi
        echo 'Waiting for containers to become healthy... (\$i/30)'
        sleep 5
    done
"

echo -e "${YELLOW}Step 7: Updating nginx configuration...${NC}"

run_on_vps "
    # Create the correct nginx configuration
    cat > /etc/nginx/sites-available/agentic-platform-dev-fixed << 'EOF'
upstream frontend_dev {
    server 127.0.0.1:3001;
}

upstream backend_dev {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name dev.consulting.sa;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection \"1; mode=block\";
    
    # Main application - proxy to Next.js
    location / {
        proxy_pass http://frontend_dev;
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
    
    # API routes - proxy to Python backend
    location /api/ {
        proxy_pass http://backend_dev/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }
    
    # Backend admin interface
    location /backend/ {
        proxy_pass http://backend_dev/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # n8n interface
    location /n8n/ {
        proxy_pass http://127.0.0.1:5679/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://backend_dev/health;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    # Remove old symlink and create new one
    rm -f /etc/nginx/sites-enabled/agentic-platform-dev*
    ln -sf /etc/nginx/sites-available/agentic-platform-dev-fixed /etc/nginx/sites-enabled/agentic-platform-dev-fixed
    
    # Test and reload nginx
    nginx -t && systemctl reload nginx
    
    echo '✓ Nginx configuration updated'
"

echo -e "${YELLOW}Step 8: Final verification...${NC}"

run_on_vps "
    cd $DEPLOY_PATH
    
    echo 'Final Container Status:'
    docker-compose ps
    
    echo
    echo 'Port Status:'
    netstat -tlnp | grep -E ':(3001|8001|5679|6380)' || echo 'No development ports found'
    
    echo
    echo 'Testing endpoints:'
    
    # Test backend
    if curl -s -f http://localhost:8001/health > /dev/null; then
        echo '✓ Backend responding on port 8001'
    else
        echo '❌ Backend not responding on port 8001'
    fi
    
    # Test frontend
    if curl -s -f http://localhost:3001/ > /dev/null; then
        echo '✓ Frontend responding on port 3001'
    else
        echo '❌ Frontend not responding on port 3001'
    fi
    
    # Test nginx proxy
    if curl -s -f -H 'Host: dev.consulting.sa' http://localhost/ > /dev/null; then
        echo '✓ Nginx proxy working'
    else
        echo '❌ Nginx proxy not working'
    fi
"

echo
echo -e "${GREEN}🎉 Development Environment Fix Complete!${NC}"
echo
echo -e "${BLUE}=== ACCESS INFORMATION ===${NC}"
echo "🌐 Development Site: https://dev.consulting.sa"
echo "🔧 API Health Check: https://dev.consulting.sa/health"  
echo "🛠️ n8n Interface: https://dev.consulting.sa/n8n/"
echo "💾 Backend Admin: https://dev.consulting.sa/backend/"
echo
echo -e "${BLUE}=== DIRECT ACCESS (for debugging) ===${NC}"
echo "Frontend: http://217.79.255.54:3001"
echo "Backend: http://217.79.255.54:8001"
echo "n8n: http://217.79.255.54:5679"
echo "Redis: 217.79.255.54:6380"
echo
echo -e "${BLUE}=== MANAGEMENT COMMANDS ===${NC}"
echo "Check status: ssh root@217.79.255.54 'cd $DEPLOY_PATH && docker-compose ps'"
echo "View logs: ssh root@217.79.255.54 'cd $DEPLOY_PATH && docker-compose logs -f'"
echo "Restart: ssh root@217.79.255.54 'cd $DEPLOY_PATH && docker-compose restart'"
echo
echo -e "${GREEN}Development environment is now properly configured!${NC}"