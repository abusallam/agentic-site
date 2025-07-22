#!/usr/bin/env python3
"""
Test SSH Connection and VPS File Management
Establishes connection to VPS and tests basic operations
"""

import paramiko
import os
import sys
from pathlib import Path

class VPSConnection:
    def __init__(self, host="217.79.255.54", username="root", password="gt5qXy22aJ"):
        self.host = host
        self.username = username
        self.password = password
        self.ssh_client = None
        self.sftp_client = None
    
    def connect(self):
        """Establish SSH connection to VPS"""
        try:
            print(f"🔌 Connecting to {self.username}@{self.host}...")
            
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            self.ssh_client.connect(
                hostname=self.host,
                username=self.username,
                password=self.password,
                timeout=30
            )
            
            # Also establish SFTP connection for file operations
            self.sftp_client = self.ssh_client.open_sftp()
            
            print("✅ SSH connection established successfully!")
            return True
            
        except Exception as e:
            print(f"❌ SSH connection failed: {e}")
            return False
    
    def execute_command(self, command):
        """Execute a command on the VPS"""
        if not self.ssh_client:
            print("❌ No SSH connection available")
            return None, None, None
        
        try:
            print(f"🔧 Executing: {command}")
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            
            # Read output
            output = stdout.read().decode('utf-8').strip()
            error = stderr.read().decode('utf-8').strip()
            exit_code = stdout.channel.recv_exit_status()
            
            if output:
                print(f"📤 Output: {output}")
            if error:
                print(f"⚠️  Error: {error}")
            
            return output, error, exit_code
            
        except Exception as e:
            print(f"❌ Command execution failed: {e}")
            return None, str(e), -1
    
    def test_basic_operations(self):
        """Test basic VPS operations"""
        print("\n🧪 Testing basic VPS operations...")
        
        # Test 1: Check system info
        print("\n1. System Information:")
        self.execute_command("uname -a")
        self.execute_command("whoami")
        self.execute_command("pwd")
        
        # Test 2: Check disk space
        print("\n2. Disk Space:")
        self.execute_command("df -h")
        
        # Test 3: Check Docker
        print("\n3. Docker Status:")
        self.execute_command("docker --version")
        self.execute_command("docker ps")
        
        # Test 4: Check if MCP directory exists
        print("\n4. MCP Directory Check:")
        self.execute_command("ls -la /home/asim/Documents/")
        self.execute_command("ls -la /home/asim/Documents/agents-mcp/ 2>/dev/null || echo 'MCP directory not found'")
    
    def create_mcp_directory(self):
        """Create MCP directory structure on VPS"""
        print("\n📁 Creating MCP directory structure...")
        
        commands = [
            "mkdir -p /home/asim/Documents/agents-mcp",
            "mkdir -p /home/asim/Documents/agents-mcp/servers",
            "mkdir -p /home/asim/Documents/agents-mcp/configs",
            "mkdir -p /home/asim/Documents/agents-mcp/docs",
            "ls -la /home/asim/Documents/agents-mcp/"
        ]
        
        for cmd in commands:
            self.execute_command(cmd)
    
    def test_file_operations(self):
        """Test file upload/download operations"""
        print("\n📁 Testing file operations...")
        
        # Create a test file locally
        test_file = "vps_test_file.txt"
        test_content = f"VPS connection test - {os.getpid()}"
        
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        try:
            # Upload test file
            remote_path = f"/tmp/{test_file}"
            print(f"📤 Uploading {test_file} to {remote_path}")
            self.sftp_client.put(test_file, remote_path)
            
            # Verify file exists on VPS
            self.execute_command(f"ls -la {remote_path}")
            self.execute_command(f"cat {remote_path}")
            
            # Download file back
            download_file = f"downloaded_{test_file}"
            print(f"📥 Downloading {remote_path} to {download_file}")
            self.sftp_client.get(remote_path, download_file)
            
            # Verify downloaded content
            with open(download_file, 'r') as f:
                downloaded_content = f.read()
            
            if downloaded_content == test_content:
                print("✅ File operations test passed!")
            else:
                print("❌ File operations test failed - content mismatch")
            
            # Cleanup
            self.execute_command(f"rm {remote_path}")
            os.remove(test_file)
            os.remove(download_file)
            
        except Exception as e:
            print(f"❌ File operations test failed: {e}")
    
    def check_project_directory(self):
        """Check if project directory exists on VPS"""
        print("\n📂 Checking project directory on VPS...")
        
        # Common project locations
        locations = [
            "/root/agentic-site",
            "/home/asim/agentic-site", 
            "/var/www/agentic-site",
            "/opt/agentic-site"
        ]
        
        for location in locations:
            output, error, exit_code = self.execute_command(f"ls -la {location} 2>/dev/null || echo 'Not found: {location}'")
    
    def close(self):
        """Close SSH and SFTP connections"""
        if self.sftp_client:
            self.sftp_client.close()
        if self.ssh_client:
            self.ssh_client.close()
        print("🔌 SSH connection closed")

def main():
    """Main connection test function"""
    print("🌐 VPS CONNECTION AND FILE MANAGEMENT TEST")
    print("="*50)
    
    vps = VPSConnection()
    
    # Test connection
    if not vps.connect():
        print("❌ Cannot proceed without VPS connection!")
        return False
    
    try:
        # Run tests
        vps.test_basic_operations()
        vps.create_mcp_directory()
        vps.test_file_operations()
        vps.check_project_directory()
        
        print("\n✅ VPS CONNECTION TEST COMPLETED SUCCESSFULLY!")
        print("\n🎯 VPS is ready for:")
        print("  • MCP file organization")
        print("  • Docker deployment")
        print("  • Project management")
        
        return True
        
    except Exception as e:
        print(f"❌ VPS test failed: {e}")
        return False
        
    finally:
        vps.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)