#!/usr/bin/env python3
"""
Organize MCP Files on VPS
Transfers MCP-related files to their proper location on the VPS
"""

import paramiko
import json
import os
from pathlib import Path
from typing import List, Dict

class MCPOrganizer:
    def __init__(self, host="217.79.255.54", username="root", password="gt5qXy22aJ"):
        self.host = host
        self.username = username
        self.password = password
        self.ssh_client = None
        self.sftp_client = None
        self.mcp_target_dir = "/home/asim/Documents/agents-mcp"
        
        # Load analysis data to identify MCP files
        self.analysis_data = self.load_analysis()
        self.transfer_log = {
            "transferred_files": [],
            "skipped_files": [],
            "errors": []
        }
    
    def load_analysis(self) -> Dict:
        """Load project analysis data"""
        try:
            with open("project_analysis.json", 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ Analysis file not found!")
            return {}
    
    def connect(self):
        """Establish SSH connection"""
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
            
            self.sftp_client = self.ssh_client.open_sftp()
            print("✅ SSH connection established!")
            return True
            
        except Exception as e:
            print(f"❌ SSH connection failed: {e}")
            return False
    
    def execute_command(self, command):
        """Execute command on VPS"""
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            output = stdout.read().decode('utf-8').strip()
            error = stderr.read().decode('utf-8').strip()
            return output, error
        except Exception as e:
            return None, str(e)
    
    def identify_mcp_files(self) -> List[str]:
        """Identify MCP files that need to be transferred"""
        mcp_files = []
        
        # MCP-related patterns
        mcp_patterns = [
            'home/asim/Documents/agents-mcp/',
            'n8n-mcp/',
            'agent/n8n_mcp_agent/',
            'agent/my_adk_agent/',
        ]
        
        # Check all files in the project
        for root, dirs, files in os.walk('.'):
            # Skip certain directories
            skip_dirs = {'.git', 'node_modules', '.next', '__pycache__', '.venv', 'backups'}
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, '.')
                
                # Check if file matches MCP patterns
                if any(pattern in relative_path for pattern in mcp_patterns):
                    mcp_files.append(relative_path)
                
                # Also check for specific MCP file types
                if (file.endswith('.py') and 
                    ('mcp' in file.lower() or 'n8n' in file.lower())):
                    mcp_files.append(relative_path)
        
        return mcp_files
    
    def create_remote_directory(self, remote_path: str):
        """Create directory on VPS if it doesn't exist"""
        try:
            # Try to create the directory
            command = f"mkdir -p {remote_path}"
            output, error = self.execute_command(command)
            if error:
                print(f"⚠️  Warning creating directory {remote_path}: {error}")
            return True
        except Exception as e:
            print(f"❌ Failed to create directory {remote_path}: {e}")
            return False
    
    def transfer_file(self, local_path: str, remote_path: str) -> bool:
        """Transfer a single file to VPS"""
        try:
            # Create remote directory if needed
            remote_dir = os.path.dirname(remote_path)
            self.create_remote_directory(remote_dir)
            
            # Transfer file
            print(f"📤 Transferring: {local_path} -> {remote_path}")
            self.sftp_client.put(local_path, remote_path)
            
            # Set proper permissions
            self.execute_command(f"chmod 644 {remote_path}")
            
            self.transfer_log["transferred_files"].append({
                "local": local_path,
                "remote": remote_path
            })
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to transfer {local_path}: {e}"
            print(f"❌ {error_msg}")
            self.transfer_log["errors"].append(error_msg)
            return False
    
    def organize_mcp_files(self):
        """Main function to organize MCP files on VPS"""
        print("🔧 ORGANIZING MCP FILES ON VPS")
        print("="*40)
        
        # Get list of MCP files
        mcp_files = self.identify_mcp_files()
        print(f"📋 Found {len(mcp_files)} MCP-related files")
        
        if not mcp_files:
            print("ℹ️  No MCP files found to transfer")
            return True
        
        # Show first 10 files
        print("📁 MCP files to transfer:")
        for file_path in mcp_files[:10]:
            print(f"  • {file_path}")
        if len(mcp_files) > 10:
            print(f"  ... and {len(mcp_files) - 10} more")
        
        # Transfer files
        transferred_count = 0
        for local_file in mcp_files:
            if not os.path.exists(local_file):
                print(f"⚠️  Local file not found: {local_file}")
                self.transfer_log["skipped_files"].append(local_file)
                continue
            
            # Determine remote path
            if local_file.startswith('home/asim/Documents/agents-mcp/'):
                # Files already in the correct structure
                remote_file = f"/{local_file}"
            elif local_file.startswith('n8n-mcp/'):
                # N8N MCP files go to servers directory
                relative_path = local_file[8:]  # Remove 'n8n-mcp/' prefix
                remote_file = f"{self.mcp_target_dir}/servers/n8n-mcp/{relative_path}"
            elif local_file.startswith('agent/'):
                # Agent files go to servers directory
                remote_file = f"{self.mcp_target_dir}/servers/{local_file}"
            else:
                # Other MCP files go to root of MCP directory
                remote_file = f"{self.mcp_target_dir}/{os.path.basename(local_file)}"
            
            # Transfer the file
            if self.transfer_file(local_file, remote_file):
                transferred_count += 1
        
        print(f"\n📊 TRANSFER SUMMARY:")
        print(f"  • Files transferred: {transferred_count}")
        print(f"  • Files skipped: {len(self.transfer_log['skipped_files'])}")
        print(f"  • Errors: {len(self.transfer_log['errors'])}")
        
        return len(self.transfer_log['errors']) == 0
    
    def set_mcp_permissions(self):
        """Set proper permissions for MCP files"""
        print("\n🔐 Setting MCP file permissions...")
        
        commands = [
            f"chown -R root:root {self.mcp_target_dir}",
            f"find {self.mcp_target_dir} -type d -exec chmod 755 {{}} \\;",
            f"find {self.mcp_target_dir} -type f -name '*.py' -exec chmod 755 {{}} \\;",
            f"find {self.mcp_target_dir} -type f -name '*.json' -exec chmod 644 {{}} \\;",
            f"find {self.mcp_target_dir} -type f -name '*.md' -exec chmod 644 {{}} \\;",
        ]
        
        for cmd in commands:
            output, error = self.execute_command(cmd)
            if error:
                print(f"⚠️  Permission warning: {error}")
        
        print("✅ Permissions set")
    
    def verify_mcp_structure(self):
        """Verify MCP directory structure on VPS"""
        print("\n🔍 Verifying MCP structure on VPS...")
        
        # Check main directory
        output, error = self.execute_command(f"ls -la {self.mcp_target_dir}")
        if output:
            print(f"📁 {self.mcp_target_dir}:")
            print(output)
        
        # Check subdirectories
        subdirs = ['servers', 'configs', 'docs']
        for subdir in subdirs:
            full_path = f"{self.mcp_target_dir}/{subdir}"
            output, error = self.execute_command(f"ls -la {full_path} 2>/dev/null || echo 'Empty: {full_path}'")
            if output:
                print(f"\n📁 {full_path}:")
                print(output[:500] + "..." if len(output) > 500 else output)
    
    def save_transfer_log(self):
        """Save transfer log"""
        log_file = "mcp_transfer_log.json"
        with open(log_file, 'w') as f:
            json.dump(self.transfer_log, f, indent=2)
        print(f"📋 Transfer log saved: {log_file}")
    
    def close(self):
        """Close connections"""
        if self.sftp_client:
            self.sftp_client.close()
        if self.ssh_client:
            self.ssh_client.close()

def main():
    """Main MCP organization function"""
    organizer = MCPOrganizer()
    
    if not organizer.connect():
        print("❌ Cannot proceed without VPS connection!")
        return False
    
    try:
        # Organize MCP files
        success = organizer.organize_mcp_files()
        
        # Set permissions
        organizer.set_mcp_permissions()
        
        # Verify structure
        organizer.verify_mcp_structure()
        
        # Save log
        organizer.save_transfer_log()
        
        if success:
            print("\n✅ MCP FILES ORGANIZED SUCCESSFULLY!")
            print(f"🎯 MCP files are now properly organized at: {organizer.mcp_target_dir}")
        else:
            print("\n⚠️  MCP organization completed with errors")
        
        return success
        
    except Exception as e:
        print(f"❌ MCP organization failed: {e}")
        return False
        
    finally:
        organizer.close()

if __name__ == "__main__":
    main()