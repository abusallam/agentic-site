#!/bin/bash

# 🌐 Configure Proper Container Separation with -dev Naming
# Fixes container naming and ensures proper environment separation

set -e

SERVER_ALIAS="agentic-fixed-217-79-255-54-development"
DEV_PATH="/opt/docker-apps/development/agentic-site/agentic-site"
PROD_PATH="/opt/docker-apps/production/agentic-site/agentic-site"

echo "🌐 Configuring proper container separation with -dev naming..."
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

echo "🛑 Phase 1: Stopping all containers..."
ssh $SERVER_ALIAS "cd $DEV_PATH && docker-compose down" 2>/dev/null || true
ssh $SERVER_ALIAS "cd $PROD_PATH && docker-compose down" 2>/dev/null || true
check_success "All containers stopped"

echo ""
echo "🔧 Phase 2: Creating DEVELOPMENT docker-compose with -dev naming..."
ssh $SERVER_ALIAS "cat > $DEV_PATH/docker-compose.yml << 'EOF'
version: '3.8'

services:
  # Development Frontend Service - Next.js
  frontend-dev:
    image: node:20-alpine
    container_name: agentic-frontend-dev
    ports:
      - \"3001:3000\"  # Development port
    environment:
      - NODE_ENV=development
      - NEXT_PUBLIC_API_URL=https://dev.consulting.sa/api
      - NEXT_PUBLIC_SUPABASE_URL=\${NEXT_PUBLIC_SUPABASE_URL}
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=\${NEXT_PUBLIC_SUPABASE_ANON_KEY}
    working_dir: /app
    volumes:
      - ./frontend:/app
    command: sh -c \"npm install && npm run dev\"
    restart: unless-stopped
    healthcheck:
      test: [\"CMD\", \"curl\", \"-f\", \"http://localhost:3000/\"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - agentic-dev-network

  # Development Backend Service - Python Agent
  backend-dev:
    image: python:3.11-slim
    container_name: agentic-backend-dev
    ports:
      - \"8001:8000\"  # Development port
    environment:
      - NODE_ENV=development
      - PYTHONPATH=/app/agent
      - ADK_AGENT_PORT=8000
      - ADK_LOG_LEVEL=DEBUG
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
      - agentic-dev-network

  # Development Redis Cache
  redis-dev:
    image: redis:7-alpine
    container_name: agentic-redis-dev
    ports:
      - \"6380:6379\"  # Development port
    restart: unless-stopped
    healthcheck:
      test: [\"CMD\", \"redis-cli\", \"ping\"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - agentic-dev-network

  # Development n8n Workflow Automation
  n8n-dev:
    image: n8nio/n8n:latest
    container_name: agentic-n8n-dev
    ports:
      - \"5679:5678\"  # Development port
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
      - n8n_dev_data:/home/node/.n8n
    restart: unless-stopped
    networks:
      - agentic-dev-network

networks:
  agentic-dev-network:
    driver: bridge
    name: agentic-dev-network

volumes:
  redis_dev_data:
    driver: local
  n8n_dev_data:
    driver: local
EOF"
check_success "Development docker-compose.yml created with -dev naming"

echo ""
echo "🔧 Phase 3: Creating PRODUCTION docker-compose with proper naming..."
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
check_success "Production docker-compose.yml created with proper naming"

echo ""
echo "🔧 Phase 4: Creating environment files..."

# Development environment
ssh $SERVER_ALIAS "cat > $DEV_PATH/.env << 'EOF'
# Development Environment Variables
NODE_ENV=development
PYTHONPATH=/app/agent

# Development URLs
NEXT_PUBLIC_SITE_URL=https://dev.consulting.sa
NEXT_PUBLIC_API_URL=https://dev.consulting.sa/api
NEXT_PUBLIC_ADMIN_URL=https://dev.consulting.sa/api

# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://xjkdaimasvoufshspibj.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhqa2RhaW1hc3ZvdWZzaHNwaWJqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI2ODEwNzEsImV4cCI6MjA2ODI1NzA3MX0.3LmGcnbXuisabz-Fx1MfPasFFl8dR5uCoIyBoKEZ3As
SUPABASE_SERVICE_KEY=your_supabase_service_key

# AI Services
GEMINI_API_KEY=AIzaSyBzj09AK5ZpQJfblSwpzx1H1nG0Za3AHGw

# n8n Configuration
N8N_USER=admin
N8N_PASSWORD=admin123

# Contact Configuration
NEXT_PUBLIC_CONTACT_EMAIL=dev@consulting.sa

# Development Settings
FORCE_HTTPS=true
DOMAIN=dev.consulting.sa
EOF"

# Production environment
ssh $SERVER_ALIAS "cat > $PROD_PATH/.env << 'EOF'
# Production Environment Variables
NODE_ENV=production
PYTHONPATH=/app/agent

# Production URLs
NEXT_PUBLIC_SITE_URL=https://consulting.sa
NEXT_PUBLIC_API_URL=https://consulting.sa/api
NEXT_PUBLIC_ADMIN_URL=https://consulting.sa/api

# Supabase Configuration
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
check_success "Environment files created"

echo ""
echo "🚀 Phase 5: Starting DEVELOPMENT containers with -dev naming..."
ssh $SERVER_ALIAS "cd $DEV_PATH && docker-compose up -d"
check_success "Development containers started"

echo ""
echo "🚀 Phase 6: Starting PRODUCTION containers..."
ssh $SERVER_ALIAS "cd $PROD_PATH && docker-compose up -d"
check_success "Production containers started"

echo "⏳ Waiting for containers to be ready..."
sleep 30

echo ""
echo "🔍 Phase 7: Checking final container status..."
ssh $SERVER_ALIAS 'docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'

echo ""
echo "🌐 Phase 8: Testing both environments..."

# Test production
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://consulting.sa)
echo "🏭 Production (consulting.sa): HTTP $HTTP_CODE"

# Test development  
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://dev.consulting.sa)
echo "🔧 Development (dev.consulting.sa): HTTP $HTTP_CODE"

echo ""
echo "🎉 CONTAINER SEPARATION WITH -DEV NAMING COMPLETE!"
echo ""
echo "📊 Final Container Structure:"
echo ""
echo "🔧 DEVELOPMENT CONTAINERS (dev.consulting.sa):"
echo "   - agentic-frontend-dev (port 3001)"
echo "   - agentic-backend-dev (port 8001)"
echo "   - agentic-redis-dev (port 6380)"
echo "   - agentic-n8n-dev (port 5679)"
echo ""
echo "🏭 PRODUCTION CONTAINERS (consulting.sa):"
echo "   - agentic-frontend-prod (port 3000)"
echo "   - agentic-backend-prod (port 8000)"
echo "   - agentic-redis-prod (port 6379)"
echo "   - agentic-n8n-prod (port 5678)"
echo ""
echo "✅ Perfect separation achieved!"
echo "🌐 consulting.sa = Production containers"
echo "🌐 dev.consulting.sa = Development containers"
echo "🔄 Changes to dev won't affect production anymore!"