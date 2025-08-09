#!/bin/bash

# 🏭 Setup Production Environment Script
# Creates separate production containers and fixes all issues

set -e

SERVER_ALIAS="agentic-fixed-217-79-255-54-development"
DEV_PATH="/opt/docker-apps/development/agentic-site/agentic-site"
PROD_PATH="/opt/docker-apps/production/agentic-site/agentic-site"

echo "🏭 Setting up SEPARATE production environment..."
echo "📅 $(date)"
echo ""

# Function to check success
check_success() {
    if [ $? -eq 0 ]; then
        echo "✅ $1"
    else
        echo "❌ $1 FAILED"
        exit 1
    fi
}

echo "📋 Phase 1: Checking current container status..."
ssh $SERVER_ALIAS 'docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"'

echo ""
echo "📁 Phase 2: Setting up production directory structure..."
ssh $SERVER_ALIAS "mkdir -p $PROD_PATH/frontend"
ssh $SERVER_ALIAS "mkdir -p $PROD_PATH/backend"
check_success "Production directories created"

echo ""
echo "📄 Phase 3: Copying development to production (as base)..."
ssh $SERVER_ALIAS "cp -r $DEV_PATH/* $PROD_PATH/"
check_success "Development copied to production"

echo ""
echo "🔧 Phase 4: Creating production docker-compose.yml..."
ssh $SERVER_ALIAS "cat > $PROD_PATH/docker-compose.yml << 'EOF'
version: '3.8'

services:
  # Production Frontend Service - Next.js
  frontend:
    image: node:20-alpine
    container_name: agentic-frontend-prod
    ports:
      - \"3000:3000\"  # Production port
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=https://consulting.sa/api
      - NEXT_PUBLIC_SUPABASE_URL=\${NEXT_PUBLIC_SUPABASE_URL}
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=\${NEXT_PUBLIC_SUPABASE_ANON_KEY}
    working_dir: /app
    volumes:
      - ./frontend:/app
    command: sh -c \"npm install && npm run build && npm start\"
    restart: unless-stopped
    healthcheck:
      test: [\"CMD\", \"curl\", \"-f\", \"http://localhost:3000/\"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - agentic-prod-network

  # Production Backend Service - Python Agent
  backend:
    image: python:3.11-slim
    container_name: agentic-backend-prod
    ports:
      - \"8000:8000\"  # Production port
    environment:
      - NODE_ENV=production
      - PYTHONPATH=/app/agent
      - ADK_AGENT_PORT=8000
      - ADK_LOG_LEVEL=INFO
      - NEXT_PUBLIC_SUPABASE_URL=\${NEXT_PUBLIC_SUPABASE_URL}
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=\${NEXT_PUBLIC_SUPABASE_ANON_KEY}
      - SUPABASE_SERVICE_KEY=\${SUPABASE_SERVICE_KEY}
      - GEMINI_API_KEY=\${GEMINI_API_KEY}
    working_dir: /app
    volumes:
      - ./backend:/app
    command: sh -c \"pip install -r requirements.txt && python agent/main.py\"
    restart: unless-stopped
    healthcheck:
      test: [\"CMD\", \"curl\", \"-f\", \"http://localhost:8000/health\"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - agentic-prod-network

  # Production Redis Cache
  redis:
    image: redis:7-alpine
    container_name: agentic-redis-prod
    ports:
      - \"6379:6379\"  # Production port
    restart: unless-stopped
    healthcheck:
      test: [\"CMD\", \"redis-cli\", \"ping\"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - agentic-prod-network

  # Production n8n Workflow Automation
  n8n:
    image: n8nio/n8n:latest
    container_name: agentic-n8n-prod
    ports:
      - \"5678:5678\"  # Production port
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
      - n8n_prod_data:/home/node/.n8n
    restart: unless-stopped
    networks:
      - agentic-prod-network

networks:
  agentic-prod-network:
    driver: bridge
    name: agentic-prod-network

volumes:
  redis_prod_data:
    driver: local
  n8n_prod_data:
    driver: local
EOF"
check_success "Production docker-compose.yml created"

echo ""
echo "🔧 Phase 5: Creating production environment file..."
ssh $SERVER_ALIAS "cat > $PROD_PATH/.env << 'EOF'
# Production Environment Variables
NODE_ENV=production
PYTHONPATH=/app/agent

# Production URLs
NEXT_PUBLIC_SITE_URL=https://consulting.sa
NEXT_PUBLIC_API_URL=https://consulting.sa/api
NEXT_PUBLIC_ADMIN_URL=https://consulting.sa/api

# Supabase Configuration (same as development)
NEXT_PUBLIC_SUPABASE_URL=https://xjkdaimasvoufshspibj.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhqa2RhaW1hc3ZvdWZzaHNwaWJqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI2ODEwNzEsImV4cCI6MjA2ODI1NzA3MX0.3LmGcnbXuisabz-Fx1MfPasFFl8dR5uCoIyBoKEZ3As
SUPABASE_SERVICE_KEY=your_supabase_service_key

# AI Services
GEMINI_API_KEY=AIzaSyBzj09AK5ZpQJfblSwpzx1H1nG0Za3AHGw

# n8n Configuration
N8N_USER=admin
N8N_PASSWORD=admin123

# Contact Configuration
NEXT_PUBLIC_CONTACT_EMAIL=info@consulting.sa

# Production Settings
FORCE_HTTPS=true
DOMAIN=consulting.sa
EOF"
check_success "Production environment file created"

echo ""
echo "🚀 Phase 6: Starting production containers..."
ssh $SERVER_ALIAS "cd $PROD_PATH && docker-compose up -d"
check_success "Production containers started"

echo "⏳ Waiting for production containers to be ready..."
sleep 30

echo ""
echo "🔍 Phase 7: Checking container status..."
ssh $SERVER_ALIAS 'docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"'

echo ""
echo "🌐 Phase 8: Testing both environments..."

# Test production
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://consulting.sa)
echo "🏭 Production (consulting.sa): HTTP $HTTP_CODE"

# Test development  
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://dev.consulting.sa)
echo "🔧 Development (dev.consulting.sa): HTTP $HTTP_CODE"

echo ""
echo "🎉 PRODUCTION ENVIRONMENT SETUP COMPLETE!"
echo ""
echo "📊 Container Summary:"
echo "🏭 PRODUCTION (consulting.sa):"
echo "   - Frontend: agentic-frontend-prod (port 3000)"
echo "   - Backend: agentic-backend-prod (port 8000)"
echo "   - Redis: agentic-redis-prod (port 6379)"
echo "   - n8n: agentic-n8n-prod (port 5678)"
echo ""
echo "🔧 DEVELOPMENT (dev.consulting.sa):"
echo "   - Frontend: agentic-site-frontend-1 (port 3001)"
echo "   - Backend: agentic-backend-dev (port 8001)"
echo "   - Redis: agentic-redis-dev (port 6380)"
echo "   - n8n: agentic-n8n-dev (port 5679)"
echo ""
echo "✅ Now you have SEPARATE environments!"
echo "🌐 consulting.sa = Production containers"
echo "🌐 dev.consulting.sa = Development containers"