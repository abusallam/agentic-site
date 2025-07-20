#!/usr/bin/env python3
"""
Mem0 MCP Server - AI Memory management
"""

import asyncio
import os
from typing import Any, Dict, List
from mcp.server import Server
import mcp.server.stdio
import mcp.types as types
from mem0 import Memory

# Initialize the MCP server
server = Server("mem0-tools")

def get_memory_client():
    """Get Mem0 memory client."""
    config = {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "collection_name": "mcp_memories",
                "host": os.getenv("QDRANT_HOST", "localhost"),
                "port": int(os.getenv("QDRANT_PORT", "6333")),
            }
        }
    }
    
    # Use OpenAI if API key is available
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        config["llm"] = {
            "provider": "openai",
            "config": {
                "model": "gpt-4o-mini",
                "temperature": 0.2,
                "max_tokens": 1500,
            }
        }
    
    return Memory.from_config(config)

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="add_memory",
            description="Add a new memory for a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text content to remember"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User ID to associate the memory with"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Additional metadata for the memory"
                    }
                },
                "required": ["text", "user_id"]
            }
        ),
        types.Tool(
            name="search_memories",
            description="Search through memories for a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User ID to search memories for"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 10
                    }
                },
                "required": ["query", "user_id"]
            }
        ),
        types.Tool(
            name="get_all_memories",
            description="Get all memories for a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID to get memories for"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of memories to return",
                        "default": 50
                    }
                },
                "required": ["user_id"]
            }
        ),
        types.Tool(
            name="update_memory",
            description="Update an existing memory",
            inputSchema={
                "type": "object",
                "properties": {
                    "memory_id": {
                        "type": "string",
                        "description": "Memory ID to update"
                    },
                    "text": {
                        "type": "string",
                        "description": "New text content"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User ID"
                    }
                },
                "required": ["memory_id", "text", "user_id"]
            }
        ),
        types.Tool(
            name="delete_memory",
            description="Delete a specific memory",
            inputSchema={
                "type": "object",
                "properties": {
                    "memory_id": {
                        "type": "string",
                        "description": "Memory ID to delete"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User ID"
                    }
                },
                "required": ["memory_id", "user_id"]
            }
        ),
        types.Tool(
            name="delete_all_memories",
            description="Delete all memories for a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID to delete all memories for"
                    }
                },
                "required": ["user_id"]
            }
        ),
        types.Tool(
            name="get_memory_history",
            description="Get the history of interactions for a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID to get history for"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of history items",
                        "default": 20
                    }
                },
                "required": ["user_id"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """Handle tool calls."""
    
    try:
        memory = get_memory_client()
        
        if name == "add_memory":
            text = arguments.get("text")
            user_id = arguments.get("user_id")
            metadata = arguments.get("metadata", {})
            
            result = memory.add(text, user_id=user_id, metadata=metadata)
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Memory added successfully. Memory ID: {result.get('id', 'Unknown')}"
                )
            ]
        
        elif name == "search_memories":
            query = arguments.get("query")
            user_id = arguments.get("user_id")
            limit = arguments.get("limit", 10)
            
            results = memory.search(query, user_id=user_id, limit=limit)
            
            if not results:
                return [
                    types.TextContent(
                        type="text",
                        text=f"No memories found for query: '{query}'"
                    )
                ]
            
            memory_list = []
            for i, result in enumerate(results, 1):
                memory_text = result.get('memory', 'No content')
                score = result.get('score', 0)
                memory_list.append(f"{i}. {memory_text} (Score: {score:.3f})")
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Search results for '{query}':\n\n" + "\n".join(memory_list)
                )
            ]
        
        elif name == "get_all_memories":
            user_id = arguments.get("user_id")
            limit = arguments.get("limit", 50)
            
            results = memory.get_all(user_id=user_id)
            
            if not results:
                return [
                    types.TextContent(
                        type="text",
                        text=f"No memories found for user: {user_id}"
                    )
                ]
            
            # Limit results
            results = results[:limit]
            
            memory_list = []
            for i, result in enumerate(results, 1):
                memory_text = result.get('memory', 'No content')
                memory_id = result.get('id', 'Unknown')
                created_at = result.get('created_at', 'Unknown')
                memory_list.append(f"{i}. [{memory_id}] {memory_text} (Created: {created_at})")
            
            return [
                types.TextContent(
                    type="text",
                    text=f"All memories for user {user_id}:\n\n" + "\n".join(memory_list)
                )
            ]
        
        elif name == "update_memory":
            memory_id = arguments.get("memory_id")
            text = arguments.get("text")
            user_id = arguments.get("user_id")
            
            result = memory.update(memory_id, data=text, user_id=user_id)
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Memory {memory_id} updated successfully"
                )
            ]
        
        elif name == "delete_memory":
            memory_id = arguments.get("memory_id")
            user_id = arguments.get("user_id")
            
            memory.delete(memory_id, user_id=user_id)
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Memory {memory_id} deleted successfully"
                )
            ]
        
        elif name == "delete_all_memories":
            user_id = arguments.get("user_id")
            
            memory.delete_all(user_id=user_id)
            
            return [
                types.TextContent(
                    type="text",
                    text=f"All memories for user {user_id} deleted successfully"
                )
            ]
        
        elif name == "get_memory_history":
            user_id = arguments.get("user_id")
            limit = arguments.get("limit", 20)
            
            # This would depend on Mem0's history API
            # For now, we'll return a placeholder
            return [
                types.TextContent(
                    type="text",
                    text=f"Memory history for user {user_id} (feature depends on Mem0 API updates)"
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