#!/bin/bash

# Fix N8N Deployment Script
# This script fixes N8N deployment issues and sets up proper configuration

set -e

echo "🔧 Fixing N8N Deployment Issues..."

# SSH connection details
SSH_HOST="agentic-fixed-217-79-255-54-development"
DOCKER_PATH="/opt/docker-apps/development/agentic-site/agentic-site"

echo "📋 Step 1: Checking current N8N status..."
ssh $SSH_HOST "cd $DOCKER_PATH && docker ps | grep n8n"

echo "📋 Step 2: Stopping N8N container..."
ssh $SSH_HOST "cd $DOCKER_PATH && docker-compose stop agentic-n8n-dev || true"

echo "📋 Step 3: Removing N8N container and volumes..."
ssh $SSH_HOST "cd $DOCKER_PATH && docker-compose rm -f agentic-n8n-dev || true"
ssh $SSH_HOST "cd $DOCKER_PATH && docker volume rm agentic-site_n8n_data || true"

echo "📋 Step 4: Creating N8N configuration directory..."
ssh $SSH_HOST "mkdir -p /opt/docker-apps/development/agentic-site/n8n-data"
ssh $SSH_HOST "chmod 755 /opt/docker-apps/development/agentic-site/n8n-data"

echo "📋 Step 5: Creating N8N environment configuration..."
ssh $SSH_HOST "cat > /opt/docker-apps/development/agentic-site/n8n.env << 'EOF'
# N8N Configuration
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=admin123
N8N_HOST=0.0.0.0
N8N_PORT=5678
N8N_PROTOCOL=http
N8N_EDITOR_BASE_URL=http://217.79.255.54:5679
WEBHOOK_URL=http://217.79.255.54:5679
N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=false
N8N_RUNNERS_ENABLED=true
N8N_LOG_LEVEL=info
N8N_METRICS=true
EXECUTIONS_PROCESS=main
EXECUTIONS_DATA_PRUNE=true
EXECUTIONS_DATA_MAX_AGE=168
N8N_PERSONALIZATION_ENABLED=false
N8N_VERSION_NOTIFICATIONS_ENABLED=false
N8N_DIAGNOSTICS_ENABLED=false
N8N_HIRING_BANNER_ENABLED=false
EOF"

echo "📋 Step 6: Updating docker-compose.yml for N8N..."
ssh $SSH_HOST "cd $DOCKER_PATH && cp docker-compose.yml docker-compose.yml.backup"

# Create updated docker-compose configuration
ssh $SSH_HOST "cd $DOCKER_PATH && cat > docker-compose-n8n-fix.yml << 'EOF'
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
    volumes:
      - ./frontend:/app
      - /app/node_modules
    networks:
      - agentic-network
    healthcheck:
      test: ['CMD', 'curl', '-f', 'http://localhost:3000']
      interval: 30s
      timeout: 10s
      retries: 3

  backend-dev:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - '8001:8000'
    environment:
      - ENVIRONMENT=development
      - GEMINI_API_KEY=\${GEMINI_API_KEY}
      - SUPABASE_URL=\${SUPABASE_URL}
      - SUPABASE_ANON_KEY=\${SUPABASE_ANON_KEY}
      - N8N_URL=http://agentic-n8n-dev:5678
      - N8N_API_KEY=n8n-dev-api-key-12345
      - MCP_SERVER_URL=http://localhost:3001
    volumes:
      - ./backend:/app
    networks:
      - agentic-network
    depends_on:
      - redis-dev
      - agentic-n8n-dev
    healthcheck:
      test: ['CMD', 'curl', '-f', 'http://localhost:8000/health']
      interval: 30s
      timeout: 10s
      retries: 3

  agentic-n8n-dev:
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
      - N8N_EDITOR_BASE_URL=http://217.79.255.54:5679
      - WEBHOOK_URL=http://217.79.255.54:5679
      - N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=false
      - N8N_RUNNERS_ENABLED=true
      - N8N_LOG_LEVEL=info
      - N8N_METRICS=true
      - EXECUTIONS_PROCESS=main
      - EXECUTIONS_DATA_PRUNE=true
      - EXECUTIONS_DATA_MAX_AGE=168
      - N8N_PERSONALIZATION_ENABLED=false
      - N8N_VERSION_NOTIFICATIONS_ENABLED=false
      - N8N_DIAGNOSTICS_ENABLED=false
      - N8N_HIRING_BANNER_ENABLED=false
    volumes:
      - /opt/docker-apps/development/agentic-site/n8n-data:/home/node/.n8n
    networks:
      - agentic-network
    healthcheck:
      test: ['CMD', 'wget', '--no-verbose', '--tries=1', '--spider', 'http://localhost:5678']
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s

  redis-dev:
    image: redis:7-alpine
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
EOF"

echo "📋 Step 7: Starting N8N with new configuration..."
ssh $SSH_HOST "cd $DOCKER_PATH && docker-compose -f docker-compose-n8n-fix.yml up -d agentic-n8n-dev"

echo "📋 Step 8: Waiting for N8N to start..."
sleep 30

echo "📋 Step 9: Checking N8N health..."
for i in {1..10}; do
    if ssh $SSH_HOST "curl -s http://localhost:5679 > /dev/null"; then
        echo "✅ N8N is responding!"
        break
    else
        echo "⏳ Waiting for N8N... (attempt $i/10)"
        sleep 10
    fi
done

echo "📋 Step 10: Testing N8N authentication..."
ssh $SSH_HOST "curl -s -u admin:admin123 http://localhost:5679/rest/workflows | head -5"

echo "📋 Step 11: Creating N8N API key..."
# N8N doesn't have built-in API key creation via CLI, so we'll use basic auth
echo "ℹ️  N8N is configured with Basic Auth: admin/admin123"
echo "ℹ️  API calls should use: Authorization: Basic YWRtaW46YWRtaW4xMjM="

echo "📋 Step 12: Testing workflow creation..."
ssh $SSH_HOST "curl -s -u admin:admin123 -X POST http://localhost:5679/rest/workflows -H 'Content-Type: application/json' -d '{
  \"name\": \"Test Workflow\",
  \"nodes\": [
    {
      \"id\": \"start\",
      \"name\": \"Start\",
      \"type\": \"n8n-nodes-base.start\",
      \"position\": [250, 300],
      \"parameters\": {}
    }
  ],
  \"connections\": {},
  \"active\": false
}' | jq ."

echo "📋 Step 13: Restarting all services with fixed configuration..."
ssh $SSH_HOST "cd $DOCKER_PATH && docker-compose -f docker-compose-n8n-fix.yml up -d"

echo "📋 Step 14: Final health check..."
sleep 20
ssh $SSH_HOST "cd $DOCKER_PATH && docker-compose -f docker-compose-n8n-fix.yml ps"

echo "✅ N8N Deployment Fix Complete!"
echo ""
echo "🔗 N8N Access Information:"
echo "   URL: http://217.79.255.54:5679"
echo "   Username: admin"
echo "   Password: admin123"
echo "   API Auth: Basic YWRtaW46YWRtaW4xMjM="
echo ""
echo "🧪 Test N8N Access:"
echo "   curl -u admin:admin123 http://217.79.255.54:5679/rest/workflows"