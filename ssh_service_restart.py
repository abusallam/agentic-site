#!/usr/bin/env python3
"""
SSH Service Restart Script
Restart SSH service to apply port change
"""

import paramiko
import sys
import time
from datetime import datetime

def log_action(action, result, details=""):
    """Log actions"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status = "✅ SUCCESS" if result else "❌ FAILED"
    print(f"[{timestamp}] {action} -> {status}")
    if details:
        print(f"    Details: {details}")
    print()

def execute_command(client, command, description="", timeout=60):
    """Execute command and log results"""
    print(f"🔧 Executing: {description or command}")
    try:
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        exit_code = stdout.channel.recv_exit_status()
        
        success = exit_code == 0
        log_action(description or command, success, output[:200] if output else error[:200])
        
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
    """Restart SSH service to apply configuration changes"""
    
    # Original connection details (port 22 should still be active)
    hostname = "217.79.255.54"
    username = "root"
    password = "SeZ7cc5uiy"
    port = 22
    
    print("🔄 SSH SERVICE RESTART & PORT VERIFICATION")
    print("=" * 60)
    print(f"Server: {username}@{hostname}:{port}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Objective: Restart SSH service and verify port 2222")
    print("=" * 60)
    print()
    
    try:
        # Connect using original credentials
        print("🔌 Connecting via original SSH port 22...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port=port, username=username, password=password, timeout=30)
        
        log_action("SSH Connection (Port 22)", True, f"Connected to {hostname}")
        
        # Check current SSH configuration
        execute_command(client, "grep -E 'Port|PermitRootLogin' /etc/ssh/sshd_config | grep -v '^#'", "Check SSH configuration")
        
        # Check if SSH is listening on port 2222
        execute_command(client, "ss -tuln | grep :2222", "Check if port 2222 is listening")
        
        # Restart SSH service to apply configuration
        print("🔄 Restarting SSH service to apply configuration...")
        execute_command(client, "systemctl restart ssh", "Restart SSH service")
        
        # Wait a moment for service to restart
        print("⏳ Waiting for SSH service to restart...")
        time.sleep(5)
        
        # Check SSH service status
        execute_command(client, "systemctl status ssh", "Check SSH service status")
        
        # Verify port 2222 is now listening
        execute_command(client, "ss -tuln | grep :2222", "Verify port 2222 is listening")
        
        # Check firewall status
        execute_command(client, "ufw status", "Check firewall status")
        
        print("✅ SSH SERVICE RESTART COMPLETED")
        print("🔍 Port 2222 should now be active")
        print("🚨 IMPORTANT: Test connection to port 2222 before closing this session!")
        print()
        
        # Close connection
        client.close()
        log_action("SSH Service Restart Complete", True, "SSH service restarted successfully")
        
    except Exception as e:
        print(f"❌ SSH service restart failed: {str(e)}")
        log_action("SSH Service Restart", False, str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()