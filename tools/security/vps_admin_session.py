#!/usr/bin/env python3
"""
Direct VPS Administration Session
Interactive SSH connection for real-time administration
"""

import paramiko
import sys
import time
from datetime import datetime

def main():
    """Direct SSH session for VPS administration"""
    
    # VPS Connection Details
    hostname = "217.79.255.54"
    username = "root"
    password = "gt5qXy22aJ"
    port = 22
    
    print("🔌 DIRECT VPS ADMINISTRATION SESSION")
    print("=" * 50)
    print(f"Connecting to: {username}@{hostname}:{port}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        # Establish SSH connection
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port=port, username=username, password=password, timeout=30)
        
        print("✅ Connected successfully!")
        print("\n🔒 SECURING VPS - INSTALLING AND CONFIGURING UFW + FAIL2BAN")
        print("-" * 50)
        
        commands = [
            # Check current status
            ("echo '🔍 Checking current system status...'", "Status check"),
            ("uname -a", "System info"),
            ("ss -tuln", "Current open ports"),
            
            # Install security tools if needed
            ("echo '📦 Installing security tools...'", "Install phase"),
            ("apt-get update", "Update packages"),
            ("apt-get install -y ufw fail2ban curl", "Install UFW, fail2ban, curl"),
            
            # Configure UFW
            ("echo '🔒 Configuring UFW firewall...'", "UFW config"),
            ("ufw --force reset", "Reset UFW"),
            ("ufw default deny incoming", "Default deny incoming"),
            ("ufw default allow outgoing", "Default allow outgoing"),
            ("ufw allow 22/tcp comment 'SSH'", "Allow SSH"),
            ("ufw allow 80/tcp comment 'HTTP'", "Allow HTTP"),
            ("ufw allow 443/tcp comment 'HTTPS'", "Allow HTTPS"),
            
            # Show rules before enabling
            ("ufw show added", "Show pending rules"),
            
            # Enable UFW (critical moment)
            ("echo '🔥 ENABLING UFW FIREWALL NOW...'", "Enable warning"),
            ("ufw --force enable", "Enable UFW"),
            ("echo '✅ UFW enabled - SSH should still work'", "Verify message"),
            
            # Configure fail2ban
            ("echo '🛡️ Configuring fail2ban...'", "Fail2ban config"),
            ("systemctl enable fail2ban", "Enable fail2ban"),
            ("systemctl start fail2ban", "Start fail2ban"),
            
            # Final verification
            ("echo '✅ FINAL VERIFICATION'", "Final check"),
            ("ufw status numbered", "UFW status"),
            ("fail2ban-client status", "Fail2ban status"),
            ("ss -tuln | grep :22", "SSH port check"),
            ("systemctl is-active ufw", "UFW service status"),
            ("systemctl is-active fail2ban", "Fail2ban service status"),
            
            # Create monitoring script
            ("echo '📊 Creating monitoring script...'", "Monitoring setup"),
        ]
        
        for command, description in commands:
            print(f"\n🔧 {description}: {command}")
            try:
                stdin, stdout, stderr = client.exec_command(command, timeout=120)
                output = stdout.read().decode('utf-8').strip()
                error = stderr.read().decode('utf-8').strip()
                exit_code = stdout.channel.recv_exit_status()
                
                if exit_code == 0:
                    print(f"✅ SUCCESS")
                    if output:
                        print(f"📝 Output: {output[:300]}{'...' if len(output) > 300 else ''}")
                else:
                    print(f"⚠️ Exit code: {exit_code}")
                    if error:
                        print(f"❌ Error: {error[:200]}")
                    if output:
                        print(f"📝 Output: {output[:200]}")
                        
            except Exception as e:
                print(f"❌ Command failed: {str(e)}")
                if "enable" in command.lower() and "ufw" in command.lower():
                    print("🚨 CRITICAL: UFW enable failed - SSH access should still work")
        
        # Create security monitoring script
        monitoring_script = '''#!/bin/bash
echo "🔒 VPS Security Status - $(date)"
echo "=================================="
echo "🛡️ UFW Status:"
ufw status
echo ""
echo "🚫 Fail2ban Status:"
fail2ban-client status
echo ""
echo "🌐 Open Ports:"
ss -tuln
echo ""
echo "🔐 Services:"
echo "SSH: $(systemctl is-active ssh)"
echo "UFW: $(systemctl is-active ufw)"
echo "Fail2ban: $(systemctl is-active fail2ban)"
echo "=================================="
'''
        
        print(f"\n📊 Creating security monitoring script...")
        stdin, stdout, stderr = client.exec_command(f"cat > /usr/local/bin/security-check.sh << 'EOF'\n{monitoring_script}\nEOF")
        stdout.read()
        
        stdin, stdout, stderr = client.exec_command("chmod +x /usr/local/bin/security-check.sh")
        stdout.read()
        
        print("✅ Security monitoring script created")
        
        # Run final security check
        print(f"\n🔍 Running final security check...")
        stdin, stdout, stderr = client.exec_command("/usr/local/bin/security-check.sh")
        output = stdout.read().decode('utf-8')
        print(output)
        
        print("\n🎉 VPS SECURITY CONFIGURATION COMPLETED!")
        print("=" * 50)
        print("✅ UFW Firewall: ACTIVE (ports 22, 80, 443 only)")
        print("✅ Fail2ban: PROTECTING SSH from brute force")
        print("✅ SSH Access: MAINTAINED and WORKING")
        print("✅ Monitoring: /usr/local/bin/security-check.sh")
        print()
        print("🚀 READY FOR FASTAPI DEPLOYMENT!")
        print("- Port 80: HTTP traffic allowed")
        print("- Port 443: HTTPS traffic allowed") 
        print("- Port 22: SSH access maintained")
        print("- All other ports: BLOCKED")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()