#!/usr/bin/env python3
"""
Sudo Helper Script
Executes sudo commands using stored local password
"""

import subprocess
import sys
import os
from pathlib import Path

# Add parent directory to path to import credentials
sys.path.insert(0, str(Path(__file__).parent.parent))
from load_credentials import get_sudo_password

def run_sudo_command(command, input_text=None):
    """
    Run a sudo command using stored password
    
    Args:
        command: Command to run with sudo (string or list)
        input_text: Optional input to send to the command
    
    Returns:
        dict: Result with success, stdout, stderr, exit_code
    """
    try:
        sudo_password = get_sudo_password()
        
        if isinstance(command, str):
            full_command = f"sudo -S {command}"
        else:
            full_command = ["sudo", "-S"] + command
        
        # Prepare input (password + any additional input)
        sudo_input = sudo_password + "\n"
        if input_text:
            sudo_input += input_text
        
        # Execute command
        process = subprocess.Popen(
            full_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=isinstance(command, str)
        )
        
        stdout, stderr = process.communicate(input=sudo_input)
        
        return {
            "success": process.returncode == 0,
            "exit_code": process.returncode,
            "stdout": stdout,
            "stderr": stderr
        }
        
    except Exception as e:
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e)
        }

def test_sudo():
    """Test sudo functionality"""
    print("🔧 Testing sudo with stored password...")
    
    # Test basic sudo command
    result = run_sudo_command("whoami")
    
    if result["success"]:
        print(f"✅ Sudo test successful!")
        print(f"   Command: sudo whoami")
        print(f"   Output: {result['stdout'].strip()}")
    else:
        print(f"❌ Sudo test failed!")
        print(f"   Error: {result['stderr']}")
    
    return result["success"]

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run command provided as arguments
        command = " ".join(sys.argv[1:])
        result = run_sudo_command(command)
        
        print(result["stdout"], end="")
        if result["stderr"]:
            print(result["stderr"], file=sys.stderr, end="")
        
        sys.exit(result["exit_code"])
    else:
        # Run test
        test_sudo()