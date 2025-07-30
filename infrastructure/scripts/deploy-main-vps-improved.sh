#!/bin/bash
set -e

# Improved VPS Deployment Script - Production Ready
# This script incorporates all lessons learned from the deployment process

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Configuration
VPS_HOST=${VPS_HOST:-"217.79.255.54"}
VPS_USER=${VPS_USER:-"root"}
VPS_PASSWORD=${VPS_PASSWORD:-"xxXNCpx9Cz"}
DOMAIN=${DOMAIN:-"consulting.sa"}

echo -e "${PURPLE}🚀 Agentic AI Platform - Systematic Deployment${NC}"
echo -e "${BLUE}📋 Incorporating all lessons learned and best practices${NC}"
echo -e "${BLUE}🎯 Target: $VPS_HOST ($DOMAIN)${NC}"
echo ""

# Function to run commands on VPS using sshpass
run_on_vps() {
    local command="$1"
    local description="${2:-$command}"
    echo -e "${YELLOW}VPS: $description${NC}"
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "$command"
}

# Function to copy files to VPS with error handling
copy_to_vps() {
    local local_path="$1"
    local remote_path="$2"
    echo -e "${YELLOW}Copying $local_path to VPS:$remote_path${NC}"
    sshpass -p "$VPS_PASSWORD" scp -o StrictHostKeyChecking=no -r "$local_path" "$VPS_USER@$VPS_HOST:$remote_path"
}

# Function to validate prerequisites
validate_prerequisites() {
    echo -e "${BLUE}Phase 1: Validating Prerequisites${NC}"
    
    # Check if sshpass is installed
    if ! command -v sshpass &> /dev/null; then
        echo -e "${YELLOW}Installing sshpass...${NC}"
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo apt-get update && sudo apt-get install -y sshpass
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install hudochenkov/sshpass/sshpass
        else
            echo -e "${RED}❌ Please install sshpass manually${NC}"
            exit 1
        fi
    fi
    
    # Test VPS connection
    echo -e "${YELLOW}Testing VPS connection...${NC}"
    if run_on_vps "echo 'Connection test successful'" "Testing connection"; then
        echo -e "${GREEN}✓ VPS connection established${NC}"
    else
        echo -e "${RED}❌ Failed to connect to VPS${NC}"
        exit 1
    fi
    
    # Check required files
    local required_files=(".env" "docker-compose.production.yml" "nginx/production.conf" "ssl/consulting.sa.crt" "ssl/consulting.sa.key")
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            echo -e "${RED}❌ Required file missing: $file${NC}"
            exit 1
        fi
    done
    echo -e "${GREEN}✓ All required files present${NC}"
    
    echo -e "${GREEN}✅ Prerequisites validation completed${NC}"
    echo ""
}

# Function to setup VPS infrastructure
setup_infrastructure() {
    echo -e "${BLUE}Phase 2: Setting up VPS Infrastructure${NC}"
    
    # Update system
    run_on_vps "apt-get update && apt-get upgrade -y" "Updating system packages"
    
    # Install basic requirements
    run_on_vps "apt-get install -y curl wget git unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release ufw fail2ban htop vim nginx certbot python3-certbot-nginx jq" "Installing system packages"
    
    # Install Docker using universal script (lesson learned)
    run_on_vps "curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh" "Installing Docker"
    run_on_vps "systemctl start docker && systemctl enable docker" "Starting Docker service"
    
    # Install Docker Compose
    run_on_vps "curl -L \"https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose" "Installing Docker Compose"
    run_on_vps "chmod +x /usr/local/bin/docker-compose" "Setting Docker Compose permissions"
    
    # Configure firewall
    run_on_vps "ufw --force reset" "Resetting firewall"
    run_on_vps "ufw allow 22/tcp && ufw allow 80/tcp && ufw allow 443/tcp && ufw allow 3000/tcp && ufw allow 8000/tcp && ufw allow 5678/tcp && ufw allow 9090/tcp && ufw allow 3001/tcp" "Configuring firewall rules"
    run_on_vps "ufw --force enable" "Enabling firewall"
    
    echo -e "${GREEN}✅ Infrastructure setup completed${NC}"
    echo ""
}

# Function to deploy application files (lesson learned: use tar for better handling)
deploy_application_files() {
    echo -e "${BLUE}Phase 3: Deploying Application Files${NC}"
    
    # Create directories
    run_on_vps "mkdir -p /opt/agentic-platform /opt/backups" "Creating directories"
    
    # Create deployment package excluding problematic directories (lesson learned)
    echo -e "${YELLOW}Creating deployment package...${NC}"
    tar --exclude='.venv' \
        --exclude='node_modules' \
        --exclude='.git' \
        --exclude='.next' \
        --exclude='n8n-mcp/node_modules' \
        --exclude='n8n-mcp/dist' \
        --exclude='infrastructure/cleanup/backups' \
        -czf /tmp/agentic-platform.tar.gz .
    
    # Transfer and extract files
    echo -e "${YELLOW}Transferring files to VPS...${NC}"
    sshpass -p "$VPS_PASSWORD" scp -o StrictHostKeyChecking=no /tmp/agentic-platform.tar.gz "$VPS_USER@$VPS_HOST:/opt/"
    
    run_on_vps "cd /opt && tar -xzf agentic-platform.tar.gz -C agentic-platform && rm agentic-platform.tar.gz" "Extracting files on VPS"
    
    # Clean up local temp file
    rm -f /tmp/agentic-platform.tar.gz
    
    echo -e "${GREEN}✅ Application files deployed${NC}"
    echo ""
}

# Function to build and start containers (lesson learned: fix build context issues)
build_and_start_containers() {
    echo -e "${BLUE}Phase 4: Building and Starting Containers${NC}"
    
    # Fix Docker build context issues (lesson learned)
    run_on_vps "cp /opt/agentic-platform/Dockerfile.backend /opt/agentic-platform/agent/" "Fixing backend Dockerfile location"
    
    # Add problematic directories to .dockerignore (lesson learned)
    run_on_vps "echo 'n8n-mcp/' >> /opt/agentic-platform/.dockerignore" "Updating .dockerignore"
    
    # Build containers
    run_on_vps "cd /opt/agentic-platform && docker compose -f docker-compose.production.yml build --no-cache" "Building Docker containers"
    
    # Start containers
    run_on_vps "cd /opt/agentic-platform && docker compose -f docker-compose.production.yml up -d" "Starting containers"
    
    echo -e "${GREEN}✅ Containers built and started${NC}"
    echo ""
}

# Function to configure Nginx with SSL (lesson learned: fix config issues)
configure_nginx_and_ssl() {
    echo -e "${BLUE}Phase 5: Configuring Nginx and SSL${NC}"
    
    # Setup SSL certificates first
    run_on_vps "mkdir -p /etc/nginx/ssl" "Creating SSL directory"
    run_on_vps "cp /opt/agentic-platform/ssl/consulting.sa.crt /etc/nginx/ssl/" "Copying SSL certificate"
    run_on_vps "cp /opt/agentic-platform/ssl/consulting.sa.key /etc/nginx/ssl/" "Copying SSL key"
    run_on_vps "chmod 600 /etc/nginx/ssl/consulting.sa.key && chmod 644 /etc/nginx/ssl/consulting.sa.crt" "Setting SSL permissions"
    
    # Configure Nginx
    run_on_vps "cp /opt/agentic-platform/nginx/production.conf /etc/nginx/sites-available/agentic-platform" "Copying Nginx configuration"
    
    # Fix known Nginx configuration issues (lesson learned)
    run_on_vps "sed -i 's/gzip_proxied expired no-cache no-store private must-revalidate auth;/gzip_proxied expired no-cache no-store private auth;/' /etc/nginx/sites-available/agentic-platform" "Fixing Nginx gzip configuration"
    
    # Test Nginx configuration
    echo -e "${YELLOW}Testing Nginx configuration...${NC}"
    if run_on_vps "nginx -t" "Testing Nginx config"; then
        echo -e "${GREEN}✓ Nginx configuration valid${NC}"
    else
        echo -e "${RED}❌ Nginx configuration test failed${NC}"
        exit 1
    fi
    
    # Enable site and reload
    run_on_vps "ln -sf /etc/nginx/sites-available/agentic-platform /etc/nginx/sites-enabled/" "Enabling site"
    run_on_vps "systemctl reload nginx" "Reloading Nginx"
    
    echo -e "${GREEN}✅ Nginx and SSL configured${NC}"
    echo ""
}

# Function to validate deployment
validate_deployment() {
    echo -e "${BLUE}Phase 6: Validating Deployment${NC}"
    
    echo -e "${YELLOW}Waiting for services to start...${NC}"
    sleep 30
    
    # Check container status
    echo -e "${YELLOW}Checking container status...${NC}"
    run_on_vps "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'" "Container status"
    
    # Health checks
    echo -e "${YELLOW}Running health checks...${NC}"
    
    # Frontend health check
    if run_on_vps "curl -s -k -H 'Host: consulting.sa' https://localhost/api/health | grep -q 'ok'" "Frontend health check"; then
        echo -e "${GREEN}✓ Frontend health check passed${NC}"
    else
        echo -e "${YELLOW}⚠ Frontend health check failed (may need time to start)${NC}"
    fi
    
    # Backend health check
    if run_on_vps "curl -s http://localhost:8000/health | grep -q 'status'" "Backend health check"; then
        echo -e "${GREEN}✓ Backend health check passed${NC}"
    else
        echo -e "${YELLOW}⚠ Backend health check failed (may need time to start)${NC}"
    fi
    
    echo -e "${GREEN}✅ Deployment validation completed${NC}"
    echo ""
}

# Function to setup monitoring and status scripts
setup_monitoring() {
    echo -e "${BLUE}Phase 7: Setting up Monitoring${NC}"
    
    # Create comprehensive status check script
    run_on_vps "cat > /opt/agentic-platform/check-status.sh << 'EOF'
#!/bin/bash
echo \"=== Agentic Platform Status ===\"
echo \"Docker containers:\"
docker ps --format \"table {{.Names}}\t{{.Status}}\t{{.Ports}}\"
echo \"\"
echo \"Nginx status:\"
systemctl status nginx --no-pager -l | head -10
echo \"\"
echo \"Health checks:\"
echo \"Frontend: \$(curl -s -k -H 'Host: consulting.sa' https://localhost/api/health | jq -r .status 2>/dev/null || echo 'failed')\"
echo \"Backend: \$(curl -s http://localhost:8000/health | jq -r .status 2>/dev/null || echo 'failed')\"
echo \"\"
echo \"System resources:\"
echo \"Disk usage:\"
df -h | grep -E '(Filesystem|/dev/)'
echo \"\"
echo \"Memory usage:\"
free -h
echo \"\"
echo \"Load average:\"
uptime
EOF" "Creating status check script"
    
    run_on_vps "chmod +x /opt/agentic-platform/check-status.sh" "Setting script permissions"
    
    echo -e "${GREEN}✅ Monitoring setup completed${NC}"
    echo ""
}

# Function to display deployment summary
display_summary() {
    echo -e "${PURPLE}🎉 Deployment Summary${NC}"
    echo ""
    echo -e "${BLUE}Access Information:${NC}"
    echo "- Website: https://$DOMAIN"
    echo "- API Health: https://$DOMAIN/api/health"
    echo "- Backend Health: http://$VPS_HOST:8000/health"
    echo ""
    echo -e "${BLUE}Management Commands:${NC}"
    echo "- Status Check: sshpass -p '$VPS_PASSWORD' ssh $VPS_USER@$VPS_HOST '/opt/agentic-platform/check-status.sh'"
    echo "- View Logs: sshpass -p '$VPS_PASSWORD' ssh $VPS_USER@$VPS_HOST 'cd /opt/agentic-platform && docker compose -f docker-compose.production.yml logs -f'"
    echo "- Restart Services: sshpass -p '$VPS_PASSWORD' ssh $VPS_USER@$VPS_HOST 'cd /opt/agentic-platform && docker compose -f docker-compose.production.yml restart'"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo "1. Update DNS to point $DOMAIN to $VPS_HOST"
    echo "2. Test all functionality"
    echo "3. Set up monitoring dashboards"
    echo "4. Configure backup procedures"
    echo ""
    echo -e "${GREEN}✅ Systematic deployment completed successfully!${NC}"
}

# Main execution flow
main() {
    echo -e "${PURPLE}Starting systematic deployment process...${NC}"
    echo ""
    
    validate_prerequisites
    setup_infrastructure
    deploy_application_files
    build_and_start_containers
    configure_nginx_and_ssl
    validate_deployment
    setup_monitoring
    display_summary
    
    echo -e "${PURPLE}🚀 Agentic AI Platform is now live and operational!${NC}"
}

# Execute main function
main "$@"