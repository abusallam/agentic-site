"""Enhanced MCP service for n8n workflow integration with comprehensive error handling."""

import os
import logging
import base64
from typing import Dict, List, Optional, Any
import httpx
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class EnhancedMCPService:
    """Enhanced service for MCP (Model Context Protocol) integration with n8n."""
    
    def __init__(self):
        """Initialize enhanced MCP service."""
        self.server_url = os.getenv("MCP_SERVER_URL", "http://localhost:3001")
        self.n8n_url = os.getenv("N8N_URL", "http://217.79.255.54:5680")
        self.n8n_api_user = os.getenv("N8N_API_USER", "admin")
        self.n8n_api_password = os.getenv("N8N_API_PASSWORD", "admin123")
        self.n8n_api_key = os.getenv("N8N_API_KEY")
        self.timeout = 30.0
        self.max_retries = 3
        self.retry_delay = 2.0
        
        # Create basic auth header
        if self.n8n_api_user and self.n8n_api_password:
            credentials = f"{self.n8n_api_user}:{self.n8n_api_password}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            self.auth_header = f"Basic {encoded_credentials}"
        else:
            self.auth_header = None
        
        logger.info(f"Enhanced MCP Service initialized with N8N URL: {self.n8n_url}")
    
    async def health_check(self) -> bool:
        """Check if MCP server is healthy."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.server_url}/health",
                    timeout=5.0
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"MCP health check failed: {e}")
            return False
    
    async def list_available_tools(self) -> Optional[List[Dict[str, Any]]]:
        """List available MCP tools."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.server_url}/tools",
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return response.json().get("tools", [])
                else:
                    logger.error(f"Failed to list tools: HTTP {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error listing MCP tools: {e}")
            return None
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call an MCP tool."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.server_url}/tools/{tool_name}",
                    json={"parameters": parameters},
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Tool call failed: HTTP {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            return None
    
    async def execute_n8n_workflow(self, workflow_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute n8n workflow via MCP or direct API."""
        try:
            # Try MCP first
            mcp_result = await self.call_tool("n8n_workflow_execute", {
                "workflow_id": workflow_id,
                "parameters": parameters
            })
            
            if mcp_result:
                return mcp_result
            
            # Fallback to direct n8n API
            return await self._execute_n8n_workflow_direct(workflow_id, parameters)
            
        except Exception as e:
            logger.error(f"Error executing workflow {workflow_id}: {e}")
            raise
    
    async def _execute_n8n_workflow_direct(self, workflow_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute n8n workflow directly via API."""
        if not self.n8n_url:
            raise ValueError("n8n URL not configured")
        
        try:
            headers = {"Content-Type": "application/json"}
            if self.n8n_api_key:
                headers["Authorization"] = f"Bearer {self.n8n_api_key}"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.n8n_url}/api/v1/workflows/{workflow_id}/execute",
                    json={"parameters": parameters},
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise Exception(f"n8n API error: HTTP {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Direct n8n workflow execution failed: {e}")
            raise
    
    async def get_workflow_status(self, execution_id: str) -> Dict[str, Any]:
        """Get workflow execution status."""
        try:
            # Try MCP first
            mcp_result = await self.call_tool("n8n_workflow_status", {
                "execution_id": execution_id
            })
            
            if mcp_result:
                return mcp_result
            
            # Fallback to direct n8n API
            return await self._get_workflow_status_direct(execution_id)
            
        except Exception as e:
            logger.error(f"Error getting workflow status {execution_id}: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _get_workflow_status_direct(self, execution_id: str) -> Dict[str, Any]:
        """Get workflow status directly from n8n API."""
        if not self.n8n_url:
            return {"status": "unknown", "error": "n8n URL not configured"}
        
        try:
            headers = {}
            if self.n8n_api_key:
                headers["Authorization"] = f"Bearer {self.n8n_api_key}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.n8n_url}/api/v1/executions/{execution_id}",
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "status": data.get("finished", False) and "completed" or "running",
                        "data": data
                    }
                else:
                    return {"status": "error", "error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Direct workflow status check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def list_n8n_workflows(self) -> List[Dict[str, Any]]:
        """List available n8n workflows."""
        try:
            # Try MCP first
            mcp_result = await self.call_tool("n8n_workflow_list", {})
            
            if mcp_result and "workflows" in mcp_result:
                return mcp_result["workflows"]
            
            # Fallback to direct n8n API
            return await self._list_n8n_workflows_direct()
            
        except Exception as e:
            logger.error(f"Error listing n8n workflows: {e}")
            return []
    
    async def _list_n8n_workflows_direct(self) -> List[Dict[str, Any]]:
        """List n8n workflows directly from API."""
        if not self.n8n_url:
            return []
        
        try:
            headers = {}
            if self.n8n_api_key:
                headers["Authorization"] = f"Bearer {self.n8n_api_key}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.n8n_url}/api/v1/workflows",
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return response.json().get("data", [])
                else:
                    logger.error(f"Failed to list workflows: HTTP {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Direct workflow listing failed: {e}")
            return []
    
    def validate_workflow_data(self, data: Dict[str, Any]) -> bool:
        """Validate workflow data structure."""
        required_fields = ["customer_id", "workflow_type"]
        return all(field in data for field in required_fields)