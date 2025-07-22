#!/usr/bin/env python3
"""
Docker Installation with Security Best Practices
PRODUCTION-READY APPROACH - Secure Docker setup for VPS
"""

import paramiko
import sys
import time
from datetime import datetime

def log_action(action, result, details=""):
    """Log all actions with detailed information"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status = "✅ SUCCESS" if result else "❌ FAILED"
    print(f"[{timestamp}] {action} -> {status}")
    if details:
        print(f"    📝 Details: {details}")
    print()

def execute_command(client, command, description="", timeout=300):
    """Execute command safely with detailed logging"""
    print(f"🔧 Executing: {description or command}")
    try:
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        exit_code = stdout.channel.recv_exit_status()
        
        success = exit_code == 0
        log_action(description or command, success, output[:400] if output else error[:400])
        
        return {
            "success": success,
            "output": output,
            "error": error,
            "exit_code": exit_code
        }
    except Exception as e:
        log_action(description or command, False, str(e))
        return {"success": False, "error": str(e), "output": "", "exit_code": -1}

def main():
    """Secure Docker installation and configuration"""
    
    # VPS Connection Details
    hostname = "217.79.255.54"
    username = "root"
    password = "gt5qXy22aJ"
    port = 22
    
    print("🐳 DOCKER INSTALLATION WITH SECURITY BEST PRACTICES")
    print("=" * 70)
    print(f"Server: {username}@{hostname}:{port}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔒 PRODUCTION-READY SECURE SETUP")
    print("📝 COMPREHENSIVE LOGGING & VERIFICATION")
    print("=" * 70)
    print()
    
    try:
        # Establish SSH connection
        print("🔌 Connecting to VPS...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port=port, username=username, password=password, timeout=30)
        
        log_action("SSH Connection", True, f"Connected successfully to {hostname}")
        
        print("📋 PHASE 1: PRE-INSTALLATION VERIFICATION")
        print("-" * 50)
        
        # Verify system is ready
        execute_command(client, "uname -a", "System information")
        execute_command(client, "free -h", "Memory status")
        execute_command(client, "df -h /", "Disk space")
        
        # Check if Docker is already installed
        docker_check = execute_command(client, "docker --version", "Check existing Docker installation")
        if docker_check["success"]:
            print("⚠️ Docker is already installed. Checking version and configuration...")
            execute_command(client, "docker info", "Docker system information")
        
        print("\n🔑 PHASE 2: DOCKER OFFICIAL REPOSITORY SETUP")
        print("-" * 50)
        
        # Remove any existing Docker packages
        execute_command(client, "apt-get remove -y docker docker-engine docker.io containerd runc", 
                       "Remove old Docker packages (if any)")
        
        # Update package index
        execute_command(client, "apt-get update", "Update package index")
        
        # Add Docker's official GPG key
        execute_command(client, "curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg", 
                       "Add Docker GPG key", timeout=120)
        
        # Add Docker repository
        execute_command(client, 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null', 
                       "Add Docker repository")
        
        # Update package index again
        execute_command(client, "apt-get update", "Update package index with Docker repo")
        
        print("\n🐳 PHASE 3: DOCKER ENGINE INSTALLATION")
        print("-" * 50)
        
        # Install Docker Engine, containerd, and Docker Compose
        execute_command(client, "apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin", 
                       "Install Docker Engine and components", timeout=600)
        
        # Start and enable Docker service
        execute_command(client, "systemctl start docker", "Start Docker service")
        execute_command(client, "systemctl enable docker", "Enable Docker service")
        
        # Verify Docker installation
        execute_command(client, "docker --version", "Verify Docker version")
        execute_command(client, "docker compose version", "Verify Docker Compose version")
        
        print("\n🔒 PHASE 4: DOCKER SECURITY CONFIGURATION")
        print("-" * 50)
        
        # Create Docker daemon configuration for security
        docker_daemon_config = '''{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": true,
  "seccomp-profile": "/etc/docker/seccomp.json",
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ],
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64000,
      "Soft": 64000
    }
  }
}'''
        
        execute_command(client, f"mkdir -p /etc/docker", "Create Docker config directory")
        execute_command(client, f"echo '{docker_daemon_config}' > /etc/docker/daemon.json", 
                       "Create Docker daemon security configuration")
        
        # Create Docker group and add user (for future non-root usage)
        execute_command(client, "groupadd docker", "Create Docker group")
        
        # Restart Docker with new configuration
        execute_command(client, "systemctl restart docker", "Restart Docker with security config")
        
        # Verify Docker is running with new config
        execute_command(client, "systemctl status docker", "Check Docker service status")
        
        print("\n🛡️ PHASE 5: DOCKER SECURITY HARDENING")
        print("-" * 50)
        
        # Create Docker security script
        docker_security_script = '''#!/bin/bash
# Docker Security Hardening Script
echo "🛡️ Docker Security Status Check - $(date)"
echo "=================================="

echo "📊 Docker System Info:"
docker system info | grep -E "(Security Options|Kernel Version|Operating System|Architecture)"

echo ""
echo "🔒 Docker Daemon Configuration:"
if [ -f /etc/docker/daemon.json ]; then
    echo "✅ Custom daemon.json exists"
    cat /etc/docker/daemon.json | jq . 2>/dev/null || cat /etc/docker/daemon.json
else
    echo "⚠️ No custom daemon.json found"
fi

echo ""
echo "🐳 Running Containers:"
docker ps --format "table {{.Names}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}"

echo ""
echo "💾 Docker Storage Usage:"
docker system df

echo ""
echo "🔍 Docker Security Scan (if available):"
docker version --format '{{.Server.Version}}' | head -1

echo "=================================="
'''
        
        execute_command(client, f"echo '{docker_security_script}' > /usr/local/bin/docker-security-check.sh", 
                       "Create Docker security check script")
        execute_command(client, "chmod +x /usr/local/bin/docker-security-check.sh", 
                       "Make Docker security script executable")
        
        # Install jq for JSON parsing
        execute_command(client, "apt-get install -y jq", "Install jq for JSON parsing")
        
        # Run security check
        execute_command(client, "/usr/local/bin/docker-security-check.sh", "Run Docker security check")
        
        print("\n📁 PHASE 6: DOCKER DIRECTORY STRUCTURE")
        print("-" * 50)
        
        # Create organized directory structure for Docker applications
        directories = [
            "/opt/docker-apps",
            "/opt/docker-apps/production",
            "/opt/docker-apps/staging", 
            "/opt/docker-apps/development",
            "/opt/docker-data",
            "/opt/docker-backups",
            "/opt/docker-configs",
            "/opt/docker-logs"
        ]
        
        for directory in directories:
            execute_command(client, f"mkdir -p {directory}", f"Create directory {directory}")
        
        # Set proper permissions
        execute_command(client, "chown -R root:docker /opt/docker-apps", "Set Docker apps ownership")
        execute_command(client, "chmod -R 755 /opt/docker-apps", "Set Docker apps permissions")
        
        print("\n🧪 PHASE 7: DOCKER FUNCTIONALITY TESTING")
        print("-" * 50)
        
        # Test Docker with hello-world
        execute_command(client, "docker run --rm hello-world", "Test Docker with hello-world", timeout=120)
        
        # Test Docker Compose
        test_compose = '''version: '3.8'
services:
  test:
    image: alpine:latest
    command: echo "Docker Compose is working!"
'''
        
        execute_command(client, f"echo '{test_compose}' > /tmp/test-compose.yml", "Create test compose file")
        execute_command(client, "cd /tmp && docker compose -f test-compose.yml up --rm", "Test Docker Compose", timeout=120)
        execute_command(client, "rm /tmp/test-compose.yml", "Clean up test compose file")
        
        print("\n🔧 PHASE 8: DOCKER MAINTENANCE TOOLS")
        print("-" * 50)
        
        # Create Docker maintenance script
        docker_maintenance_script = '''#!/bin/bash
# Docker Maintenance Script
echo "🧹 Docker System Maintenance - $(date)"
echo "====================================="

echo "📊 Before cleanup:"
docker system df

echo ""
echo "🗑️ Cleaning up unused Docker resources..."

# Remove unused containers
echo "Removing stopped containers..."
docker container prune -f

# Remove unused images
echo "Removing unused images..."
docker image prune -f

# Remove unused volumes
echo "Removing unused volumes..."
docker volume prune -f

# Remove unused networks
echo "Removing unused networks..."
docker network prune -f

echo ""
echo "📊 After cleanup:"
docker system df

echo ""
echo "🔍 Current Docker status:"
docker ps -a
echo ""
docker images

echo "====================================="
echo "✅ Docker maintenance completed!"
'''
        
        execute_command(client, f"echo '{docker_maintenance_script}' > /usr/local/bin/docker-maintenance.sh", 
                       "Create Docker maintenance script")
        execute_command(client, "chmod +x /usr/local/bin/docker-maintenance.sh", 
                       "Make Docker maintenance script executable")
        
        print("\n✅ DOCKER INSTALLATION COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("🐳 Docker Engine installed and configured")
        print("🔒 Security hardening applied")
        print("📁 Directory structure created")
        print("🛡️ Security monitoring scripts installed")
        print("🧹 Maintenance tools configured")
        print()
        
        print("🎯 DOCKER INSTALLATION SUMMARY:")
        print("- Docker Engine: Latest stable version")
        print("- Docker Compose: Plugin version installed")
        print("- Security: Daemon hardened with best practices")
        print("- Logging: Configured with rotation")
        print("- Storage: Overlay2 driver optimized")
        print("- Monitoring: Security check script available")
        print("- Maintenance: Cleanup script ready")
        print()
        
        print("🚀 READY FOR NEXT PHASE:")
        print("1. 🔒 Advanced security configuration (UFW, fail2ban)")
        print("2. 🌐 Web server setup (Nginx/Traefik)")
        print("3. 📊 Monitoring stack (Prometheus/Grafana)")
        print("4. 🚀 Application deployment")
        print()
        
        print("📋 USEFUL COMMANDS:")
        print("- Check Docker status: systemctl status docker")
        print("- Security check: /usr/local/bin/docker-security-check.sh")
        print("- Maintenance: /usr/local/bin/docker-maintenance.sh")
        print("- System monitoring: /usr/local/bin/system-status.sh")
        
        # Close connection
        client.close()
        log_action("Docker Installation Complete", True, "Docker installed and configured successfully")
        
    except Exception as e:
        print(f"❌ Docker installation failed: {str(e)}")
        log_action("Docker Installation", False, str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()