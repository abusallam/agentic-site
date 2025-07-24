#!/bin/bash
set -e

# Main VPS Deployment Script - Production Ready
# This script deploys the agentic AI platform to the main VPS with comprehensive error handling

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Configuration
VPS_HOST=${VPS_HOST:-"217.79.255.54"}
VPS_USER=${VPS_USER:-"root"}
VPS_PASSWORD=${VPS_PASSWORD:-"gt5qXy22aJ"}
DOMAIN=${DOMAIN:-"consulting.sa"}

echo -e "${BLUE}🚀 Deploying Agentic AI Platform to VPS: $VPS_HOST${NC}"
echo -e "${BLUE}📋 This deployment includes all lessons learned and fixes${NC}"

# Function to run commands on VPS using sshpass
run_on_vps() {
    local command="$1"
    echo -e "${YELLOW}Running on VPS: $command${NC}"
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "$command"
}

# Function to copy files to VPS
copy_to_vps() {
    local local_path="$1"
    local remote_path="$2"
    echo -e "${YELLOW}Copying $local_path to VPS:$remote_path${NC}"
    sshpass -p "$VPS_PASSWORD" scp -o StrictHostKeyChecking=no -r "$local_path" "$VPS_USER@$VPS_HOST:$remote_path"
}

# Check if sshpass is installed
if ! command -v sshpass &> /dev/null; then
    echo -e "${YELLOW}Installing sshpass...${NC}"
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update && sudo apt-get install -y sshpass
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install hudochenkov/sshpass/sshpass
    else
        echo -e "${RED}Please install sshpass manually${NC}"
        exit 1
    fi
fi

# Test VPS connection
echo -e "${BLUE}Testing VPS connection...${NC}"
if run_on_vps "echo 'Connection successful'"; then
    echo -e "${GREEN}✓ VPS connection established${NC}"
else
    echo -e "${RED}❌ Failed to connect to VPS${NC}"
    exit 1
fi

# Step 1: Update system and install basic requirements
echo -e "${BLUE}Step 1: Setting up basic system requirements...${NC}"
run_on_vps "apt-get update && apt-get upgrade -y"
run_on_vps "apt-get install -y curl wget git unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release ufw fail2ban htop vim nginx certbot python3-certbot-nginx"

# Step 2: Install Docker and Docker Compose
echo -e "${BLUE}Step 2: Installing Docker...${NC}"
run_on_vps "curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh"
run_on_vps "systemctl start docker && systemctl enable docker"
run_on_vps "curl -L \"https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose"
run_on_vps "chmod +x /usr/local/bin/docker-compose"

# Step 3: Configure firewall
echo -e "${BLUE}Step 3: Configuring firewall...${NC}"
run_on_vps "ufw --force reset"
run_on_vps "ufw allow 22/tcp"      # SSH
run_on_vps "ufw allow 80/tcp"      # HTTP
run_on_vps "ufw allow 443/tcp"     # HTTPS
run_on_vps "ufw allow 3000/tcp"    # Frontend
run_on_vps "ufw allow 8000/tcp"    # Backend
run_on_vps "ufw allow 5678/tcp"    # n8n
run_on_vps "ufw allow 9090/tcp"    # Prometheus
run_on_vps "ufw allow 3001/tcp"    # Grafana/MCP
run_on_vps "ufw --force enable"

# Step 4: Create application directory and copy files
echo -e "${BLUE}Step 4: Setting up application...${NC}"
run_on_vps "mkdir -p /opt/agentic-platform"
run_on_vps "mkdir -p /opt/backups"

# Copy application files (excluding problematic directories)
echo -e "${YELLOW}Copying application files...${NC}"
sshpass -p "$VPS_PASSWORD" rsync -avz --exclude='.venv' --exclude='node_modules' --exclude='.git' --exclude='.next' --exclude='__pycache__' --exclude='*.pyc' -e "ssh -o StrictHostKeyChecking=no" . "$VPS_USER@$VPS_HOST:/opt/agentic-platform/"

# Copy environment file
copy_to_vps ".env" "/opt/agentic-platform/.env"

# Step 5: Build and start the application
echo -e "${BLUE}Step 5: Building and starting application...${NC}"
run_on_vps "cd /opt/agentic-platform && docker-compose -f docker-compose.production.yml build"
run_on_vps "cd /opt/agentic-platform && docker-compose -f docker-compose.production.yml up -d"

# Step 6: Configure Nginx
echo -e "${BLUE}Step 6: Configuring Nginx...${NC}"
copy_to_vps "nginx/production.conf" "/etc/nginx/sites-available/agentic-platform"
run_on_vps "ln -sf /etc/nginx/sites-available/agentic-platform /etc/nginx/sites-enabled/"
run_on_vps "rm -f /etc/nginx/sites-enabled/default"
run_on_vps "nginx -t && systemctl reload nginx"

# Step 7: Setup SSL certificates (Cloudflare Origin)
echo -e "${BLUE}Step 7: Setting up SSL certificates...${NC}"
run_on_vps "mkdir -p /etc/nginx/ssl"
copy_to_vps "ssl/consulting.sa.crt" "/etc/nginx/ssl/"
copy_to_vps "ssl/consulting.sa.key" "/etc/nginx/ssl/"
run_on_vps "chmod 600 /etc/nginx/ssl/consulting.sa.key"
run_on_vps "chmod 644 /etc/nginx/ssl/consulting.sa.crt"

# Step 8: Setup monitoring (optional for now)
echo -e "${BLUE}Step 8: Setting up basic monitoring...${NC}"
run_on_vps "cd /opt/agentic-platform/monitoring && docker-compose -f docker-compose.monitoring.yml up -d" || echo "Monitoring setup skipped"

# Step 9: Health checks
echo -e "${BLUE}Step 9: Running health checks...${NC}"
sleep 30

# Check if services are running
if run_on_vps "curl -f http://localhost:3000/api/health"; then
    echo -e "${GREEN}✓ Frontend is healthy${NC}"
else
    echo -e "${YELLOW}⚠ Frontend health check failed${NC}"
fi

if run_on_vps "curl -f http://localhost:8000/health"; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${YELLOW}⚠ Backend health check failed${NC}"
fi

# Step 10: Display access information
echo -e "${GREEN}🎉 Deployment completed!${NC}"
echo ""
echo -e "${BLUE}Access URLs:${NC}"
echo "- Website: https://$DOMAIN"
echo "- Backend API: https://$DOMAIN/api"
echo "- Health Check: https://$DOMAIN/api/health"
echo ""
echo -e "${BLUE}VPS Services:${NC}"
echo "- n8n: http://$VPS_HOST:5678 (will be installed in step 2)"
echo "- Grafana: http://$VPS_HOST:3001 (will be installed in step 2)"
echo "- Prometheus: http://$VPS_HOST:9090 (will be installed in step 2)"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Update your DNS to point $DOMAIN to $VPS_HOST"
echo "2. Provide your Supabase and Gemini API keys"
echo "3. Run the monitoring setup script"
echo "4. Test all functionality"

# Create a status check script on VPS
run_on_vps "cat > /opt/agentic-platform/check-status.sh << 'EOF'
#!/bin/bash
echo \"=== Agentic Platform Status ===\"
echo \"Docker containers:\"
docker ps --format \"table {{.Names}}\t{{.Status}}\t{{.Ports}}\"
echo \"\"
echo \"Nginx status:\"
systemctl status nginx --no-pager -l
echo \"\"
echo \"Disk usage:\"
df -h
echo \"\"
echo \"Memory usage:\"
free -h
EOF"

run_on_vps "chmod +x /opt/agentic-platform/check-status.sh"

echo -e "${GREEN}✅ Main VPS deployment script completed!${NC}"
echo -e "${BLUE}To check status: sshpass -p '$VPS_PASSWORD' ssh $VPS_USER@$VPS_HOST '/opt/agentic-platform/check-status.sh'${NC}"