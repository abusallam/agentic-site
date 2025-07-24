#!/usr/bin/env python3
"""
Credential Loader Utility
Loads stored credentials for MCP servers and system operations
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def load_credentials():
    """Load credentials from the .credentials file"""
    credentials_file = Path(__file__).parent / ".credentials"
    
    if credentials_file.exists():
        load_dotenv(credentials_file)
        return {
            "vps_host": os.getenv("VPS_HOST"),
            "vps_user": os.getenv("VPS_USER"), 
            "vps_password": os.getenv("VPS_PASSWORD"),
            "vps_port": int(os.getenv("VPS_PORT", "22")),
            "local_sudo_password": os.getenv("LOCAL_SUDO_PASSWORD")
        }
    else:
        raise FileNotFoundError("Credentials file not found. Please create .credentials file.")

def get_vps_credentials():
    """Get VPS SSH credentials"""
    creds = load_credentials()
    return {
        "host": creds["vps_host"],
        "user": creds["vps_user"],
        "password": creds["vps_password"],
        "port": creds["vps_port"]
    }

def get_sudo_password():
    """Get local sudo password"""
    creds = load_credentials()
    return creds["local_sudo_password"]

def test_credentials():
    """Test that credentials are loaded correctly"""
    try:
        creds = load_credentials()
        print("✅ Credentials loaded successfully:")
        print(f"   VPS Host: {creds['vps_host']}")
        print(f"   VPS User: {creds['vps_user']}")
        print(f"   VPS Port: {creds['vps_port']}")
        print(f"   VPS Password: {'*' * len(creds['vps_password']) if creds['vps_password'] else 'Not set'}")
        print(f"   Local Sudo: {'*' * len(creds['local_sudo_password']) if creds['local_sudo_password'] else 'Not set'}")
        return True
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return False

if __name__ == "__main__":
    test_credentials()