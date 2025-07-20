"""
n8n MCP Agent - Dedicated agent for managing n8n MCP server integration.
"""

import json
import logging
import os
import subprocess
import asyncio
from typing import Dict, Any, Optional, List
from google.adk.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

# Auth token for MCP server communication
MCP_AUTH_TOKEN = "adk-agent-secure-token-12345678901234567890"


class N8nMCPAgent(BaseAgent):
    """ADK Agent dedicated to managing n8n MCP server integration."""
    
    def __init__(self):
        """Initialize the n8n MCP agent."""
        super().__init__(
            name="n8n_mcp_agent",
            description="Dedicated agent for managing n8n MCP server integration and workflow automation"
        )
        
        # MCP server configuration using object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, 'mcp_server_path', os.path.join(os.path.dirname(__file__), "../../n8n-mcp"))
        object.__setattr__(self, 'mcp_process', None)
        object.__setattr__(self, 'mcp_port', int(os.getenv("N8N_MCP_PORT", "8001")))
        object.__setattr__(self, 'n8n_url', os.getenv("N8N_BASE_URL") or os.getenv("N8N_URL", "http://localhost:5678"))
        object.__setattr__(self, 'n8n_api_key', os.getenv("N8N_API_KEY"))
        
        # Initialize MCP server
        object.__setattr__(self, '_mcp_initialized', False)
        
        logger.info("N8nMCPAgent initialized")
    
    async def initialize_mcp_server(self) -> Dict[str, Any]:
        """Initialize and start the n8n MCP server."""
        try:
            if self._mcp_initialized:
                return {"status": "success", "message": "MCP server already initialized"}
            
            logger.info("Initializing n8n MCP server...")
            
            # Check if n8n-mcp directory exists
            if not os.path.exists(self.mcp_server_path):
                return {
                    "status": "error",
                    "error": "n8n-mcp directory not found. Please ensure it's cloned in the project root."
                }
            
            # Install dependencies if needed
            package_json_path = os.path.join(self.mcp_server_path, "package.json")
            node_modules_path = os.path.join(self.mcp_server_path, "node_modules")
            
            if not os.path.exists(node_modules_path):
                logger.info("Installing n8n MCP dependencies...")
                result = subprocess.run(
                    ["npm", "install"],
                    cwd=self.mcp_server_path,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    return {
                        "status": "error",
                        "error": f"Failed to install dependencies: {result.stderr}"
                    }
            
            # Build the project
            dist_path = os.path.join(self.mcp_server_path, "dist")
            if not os.path.exists(dist_path):
                logger.info("Building n8n MCP server...")
                result = subprocess.run(
                    ["npm", "run", "build"],
                    cwd=self.mcp_server_path,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    return {
                        "status": "error",
                        "error": f"Failed to build MCP server: {result.stderr}"
                    }
            
            # Initialize database
            logger.info("Initializing MCP database...")
            result = subprocess.run(
                ["npm", "run", "rebuild"],
                cwd=self.mcp_server_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.warning(f"Database rebuild warning: {result.stderr}")
            
            object.__setattr__(self, '_mcp_initialized', True)
            
            return {
                "status": "success",
                "message": "n8n MCP server initialized successfully",
                "server_path": self.mcp_server_path,
                "port": self.mcp_port
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP server: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def start_mcp_server(self) -> Dict[str, Any]:
        """Start the n8n MCP server in HTTP mode."""
        try:
            if self.mcp_process and self.mcp_process.poll() is None:
                return {
                    "status": "success",
                    "message": "MCP server already running",
                    "port": self.mcp_port
                }
            
            # Ensure server is initialized
            init_result = await self.initialize_mcp_server()
            if init_result["status"] != "success":
                return init_result
            
            logger.info(f"Starting n8n MCP server on port {self.mcp_port}...")
            
            # Set environment variables for the MCP server
            env = os.environ.copy()
            env.update({
                "MCP_MODE": "http",
                "PORT": str(self.mcp_port),
                "N8N_API_URL": self.n8n_url,
                "N8N_API_KEY": self.n8n_api_key or "",
                "LOG_LEVEL": "info",
                "AUTH_TOKEN": MCP_AUTH_TOKEN,  # 32+ character auth token
                "DISABLE_CONSOLE_OUTPUT": "false"
            })
            
            # Start the MCP server
            mcp_process = subprocess.Popen(
                ["npm", "run", "start:http"],
                cwd=self.mcp_server_path,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Store the process using object.__setattr__
            object.__setattr__(self, 'mcp_process', mcp_process)
            
            # Wait a moment for the server to start
            await asyncio.sleep(2)
            
            # Check if the process is still running
            if self.mcp_process.poll() is not None:
                stdout, stderr = self.mcp_process.communicate()
                return {
                    "status": "error",
                    "error": f"MCP server failed to start: {stderr}",
                    "stdout": stdout
                }
            
            return {
                "status": "success",
                "message": f"n8n MCP server started on port {self.mcp_port}",
                "port": self.mcp_port,
                "url": f"http://localhost:{self.mcp_port}",
                "pid": self.mcp_process.pid
            }
            
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def stop_mcp_server(self) -> Dict[str, Any]:
        """Stop the n8n MCP server."""
        try:
            if not self.mcp_process or self.mcp_process.poll() is not None:
                return {
                    "status": "success",
                    "message": "MCP server not running"
                }
            
            logger.info("Stopping n8n MCP server...")
            
            # Terminate the process
            self.mcp_process.terminate()
            
            # Wait for graceful shutdown
            try:
                self.mcp_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't stop gracefully
                self.mcp_process.kill()
                self.mcp_process.wait()
            
            object.__setattr__(self, 'mcp_process', None)
            
            return {
                "status": "success",
                "message": "n8n MCP server stopped"
            }
            
        except Exception as e:
            logger.error(f"Failed to stop MCP server: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_mcp_server_status(self) -> Dict[str, Any]:
        """Get the current status of the n8n MCP server."""
        try:
            is_running = self.mcp_process and self.mcp_process.poll() is None
            
            status = {
                "status": "success",
                "server_running": is_running,
                "initialized": self._mcp_initialized,
                "port": self.mcp_port,
                "url": f"http://localhost:{self.mcp_port}",
                "n8n_url": self.n8n_url,
                "n8n_api_configured": bool(self.n8n_api_key)
            }
            
            if is_running:
                status["pid"] = self.mcp_process.pid
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get MCP server status: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def create_workflow_via_mcp(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a workflow using the n8n MCP server."""
        try:
            import httpx
            
            # Ensure MCP server is running
            status = await self.get_mcp_server_status()
            if not status.get("server_running"):
                start_result = await self.start_mcp_server()
                if start_result["status"] != "success":
                    return start_result
            
            # Make request to MCP server using JSON-RPC format
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://localhost:{self.mcp_port}/mcp",
                    headers={
                        "Authorization": "Bearer adk-agent-secure-token-12345678901234567890",
                        "Content-Type": "application/json"
                    },
                    json={
                        "jsonrpc": "2.0",
                        "method": "n8n_create_workflow",
                        "params": {
                            "workflow": workflow_config
                        },
                        "id": 1
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Workflow created via MCP: {result}")
                    return {
                        "status": "success",
                        "workflow": result,
                        "created_via": "n8n_mcp_server"
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"MCP server error: {response.status_code}",
                        "response": response.text
                    }
            
        except Exception as e:
            logger.error(f"Failed to create workflow via MCP: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def list_workflows_via_mcp(self) -> Dict[str, Any]:
        """List workflows using the n8n MCP server."""
        try:
            import httpx
            
            # Ensure MCP server is running
            status = await self.get_mcp_server_status()
            if not status.get("server_running"):
                start_result = await self.start_mcp_server()
                if start_result["status"] != "success":
                    return start_result
            
            # Make request to MCP server using JSON-RPC format
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://localhost:{self.mcp_port}/mcp",
                    headers={
                        "Authorization": "Bearer adk-agent-secure-token-12345678901234567890",
                        "Content-Type": "application/json"
                    },
                    json={
                        "jsonrpc": "2.0",
                        "method": "n8n_list_workflows",
                        "params": {},
                        "id": 2
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "status": "success",
                        "workflows": result,
                        "retrieved_via": "n8n_mcp_server"
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"MCP server error: {response.status_code}",
                        "response": response.text
                    }
            
        except Exception as e:
            logger.error(f"Failed to list workflows via MCP: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_node_info_via_mcp(self, node_type: str) -> Dict[str, Any]:
        """Get node information using the n8n MCP server."""
        try:
            import httpx
            
            # Ensure MCP server is running
            status = await self.get_mcp_server_status()
            if not status.get("server_running"):
                start_result = await self.start_mcp_server()
                if start_result["status"] != "success":
                    return start_result
            
            # Make request to MCP server using JSON-RPC format
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://localhost:{self.mcp_port}/mcp",
                    headers={
                        "Authorization": "Bearer adk-agent-secure-token-12345678901234567890",
                        "Content-Type": "application/json"
                    },
                    json={
                        "jsonrpc": "2.0",
                        "method": "get_node_essentials",
                        "params": {
                            "nodeType": node_type
                        },
                        "id": 3
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "status": "success",
                        "node_info": result,
                        "retrieved_via": "n8n_mcp_server"
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"MCP server error: {response.status_code}",
                        "response": response.text
                    }
            
        except Exception as e:
            logger.error(f"Failed to get node info via MCP: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def validate_workflow_via_mcp(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a workflow using the n8n MCP server."""
        try:
            import httpx
            
            # Ensure MCP server is running
            status = await self.get_mcp_server_status()
            if not status.get("server_running"):
                start_result = await self.start_mcp_server()
                if start_result["status"] != "success":
                    return start_result
            
            # Make request to MCP server using JSON-RPC format
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://localhost:{self.mcp_port}/mcp",
                    headers={
                        "Authorization": "Bearer adk-agent-secure-token-12345678901234567890",
                        "Content-Type": "application/json"
                    },
                    json={
                        "jsonrpc": "2.0",
                        "method": "validate_workflow",
                        "params": {
                            "workflow": workflow
                        },
                        "id": 4
                    },
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "status": "success",
                        "validation": result,
                        "validated_via": "n8n_mcp_server"
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"MCP server error: {response.status_code}",
                        "response": response.text
                    }
            
        except Exception as e:
            logger.error(f"Failed to validate workflow via MCP: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def run(self, user_input: str) -> str:
        """Main entry point for n8n MCP agent execution."""
        try:
            logger.info(f"Processing n8n MCP request: {user_input[:100]}...")
            
            # Try to parse as JSON command first
            try:
                command = json.loads(user_input)
                if isinstance(command, dict) and "action" in command:
                    return await self._handle_command(command)
            except json.JSONDecodeError:
                pass
            
            # Handle as natural language input
            return await self._handle_natural_language(user_input)
            
        except Exception as e:
            logger.error(f"Error in n8n MCP agent run: {e}")
            return f"I encountered an error: {str(e)}. Please try again or contact support."
    
    async def _handle_command(self, command: Dict[str, Any]) -> str:
        """Handle structured JSON commands."""
        action = command.get("action")
        params = command.get("params", {})
        
        if action == "initialize":
            result = await self.initialize_mcp_server()
        elif action == "start":
            result = await self.start_mcp_server()
        elif action == "stop":
            result = await self.stop_mcp_server()
        elif action == "status":
            result = await self.get_mcp_server_status()
        elif action == "create_workflow":
            result = await self.create_workflow_via_mcp(params.get("workflow", {}))
        elif action == "list_workflows":
            result = await self.list_workflows_via_mcp()
        elif action == "get_node_info":
            result = await self.get_node_info_via_mcp(params.get("node_type", ""))
        elif action == "validate_workflow":
            result = await self.validate_workflow_via_mcp(params.get("workflow", {}))
        else:
            return f"Unknown action: {action}"
        
        return json.dumps(result, indent=2)
    
    async def _handle_natural_language(self, user_input: str) -> str:
        """Handle natural language input."""
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ["hello", "hi", "help"]):
            return """Hello! I'm your n8n MCP Agent. I can help you with:

• Starting and managing the n8n MCP server
• Creating and validating workflows via MCP
• Getting node information and documentation
• Managing workflow automation

Available commands:
- "start server" - Start the n8n MCP server
- "stop server" - Stop the n8n MCP server  
- "server status" - Check server status
- "list workflows" - List all workflows
- "get node info [node-type]" - Get node information

What would you like to do?"""
        
        elif any(word in input_lower for word in ["start", "initialize"]):
            result = await self.start_mcp_server()
            if result["status"] == "success":
                return f"""✅ n8n MCP Server Started Successfully!

Server URL: {result['url']}
Process ID: {result.get('pid', 'N/A')}

The server is now ready to handle workflow automation requests. You can:
- Create workflows via MCP API
- Validate workflow configurations
- Get node documentation and examples
- Manage n8n workflows programmatically"""
            else:
                return f"❌ Failed to start n8n MCP server: {result['error']}"
        
        elif any(word in input_lower for word in ["stop", "shutdown"]):
            result = await self.stop_mcp_server()
            if result["status"] == "success":
                return "✅ n8n MCP server stopped successfully."
            else:
                return f"❌ Failed to stop n8n MCP server: {result['error']}"
        
        elif any(word in input_lower for word in ["status", "health"]):
            result = await self.get_mcp_server_status()
            if result["status"] == "success":
                status_text = f"""📊 n8n MCP Server Status:

• Server Running: {'✅ Yes' if result['server_running'] else '❌ No'}
• Initialized: {'✅ Yes' if result['initialized'] else '❌ No'}
• Port: {result['port']}
• URL: {result['url']}
• n8n URL: {result['n8n_url']}
• n8n API Configured: {'✅ Yes' if result['n8n_api_configured'] else '❌ No'}"""
                
                if result.get('pid'):
                    status_text += f"\n• Process ID: {result['pid']}"
                
                return status_text
            else:
                return f"❌ Failed to get server status: {result['error']}"
        
        elif "list workflows" in input_lower:
            result = await self.list_workflows_via_mcp()
            if result["status"] == "success":
                workflows = result.get("workflows", [])
                if workflows:
                    workflow_list = "\n".join([f"• {w.get('name', 'Unnamed')} (ID: {w.get('id', 'N/A')})" for w in workflows])
                    return f"📋 Available Workflows:\n\n{workflow_list}"
                else:
                    return "📋 No workflows found."
            else:
                return f"❌ Failed to list workflows: {result['error']}"
        
        else:
            return """I can help you manage the n8n MCP server and workflows. Try:

• "start server" - Start the MCP server
• "server status" - Check current status  
• "list workflows" - Show available workflows
• "help" - Show available commands

What would you like to do?"""