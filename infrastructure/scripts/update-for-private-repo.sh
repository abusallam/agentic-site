#!/bin/bash
# 🔧 UPDATE GITHUB INTEGRATION FOR PRIVATE REPOSITORY
# Updates the GitHub integration script to work with private repositories

set -e

echo "🔧 UPDATING GITHUB INTEGRATION FOR PRIVATE REPOSITORY"
echo "📅 $(date)"
echo ""

# Check if the setup script exists
if [ ! -f "infrastructure/scripts/setup-github-integration.sh" ]; then
    echo "❌ setup-github-integration.sh not found"
    exit 1
fi

echo "🔍 Step 1: Creating backup of original script..."
cp infrastructure/scripts/setup-github-integration.sh infrastructure/scripts/setup-github-integration.sh.backup

echo "🔍 Step 2: Updating repository URLs to use SSH format..."

# Update HTTPS URLs to SSH URLs in deployment scripts
sed -i 's|https://github.com/your-username/your-private-repo.git|git@github.com:your-username/your-private-repo.git|g' infrastructure/scripts/setup-github-integration.sh

echo "🔍 Step 3: Adding SSH key setup to the integration script..."

# Create the updated section for SSH setup
cat > /tmp/ssh_setup_section << 'EOF'

echo "🔍 Phase 1.5: Verifying GitHub SSH access for private repository..."

# Check if SSH key exists and GitHub access is configured
if ssh_run "test -f /root/.ssh/github_deploy_key"; then
    echo "✅ GitHub SSH key found"
    
    # Test GitHub connection
    if ssh_run "ssh -T git@github.com 2>&1 | grep -q 'successfully authenticated'"; then
        echo "✅ GitHub SSH connection working"
    else
        echo "❌ GitHub SSH connection failed"
        echo ""
        echo "🔑 SETUP REQUIRED:"
        echo "   1. Run: ./infrastructure/scripts/setup-private-github-access.sh"
        echo "   2. Add the SSH key to your GitHub repository as a Deploy Key"
        echo "   3. Then re-run this script"
        echo ""
        exit 1
    fi
else
    echo "❌ GitHub SSH key not found"
    echo ""
    echo "🔑 SETUP REQUIRED:"
    echo "   1. Run: ./infrastructure/scripts/setup-private-github-access.sh"
    echo "   2. Add the SSH key to your GitHub repository as a Deploy Key"
    echo "   3. Then re-run this script"
    echo ""
    exit 1
fi

EOF

# Insert the SSH setup section after Phase 1
sed -i '/echo "✅ System packages and Docker installed"/r /tmp/ssh_setup_section' infrastructure/scripts/setup-github-integration.sh

echo "🔍 Step 4: Creating instructions file..."

cat > GITHUB_PRIVATE_REPO_SETUP.md << 'EOF'
# 🔐 GitHub Private Repository Setup Instructions

## Quick Setup Process

### Step 1: Set up SSH access for private repository
```bash
chmod +x infrastructure/scripts/setup-private-github-access.sh
./infrastructure/scripts/setup-private-github-access.sh
```

### Step 2: Add SSH key to GitHub
1. Copy the SSH public key displayed by the script
2. Go to your GitHub repository → Settings → Deploy keys → Add deploy key
3. Title: "VPS Deploy Key - consulting.sa"
4. Paste the key and ✅ check "Allow write access"
5. Click "Add key"

### Step 3: Update repository URL in scripts
Edit the deployment scripts and replace:
```bash
# Find this line in the scripts:
REPO_URL="git@github.com:your-username/your-private-repo.git"

# Replace with your actual repository:
REPO_URL="git@github.com:yourusername/your-actual-repo-name.git"
```

### Step 4: Run GitHub integration setup
```bash
./infrastructure/scripts/update-for-private-repo.sh  # (This script)
./infrastructure/scripts/setup-github-integration.sh
```

### Step 5: Configure webhook in GitHub
1. Go to your repository → Settings → Webhooks → Add webhook
2. Payload URL: https://www.consulting.sa/webhook
3. Content type: application/json
4. Events: Push events
5. Add webhook

## Verification
Test the setup:
```bash
# Test SSH connection
ssh root@217.79.255.54 'ssh -T git@github.com'

# Should show: "Hi username/repo! You've successfully authenticated..."
```

## Security Notes
- SSH Deploy Keys provide repository-specific access
- No personal credentials are stored on the VPS
- Keys can be revoked from GitHub at any time
- This is the most secure method for private repository access
EOF

# Cleanup
rm -f /tmp/ssh_setup_section

echo ""
echo "✅ GITHUB INTEGRATION UPDATED FOR PRIVATE REPOSITORY"
echo ""
echo "📋 What was updated:"
echo "├── 🔄 Repository URLs changed from HTTPS to SSH format"
echo "├── 🔑 Added SSH key verification to integration script"
echo "├── 📝 Created GITHUB_PRIVATE_REPO_SETUP.md instructions"
echo "└── 💾 Backup created: setup-github-integration.sh.backup"
echo ""
echo "🚀 Next steps:"
echo "   1. Set up SSH access: ./infrastructure/scripts/setup-private-github-access.sh"
echo "   2. Add SSH key to GitHub repository as Deploy Key"
echo "   3. Update repository URL in scripts with your actual repo name"
echo "   4. Run GitHub integration: ./infrastructure/scripts/setup-github-integration.sh"
echo ""
echo "📖 See GITHUB_PRIVATE_REPO_SETUP.md for detailed instructions"