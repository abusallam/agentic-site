# 🔐 Private GitHub Repository Setup Guide
## Secure Access Configuration for VPS Deployment

**Purpose**: Configure secure access to private GitHub repositories for automated deployment  
**Security Level**: Production-grade SSH key authentication  
**Status**: ✅ Ready for Implementation  

---

## 🎯 Overview

Private repositories require proper authentication for VPS access. This guide covers the most secure method using SSH Deploy Keys, which provides repository-specific access without exposing personal credentials.

### Why SSH Deploy Keys?
- ✅ **Repository-specific**: Access only to the specific repository
- ✅ **No personal credentials**: Doesn't use your personal GitHub account
- ✅ **Secure**: Uses SSH key authentication
- ✅ **Auditable**: Clear access trail in GitHub
- ✅ **Revocable**: Can be removed without affecting other access

---

## 🔧 Authentication Methods Comparison

### Method 1: SSH Deploy Keys (RECOMMENDED)
```bash
# Repository URL format
git@github.com:username/repository.git
```
**Pros**: Most secure, repository-specific, no personal token needed  
**Cons**: Requires SSH key setup  
**Best for**: Production deployments, automated systems  

### Method 2: Personal Access Token
```bash
# Repository URL format
https://token@github.com/username/repository.git
```
**Pros**: Easy to set up, works with HTTPS  
**Cons**: Uses personal credentials, broader access  
**Best for**: Development, temporary access  

### Method 3: GitHub App (Enterprise)
```bash
# Complex authentication flow
```
**Pros**: Fine-grained permissions, enterprise features  
**Cons**: Complex setup, overkill for simple deployments  
**Best for**: Large organizations, complex workflows  

---

## 🚀 Implementation: SSH Deploy Keys

### Step 1: Run the Setup Script
```bash
chmod +x infrastructure/scripts/setup-private-github-access.sh
./infrastructure/scripts/setup-private-github-access.sh
```

This script will:
- Generate SSH key pair on the VPS
- Configure SSH for GitHub access
- Display the public key for GitHub setup
- Test the connection

### Step 2: Add Deploy Key to GitHub

1. **Copy the SSH public key** displayed by the script
2. **Go to your GitHub repository**
3. **Navigate to**: Settings → Deploy keys → Add deploy key
4. **Configure the deploy key**:
   - **Title**: `VPS Deploy Key - consulting.sa`
   - **Key**: Paste the public key from Step 1
   - **✅ Allow write access**: Check this box (required for deployment status updates)
5. **Click**: Add key

### Step 3: Test the Connection
```bash
# Test SSH connection to GitHub
ssh root@217.79.255.54 'ssh -T git@github.com'

# Expected output:
# Hi username/repository! You've successfully authenticated, but GitHub does not provide shell access.
```

### Step 4: Update Repository URLs
Update your deployment scripts to use SSH URLs:
```bash
# ❌ HTTPS URL (won't work for private repos without token)
https://github.com/username/repository.git

# ✅ SSH URL (works with deploy key)
git@github.com:username/repository.git
```

---

## 🔧 Configuration Details

### SSH Configuration Created
```bash
# /root/.ssh/config
Host github.com
    HostName github.com
    User git
    IdentityFile /root/.ssh/github_deploy_key
    IdentitiesOnly yes
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
```

### Key Files Created
```bash
/root/.ssh/github_deploy_key      # Private key (keep secure)
/root/.ssh/github_deploy_key.pub  # Public key (add to GitHub)
/root/.ssh/config                 # SSH configuration
```

### Security Considerations
- ✅ **Private key stays on VPS**: Never shared or transmitted
- ✅ **Repository-specific access**: Key only works for the specific repository
- ✅ **No personal account access**: Doesn't provide access to your personal GitHub
- ✅ **Revocable**: Can be removed from GitHub at any time

---

## 🛠️ Deployment Script Updates

### Updated Production Deployment
```bash
#!/bin/bash
# deploy-production.sh

REPO_URL="git@github.com:username/your-private-repo.git"  # SSH URL
DEPLOY_DIR="/opt/apps/production"

# Clone or update repository
if [ -d "$DEPLOY_DIR/.git" ]; then
    cd "$DEPLOY_DIR"
    git fetch origin
    git reset --hard origin/main
else
    rm -rf "$DEPLOY_DIR"
    git clone "$REPO_URL" "$DEPLOY_DIR"
    cd "$DEPLOY_DIR"
fi

# Continue with deployment...
```

### Updated Development Deployment
```bash
#!/bin/bash
# deploy-development.sh

REPO_URL="git@github.com:username/your-private-repo.git"  # SSH URL
DEPLOY_DIR="/opt/apps/development"

# Clone or update repository
if [ -d "$DEPLOY_DIR/.git" ]; then
    cd "$DEPLOY_DIR"
    git fetch origin
    git reset --hard origin/development
else
    rm -rf "$DEPLOY_DIR"
    git clone -b development "$REPO_URL" "$DEPLOY_DIR"
    cd "$DEPLOY_DIR"
fi

# Continue with deployment...
```

---

## 🔍 Troubleshooting

### Issue 1: Permission Denied (publickey)
**Symptoms**: `Permission denied (publickey)` when accessing repository
**Solutions**:
```bash
# Check SSH key exists
ls -la /root/.ssh/github_deploy_key*

# Test SSH connection
ssh -T git@github.com

# Check SSH config
cat /root/.ssh/config

# Verify key is added to GitHub
# Go to GitHub → Repository → Settings → Deploy keys
```

### Issue 2: Repository Not Found
**Symptoms**: `Repository not found` error
**Solutions**:
- Verify repository URL is correct
- Ensure deploy key has been added to GitHub
- Check repository is accessible with the key
- Verify SSH URL format: `git@github.com:username/repo.git`

### Issue 3: Host Key Verification Failed
**Symptoms**: `Host key verification failed`
**Solutions**:
```bash
# Add GitHub to known hosts
ssh-keyscan github.com >> /root/.ssh/known_hosts

# Or use StrictHostKeyChecking no in SSH config (already configured)
```

### Issue 4: Write Access Denied
**Symptoms**: Cannot push or update deployment status
**Solutions**:
- Ensure "Allow write access" is checked for the deploy key in GitHub
- Verify the key has the necessary permissions

---

## 🔐 Security Best Practices

### Key Management
- ✅ **Generate unique keys**: One key per VPS/environment
- ✅ **Use descriptive names**: Include hostname and date in key comment
- ✅ **Regular rotation**: Rotate keys periodically (quarterly/annually)
- ✅ **Monitor access**: Review deploy key usage in GitHub

### Access Control
- ✅ **Minimal permissions**: Deploy keys only for specific repositories
- ✅ **Environment separation**: Different keys for prod/dev if needed
- ✅ **Audit trail**: Monitor repository access logs
- ✅ **Revocation plan**: Know how to quickly revoke access

### Backup and Recovery
- ✅ **Key backup**: Securely backup private keys
- ✅ **Recovery procedure**: Document key recovery process
- ✅ **Alternative access**: Maintain alternative access method
- ✅ **Emergency contacts**: Know who can manage repository access

---

## 📋 Checklist

### Pre-Setup
- [ ] Private GitHub repository created
- [ ] VPS access confirmed
- [ ] SSH access to VPS working
- [ ] GitHub repository permissions confirmed

### Setup Process
- [ ] Run `setup-private-github-access.sh`
- [ ] Copy SSH public key
- [ ] Add deploy key to GitHub repository
- [ ] Enable "Allow write access" for deploy key
- [ ] Test SSH connection to GitHub
- [ ] Update deployment scripts with SSH URLs

### Post-Setup Verification
- [ ] SSH connection to GitHub works
- [ ] Repository can be cloned via SSH
- [ ] Deployment scripts updated
- [ ] Test deployment process
- [ ] Document key information

### Security Review
- [ ] Private key secured on VPS
- [ ] Public key added only to required repository
- [ ] SSH configuration reviewed
- [ ] Access permissions verified
- [ ] Monitoring and audit plan established

---

## 🚀 Next Steps

After completing the private repository setup:

1. **Test the authentication**:
   ```bash
   ssh root@217.79.255.54 'ssh -T git@github.com'
   ```

2. **Update deployment scripts** with SSH URLs

3. **Run the GitHub integration setup**:
   ```bash
   ./infrastructure/scripts/setup-github-integration.sh
   ```

4. **Configure webhook** in GitHub repository

5. **Test automated deployment** process

---

## 📞 Support

### Common Commands
```bash
# Test GitHub SSH connection
ssh -T git@github.com

# Check SSH key
cat /root/.ssh/github_deploy_key.pub

# Test repository access
git clone git@github.com:username/repo.git /tmp/test-clone

# View SSH debug info
ssh -vT git@github.com
```

### GitHub Repository Settings
- **Location**: Repository → Settings → Deploy keys
- **Required**: "Allow write access" must be checked
- **Verification**: Key should appear in the deploy keys list

---

**This setup provides secure, production-ready access to private GitHub repositories for automated deployment while maintaining security best practices.**