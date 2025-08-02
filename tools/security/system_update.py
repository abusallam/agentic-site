#!/usr/bin/env python3
"""
Create missing system-status.sh script and final verification
"""

import paramiko
import sys

def main():
    hostname = "217.79.255.54"
    username = "root" 
    password = "gt5qXy22aJ"
    port = 22
    
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port=port, username=username, password=password, timeout=30)
        
        # Create the missing system-status.sh script
        system_status_script = """#!/bin/bash
# System Status Monitoring Script
echo "🖥️ System Status Report - $(date)"
echo "=================================="
echo "📊 System Load:"
uptime
echo ""
echo "🧠 Memory Usage:"
free -h
echo ""
echo "💾 Disk Usage:"
df -h /
echo ""
echo "🌐 Network Status:"
ss -tuln | grep :22
echo ""
echo "🔒 SSH Service:"
systemctl is-active ssh
echo ""
echo "🔥 UFW Service:"
systemctl is-active ufw
echo ""
echo "🛡️ Fail2ban Service:"
systemctl is-active fail2ban
echo ""
echo "🚀 FastAPI Service:"
systemctl is-active fastapi
echo ""
echo "🐳 Docker Service:"
systemctl is-active docker
echo ""
echo "👥 Current Users:"
who
echo ""
echo "📈 Top Processes:"
ps aux --sort=-%cpu | head -6
echo "=================================="
"""
        
        # Install the script
        stdin, stdout, stderr = client.exec_command(f"echo '{system_status_script}' | sudo tee /usr/local/bin/system-status.sh && sudo chmod +x /usr/local/bin/system-status.sh")
        stdout.read()
        
        print("✅ Created missing system-status.sh script")
        
        # Test the script
        stdin, stdout, stderr = client.exec_command("/usr/local/bin/system-status.sh")
        output = stdout.read().decode('utf-8')
        print("📊 System Status Test:")
        print(output)
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        return False

if __name__ == "__main__":
    main()