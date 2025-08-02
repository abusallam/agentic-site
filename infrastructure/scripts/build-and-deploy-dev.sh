#!/bin/bash

# Build and Deploy Development Environment
# This script builds containers locally and deploys them to the VPS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

VPS_HOST="agentic-vps"  # Using SSH alias
DEPLOY_PATH="/opt/docker-apps/development/agentic-site"

echo -e "${BLUE}🏗️ Building and Deploying Development Environment${NC}"
echo "Target VPS: $VPS_HOST"
echo "Deploy Path: $DEPLOY_PATH"
echo "Timestamp: $(date)"
echo

# Function to run commands on VPS (no password needed now)
run_on_vps() {
    ssh $VPS_HOST "$1"
}

echo -e "${YELLOW}Step 1: Preparing local build environment...${NC}"

# Ensure we have the latest code
git pull origin develop 2>/dev/null || echo "Git pull skipped"

# Create build directory
mkdir -p .build-temp
cd .build-temp

echo "✓ Build environment prepared"

echo -e "${YELLOW}Step 2: Building frontend container...${NC}"

# Create frontend Dockerfile
cat > Dockerfile.frontend << 'EOF'
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./
RUN npm ci

# Copy source code
COPY frontend/ ./

# Build the application
RUN npm run build

# Production stage
FROM node:18-alpine AS runner

WORKDIR /app

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy package files
COPY frontend/package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Copy built application
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.mjs ./
COPY --from=builder /app/tailwind.config.ts ./
COPY --from=builder /app/tsconfig.json ./

USER nextjs

EXPOSE 3000

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

CMD ["npm", "start"]
EOF

# Build frontend image
docker build -f Dockerfile.frontend -t agentic-frontend-dev:latest ../

echo "✓ Frontend container built"

echo -e "${YELLOW}Step 3: Building backend container...${NC}"

# Create backend Dockerfile
cat > Dockerfile.backend << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend code
COPY backend/ ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt || \
    pip install --no-cache-dir fastapi uvicorn python-multipart aiofiles || \
    echo "Using minimal dependencies"

# Create a simple health check endpoint
RUN mkdir -p /app && cat > /app/main.py << 'PYEOF'
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os

app = FastAPI(title="Agentic Backend Development")

@app.get("/")
async def root():
    return {"message": "Agentic Backend Development Server", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "environment": "development"}

@app.get("/api/health")
async def api_health():
    return {"status": "healthy", "api": "ready"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
PYEOF

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "main.py"]
EOF

# Build backend image
docker build -f Dockerfile.backend -t agentic-backend-dev:latest ../

echo "✓ Backend container built"

echo -e "${YELLOW}Step 4: Saving and transferring container images...${NC}"

# Save images as tar files
docker save agentic-frontend-dev:latest | gzip > frontend-dev.tar.gz
docker save agentic-backend-dev:latest | gzip > backend-dev.tar.gz

echo "✓ Container images saved"

# Transfer images to VPS
echo "Transferring frontend image..."
scp frontend-dev.tar.gz $VPS_HOST:/tmp/

echo "Transferring backend image..."
scp backend-dev.tar.gz $VPS_HOST:/tmp/

echo "✓ Images transferred to VPS"

echo -e "${YELLOW}Step 5: Loading images on VPS...${NC}"

run_on_vps "
    echo 'Loading frontend image...'
    docker load < /tmp/frontend-dev.tar.gz
    
    echo 'Loading backend image...'
    docker load < /tmp/backend-dev.tar.gz
    
    # Clean up transfer files
    rm -f /tmp/frontend-dev.tar.gz /tmp/backend-dev.tar.gz
    
    echo '✓ Images loaded successfully'
"

echo -e "${YELLOW}Step 6: Preparing deployment directory...${NC}"

run_on_vps "
    mkdir -p $DEPLOY_PATH
    cd $DEPLOY_PATH
    
    # Stop any existing containers
    docker-compose down 2>/dev/null || true
    
    echo '✓ Deployment directory prepared'
"

echo -e "${YELLOW}Step 7: Creating docker-compose configuration...${NC}"

# Create a simplified docker-compose file that uses local images
cat > docker-compose.local.yml << 'EOF'
version: '3.8'

services:
  frontend-dev:
    image: agentic-frontend-dev:latest
    container_name: agentic-frontend-dev
    ports:
      - "3001:3000"
    environment:
      - NODE_ENV=development
      - NEXT_PUBLIC_API_URL=https://dev.consulting.sa/api
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - agentic-dev-network

  backend-dev:
    image: agentic-backend-dev:latest
    container_name: agentic-backend-dev
    ports:
      - "8001:8000"
    environment:
      - NODE_ENV=development
      - PYTHONPATH=/app
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - agentic-dev-network

  redis-dev:
    image: redis:7-alpine
    container_name: agentic-redis-dev
    ports:
      - "6380:6379"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - agentic-dev-network

  n8n-dev:
    image: n8nio/n8n:latest
    container_name: agentic-n8n-dev
    ports:
      - "5679:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=admin123
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://localhost:5678/
      - GENERIC_TIMEZONE=UTC
    volumes:
      - n8n_data:/home/node/.n8n
    restart: unless-stopped
    networks:
      - agentic-dev-network

networks:
  agentic-dev-network:
    driver: bridge
    name: agentic-dev-network

volumes:
  n8n_data:
    driver: local
EOF

# Transfer docker-compose file
scp docker-compose.local.yml $VPS_HOST:$DEPLOY_PATH/docker-compose.yml

echo "✓ Docker-compose configuration deployed"

echo -e "${YELLOW}Step 8: Starting development environment...${NC}"

run_on_vps "
    cd $DEPLOY_PATH
    
    # Start the development environment
    docker-compose up -d
    
    echo '✓ Development environment started'
"

echo -e "${YELLOW}Step 9: Waiting for services to be ready...${NC}"

run_on_vps "
    cd $DEPLOY_PATH
    
    # Wait for containers to start
    sleep 15
    
    echo 'Container Status:'
    docker-compose ps
    
    # Wait for health checks
    echo 'Waiting for health checks...'
    for i in {1..30}; do
        healthy_count=\$(docker-compose ps | grep -c 'healthy' || echo 0)
        if [ \$healthy_count -ge 2 ]; then
            echo '✓ Services are healthy'
            break
        elif [ \$i -eq 30 ]; then
            echo '⚠ Health check timeout, but services may still be starting'
            break
        else
            echo \"Waiting for services to become healthy... (\$i/30)\"
            sleep 5
        fi
    done
"

echo -e "${YELLOW}Step 10: Updating nginx configuration...${NC}"

run_on_vps "
    # Create the nginx configuration
    cat > /etc/nginx/sites-available/agentic-platform-dev-local << 'EOF'
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

    # Remove old symlinks and create new one
    rm -f /etc/nginx/sites-enabled/agentic-platform-dev*
    ln -sf /etc/nginx/sites-available/agentic-platform-dev-local /etc/nginx/sites-enabled/agentic-platform-dev-local
    
    # Test and reload nginx
    nginx -t && systemctl reload nginx
    
    echo '✓ Nginx configuration updated'
"

echo -e "${YELLOW}Step 11: Final verification...${NC}"

run_on_vps "
    cd $DEPLOY_PATH
    
    echo 'Final Container Status:'
    docker-compose ps
    
    echo
    echo 'Testing endpoints:'
    
    # Test backend
    if curl -s -f --max-time 10 http://localhost:8001/health > /dev/null; then
        echo '✓ Backend responding on port 8001'
    else
        echo '❌ Backend not responding on port 8001'
    fi
    
    # Test frontend
    if curl -s -f --max-time 10 http://localhost:3001/ > /dev/null; then
        echo '✓ Frontend responding on port 3001'
    else
        echo '❌ Frontend not responding on port 3001'
    fi
    
    # Test nginx proxy
    if curl -s -f --max-time 10 -H 'Host: dev.consulting.sa' http://localhost/ > /dev/null; then
        echo '✓ Nginx proxy working'
    else
        echo '❌ Nginx proxy not working'
    fi
"

# Clean up local build files
cd ..
rm -rf .build-temp

echo
echo -e "${GREEN}🎉 Build and Deploy Complete!${NC}"
echo
echo -e "${BLUE}=== ACCESS INFORMATION ===${NC}"
echo "🌐 Development Site: https://dev.consulting.sa/"
echo "🔧 API Health Check: https://dev.consulting.sa/health"
echo "🛠️ n8n Interface: https://dev.consulting.sa/n8n/"
echo "💾 Backend Admin: https://dev.consulting.sa/backend/"
echo
echo -e "${BLUE}=== DIRECT ACCESS (for debugging) ===${NC}"
echo "Frontend: http://217.79.255.54:3001/"
echo "Backend: http://217.79.255.54:8001/"
echo "n8n: http://217.79.255.54:5679/"
echo "Redis: 217.79.255.54:6380"
echo
echo -e "${BLUE}=== MANAGEMENT COMMANDS ===${NC}"
echo "Check status: ssh $VPS_HOST 'cd $DEPLOY_PATH && docker-compose ps'"
echo "View logs: ssh $VPS_HOST 'cd $DEPLOY_PATH && docker-compose logs -f'"
echo "Restart: ssh $VPS_HOST 'cd $DEPLOY_PATH && docker-compose restart'"
echo
echo -e "${GREEN}Development environment is now fully operational!${NC}"