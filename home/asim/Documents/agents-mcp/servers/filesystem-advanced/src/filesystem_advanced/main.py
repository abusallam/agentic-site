#!/usr/bin/env python3
"""
Advanced Filesystem MCP Server - Enhanced file operations
"""

import asyncio
import os
import shutil
import stat
import hashlib
import mimetypes
from pathlib import Path
from typing import Any, Dict, List
from mcp.server import Server
import mcp.server.stdio
import mcp.types as types
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Initialize the MCP server
server = Server("filesystem-advanced")

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="search_files",
            description="Search for files by name pattern or content",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory to search in"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "File name pattern (glob style)"
                    },
                    "content": {
                        "type": "string",
                        "description": "Search for files containing this text"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Search recursively",
                        "default": True
                    }
                },
                "required": ["path"]
            }
        ),
        types.Tool(
            name="get_file_info",
            description="Get detailed information about a file or directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to file or directory"
                    }
                },
                "required": ["path"]
            }
        ),
        types.Tool(
            name="copy_file",
            description="Copy a file or directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source path"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination path"
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Overwrite if destination exists",
                        "default": False
                    }
                },
                "required": ["source", "destination"]
            }
        ),
        types.Tool(
            name="move_file",
            description="Move or rename a file or directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source path"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination path"
                    }
                },
                "required": ["source", "destination"]
            }
        ),
        types.Tool(
            name="delete_file",
            description="Delete a file or directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to delete"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Delete directories recursively",
                        "default": False
                    }
                },
                "required": ["path"]
            }
        ),
        types.Tool(
            name="create_directory",
            description="Create a directory (and parent directories if needed)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to create"
                    },
                    "parents": {
                        "type": "boolean",
                        "description": "Create parent directories if they don't exist",
                        "default": True
                    }
                },
                "required": ["path"]
            }
        ),
        types.Tool(
            name="get_file_hash",
            description="Calculate hash of a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path"
                    },
                    "algorithm": {
                        "type": "string",
                        "enum": ["md5", "sha1", "sha256", "sha512"],
                        "description": "Hash algorithm",
                        "default": "sha256"
                    }
                },
                "required": ["path"]
            }
        ),
        types.Tool(
            name="set_permissions",
            description="Set file or directory permissions",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to file or directory"
                    },
                    "mode": {
                        "type": "string",
                        "description": "Permission mode (e.g., '755', '644')"
                    }
                },
                "required": ["path", "mode"]
            }
        ),
        types.Tool(
            name="compress_directory",
            description="Create a compressed archive of a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_dir": {
                        "type": "string",
                        "description": "Directory to compress"
                    },
                    "output_file": {
                        "type": "string",
                        "description": "Output archive file path"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["zip", "tar", "gztar", "bztar", "xztar"],
                        "description": "Archive format",
                        "default": "zip"
                    }
                },
                "required": ["source_dir", "output_file"]
            }
        ),
        types.Tool(
            name="extract_archive",
            description="Extract a compressed archive",
            inputSchema={
                "type": "object",
                "properties": {
                    "archive_path": {
                        "type": "string",
                        "description": "Path to archive file"
                    },
                    "extract_to": {
                        "type": "string",
                        "description": "Directory to extract to"
                    }
                },
                "required": ["archive_path", "extract_to"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """Handle tool calls."""
    
    try:
        if name == "search_files":
            path = arguments.get("path")
            pattern = arguments.get("pattern")
            content = arguments.get("content")
            recursive = arguments.get("recursive", True)
            
            results = []
            search_path = Path(path)
            
            if pattern:
                if recursive:
                    matches = search_path.rglob(pattern)
                else:
                    matches = search_path.glob(pattern)
                
                for match in matches:
                    results.append(str(match))
            
            if content:
                if recursive:
                    files = search_path.rglob("*")
                else:
                    files = search_path.glob("*")
                
                for file_path in files:
                    if file_path.is_file():
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                if content.lower() in f.read().lower():
                                    results.append(str(file_path))
                        except:
                            continue
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Search results:\n\n" + "\n".join(results) if results else "No files found"
                )
            ]
        
        elif name == "get_file_info":
            path = arguments.get("path")
            file_path = Path(path)
            
            if not file_path.exists():
                return [
                    types.TextContent(
                        type="text",
                        text=f"Path does not exist: {path}"
                    )
                ]
            
            stat_info = file_path.stat()
            
            info = f"""Path: {path}
Type: {'Directory' if file_path.is_dir() else 'File'}
Size: {stat_info.st_size} bytes
Permissions: {oct(stat_info.st_mode)[-3:]}
Owner: {stat_info.st_uid}
Group: {stat_info.st_gid}
Created: {stat_info.st_ctime}
Modified: {stat_info.st_mtime}
Accessed: {stat_info.st_atime}"""
            
            if file_path.is_file():
                mime_type, _ = mimetypes.guess_type(str(file_path))
                info += f"\nMIME Type: {mime_type or 'Unknown'}"
            
            return [
                types.TextContent(
                    type="text",
                    text=info
                )
            ]
        
        elif name == "copy_file":
            source = arguments.get("source")
            destination = arguments.get("destination")
            overwrite = arguments.get("overwrite", False)
            
            source_path = Path(source)
            dest_path = Path(destination)
            
            if not source_path.exists():
                return [
                    types.TextContent(
                        type="text",
                        text=f"Source does not exist: {source}"
                    )
                ]
            
            if dest_path.exists() and not overwrite:
                return [
                    types.TextContent(
                        type="text",
                        text=f"Destination exists and overwrite is False: {destination}"
                    )
                ]
            
            if source_path.is_dir():
                shutil.copytree(source, destination, dirs_exist_ok=overwrite)
            else:
                shutil.copy2(source, destination)
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Successfully copied {source} to {destination}"
                )
            ]
        
        elif name == "move_file":
            source = arguments.get("source")
            destination = arguments.get("destination")
            
            shutil.move(source, destination)
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Successfully moved {source} to {destination}"
                )
            ]
        
        elif name == "delete_file":
            path = arguments.get("path")
            recursive = arguments.get("recursive", False)
            
            file_path = Path(path)
            
            if not file_path.exists():
                return [
                    types.TextContent(
                        type="text",
                        text=f"Path does not exist: {path}"
                    )
                ]
            
            if file_path.is_dir():
                if recursive:
                    shutil.rmtree(path)
                else:
                    file_path.rmdir()
            else:
                file_path.unlink()
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Successfully deleted {path}"
                )
            ]
        
        elif name == "create_directory":
            path = arguments.get("path")
            parents = arguments.get("parents", True)
            
            dir_path = Path(path)
            dir_path.mkdir(parents=parents, exist_ok=True)
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Successfully created directory {path}"
                )
            ]
        
        elif name == "get_file_hash":
            path = arguments.get("path")
            algorithm = arguments.get("algorithm", "sha256")
            
            file_path = Path(path)
            
            if not file_path.is_file():
                return [
                    types.TextContent(
                        type="text",
                        text=f"File does not exist: {path}"
                    )
                ]
            
            hash_func = getattr(hashlib, algorithm)()
            
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            
            return [
                types.TextContent(
                    type="text",
                    text=f"{algorithm.upper()} hash of {path}: {hash_func.hexdigest()}"
                )
            ]
        
        elif name == "set_permissions":
            path = arguments.get("path")
            mode = arguments.get("mode")
            
            file_path = Path(path)
            
            if not file_path.exists():
                return [
                    types.TextContent(
                        type="text",
                        text=f"Path does not exist: {path}"
                    )
                ]
            
            # Convert string mode to octal
            octal_mode = int(mode, 8)
            file_path.chmod(octal_mode)
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Successfully set permissions {mode} on {path}"
                )
            ]
        
        elif name == "compress_directory":
            source_dir = arguments.get("source_dir")
            output_file = arguments.get("output_file")
            format_type = arguments.get("format", "zip")
            
            # Remove extension from output_file as make_archive adds it
            base_name = output_file.rsplit('.', 1)[0] if '.' in output_file else output_file
            
            shutil.make_archive(base_name, format_type, source_dir)
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Successfully created {format_type} archive: {base_name}.{format_type}"
                )
            ]
        
        elif name == "extract_archive":
            archive_path = arguments.get("archive_path")
            extract_to = arguments.get("extract_to")
            
            shutil.unpack_archive(archive_path, extract_to)
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Successfully extracted {archive_path} to {extract_to}"
                )
            ]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )
        ]

async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    asyncio.run(main())