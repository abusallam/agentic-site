#!/bin/bash
# 🔐 SETUP PRIVATE GITHUB REPOSITORY ACCESS
# Configures SSH keys and authentication for private GitHub repositories

set -e

SERVER_IP="217.79.255.54"
SERVER_USER="root"
SERVER_PASS="gnqLG7FDd4"

echo "🔐 SETTING UP PRIVATE GITHUB REPOSITORY ACCESS"
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

# Function to copy file to server
scp_file() {
    sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no "$1" "$SERVER_USER@$SERVER_IP:$2"
    if [ $? -eq 0 ]; then
        echo "✅ SCP: $1 → $2"
    else
        echo "❌ SCP FAILED: $1 → $2"
        exit 1
    fi
}

echo "🔍 Step 1: Creating SSH key for GitHub access..."

# Generate SSH key for GitHub if it doesn't exist
ssh_run "mkdir -p /root/.ssh"
ssh_run "if [ ! -f /root/.ssh/github_deploy_key ]; then ssh-keygen -t ed25519 -f /root/.ssh/github_deploy_key -N '' -C 'VPS-Deploy-Key-$(hostname)-$(date +%Y%m%d)'; fi"

echo ""
echo "🔍 Step 2: Configuring SSH for GitHub..."

# Create SSH config for GitHub
cat > /tmp/ssh_config << 'EOF'
# GitHub configuration for private repository access
Host github.com
    HostName github.com
    User git
    IdentityFile /root/.ssh/github_deploy_key
    IdentitiesOnly yes
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
EOF

scp_file "/tmp/ssh_config" "/root/.ssh/config"
ssh_run "chmod 600 /root/.ssh/config /root/.ssh/github_deploy_key /root/.ssh/github_deploy_key.pub"

echo ""
echo "🔍 Step 3: Testing SSH connection to GitHub..."
ssh_run "ssh -T git@github.com || echo 'SSH key not yet added to GitHub'"

echo ""
echo "✅ SSH KEY SETUP COMPLETED"
echo ""
echo "🔑 CRITICAL NEXT STEPS:"
echo "========================================"
echo ""
echo "1. 📋 COPY THE PUBLIC KEY BELOW:"
echo ""
ssh_run "cat /root/.ssh/github_deploy_key.pub"
echo ""
echo "2. 🔧 ADD TO GITHUB REPOSITORY:"
echo "   • Go to your GitHub repository"
echo "   • Settings → Deploy keys → Add deploy key"
echo "   • Title: 'VPS Deploy Key - $(date +%Y-%m-%d)'"
echo "   • Key: [paste the public key above]"
echo "   • ✅ Check 'Allow write access' (required for deployment)"
echo ""
echo "3. 🧪 TEST THE CONNECTION:"
echo "   After adding the key, run this command to test:"
echo "   ssh root@$SERVER_IP 'ssh -T git@github.com'"
echo ""
echo "4. 🚀 CONTINUE WITH GITHUB INTEGRATION:"
echo "   Once the key is added and tested, run:"
echo "   ./infrastructure/scripts/setup-github-integration.sh"
echo ""

# Cleanup
rm -f /tmp/ssh_config

echo "📝 AUTHENTICATION METHODS FOR PRIVATE REPOSITORIES:"
echo ""
echo "Method 1: SSH Deploy Keys (RECOMMENDED - What we just set up)"
echo "✅ Pros: Secure, repository-specific, no personal token needed"
echo "✅ Use: For automated deployments from VPS"
echo ""
echo "Method 2: Personal Access Token (Alternative)"
echo "• Create token: GitHub → Settings → Developer settings → Personal access tokens"
echo "• Permissions: repo (full control of private repositories)"
echo "• Usage: HTTPS clone with token as password"
echo ""
echo "Method 3: GitHub App (Enterprise)"
echo "• More complex setup but better for organizations"
echo "• Fine-grained permissions"
echo "• Better audit trail"
echo ""
echo "🎯 WE'RE USING METHOD 1 (SSH Deploy Keys) - Most secure for VPS deployment"