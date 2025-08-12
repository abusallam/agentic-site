"""
Composio Service - OAuth provider integration for handling authentication
Handles OAuth flows for various services (Google, Facebook, GitHub, etc.)
"""

import asyncio
import json
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ComposioService:
    """
    Service for handling OAuth authentication via Composio
    Provides unified OAuth for multiple providers
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get("COMPOSIO_API_KEY")
        self.base_url = "https://backend.composio.dev/api/v1"
        
        if not self.api_key:
            logger.warning("Composio API key not provided - OAuth features will be limited")
        
        # HTTP client for API calls
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "X-API-Key": self.api_key,
                "Content-Type": "application/json"
            } if self.api_key else {"Content-Type": "application/json"}
        )
    
    async def get_available_apps(self) -> Dict[str, Any]:
        """
        Get list of available OAuth applications
        
        Returns:
            List of supported OAuth providers
        """
        try:
            if not self.api_key:
                return {
                    "success": False,
                    "error": "Composio API key not configured",
                    "mock_apps": [
                        {"name": "Google", "id": "google", "status": "available"},
                        {"name": "GitHub", "id": "github", "status": "available"},
                        {"name": "Slack", "id": "slack", "status": "available"},
                        {"name": "Notion", "id": "notion", "status": "available"},
                        {"name": "Gmail", "id": "gmail", "status": "available"}
                    ]
                }
            
            response = await self.client.get(f"{self.base_url}/apps")
            
            if response.status_code == 200:
                apps_data = response.json()
                
                logger.info(f"Retrieved {len(apps_data.get('apps', []))} available apps")
                
                return {
                    "success": True,
                    "apps": apps_data.get("apps", []),
                    "total_count": len(apps_data.get("apps", []))
                }
            else:
                logger.error(f"Failed to get apps: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error getting available apps: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def initiate_oauth_flow(self, app_name: str, customer_id: str, redirect_url: str = None) -> Dict[str, Any]:
        """
        Initiate OAuth flow for a specific application
        
        Args:
            app_name: Name of the OAuth provider (google, github, etc.)
            customer_id: Customer identifier
            redirect_url: URL to redirect after OAuth completion
            
        Returns:
            OAuth initiation result with authorization URL
        """
        try:
            if not self.api_key:
                return {
                    "success": False,
                    "error": "Composio API key not configured",
                    "mock_auth_url": f"https://mock-oauth.composio.dev/auth/{app_name}?customer={customer_id}"
                }
            
            # Prepare OAuth initiation payload
            oauth_payload = {
                "appName": app_name,
                "entityId": customer_id,
                "redirectUrl": redirect_url or f"https://consulting.sa/oauth/callback/{app_name}"
            }
            
            response = await self.client.post(
                f"{self.base_url}/connectedAccounts",
                json=oauth_payload
            )
            
            if response.status_code in [200, 201]:
                oauth_result = response.json()
                
                logger.info(f"OAuth flow initiated for {app_name} - customer {customer_id}")
                
                return {
                    "success": True,
                    "auth_url": oauth_result.get("redirectUrl"),
                    "connection_id": oauth_result.get("connectionId"),
                    "app_name": app_name,
                    "customer_id": customer_id,
                    "expires_in": oauth_result.get("expiresIn", 3600)
                }
            else:
                logger.error(f"Failed to initiate OAuth: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"OAuth initiation failed: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error initiating OAuth flow: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_connection_status(self, customer_id: str, app_name: str = None) -> Dict[str, Any]:
        """
        Get OAuth connection status for a customer
        
        Args:
            customer_id: Customer identifier
            app_name: Optional specific app to check
            
        Returns:
            Connection status information
        """
        try:
            if not self.api_key:
                return {
                    "success": False,
                    "error": "Composio API key not configured",
                    "mock_connections": [
                        {
                            "app_name": "google",
                            "status": "connected",
                            "connected_at": datetime.now().isoformat(),
                            "scopes": ["email", "profile"]
                        }
                    ]
                }
            
            # Get connections for customer
            params = {"entityId": customer_id}
            if app_name:
                params["appName"] = app_name
            
            response = await self.client.get(
                f"{self.base_url}/connectedAccounts",
                params=params
            )
            
            if response.status_code == 200:
                connections_data = response.json()
                
                connections = []
                for conn in connections_data.get("connectedAccounts", []):
                    connections.append({
                        "app_name": conn.get("appName"),
                        "status": conn.get("status", "unknown"),
                        "connected_at": conn.get("createdAt"),
                        "connection_id": conn.get("id"),
                        "scopes": conn.get("scopes", [])
                    })
                
                logger.info(f"Retrieved {len(connections)} connections for customer {customer_id}")
                
                return {
                    "success": True,
                    "connections": connections,
                    "total_connections": len(connections)
                }
            else:
                logger.error(f"Failed to get connections: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Failed to get connections: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error getting connection status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_action(self, customer_id: str, app_name: str, action: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute an action using OAuth-connected service
        
        Args:
            customer_id: Customer identifier
            app_name: OAuth provider name
            action: Action to execute (e.g., "send_email", "create_file")
            parameters: Action parameters
            
        Returns:
            Action execution result
        """
        try:
            if not self.api_key:
                return {
                    "success": False,
                    "error": "Composio API key not configured",
                    "mock_result": {
                        "action": action,
                        "app": app_name,
                        "status": "simulated",
                        "message": f"Mock execution of {action} on {app_name}"
                    }
                }
            
            # Prepare action execution payload
            action_payload = {
                "entityId": customer_id,
                "appName": app_name,
                "actionName": action,
                "input": parameters or {}
            }
            
            response = await self.client.post(
                f"{self.base_url}/actions/execute",
                json=action_payload
            )
            
            if response.status_code == 200:
                action_result = response.json()
                
                logger.info(f"Action {action} executed successfully for {app_name}")
                
                return {
                    "success": True,
                    "result": action_result.get("data"),
                    "execution_id": action_result.get("executionId"),
                    "status": action_result.get("status"),
                    "executed_at": datetime.now().isoformat()
                }
            else:
                logger.error(f"Failed to execute action: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Action execution failed: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error executing action: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def revoke_connection(self, customer_id: str, app_name: str) -> Dict[str, Any]:
        """
        Revoke OAuth connection for a customer
        
        Args:
            customer_id: Customer identifier
            app_name: OAuth provider name
            
        Returns:
            Revocation result
        """
        try:
            if not self.api_key:
                return {
                    "success": False,
                    "error": "Composio API key not configured"
                }
            
            # Find connection ID first
            connections = await self.get_connection_status(customer_id, app_name)
            if not connections.get("success"):
                return connections
            
            connection_id = None
            for conn in connections.get("connections", []):
                if conn.get("app_name") == app_name:
                    connection_id = conn.get("connection_id")
                    break
            
            if not connection_id:
                return {
                    "success": False,
                    "error": f"No connection found for {app_name}"
                }
            
            response = await self.client.delete(
                f"{self.base_url}/connectedAccounts/{connection_id}"
            )
            
            if response.status_code in [200, 204]:
                logger.info(f"Connection revoked for {app_name} - customer {customer_id}")
                
                return {
                    "success": True,
                    "message": f"Connection to {app_name} revoked successfully",
                    "revoked_at": datetime.now().isoformat()
                }
            else:
                logger.error(f"Failed to revoke connection: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Failed to revoke connection: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error revoking connection: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()