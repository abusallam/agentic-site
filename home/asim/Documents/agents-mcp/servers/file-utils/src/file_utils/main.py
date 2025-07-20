#!/usr/bin/env python3
"""
file-utils MCP Server - Provides file system utilities
"""

import asyncio
import os
from typing import Any, Dict, List
from mcp.server import Server
import mcp.server.stdio
import mcp.types as types

# Initialize the MCP server
server = Server("file-utils")

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="read_file",
            description="Read the contents of a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    }
                },
                "required": ["path"]
            }
        ),
        types.Tool(
            name="write_file",
            description="Write content to a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["path", "content"]
            }
        ),
        types.Tool(
            name="list_directory",
            description="List contents of a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the directory to list"
                    }
                },
                "required": ["path"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """Handle tool calls."""
    
    if name == "read_file":
        path = arguments.get("path")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return [
                types.TextContent(
                    type="text",
                    text=f"Contents of {path}:\n\n{content}"
                )
            ]
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error reading file {path}: {str(e)}"
                )
            ]
    
    elif name == "write_file":
        path = arguments.get("path")
        content = arguments.get("content")
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return [
                types.TextContent(
                    type="text",
                    text=f"Successfully wrote to {path}"
                )
            ]
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error writing to file {path}: {str(e)}"
                )
            ]
    
    elif name == "list_directory":
        path = arguments.get("path")
        try:
            items = os.listdir(path)
            items_info = []
            for item in sorted(items):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    items_info.append(f"📁 {item}/")
                else:
                    size = os.path.getsize(item_path)
                    items_info.append(f"📄 {item} ({size} bytes)")
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Contents of {path}:\n\n" + "\n".join(items_info)
                )
            ]
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error listing directory {path}: {str(e)}"
                )
            ]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    asyncio.run(main())