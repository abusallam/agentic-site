#!/usr/bin/env python3
"""
GitHub MCP Server - Provides GitHub API integration
"""

import asyncio
import os
from typing import Any, Dict, List
from mcp.server import Server
import mcp.server.stdio
import mcp.types as types
from github import Github
import requests

# Initialize the MCP server
server = Server("github-tools")

def get_github_client():
    """Get GitHub client with token from environment."""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is required")
    return Github(token)

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="list_repos",
            description="List repositories for a user or organization",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "GitHub username or organization name"
                    },
                    "type": {
                        "type": "string",
                        "enum": ["all", "owner", "public", "private"],
                        "description": "Type of repositories to list",
                        "default": "all"
                    }
                },
                "required": ["username"]
            }
        ),
        types.Tool(
            name="get_repo_info",
            description="Get detailed information about a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    }
                },
                "required": ["owner", "repo"]
            }
        ),
        types.Tool(
            name="create_issue",
            description="Create a new issue in a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "title": {
                        "type": "string",
                        "description": "Issue title"
                    },
                    "body": {
                        "type": "string",
                        "description": "Issue body/description"
                    },
                    "labels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Labels to add to the issue"
                    }
                },
                "required": ["owner", "repo", "title"]
            }
        ),
        types.Tool(
            name="list_issues",
            description="List issues in a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "state": {
                        "type": "string",
                        "enum": ["open", "closed", "all"],
                        "description": "Issue state",
                        "default": "open"
                    }
                },
                "required": ["owner", "repo"]
            }
        ),
        types.Tool(
            name="get_file_content",
            description="Get the content of a file from a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "path": {
                        "type": "string",
                        "description": "File path in the repository"
                    },
                    "branch": {
                        "type": "string",
                        "description": "Branch name (default: main)",
                        "default": "main"
                    }
                },
                "required": ["owner", "repo", "path"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """Handle tool calls."""
    
    try:
        g = get_github_client()
        
        if name == "list_repos":
            username = arguments.get("username")
            repo_type = arguments.get("type", "all")
            
            user = g.get_user(username)
            repos = user.get_repos(type=repo_type)
            
            repo_list = []
            for repo in repos[:20]:  # Limit to first 20
                repo_list.append(f"📁 {repo.name} - {repo.description or 'No description'}")
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Repositories for {username}:\n\n" + "\n".join(repo_list)
                )
            ]
        
        elif name == "get_repo_info":
            owner = arguments.get("owner")
            repo_name = arguments.get("repo")
            
            repo = g.get_repo(f"{owner}/{repo_name}")
            
            info = f"""Repository: {repo.full_name}
Description: {repo.description or 'No description'}
Language: {repo.language or 'Not specified'}
Stars: {repo.stargazers_count}
Forks: {repo.forks_count}
Issues: {repo.open_issues_count}
Created: {repo.created_at}
Updated: {repo.updated_at}
Clone URL: {repo.clone_url}
Homepage: {repo.homepage or 'None'}
License: {repo.license.name if repo.license else 'None'}"""
            
            return [
                types.TextContent(
                    type="text",
                    text=info
                )
            ]
        
        elif name == "create_issue":
            owner = arguments.get("owner")
            repo_name = arguments.get("repo")
            title = arguments.get("title")
            body = arguments.get("body", "")
            labels = arguments.get("labels", [])
            
            repo = g.get_repo(f"{owner}/{repo_name}")
            issue = repo.create_issue(title=title, body=body, labels=labels)
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Created issue #{issue.number}: {issue.title}\nURL: {issue.html_url}"
                )
            ]
        
        elif name == "list_issues":
            owner = arguments.get("owner")
            repo_name = arguments.get("repo")
            state = arguments.get("state", "open")
            
            repo = g.get_repo(f"{owner}/{repo_name}")
            issues = repo.get_issues(state=state)
            
            issue_list = []
            for issue in issues[:10]:  # Limit to first 10
                issue_list.append(f"#{issue.number} - {issue.title} ({issue.state})")
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Issues in {owner}/{repo_name} ({state}):\n\n" + "\n".join(issue_list)
                )
            ]
        
        elif name == "get_file_content":
            owner = arguments.get("owner")
            repo_name = arguments.get("repo")
            file_path = arguments.get("path")
            branch = arguments.get("branch", "main")
            
            repo = g.get_repo(f"{owner}/{repo_name}")
            file_content = repo.get_contents(file_path, ref=branch)
            
            if file_content.type == "file":
                content = file_content.decoded_content.decode('utf-8')
                return [
                    types.TextContent(
                        type="text",
                        text=f"File: {file_path} (branch: {branch})\n\n{content}"
                    )
                ]
            else:
                return [
                    types.TextContent(
                        type="text",
                        text=f"Path {file_path} is not a file"
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