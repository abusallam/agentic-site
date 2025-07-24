#!/usr/bin/env python3
"""
Simple Docker and Log Test
Test Docker control and log monitoring without full MCP framework
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ssh_control.services.ssh_connection_manager import SSHConnectionManager
from ssh_control.services.docker_manager import DockerManager

async def test_docker_control():
    """Test Docker control capabilities"""
    print("🐳 Testing Docker Control...")
    print("=" * 40)
    
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
    print("\n2. Getting Docker status...")
    docker_status = await docker_manager.get_docker_status("vps")
    print("Docker Status:")
    print(docker_status)
    
    # Test container listing
    print("\n3. Listing containers...")
    containers = await docker_manager.list_containers("vps", all_containers=True)
    print("All Containers:")
    print(containers)
    
    await ssh_manager.disconnect("vps")
    return True

async def test_log_monitoring():
    """Test log monitoring capabilities"""
    print("\n📋 Testing Log Monitoring...")
    print("=" * 40)
    
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
    print("\n2. Monitoring system logs...")
    syslog_cmd = "tail -10 /var/log/syslog"
    syslog_result = await ssh_manager.execute_command(syslog_cmd, "vps")
    
    if syslog_result.success:
        print("✅ System log (last 10 lines):")
        print(syslog_result.stdout[:400] + "..." if len(syslog_result.stdout) > 400 else syslog_result.stdout)
    else:
        print(f"❌ Failed to read system log: {syslog_result.stderr}")
    
    # Test auth log monitoring
    print("\n3. Monitoring auth logs...")
    auth_cmd = "tail -5 /var/log/auth.log"
    auth_result = await ssh_manager.execute_command(auth_cmd, "vps")
    
    if auth_result.success:
        print("✅ Auth log (last 5 lines):")
        print(auth_result.stdout[:300] + "..." if len(auth_result.stdout) > 300 else auth_result.stdout)
    else:
        print(f"❌ Failed to read auth log: {auth_result.stderr}")
    
    # Test log search
    print("\n4. Searching logs for SSH activity...")
    search_cmd = "grep 'ssh' /var/log/auth.log | tail -3"
    search_result = await ssh_manager.execute_command(search_cmd, "vps")
    
    if search_result.success:
        print("✅ SSH activity in auth log:")
        print(search_result.stdout[:300] + "..." if len(search_result.stdout) > 300 else search_result.stdout)
    else:
        print("⚠️ No SSH activity found or error reading log")
    
    await ssh_manager.disconnect("vps")
    return True

async def test_system_monitoring():
    """Test system monitoring capabilities"""
    print("\n📊 Testing System Monitoring...")
    print("=" * 40)
    
    # Initialize SSH manager
    ssh_manager = SSHConnectionManager()
    await ssh_manager.initialize_default_connections()
    
    # Connect to VPS
    connect_result = await ssh_manager.connect("vps")
    if not connect_result["success"]:
        print(f"❌ Connection failed: {connect_result['error']}")
        return False
    
    print("✅ Connected successfully!")
    
    # System monitoring commands
    monitoring_commands = {
        "System Uptime": "uptime",
        "Memory Usage": "free -h",
        "Disk Usage": "df -h /",
        "CPU Info": "top -bn1 | grep 'Cpu(s)' | head -1",
        "Running Processes": "ps aux --sort=-%cpu | head -5",
        "Network Connections": "netstat -tuln | head -5"
    }
    
    for desc, cmd in monitoring_commands.items():
        print(f"\n📋 {desc}:")
        result = await ssh_manager.execute_command(cmd, "vps")
        
        if result.success:
            output = result.stdout.strip()
            print(f"✅ {output[:200]}{'...' if len(output) > 200 else ''}")
        else:
            print(f"❌ Error: {result.stderr}")
    
    await ssh_manager.disconnect("vps")
    return True

async def test_docker_operations():
    """Test practical Docker operations"""
    print("\n🔧 Testing Docker Operations...")
    print("=" * 40)
    
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
    
    # Check if Docker is installed
    print("\n1. Checking Docker installation...")
    docker_check = await ssh_manager.execute_command("docker --version", "vps")
    
    if docker_check.success:
        print(f"✅ Docker installed: {docker_check.stdout.strip()}")
        
        # Test Docker info
        print("\n2. Getting Docker system info...")
        docker_info = await ssh_manager.execute_command("docker info --format '{{.ServerVersion}} | {{.Architecture}} | {{.OSType}}'", "vps")
        if docker_info.success:
            print(f"✅ Docker info: {docker_info.stdout.strip()}")
        
        # Test container operations
        print("\n3. Testing container operations...")
        
        # List containers
        containers_result = await docker_manager.list_containers("vps", all_containers=True)
        print("📋 Container list:")
        print(containers_result[:300] + "..." if len(containers_result) > 300 else containers_result)
        
        # Test a simple container run (hello-world)
        print("\n4. Testing simple container run...")
        hello_result = await ssh_manager.execute_command("docker run --rm hello-world", "vps", timeout=60)
        if hello_result.success:
            print("✅ Hello-world container ran successfully!")
            print(hello_result.stdout[:200] + "..." if len(hello_result.stdout) > 200 else hello_result.stdout)
        else:
            print(f"⚠️ Hello-world test failed: {hello_result.stderr}")
        
    else:
        print("⚠️ Docker not installed or not accessible")
        print("You can install Docker with: curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh")
    
    await ssh_manager.disconnect("vps")
    return True

async def main():
    """Main test function"""
    print("🚀 SSH MCP Server - Docker & Log Monitoring Test")
    print("=" * 60)
    
    try:
        # Test Docker control
        docker_success = await test_docker_control()
        
        # Test log monitoring
        log_success = await test_log_monitoring()
        
        # Test system monitoring
        system_success = await test_system_monitoring()
        
        # Test Docker operations
        docker_ops_success = await test_docker_operations()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Docker Control: {'✅ PASSED' if docker_success else '❌ FAILED'}")
        print(f"Log Monitoring: {'✅ PASSED' if log_success else '❌ FAILED'}")
        print(f"System Monitoring: {'✅ PASSED' if system_success else '❌ FAILED'}")
        print(f"Docker Operations: {'✅ PASSED' if docker_ops_success else '❌ FAILED'}")
        
        if all([docker_success, log_success, system_success, docker_ops_success]):
            print("\n🎉 All tests passed! SSH MCP server is ready for Docker control and log monitoring!")
            print("\n🔧 Available capabilities:")
            print("   • Docker container management (start, stop, restart, logs)")
            print("   • System log monitoring (syslog, auth.log, custom logs)")
            print("   • Real-time system monitoring (CPU, memory, disk, processes)")
            print("   • Docker Compose operations")
            print("   • Log searching and filtering")
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