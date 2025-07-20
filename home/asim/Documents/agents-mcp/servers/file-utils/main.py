#!/usr/bin/env python3
"""
File Utilities MCP Server
Provides tools for file operations and text processing
"""

import asyncio
import os
import json
from typing import Any, Dict, List
from pathlib import Path

# Simple MCP server implementation
class MCPServer:
    def __init__(self, name: str):
        self.name = name
        self.tools = []
    
    def add_tool(self, name: str, description: str, schema: Dict[str, Any], handler):
        self.tools.append({
            "name": name,
            "description": description,
            "inputSchema": schema,
            "handler": handler
        })
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        method = request.get("method")
        
        if method == "tools/list":
            return {
                "tools": [
                    {
                        "name": tool["name"],
                        "description": tool["description"],
                        "inputSchema": tool["inputSchema"]
                    }
                    for tool in self.tools
                ]
            }
        
        elif method == "tools/call":
            tool_name = request["params"]["name"]
            arguments = request["params"]["arguments"]
            
            for tool in self.tools:
                if tool["name"] == tool_name:
                    result = await tool["handler"](arguments)
                    return {"content": [{"type": "text", "text": result}]}
            
            return {"error": f"Unknown tool: {tool_name}"}
        
        return {"error": f"Unknown method: {method}"}

# Initialize server
server = MCPServer("file-utils")

async def read_file_tool(args: Dict[str, Any]) -> str:
    """Read contents of a file"""
    try:
        file_path = args["path"]
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"File contents of {file_path}:\n\n{content}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

async def write_file_tool(args: Dict[str, Any]) -> str:
    """Write content to a file"""
    try:
        file_path = args["path"]
        content = args["content"]
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote content to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

async def list_files_tool(args: Dict[str, Any]) -> str:
    """List files in a directory"""
    try:
        directory = args.get("directory", ".")
        pattern = args.get("pattern", "*")
        
        path = Path(directory)
        if not path.exists():
            return f"Directory {directory} does not exist"
        
        files = list(path.glob(pattern))
        file_list = "\n".join([f"{'📁' if f.is_dir() else '📄'} {f.name}" for f in files])
        
        return f"Files in {directory}:\n\n{file_list}"
    except Exception as e:
        return f"Error listing files: {str(e)}"

# Register tools
server.add_tool(
    "read_file",
    "Read the contents of a text file",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path to the file to read"}
        },
        "required": ["path"]
    },
    read_file_tool
)

server.add_tool(
    "write_file", 
    "Write content to a text file",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path to the file to write"},
            "content": {"type": "string", "description": "Content to write to the file"}
        },
        "required": ["path", "content"]
    },
    write_file_tool
)

server.add_tool(
    "list_files",
    "List files in a directory",
    {
        "type": "object", 
        "properties": {
            "directory": {"type": "string", "description": "Directory to list (default: current)"},
            "pattern": {"type": "string", "description": "File pattern to match (default: *)"}
        }
    },
    list_files_tool
)

async def main():
    """Simple stdio-based MCP server"""
    import sys
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
                
            request = json.loads(line.strip())
            response = await server.handle_request(request)
            
            print(json.dumps(response))
            sys.stdout.flush()
            
        except Exception as e:
            error_response = {"error": str(e)}
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())