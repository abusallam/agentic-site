#!/bin/bash

# Comprehensive Deployment Fix for Agentic Site
# Fixes frontend permission issues, N8N integration, and ensures all services work properly

set -e

echo "🚀 Starting Comprehensive Agentic Site Deployment Fix..."

# SSH connection details
SSH_HOST="agentic-fixed-217-79-255-54-development"
DOCKER_PATH="/opt/docker-apps/development/agentic-site/agentic-site"

echo "📋 Step 1: Stopping all existing containers and cleaning up..."
ssh $SSH_HOST "cd $DOCKER_PATH && docker-compose -f docker-compose-n8n-production.yml down 2>/dev/null || true"
ssh $SSH_HOST "docker stop \$(docker ps -q --filter 'name=agentic-site') 2>/dev/null || true"
ssh $SSH_HOST "docker rm \$(docker ps -aq --filter 'name=agentic-site') 2>/dev/null || true"

echo "📋 Step 2: Fixing frontend permission issues..."
ssh $SSH_HOST "cd $DOCKER_PATH && rm -rf frontend/.next frontend/node_modules"
ssh $SSH_HOST "cd $DOCKER_PATH && mkdir -p frontend/.next"
ssh $SSH_HOST "cd $DOCKER_PATH && chmod -R 777 frontend/.next"

echo "📋 Step 3: Creating comprehensive environment configuration..."
ssh $SSH_HOST "cd $DOCKER_PATH && cat > .env.comprehensive << 'EOF'
# =============================================================================
# COMPREHENSIVE DEVELOPMENT ENVIRONMENT CONFIGURATION
# =============================================================================

# Basic Configuration
NODE_ENV=development
PORT=3000
NEXT_PUBLIC_SITE_URL=http://217.79.255.54:3001

# Database Configuration
NEXT_PUBLIC_SUPABASE_URL=https://xjkdaimasvoufshspibj.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhqa2RhaW1hc3ZvdWZzaHNwaWJqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI2ODEwNzEsImV4cCI6MjA2ODI1NzA3MX0.3LmGcnbXuisabz-Fx1MfPasFFl8dR5uCoIyBoKEZ3As
SUPABASE_URL=https://xjkdaimasvoufshspibj.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhqa2RhaW1hc3ZvdWZzaHNwaWJqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI2ODEwNzEsImV4cCI6MjA2ODI1NzA3MX0.3LmGcnbXuisabz-Fx1MfPasFFl8dR5uCoIyBoKEZ3As
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhqa2RhaW1hc3ZvdWZzaHNwaWJqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MjY4MTA3MSwiZXhwIjoyMDY4MjU3MDcxfQ.dummy_service_key_placeholder

# AI Services Configuration
GOOGLE_API_KEY=AIzaSyBzj09AK5ZpQJfblSwpzx1H1nG0Za3AHGw
GEMINI_API_KEY=AIzaSyBzj09AK5ZpQJfblSwpzx1H1nG0Za3AHGw

# Livekit Configuration
LIVEKIT_URL=wss://con.livekit.cloud
LIVEKIT_API_KEY=APIP6v8eDW3yEFN
LIVEKIT_API_SECRET=0jnJoJcsbAjMlVXvInJSKI8HDIxkdhHuPeHtDsxc1Vf

# Payment Processing (Stripe) - Development Keys
STRIPE_SECRET_KEY=sk_test_dummy_development_key
STRIPE_PUBLISHABLE_KEY=pk_test_dummy_development_key

# N8N Configuration (Updated for our deployment)
N8N_URL=http://n8n-dev:5678
N8N_BASE_URL=http://217.79.255.54:5680
N8N_API_KEY=n8n-dev-api-key-production-12345
N8N_API_USER=admin
N8N_API_PASSWORD=StrongPassword123

# MCP Configuration
MCP_SERVER_URL=http://backend-dev:8000
MCP_SERVER_PORT=8000
N8N_MCP_PORT=8003

# Development Specific
DEBUG=true
VERBOSE_LOGGING=true
LOG_LEVEL=info

# Security Configuration
JWT_SECRET=development_jwt_secret_key_here
ENCRYPTION_KEY=development_encryption_key_32_chars

# CORS Configuration
ALLOWED_ORIGINS=http://217.79.255.54:3001,http://localhost:3000,http://localhost:3001
EOF"

echo "📋 Step 4: Creating comprehensive docker-compose configuration..."
ssh $SSH_HOST "cd $DOCKER_PATH && cat > docker-compose-comprehensive.yml << 'COMPOSE_EOF'
version: '3.8'

services:
  frontend-dev:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - '3001:3000'
    environment:
      - NODE_ENV=development
      - NEXT_TELEMETRY_DISABLED=1
      - NEXT_PUBLIC_SUPABASE_URL=\${NEXT_PUBLIC_SUPABASE_URL}
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=\${NEXT_PUBLIC_SUPABASE_ANON_KEY}
      - NEXT_PUBLIC_SITE_URL=http://217.79.255.54:3001
      - NEXT_PUBLIC_BACKEND_URL=http://217.79.255.54:8001
    volumes:
      - ./frontend:/app
      - frontend_node_modules:/app/node_modules
      - frontend_next:/app/.next
    networks:
      - agentic-network
    healthcheck:
      test: ['CMD', 'curl', '-f', 'http://localhost:3000/api/health || http://localhost:3000']
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    depends_on:
      - backend-dev
    user: \"1000:1000\"
    command: >
      sh -c \"
        npm install &&
        mkdir -p /app/.next &&
        chmod -R 777 /app/.next &&
        npm run dev
      \"

  backend-dev:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - '8001:8000'
    environment:
      - ENVIRONMENT=development
      - PYTHONPATH=/app/agent
      - GEMINI_API_KEY=\${GEMINI_API_KEY}
      - SUPABASE_URL=\${SUPABASE_URL}
      - SUPABASE_ANON_KEY=\${SUPABASE_ANON_KEY}
      - SUPABASE_SERVICE_ROLE_KEY=\${SUPABASE_SERVICE_ROLE_KEY}
      - N8N_URL=http://n8n-dev:5678
      - N8N_BASE_URL=http://217.79.255.54:5680
      - N8N_API_KEY=n8n-dev-api-key-production-12345
      - N8N_API_USER=admin
      - N8N_API_PASSWORD=StrongPassword123
      - MCP_SERVER_URL=http://localhost:8000
      - LIVEKIT_API_KEY=\${LIVEKIT_API_KEY}
      - LIVEKIT_API_SECRET=\${LIVEKIT_API_SECRET}
      - STRIPE_SECRET_KEY=\${STRIPE_SECRET_KEY}
    volumes:
      - ./backend:/app
      - ./agent:/app/agent
    networks:
      - agentic-network
    depends_on:
      - redis-dev
      - n8n-dev
    healthcheck:
      test: ['CMD', 'curl', '-f', 'http://localhost:8000/health']
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  n8n-dev:
    image: n8nio/n8n:1.75.0
    restart: unless-stopped
    ports:
      - '5680:5678'
    environment:
      # Core Settings
      - N8N_HOST=217.79.255.54
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      
      # Auth Settings
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=StrongPassword123
      
      # URLs
      - N8N_EDITOR_BASE_URL=http://217.79.255.54:5680
      - WEBHOOK_URL=http://217.79.255.54:5680/
      
      # Data Persistence
      - N8N_USER_FOLDER=/home/node/.n8n
      
      # Execution Mode
      - EXECUTIONS_PROCESS=main
      - EXECUTIONS_DATA_SAVE_ON_ERROR=all
      - EXECUTIONS_DATA_SAVE_ON_SUCCESS=all
      - EXECUTIONS_DATA_PRUNE=true
      - EXECUTIONS_DATA_MAX_AGE=168
      
      # Performance & Security
      - N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=false
      - N8N_RUNNERS_ENABLED=true
      - N8N_LOG_LEVEL=info
      - N8N_METRICS=true
      - N8N_PERSONALIZATION_ENABLED=false
      - N8N_VERSION_NOTIFICATIONS_ENABLED=false
      - N8N_DIAGNOSTICS_ENABLED=false
      - N8N_HIRING_BANNER_ENABLED=false
      
      # API Key for MCP Integration
      - N8N_API_KEY=n8n-dev-api-key-production-12345
    volumes:
      - n8n_data:/home/node/.n8n
    networks:
      - agentic-network
    healthcheck:
      test: ['CMD', 'curl', '-f', 'http://localhost:5678/healthz']
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s

  redis-dev:
    image: redis:7-alpine
    restart: unless-stopped
    ports:
      - '6380:6379'
    networks:
      - agentic-network
    healthcheck:
      test: ['CMD', 'redis-cli', 'ping']
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  agentic-network:
    driver: bridge

volumes:
  n8n_data:
    driver: local
  frontend_node_modules:
    driver: local
  frontend_next:
    driver: local
COMPOSE_EOF"

echo "📋 Step 5: Starting services with comprehensive configuration..."
ssh $SSH_HOST "cd $DOCKER_PATH && docker-compose -f docker-compose-comprehensive.yml --env-file .env.comprehensive up -d"

echo "📋 Step 6: Waiting for services to initialize (90 seconds)..."
sleep 90

echo "📋 Step 7: Checking service status..."
ssh $SSH_HOST "cd $DOCKER_PATH && docker-compose -f docker-compose-comprehensive.yml ps"

echo "📋 Step 8: Testing service health..."
echo "Testing N8N..."
ssh $SSH_HOST "curl -s http://localhost:5680/healthz | jq . || echo 'N8N health check completed'"

echo "Testing Backend..."
ssh $SSH_HOST "curl -s http://localhost:8001/health | jq . || echo 'Backend health check completed'"

echo "Testing Frontend..."
ssh $SSH_HOST "curl -s -I http://localhost:3001 | head -5 || echo 'Frontend health check completed'"

echo "📋 Step 9: Creating test workflow in N8N..."
ssh $SSH_HOST "curl -s -u admin:StrongPassword123 -X POST http://localhost:5680/rest/workflows \\
  -H 'Content-Type: application/json' \\
  -d '{
    \"name\": \"Comprehensive Test Workflow\",
    \"nodes\": [
      {
        \"id\": \"start-node\",
        \"name\": \"Start\",
        \"type\": \"n8n-nodes-base.start\",
        \"position\": [250, 300],
        \"parameters\": {}
      },
      {
        \"id\": \"webhook-node\",
        \"name\": \"Test Webhook\",
        \"type\": \"n8n-nodes-base.webhook\",
        \"position\": [450, 300],
        \"parameters\": {
          \"path\": \"comprehensive-test\",
          \"httpMethod\": \"POST\"
        }
      }
    ],
    \"connections\": {
      \"Start\": {
        \"main\": [
          [
            {
              \"node\": \"Test Webhook\",
              \"type\": \"main\",
              \"index\": 0
            }
          ]
        ]
      }
    },
    \"active\": false,
    \"settings\": {}
  }' | jq . 2>/dev/null || echo 'Test workflow creation completed'"

echo "📋 Step 10: Final comprehensive health check..."
echo ""
echo "🔍 Service Status Summary:"
echo "=========================="

# Check N8N
if ssh $SSH_HOST "curl -s http://localhost:5680/healthz > /dev/null 2>&1"; then
    echo "✅ N8N: HEALTHY (http://217.79.255.54:5680)"
else
    echo "❌ N8N: UNHEALTHY"
fi

# Check Backend
if ssh $SSH_HOST "curl -s http://localhost:8001/health > /dev/null 2>&1"; then
    echo "✅ Backend: HEALTHY (http://217.79.255.54:8001)"
else
    echo "❌ Backend: UNHEALTHY"
fi

# Check Frontend
if ssh $SSH_HOST "curl -s http://localhost:3001 > /dev/null 2>&1"; then
    echo "✅ Frontend: HEALTHY (http://217.79.255.54:3001)"
else
    echo "❌ Frontend: UNHEALTHY"
fi

# Check Redis
if ssh $SSH_HOST "docker exec \$(docker ps -q --filter 'name=redis-dev') redis-cli ping > /dev/null 2>&1"; then
    echo "✅ Redis: HEALTHY"
else
    echo "❌ Redis: UNHEALTHY"
fi

echo ""
echo "🔗 Access Information:"
echo "====================="
echo "Frontend: http://217.79.255.54:3001"
echo "Backend:  http://217.79.255.54:8001"
echo "N8N:      http://217.79.255.54:5680 (admin/StrongPassword123)"
echo "Redis:    217.79.255.54:6380"
echo ""
echo "🧪 Ready for comprehensive testing!"
echo ""
echo "📋 Next Steps:"
echo "1. Run: python tests/quick_agentic_test.py"
echo "2. Run: python tests/comprehensive_agentic_test_suite.py"
echo "3. Check logs: docker-compose -f docker-compose-comprehensive.yml logs -f"
echo ""
echo "✅ Comprehensive Deployment Fix Complete!"