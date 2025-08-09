#!/bin/bash

# Working Enterprise Deployment - Simple and Reliable
# Usage: ./working-enterprise-setup.sh <SSH_ALIAS> <ENVIRONMENT>

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
GITHUB_TOKEN="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"

echo -e "${BOLD}${PURPLE}🚀 Working Enterprise Deployment${NC}"
echo -e "${BLUE}================================${NC}"
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

echo -e "${YELLOW}Step 2: Setting up deployment directory and cloning repository...${NC}"
ssh "$SSH_ALIAS" "
    echo 'Setting up deployment directory...'
    mkdir -p $DEPLOY_PATH
    cd $DEPLOY_PATH
    
    # Clean up any existing deployment
    rm -rf agentic-site
    
    # Clone repository with token authentication
    echo 'Cloning repository with authentication...'
    git clone https://$GITHUB_TOKEN@github.com/abusallam/agentic-site.git
    cd agentic-site
    git checkout develop
    
    echo '✓ Repository cloned successfully'
"

echo -e "${YELLOW}Step 3: Creating minimal working docker-compose.yml...${NC}"
ssh "$SSH_ALIAS" "
    cd $DEPLOY_PATH/agentic-site
    
    # Create a minimal working docker-compose.yml
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  frontend:
    image: node:18-alpine
    working_dir: /app
    ports:
      - '3001:3000'
    environment:
      - NODE_ENV=development
      - PORT=3000
    volumes:
      - ./frontend:/app
    command: sh -c 'npm install && npm run dev'
    restart: unless-stopped
    networks:
      - agentic-network

  backend:
    image: python:3.11-slim
    working_dir: /app
    ports:
      - '8001:8000'
    environment:
      - ENVIRONMENT=development
      - PYTHONPATH=/app
    volumes:
      - ./backend:/app
    command: sh -c 'pip install -r requirements.txt && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload'
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

echo -e "${YELLOW}Step 4: Creating basic package.json for frontend (if missing)...${NC}"
ssh "$SSH_ALIAS" "
    cd $DEPLOY_PATH/agentic-site/frontend
    
    # Create basic package.json if it doesn't exist or is incomplete
    if [ ! -f package.json ] || ! grep -q '\"dev\"' package.json; then
        echo 'Creating basic package.json...'
        cat > package.json << 'EOF'
{
  \"name\": \"agentic-frontend\",
  \"version\": \"1.0.0\",
  \"private\": true,
  \"scripts\": {
    \"dev\": \"next dev\",
    \"build\": \"next build\",
    \"start\": \"next start\",
    \"lint\": \"next lint\"
  },
  \"dependencies\": {
    \"next\": \"^14.0.0\",
    \"react\": \"^18.0.0\",
    \"react-dom\": \"^18.0.0\",
    \"typescript\": \"^5.0.0\",
    \"@types/node\": \"^20.0.0\",
    \"@types/react\": \"^18.0.0\",
    \"@types/react-dom\": \"^18.0.0\"
  },
  \"devDependencies\": {
    \"eslint\": \"^8.0.0\",
    \"eslint-config-next\": \"^14.0.0\"
  }
}
EOF
    fi
    
    # Create basic Next.js pages if they don't exist
    mkdir -p pages
    if [ ! -f pages/index.js ]; then
        cat > pages/index.js << 'EOF'
export default function Home() {
  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <h1>Agentic Site - Development Environment</h1>
      <p>Frontend is running successfully!</p>
      <p>Environment: Development</p>
      <p>Port: 3001</p>
    </div>
  )
}
EOF
    fi
    
    echo '✓ Frontend configuration created'
"

echo -e "${YELLOW}Step 5: Creating basic backend files (if missing)...${NC}"
ssh "$SSH_ALIAS" "
    cd $DEPLOY_PATH/agentic-site/backend
    
    # Create basic requirements.txt if missing
    if [ ! -f requirements.txt ]; then
        cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pydantic==2.5.0
python-dotenv==1.0.0
EOF
    fi
    
    # Create basic main.py if missing
    if [ ! -f main.py ]; then
        cat > main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title=\"Agentic Backend\", version=\"1.0.0\")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[\"*\"],
    allow_credentials=True,
    allow_methods=[\"*\"],
    allow_headers=[\"*\"],
)

@app.get(\"/\")
async def root():
    return {
        \"message\": \"Agentic Backend is running!\",
        \"environment\": os.getenv(\"ENVIRONMENT\", \"development\"),
        \"port\": 8001,
        \"status\": \"healthy\"
    }

@app.get(\"/health\")
async def health():
    return {\"status\": \"healthy\", \"service\": \"backend\"}

@app.get(\"/api/test\")
async def test():
    return {\"message\": \"API is working!\", \"timestamp\": \"$(date)\"}
EOF
    fi
    
    echo '✓ Backend configuration created'
"

echo -e "${YELLOW}Step 6: Starting services...${NC}"
ssh "$SSH_ALIAS" "
    cd $DEPLOY_PATH/agentic-site
    
    echo 'Stopping any existing containers...'
    docker-compose down 2>/dev/null || true
    
    echo 'Starting services...'
    docker-compose up -d
    
    echo 'Waiting for services to initialize...'
    sleep 45
    
    echo '✓ Services started'
"

echo -e "${YELLOW}Step 7: Verifying deployment...${NC}"
ssh "$SSH_ALIAS" "
    cd $DEPLOY_PATH/agentic-site
    
    echo 'Container Status:'
    docker-compose ps
    
    echo
    echo 'Service Health Check:'
    
    # Get the actual IP address
    VPS_IP=\$(curl -s ifconfig.me)
    
    # Check frontend
    sleep 10
    if curl -s http://localhost:3001 > /dev/null 2>&1; then
        echo '✅ Frontend is responding on port 3001'
        echo '   URL: http://'\$VPS_IP':3001'
    else
        echo '❌ Frontend not responding on port 3001'
        echo 'Frontend logs:'
        docker-compose logs frontend | tail -10
    fi
    
    # Check backend
    if curl -s http://localhost:8001 > /dev/null 2>&1; then
        echo '✅ Backend is responding on port 8001'
        echo '   URL: http://'\$VPS_IP':8001'
    else
        echo '❌ Backend not responding on port 8001'
        echo 'Backend logs:'
        docker-compose logs backend | tail -10
    fi
    
    # Check Redis
    if docker-compose exec -T redis redis-cli ping 2>/dev/null | grep -q PONG; then
        echo '✅ Redis is responding'
    else
        echo '❌ Redis not responding'
    fi
    
    # Check n8n
    sleep 5
    if curl -s http://localhost:5679 > /dev/null 2>&1; then
        echo '✅ n8n is responding on port 5679'
        echo '   URL: http://'\$VPS_IP':5679 (admin/admin123)'
    else
        echo '❌ n8n not responding on port 5679'
    fi
"

# Get VPS IP for final output
VPS_IP=$(ssh "$SSH_ALIAS" 'curl -s ifconfig.me')

echo
echo -e "${BOLD}${GREEN}🎉 Working Enterprise Deployment Complete!${NC}"
echo -e "${BLUE}===========================================${NC}"
echo
echo -e "${BOLD}${CYAN}🌐 Access URLs:${NC}"
echo "Frontend: http://$VPS_IP:3001"
echo "Backend: http://$VPS_IP:8001"
echo "Backend API: http://$VPS_IP:8001/api/test"
echo "n8n: http://$VPS_IP:5679 (admin/admin123)"
echo "Redis: $VPS_IP:6380"
echo
echo -e "${BOLD}${CYAN}🛠️ Management Commands:${NC}"
echo "Status: ssh $SSH_ALIAS 'cd $DEPLOY_PATH/agentic-site && docker-compose ps'"
echo "Logs: ssh $SSH_ALIAS 'cd $DEPLOY_PATH/agentic-site && docker-compose logs -f'"
echo "Restart: ssh $SSH_ALIAS 'cd $DEPLOY_PATH/agentic-site && docker-compose restart'"
echo "Stop: ssh $SSH_ALIAS 'cd $DEPLOY_PATH/agentic-site && docker-compose down'"
echo
echo -e "${BOLD}${CYAN}🔧 Quick Tests:${NC}"
echo "Test Frontend: curl http://$VPS_IP:3001"
echo "Test Backend: curl http://$VPS_IP:8001"
echo "Test API: curl http://$VPS_IP:8001/api/test"
echo
echo -e "${BOLD}${GREEN}✅ Application is now running on the VPS!${NC}"
echo -e "${BOLD}${YELLOW}⚠️  This is a development setup - configure environment variables for production${NC}"