#!/usr/bin/env python3
"""
Connection Test Script
Test various connection methods to diagnose SSH issues
"""

import paramiko
import socket
import sys
from datetime import datetime

def test_port(hostname, port, timeout=10):
    """Test if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((hostname, port))
        sock.close()
        return result == 0
    except Exception as e:
        return False

def test_ssh_connection(hostname, port, username, password, timeout=10):
    """Test SSH connection"""
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port=port, username=username, password=password, timeout=timeout)
        
        # Test a simple command
        stdin, stdout, stderr = client.exec_command("whoami", timeout=5)
        output = stdout.read().decode('utf-8').strip()
        client.close()
        
        return True, output
    except Exception as e:
        return False, str(e)

def main():
    """Test various connection methods"""
    
    hostname = "217.79.255.54"
    
    print("🔍 VPS CONNECTION DIAGNOSTIC TEST")
    print("=" * 50)
    print(f"Target: {hostname}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    print()
    
    # Test different ports
    ports_to_test = [22, 2222, 80, 443]
    
    print("📡 PORT CONNECTIVITY TEST")
    print("-" * 30)
    
    for port in ports_to_test:
        print(f"Testing port {port}...", end=" ")
        if test_port(hostname, port):
            print("✅ OPEN")
        else:
            print("❌ CLOSED/FILTERED")
    
    print()
    
    # Test SSH connections
    print("🔐 SSH CONNECTION TEST")
    print("-" * 30)
    
    # Test configurations
    test_configs = [
        {"port": 22, "username": "root", "password": "SeZ7cc5uiy", "desc": "Original root@22"},
        {"port": 2222, "username": "root", "password": "SeZ7cc5uiy", "desc": "Root@2222"},
        {"port": 2222, "username": "admin", "password": "TempAdmin123!", "desc": "Admin@2222"},
        {"port": 22, "username": "admin", "password": "TempAdmin123!", "desc": "Admin@22"}
    ]
    
    for config in test_configs:
        print(f"Testing {config['desc']}...", end=" ")
        success, result = test_ssh_connection(
            hostname, 
            config['port'], 
            config['username'], 
            config['password']
        )
        
        if success:
            print(f"✅ SUCCESS (user: {result})")
        else:
            print(f"❌ FAILED ({result[:50]}...)")
    
    print()
    print("🎯 DIAGNOSIS COMPLETE")
    print("If all connections failed, the server might be:")
    print("1. Restarting SSH service")
    print("2. Firewall blocking connections")
    print("3. SSH configuration issue")
    print("4. Network connectivity problem")

if __name__ == "__main__":
    main()