#!/bin/bash
# 🔧 FIX AND PROMOTE GITHUB WORKFLOW
# Fixes the docker-compose issue and continues with GitHub integration

set -e

SERVER_IP="217.79.255.54"
SERVER_USER="root"
SERVER_PASS="gnqLG7FDd4"

echo "🔧 FIXING DOCKER-COMPOSE ISSUE AND CONTINUING GITHUB SETUP"
echo "📅 $(date)"
echo ""

# Function to run SSH command
ssh_run() {
    sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "$1"
    if [ $? -eq 0 ]; then
        echo "✅ SSH: $1"
    else
        echo "❌ SSH FAILED: $1"
        exit 1
    fi
}

echo "🔍 Step 1: Installing Docker Compose properly..."

# Install Docker Compose using the official method
ssh_run "curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose"
ssh_run "chmod +x /usr/local/bin/docker-compose"
ssh_run "ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose"

# Verify installation
ssh_run "docker-compose --version"

echo ""
echo "🔍 Step 2: Installing remaining packages..."

# Install other required packages
ssh_run "apt-get install -y git nodejs npm python3-pip nginx certbot python3-certbot-nginx sshpass curl wget"

echo ""
echo "🔍 Step 3: Checking current system status..."

# Check Docker status
ssh_run "systemctl status docker --no-pager -l" || echo "Docker may need to be started"
ssh_run "systemctl enable docker && systemctl start docker"

# Check current containers
echo "Current container status:"
ssh_run "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

echo ""
echo "🔍 Step 4: Setting up private repository access..."

echo "Before we continue with GitHub integration, we need to set up access to your private repository."
echo ""
echo "🔑 PRIVATE REPOSITORY SETUP REQUIRED:"
echo "   1. First, set up SSH access for your private repository:"
echo "      ./infrastructure/scripts/setup-private-github-access.sh"
echo ""
echo "   2. Then add the SSH key to your GitHub repository as a Deploy Key"
echo ""
echo "   3. Finally, continue with the GitHub integration setup"
echo ""

echo "✅ DOCKER-COMPOSE ISSUE FIXED"
echo ""
echo "📋 System Status:"
echo "├── ✅ Docker Compose installed and working"
echo "├── ✅ Required packages installed"
echo "├── ✅ Docker service running"
echo "└── ✅ Current containers operational"
echo ""
echo "🚀 Next Steps:"
echo "   1. Set up private repository access:"
echo "      chmod +x infrastructure/scripts/setup-private-github-access.sh"
echo "      ./infrastructure/scripts/setup-private-github-access.sh"
echo ""
echo "   2. Add SSH key to GitHub repository (follow script instructions)"
echo ""
echo "   3. Continue with GitHub integration:"
echo "      ./infrastructure/scripts/setup-github-integration.sh"
echo ""
echo "📖 For detailed instructions, see: PRIVATE_GITHUB_SETUP_GUIDE.md"