"""
Server configuration for SSH Control MCP Server
"""

# Server configuration
SERVER_CONFIG = {
    "name": "ssh-control",
    "version": "2.0.0",
    "description": "Enhanced SSH Control MCP Server with Docker Integration"
}

# Default SSH configurations
DEFAULT_SSH_CONFIGS = {
    "localhost": {
        "name": "localhost",
        "host": "127.0.0.1",
        "port": 22,
        "username": "user",
        "auth_type": "key",
        "timeout": 30
    }
}