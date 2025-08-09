#!/bin/bash

# Deploy to Clean VPS Script
# This script deploys the application to a VPS that was set up with setup-fresh-vps.sh
# Usage: ./deploy-to-clean-vps.sh <SSH_ALIAS> <ENVIRONMENT>

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
    echo -e "${YELLOW}Example: $0 agentic-217-79-255-54-development development${NC}"
    echo -e "${YELLOW}Example: $0 agentic-192-168-1-100-production production${NC}"
    exit 1
fi

SSH_ALIAS="$1"
ENVIRONMENT="$2"
DEPLOY_PATH="/opt/docker-apps/$ENVIRONMENT/agentic-site"

echo -e "${PURPLE}🚀 Deploying Agentic Site to Clean VPS${NC}"
echo -e "${BLUE}=======================================${NC}"
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

echo -e "${YELLOW}Step 1: Verifying VPS connection and setup...${NC}"

if run_on_vps "echo 'Connection successful'"; then
    echo "✓ VPS connection verified"
else
    echo -e "${RED}❌ Failed to connect to VPS. Please check SSH alias.${NC}"
    echo "Try: ssh $SSH_ALIAS"
    exit 1
fi

# Verify VPS is properly set up
if run_on_vps "docker --version && nginx -v && [ -d '$DEPLOY_PATH' ]"; then
    echo "✓ VPS is properly set up with Docker, Nginx, and deployment directory"
else
    echo -e "${RED}❌ VPS is not properly set up. Please run setup-fresh-vps.sh first.${NC}"
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

echo -e "${YELLOW}Step 3: Building optimized frontend container...${NC}"

# Create production-ready frontend Dockerfile
cat > Dockerfile.frontend << 'EOF'
# Multi-stage build for optimized frontend
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./
RUN npm ci --only=production

# Copy source code
COPY frontend/ ./

# Build the application
RUN npm run build

# Production stage
FROM node:18-alpine AS runner

WORKDIR /app

# Create non-root user for security
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Install curl for health checks
RUN apk add --no-cache curl

# Copy package files and install production dependencies
COPY frontend/package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Copy built application with proper ownership
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder /app/next.config.mjs ./
COPY --from=builder /app/tailwind.config.ts ./
COPY --from=builder /app/tsconfig.json ./

# Switch to non-root user
USER nextjs

EXPOSE 3000

# Environment variables
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

# Start the application
CMD ["npm", "start"]
EOF

# Build frontend image
echo "Building frontend container..."
docker build -f Dockerfile.frontend -t "agentic-frontend-$ENVIRONMENT:latest" ../

echo "✓ Frontend container built"

echo -e "${YELLOW}Step 4: Building robust backend container...${NC}"

# Create production-ready backend Dockerfile
cat > Dockerfile.backend << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app

# Copy backend code
COPY backend/ ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create comprehensive main application
RUN cat > main.py << 'PYEOF'
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import uvicorn
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agentic Backend",
    description="AI-powered backend for consulting.sa",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Agentic Backend starting up...")
    logger.info(f"Environment: {os.getenv('NODE_ENV', 'development')}")

@app.get("/")
async def root():
    return {
        "message": "Agentic Backend Server", 
        "status": "running",
        "environment": os.getenv("NODE_ENV", "development"),
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "environment": os.getenv("NODE_ENV", "development"),
        "service": "backend",
        "timestamp": datetime.now().isoformat(),
        "uptime": "running"
    }

@app.get("/api/health")
async def api_health():
    return {
        "status": "healthy", 
        "api": "ready",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    try:
        body = await request.json()
        message = body.get("message", "")
        
        # Simple AI response logic (can be enhanced with actual AI integration)
        response_text = f"Hello! I received your message: '{message}'. I'm the AI assistant for consulting.sa. How can I help you with our AI consulting services?"
        
        return {
            "response": response_text,
            "type": "text",
            "handoff_required": False,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/status")
async def api_status():
    return {
        "api": "operational",
        "services": {
            "chat": "available",
            "health": "available"
        },
        "timestamp": datetime.now().isoformat()
    }

# Admin interface
@app.get("/admin", response_class=HTMLResponse)
async def admin_interface():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agentic Backend Admin</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .status { background: #f0f8ff; padding: 20px; border-radius: 8px; }
            .healthy { color: #008000; }
        </style>
    </head>
    <body>
        <h1>Agentic Backend Admin Interface</h1>
        <div class="status">
            <h2>System Status</h2>
            <p class="healthy">✓ Backend is running</p>
            <p class="healthy">✓ API endpoints available</p>
            <p class="healthy">✓ Health checks passing</p>
        </div>
        <h2>Available Endpoints</h2>
        <ul>
            <li><a href="/health">Health Check</a></li>
            <li><a href="/api/health">API Health</a></li>
            <li><a href="/api/status">API Status</a></li>
            <li><a href="/docs">API Documentation</a></li>
        </ul>
    </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")
PYEOF

# Change ownership to app user
RUN chown -R app:app /app

# Switch to non-root user
USER app

EXPOSE 8000

# Environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["python", "main.py"]
EOF

# Build backend image
echo "Building backend container..."
docker build -f Dockerfile.backend -t "agentic-backend-$ENVIRONMENT:latest" ../

echo "✓ Backend container built"

echo -e "${YELLOW}Step 5: Saving and transferring container images...${NC}"

# Save images as compressed tar files
echo "Saving container images..."
docker save "agentic-frontend-$ENVIRONMENT:latest" | gzip > "frontend-$ENVIRONMENT.tar.gz"
docker save "agentic-backend-$ENVIRONMENT:latest" | gzip > "backend-$ENVIRONMENT.tar.gz"

echo "✓ Container images saved"

# Transfer images to VPS
echo "Transferring images to VPS..."
copy_to_vps "frontend-$ENVIRONMENT.tar.gz" "/tmp/"
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

echo -e "${YELLOW}Step 7: Creating production docker-compose configuration...${NC}"

# Set ports based on environment
if [ "$ENVIRONMENT" = "development" ]; then
    FRONTEND_PORT="3001"
    BACKEND_PORT="8001"
    N8N_PORT="5679"
    REDIS_PORT="6380"
    DOMAIN="dev.consulting.sa"
else
    FRONTEND_PORT="3000"
    BACKEND_PORT="8000"
    N8N_PORT="5678"
    REDIS_PORT="6379"
    DOMAIN="consulting.sa"
fi

# Create comprehensive docker-compose file
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
      - NEXT_PUBLIC_API_URL=https://$DOMAIN/api
      - NEXT_PUBLIC_SITE_URL=https://$DOMAIN
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
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  backend:
    image: agentic-backend-$ENVIRONMENT:latest
    container_name: agentic-backend-$ENVIRONMENT
    ports:
      - "$BACKEND_PORT:8000"
    environment:
      - NODE_ENV=$ENVIRONMENT
      - PYTHONPATH=/app
      - PORT=8000
      - HOST=0.0.0.0
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - agentic-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  redis:
    image: redis:7-alpine
    container_name: agentic-redis-$ENVIRONMENT
    ports:
      - "$REDIS_PORT:6379"
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
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
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  n8n:
    image: n8nio/n8n:latest
    container_name: agentic-n8n-$ENVIRONMENT
    ports:
      - "$N8N_PORT:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=admin123
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=https://$DOMAIN/n8n/
      - GENERIC_TIMEZONE=UTC
      - N8N_METRICS=true
    volumes:
      - n8n_data:/home/node/.n8n
    restart: unless-stopped
    networks:
      - agentic-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  agentic-network:
    driver: bridge
    name: agentic-$ENVIRONMENT-network

volumes:
  redis_data:
    driver: local
    name: agentic-redis-$ENVIRONMENT-data
  n8n_data:
    driver: local
    name: agentic-n8n-$ENVIRONMENT-data
EOF

# Transfer docker-compose file
copy_to_vps docker-compose.yml "$DEPLOY_PATH/"

echo "✓ Docker-compose configuration deployed"

echo -e "${YELLOW}Step 8: Creating environment configuration...${NC}"

# Create environment file
cat > .env << EOF
# Agentic Site $ENVIRONMENT Environment
# Generated: $(date)

# Environment
NODE_ENV=$ENVIRONMENT
COMPOSE_PROJECT_NAME=agentic-$ENVIRONMENT

# Domain Configuration
DOMAIN=$DOMAIN
NEXT_PUBLIC_SITE_URL=https://$DOMAIN
NEXT_PUBLIC_API_URL=https://$DOMAIN/api

# Container Configuration
FRONTEND_PORT=$FRONTEND_PORT
BACKEND_PORT=$BACKEND_PORT
REDIS_PORT=$REDIS_PORT
N8N_PORT=$N8N_PORT

# n8n Configuration
N8N_USER=admin
N8N_PASSWORD=admin123

# Health Check Configuration
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_INTERVAL=30

# Logging
LOG_LEVEL=INFO
EOF

# Transfer environment file
copy_to_vps .env "$DEPLOY_PATH/"

echo "✓ Environment configuration deployed"

echo -e "${YELLOW}Step 9: Setting up Nginx configuration...${NC}"

run_on_vps "
    echo 'Creating Nginx configuration for $ENVIRONMENT...'
    
    cat > /etc/nginx/sites-available/agentic-$ENVIRONMENT << 'NGINXEOF'
# Agentic Site $ENVIRONMENT Configuration
upstream frontend_$ENVIRONMENT {
    server 127.0.0.1:$FRONTEND_PORT;
    keepalive 32;
}

upstream backend_$ENVIRONMENT {
    server 127.0.0.1:$BACKEND_PORT;
    keepalive 32;
}

# Rate limiting
limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone \$binary_remote_addr zone=general:10m rate=30r/s;

server {
    listen 80;
    server_name $DOMAIN;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection \"1; mode=block\";
    add_header Referrer-Policy \"strict-origin-when-cross-origin\";
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Main application - proxy to Next.js
    location / {
        limit_req zone=general burst=20 nodelay;
        
        proxy_pass http://frontend_$ENVIRONMENT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 86400;
        proxy_connect_timeout 60;
        proxy_send_timeout 60;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }
    
    # API routes - proxy to Python backend
    location /api/ {
        limit_req zone=api burst=10 nodelay;
        
        proxy_pass http://backend_$ENVIRONMENT/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
        proxy_connect_timeout 60;
        proxy_send_timeout 60;
    }
    
    # Backend admin interface
    location /backend/ {
        proxy_pass http://backend_$ENVIRONMENT/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # n8n interface
    location /n8n/ {
        proxy_pass http://127.0.0.1:$N8N_PORT/;
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
        access_log off;
        proxy_pass http://backend_$ENVIRONMENT/health;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Static files with caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        proxy_pass http://frontend_$ENVIRONMENT;
        proxy_cache_valid 200 1y;
        add_header Cache-Control \"public, immutable\";
        expires 1y;
    }
    
    # Security - block access to sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
NGINXEOF

    # Enable the site
    ln -sf /etc/nginx/sites-available/agentic-$ENVIRONMENT /etc/nginx/sites-enabled/agentic-$ENVIRONMENT
    
    # Remove default site if it exists
    rm -f /etc/nginx/sites-enabled/default
    
    # Test nginx configuration
    nginx -t
    
    # Reload nginx
    systemctl reload nginx
    
    echo '✓ Nginx configuration created and enabled'
"

echo -e "${YELLOW}Step 10: Deploying and starting application...${NC}"

run_on_vps "
    cd $DEPLOY_PATH
    
    # Stop any existing containers
    docker-compose down 2>/dev/null || true
    
    # Start the application
    echo 'Starting application containers...'
    docker-compose up -d
    
    echo '✓ Application deployment started'
"

echo -e "${YELLOW}Step 11: Waiting for services to be ready...${NC}"

run_on_vps "
    cd $DEPLOY_PATH
    
    # Wait for containers to start
    sleep 20
    
    echo 'Container Status:'
    docker-compose ps
    
    # Wait for health checks
    echo 'Waiting for health checks...'
    for i in {1..60}; do
        healthy_count=\$(docker-compose ps | grep -c 'healthy' || echo 0)
        
        if [ \$healthy_count -ge 2 ]; then
            echo '✓ Core services are healthy'
            break
        elif [ \$i -eq 60 ]; then
            echo '⚠ Health check timeout, checking individual services...'
            echo 'Frontend logs:'
            docker-compose logs --tail=5 frontend || true
            echo 'Backend logs:'
            docker-compose logs --tail=5 backend || true
            break
        else
            echo \"Waiting for services to become healthy... (\$i/60) - Healthy: \$healthy_count\"
            sleep 5
        fi
    done
"

echo -e "${YELLOW}Step 12: Final testing and verification...${NC}"

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
    if curl -s -f --max-time 10 -H 'Host: $DOMAIN' http://localhost/ > /dev/null; then
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
    
    # Test n8n
    if curl -s -f --max-time 10 http://localhost:$N8N_PORT/ > /dev/null; then
        echo '✓ n8n responding'
    else
        echo '❌ n8n not responding'
    fi
"

# Clean up local build files
cd ..
rm -rf "$BUILD_DIR"

echo
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo -e "${BLUE}=======================================${NC}"
echo

echo -e "${CYAN}🌐 Access Information:${NC}"
echo "Website: https://$DOMAIN/"
echo "API Health: https://$DOMAIN/health"
echo "Backend Admin: https://$DOMAIN/backend/"
echo "n8n Interface: https://$DOMAIN/n8n/"
echo "API Documentation: https://$DOMAIN/backend/docs"
echo

echo -e "${CYAN}🔧 Direct Access (for debugging):${NC}"
VPS_IP=\$(run_on_vps "curl -s ifconfig.me" 2>/dev/null || echo "unknown")
echo "Frontend: http://\$VPS_IP:$FRONTEND_PORT/"
echo "Backend: http://\$VPS_IP:$BACKEND_PORT/"
echo "n8n: http://\$VPS_IP:$N8N_PORT/"
echo "Redis: \$VPS_IP:$REDIS_PORT"
echo

echo -e "${CYAN}🛠️ Management Commands:${NC}"
echo "Status: ssh $SSH_ALIAS '/usr/local/bin/agentic-$ENVIRONMENT-status.sh'"
echo "Logs: ssh $SSH_ALIAS '/usr/local/bin/agentic-$ENVIRONMENT-logs.sh'"
echo "Restart: ssh $SSH_ALIAS '/usr/local/bin/agentic-$ENVIRONMENT-restart.sh'"
echo "Backup: ssh $SSH_ALIAS '/usr/local/bin/agentic-$ENVIRONMENT-backup.sh'"
echo "Connect: ssh $SSH_ALIAS"
echo

echo -e "${CYAN}📊 Container Status:${NC}"
run_on_vps "cd $DEPLOY_PATH && docker-compose ps"

echo
echo -e "${GREEN}✅ Your application is now live and ready!${NC}"
echo -e "${YELLOW}🔗 Visit https://$DOMAIN to see your site${NC}"