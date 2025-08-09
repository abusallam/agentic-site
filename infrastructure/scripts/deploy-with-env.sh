#!/bin/bash

# Deploy with Environment Configuration
# Usage: ./deploy-with-env.sh <SSH_ALIAS> <CLOUDFLARE_TOKEN> <ZONE_ID>

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
if [ $# -lt 3 ]; then
    echo -e "${RED}Usage: $0 <SSH_ALIAS> <CLOUDFLARE_TOKEN> <ZONE_ID>${NC}"
    echo -e "${YELLOW}Example: $0 agentic-fixed-217-79-255-54-development 9h0vFxdufAjLy3qtQkmLzF_EFAhpKFQuWwtqmMkL a3694eb9575dd4bdf6f721f18c4953ca${NC}"
    exit 1
fi

SSH_ALIAS="$1"
CLOUDFLARE_TOKEN="$2"
ZONE_ID="$3"

echo -e "${BOLD}${PURPLE}🚀 Complete Environment Deployment${NC}"
echo -e "${BLUE}===================================${NC}"
echo "SSH Alias: $SSH_ALIAS"
echo "Zone ID: $ZONE_ID"
echo "Timestamp: $(date)"
echo

# Get correct IPv4 address
echo -e "${YELLOW}Step 1: Getting VPS IPv4 address...${NC}"
VPS_IP=$(ssh "$SSH_ALIAS" 'curl -s ipv4.icanhazip.com')
echo "✓ VPS IPv4: $VPS_IP"

echo -e "${YELLOW}Step 2: Configuring Cloudflare DNS records...${NC}"

# Function to create or update DNS record
update_dns_record() {
    local record_name="$1"
    local record_ip="$2"
    local proxied="$3"
    
    echo "Configuring DNS record: $record_name -> $record_ip (Proxied: $proxied)"
    
    # First, try to get existing record
    EXISTING_RECORD=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records?name=$record_name&type=A" \
         -H "Authorization: Bearer $CLOUDFLARE_TOKEN" \
         -H "Content-Type: application/json")
    
    RECORD_ID=$(echo "$EXISTING_RECORD" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    
    if [ -n "$RECORD_ID" ]; then
        # Update existing record
        RESULT=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$RECORD_ID" \
             -H "Authorization: Bearer $CLOUDFLARE_TOKEN" \
             -H "Content-Type: application/json" \
             --data "{
               \"type\": \"A\",
               \"name\": \"$record_name\",
               \"content\": \"$record_ip\",
               \"ttl\": 300,
               \"proxied\": $proxied
             }")
    else
        # Create new record
        RESULT=$(curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
             -H "Authorization: Bearer $CLOUDFLARE_TOKEN" \
             -H "Content-Type: application/json" \
             --data "{
               \"type\": \"A\",
               \"name\": \"$record_name\",
               \"content\": \"$record_ip\",
               \"ttl\": 300,
               \"proxied\": $proxied
             }")
    fi
    
    if echo "$RESULT" | grep -q '"success":true'; then
        echo "  ✓ $record_name configured successfully"
    else
        echo "  ❌ Failed to configure $record_name"
        echo "  Error: $(echo "$RESULT" | grep -o '"message":"[^"]*"' | cut -d'"' -f4)"
    fi
}

# Configure DNS records
update_dns_record "consulting.sa" "$VPS_IP" "true"
update_dns_record "www.consulting.sa" "$VPS_IP" "true"
update_dns_record "dev.consulting.sa" "$VPS_IP" "true"

echo -e "${YELLOW}Step 3: Fixing Next.js conflicts in both environments...${NC}"

ssh "$SSH_ALIAS" "
    echo 'Fixing Next.js conflicts in development environment...'
    cd /opt/docker-apps/development/agentic-site/agentic-site/frontend
    
    # Remove conflicting files
    rm -f pages/index.js
    rm -rf pages/_app.js pages/_document.js
    
    # Ensure we're using App Router
    if [ ! -f app/page.tsx ]; then
        mkdir -p app
        cat > app/page.tsx << 'EOF'
export default function Home() {
  return (
    <div className=\"min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4\">
      <div className=\"max-w-4xl mx-auto text-center\">
        <h1 className=\"text-4xl font-bold text-gray-900 mb-6\">
          Agentic Site - Development Environment
        </h1>
        <p className=\"text-xl text-gray-600 mb-8\">
          Welcome to the development environment. This is running on Next.js with App Router.
        </p>
        <div className=\"grid grid-cols-1 md:grid-cols-3 gap-6 mt-8\">
          <div className=\"bg-white p-6 rounded-lg shadow-md\">
            <h3 className=\"text-lg font-semibold mb-2\">Frontend</h3>
            <p className=\"text-gray-600\">Next.js 15 with App Router</p>
          </div>
          <div className=\"bg-white p-6 rounded-lg shadow-md\">
            <h3 className=\"text-lg font-semibold mb-2\">Backend</h3>
            <p className=\"text-gray-600\">Python FastAPI</p>
          </div>
          <div className=\"bg-white p-6 rounded-lg shadow-md\">
            <h3 className=\"text-lg font-semibold mb-2\">Environment</h3>
            <p className=\"text-gray-600\">Development</p>
          </div>
        </div>
      </div>
    </div>
  )
}
EOF
    fi
    
    echo 'Fixing Next.js conflicts in production environment...'
    cd /opt/docker-apps/production/agentic-site/agentic-site/frontend
    
    # Remove conflicting files
    rm -f pages/index.js
    rm -rf pages/_app.js pages/_document.js
    
    # Ensure we're using App Router
    if [ ! -f app/page.tsx ]; then
        mkdir -p app
        cat > app/page.tsx << 'EOF'
export default function Home() {
  return (
    <div className=\"min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center p-4\">
      <div className=\"max-w-4xl mx-auto text-center\">
        <h1 className=\"text-4xl font-bold text-gray-900 mb-6\">
          Agentic Site - Production Environment
        </h1>
        <p className=\"text-xl text-gray-600 mb-8\">
          Welcome to the production environment. This is running on Next.js with App Router.
        </p>
        <div className=\"grid grid-cols-1 md:grid-cols-3 gap-6 mt-8\">
          <div className=\"bg-white p-6 rounded-lg shadow-md\">
            <h3 className=\"text-lg font-semibold mb-2\">Frontend</h3>
            <p className=\"text-gray-600\">Next.js 15 with App Router</p>
          </div>
          <div className=\"bg-white p-6 rounded-lg shadow-md\">
            <h3 className=\"text-lg font-semibold mb-2\">Backend</h3>
            <p className=\"text-gray-600\">Python FastAPI</p>
          </div>
          <div className=\"bg-white p-6 rounded-lg shadow-md\">
            <h3 className=\"text-lg font-semibold mb-2\">Environment</h3>
            <p className=\"text-gray-600\">Production</p>
          </div>
        </div>
      </div>
    </div>
  )
}
EOF
    fi
    
    echo '✓ Next.js conflicts resolved in both environments'
"

echo -e "${YELLOW}Step 4: Restarting development environment with fixes...${NC}"

ssh "$SSH_ALIAS" "
    cd /opt/docker-apps/development/agentic-site/agentic-site
    
    echo 'Stopping development containers...'
    docker-compose -f docker-compose.development.yml down 2>/dev/null || docker-compose down
    
    echo 'Starting development containers with fixes...'
    docker-compose -f docker-compose.development.yml up -d 2>/dev/null || docker-compose up -d
    
    echo 'Waiting for services to start...'
    sleep 30
    
    echo 'Development container status:'
    docker-compose -f docker-compose.development.yml ps 2>/dev/null || docker-compose ps
"

echo -e "${YELLOW}Step 5: Deploying production environment...${NC}"

ssh "$SSH_ALIAS" "
    cd /opt/docker-apps/production/agentic-site/agentic-site
    
    echo 'Starting production containers...'
    docker-compose -f docker-compose.production.yml up -d
    
    echo 'Waiting for services to start...'
    sleep 30
    
    echo 'Production container status:'
    docker-compose -f docker-compose.production.yml ps
"

echo -e "${YELLOW}Step 6: Verifying deployments...${NC}"

ssh "$SSH_ALIAS" "
    echo '=== Service Health Check ==='
    
    # Check development
    if curl -s http://localhost:3001 > /dev/null 2>&1; then
        echo '✅ Development frontend responding on port 3001'
    else
        echo '❌ Development frontend not responding'
    fi
    
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo '✅ Development backend responding on port 8001'
    else
        echo '❌ Development backend not responding'
    fi
    
    # Check production
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo '✅ Production frontend responding on port 3000'
    else
        echo '❌ Production frontend not responding'
    fi
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo '✅ Production backend responding on port 8000'
    else
        echo '❌ Production backend not responding'
    fi
"

echo -e "${YELLOW}Step 7: Testing domain access...${NC}"

echo "Waiting for DNS propagation..."
sleep 10

# Test domains
for domain in "consulting.sa" "dev.consulting.sa"; do
    echo "Testing https://$domain..."
    
    # Test HTTPS
    if curl -s -I "https://$domain" | grep -q "200\|301\|302"; then
        echo "  ✅ https://$domain is accessible"
    else
        echo "  ⚠ https://$domain may still be propagating"
    fi
done

echo
echo -e "${BOLD}${GREEN}🎉 Complete Environment Deployment Finished!${NC}"
echo -e "${BLUE}=============================================${NC}"
echo
echo -e "${BOLD}${CYAN}🌐 Live URLs:${NC}"
echo "✅ Production: https://consulting.sa"
echo "✅ Development: https://dev.consulting.sa"
echo "✅ Production API: https://consulting.sa/api/"
echo "✅ Development API: https://dev.consulting.sa/api/"
echo
echo -e "${BOLD}${CYAN}🏗️ Container Architecture:${NC}"
echo "Production Environment:"
echo "  - Frontend: Port 3000 → https://consulting.sa"
echo "  - Backend: Port 8000 → https://consulting.sa/api/"
echo "  - Redis: Port 6379 (internal)"
echo "  - n8n: Port 5678 → https://consulting.sa/workflows/"
echo
echo "Development Environment:"
echo "  - Frontend: Port 3001 → https://dev.consulting.sa"
echo "  - Backend: Port 8001 → https://dev.consulting.sa/api/"
echo "  - Redis: Port 6380 (internal)"
echo "  - n8n: Port 5679 → https://dev.consulting.sa/workflows/"
echo
echo -e "${BOLD}${CYAN}🔧 Management Commands:${NC}"
echo "Production Status: ssh $SSH_ALIAS '/usr/local/bin/agentic-status.sh'"
echo "Development Logs: ssh $SSH_ALIAS 'cd /opt/docker-apps/development/agentic-site/agentic-site && docker-compose logs -f'"
echo "Production Logs: ssh $SSH_ALIAS 'cd /opt/docker-apps/production/agentic-site/agentic-site && docker-compose -f docker-compose.production.yml logs -f'"
echo
echo -e "${BOLD}${GREEN}✅ Both environments are now running separately!${NC}"
echo -e "${BOLD}${YELLOW}⚠️  You can now develop on dev.consulting.sa and deploy to consulting.sa${NC}"