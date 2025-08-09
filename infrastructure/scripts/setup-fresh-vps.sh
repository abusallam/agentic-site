#!/bin/bash

# Fresh VPS Setup Script - Professional Server Administration
# This script sets up a new Debian 12 VPS with proper security practices
# Usage: ./setup-fresh-vps.sh <IP> <ROOT_PASSWORD> <ENVIRONMENT>

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
    echo -e "${RED}Usage: $0 <IP> <ROOT_PASSWORD> <ENVIRONMENT>${NC}"
    echo -e "${YELLOW}Example: $0 217.79.255.54 xxXNCpx9Cz development${NC}"
    echo -e "${YELLOW}Example: $0 192.168.1.100 mypassword production${NC}"
    exit 1
fi

VPS_IP="$1"
ROOT_PASSWORD="$2"
ENVIRONMENT="$3"

# Generate secure admin port (random port between 10000-65000)
ADMIN_SSH_PORT=$((10000 + RANDOM % 55000))
NEW_ROOT_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

echo -e "${PURPLE}🚀 Fresh VPS Setup - Professional Server Administration${NC}"
echo -e "${BLUE}=======================================================${NC}"
echo "Target IP: $VPS_IP"
echo "Environment: $ENVIRONMENT"
echo "Admin SSH Port: $ADMIN_SSH_PORT (SAVE THIS!)"
echo "Timestamp: $(date)"
echo

# Function to run commands on VPS with password
run_with_password() {
    sshpass -p "$ROOT_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 "$1@$VPS_IP" "$2"
}

# Function to copy files to VPS with password
copy_with_password() {
    sshpass -p "$ROOT_PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$1" "root@$VPS_IP:$2"
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

if run_with_password "root" "echo 'Connection successful'"; then
    echo "✓ VPS connection established"
else
    echo -e "${RED}❌ Failed to connect to VPS. Please check IP and password.${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 3: System update and essential packages...${NC}"

run_with_password "root" "
    echo 'Updating system packages...'
    apt-get update -y
    apt-get upgrade -y
    
    echo 'Installing essential packages...'
    apt-get install -y curl wget git unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release htop nano vim ufw fail2ban
    
    echo '✓ System updated and essential packages installed'
"

echo -e "${YELLOW}Step 4: Installing Docker and Docker Compose...${NC}"

run_with_password "root" "
    echo 'Installing Docker...'
    # Remove old Docker versions
    apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Add Docker GPG key
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo \"deb [arch=\$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \$(lsb_release -cs) stable\" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    
    echo 'Installing Docker Compose...'
    curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    # Verify installation
    docker --version
    docker-compose --version
    
    echo '✓ Docker and Docker Compose installed'
"

echo -e "${YELLOW}Step 5: Installing and configuring Nginx...${NC}"

run_with_password "root" "
    echo 'Installing Nginx...'
    apt-get install -y nginx
    
    # Start and enable Nginx
    systemctl start nginx
    systemctl enable nginx
    
    # Create basic security configuration
    cat > /etc/nginx/conf.d/security.conf << 'EOF'
# Security headers
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection \"1; mode=block\";
add_header Referrer-Policy \"strict-origin-when-cross-origin\";
add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;

# Hide Nginx version
server_tokens off;

# Limit request size
client_max_body_size 10M;
EOF
    
    # Test nginx configuration
    nginx -t
    
    echo '✓ Nginx installed and configured'
"

echo -e "${YELLOW}Step 6: Setting up SSH keys (keeping password as backup)...${NC}"

# Generate SSH key locally
SSH_KEY_NAME="agentic-${VPS_IP//\./-}-${ENVIRONMENT}"
SSH_KEY_PATH="$HOME/.ssh/$SSH_KEY_NAME"

if [ ! -f "$SSH_KEY_PATH" ]; then
    echo "Generating SSH key pair..."
    ssh-keygen -t rsa -b 4096 -f "$SSH_KEY_PATH" -N "" -C "agentic-$ENVIRONMENT-$VPS_IP-$(date +%Y%m%d)"
    echo "✓ SSH key pair generated"
else
    echo "✓ SSH key pair already exists"
fi

# Copy public key to VPS
echo "Setting up SSH key authentication..."
run_with_password "root" "mkdir -p ~/.ssh && chmod 700 ~/.ssh"
sshpass -p "$ROOT_PASSWORD" ssh-copy-id -i "$SSH_KEY_PATH.pub" -o StrictHostKeyChecking=no "root@$VPS_IP"

# Test SSH key authentication
if ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no "root@$VPS_IP" 'echo "SSH key authentication successful"'; then
    echo "✓ SSH key authentication working"
else
    echo -e "${RED}❌ SSH key authentication failed${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 7: Configuring secure SSH (keeping password as admin backup)...${NC}"

# Update SSH config
SSH_ALIAS="agentic-${VPS_IP//\./-}-${ENVIRONMENT}"
mkdir -p ~/.ssh

# Remove existing entry if it exists
sed -i "/^Host $SSH_ALIAS$/,/^$/d" ~/.ssh/config 2>/dev/null || true

# Add new entry
cat >> ~/.ssh/config << EOF

# Agentic Site VPS - $VPS_IP ($ENVIRONMENT)
Host $SSH_ALIAS
    HostName $VPS_IP
    User root
    Port 22
    IdentityFile $SSH_KEY_PATH
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    ServerAliveInterval 60
    ServerAliveCountMax 3
    ControlMaster auto
    ControlPath ~/.ssh/control-%r@%h:%p
    ControlPersist 10m

# Admin backup access (use only in emergency)
Host $SSH_ALIAS-admin
    HostName $VPS_IP
    User root
    Port $ADMIN_SSH_PORT
    PreferredAuthentications password
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

EOF

echo "✓ SSH configuration updated (alias: $SSH_ALIAS)"

# Configure SSH on server (secure but keep password backup)
ssh -i "$SSH_KEY_PATH" "root@$VPS_IP" "
    echo 'Configuring SSH security...'
    
    # Backup original SSH config
    cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
    
    # Create secure SSH configuration
    cat > /etc/ssh/sshd_config << 'SSHEOF'
# Agentic Site SSH Configuration - Secure with Admin Backup

# Network
Port 22
AddressFamily any
ListenAddress 0.0.0.0

# Authentication
LoginGraceTime 2m
PermitRootLogin yes
StrictModes yes
MaxAuthTries 6
MaxSessions 10

# Key-based authentication (preferred)
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys

# Password authentication (backup for admin)
PasswordAuthentication yes
PermitEmptyPasswords no
ChallengeResponseAuthentication no

# Security
UsePAM yes
X11Forwarding no
PrintMotd no
AcceptEnv LANG LC_*
Subsystem sftp /usr/lib/openssh/sftp-server

# Admin backup port
Port $ADMIN_SSH_PORT
SSHEOF

    # Test SSH configuration
    sshd -t
    
    echo '✓ SSH configuration updated'
"

echo -e "${YELLOW}Step 8: Configuring firewall with proper port management...${NC}"

ssh -i "$SSH_KEY_PATH" "root@$VPS_IP" "
    echo 'Configuring UFW firewall...'
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    
    # Allow SSH on both ports
    ufw allow 22/tcp comment 'SSH Standard'
    ufw allow $ADMIN_SSH_PORT/tcp comment 'SSH Admin Backup'
    
    # Allow HTTP and HTTPS
    ufw allow 80/tcp comment 'HTTP'
    ufw allow 443/tcp comment 'HTTPS'
    
    # Allow environment-specific ports
    if [ '$ENVIRONMENT' = 'development' ]; then
        ufw allow 3001/tcp comment 'Frontend Dev'
        ufw allow 8001/tcp comment 'Backend Dev'
        ufw allow 5679/tcp comment 'n8n Dev'
        ufw allow 6380/tcp comment 'Redis Dev'
    else
        ufw allow 3000/tcp comment 'Frontend Prod'
        ufw allow 8000/tcp comment 'Backend Prod'
        ufw allow 5678/tcp comment 'n8n Prod'
        ufw allow 6379/tcp comment 'Redis Prod'
    fi
    
    # Allow monitoring ports
    ufw allow 9090/tcp comment 'Prometheus'
    ufw allow 3001/tcp comment 'Grafana'
    ufw allow 9100/tcp comment 'Node Exporter'
    
    # Enable firewall
    ufw --force enable
    
    # Show firewall status
    ufw status numbered
    
    echo '✓ Firewall configured with proper port management'
"

echo -e "${YELLOW}Step 9: Setting up strong admin password and security...${NC}"

ssh -i "$SSH_KEY_PATH" "root@$VPS_IP" "
    echo 'Setting up enhanced security...'
    
    # Change root password to a very strong one
    echo 'root:$NEW_ROOT_PASSWORD' | chpasswd
    
    # Configure fail2ban
    cat > /etc/fail2ban/jail.local << 'F2BEOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = 22,$ADMIN_SSH_PORT
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
F2BEOF

    systemctl enable fail2ban
    systemctl start fail2ban
    
    echo '✓ Enhanced security configured'
"

echo -e "${YELLOW}Step 10: Creating deployment directories and structure...${NC}"

DEPLOY_PATH="/opt/docker-apps/$ENVIRONMENT/agentic-site"

ssh -i "$SSH_KEY_PATH" "root@$VPS_IP" "
    echo 'Creating deployment directories...'
    mkdir -p $DEPLOY_PATH
    mkdir -p /opt/docker-apps/shared/ssl
    mkdir -p /opt/docker-apps/shared/backups
    mkdir -p /opt/docker-apps/shared/logs
    mkdir -p /var/log/agentic-site
    
    # Set proper permissions
    chown -R root:root /opt/docker-apps
    chmod -R 755 /opt/docker-apps
    
    echo '✓ Deployment directories created'
"

echo -e "${YELLOW}Step 11: Creating management and monitoring scripts...${NC}"

ssh -i "$SSH_KEY_PATH" "root@$VPS_IP" "
    echo 'Creating management scripts...'
    
    # Status script
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
echo \"=== Container Status ===\"
cd $DEPLOY_PATH && docker-compose ps 2>/dev/null || echo \"No containers running\"
echo
echo \"=== Port Status ===\"
netstat -tlnp | grep -E ':(3000|3001|8000|8001|5678|5679|6379|6380)' || echo \"No application ports listening\"
echo
echo \"=== Nginx Status ===\"
systemctl status nginx --no-pager -l
echo
echo \"=== Firewall Status ===\"
ufw status numbered
echo
echo \"=== SSH Connections ===\"
who
STATUSEOF

    # Restart script
    cat > /usr/local/bin/agentic-$ENVIRONMENT-restart.sh << 'RESTARTEOF'
#!/bin/bash
echo \"=== Restarting Agentic Site $ENVIRONMENT ===\"
echo \"Timestamp: \$(date)\"
cd $DEPLOY_PATH
echo \"Stopping containers...\"
docker-compose down
echo \"Starting containers...\"
docker-compose up -d
echo \"Waiting for services...\"
sleep 10
echo \"Container status:\"
docker-compose ps
echo \"=== Restart Complete ===\"
RESTARTEOF

    # Logs script
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

    # Backup script
    cat > /usr/local/bin/agentic-$ENVIRONMENT-backup.sh << 'BACKUPEOF'
#!/bin/bash
echo \"=== Creating Backup for $ENVIRONMENT ===\"
BACKUP_DIR=\"/opt/docker-apps/shared/backups\"
BACKUP_FILE=\"agentic-$ENVIRONMENT-\$(date +%Y%m%d-%H%M%S).tar.gz\"
cd $DEPLOY_PATH
tar -czf \"\$BACKUP_DIR/\$BACKUP_FILE\" .
echo \"Backup created: \$BACKUP_DIR/\$BACKUP_FILE\"
# Keep only last 10 backups
ls -t \$BACKUP_DIR/agentic-$ENVIRONMENT-*.tar.gz | tail -n +11 | xargs -r rm
echo \"Old backups cleaned up\"
BACKUPEOF

    # Make scripts executable
    chmod +x /usr/local/bin/agentic-$ENVIRONMENT-*.sh
    
    echo '✓ Management scripts created'
"

echo -e "${YELLOW}Step 12: System optimization and final configuration...${NC}"

ssh -i "$SSH_KEY_PATH" "root@$VPS_IP" "
    echo 'Optimizing system settings...'
    
    # Increase file limits
    cat >> /etc/security/limits.conf << 'LIMITSEOF'
# Agentic Site Optimizations
* soft nofile 65536
* hard nofile 65536
root soft nofile 65536
root hard nofile 65536
LIMITSEOF

    # Optimize sysctl settings
    cat >> /etc/sysctl.conf << 'SYSCTLEOF'
# Agentic Site Network Optimizations
net.core.somaxconn = 65536
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 65536
net.ipv4.tcp_keepalive_time = 600
net.ipv4.tcp_keepalive_intvl = 60
net.ipv4.tcp_keepalive_probes = 10
vm.swappiness = 10
SYSCTLEOF

    sysctl -p
    
    # Set timezone
    timedatectl set-timezone UTC
    
    # Create environment info file
    cat > /opt/docker-apps/shared/vps-info.txt << INFOEOF
VPS Setup Information
====================
IP Address: $VPS_IP
Environment: $ENVIRONMENT
Setup Date: \$(date)
SSH Key: $SSH_KEY_PATH
SSH Alias: $SSH_ALIAS
Admin SSH Port: $ADMIN_SSH_PORT
Deploy Path: $DEPLOY_PATH

SSH Access:
- Standard: ssh $SSH_ALIAS
- Admin Backup: ssh $SSH_ALIAS-admin (port $ADMIN_SSH_PORT)

Management Commands:
- Status: /usr/local/bin/agentic-$ENVIRONMENT-status.sh
- Restart: /usr/local/bin/agentic-$ENVIRONMENT-restart.sh
- Logs: /usr/local/bin/agentic-$ENVIRONMENT-logs.sh
- Backup: /usr/local/bin/agentic-$ENVIRONMENT-backup.sh
INFOEOF

    echo '✓ System optimization complete'
"

# Create local environment file
cat > ".env.$ENVIRONMENT.vps" << EOF
# VPS Environment Configuration - Generated $(date)
# This file contains the VPS-specific configuration

# VPS Connection Details
VPS_IP=$VPS_IP
VPS_ENVIRONMENT=$ENVIRONMENT
SSH_ALIAS=$SSH_ALIAS
SSH_KEY_PATH=$SSH_KEY_PATH

# SSH Access
SSH_STANDARD_PORT=22
SSH_ADMIN_PORT=$ADMIN_SSH_PORT
ROOT_PASSWORD=$NEW_ROOT_PASSWORD

# Deployment
DEPLOY_PATH=$DEPLOY_PATH
DOMAIN=${ENVIRONMENT}.consulting.sa

# Application Ports
FRONTEND_PORT=$([[ "$ENVIRONMENT" == "development" ]] && echo "3001" || echo "3000")
BACKEND_PORT=$([[ "$ENVIRONMENT" == "development" ]] && echo "8001" || echo "8000")
REDIS_PORT=$([[ "$ENVIRONMENT" == "development" ]] && echo "6380" || echo "6379")
N8N_PORT=$([[ "$ENVIRONMENT" == "development" ]] && echo "5679" || echo "5678")

# Management Scripts
STATUS_SCRIPT=/usr/local/bin/agentic-$ENVIRONMENT-status.sh
RESTART_SCRIPT=/usr/local/bin/agentic-$ENVIRONMENT-restart.sh
LOGS_SCRIPT=/usr/local/bin/agentic-$ENVIRONMENT-logs.sh
BACKUP_SCRIPT=/usr/local/bin/agentic-$ENVIRONMENT-backup.sh
EOF

echo
echo -e "${GREEN}🎉 Fresh VPS Setup Complete!${NC}"
echo -e "${BLUE}=======================================================${NC}"
echo
echo -e "${CYAN}🔐 CRITICAL SECURITY INFORMATION (SAVE THIS!)${NC}"
echo -e "${YELLOW}New Root Password: $NEW_ROOT_PASSWORD${NC}"
echo -e "${YELLOW}Admin SSH Port: $ADMIN_SSH_PORT${NC}"
echo
echo -e "${CYAN}🔑 SSH Access Methods:${NC}"
echo "Primary (SSH Key): ssh $SSH_ALIAS"
echo "Admin Backup: ssh $SSH_ALIAS-admin -p $ADMIN_SSH_PORT"
echo
echo -e "${CYAN}📁 Files Created:${NC}"
echo "• SSH Key: $SSH_KEY_PATH"
echo "• SSH Config: ~/.ssh/config (entry: $SSH_ALIAS)"
echo "• VPS Environment: .env.$ENVIRONMENT.vps"
echo
echo -e "${CYAN}🛠️ Management Commands:${NC}"
echo "• Status: ssh $SSH_ALIAS '/usr/local/bin/agentic-$ENVIRONMENT-status.sh'"
echo "• Logs: ssh $SSH_ALIAS '/usr/local/bin/agentic-$ENVIRONMENT-logs.sh'"
echo "• Restart: ssh $SSH_ALIAS '/usr/local/bin/agentic-$ENVIRONMENT-restart.sh'"
echo "• Backup: ssh $SSH_ALIAS '/usr/local/bin/agentic-$ENVIRONMENT-backup.sh'"
echo
echo -e "${CYAN}🚀 Next Steps:${NC}"
echo "1. Test SSH access: ssh $SSH_ALIAS"
echo "2. Deploy application: ./infrastructure/scripts/deploy-to-clean-vps.sh $SSH_ALIAS $ENVIRONMENT"
echo "3. Configure your domain DNS to point to $VPS_IP"
echo
echo -e "${GREEN}✅ VPS is now ready for secure deployment!${NC}"
echo -e "${YELLOW}⚠️  IMPORTANT: Save the new root password and admin SSH port!${NC}"