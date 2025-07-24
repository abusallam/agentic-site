#!/usr/bin/env python3
"""
Test SSH Connection Script
Quick test to verify SSH connection works with password authentication
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ssh_control.services.ssh_connection_manager import SSHConnectionManager
from ssh_control.utils.logger import Logger

async def test_ssh_connection():
    """Test SSH connection to VPS"""
    print("🔧 Testing SSH Connection to VPS...")
    print("=" * 50)
    
    # Initialize SSH manager
    ssh_manager = SSHConnectionManager()
    await ssh_manager.initialize_default_connections()
    
    # Test connection
    print("1. Testing SSH connection...")
    connect_result = await ssh_manager.connect("vps")
    
    if connect_result["success"]:
        print(f"✅ Connection successful!")
        print(f"   Host: {connect_result['host']}")
        print(f"   Username: {connect_result['username']}")
        print(f"   Port: {connect_result['port']}")
        print(f"   Auth Type: {connect_result['auth_type']}")
        print(f"   Test Result: {connect_result['test_result']}")
        
        # Test basic commands
        print("\n2. Testing basic commands...")
        
        test_commands = [
            "whoami",
            "pwd",
            "uname -a",
            "date",
            "df -h /"
        ]
        
        for cmd in test_commands:
            print(f"\n   Executing: {cmd}")
            result = await ssh_manager.execute_command(cmd, "vps", timeout=10)
            
            if result.success:
                print(f"   ✅ Success (exit: {result.exit_code}, time: {result.execution_time:.2f}s)")
                print(f"   Output: {result.stdout.strip()}")
            else:
                print(f"   ❌ Failed (exit: {result.exit_code})")
                print(f"   Error: {result.stderr.strip()}")
        
        # Test system info
        print("\n3. Testing system information...")
        system_info = await ssh_manager.get_system_info("vps")
        print("   System Info:")
        print(f"   {system_info}")
        
        # Test connection status
        print("\n4. Testing connection status...")
        statuses = await ssh_manager.get_connection_status()
        for status in statuses:
            print(f"   Connection: {status.name}")
            print(f"   Host: {status.host}:{status.port}")
            print(f"   Username: {status.username}")
            print(f"   Connected: {status.connected}")
            print(f"   Last Activity: {status.last_activity}")
        
        # Disconnect
        print("\n5. Testing disconnection...")
        disconnect_result = await ssh_manager.disconnect("vps")
        if disconnect_result["success"]:
            print("   ✅ Disconnected successfully")
        else:
            print(f"   ❌ Disconnect failed: {disconnect_result['error']}")
        
        print("\n🎉 All tests completed successfully!")
        
    else:
        print(f"❌ Connection failed!")
        print(f"   Error: {connect_result['error']}")
        print(f"   Message: {connect_result['message']}")
        
        # Debug information
        print("\n🔍 Debug Information:")
        print(f"   Available configs: {list(ssh_manager.configs.keys())}")
        
        if "vps" in ssh_manager.configs:
            config = ssh_manager.configs["vps"]
            print(f"   VPS Config:")
            print(f"     Host: {config.host}")
            print(f"     Port: {config.port}")
            print(f"     Username: {config.username}")
            print(f"     Auth Type: {config.auth_type}")
            print(f"     Has Password: {'Yes' if config.password else 'No'}")
        
        return False
    
    return True

async def main():
    """Main test function"""
    try:
        success = await test_ssh_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as error:
        print(f"\n💥 Test failed with error: {error}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())