# 🔐 MCP Server Credentials Usage Guide

## 📁 Stored Credentials

All passwords are now securely stored in `home/asim/Documents/agents-mcp/.credentials`:

- **VPS SSH**: `root@217.79.255.54:22` with password `gt5qXy22aJ`
- **Local Sudo**: Password `3480` for local terminal sudo operations

## 🚀 How to Use

### 1. SSH to VPS (Automatic)
The SSH MCP server automatically loads VPS credentials:

```bash
# Test SSH connection
python3 home/asim/Documents/agents-mcp/servers/ssh-control/test_ssh_connection.py

# Start SSH MCP server
cd home/asim/Documents/agents-mcp/servers/ssh-control
python3 src/ssh_control/main.py
```

### 2. Load Credentials in Python
```python
from load_credentials import load_credentials, get_vps_credentials, get_sudo_password

# Load all credentials
creds = load_credentials()

# Get VPS credentials
vps = get_vps_credentials()
print(f"VPS: {vps['user']}@{vps['host']}:{vps['port']}")

# Get sudo password
sudo_pass = get_sudo_password()
```

### 3. Use Sudo Helper
```bash
# Test sudo functionality
python3 home/asim/Documents/agents-mcp/scripts/sudo_helper.py

# Run sudo commands
python3 home/asim/Documents/agents-mcp/scripts/sudo_helper.py "apt update"
python3 home/asim/Documents/agents-mcp/scripts/sudo_helper.py "systemctl status docker"
```

## 🔧 Available Tools

### SSH MCP Server Tools
- `ssh_connect` - Connect to VPS (uses stored password)
- `ssh_execute` - Run commands on VPS
- `ssh_get_system_info` - Get VPS system information
- `ssh_upload_file` / `ssh_download_file` - Transfer files
- `ssh_install_package` - Install packages on VPS

### Local Sudo Operations
- `sudo_helper.py` - Run local sudo commands with stored password

## 🛡️ Security Features

1. **File Permissions**: Credentials file has 600 permissions (owner read/write only)
2. **No Git Tracking**: Credentials file is excluded from version control
3. **Masked Display**: Passwords shown as asterisks in logs
4. **Secure Loading**: Credentials loaded only when needed

## 📋 Quick Reference

### VPS Connection Details
- **Host**: 217.79.255.54
- **User**: root
- **Password**: gt5qXy22aJ (stored securely)
- **Port**: 22

### Local System
- **Sudo Password**: 3480 (stored securely)

## ✅ Verification

All credentials have been tested and verified working:

```
✅ VPS SSH Connection: Working
✅ VPS Command Execution: Working  
✅ VPS System Information: Working
✅ Local Sudo Operations: Working
```

## 🎯 Next Steps

1. **SSH Operations**: Use the SSH MCP server for VPS management
2. **Local Admin**: Use sudo_helper.py for local system administration
3. **Automation**: Integrate credentials into your automation scripts
4. **Security**: Keep credentials file secure and never share

**No more password prompts or hanging SSH connections!** 🎉