#!/usr/bin/env python3
"""
Setup GitHub Integration Workflow
Establishes the local → GitHub → VPS deployment workflow
"""

import paramiko
import subprocess
import os
from pathlib import Path

class GitHubWorkflowSetup:
    def __init__(self, host="217.79.255.54", username="root", password="gt5qXy22aJ"):
        self.host = host
        self.username = username
        self.password = password
        self.ssh_client = None
        self.project_name = "agentic-site"
        self.vps_project_path = f"/root/{self.project_name}"
        
    def connect_ssh(self):
        """Connect to VPS via SSH"""
        try:
            print(f"🔌 Connecting to VPS...")
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                hostname=self.host,
                username=self.username,
                password=self.password,
                timeout=30
            )
            print("✅ SSH connection established!")
            return True
        except Exception as e:
            print(f"❌ SSH connection failed: {e}")
            return False
    
    def execute_command(self, command, local=False):
        """Execute command locally or on VPS"""
        try:
            if local:
                print(f"🔧 Local: {command}")
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout.strip()
                error = result.stderr.strip()
                exit_code = result.returncode
            else:
                print(f"🔧 VPS: {command}")
                stdin, stdout, stderr = self.ssh_client.exec_command(command)
                output = stdout.read().decode('utf-8').strip()
                error = stderr.read().decode('utf-8').strip()
                exit_code = stdout.channel.recv_exit_status()
            
            if output:
                print(f"📤 Output: {output}")
            if error and exit_code != 0:
                print(f"⚠️  Error: {error}")
            
            return output, error, exit_code
        except Exception as e:
            print(f"❌ Command failed: {e}")
            return None, str(e), -1
    
    def check_local_git_status(self):
        """Check local git repository status"""
        print("\n📋 Checking local Git status...")
        
        # Check if we're in a git repository
        output, error, exit_code = self.execute_command("git status", local=True)
        if exit_code != 0:
            print("❌ Not in a Git repository or Git not initialized")
            return False
        
        # Check for uncommitted changes (only staged changes, ignore untracked files)
        output, error, exit_code = self.execute_command("git diff --cached --name-only", local=True)
        if output:
            print("⚠️  Staged but uncommitted changes found:")
            print(output)
            print("Please commit your staged changes first.")
            return False
        
        # Check for modified tracked files
        output, error, exit_code = self.execute_command("git diff --name-only", local=True)
        if output:
            print("⚠️  Modified tracked files found:")
            print(output)
            print("Please commit your changes first.")
            return False
        
        # Check current branch
        output, error, exit_code = self.execute_command("git branch --show-current", local=True)
        current_branch = output
        print(f"📍 Current branch: {current_branch}")
        
        # Check remote origin
        output, error, exit_code = self.execute_command("git remote get-url origin", local=True)
        if exit_code == 0:
            print(f"🌐 Remote origin: {output}")
            return True
        else:
            print("❌ No remote origin configured")
            return False
    
    def setup_vps_git_repository(self):
        """Set up Git repository on VPS for deployment"""
        print("\n📦 Setting up Git repository on VPS...")
        
        # Check if project directory exists
        output, error, exit_code = self.execute_command(f"ls -la {self.vps_project_path}")
        if exit_code == 0:
            print(f"📁 Project directory already exists: {self.vps_project_path}")
            # Check if it's a git repository
            output, error, exit_code = self.execute_command(f"cd {self.vps_project_path} && git status")
            if exit_code == 0:
                print("✅ Git repository already initialized on VPS")
                return True
        
        # Create project directory
        self.execute_command(f"mkdir -p {self.vps_project_path}")
        
        # Initialize git repository
        self.execute_command(f"cd {self.vps_project_path} && git init")
        
        # Get the remote origin URL from local
        output, error, exit_code = self.execute_command("git remote get-url origin", local=True)
        if exit_code == 0:
            remote_url = output
            print(f"🔗 Adding remote origin: {remote_url}")
            self.execute_command(f"cd {self.vps_project_path} && git remote add origin {remote_url}")
        
        print("✅ Git repository set up on VPS")
        return True
    
    def create_deployment_script(self):
        """Create deployment script on VPS"""
        print("\n📝 Creating deployment script on VPS...")
        
        deployment_script = f"""#!/bin/bash
# Automated deployment script for {self.project_name}
set -e

PROJECT_DIR="{self.vps_project_path}"
LOG_FILE="/var/log/{self.project_name}-deploy.log"

echo "$(date): Starting deployment..." >> $LOG_FILE

# Navigate to project directory
cd $PROJECT_DIR

# Fetch latest changes
echo "$(date): Fetching from GitHub..." >> $LOG_FILE
git fetch origin

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "$(date): Current branch: $CURRENT_BRANCH" >> $LOG_FILE

# Pull latest changes
echo "$(date): Pulling latest changes..." >> $LOG_FILE
git pull origin $CURRENT_BRANCH

# Stop existing containers
echo "$(date): Stopping existing containers..." >> $LOG_FILE
docker-compose down || true

# Build and start containers
echo "$(date): Building and starting containers..." >> $LOG_FILE
docker-compose up -d --build

# Check container status
echo "$(date): Checking container status..." >> $LOG_FILE
docker-compose ps >> $LOG_FILE

# Health check
sleep 10
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "$(date): Deployment successful - Application is responding" >> $LOG_FILE
    echo "✅ Deployment successful!"
else
    echo "$(date): Deployment warning - Application may not be responding" >> $LOG_FILE
    echo "⚠️  Application may not be responding on port 3000"
fi

echo "$(date): Deployment completed" >> $LOG_FILE
"""
        
        # Write deployment script to VPS
        script_path = f"{self.vps_project_path}/deploy.sh"
        
        # Create the script file
        self.execute_command(f"cat > {script_path} << 'EOF'\n{deployment_script}\nEOF")
        
        # Make it executable
        self.execute_command(f"chmod +x {script_path}")
        
        print(f"✅ Deployment script created: {script_path}")
        return script_path
    
    def test_github_workflow(self):
        """Test the GitHub workflow"""
        print("\n🧪 Testing GitHub workflow...")
        
        # Check local git status
        if not self.check_local_git_status():
            print("❌ Local Git repository not ready")
            return False
        
        # Test VPS git operations
        print("\n📡 Testing VPS Git operations...")
        
        # Try to fetch from remote
        output, error, exit_code = self.execute_command(f"cd {self.vps_project_path} && git fetch origin")
        if exit_code != 0:
            print(f"❌ Failed to fetch from GitHub: {error}")
            return False
        
        print("✅ VPS can fetch from GitHub successfully")
        
        # Test deployment script
        print("\n🚀 Testing deployment script...")
        script_path = f"{self.vps_project_path}/deploy.sh"
        
        # Check if script exists and is executable
        output, error, exit_code = self.execute_command(f"ls -la {script_path}")
        if exit_code != 0:
            print("❌ Deployment script not found")
            return False
        
        print("✅ Deployment script is ready")
        return True
    
    def create_local_push_script(self):
        """Create local script for easy pushing to GitHub"""
        print("\n📝 Creating local push helper script...")
        
        push_script = """#!/bin/bash
# Quick push to GitHub and deploy script
set -e

echo "🚀 Pushing to GitHub and deploying..."

# Check for uncommitted changes
if [[ -n $(git status --porcelain) ]]; then
    echo "⚠️  You have uncommitted changes. Please commit them first."
    git status
    exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push origin $CURRENT_BRANCH

echo "✅ Pushed to GitHub successfully!"
echo ""
echo "🎯 To deploy on VPS, run:"
echo "   ssh root@217.79.255.54 'cd /root/agentic-site && ./deploy.sh'"
echo ""
echo "Or use the deploy script:"
echo "   ./deploy-to-vps.sh"
"""
        
        with open("push-to-github.sh", 'w') as f:
            f.write(push_script)
        
        os.chmod("push-to-github.sh", 0o755)
        print("✅ Created push-to-github.sh")
        
        # Create VPS deployment script
        deploy_script = f"""#!/bin/bash
# Deploy to VPS script
set -e

echo "🚀 Deploying to VPS..."

# SSH to VPS and run deployment
ssh root@{self.host} 'cd {self.vps_project_path} && ./deploy.sh'

echo "✅ Deployment completed!"
"""
        
        with open("deploy-to-vps.sh", 'w') as f:
            f.write(deploy_script)
        
        os.chmod("deploy-to-vps.sh", 0o755)
        print("✅ Created deploy-to-vps.sh")
    
    def setup_workflow(self):
        """Main workflow setup function"""
        print("🔄 SETTING UP GITHUB INTEGRATION WORKFLOW")
        print("="*50)
        
        # Connect to VPS
        if not self.connect_ssh():
            return False
        
        try:
            # Check local git status
            if not self.check_local_git_status():
                print("❌ Please ensure your local repository is properly set up with Git")
                return False
            
            # Set up VPS git repository
            if not self.setup_vps_git_repository():
                return False
            
            # Create deployment script
            self.create_deployment_script()
            
            # Create local helper scripts
            self.create_local_push_script()
            
            # Test the workflow
            if not self.test_github_workflow():
                print("⚠️  Workflow setup completed but testing failed")
                return False
            
            print("\n✅ GITHUB WORKFLOW SETUP COMPLETED!")
            print("\n🎯 WORKFLOW SUMMARY:")
            print("  1. Local Development → GitHub:")
            print("     ./push-to-github.sh")
            print("")
            print("  2. GitHub → VPS Deployment:")
            print("     ./deploy-to-vps.sh")
            print("")
            print("  3. Or deploy directly via SSH:")
            print(f"     ssh root@{self.host} 'cd {self.vps_project_path} && ./deploy.sh'")
            print("")
            print("📋 WORKFLOW PROCESS:")
            print("  1. Make changes locally")
            print("  2. Commit changes: git add . && git commit -m 'message'")
            print("  3. Push to GitHub: ./push-to-github.sh")
            print("  4. Deploy to VPS: ./deploy-to-vps.sh")
            
            return True
            
        except Exception as e:
            print(f"❌ Workflow setup failed: {e}")
            return False
        
        finally:
            if self.ssh_client:
                self.ssh_client.close()

def main():
    """Main function"""
    setup = GitHubWorkflowSetup()
    success = setup.setup_workflow()
    return success

if __name__ == "__main__":
    main()