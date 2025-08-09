#!/bin/bash

# Direct VPS Deployment - Build and Deploy on VPS
# Usage: ./deploy-direct-to-vps.sh <SSH_ALIAS> <ENVIRONMENT>

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Check arguments
if [ $# -lt 2 ]; then
    echo -e "${RED}Usage: $0 <SSH_ALIAS> <ENVIRONMENT>${NC}"
    echo -e "${YELLOW}Example: $0 agentic-fixed-217-79-255-54-development development${NC}"
    exit 1
fi

SSH_ALIAS="$1"
ENVIRONMENT="$2"
DEPLOY_PATH="/opt/docker-apps/$ENVIRONMENT/agentic-site"

echo -e "${BOLD}${PURPLE}🚀 Direct VPS Deployment${NC}"
echo -e "${BLUE}========================${NC}"
echo "SSH Alias: $SSH_ALIAS"
echo "Environment: $ENVIRONMENT"
echo "Deploy Path: $DEPLOY_PATH"
echo "Timestamp: $(date)"
echo

echo -e "${YELLOW}Step 1: Verifying VPS connection...${NC}"
if ssh "$SSH_ALIAS" 'echo "Connection successful"'; then
    echo "✓ VPS connection verified"
else
    echo -e "${RED}❌ Failed to connect to VPS${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 2: Cloning repository directly on VPS...${NC}"
ssh "$SSH_ALIAS" "
    echo 'Preparing deployment directory...'
    cd $DEPLOY_PATH
    
    # Remove existing code if present
    rm -rf agentic-site-temp
    
    # Clone fresh repository
    echo 'Cloning repository...'
    git clone https://github.com/abusallam/agentic-site.git agentic-site-temp
    cd agentic-site-temp
    git checkout develop
    
    echo '✓ Repository cloned successfully'
"

echo -e "${YELLOW}Step 3: Creating production docker-compose configuration...${NC}"
ssh "$SSH_ALIAS" "
    cd $DEPLOY_PATH/agentic-site-temp
    
    # Create production docker-compose.yml
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - '3001:3000'
    environment:
      - NODE_ENV=development
      - NEXT_PUBLIC_API_URL=http://localhost:8001
      - NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    restart: unless-stopped
    networks:
      - agentic-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - '8001:8000'
    environment:
      - ENVIRONMENT=development
      - SUPABASE_URL=https://your-project.supabase.co
      - SUPABASE_KEY=your-service-role-key
      - GEMINI_API_KEY=your-gemini-key
    volumes:
      - ./backend:/app
      - /app/.venv
    restart: unless-stopped
    networks:
      - agentic-network

  redis:
    image: redis:7-alpine
    ports:
      - '6380:6379'
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - agentic-network

  n8n:
    image: n8nio/n8n:latest
    ports:
      - '5679:5678'
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=admin123
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - NODE_ENV=development
    volumes:
      - n8n_data:/home/node/.n8n
    restart: unless-stopped
    networks:
      - agentic-network

volumes:
  redis_data:
  n8n_data:

networks:
  agentic-network:
    driver: bridge
EOF

    echo '✓ Docker Compose configuration created'
"

echo -e "${YELLOW}Step 4: Creating frontend Dockerfile...${NC}"
ssh "$SSH_ALIAS" "
    cd $DEPLOY_PATH/agentic-site-temp/frontend
    
    # Create optimized Dockerfile for frontend
    cat > Dockerfile << 'EOF'
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json package-lock.json* ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build the application
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=development
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME=\"0.0.0.0\"

CMD [\"node\", \"server.js\"]
EOF

    echo '✓ Frontend Dockerfile created'
"

echo -e "${YELLOW}Step 5: Creating backend Dockerfile...${NC}"
ssh "$SSH_ALIAS" "
    cd $DEPLOY_PATH/agentic-site-temp/backend
    
    # Create optimized Dockerfile for backend
    cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster Python package management
RUN pip install uv

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Run the application
CMD [\"python\", \"-m\", \"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\", \"--reload\"]
EOF

    echo '✓ Backend Dockerfile created'
"

echo -e "${YELLOW}Step 6: Building and starting services...${NC}"
ssh "$SSH_ALIAS" "
    cd $DEPLOY_PATH/agentic-site-temp
    
    echo 'Stopping any existing containers...'
    docker-compose down 2>/dev/null || true
    
    echo 'Building and starting services...'
    docker-compose up -d --build
    
    echo 'Waiting for services to start...'
    sleep 30
    
    echo '✓ Services started'
"

echo -e "${YELLOW}Step 7: Verifying deployment...${NC}"
ssh "$SSH_ALIAS" "
    cd $DEPLOY_PATH/agentic-site-temp
    
    echo 'Container Status:'
    docker-compose ps
    
    echo
    echo 'Service Health Check:'
    
    # Check frontend
    if curl -s http://localhost:3001 > /dev/null; then
        echo '✅ Frontend is responding on port 3001'
    else
        echo '❌ Frontend not responding on port 3001'
    fi
    
    # Check backend
    if curl -s http://localhost:8001 > /dev/null; then
        echo '✅ Backend is responding on port 8001'
    else
        echo '❌ Backend not responding on port 8001'
    fi
    
    # Check Redis
    if docker-compose exec -T redis redis-cli ping | grep -q PONG; then
        echo '✅ Redis is responding'
    else
        echo '❌ Redis not responding'
    fi
    
    # Check n8n
    if curl -s http://localhost:5679 > /dev/null; then
        echo '✅ n8n is responding on port 5679'
    else
        echo '❌ n8n not responding on port 5679'
    fi
"

echo -e "${YELLOW}Step 8: Moving to production location...${NC}"
ssh "$SSH_ALIAS" "
    cd $DEPLOY_PATH
    
    # Stop services in temp location
    cd agentic-site-temp
    docker-compose down
    
    # Move to production location
    cd ..
    rm -rf agentic-site-old
    if [ -d agentic-site ]; then
        mv agentic-site agentic-site-old
    fi
    mv agentic-site-temp agentic-site
    
    # Start services in production location
    cd agentic-site
    docker-compose up -d
    
    echo '✓ Moved to production location and restarted services'
"

echo
echo -e "${BOLD}${GREEN}🎉 Direct VPS Deployment Complete!${NC}"
echo -e "${BLUE}===================================${NC}"
echo
echo -e "${BOLD}${CYAN}🌐 Access URLs:${NC}"
echo "Frontend: http://$(ssh "$SSH_ALIAS" 'curl -s ifconfig.me'):3001"
echo "Backend: http://$(ssh "$SSH_ALIAS" 'curl -s ifconfig.me'):8001"
echo "n8n: http://$(ssh "$SSH_ALIAS" 'curl -s ifconfig.me'):5679"
echo "Redis: $(ssh "$SSH_ALIAS" 'curl -s ifconfig.me'):6380"
echo
echo -e "${BOLD}${CYAN}🛠️ Management Commands:${NC}"
echo "Status: ssh $SSH_ALIAS 'cd $DEPLOY_PATH/agentic-site && docker-compose ps'"
echo "Logs: ssh $SSH_ALIAS 'cd $DEPLOY_PATH/agentic-site && docker-compose logs -f'"
echo "Restart: ssh $SSH_ALIAS 'cd $DEPLOY_PATH/agentic-site && docker-compose restart'"
echo "Stop: ssh $SSH_ALIAS 'cd $DEPLOY_PATH/agentic-site && docker-compose down'"
echo
echo -e "${BOLD}${GREEN}✅ Application is now running on the VPS!${NC}"