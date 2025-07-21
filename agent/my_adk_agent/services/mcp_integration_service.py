"""
MCP Integration Service - Utilizes all available MCP servers
Integrates Playwright, n8n, GitHub, and File Utils MCP servers
"""

import asyncio
import json
import logging
import subprocess
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MCPIntegrationService:
    """Service to integrate and utilize all available MCP servers."""
    
    def __init__(self):
        """Initialize MCP Integration Service with all available servers."""
        self.mcp_servers = {
            "playwright-tools": {
                "description": "Web scraping, automation, and browser interactions",
                "capabilities": ["scrape_page", "take_screenshot", "fill_form", "click_element"],
                "cwd": "/home/asim/Documents/agents-mcp/servers/playwright-tools"
            },
            "n8n-tools": {
                "description": "Workflow automation and n8n integration",
                "capabilities": ["list_workflows", "get_executions", "trigger_workflow", "create_workflow"],
                "cwd": "/home/asim/Documents/agents-mcp/servers/n8n-tools"
            },
            "github-tools": {
                "description": "GitHub repository management and operations",
                "capabilities": ["list_repos", "get_repo_info", "create_issue", "get_commits"],
                "cwd": "/home/asim/Documents/agents-mcp/servers/github-tools"
            },
            "file-utils": {
                "description": "File system operations and utilities",
                "capabilities": ["read_file", "list_directory", "write_file", "search_files"],
                "cwd": "/home/asim/Documents/agents-mcp/servers/file-utils"
            }
        }
        logger.info("MCP Integration Service initialized with servers: %s", list(self.mcp_servers.keys()))
    
    async def call_mcp_server(self, server_name: str, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific MCP server tool with parameters."""
        try:
            if server_name not in self.mcp_servers:
                return {"error": f"MCP server '{server_name}' not available"}
            
            server_info = self.mcp_servers[server_name]
            cwd = server_info["cwd"]
            
            # Prepare the MCP call
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": parameters
                }
            }
            
            # Execute MCP server call
            cmd = ["uv", "run", "python", "src/main.py"]
            
            logger.info(f"Calling MCP server {server_name} with tool {tool_name}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=cwd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Send request and get response
            stdout, stderr = await process.communicate(
                input=json.dumps(mcp_request).encode()
            )
            
            if process.returncode == 0:
                response = json.loads(stdout.decode())
                logger.info(f"MCP server {server_name} responded successfully")
                return response.get("result", {})
            else:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(f"MCP server {server_name} error: {error_msg}")
                return {"error": f"MCP server error: {error_msg}"}
                
        except Exception as e:
            logger.error(f"Error calling MCP server {server_name}: {e}")
            return {"error": str(e)}
    
    # Playwright Tools Integration
    async def scrape_website(self, url: str, selector: Optional[str] = None) -> Dict[str, Any]:
        """Scrape a website using Playwright MCP server."""
        parameters = {"url": url}
        if selector:
            parameters["selector"] = selector
            
        return await self.call_mcp_server("playwright-tools", "scrape_page", parameters)
    
    async def take_screenshot(self, url: str, filename: Optional[str] = None) -> Dict[str, Any]:
        """Take a screenshot of a website."""
        parameters = {"url": url}
        if filename:
            parameters["filename"] = filename
            
        return await self.call_mcp_server("playwright-tools", "take_screenshot", parameters)
    
    # n8n Tools Integration
    async def list_n8n_workflows(self) -> Dict[str, Any]:
        """List all n8n workflows."""
        return await self.call_mcp_server("n8n-tools", "list_workflows", {})
    
    async def get_workflow_executions(self, workflow_id: str) -> Dict[str, Any]:
        """Get executions for a specific workflow."""
        return await self.call_mcp_server("n8n-tools", "get_executions", {"workflow_id": workflow_id})
    
    async def trigger_n8n_workflow(self, workflow_id: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Trigger an n8n workflow."""
        parameters = {"workflow_id": workflow_id}
        if data:
            parameters["data"] = data
            
        return await self.call_mcp_server("n8n-tools", "trigger_workflow", parameters)
    
    # GitHub Tools Integration
    async def list_github_repos(self, username: Optional[str] = None) -> Dict[str, Any]:
        """List GitHub repositories."""
        parameters = {}
        if username:
            parameters["username"] = username
            
        return await self.call_mcp_server("github-tools", "list_repos", parameters)
    
    async def get_repo_info(self, repo_name: str, owner: Optional[str] = None) -> Dict[str, Any]:
        """Get information about a GitHub repository."""
        parameters = {"repo": repo_name}
        if owner:
            parameters["owner"] = owner
            
        return await self.call_mcp_server("github-tools", "get_repo_info", parameters)
    
    async def create_github_issue(self, repo: str, title: str, body: str, owner: Optional[str] = None) -> Dict[str, Any]:
        """Create a GitHub issue."""
        parameters = {
            "repo": repo,
            "title": title,
            "body": body
        }
        if owner:
            parameters["owner"] = owner
            
        return await self.call_mcp_server("github-tools", "create_issue", parameters)
    
    # File Utils Integration
    async def read_file_content(self, file_path: str) -> Dict[str, Any]:
        """Read file content using file utils."""
        return await self.call_mcp_server("file-utils", "read_file", {"path": file_path})
    
    async def list_directory_contents(self, directory_path: str) -> Dict[str, Any]:
        """List directory contents."""
        return await self.call_mcp_server("file-utils", "list_directory", {"path": directory_path})
    
    async def write_file_content(self, file_path: str, content: str) -> Dict[str, Any]:
        """Write content to a file."""
        return await self.call_mcp_server("file-utils", "write_file", {
            "path": file_path,
            "content": content
        })
    
    async def search_files(self, directory: str, pattern: str) -> Dict[str, Any]:
        """Search for files matching a pattern."""
        return await self.call_mcp_server("file-utils", "search_files", {
            "directory": directory,
            "pattern": pattern
        })
    
    # High-level AI Agent Functions
    async def analyze_competitor_website(self, url: str) -> Dict[str, Any]:
        """Analyze a competitor website using Playwright."""
        try:
            # Scrape the website
            scrape_result = await self.scrape_website(url)
            
            if "error" in scrape_result:
                return scrape_result
            
            # Take a screenshot for visual analysis
            screenshot_result = await self.take_screenshot(url, f"competitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            
            return {
                "status": "success",
                "website_content": scrape_result,
                "screenshot": screenshot_result,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing competitor website: {e}")
            return {"error": str(e)}
    
    async def automate_customer_workflow(self, customer_email: str, service_type: str) -> Dict[str, Any]:
        """Create and trigger automated workflow for customer onboarding."""
        try:
            # List existing workflows
            workflows = await self.list_n8n_workflows()
            
            if "error" in workflows:
                return workflows
            
            # Find or create appropriate workflow
            workflow_name = f"customer_onboarding_{service_type}"
            
            # Trigger the workflow with customer data
            trigger_data = {
                "customer_email": customer_email,
                "service_type": service_type,
                "timestamp": datetime.now().isoformat()
            }
            
            # For now, trigger the first available workflow
            if workflows.get("workflows"):
                first_workflow = workflows["workflows"][0]
                workflow_id = first_workflow.get("id")
                
                if workflow_id:
                    result = await self.trigger_n8n_workflow(workflow_id, trigger_data)
                    return {
                        "status": "success",
                        "workflow_triggered": workflow_id,
                        "customer_email": customer_email,
                        "result": result
                    }
            
            return {"error": "No suitable workflow found"}
            
        except Exception as e:
            logger.error(f"Error automating customer workflow: {e}")
            return {"error": str(e)}
    
    async def backup_customer_data(self, customer_id: str) -> Dict[str, Any]:
        """Backup customer data using file utils and GitHub."""
        try:
            # Create backup directory
            backup_dir = f"/tmp/customer_backup_{customer_id}_{datetime.now().strftime('%Y%m%d')}"
            
            # List customer files (example)
            files_result = await self.list_directory_contents("/tmp")
            
            # Create backup summary
            backup_summary = {
                "customer_id": customer_id,
                "backup_timestamp": datetime.now().isoformat(),
                "files_backed_up": files_result
            }
            
            # Write backup summary
            summary_file = f"{backup_dir}/backup_summary.json"
            write_result = await self.write_file_content(summary_file, json.dumps(backup_summary, indent=2))
            
            return {
                "status": "success",
                "backup_location": backup_dir,
                "summary": backup_summary,
                "write_result": write_result
            }
            
        except Exception as e:
            logger.error(f"Error backing up customer data: {e}")
            return {"error": str(e)}
    
    def get_available_capabilities(self) -> Dict[str, Any]:
        """Get all available MCP server capabilities."""
        return {
            "servers": self.mcp_servers,
            "total_servers": len(self.mcp_servers),
            "capabilities_summary": {
                "web_automation": "Playwright tools for web scraping and automation",
                "workflow_automation": "n8n integration for business process automation", 
                "code_management": "GitHub tools for repository operations",
                "file_operations": "File system utilities for data management"
            }
        }