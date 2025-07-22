#!/usr/bin/env python3
"""
SSH Control MCP Server
Main entry point for the SSH-based MCP server with Docker integration
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ssh_control.core.mcp_server import SSHMCPServer
from ssh_control.utils.logger import Logger

async def main():
    """Main entry point"""
    try:
        Logger.info("Starting Enhanced SSH Control MCP Server with Docker integration...")
        server = SSHMCPServer()
        await server.run()
    except KeyboardInterrupt:
        Logger.info("Server stopped by user")
    except Exception as error:
        Logger.error(f"SSH MCP Server Error: {error}")
        import traceback
        Logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())