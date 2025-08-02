#!/bin/bash
set -e

# Development Environment Fixed Deployment Script
# This script deploys the complete development environment with full frontend functionality
# Based on the fixed development branch that now matches main branch functionality

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
VPS_HOST="217.79.255.54"
VPS_USER="root"
VPS_PASSWORD="xxXNCpx9Cz"

echo -e "${PURPLE}🚀 Development Environment Fixed Deployment${NC}"
echo -e "${BLUE}Target VPS: $VPS_HOST${NC}"
echo -e "${BLUE}User: $VPS_USER${NC}"
echo -e "${BLUE}Strategy: Clean → Build → Deploy → Verify${NC}"
echo ""

# Function to run commands on VPS using sshpass
run_on_vps() {
    local command="$1"
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "$command"
}

# Function to check if a service is responding
check_service() {
    local url="$1"
    local service_name="$2"
    if run_on_vps "curl -f -s $url > /dev/null 2>&1"; then
        echo -e "${GREEN}✓ $service_name is responding${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ $service_name is not responding${NC}"
        return 1
    fi
}

# Test VPS connection
echo -e "${BLUE}🔗 Testing VPS connection...${NC}"
if run_on_vps "echo 'Connection successful'" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ VPS connection established${NC}"
else
    echo -e "${RED}❌ Failed to connect to VPS${NC}"
    exit 1
fi

# Phase 1: Local Build Verification
echo ""
echo -e "${PURPLE}📋 Phase 1: Local Build Verification${NC}"
echo -e "${YELLOW}Building frontend locally to ensure it works...${NC}"

cd frontend
if npm run build; then
    echo -e "${GREEN}✓ Frontend builds successfully${NC}"
else
    echo -e "${RED}❌ Frontend build failed${NC}"
    exit 1
fi
cd ..

# Phase 2: Clean Development Environment
echo ""
echo -e "${PURPLE}📋 Phase 2: Clean Development Environment${NC}"
echo -e "${YELLOW}Cleaning up existing development containers...${NC}"

run_on_vps "docker stop \$(docker ps -q --filter name=agentic-*-dev) 2>/dev/null || true"
run_on_vps "docker rm \$(docker ps -aq --filter name=agentic-*-dev) 2>/dev/null || true"
run_on_vps "docker system prune -f"
echo -e "${GREEN}✓ Development environment cleaned${NC}"

# Phase 3: Create Development Directory Structure
echo ""
echo -e "${PURPLE}📋 Phase 3: Setup Development Directory${NC}"
echo -e "${YELLOW}Creating development directory structure...${NC}"

run_on_vps "mkdir -p /opt/agentic-development"
run_on_vps "cd /opt/agentic-development && rm -rf *"
echo -e "${GREEN}✓ Development directory prepared${NC}"

# Phase 4: Deploy Docker Compose Configuration
echo ""
echo -e "${PURPLE}📋 Phase 4: Deploy Docker Compose Configuration${NC}"
echo -e "${YELLOW}Creating development docker-compose configuration...${NC}"

# Create docker-compose.development.yml on VPS
run_on_vps "cat > /opt/agentic-development/docker-compose.development.yml" << 'EOF'
version: '3.8'

services:
  # Frontend Service - Next.js Development
  frontend:
    build:
      context: /opt/agentic-development
      dockerfile: Dockerfile.frontend
    container_name: agentic-frontend-development
    ports:
      - "3002:3000"
    environment:
      - NODE_ENV=development
      - NEXT_TELEMETRY_DISABLED=1
      - PORT=3000
      - HOSTNAME=0.0.0.0
      
      # Supabase Configuration
      - NEXT_PUBLIC_SUPABASE_URL=${NEXT_PUBLIC_SUPABASE_URL}
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=${NEXT_PUBLIC_SUPABASE_ANON_KEY}
      
      # Contact Configuration
      - NEXT_PUBLIC_CONTACT_EMAIL=${NEXT_PUBLIC_CONTACT_EMAIL:-asim@consulting.sa}
      
      # Analytics (disabled for dev)
      - NEXT_PUBLIC_GA_ID=
      
      # Development Site Configuration
      - NEXT_PUBLIC_SITE_URL=${DEV_SITE_URL:-https://dev.consulting.sa}
      - NEXT_PUBLIC_ADMIN_URL=${DEV_ADMIN_URL:-https://dev.consulting.sa/api}
      - NEXT_PUBLIC_BACKEND_URL=http://backend:8000
      - FORCE_HTTPS=true
      
    depends_on:
      - backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - agentic-network

  # Backend Service - Python Agent Development
  backend:
    build:
      context: /opt/agentic-development
      dockerfile: Dockerfile.backend
    container_name: agentic-backend-development
    ports:
      - "8002:8000"
    environment:
      - NODE_ENV=development
      - PYTHONPATH=/app/agent
      - ADK_AGENT_PORT=8000
      - ADK_LOG_LEVEL=DEBUG
      
      # Database Configuration
      - NEXT_PUBLIC_SUPABASE_URL=${NEXT_PUBLIC_SUPABASE_URL}
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=${NEXT_PUBLIC_SUPABASE_ANON_KEY}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
      
      # AI Services
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      
      # Payment Integration (development keys)
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLISHABLE_KEY}
      - STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET}
      
      # Communication Services
      - LIVEKIT_URL=${LIVEKIT_URL}
      - LIVEKIT_API_KEY=${LIVEKIT_API_KEY}
      - LIVEKIT_API_SECRET=${LIVEKIT_API_SECRET}
      
      # Workflow Automation
      - N8N_URL=${N8N_URL}
      - N8N_BASE_URL=${N8N_BASE_URL}
      - N8N_API_KEY=${N8N_API_KEY}
      
      # MCP Server Configuration
      - MCP_SERVER_URL=${MCP_SERVER_URL:-http://localhost:8000}
      - MCP_SERVER_PORT=${MCP_SERVER_PORT:-8000}
      - N8N_MCP_PORT=${N8N_MCP_PORT:-8003}
      
      # GitHub Integration
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - agentic-network

  # Redis Cache for Development
  redis:
    image: redis:7-alpine
    container_name: agentic-redis-development
    ports:
      - "6381:6379"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - agentic-network

  # n8n Workflow Automation for Development
  n8n:
    image: n8nio/n8n:latest
    container_name: agentic-n8n-development
    ports:
      - "5680:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER:-admin}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD:-admin123}
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
    name: agentic-development-network

volumes:
  redis_data:
    driver: local
  n8n_data:
    driver: local
EOF

echo -e "${GREEN}✓ Docker Compose configuration created${NC}"

# Phase 5: Create Dockerfiles
echo ""
echo -e "${PURPLE}📋 Phase 5: Create Dockerfiles${NC}"
echo -e "${YELLOW}Creating Dockerfile.frontend...${NC}"

run_on_vps "cat > /opt/agentic-development/Dockerfile.frontend" << 'EOF'
# Multi-stage build for Next.js frontend
FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY frontend/package.json ./
RUN npm install

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY frontend/ .

# Set build-time environment variables
ARG NEXT_PUBLIC_SUPABASE_URL
ARG NEXT_PUBLIC_SUPABASE_ANON_KEY
ARG NODE_ENV=production

ENV NEXT_PUBLIC_SUPABASE_URL=$NEXT_PUBLIC_SUPABASE_URL
ENV NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEXT_PUBLIC_SUPABASE_ANON_KEY
ENV NODE_ENV=$NODE_ENV
ENV NEXT_TELEMETRY_DISABLED=1

# Build the application
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Install curl for health checks
RUN apk add --no-cache curl

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Copy the built application
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nextjs:nodejs /app/package.json ./package.json

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/ || exit 1

CMD ["npm", "start"]
EOF

echo -e "${YELLOW}Creating Dockerfile.backend...${NC}"

run_on_vps "cat > /opt/agentic-development/Dockerfile.backend" << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy backend files
COPY backend/ ./backend/

# Fix the dotenv path in main.py
RUN sed -i 's|load_dotenv(dotenv_path="../.env")|load_dotenv(dotenv_path="/app/.env")|g' backend/agent/main.py

# Install Python dependencies
RUN cd backend && uv sync
RUN cd backend/agent && uv sync
RUN pip install python-dotenv

# Set environment variables
ENV PYTHONPATH=/app/backend/agent
ENV ADK_AGENT_PORT=8000

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the agent
CMD ["uv", "run", "--python", "python", "backend/agent/main.py"]
EOF

echo -e "${GREEN}✓ Dockerfiles created${NC}"

# Phase 6: Copy Project Files
echo ""
echo -e "${PURPLE}📋 Phase 6: Copy Project Files${NC}"
echo -e "${YELLOW}Copying project files to VPS...${NC}"

# Create a temporary tar file
tar --exclude='.git' --exclude='node_modules' --exclude='.next' --exclude='.swc' -czf /tmp/agentic-development.tar.gz .

# Copy to VPS
sshpass -p "$VPS_PASSWORD" scp -o StrictHostKeyChecking=no /tmp/agentic-development.tar.gz "$VPS_USER@$VPS_HOST:/opt/agentic-development/"

# Extract on VPS
run_on_vps "cd /opt/agentic-development && tar -xzf agentic-development.tar.gz && rm agentic-development.tar.gz"

# Clean up local tar
rm /tmp/agentic-development.tar.gz

echo -e "${GREEN}✓ Project files copied to VPS${NC}"

# Phase 7: Create Environment File
echo ""
echo -e "${PURPLE}📋 Phase 7: Create Environment File${NC}"
echo -e "${YELLOW}Creating environment configuration...${NC}"

run_on_vps "cat > /opt/agentic-development/.env" << 'EOF'
# Development Environment Configuration
ENVIRONMENT=development

# Supabase Configuration (use your actual values)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# AI Services (use your actual keys)
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Payment Integration (use test keys for development)
STRIPE_SECRET_KEY=sk_test_your-stripe-key
STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret

# Communication Services
LIVEKIT_URL=https://your-livekit-url
LIVEKIT_API_KEY=your-livekit-key
LIVEKIT_API_SECRET=your-livekit-secret

# n8n Configuration
N8N_URL=http://localhost:5678
N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=your-n8n-key
N8N_USER=admin
N8N_PASSWORD=admin123

# MCP Configuration
MCP_SERVER_URL=http://localhost:8000
MCP_SERVER_PORT=8000
N8N_MCP_PORT=8003

# GitHub Integration
GITHUB_TOKEN=your-github-token

# Development Configuration
DEV_SITE_URL=https://dev.consulting.sa
DEV_ADMIN_URL=https://dev.consulting.sa/api
EOF

echo -e "${GREEN}✓ Environment file created${NC}"

# Phase 8: Build and Deploy
echo ""
echo -e "${PURPLE}📋 Phase 8: Build and Deploy${NC}"
echo -e "${YELLOW}Building and starting containers...${NC}"

run_on_vps "cd /opt/agentic-development && docker-compose -f docker-compose.development.yml build"
run_on_vps "cd /opt/agentic-development && docker-compose -f docker-compose.development.yml up -d"

echo -e "${GREEN}✓ Containers built and started${NC}"

# Phase 9: Wait for Services
echo ""
echo -e "${PURPLE}📋 Phase 9: Wait for Services${NC}"
echo -e "${YELLOW}Waiting for services to start...${NC}"

sleep 30

# Phase 10: Health Checks
echo ""
echo -e "${PURPLE}📋 Phase 10: Health Checks${NC}"

check_service "http://localhost:8002/health" "Backend API"
check_service "http://localhost:3002/" "Frontend"
check_service "http://localhost:5680/" "n8n Workflows"

# Check Redis
if run_on_vps "docker exec agentic-redis-development redis-cli ping" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis is responding${NC}"
else
    echo -e "${YELLOW}⚠ Redis health check failed${NC}"
fi

# Phase 11: Update Nginx Configuration
echo ""
echo -e "${PURPLE}📋 Phase 11: Update Nginx Configuration${NC}"
echo -e "${YELLOW}Updating nginx configuration for development...${NC}"

run_on_vps "cat > /etc/nginx/sites-available/dev.consulting.sa" << 'EOF'
server {
    listen 80;
    server_name dev.consulting.sa;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

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
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Frontend - Next.js application
    location / {
        proxy_pass http://localhost:3002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8002/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }

    # Backend health check
    location /health {
        proxy_pass http://localhost:8002/health;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # n8n Workflow Automation
    location /n8n/ {
        proxy_pass http://localhost:5680/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }

    # WebSocket support for real-time features
    location /ws/ {
        proxy_pass http://localhost:8002/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Error pages
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
    
    location = /50x.html {
        root /usr/share/nginx/html;
    }

    # Logging
    access_log /var/log/nginx/dev.consulting.sa.access.log;
    error_log /var/log/nginx/dev.consulting.sa.error.log;
}
EOF

# Enable the site
run_on_vps "ln -sf /etc/nginx/sites-available/dev.consulting.sa /etc/nginx/sites-enabled/"
run_on_vps "nginx -t && systemctl reload nginx"

echo -e "${GREEN}✓ Nginx configuration updated${NC}"

# Phase 12: Final Verification
echo ""
echo -e "${PURPLE}📋 Phase 12: Final Verification${NC}"

echo -e "${YELLOW}Testing external endpoints...${NC}"
check_service "https://dev.consulting.sa/" "Development Frontend"
check_service "https://dev.consulting.sa/api/health" "Development API"
check_service "https://dev.consulting.sa/n8n/" "Development n8n"

# Show container status
echo ""
echo -e "${BLUE}📊 Container Status:${NC}"
run_on_vps "docker ps --filter name=agentic-*-development --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

echo ""
echo -e "${GREEN}🎉 Development Environment Deployment Complete!${NC}"
echo -e "${BLUE}Frontend: https://dev.consulting.sa${NC}"
echo -e "${BLUE}Backend API: https://dev.consulting.sa/api/health${NC}"
echo -e "${BLUE}n8n Workflows: https://dev.consulting.sa/n8n/${NC}"
echo ""
echo -e "${YELLOW}Note: Update the .env file on the VPS with your actual API keys and credentials.${NC}" 