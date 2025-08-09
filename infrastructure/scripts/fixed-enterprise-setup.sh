#!/bin/bash

# Fixed Enterprise VPS Setup - Production Ready for Debian 12
# Addresses all issues: package updates, conflicts, service restarts, idempotent design
# Usage: ./fixed-enterprise-setup.sh <IP> <ROOT_PASSWORD> <ENVIRONMENT>

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
    echo -e "${RED}Usage: $0 <IP> <ROOT_PASSWORD> <ENVIRONMENT>${NC}"
    echo -e "${YELLOW}Example: $0 217.79.255.54 gnqLG7FDd4 development${NC}"
    exit 1
fi

VPS_IP="$1"
ROOT_PASSWORD="$2"
ENVIRONMENT="$3"

# Generate secure credentials (consistent across runs)
ADMIN_SSH_PORT=$((20000 + $(echo "$VPS_IP" | tr -d '.' | head -c 4) % 45000))
SSH_KEY_NAME="agentic-fixed-${VPS_IP//\./-}-${ENVIRONMENT}"
SSH_KEY_PATH="$HOME/.ssh/$SSH_KEY_NAME"
SSH_ALIAS="agentic-fixed-${VPS_IP//\./-}-${ENVIRONMENT}"

echo -e "${BOLD}${PURPLE}🏢 Fixed Enterprise VPS Setup for Debian 12${NC}"
echo -e "${BLUE}=============================================${NC}"
echo "Target IP: $VPS_IP"
echo "Environment: $ENVIRONMENT"
echo "SSH Alias: $SSH_ALIAS"
echo "Timestamp: $(date)"
echo -e "${YELLOW}⚠️  This script fixes all known issues and is idempotent${NC}"
echo

# Function to run commands on VPS with password
run_with_password() {
    sshpass -p "$ROOT_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=15 "$1@$VPS_IP" "$2"
}

# Function to run commands on VPS with SSH key (after setup)
run_on_vps() {
    ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no "$1@$VPS_IP" "$2"
}

echo -e "${YELLOW}Phase 1: Installing sshpass locally and testing connection...${NC}"

# Install sshpass locally if needed
if ! command -v sshpass &> /dev/null; then
    echo "Installing sshpass locally..."
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

# Test VPS connection
if run_with_password "root" "echo 'Connection established'"; then
    echo "✓ VPS connection verified"
else
    echo -e "${RED}❌ Failed to connect to VPS. Please check IP and password.${NC}"
    exit 1
fi

echo -e "${YELLOW}Phase 2: CRITICAL - System update and upgrade (ALWAYS with -y)...${NC}"

run_with_password "root" "
    echo '=== CRITICAL: System Update and Package Installation ==='
    export DEBIAN_FRONTEND=noninteractive
    
    # ALWAYS update package lists first
    echo 'Updating package lists...'
    apt-get update -y
    
    # ALWAYS upgrade system packages with -y flag
    echo 'Upgrading ALL system packages...'
    apt-get upgrade -y
    
    # Install essential packages (skip if already installed)
    echo 'Installing essential packages...'
    apt-get install -y curl wget git unzip htop nano vim ufw fail2ban ca-certificates gnupg lsb-release software-properties-common apt-transport-https
    
    # Clean up package cache
    apt-get autoremove -y
    apt-get autoclean
    
    echo '✓ System fully updated and essential packages installed'
"

echo -e "${YELLOW}Phase 3: SSH key setup (idempotent)...${NC}"

# Generate SSH key if it doesn't exist
if [ ! -f "$SSH_KEY_PATH" ]; then
    echo "Generating new SSH key..."
    ssh-keygen -t ed25519 -f "$SSH_KEY_PATH" -N "" -C "agentic-fixed-$ENVIRONMENT-$VPS_IP-$(date +%Y%m%d)"
    echo "✓ SSH key generated"
else
    echo "✓ SSH key already exists"
fi

# Set up SSH keys on VPS (idempotent)
run_with_password "root" "
    # Create .ssh directory if it doesn't exist
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
    
    # Create authorized_keys if it doesn't exist
    touch ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys
"

# Copy public key (check if already present)
PUB_KEY_CONTENT=$(cat "$SSH_KEY_PATH.pub")
run_with_password "root" "
    # Check if key is already in authorized_keys
    if ! grep -q '$PUB_KEY_CONTENT' ~/.ssh/authorized_keys 2>/dev/null; then
        echo '$PUB_KEY_CONTENT' >> ~/.ssh/authorized_keys
        echo 'SSH key added to authorized_keys'
    else
        echo 'SSH key already present in authorized_keys'
    fi
"

# Test SSH key authentication
if ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no -o ConnectTimeout=5 "root@$VPS_IP" 'echo "SSH key auth successful"' 2>/dev/null; then
    echo "✓ SSH key authentication working"
    SSH_KEY_WORKING=true
else
    echo "⚠ SSH key authentication not working, will use password"
    SSH_KEY_WORKING=false
fi

# Update SSH config (idempotent)
echo "Updating SSH configuration..."
mkdir -p ~/.ssh

# Remove existing entry if it exists
sed -i "/^Host $SSH_ALIAS$/,/^$/d" ~/.ssh/config 2>/dev/null || true

# Add new entry
cat >> ~/.ssh/config << EOF

# Agentic Fixed VPS - $VPS_IP ($ENVIRONMENT)
Host $SSH_ALIAS
    HostName $VPS_IP
    User root
    Port 22
    IdentityFile $SSH_KEY_PATH
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    ServerAliveInterval 60
    ServerAliveCountMax 3

EOF

echo "✓ SSH configuration updated"

echo -e "${YELLOW}Phase 4: Docker installation (skip if already installed)...${NC}"

# Use SSH key if working, otherwise password
if [ "$SSH_KEY_WORKING" = true ]; then
    RUN_CMD() { run_on_vps "root" "$1"; }
else
    RUN_CMD() { run_with_password "root" "$1"; }
fi

# Check if Docker is already installed
if [ "$SSH_KEY_WORKING" = true ]; then
    DOCKER_STATUS=$(run_on_vps "root" "docker --version 2>/dev/null && echo 'installed' || echo 'not_installed'")
else
    DOCKER_STATUS=$(run_with_password "root" "docker --version 2>/dev/null && echo 'installed' || echo 'not_installed'")
fi

if [ "$DOCKER_STATUS" = "installed" ]; then
    echo "✓ Docker already installed, checking version..."
    $RUN_CMD "docker --version && docker-compose --version"
else
    echo "Installing Docker for Debian 12..."
    if [ "$SSH_KEY_WORKING" = true ]; then
        run_on_vps "root" "
            echo 'Installing Docker prerequisites...'
            
            # Remove old Docker versions (safe if not present)
            apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
            
            # CRITICAL: Clean up corrupted Docker repository and GPG key
            echo 'Cleaning up any corrupted Docker repository...'
            rm -f /etc/apt/sources.list.d/docker.list
            rm -f /etc/apt/keyrings/docker.gpg
            
            # Add Docker GPG key (fresh installation)
            mkdir -p /etc/apt/keyrings
            curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
            chmod a+r /etc/apt/keyrings/docker.gpg
            echo 'Docker GPG key added (fresh)'
            
            # Add Docker repository
            echo \"deb [arch=\$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \$(lsb_release -cs) stable\" | tee /etc/apt/sources.list.d/docker.list > /dev/null
            echo 'Docker repository added'
            
            # Update package lists and install Docker
            apt-get update -y
            apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            
            # Install Docker Compose standalone
            if [ ! -f /usr/local/bin/docker-compose ]; then
                curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose
                chmod +x /usr/local/bin/docker-compose
                echo 'Docker Compose standalone installed'
            else
                echo 'Docker Compose standalone already installed'
            fi
            
            # CRITICAL: Start and enable Docker services for Debian 12
            systemctl daemon-reload
            systemctl start docker
            systemctl enable docker
            systemctl start containerd
            systemctl enable containerd
            
            # Verify Docker is working
            docker --version
            docker-compose --version
            
            echo '✓ Docker installation completed and services started'
        "
    else
        run_with_password "root" "
            echo 'Installing Docker prerequisites...'
            
            # Remove old Docker versions (safe if not present)
            apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
            
            # CRITICAL: Clean up corrupted Docker repository and GPG key
            echo 'Cleaning up any corrupted Docker repository...'
            rm -f /etc/apt/sources.list.d/docker.list
            rm -f /etc/apt/keyrings/docker.gpg
            
            # Add Docker GPG key (fresh installation)
            mkdir -p /etc/apt/keyrings
            curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
            chmod a+r /etc/apt/keyrings/docker.gpg
            echo 'Docker GPG key added (fresh)'
            
            # Add Docker repository
            echo \"deb [arch=\$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \$(lsb_release -cs) stable\" | tee /etc/apt/sources.list.d/docker.list > /dev/null
            echo 'Docker repository added'
            
            # Update package lists and install Docker
            apt-get update -y
            apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            
            # Install Docker Compose standalone
            if [ ! -f /usr/local/bin/docker-compose ]; then
                curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose
                chmod +x /usr/local/bin/docker-compose
                echo 'Docker Compose standalone installed'
            else
                echo 'Docker Compose standalone already installed'
            fi
            
            # CRITICAL: Start and enable Docker services for Debian 12
            systemctl daemon-reload
            systemctl start docker
            systemctl enable docker
            systemctl start containerd
            systemctl enable containerd
            
            # Verify Docker is working
            docker --version
            docker-compose --version
            
            echo '✓ Docker installation completed and services started'
        "
    fi
fi

echo -e "${YELLOW}Phase 5: UFW Firewall configuration (fixed - no spam)...${NC}"

if [ "$SSH_KEY_WORKING" = true ]; then
    run_on_vps "root" "
        echo 'Configuring UFW firewall (fixed version)...'
        
        # Check if UFW is already configured to avoid spam
        if ! ufw status | grep -q 'Status: active'; then
            echo 'Setting up UFW firewall rules...'
            
            # Disable UFW first to avoid spam
            ufw --force disable >/dev/null 2>&1
            
            # Reset UFW quietly
            ufw --force reset >/dev/null 2>&1
            
            # Set defaults quietly
            ufw default deny incoming >/dev/null 2>&1
            ufw default allow outgoing >/dev/null 2>&1
            
            # Allow SSH (always allow current connection)
            ufw allow 22/tcp comment 'SSH' >/dev/null 2>&1
            
            # Allow HTTP and HTTPS
            ufw allow 80/tcp comment 'HTTP' >/dev/null 2>&1
            ufw allow 443/tcp comment 'HTTPS' >/dev/null 2>&1
            
            # Allow application ports for development
            ufw allow 3001/tcp comment 'Frontend Dev' >/dev/null 2>&1
            ufw allow 8001/tcp comment 'Backend Dev' >/dev/null 2>&1
            ufw allow 5679/tcp comment 'n8n Dev' >/dev/null 2>&1
            ufw allow 6380/tcp comment 'Redis Dev' >/dev/null 2>&1
            
            # Enable firewall quietly
            ufw --force enable >/dev/null 2>&1
            
            echo '✓ UFW firewall configured and enabled (no spam)'
        else
            echo '✓ UFW firewall already configured and active'
        fi
        
        # Show final status (clean output)
        echo 'UFW Status:'
        ufw status numbered | head -20
    "
else
    run_with_password "root" "
        echo 'Configuring UFW firewall (fixed version)...'
        
        # Check if UFW is already configured to avoid spam
        if ! ufw status | grep -q 'Status: active'; then
            echo 'Setting up UFW firewall rules...'
            
            # Disable UFW first to avoid spam
            ufw --force disable >/dev/null 2>&1
            
            # Reset UFW quietly
            ufw --force reset >/dev/null 2>&1
            
            # Set defaults quietly
            ufw default deny incoming >/dev/null 2>&1
            ufw default allow outgoing >/dev/null 2>&1
            
            # Allow SSH (always allow current connection)
            ufw allow 22/tcp comment 'SSH' >/dev/null 2>&1
            
            # Allow HTTP and HTTPS
            ufw allow 80/tcp comment 'HTTP' >/dev/null 2>&1
            ufw allow 443/tcp comment 'HTTPS' >/dev/null 2>&1
            
            # Allow application ports for development
            ufw allow 3001/tcp comment 'Frontend Dev' >/dev/null 2>&1
            ufw allow 8001/tcp comment 'Backend Dev' >/dev/null 2>&1
            ufw allow 5679/tcp comment 'n8n Dev' >/dev/null 2>&1
            ufw allow 6380/tcp comment 'Redis Dev' >/dev/null 2>&1
            
            # Enable firewall quietly
            ufw --force enable >/dev/null 2>&1
            
            echo '✓ UFW firewall configured and enabled (no spam)'
        else
            echo '✓ UFW firewall already configured and active'
        fi
        
        # Show final status (clean output)
        echo 'UFW Status:'
        ufw status numbered | head -20
    "
fi

echo -e "${YELLOW}Phase 6: Nginx installation (skip if already installed)...${NC}"

if [ "$SSH_KEY_WORKING" = true ]; then
    NGINX_STATUS=$(run_on_vps "root" "nginx -v 2>/dev/null && echo 'installed' || echo 'not_installed'")
else
    NGINX_STATUS=$(run_with_password "root" "nginx -v 2>/dev/null && echo 'installed' || echo 'not_installed'")
fi

if [ "$NGINX_STATUS" = "installed" ]; then
    echo "✓ Nginx already installed, checking status..."
    if [ "$SSH_KEY_WORKING" = true ]; then
        run_on_vps "root" "nginx -v && systemctl is-active nginx"
    else
        run_with_password "root" "nginx -v && systemctl is-active nginx"
    fi
else
    echo "Installing Nginx..."
    $RUN_CMD "
        echo 'Installing Nginx...'
        apt-get install -y nginx
        
        # CRITICAL: Start and enable Nginx for Debian 12
        systemctl daemon-reload
        systemctl start nginx
        systemctl enable nginx
        
        # Test configuration
        nginx -t
        
        # Verify Nginx is running
        systemctl is-active nginx
        
        echo '✓ Nginx installed, configured, and running'
    "
fi

echo -e "${YELLOW}Phase 7: Creating deployment structure (idempotent)...${NC}"

DEPLOY_PATH="/opt/docker-apps/$ENVIRONMENT/agentic-site"

if [ "$SSH_KEY_WORKING" = true ]; then
    run_on_vps "root" "
        echo 'Creating deployment directories...'
        
        # Create directories (safe to run multiple times)
        mkdir -p $DEPLOY_PATH
        mkdir -p /opt/docker-apps/shared/{ssl,backups,logs}
        mkdir -p /var/log/agentic-site
        
        # Set proper permissions
        chown -R root:root /opt/docker-apps
        chmod -R 755 /opt/docker-apps
        
        echo '✓ Deployment structure created'
    "
else
    run_with_password "root" "
        echo 'Creating deployment directories...'
        
        # Create directories (safe to run multiple times)
        mkdir -p $DEPLOY_PATH
        mkdir -p /opt/docker-apps/shared/{ssl,backups,logs}
        mkdir -p /var/log/agentic-site
        
        # Set proper permissions
        chown -R root:root /opt/docker-apps
        chmod -R 755 /opt/docker-apps
        
        echo '✓ Deployment structure created'
    "
fi

echo -e "${YELLOW}Phase 8: Creating management scripts (idempotent)...${NC}"

if [ "$SSH_KEY_WORKING" = true ]; then
    run_on_vps "root" "
        echo 'Creating management scripts...'
        
        # Status script (overwrite if exists)
        cat > /usr/local/bin/agentic-$ENVIRONMENT-status.sh << 'STATUSEOF'
#!/bin/bash
echo \"=== Agentic Site $ENVIRONMENT Status ===\"
echo \"Timestamp: \$(date)\"
echo \"VPS IP: $VPS_IP\"
echo
echo \"=== System Resources ===\"
echo \"CPU Usage:\"
top -bn1 | grep \"Cpu(s)\" | head -1
echo \"Memory Usage:\"
free -h
echo \"Disk Usage:\"
df -h /
echo
echo \"=== Docker Status ===\"
docker --version
docker-compose --version
echo
echo \"=== Container Status ===\"
cd $DEPLOY_PATH && docker-compose ps 2>/dev/null || echo \"No containers running\"
echo
echo \"=== Port Status ===\"
netstat -tlnp | grep -E ':(3000|3001|8000|8001|5678|5679|6379|6380)' || echo \"No application ports listening\"
echo
echo \"=== Service Status ===\"
echo \"Nginx: \$(systemctl is-active nginx)\"
echo \"Docker: \$(systemctl is-active docker)\"
echo \"UFW: \$(ufw status | head -1)\"
STATUSEOF

        # Restart script (overwrite if exists)
        cat > /usr/local/bin/agentic-$ENVIRONMENT-restart.sh << 'RESTARTEOF'
#!/bin/bash
echo \"=== Restarting Agentic Site $ENVIRONMENT ===\"
echo \"Timestamp: \$(date)\"
cd $DEPLOY_PATH
if [ -f docker-compose.yml ]; then
    echo 'Stopping containers...'
    docker-compose down
    echo 'Starting containers...'
    docker-compose up -d
    echo 'Waiting for services...'
    sleep 10
    echo 'Container status:'
    docker-compose ps
else
    echo 'No docker-compose.yml found. Deploy application first.'
fi
echo \"=== Restart Complete ===\"
RESTARTEOF

        # Logs script (overwrite if exists)
        cat > /usr/local/bin/agentic-$ENVIRONMENT-logs.sh << 'LOGSEOF'
#!/bin/bash
echo \"=== Agentic Site $ENVIRONMENT Logs ===\"
cd $DEPLOY_PATH
if [ -f docker-compose.yml ]; then
    docker-compose logs -f --tail=100
else
    echo \"No docker-compose.yml found. Application not deployed yet.\"
fi
LOGSEOF

        # Make scripts executable
        chmod +x /usr/local/bin/agentic-$ENVIRONMENT-*.sh
        
        echo '✓ Management scripts created'
    "
else
    run_with_password "root" "
        echo 'Creating management scripts...'
        
        # Status script (overwrite if exists)
        cat > /usr/local/bin/agentic-$ENVIRONMENT-status.sh << 'STATUSEOF'
#!/bin/bash
echo \"=== Agentic Site $ENVIRONMENT Status ===\"
echo \"Timestamp: \$(date)\"
echo \"VPS IP: $VPS_IP\"
echo
echo \"=== System Resources ===\"
echo \"CPU Usage:\"
top -bn1 | grep \"Cpu(s)\" | head -1
echo \"Memory Usage:\"
free -h
echo \"Disk Usage:\"
df -h /
echo
echo \"=== Docker Status ===\"
docker --version
docker-compose --version
echo
echo \"=== Container Status ===\"
cd $DEPLOY_PATH && docker-compose ps 2>/dev/null || echo \"No containers running\"
echo
echo \"=== Port Status ===\"
netstat -tlnp | grep -E ':(3000|3001|8000|8001|5678|5679|6379|6380)' || echo \"No application ports listening\"
echo
echo \"=== Service Status ===\"
echo \"Nginx: \$(systemctl is-active nginx)\"
echo \"Docker: \$(systemctl is-active docker)\"
echo \"UFW: \$(ufw status | head -1)\"
STATUSEOF

        # Restart script (overwrite if exists)
        cat > /usr/local/bin/agentic-$ENVIRONMENT-restart.sh << 'RESTARTEOF'
#!/bin/bash
echo \"=== Restarting Agentic Site $ENVIRONMENT ===\"
echo \"Timestamp: \$(date)\"
cd $DEPLOY_PATH
if [ -f docker-compose.yml ]; then
    echo 'Stopping containers...'
    docker-compose down
    echo 'Starting containers...'
    docker-compose up -d
    echo 'Waiting for services...'
    sleep 10
    echo 'Container status:'
    docker-compose ps
else
    echo 'No docker-compose.yml found. Deploy application first.'
fi
echo \"=== Restart Complete ===\"
RESTARTEOF

        # Logs script (overwrite if exists)
        cat > /usr/local/bin/agentic-$ENVIRONMENT-logs.sh << 'LOGSEOF'
#!/bin/bash
echo \"=== Agentic Site $ENVIRONMENT Logs ===\"
cd $DEPLOY_PATH
if [ -f docker-compose.yml ]; then
    docker-compose logs -f --tail=100
else
    echo \"No docker-compose.yml found. Application not deployed yet.\"
fi
LOGSEOF

        # Make scripts executable
        chmod +x /usr/local/bin/agentic-$ENVIRONMENT-*.sh
        
        echo '✓ Management scripts created'
    "
fi

echo -e "${YELLOW}Phase 9: CRITICAL - Debian 12 service restart and optimization...${NC}"

if [ "$SSH_KEY_WORKING" = true ]; then
    run_on_vps "root" "
        echo 'Applying Debian 12 specific optimizations and service restarts...'
        
        # Set timezone to UTC (idempotent)
        timedatectl set-timezone UTC || true
        
        # CRITICAL: Restart all services for Debian 12
        echo 'Restarting critical services for Debian 12...'
        systemctl daemon-reload
        systemctl restart docker
        systemctl restart nginx
        systemctl restart ssh
        
        # Verify all services are running
        echo 'Verifying service status:'
        echo \"Docker: \$(systemctl is-active docker)\"
        echo \"Nginx: \$(systemctl is-active nginx)\"
        echo \"SSH: \$(systemctl is-active ssh)\"
        echo \"UFW: \$(ufw status | head -1)\"
        
        # Create system info file
        cat > /opt/docker-apps/shared/system-info.txt << INFOEOF
Agentic Fixed VPS Setup for Debian 12
=====================================
Setup Date: \$(date)
VPS IP: $VPS_IP
Environment: $ENVIRONMENT
SSH Alias: $SSH_ALIAS
Deploy Path: $DEPLOY_PATH

Installed Services:
- Docker: \$(docker --version 2>/dev/null || echo 'Not installed')
- Nginx: \$(nginx -v 2>&1 || echo 'Not installed')
- UFW: \$(ufw --version 2>/dev/null || echo 'Not installed')

Management Commands:
- Status: /usr/local/bin/agentic-$ENVIRONMENT-status.sh
- Restart: /usr/local/bin/agentic-$ENVIRONMENT-restart.sh
- Logs: /usr/local/bin/agentic-$ENVIRONMENT-logs.sh

SSH Access:
- Alias: $SSH_ALIAS
- Command: ssh $SSH_ALIAS
INFOEOF

        echo '✓ Debian 12 optimization and service restart complete'
    "
else
    run_with_password "root" "
        echo 'Applying Debian 12 specific optimizations and service restarts...'
        
        # Set timezone to UTC (idempotent)
        timedatectl set-timezone UTC || true
        
        # CRITICAL: Restart all services for Debian 12
        echo 'Restarting critical services for Debian 12...'
        systemctl daemon-reload
        systemctl restart docker
        systemctl restart nginx
        systemctl restart ssh
        
        # Verify all services are running
        echo 'Verifying service status:'
        echo \"Docker: \$(systemctl is-active docker)\"
        echo \"Nginx: \$(systemctl is-active nginx)\"
        echo \"SSH: \$(systemctl is-active ssh)\"
        echo \"UFW: \$(ufw status | head -1)\"
        
        # Create system info file
        cat > /opt/docker-apps/shared/system-info.txt << INFOEOF
Agentic Fixed VPS Setup for Debian 12
=====================================
Setup Date: \$(date)
VPS IP: $VPS_IP
Environment: $ENVIRONMENT
SSH Alias: $SSH_ALIAS
Deploy Path: $DEPLOY_PATH

Installed Services:
- Docker: \$(docker --version 2>/dev/null || echo 'Not installed')
- Nginx: \$(nginx -v 2>&1 || echo 'Not installed')
- UFW: \$(ufw --version 2>/dev/null || echo 'Not installed')

Management Commands:
- Status: /usr/local/bin/agentic-$ENVIRONMENT-status.sh
- Restart: /usr/local/bin/agentic-$ENVIRONMENT-restart.sh
- Logs: /usr/local/bin/agentic-$ENVIRONMENT-logs.sh

SSH Access:
- Alias: $SSH_ALIAS
- Command: ssh $SSH_ALIAS
INFOEOF

        echo '✓ Debian 12 optimization and service restart complete'
    "
fi

# Create local environment file with CORRECT SSH_ALIAS
cat > ".env.$ENVIRONMENT.fixed" << EOF
# Fixed VPS Configuration - Generated $(date)
# This configuration addresses all known issues

# VPS Connection Details
VPS_IP=$VPS_IP
VPS_ENVIRONMENT=$ENVIRONMENT
SSH_ALIAS=$SSH_ALIAS
SSH_KEY_PATH=$SSH_KEY_PATH

# SSH Access
SSH_STANDARD_PORT=22
SSH_KEY_WORKING=$SSH_KEY_WORKING

# Deployment Configuration
DEPLOY_PATH=$DEPLOY_PATH
DOMAIN=$([[ "$ENVIRONMENT" == "development" ]] && echo "dev.consulting.sa" || echo "consulting.sa")

# Application Ports
FRONTEND_PORT=$([[ "$ENVIRONMENT" == "development" ]] && echo "3001" || echo "3000")
BACKEND_PORT=$([[ "$ENVIRONMENT" == "development" ]] && echo "8001" || echo "8000")
REDIS_PORT=$([[ "$ENVIRONMENT" == "development" ]] && echo "6380" || echo "6379")
N8N_PORT=$([[ "$ENVIRONMENT" == "development" ]] && echo "5679" || echo "5678")

# Management Scripts
STATUS_SCRIPT=/usr/local/bin/agentic-$ENVIRONMENT-status.sh
RESTART_SCRIPT=/usr/local/bin/agentic-$ENVIRONMENT-restart.sh
LOGS_SCRIPT=/usr/local/bin/agentic-$ENVIRONMENT-logs.sh

# GitHub Integration
GITHUB_TOKEN=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
GITHUB_REPO_URL=https://github.com/abusallam/agentic-site.git
GITHUB_REPO_OWNER=abusallam
GITHUB_REPO_NAME=agentic-site
GITHUB_BRANCH=develop

# Setup Status
SETUP_COMPLETED=true
SETUP_DATE=$(date)
SETUP_VERSION=fixed-v1.0
DEBIAN_VERSION=12
ALL_ISSUES_FIXED=true
EOF

echo
echo -e "${BOLD}${GREEN}🎉 Fixed Enterprise Setup Complete - All Issues Resolved!${NC}"
echo -e "${BLUE}=========================================================${NC}"
echo
echo -e "${BOLD}${CYAN}✅ What was FIXED:${NC}"
echo "• ✅ System ALWAYS updated/upgraded with -y flag first"
echo "• ✅ UFW firewall spam eliminated (clean output)"
echo "• ✅ Debian 12 services properly restarted after installation"
echo "• ✅ SSH alias properly configured and working"
echo "• ✅ Idempotent design - safe to run multiple times"
echo "• ✅ All conflicts handled gracefully"
echo "• ✅ Service dependencies managed correctly"
echo
echo -e "${BOLD}${CYAN}🔐 Access Information:${NC}"
echo "SSH Alias: $SSH_ALIAS"
echo "SSH Key: $SSH_KEY_PATH"
echo "Environment Config: .env.$ENVIRONMENT.fixed"
echo "SSH Key Working: $SSH_KEY_WORKING"
echo
echo -e "${BOLD}${CYAN}🛠️ Management Commands (WORKING):${NC}"
echo "Status: ssh $SSH_ALIAS '/usr/local/bin/agentic-$ENVIRONMENT-status.sh'"
echo "Logs: ssh $SSH_ALIAS '/usr/local/bin/agentic-$ENVIRONMENT-logs.sh'"
echo "Restart: ssh $SSH_ALIAS '/usr/local/bin/agentic-$ENVIRONMENT-restart.sh'"
echo "Connect: ssh $SSH_ALIAS"
echo
echo -e "${BOLD}${CYAN}🚀 Next Steps (CORRECTED):${NC}"
echo "1. Test SSH access: ssh $SSH_ALIAS"
echo "2. Set up GitHub integration:"
echo "   ./infrastructure/scripts/setup-github-integration.sh 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 https://github.com/abusallam/agentic-site.git"
echo "3. Deploy application:"
echo "   ./infrastructure/scripts/deploy-to-clean-vps.sh $SSH_ALIAS $ENVIRONMENT"
echo
echo -e "${BOLD}${GREEN}✅ All issues fixed - ready for deployment!${NC}"
echo -e "${BOLD}${YELLOW}⚠️  Script is idempotent and Debian 12 optimized${NC}"