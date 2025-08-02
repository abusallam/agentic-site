#!/bin/bash

# Setup SSH Keys for Automated Deployment
# This script sets up passwordless SSH access to the VPS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

VPS_HOST="217.79.255.54"
VPS_USER="root"

echo -e "${BLUE}🔑 Setting up SSH Key Authentication${NC}"
echo "Target VPS: $VPS_HOST"
echo "User: $VPS_USER"
echo

# Check if SSH key already exists
if [ ! -f ~/.ssh/id_rsa ]; then
    echo -e "${YELLOW}Generating SSH key pair...${NC}"
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N "" -C "$(whoami)@$(hostname)-agentic-deployment"
    echo "✓ SSH key pair generated"
else
    echo "✓ SSH key pair already exists"
fi

# Copy public key to VPS
echo -e "${YELLOW}Copying public key to VPS...${NC}"
echo "You will be asked for the VPS password one last time:"

ssh-copy-id -i ~/.ssh/id_rsa.pub $VPS_USER@$VPS_HOST

echo -e "${YELLOW}Testing passwordless SSH connection...${NC}"

if ssh -o BatchMode=yes -o ConnectTimeout=5 $VPS_USER@$VPS_HOST 'echo "SSH key authentication successful"' 2>/dev/null; then
    echo -e "${GREEN}✓ Passwordless SSH authentication is working!${NC}"
else
    echo -e "${RED}❌ SSH key authentication failed. Please check the setup.${NC}"
    exit 1
fi

echo -e "${YELLOW}Configuring SSH client for better performance...${NC}"

# Create or update SSH config
mkdir -p ~/.ssh
cat >> ~/.ssh/config << EOF

# Agentic Site VPS Configuration
Host agentic-vps
    HostName $VPS_HOST
    User $VPS_USER
    IdentityFile ~/.ssh/id_rsa
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    ServerAliveInterval 60
    ServerAliveCountMax 3
    ControlMaster auto
    ControlPath ~/.ssh/control-%r@%h:%p
    ControlPersist 10m

EOF

echo "✓ SSH configuration updated"

echo -e "${YELLOW}Testing optimized SSH connection...${NC}"

if ssh agentic-vps 'echo "Optimized SSH connection successful"'; then
    echo -e "${GREEN}✓ Optimized SSH connection is working!${NC}"
else
    echo -e "${RED}❌ Optimized SSH connection failed.${NC}"
    exit 1
fi

echo
echo -e "${GREEN}🎉 SSH Key Authentication Setup Complete!${NC}"
echo
echo -e "${BLUE}=== NEXT STEPS ===${NC}"
echo "1. All future scripts will now run without password prompts"
echo "2. You can use 'ssh agentic-vps' for quick access"
echo "3. SSH connections will be faster and more reliable"
echo
echo -e "${BLUE}=== SECURITY NOTES ===${NC}"
echo "• Your SSH private key is stored in ~/.ssh/id_rsa"
echo "• Keep this key secure and never share it"
echo "• The VPS now trusts this key for authentication"
echo
echo -e "${GREEN}Ready for automated deployments!${NC}"