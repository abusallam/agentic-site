#!/bin/bash

# Deploy Frontend Development Script
# This script builds and deploys the frontend with all the fixes we made

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

VPS_HOST="217.79.255.54"
DEPLOY_PATH="/opt/docker-apps/development/agentic-site"

echo -e "${BLUE}🚀 Deploying Frontend Development Build${NC}"
echo "Target VPS: $VPS_HOST"
echo "Timestamp: $(date)"
echo

# Function to run commands on VPS
run_on_vps() {
    ssh root@$VPS_HOST "$1"
}

echo -e "${YELLOW}Step 1: Building frontend locally...${NC}"

# Build the frontend
cd frontend
npm install
npm run build
cd ..

echo "✓ Frontend built successfully"

echo -e "${YELLOW}Step 2: Creating deployment package...${NC}"

# Create a deployment package
tar -czf frontend-dev-deploy.tar.gz \
    frontend/.next \
    frontend/public \
    frontend/package.json \
    frontend/package-lock.json \
    frontend/next.config.mjs \
    frontend/tailwind.config.ts \
    frontend/tsconfig.json \
    frontend/components.json \
    --exclude='frontend/node_modules' \
    --exclude='frontend/.next/cache'

echo "✓ Deployment package created"

echo -e "${YELLOW}Step 3: Uploading to server...${NC}"

# Upload the package
scp frontend-dev-deploy.tar.gz root@$VPS_HOST:/tmp/

echo "✓ Package uploaded"

echo -e "${YELLOW}Step 4: Deploying on server...${NC}"

run_on_vps "
    cd $DEPLOY_PATH
    
    # Create frontend directory if it doesn't exist
    mkdir -p frontend
    
    # Extract the deployment package
    cd frontend
    tar -xzf /tmp/frontend-dev-deploy.tar.gz --strip-components=1
    
    # Install dependencies
    npm ci --only=production
    
    echo '✓ Frontend deployed to server'
"

echo -e "${YELLOW}Step 5: Creating Dockerfile for development...${NC}"

run_on_vps "
    cd $DEPLOY_PATH
    
    # Create a development Dockerfile
    cat > Dockerfile.frontend-dev << 'EOF'
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./
RUN npm ci --only=production

# Copy built application
COPY frontend/.next ./.next
COPY frontend/public ./public
COPY frontend/next.config.mjs ./
COPY frontend/tailwind.config.ts ./
COPY frontend/tsconfig.json ./
COPY frontend/components.json ./

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

# Start the application
CMD [\"npm\", \"start\"]
EOF

    echo '✓ Development Dockerfile created'
"

echo -e "${YELLOW}Step 6: Building and starting frontend container...${NC}"

run_on_vps "
    cd $DEPLOY_PATH
    
    # Stop existing frontend container
    docker stop agentic-frontend-dev 2>/dev/null || true
    docker rm agentic-frontend-dev 2>/dev/null || true
    
    # Build new frontend image
    docker build -f Dockerfile.frontend-dev -t agentic-frontend-dev:latest .
    
    # Start the frontend container
    docker run -d \
        --name agentic-frontend-dev \
        --network agentic-dev-network \
        -p 3001:3000 \
        --restart unless-stopped \
        -e NODE_ENV=development \
        -e NEXT_PUBLIC_API_URL=https://dev.consulting.sa/api \
        agentic-frontend-dev:latest
    
    echo '✓ Frontend container started'
"

echo -e "${YELLOW}Step 7: Waiting for container to be ready...${NC}"

run_on_vps "
    # Wait for container to start
    sleep 10
    
    # Check if container is running
    if docker ps | grep -q agentic-frontend-dev; then
        echo '✓ Frontend container is running'
    else
        echo '❌ Frontend container failed to start'
        docker logs agentic-frontend-dev
        exit 1
    fi
    
    # Wait for health check
    echo 'Waiting for health check...'
    for i in {1..20}; do
        if docker inspect agentic-frontend-dev | grep -q '\"Status\": \"healthy\"'; then
            echo '✓ Frontend container is healthy'
            break
        elif [ \$i -eq 20 ]; then
            echo '⚠ Health check timeout, but container is running'
            break
        else
            echo \"Waiting for health check... (\$i/20)\"
            sleep 5
        fi
    done
"

echo -e "${YELLOW}Step 8: Testing deployment...${NC}"

run_on_vps "
    echo 'Testing frontend deployment:'
    
    # Test direct access
    if curl -s -f --max-time 10 http://localhost:3001/ > /dev/null; then
        echo '✓ Frontend responding on port 3001'
    else
        echo '❌ Frontend not responding on port 3001'
        docker logs --tail 20 agentic-frontend-dev
    fi
    
    # Test through nginx
    if curl -s -f --max-time 10 -H 'Host: dev.consulting.sa' http://localhost/ > /dev/null; then
        echo '✓ Frontend accessible through nginx'
    else
        echo '❌ Frontend not accessible through nginx'
    fi
"

# Clean up local files
rm -f frontend-dev-deploy.tar.gz

echo
echo -e "${GREEN}🎉 Frontend Development Deployment Complete!${NC}"
echo
echo -e "${BLUE}=== ACCESS INFORMATION ===${NC}"
echo "🌐 Development Site: https://dev.consulting.sa/"
echo "🔧 Direct Frontend: http://217.79.255.54:3001/"
echo
echo -e "${BLUE}=== CONTAINER STATUS ===${NC}"

run_on_vps "
    echo 'Current frontend container status:'
    docker ps | grep agentic-frontend-dev || echo 'Container not found'
    
    echo
    echo 'Recent logs:'
    docker logs --tail 10 agentic-frontend-dev 2>/dev/null || echo 'No logs available'
"

echo
echo -e "${GREEN}Frontend deployment completed successfully!${NC}"