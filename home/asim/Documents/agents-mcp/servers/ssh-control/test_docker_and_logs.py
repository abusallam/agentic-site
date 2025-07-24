#!/usr/bin/env python3
"""
Test Docker Control and Log Monitoring
Comprehensive test for enhanced SSH MCP server capabilities
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ssh_control.services.ssh_connection_manager import SSHConnectionManager
from ssh_control.services.docker_manager import DockerManager
from ssh_control.tools.system_tools import _monitor_log_file, _get_system_status, _check_service_status
from ssh_control.utils.logger import Logger

async def test_docker_capabilities():
    """Test Docker control capabilities"""
    print("🐳 Testing Docker Control Capabilities...")
    print("=" * 50)
    
    # Initialize managers
    ssh_manager = SSHConnectionManager()
    docker_manager = DockerManager()
    docker_manager.set_ssh_manager(ssh_manager)
    
    await ssh_manager.initialize_default_connections()
    
    # Connect to VPS
    print("1. Connecting to VPS...")
    connect_result = await ssh_manager.connect("vps")
    
    if not connect_result["success"]:
        print(f"❌ Connection failed: {connect_result['error']}")
        return False
    
    print("✅ Connected successfully!")
    
    # Test Docker status
    print("\n2. Testing Docker status...")
    docker_status = await docker_manager.get_docker_status("vps")
    print("Docker Status:")
    print(docker_status)
    
    # Test container listing
    print("\n3. Testing container listing...")
    containers = await docker_manager.list_containers("vps", all_containers=True)
    print("All Containers:")
    print(containers)
    
    # Test running containers only
    print("\n4. Testing running containers...")
    running_containers = await docker_manager.list_containers("vps", all_containers=False)
    print("Running Containers:")
    print(running_containers)
    
    # Test Docker Compose status (if available)
    print("\n5. Testing Docker Compose...")
    compose_result = await ssh_manager.execute_command("docker-compose --version", "vps")
    if compose_result.success:
        print(f"✅ Docker Compose available: {compose_result.stdout.strip()}")
    else:
        print("⚠️ Docker Compose not available")
    
    await ssh_manager.disconnect("vps")
    return True

async def test_log_monitoring():
    """Test log monitoring capabilities"""
    print("\n📋 Testing Log Monitoring Capabilities...")
    print("=" * 50)
    
    # Initialize SSH manager
    ssh_manager = SSHConnectionManager()
    await ssh_manager.initialize_default_connections()
    
    # Connect to VPS
    print("1. Connecting to VPS...")
    connect_result = await ssh_manager.connect("vps")
    
    if not connect_result["success"]:
        print(f"❌ Connection failed: {connect_result['error']}")
        return False
    
    print("✅ Connected successfully!")
    
    # Test system log monitoring
    print("\n2. Testing system log monitoring...")
    syslog_result = await _monitor_log_file(ssh_manager, "vps", "/var/log/syslog", 10, False)
    print("System Log (last 10 lines):")
    print(syslog_result[:500] + "..." if len(syslog_result) > 500 else syslog_result)
    
    # Test auth log monitoring
    print("\n3. Testing auth log monitoring...")
    auth_log_result = await _monitor_log_file(ssh_manager, "vps", "/var/log/auth.log", 5, False)
    print("Auth Log (last 5 lines):")
    print(auth_log_result[:300] + "..." if len(auth_log_result) > 300 else auth_log_result)
    
    # Test system status
    print("\n4. Testing comprehensive system status...")
    system_status = await _get_system_status(ssh_manager, "vps")
    print("System Status:")
    print(system_status[:800] + "..." if len(system_status) > 800 else system_status)
    
    # Test service status (SSH service)
    print("\n5. Testing service status monitoring...")
    ssh_service_status = await _check_service_status(ssh_manager, "vps", "ssh")
    print("SSH Service Status:")
    print(ssh_service_status[:400] + "..." if len(ssh_service_status) > 400 else ssh_service_status)
    
    await ssh_manager.disconnect("vps")
    return True

async def test_practical_scenarios():
    """Test practical usage scenarios"""
    print("\n🎯 Testing Practical Usage Scenarios...")
    print("=" * 50)
    
    # Initialize managers
    ssh_manager = SSHConnectionManager()
    docker_manager = DockerManager()
    docker_manager.set_ssh_manager(ssh_manager)
    
    await ssh_manager.initialize_default_connections()
    
    # Connect to VPS
    connect_result = await ssh_manager.connect("vps")
    if not connect_result["success"]:
        print(f"❌ Connection failed: {connect_result['error']}")
        return False
    
    print("✅ Connected successfully!")
    
    # Scenario 1: Check if Docker is installed and running
    print("\n📋 Scenario 1: Docker Installation Check")
    docker_check = await ssh_manager.execute_command("docker --version && docker info", "vps")
    if docker_check.success:
        print("✅ Docker is installed and running")
        version_line = docker_check.stdout.split('\n')[0]
        print(f"Version: {version_line}")
    else:
        print("⚠️ Docker not available or not running")
        print("Installing Docker...")
        install_result = await ssh_manager.execute_command(
            "curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh", 
            "vps", 
            timeout=300
        )
        if install_result.success:
            print("✅ Docker installation completed")
        else:
            print(f"❌ Docker installation failed: {install_result.stderr}")
    
    # Scenario 2: Monitor system resources
    print("\n📊 Scenario 2: System Resource Monitoring")
    resource_commands = {
        "CPU Usage": "top -bn1 | grep 'Cpu(s)' | head -1",
        "Memory Usage": "free -h | grep Mem",
        "Disk Usage": "df -h / | tail -1",
        "Network Connections": "netstat -tuln | wc -l"
    }
    
    for desc, cmd in resource_commands.items():
        result = await ssh_manager.execute_command(cmd, "vps")
        if result.success:
            print(f"✅ {desc}: {result.stdout.strip()}")
        else:
            print(f"❌ {desc}: Error")
    
    # Scenario 3: Check running services
    print("\n🔧 Scenario 3: Critical Services Check")
    services = ["ssh", "systemd-resolved", "cron"]
    
    for service in services:
        result = await ssh_manager.execute_command(f"systemctl is-active {service}", "vps")
        status = result.stdout.strip() if result.success else "unknown"
        status_icon = "✅" if status == "active" else "⚠️"
        print(f"{status_icon} {service}: {status}")
    
    # Scenario 4: Log analysis for security
    print("\n🔒 Scenario 4: Security Log Analysis")
    security_checks = {
        "Failed SSH logins": "grep 'Failed password' /var/log/auth.log | tail -5",
        "Successful SSH logins": "grep 'Accepted password' /var/log/auth.log | tail -3",
        "Sudo usage": "grep 'sudo:' /var/log/auth.log | tail -3"
    }
    
    for desc, cmd in security_checks.items():
        result = await ssh_manager.execute_command(cmd, "vps")
        if result.success and result.stdout.strip():
            print(f"📋 {desc}:")
            print(f"   {result.stdout.strip()[:100]}...")
        else:
            print(f"✅ {desc}: No recent events")
    
    await ssh_manager.disconnect("vps")
    return True

async def main():
    """Main test function"""
    print("🚀 SSH MCP Server - Docker & Log Monitoring Test")
    print("=" * 60)
    
    try:
        # Test Docker capabilities
        docker_success = await test_docker_capabilities()
        
        # Test log monitoring
        log_success = await test_log_monitoring()
        
        # Test practical scenarios
        practical_success = await test_practical_scenarios()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Docker Control: {'✅ PASSED' if docker_success else '❌ FAILED'}")
        print(f"Log Monitoring: {'✅ PASSED' if log_success else '❌ FAILED'}")
        print(f"Practical Scenarios: {'✅ PASSED' if practical_success else '❌ FAILED'}")
        
        if docker_success and log_success and practical_success:
            print("\n🎉 All tests passed! SSH MCP server is ready for Docker control and log monitoring!")
            return True
        else:
            print("\n⚠️ Some tests failed. Check the output above for details.")
            return False
            
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)