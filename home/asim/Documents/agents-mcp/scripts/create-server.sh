#!/bin/bash

# Script to create a new MCP server template using uv

if [ -z "$1" ]; then
    echo "Usage: $0 <server-name>"
    echo "Example: $0 my-custom-server"
    exit 1
fi

SERVER_NAME="$1"
SERVER_DIR="/home/asim/Documents/agents-mcp/servers/$SERVER_NAME"

echo "Creating MCP server: $SERVER_NAME"
mkdir -p "$SERVER_DIR"
cd "$SERVER_DIR"

# Initialize uv project
uv init --name "$SERVER_NAME" --package

# Add MCP dependency
uv add mcp

# Create main.py with MCP server template
cat > "src/$SERVER_NAME/main.py" << EOF
#!/usr/bin/env python3
"""
$SERVER_NAME MCP Server
"""

import asyncio
from typing import Any, Dict, List
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Initialize the MCP server
server = Server("$SERVER_NAME")

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
                text=f"Hello, {name_arg}! This is from {server.name} MCP server."
            )
        ]
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="$SERVER_NAME",
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

# Create README
cat > "README.md" << EOF
# $SERVER_NAME MCP Server

## Description

Custom MCP server for [describe your server's purpose here].

## Development

This project uses \`uv\` for dependency management.

### Setup
\`\`\`bash
# Install dependencies
uv sync

# Run the server
uv run python src/$SERVER_NAME/main.py
\`\`\`

### Testing
\`\`\`bash
# Test the server locally
uv run python src/$SERVER_NAME/main.py
\`\`\`

## Configuration

Add to your MCP configuration:

\`\`\`json
{
  "mcpServers": {
    "$SERVER_NAME": {
      "command": "uv",
      "args": ["run", "python", "$SERVER_DIR/src/$SERVER_NAME/main.py"],
      "cwd": "$SERVER_DIR",
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
echo "📝 Edit $SERVER_DIR/src/$SERVER_NAME/main.py to customize your server"
echo "🔧 Run 'cd $SERVER_DIR && uv sync' to install dependencies"
echo "🚀 Test with 'cd $SERVER_DIR && uv run python src/$SERVER_NAME/main.py'"