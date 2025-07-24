#!/bin/bash
set -e

# VPS Setup Script for CI/CD Pipeline
# This script sets up a VPS for the Agentic AI platform

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-staging}
VPS_HOST=${2}
SSH_KEY=${3}
ANSIBLE_VAULT_PASSWORD=${4}

# Validate inputs
if [ -z "$VPS_HOST" ] || [ -z "$SSH_KEY" ]; then
    echo -e "${RED}Error: Missing required parameters${NC}"
    echo "Usage: $0 <environment> <vps_host> <ssh_key_path> [ansible_vault_password]"
    echo "Example: $0 staging 192.168.1.100 ~/.ssh/id_rsa"
    exit 1
fi

if [ ! -f "$SSH_KEY" ]; then
    echo -e "${RED}Error: SSH key file not found: $SSH_KEY${NC}"
    exit 1
fi

echo -e "${GREEN}Setting up VPS for environment: $ENVIRONMENT${NC}"
echo -e "${YELLOW}Host: $VPS_HOST${NC}"

# Check if Ansible is installed
if ! command -v ansible &> /dev/null; then
    echo -e "${YELLOW}Installing Ansible...${NC}"
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y ansible
    elif command -v yum &> /dev/null; then
        sudo yum install -y ansible
    elif command -v brew &> /dev/null; then
        brew install ansible
    else
        echo -e "${RED}Error: Could not install Ansible. Please install it manually.${NC}"
        exit 1
    fi
fi

# Create temporary inventory file
TEMP_INVENTORY=$(mktemp)
cat > "$TEMP_INVENTORY" << EOF
[$ENVIRONMENT]
${ENVIRONMENT}-server ansible_host=$VPS_HOST ansible_user=root ansible_ssh_private_key_file=$SSH_KEY

[all:vars]
ansible_python_interpreter=/usr/bin/python3
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
EOF

echo -e "${YELLOW}Testing SSH connection...${NC}"
if ! ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no -o ConnectTimeout=10 root@"$VPS_HOST" "echo 'SSH connection successful'"; then
    echo -e "${RED}Error: Cannot connect to VPS via SSH${NC}"
    rm "$TEMP_INVENTORY"
    exit 1
fi

echo -e "${GREEN}SSH connection successful${NC}"

# Run Ansible playbook for server setup
echo -e "${YELLOW}Running server setup playbook...${NC}"
ANSIBLE_CMD="ansible-playbook -i $TEMP_INVENTORY infrastructure/ansible/playbooks/server-setup.yml"

# Add vault password if provided
if [ -n "$ANSIBLE_VAULT_PASSWORD" ]; then
    echo "$ANSIBLE_VAULT_PASSWORD" > /tmp/vault_pass
    ANSIBLE_CMD="$ANSIBLE_CMD --vault-password-file /tmp/vault_pass"
fi

# Add extra variables
ANSIBLE_CMD="$ANSIBLE_CMD -e environment=$ENVIRONMENT"

# Set domain based on environment
if [ "$ENVIRONMENT" = "production" ]; then
    ANSIBLE_CMD="$ANSIBLE_CMD -e domain=consulting.sa"
else
    ANSIBLE_CMD="$ANSIBLE_CMD -e domain=staging.consulting.sa"
fi

# Run the playbook
if $ANSIBLE_CMD; then
    echo -e "${GREEN}Server setup completed successfully${NC}"
else
    echo -e "${RED}Server setup failed${NC}"
    rm "$TEMP_INVENTORY"
    [ -f /tmp/vault_pass ] && rm /tmp/vault_pass
    exit 1
fi

# Cleanup
rm "$TEMP_INVENTORY"
[ -f /tmp/vault_pass ] && rm /tmp/vault_pass

# Test the setup
echo -e "${YELLOW}Testing server setup...${NC}"

# Test Docker installation
if ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no root@"$VPS_HOST" "docker --version"; then
    echo -e "${GREEN}✓ Docker installed successfully${NC}"
else
    echo -e "${RED}✗ Docker installation failed${NC}"
fi

# Test Docker Compose installation
if ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no root@"$VPS_HOST" "docker-compose --version"; then
    echo -e "${GREEN}✓ Docker Compose installed successfully${NC}"
else
    echo -e "${RED}✗ Docker Compose installation failed${NC}"
fi

# Test Nginx installation
if ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no root@"$VPS_HOST" "nginx -v"; then
    echo -e "${GREEN}✓ Nginx installed successfully${NC}"
else
    echo -e "${RED}✗ Nginx installation failed${NC}"
fi

# Test firewall status
if ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no root@"$VPS_HOST" "ufw status"; then
    echo -e "${GREEN}✓ Firewall configured${NC}"
else
    echo -e "${YELLOW}⚠ Firewall status unknown${NC}"
fi

# Create deployment script for this VPS
DEPLOY_SCRIPT="scripts/ci/deploy-to-${ENVIRONMENT}.sh"
cat > "$DEPLOY_SCRIPT" << EOF
#!/bin/bash
# Auto-generated deployment script for $ENVIRONMENT environment
set -e

VPS_HOST="$VPS_HOST"
SSH_KEY="$SSH_KEY"
ENVIRONMENT="$ENVIRONMENT"

# Deploy application
ansible-playbook -i infrastructure/ansible/inventory/hosts.yml \\
    infrastructure/ansible/playbooks/deploy-application.yml \\
    --limit \$ENVIRONMENT \\
    -e environment=\$ENVIRONMENT \\
    -e github_username=\${GITHUB_ACTOR} \\
    -e github_token=\${GITHUB_TOKEN} \\
    "\$@"
EOF

chmod +x "$DEPLOY_SCRIPT"

echo -e "${GREEN}VPS setup completed successfully!${NC}"
echo -e "${YELLOW}Deployment script created: $DEPLOY_SCRIPT${NC}"
echo -e "${YELLOW}You can now deploy the application using:${NC}"
echo -e "${GREEN}./$DEPLOY_SCRIPT${NC}"

# Display next steps
echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Configure your GitHub secrets with the VPS details"
echo "2. Update your environment variables in the CI/CD pipeline"
echo "3. Push your code to trigger the deployment"

if [ "$ENVIRONMENT" = "production" ]; then
    echo "4. Configure your DNS to point to: $VPS_HOST"
    echo "5. SSL certificate will be automatically generated"
fi