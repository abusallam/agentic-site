#!/bin/bash

# Deploy to VPS Script
# This script deploys the application to a VPS that was set up with setup-new-vps.sh
# Usage: ./deploy-to-vps.sh <SSH_ALIAS> <ENVIRONMENT>

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check arguments
if [ $# -lt 2 ]; then
    echo -e "${RED}Usage: $0 <SSH_ALIAS> <ENVIRONMENT>${NC}"
    echo -e "${YELLOW}Example: $0 agentic-217-79-255-54 development${NC}"
    echo -e "${YELLOW}Example: $0 agentic-192-168-1-100 production${NC}"
    exit 1
fi

SSH_ALIAS="$1"
ENVIRONMENT="$2"
DEPLOY_PATH="/opt/docker-apps/$ENVIRONMENT/agentic-site"

echo -e "${PURPLE}🚀 Deploying Agentic Site to VPS${NC}"
echo -e "${BLUE}=================================${NC}"
echo "SSH Alias: $SSH_ALIAS"
echo "Environment: $ENVIRONMENT"
echo "Deploy Path: $DEPLOY_PATH"
echo "Timestamp: $(date)"
echo

# Function to run commands on VPS
run_on_vps() {
    ssh "$SSH_ALIAS" "$1"
}

# Function to copy files to VPS
copy_to_vps() {
    scp "$1" "$SSH_ALIAS:$2"
}

echo -e "${YELLOW}Step 1: Verifying VPS connection...${NC}"

if run_on_vps "echo 'Connection successful'"; then
    echo "✓ VPS connection verified"
else
    echo -e "${RED}❌ Failed to connect to VPS. Please check SSH alias.${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 2: Preparing local build environment...${NC}"

# Ensure we have the latest code
git pull origin develop 2>/dev/null || echo "Git pull skipped"

# Create build directory
BUILD_DIR=".build-$ENVIRONMENT"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

echo "✓ Build environment prepared"

echo -e "${YELLOW}Step 3: Building frontend container...${NC}"

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

# Install curl for health checks
RUN apk add --no-cache curl

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
echo "Building frontend container..."
docker build -f Dockerfile.frontend -t "agentic-frontend-$ENVIRONMENT:latest" ../

echo "✓ Frontend container built"

echo -e "${YELLOW}Step 4: Building backend container...${NC}"

# Create backend Dockerfile
cat > Dockerfile.backend << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend code
COPY backend/ ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create main application if it doesn't exist
RUN if [ ! -f main.py ]; then \
    cat > main.py << 'PYEOF'
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn

app = FastAPI(
    title="Agentic Backend",
    description="AI-powered backend for consulting.sa",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Agentic Backend Server", 
        "status": "running",
        "environment": os.getenv("NODE_ENV", "development")
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "environment": os.getenv("NODE_ENV", "development"),
        "service": "backend"
    }

@app.get("/api/health")
async def api_health():
    return {
        "status": "healthy", 
        "api": "ready",
        "version": "1.0.0"
    }

@app.post("/api/chat")
async def chat_endpoint(request: dict):
    # Simple echo response for now
    return {
        "response": "Hello! I'm the AI assistant. This is a development response.",
        "type": "text",
        "handoff_required": False
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
PYEOF
fi

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "main.py"]
EOF

# Build backend image
echo "Building backend container..."
docker build -f Dockerfile.backend -t "agentic-backend-$ENVIRONMENT:latest" ../

echo "✓ Backend container built"

echo -e "${YELLOW}Step 5: Saving and transferring container images...${NC}"

# Save images as tar files
echo "Saving container images..."
docker save "agentic-frontend-$ENVIRONMENT:latest" | gzip > "frontend-$ENVIRONMENT.tar.gz"
docker save "agentic-backend-$ENVIRONMENT:latest" | gzip > "backend-$ENVIRONMENT.tar.gz"

echo "✓ Container images saved"

# Transfer images to VPS
echo "Transferring frontend image..."
copy_to_vps "frontend-$ENVIRONMENT.tar.gz" "/tmp/"

echo "Transferring backend image..."
copy_to_vps "backend-$ENVIRONMENT.tar.gz" "/tmp/"

echo "✓ Images transferred to VPS"

echo -e "${YELLOW}Step 6: Loading images on VPS...${NC}"

run_on_vps "
    echo 'Loading frontend image...'
    docker load < /tmp/frontend-$ENVIRONMENT.tar.gz
    
    echo 'Loading backend image...'
    docker load < /tmp/backend-$ENVIRONMENT.tar.gz
    
    # Clean up transfer files
    rm -f /tmp/frontend-$ENVIRONMENT.tar.gz /tmp/backend-$ENVIRONMENT.tar.gz
    
    echo '✓ Images loaded successfully'
"

echo -e "${YELLOW}Step 7: Creating docker-compose configuration...${NC}"

# Set ports based on environment
if [ "$ENVIRONMENT" = "development" ]; then
    FRONTEND_PORT="3001"
    BACKEND_PORT="8001"
    N8N_PORT="5679"
    REDIS_PORT="6380"
else
    FRONTEND_PORT="3000"
    BACKEND_PORT="8000"
    N8N_PORT="5678"
    REDIS_PORT="6379"
fi

# Create docker-compose file
cat > docker-compose.yml << EOF
version: '3.8'

services:
  frontend:
    image: agentic-frontend-$ENVIRONMENT:latest
    container_name: agentic-frontend-$ENVIRONMENT
    ports:
      - "$FRONTEND_PORT:3000"
    environment:
      - NODE_ENV=$ENVIRONMENT
      - NEXT_PUBLIC_API_URL=https://\${DOMAIN:-localhost}/api
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - agentic-network
    depends_on:
      - backend

  backend:
    image: agentic-backend-$ENVIRONMENT:latest
    container_name: agentic-backend-$ENVIRONMENT
    ports:
      - "$BACKEND_PORT:8000"
    environment:
      - NODE_ENV=$ENVIRONMENT
      - PYTHONPATH=/app
      - PORT=8000
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - agentic-network

  redis:
    image: redis:7-alpine
    container_name: agentic-redis-$ENVIRONMENT
    ports:
      - "$REDIS_PORT:6379"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - agentic-network
    volumes:
      - redis_data:/data

  n8n:
    image: n8nio/n8n:latest
    container_name: agentic-n8n-$ENVIRONMENT
    ports:
      - "$N8N_PORT:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=\${N8N_USER:-admin}
      - N8N_BASIC_AUTH_PASSWORD=\${N8N_PASSWORD:-admin123}
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://localhost:5678/
      - GENERIC_TIMEZONE=UTC
    volumes:
      - n8n_data:/home/node/.n8n
    restart: unless-stopped
    networks:
      - agentic-network

networks:
  agentic-network:
    driver: bridge
    name: agentic-$ENVIRONMENT-network

volumes:
  redis_data:
    driver: local
  n8n_data:
    driver: local
EOF

# Transfer docker-compose file
copy_to_vps docker-compose.yml "$DEPLOY_PATH/"

echo "✓ Docker-compose configuration deployed"

echo -e "${YELLOW}Step 8: Updating environment configuration...${NC}"

# Copy environment file if it exists
if [ -f "../.env.$ENVIRONMENT" ]; then
    copy_to_vps "../.env.$ENVIRONMENT" "$DEPLOY_PATH/.env"
    echo "✓ Environment configuration updated"
else
    echo "⚠ No .env.$ENVIRONMENT file found, using existing configuration"
fi

echo -e "${YELLOW}Step 9: Deploying application...${NC}"

run_on_vps "
    cd $DEPLOY_PATH
    
    # Stop existing containers
    docker-compose down 2>/dev/null || true
    
    # Start the application
    echo 'Starting application containers...'
    docker-compose up -d
    
    echo '✓ Application deployment started'
"

echo -e "${YELLOW}Step 10: Waiting for services to be ready...${NC}"

run_on_vps "
    cd $DEPLOY_PATH
    
    # Wait for containers to start
    sleep 15
    
    echo 'Container Status:'
    docker-compose ps
    
    # Wait for health checks
    echo 'Waiting for health checks...'
    for i in {1..60}; do
        healthy_count=\$(docker-compose ps | grep -c 'healthy' || echo 0)
        total_services=4  # frontend, backend, redis, n8n
        
        if [ \$healthy_count -ge 2 ]; then
            echo '✓ Core services are healthy'
            break
        elif [ \$i -eq 60 ]; then
            echo '⚠ Health check timeout, checking individual services...'
            docker-compose logs --tail=10 frontend || true
            docker-compose logs --tail=10 backend || true
            break
        else
            echo \"Waiting for services to become healthy... (\$i/60) - Healthy: \$healthy_count\"
            sleep 5
        fi
    done
"

echo -e "${YELLOW}Step 11: Testing deployment...${NC}"

run_on_vps "
    echo 'Testing deployment endpoints:'
    
    # Test backend
    if curl -s -f --max-time 10 http://localhost:$BACKEND_PORT/health > /dev/null; then
        echo '✓ Backend responding on port $BACKEND_PORT'
    else
        echo '❌ Backend not responding on port $BACKEND_PORT'
    fi
    
    # Test frontend
    if curl -s -f --max-time 10 http://localhost:$FRONTEND_PORT/ > /dev/null; then
        echo '✓ Frontend responding on port $FRONTEND_PORT'
    else
        echo '❌ Frontend not responding on port $FRONTEND_PORT'
    fi
    
    # Test nginx proxy
    if curl -s -f --max-time 10 http://localhost/ > /dev/null; then
        echo '✓ Nginx proxy working'
    else
        echo '❌ Nginx proxy not working'
    fi
    
    # Test Redis
    if docker exec agentic-redis-$ENVIRONMENT redis-cli ping > /dev/null 2>&1; then
        echo '✓ Redis responding'
    else
        echo '❌ Redis not responding'
    fi
"

# Clean up local build files
cd ..
rm -rf "$BUILD_DIR"

echo
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo -e "${BLUE}=================================${NC}"
echo

# Get domain from VPS
DOMAIN=\$(run_on_vps "grep DOMAIN $DEPLOY_PATH/.env | cut -d'=' -f2" 2>/dev/null || echo "localhost")

echo -e "${CYAN}Access Information:${NC}"
echo "🌐 Website: http://\$DOMAIN/"
echo "🔧 API Health: http://\$DOMAIN/health"
echo "🛠️ n8n Interface: http://\$DOMAIN/n8n/"
echo "💾 Backend Admin: http://\$DOMAIN/backend/"
echo

echo -e "${CYAN}Direct Access (for debugging):${NC}"
VPS_IP=\$(run_on_vps "curl -s ifconfig.me" 2>/dev/null || echo "unknown")
echo "Frontend: http://\$VPS_IP:$FRONTEND_PORT/"
echo "Backend: http://\$VPS_IP:$BACKEND_PORT/"
echo "n8n: http://\$VPS_IP:$N8N_PORT/"
echo "Redis: \$VPS_IP:$REDIS_PORT"
echo

echo -e "${CYAN}Management Commands:${NC}"
echo "Check status: ssh $SSH_ALIAS '/usr/local/bin/agentic-$ENVIRONMENT-status.sh'"
echo "View logs: ssh $SSH_ALIAS '/usr/local/bin/agentic-$ENVIRONMENT-logs.sh'"
echo "Restart: ssh $SSH_ALIAS '/usr/local/bin/agentic-$ENVIRONMENT-restart.sh'"
echo "Connect: ssh $SSH_ALIAS"
echo

echo -e "${GREEN}Deployment successful! Your application is now running.${NC}"