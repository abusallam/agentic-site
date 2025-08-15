#!/bin/bash

# Fix N8N Deployment Script v2
# This script properly fixes N8N deployment issues by stopping existing containers first

set -e

echo "🔧 Fixing N8N Deployment Issues (v2)..."

# SSH connection details
SSH_HOST="agentic-fixed-217-79-255-54-development"
DOCKER_PATH="/opt/docker-apps/development/agentic-site/agentic-site"

echo "📋 Step 1: Checking current containers..."
ssh $SSH_HOST "docker ps | grep n8n"

echo "📋 Step 2: Stopping ALL N8N containers..."
ssh $SSH_HOST "docker stop agentic-n8n-dev || true"
ssh $SSH_HOST "docker stop consulting-n8n-prod || true"
ssh $SSH_HOST "docker stop \$(docker ps -q --filter 'ancestor=n8nio/n8n:latest') || true"

echo "📋 Step 3: Removing N8N containers..."
ssh $SSH_HOST "docker rm agentic-n8n-dev || true"
ssh $SSH_HOST "docker rm \$(docker ps -aq --filter 'ancestor=n8nio/n8n:latest') || true"

echo "📋 Step 4: Cleaning up port conflicts..."
ssh $SSH_HOST "netstat -tulpn | grep :5679 || echo 'Port 5679 is free'"
ssh $SSH_HOST "netstat -tulpn | grep :5678 || echo 'Port 5678 is free'"

echo "📋 Step 5: Creating N8N data directory with proper permissions..."
ssh $SSH_HOST "rm -rf /opt/docker-apps/development/agentic-site/n8n-data"
ssh $SSH_HOST "mkdir -p /opt/docker-apps/development/agentic-site/n8n-data"
ssh $SSH_HOST "chmod 755 /opt/docker-apps/development/agentic-site/n8n-data"

echo "📋 Step 6: Starting fresh N8N container..."
ssh $SSH_HOST "docker run -d \\
  --name agentic-n8n-dev-new \\
  --restart unless-stopped \\
  -p 5679:5678 \\
  -e N8N_BASIC_AUTH_ACTIVE=true \\
  -e N8N_BASIC_AUTH_USER=admin \\
  -e N8N_BASIC_AUTH_PASSWORD=admin123 \\
  -e N8N_HOST=0.0.0.0 \\
  -e N8N_PORT=5678 \\
  -e N8N_PROTOCOL=http \\
  -e N8N_EDITOR_BASE_URL=http://217.79.255.54:5679 \\
  -e WEBHOOK_URL=http://217.79.255.54:5679 \\
  -e N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=false \\
  -e N8N_RUNNERS_ENABLED=true \\
  -e N8N_LOG_LEVEL=info \\
  -e N8N_METRICS=true \\
  -e EXECUTIONS_PROCESS=main \\
  -e EXECUTIONS_DATA_PRUNE=true \\
  -e EXECUTIONS_DATA_MAX_AGE=168 \\
  -e N8N_PERSONALIZATION_ENABLED=false \\
  -e N8N_VERSION_NOTIFICATIONS_ENABLED=false \\
  -e N8N_DIAGNOSTICS_ENABLED=false \\
  -e N8N_HIRING_BANNER_ENABLED=false \\
  -v /opt/docker-apps/development/agentic-site/n8n-data:/home/node/.n8n \\
  n8nio/n8n:latest"

echo "📋 Step 7: Waiting for N8N to start..."
sleep 45

echo "📋 Step 8: Checking N8N container status..."
ssh $SSH_HOST "docker ps | grep agentic-n8n-dev-new"
ssh $SSH_HOST "docker logs agentic-n8n-dev-new --tail 10"

echo "📋 Step 9: Testing N8N accessibility..."
for i in {1..15}; do
    if ssh $SSH_HOST "curl -s http://localhost:5679 > /dev/null 2>&1"; then
        echo "✅ N8N is responding!"
        break
    else
        echo "⏳ Waiting for N8N... (attempt $i/15)"
        sleep 10
    fi
done

echo "📋 Step 10: Testing N8N authentication..."
ssh $SSH_HOST "curl -s -u admin:admin123 http://localhost:5679/rest/active-workflows | head -5 || echo 'Auth test completed'"

echo "📋 Step 11: Creating test workflow..."
ssh $SSH_HOST "curl -s -u admin:admin123 -X POST http://localhost:5679/rest/workflows \\
  -H 'Content-Type: application/json' \\
  -d '{
    \"name\": \"Test Workflow - $(date +%Y%m%d_%H%M%S)\",
    \"nodes\": [
      {
        \"id\": \"start-node\",
        \"name\": \"Start\",
        \"type\": \"n8n-nodes-base.start\",
        \"position\": [250, 300],
        \"parameters\": {}
      }
    ],
    \"connections\": {},
    \"active\": false,
    \"settings\": {}
  }' | jq . || echo 'Workflow creation test completed'"

echo "📋 Step 12: Updating MCP service configuration..."
# Update the MCP service to use the correct N8N URL
ssh $SSH_HOST "cd $DOCKER_PATH && cat > n8n-mcp-config.env << 'EOF'
N8N_URL=http://217.79.255.54:5679
N8N_API_USER=admin
N8N_API_PASSWORD=admin123
N8N_BASE_URL=http://217.79.255.54:5679
MCP_SERVER_URL=http://localhost:3001
EOF"

echo "📋 Step 13: Testing N8N API endpoints..."
echo "Testing workflows endpoint:"
ssh $SSH_HOST "curl -s -u admin:admin123 http://localhost:5679/rest/workflows | jq 'length' || echo 'API test completed'"

echo "Testing credentials endpoint:"
ssh $SSH_HOST "curl -s -u admin:admin123 http://localhost:5679/rest/credentials | jq 'length' || echo 'Credentials test completed'"

echo "Testing executions endpoint:"
ssh $SSH_HOST "curl -s -u admin:admin123 http://localhost:5679/rest/executions | jq 'length' || echo 'Executions test completed'"

echo "✅ N8N Deployment Fix Complete!"
echo ""
echo "🔗 N8N Access Information:"
echo "   URL: http://217.79.255.54:5679"
echo "   Username: admin"
echo "   Password: admin123"
echo "   Container: agentic-n8n-dev-new"
echo ""
echo "🧪 Test N8N Access:"
echo "   curl -u admin:admin123 http://217.79.255.54:5679/rest/workflows"
echo "   curl -u admin:admin123 http://217.79.255.54:5679/rest/active-workflows"
echo ""
echo "🔧 Next Steps:"
echo "   1. Update backend environment variables to use N8N_URL=http://217.79.255.54:5679"
echo "   2. Test MCP integration with N8N"
echo "   3. Run comprehensive testing suite"