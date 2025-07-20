#!/bin/bash

# Script to create a new MCP server template

if [ -z "$1" ]; then
    echo "Usage: $0 <server-name>"
    echo "Example: $0 my-custom-server"
    exit 1
fi

SERVER_NAME="$1"
SERVER_DIR="~/Documents/agents-mcp/servers/$SERVER_NAME"

echo "Creating MCP server: $SERVER_NAME"

# Create server directory
mkdir -p "$SERVER_DIR"

# Create basic Python MCP server template
cat > "$SERVER_DIR/main.py" << 'EOF'
#!/usr/bin/env python3
"""
Basic MCP Server Template
"""

import asyncio
import json
from typing import Any, Dict, List
from mcp import ClientSession, StdioServerParameters
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Initialize the MCP server
server = Server("SERVER_NAME_PLACEHOLDER")

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="example_tool",
            description="An example tool that returns a greeting",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name to greet"
                    }
                },
                "required": ["name"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """Handle tool calls."""
    if name == "example_tool":
        name_arg = arguments.get("name", "World")
        return [
            types.TextContent(
                type="text",
                text=f"Hello, {name_arg}! This is from your custom MCP server."
            )
        ]
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="SERVER_NAME_PLACEHOLDER",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
EOF

# Replace placeholder with actual server name
sed -i "s/SERVER_NAME_PLACEHOLDER/$SERVER_NAME/g" "$SERVER_DIR/main.py"

# Create requirements.txt
cat > "$SERVER_DIR/requirements.txt" << 'EOF'
mcp>=0.1.0
EOF

# Create README
cat > "$SERVER_DIR/README.md" << EOF
# $SERVER_NAME MCP Server

## Description

Custom MCP server for [describe your server's purpose here].

## Installation

1. Install dependencies:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

2. Test the server:
   \`\`\`bash
   python main.py
   \`\`\`

## Configuration

Add to your MCP configuration:

\`\`\`json
{
  "mcpServers": {
    "$SERVER_NAME": {
      "command": "python",
      "args": ["$SERVER_DIR/main.py"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
\`\`\`

## Available Tools

- \`example_tool\`: Returns a greeting message

## Usage

[Add usage examples here]
EOF

echo "✅ Created MCP server template at: $SERVER_DIR"
echo "📝 Edit $SERVER_DIR/main.py to customize your server"
echo "📖 See $SERVER_DIR/README.md for setup instructions"