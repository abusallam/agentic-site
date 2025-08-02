#!/bin/bash

# Complete VPS Setup Script
# This script sets up a new VPS from scratch with just IP, username, and password
# Usage: ./setup-new-vps.sh <IP> <USERNAME> <PASSWORD> [ENVIRONMENT]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check arguments
if [ $# -lt 3 ]; then
    echo -e "${RED}Usage: $0 <IP> <USERNAME> <PASSWORD> [ENVIRONMENT]${NC}"
    echo -e "${YELLOW}Example: $0 217.79.255.54 root mypassword development${NC}"
    echo -e "${YELLOW}Example: $0 192.168.1.100 root mypassword production${NC}"
    exit 1
fi

VPS_IP="$1"
VPS_USER="$2"
VPS_PASSWORD="$3"
ENVIRONMENT="${4:-development}"  # Default to development

echo -e "${PURPLE}🚀 Complete VPS Setup for Agentic Site${NC}"
echo -e "${BLUE}=================================${NC}"
echo "Target IP: $VPS_IP"
echo "Username: $VPS_USER"
echo "Environment: $ENVIRONMENT"
echo "Timestamp: $(date)"
echo

# Function to run commands on VPS with password
run_with_password() {
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$VPS_USER@$VPS_IP" "$1"
}

# Function to copy files to VPS with password
copy_with_password() {
    sshpass -p "$VPS_PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$1" "$VPS_USER@$VPS_IP:$2"
}

# Function to run commands on VPS without password (after SSH key setup)
run_on_vps() {
    ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_IP" "$1"
}

echo -e "${YELLOW}Step 1: Installing required tools locally...${NC}"

# Check and install sshpass if not available
if ! command -v sshpass &> /dev/null; then
    echo "Installing sshpass..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y sshpass
    elif command -v yum &> /dev/null; then
        sudo yum install -y sshpass
    elif command -v brew &> /dev/null; then
        brew install sshpass
    else
        echo -e "${RED}❌ Please install sshpass manually${NC}"
        exit 1
    fi
fi

echo "✓ Required tools installed"

echo -e "${YELLOW}Step 2: Testing initial VPS connection...${NC}"

echo "Testing connection with provided credentials..."
echo "IP: $VPS_IP"
echo "User: $VPS_USER"
echo "Attempting connection..."

# Try different SSH options to debug the connection
if sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 -o PreferredAuthentications=password -o PubkeyAuthentication=no "$VPS_USER@$VPS_IP" "echo 'Connection successful'" 2>/dev/null; then
    echo "✓ VPS connection established"
else
    echo -e "${RED}❌ Failed to connect to VPS.${NC}"
    echo -e "${YELLOW}Debugging connection issue...${NC}"
    
    # Test if host is reachable
    if ping -c 1 -W 5 "$VPS_IP" >/dev/null 2>&1; then
        echo "✓ Host is reachable via ping"
    else
        echo "❌ Host is not reachable via ping"
    fi
    
    # Test if SSH port is open
    if timeout 5 bash -c "</dev/tcp/$VPS_IP/22" 2>/dev/null; then
        echo "✓ SSH port 22 is open"
    else
        echo "❌ SSH port 22 is not accessible"
    fi
    
    # Try to get more detailed SSH error
    echo -e "${YELLOW}Detailed SSH connection attempt:${NC}"
    sshpass -p "$VPS_PASSWORD" ssh -v -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 -o PreferredAuthentications=password -o PubkeyAuthentication=no "$VPS_USER@$VPS_IP" "echo 'Connection successful'" 2>&1 | head -20
    
    echo -e "${YELLOW}Possible solutions:${NC}"
    echo "1. Verify the password is correct"
    echo "2. Check if password authentication is enabled on the server"
    echo "3. Verify the username is correct (try 'ubuntu' instead of 'root')"
    echo "4. Check if the server requires key-based authentication only"
    echo "5. Verify the IP address is correct and accessible"
    
    exit 1
fi

echo -e "${YELLOW}Step 3: Setting up SSH key authentication...${NC}"

# Generate SSH key if it doesn't exist
SSH_KEY_NAME="agentic-${VPS_IP//\./-}"
SSH_KEY_PATH="$HOME/.ssh/$SSH_KEY_NAME"

if [ ! -f "$SSH_KEY_PATH" ]; then
    echo "Generating SSH key pair for this VPS..."
    ssh-keygen -t rsa -b 4096 -f "$SSH_KEY_PATH" -N "" -C "agentic-deployment-$VPS_IP"
    echo "✓ SSH key pair generated"
else
    echo "✓ SSH key pair already exists"
fi

# Copy public key to VPS
echo "Setting up passwordless authentication..."
run_with_password "mkdir -p ~/.ssh && chmod 700 ~/.ssh"
sshpass -p "$VPS_PASSWORD" ssh-copy-id -i "$SSH_KEY_PATH.pub" -o StrictHostKeyChecking=no "$VPS_USER@$VPS_IP"

# Test passwordless connection
if ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no "$VPS_USER@$VPS_IP" 'echo "SSH key authentication successful"'; then
    echo "✓ Passwordless SSH authentication working"
else
    echo -e "${RED}❌ SSH key authentication failed${NC}"
    exit 1
fi

# Update SSH config
echo "Updating SSH configuration..."
SSH_ALIAS="agentic-${VPS_IP//\./-}"
mkdir -p ~/.ssh

# Remove existing entry if it exists
sed -i "/^Host $SSH_ALIAS$/,/^$/d" ~/.ssh/config 2>/dev/null || true

# Add new entry
cat >> ~/.ssh/config << EOF

# Agentic Site VPS - $VPS_IP ($ENVIRONMENT)
Host $SSH_ALIAS
    HostName $VPS_IP
    User $VPS_USER
    IdentityFile $SSH_KEY_PATH
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    ServerAliveInterval 60
    ServerAliveCountMax 3
    ControlMaster auto
    ControlPath ~/.ssh/control-%r@%h:%p
    ControlPersist 10m

EOF

echo "✓ SSH configuration updated (alias: $SSH_ALIAS)"

# Update run_on_vps function to use the SSH alias
run_on_vps() {
    ssh "$SSH_ALIAS" "$1"
}

echo -e "${YELLOW}Step 4: Installing system dependencies on VPS...${NC}"

run_on_vps "
    echo 'Updating system packages...'
    apt-get update -y
    
    echo 'Installing essential packages...'
    apt-get install -y curl wget git unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release
    
    echo 'Installing Docker...'
    # Remove old Docker versions
    apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Add Docker GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo \"deb [arch=\$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \$(lsb_release -cs) stable\" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    
    echo 'Installing Docker Compose...'
    curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    echo 'Installing Nginx...'
    apt-get install -y nginx
    systemctl start nginx
    systemctl enable nginx
    
    echo 'Installing UFW firewall...'
    apt-get install -y ufw
    
    echo '✓ System dependencies installed'
"

echo -e "${YELLOW}Step 5: Configuring firewall and security...${NC}"

run_on_vps "
    echo 'Configuring UFW firewall...'
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    
    # Allow SSH
    ufw allow 22/tcp
    
    # Allow HTTP and HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # Allow development ports based on environment
    if [ '$ENVIRONMENT' = 'development' ]; then
        ufw allow 3001/tcp  # Frontend dev
        ufw allow 8001/tcp  # Backend dev
        ufw allow 5679/tcp  # n8n dev
        ufw allow 6380/tcp  # Redis dev
    else
        ufw allow 3000/tcp  # Frontend prod
        ufw allow 8000/tcp  # Backend prod
        ufw allow 5678/tcp  # n8n prod
        ufw allow 6379/tcp  # Redis prod
    fi
    
    # Allow monitoring ports
    ufw allow 9090/tcp  # Prometheus
    ufw allow 3001/tcp  # Grafana
    ufw allow 9100/tcp  # Node Exporter
    
    # Enable firewall
    ufw --force enable
    
    echo '✓ Firewall configured'
"

echo -e "${YELLOW}Step 6: Creating deployment directories...${NC}"

DEPLOY_PATH="/opt/docker-apps/$ENVIRONMENT/agentic-site"

run_on_vps "
    echo 'Creating deployment directories...'
    mkdir -p $DEPLOY_PATH
    mkdir -p /opt/docker-apps/shared/ssl
    mkdir -p /opt/docker-apps/shared/backups
    mkdir -p /var/log/agentic-site
    
    # Set proper permissions
    chown -R root:root /opt/docker-apps
    chmod -R 755 /opt/docker-apps
    
    echo '✓ Deployment directories created'
"

echo -e "${YELLOW}Step 7: Setting up Nginx configuration...${NC}"

# Create environment-specific nginx config
if [ "$ENVIRONMENT" = "development" ]; then
    DOMAIN="dev.consulting.sa"
    FRONTEND_PORT="3001"
    BACKEND_PORT="8001"
    N8N_PORT="5679"
else
    DOMAIN="consulting.sa"
    FRONTEND_PORT="3000"
    BACKEND_PORT="8000"
    N8N_PORT="5678"
fi

run_on_vps "
    echo 'Creating Nginx configuration for $ENVIRONMENT...'
    
    cat > /etc/nginx/sites-available/agentic-$ENVIRONMENT << 'EOF'
upstream frontend_$ENVIRONMENT {
    server 127.0.0.1:$FRONTEND_PORT;
}

upstream backend_$ENVIRONMENT {
    server 127.0.0.1:$BACKEND_PORT;
}

server {
    listen 80;
    server_name $DOMAIN;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection \"1; mode=block\";
    add_header Referrer-Policy \"strict-origin-when-cross-origin\";
    
    # Main application - proxy to Next.js
    location / {
        proxy_pass http://frontend_$ENVIRONMENT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 86400;
        proxy_connect_timeout 60;
        proxy_send_timeout 60;
    }
    
    # API routes - proxy to Python backend
    location /api/ {
        proxy_pass http://backend_$ENVIRONMENT/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
        proxy_connect_timeout 60;
        proxy_send_timeout 60;
    }
    
    # Backend admin interface
    location /backend/ {
        proxy_pass http://backend_$ENVIRONMENT/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # n8n interface
    location /n8n/ {
        proxy_pass http://127.0.0.1:$N8N_PORT/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://backend_$ENVIRONMENT/health;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Static files with caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        proxy_pass http://frontend_$ENVIRONMENT;
        proxy_cache_valid 200 1y;
        add_header Cache-Control \"public, immutable\";
    }
}
EOF

    # Enable the site
    ln -sf /etc/nginx/sites-available/agentic-$ENVIRONMENT /etc/nginx/sites-enabled/agentic-$ENVIRONMENT
    
    # Remove default site
    rm -f /etc/nginx/sites-enabled/default
    
    # Test nginx configuration
    nginx -t
    
    # Reload nginx
    systemctl reload nginx
    
    echo '✓ Nginx configuration created and enabled'
"

echo -e "${YELLOW}Step 8: Creating management scripts...${NC}"

run_on_vps "
    echo 'Creating management scripts...'
    
    # Status script
    cat > /usr/local/bin/agentic-$ENVIRONMENT-status.sh << 'EOF'
#!/bin/bash
echo \"=== Agentic Site $ENVIRONMENT Status ===\"
echo \"Timestamp: \$(date)\"
echo
echo \"=== Container Status ===\"
cd $DEPLOY_PATH && docker-compose ps 2>/dev/null || echo \"No containers running\"
echo
echo \"=== Port Status ===\"
netstat -tlnp | grep -E ':($FRONTEND_PORT|$BACKEND_PORT|$N8N_PORT)' || echo \"No services listening\"
echo
echo \"=== Nginx Status ===\"
systemctl status nginx --no-pager -l
echo
echo \"=== Disk Usage ===\"
df -h /
echo
echo \"=== Memory Usage ===\"
free -h
EOF

    # Restart script
    cat > /usr/local/bin/agentic-$ENVIRONMENT-restart.sh << 'EOF'
#!/bin/bash
echo \"=== Restarting Agentic Site $ENVIRONMENT ===\"
cd $DEPLOY_PATH
docker-compose down
docker-compose up -d
echo \"=== Restart Complete ===\"
EOF

    # Logs script
    cat > /usr/local/bin/agentic-$ENVIRONMENT-logs.sh << 'EOF'
#!/bin/bash
echo \"=== Agentic Site $ENVIRONMENT Logs ===\"
cd $DEPLOY_PATH
docker-compose logs -f --tail=100
EOF

    # Make scripts executable
    chmod +x /usr/local/bin/agentic-$ENVIRONMENT-*.sh
    
    echo '✓ Management scripts created'
"

echo -e "${YELLOW}Step 9: Setting up log rotation...${NC}"

run_on_vps "
    echo 'Setting up log rotation...'
    
    cat > /etc/logrotate.d/agentic-$ENVIRONMENT << 'EOF'
/var/log/agentic-site/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        systemctl reload nginx > /dev/null 2>&1 || true
    endscript
}
EOF

    echo '✓ Log rotation configured'
"

echo -e "${YELLOW}Step 10: Creating environment configuration...${NC}"

# Create environment-specific configuration
cat > ".env.$ENVIRONMENT" << EOF
# Agentic Site $ENVIRONMENT Environment Configuration
# Generated on $(date)

# Environment
NODE_ENV=$ENVIRONMENT
COMPOSE_PROJECT_NAME=agentic-$ENVIRONMENT

# Server Configuration
VPS_IP=$VPS_IP
DOMAIN=$DOMAIN
FRONTEND_PORT=$FRONTEND_PORT
BACKEND_PORT=$BACKEND_PORT

# Container Images (will be built locally)
FRONTEND_IMAGE=agentic-frontend-$ENVIRONMENT:latest
BACKEND_IMAGE=agentic-backend-$ENVIRONMENT:latest

# Database Configuration (add your actual values)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# AI Services (optional)
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Payment Integration (optional)
STRIPE_SECRET_KEY=your_stripe_secret
STRIPE_PUBLISHABLE_KEY=your_stripe_public
STRIPE_WEBHOOK_SECRET=your_stripe_webhook

# Communication Services (optional)
LIVEKIT_URL=your_livekit_url
LIVEKIT_API_KEY=your_livekit_key
LIVEKIT_API_SECRET=your_livekit_secret

# Workflow Automation
N8N_USER=admin
N8N_PASSWORD=admin123
N8N_URL=http://localhost:$N8N_PORT
N8N_BASE_URL=http://localhost:$N8N_PORT
N8N_API_KEY=your_n8n_key

# MCP Server Configuration
MCP_SERVER_URL=http://localhost:$BACKEND_PORT
MCP_SERVER_PORT=$BACKEND_PORT
N8N_MCP_PORT=8003

# GitHub Integration (optional)
GITHUB_TOKEN=your_github_token

# Logging
ADK_LOG_LEVEL=INFO
EOF

# Copy environment file to VPS
copy_with_password ".env.$ENVIRONMENT" "$DEPLOY_PATH/.env"

echo "✓ Environment configuration created"

echo -e "${YELLOW}Step 11: Final system optimization...${NC}"

run_on_vps "
    echo 'Optimizing system settings...'
    
    # Increase file limits
    cat >> /etc/security/limits.conf << 'EOF'
* soft nofile 65536
* hard nofile 65536
root soft nofile 65536
root hard nofile 65536
EOF

    # Optimize sysctl settings
    cat >> /etc/sysctl.conf << 'EOF'
# Agentic Site Optimizations
net.core.somaxconn = 65536
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 65536
net.ipv4.tcp_keepalive_time = 600
net.ipv4.tcp_keepalive_intvl = 60
net.ipv4.tcp_keepalive_probes = 10
vm.swappiness = 10
EOF

    sysctl -p
    
    # Set timezone
    timedatectl set-timezone UTC
    
    echo '✓ System optimization complete'
"

echo
echo -e "${GREEN}🎉 VPS Setup Complete!${NC}"
echo -e "${BLUE}=================================${NC}"
echo
echo -e "${CYAN}VPS Information:${NC}"
echo "IP Address: $VPS_IP"
echo "SSH Alias: $SSH_ALIAS"
echo "Environment: $ENVIRONMENT"
echo "Domain: $DOMAIN"
echo "Deploy Path: $DEPLOY_PATH"
echo
echo -e "${CYAN}Quick Access Commands:${NC}"
echo "Connect to VPS: ssh $SSH_ALIAS"
echo "Check status: ssh $SSH_ALIAS '/usr/local/bin/agentic-$ENVIRONMENT-status.sh'"
echo "View logs: ssh $SSH_ALIAS '/usr/local/bin/agentic-$ENVIRONMENT-logs.sh'"
echo "Restart services: ssh $SSH_ALIAS '/usr/local/bin/agentic-$ENVIRONMENT-restart.sh'"
echo
echo -e "${CYAN}Next Steps:${NC}"
echo "1. Update .env.$ENVIRONMENT with your actual API keys and configuration"
echo "2. Run the deployment script: ./infrastructure/scripts/deploy-to-vps.sh $SSH_ALIAS $ENVIRONMENT"
echo "3. Access your site at: http://$DOMAIN"
echo
echo -e "${CYAN}Files Created:${NC}"
echo "• SSH Key: $SSH_KEY_PATH"
echo "• Environment Config: .env.$ENVIRONMENT"
echo "• SSH Config Entry: $SSH_ALIAS"
echo
echo -e "${GREEN}VPS is now ready for deployment!${NC}"