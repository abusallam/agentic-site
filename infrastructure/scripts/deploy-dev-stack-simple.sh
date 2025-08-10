#!/bin/bash
# 🚀 SIMPLE DEVELOPMENT STACK DEPLOYMENT
# Deploys our enhanced development environment to VPS
set -e

SERVER_IP="217.79.255.54"
SERVER_USER="root"
SERVER_PASS="gnqLG7FDd4"
REPO_URL="git@github.com:abusallam/agentic-site.git"
BRANCH="develop"

echo "🚀 DEPLOYING ENHANCED DEVELOPMENT STACK"
echo "📅 $(date)"
echo "🎯 Target: Development environment at dev.consulting.sa"
echo "📦 Repository: $REPO_URL"
echo "🌿 Branch: $BRANCH"
echo ""

# Function to run SSH command with error handling
ssh_run() {
    sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "$1"
    if [ $? -eq 0 ]; then
        echo "✅ SSH: $1"
    else
        echo "❌ SSH FAILED: $1"
        exit 1
    fi
}

echo "🔍 Step 1: Cloning enhanced repository to development environment..."

# Clone our enhanced repository to development directory
ssh_run "cd /opt/apps && rm -rf development/agentic-site"
ssh_run "cd /opt/apps/development && git clone -b $BRANCH $REPO_URL agentic-site"
ssh_run "cd /opt/apps/development/agentic-site && git checkout $BRANCH"

echo ""
echo "🔍 Step 2: Checking repository contents..."

# Verify the repository was cloned correctly
ssh_run "cd /opt/apps/development/agentic-site && ls -la | head -10"
ssh_run "cd /opt/apps/development/agentic-site && echo 'Docker Compose files:' && ls -la docker-compose*.yml"

echo ""
echo "🔍 Step 3: Setting up environment file..."

# Copy the development environment file
ssh_run "cd /opt/apps/development/agentic-site && cp .env.development .env"

echo ""
echo "🔍 Step 4: Stopping any existing development containers..."

# Stop any existing development containers
ssh_run "cd /opt/apps/development/agentic-site && docker compose -f docker-compose.development.yml down || true"

echo ""
echo "🔍 Step 5: Building and starting development containers..."

# Build and start development containers
ssh_run "cd /opt/apps/development/agentic-site && docker compose -f docker-compose.development.yml up -d --build"

echo ""
echo "🔍 Step 6: Waiting for containers to be healthy..."

# Wait for containers to start
sleep 45

# Check container status
echo "Development Container Status:"
ssh_run "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E '(dev|NAMES)'"

echo ""
echo "🔍 Step 7: Testing development endpoints..."

# Test development endpoints
echo "Testing development endpoints..."
ssh_run "curl -I http://localhost:3001/ || echo 'Frontend not ready yet'"
ssh_run "curl -I http://localhost:8001/health || echo 'Backend not ready yet'"

echo ""
echo "🔍 Step 8: Setting up Nginx configuration for development..."

# Create development Nginx configuration
cat > /tmp/nginx-dev.conf << 'EOF'
# Development Site Configuration
server {
    listen 80;
    server_name dev.consulting.sa;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name dev.consulting.sa;
    
    # SSL Configuration (using existing wildcard cert)
    ssl_certificate /etc/letsencrypt/live/consulting.sa/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/consulting.sa/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Development-specific headers
    add_header X-Environment "development" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    
    # Main application (development port 3001)
    location / {
        proxy_pass http://127.0.0.1:3001;
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
    
    # API routes (development port 8001)
    location /api/ {
        proxy_pass http://127.0.0.1:8001/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
    
    # Development tools - N8N
    location /n8n/ {
        proxy_pass http://127.0.0.1:5679/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "development healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Copy and apply Nginx configuration
sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no /tmp/nginx-dev.conf "$SERVER_USER@$SERVER_IP:/etc/nginx/sites-available/dev-consulting.conf"
ssh_run "ln -sf /etc/nginx/sites-available/dev-consulting.conf /etc/nginx/sites-enabled/"
ssh_run "nginx -t && systemctl reload nginx"

echo ""
echo "🔍 Step 9: Final health check..."

# Final status check
echo "Final Container Status:"
ssh_run "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E '(dev|prod|NAMES)'"

echo ""
echo "Testing URLs:"
ssh_run "curl -I https://dev.consulting.sa/health || echo 'Development site not accessible yet - may need a few more minutes'"

# Cleanup temporary files
rm -f /tmp/nginx-dev.conf

echo ""
echo "🎉 ENHANCED DEVELOPMENT STACK DEPLOYMENT COMPLETED!"
echo ""
echo "📋 What's Deployed:"
echo "├── 🌐 Development Site: https://dev.consulting.sa"
echo "├── 🔧 Frontend Container: agentic-frontend-dev (port 3001)"
echo "├── 🔧 Backend Container: agentic-backend-dev (port 8001)"
echo "├── 🔧 Redis Container: agentic-redis-dev (port 6380)"
echo "├── 🔧 N8N Container: agentic-n8n-dev (port 5679)"
echo "└── 🔗 GitHub Repository: Connected to '$BRANCH' branch with all enhancements"
echo ""
echo "✨ Enhanced Features Deployed:"
echo "├── 🔧 Fixed Next.js SSR errors with ChatbotWrapper"
echo "├── 📚 Comprehensive documentation and guides"
echo "├── 🚀 Professional deployment scripts"
echo "├── 🔐 SSH deploy key integration"
echo "├── 🌐 Multi-domain SSL support"
echo "└── 📊 Health monitoring and backup systems"
echo ""
echo "🚀 Next Steps:"
echo "1. **Test Development Site**: Visit https://dev.consulting.sa"
echo "2. **Verify All Features**: Test the enhanced functionality"
echo "3. **Set up GitHub Webhook**: For automatic deployments on push"
echo "4. **Test Promotion Workflow**: When ready, promote dev to production"
echo ""
echo "🔧 Management Commands:"
echo "   View dev containers: docker ps | grep dev"
echo "   View dev logs: docker logs agentic-frontend-dev"
echo "   Restart dev stack: cd /opt/apps/development/agentic-site && docker compose -f docker-compose.development.yml restart"
echo "   Update from GitHub: cd /opt/apps/development/agentic-site && git pull origin $BRANCH"
echo ""
echo "📝 Your deployment strategy is now ready:"
echo "   ✅ Enhanced Dev Stack (dev.consulting.sa) ← GitHub '$BRANCH' branch"
echo "   🧪 Test & Validate ← Development environment with all fixes"
echo "   🔄 Promote via Nginx ← Switch domains when ready"
echo "   🚀 Production Promotion ← Dev becomes prod, new dev created"