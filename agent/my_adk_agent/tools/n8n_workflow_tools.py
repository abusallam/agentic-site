"""
N8N Workflow Tools - Comprehensive tools for n8n workflow management
Integrates with n8n Server, n8n MCP, Composio OAuth, and OpenRouter LLM
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from ..services.mcp_service import MCPService
from ..services.composio_service import ComposioService
from ..services.openrouter_service import OpenRouterService

logger = logging.getLogger(__name__)

class N8nWorkflowTools:
    """
    Comprehensive tools for n8n workflow automation
    Handles workflow creation, execution, monitoring, and OAuth integration
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.mcp_service = MCPService(config)
        self.composio_service = ComposioService(config)
        self.openrouter_service = OpenRouterService(config)
        
        # Workflow templates with detailed configurations
        self.workflow_templates = {
            "email_automation": {
                "name": "Email Automation Workflow",
                "description": "Automated email processing and responses",
                "setup_time": "15 minutes",
                "complexity": "beginner",
                "required_oauth": ["gmail", "google"],
                "required_config": ["email_host", "email_user", "from_email", "response_template"]
            },
            "data_processing": {
                "name": "Data Processing Pipeline",
                "description": "Fetch, transform, and store data automatically",
                "setup_time": "20 minutes", 
                "complexity": "intermediate",
                "required_oauth": ["database", "api_service"],
                "required_config": ["data_url", "transform_code", "db_host", "db_name", "db_user", "db_table"]
            },
            "system_integration": {
                "name": "System Integration Workflow",
                "description": "Connect multiple systems and sync data",
                "setup_time": "30 minutes",
                "complexity": "advanced",
                "required_oauth": ["slack", "notion", "github"],
                "required_config": ["source_system", "target_system", "sync_frequency", "mapping_rules"]
            },
            "notifications": {
                "name": "Automated Notifications",
                "description": "Smart notification system with conditions",
                "setup_time": "10 minutes",
                "complexity": "beginner",
                "required_oauth": ["slack", "teams"],
                "required_config": ["slack_channel", "notification_message", "condition_field", "condition_value"]
            },
            "sentiment_analysis": {
                "name": "Sentiment Analysis Pipeline",
                "description": "Analyze text sentiment using AI models",
                "setup_time": "25 minutes",
                "complexity": "intermediate",
                "required_oauth": ["openai", "database"],
                "required_config": ["text_source", "ai_model", "output_destination", "analysis_frequency"]
            }
        }
    
    async def get_workflow_templates(self, language: str = "en") -> Dict[str, Any]:
        """
        Get available workflow templates with descriptions
        
        Args:
            language: Response language (en/ar)
            
        Returns:
            List of available workflow templates
        """
        try:
            # Use OpenRouter to generate localized descriptions
            if language == "ar":
                system_prompt = """You are a technical translator. Translate the following workflow template information to Arabic while keeping technical terms in English where appropriate. Maintain the JSON structure."""
                
                templates_json = json.dumps(self.workflow_templates, indent=2)
                translation_result = await self.openrouter_service.generate_response(
                    prompt=f"Translate this workflow templates data to Arabic: {templates_json}",
                    system_prompt=system_prompt,
                    model="meta-llama/llama-3.1-8b-instruct:free",
                    max_tokens=1500,
                    temperature=0.3
                )
                
                if translation_result.get("success"):
                    try:
                        translated_templates = json.loads(translation_result["response"])
                        return {
                            "success": True,
                            "templates": translated_templates,
                            "total_count": len(translated_templates),
                            "language": language
                        }
                    except json.JSONDecodeError:
                        pass  # Fall back to English
            
            return {
                "success": True,
                "templates": self.workflow_templates,
                "total_count": len(self.workflow_templates),
                "language": language,
                "recommended": "email_automation"
            }
            
        except Exception as e:
            logger.error(f"Error getting workflow templates: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_workflow_from_template(self, 
                                          template_id: str,
                                          customer_id: str,
                                          workflow_name: str,
                                          custom_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a new workflow from template
        
        Args:
            template_id: Template identifier
            customer_id: Customer identifier
            workflow_name: Custom workflow name
            custom_config: Template-specific configuration
            
        Returns:
            Workflow creation result
        """
        try:
            if template_id not in self.workflow_templates:
                return {
                    "success": False,
                    "error": f"Template '{template_id}' not found",
                    "available_templates": list(self.workflow_templates.keys())
                }
            
            template = self.workflow_templates[template_id]
            
            # Check OAuth requirements
            oauth_status = await self._check_oauth_requirements(customer_id, template["required_oauth"])
            if not oauth_status.get("all_connected", False):
                return {
                    "success": False,
                    "error": "OAuth connections required",
                    "missing_oauth": oauth_status.get("missing_connections", []),
                    "oauth_urls": oauth_status.get("auth_urls", {})
                }
            
            # Prepare workflow data
            workflow_data = {
                "name": workflow_name,
                "template_id": template_id,
                "customer_id": customer_id,
                "custom_config": custom_config or {}
            }
            
            # Create workflow via MCP service
            creation_result = await self.mcp_service.create_workflow(workflow_data)
            
            if creation_result.get("success"):
                logger.info(f"Workflow created: {creation_result['workflow_id']} for customer {customer_id}")
                
                return {
                    "success": True,
                    "workflow_id": creation_result["workflow_id"],
                    "workflow_name": creation_result["name"],
                    "template_used": template_id,
                    "setup_time": template["setup_time"],
                    "complexity": template["complexity"],
                    "created_at": creation_result["created_at"],
                    "next_steps": [
                        "Test the workflow with sample data",
                        "Configure monitoring and alerts",
                        "Schedule regular execution if needed"
                    ]
                }
            else:
                return creation_result
                
        except Exception as e:
            logger.error(f"Error creating workflow from template: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_workflow(self, 
                             workflow_id: str,
                             customer_id: str,
                             input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute an existing workflow
        
        Args:
            workflow_id: Workflow identifier
            customer_id: Customer identifier
            input_data: Optional input data
            
        Returns:
            Execution result
        """
        try:
            # Verify customer has access to this workflow
            access_check = await self._verify_workflow_access(workflow_id, customer_id)
            if not access_check.get("has_access", False):
                return {
                    "success": False,
                    "error": "Access denied to workflow",
                    "workflow_id": workflow_id
                }
            
            # Execute workflow via MCP service
            execution_result = await self.mcp_service.execute_workflow(workflow_id, input_data)
            
            if execution_result.get("success"):
                logger.info(f"Workflow executed: {workflow_id} by customer {customer_id}")
                
                return {
                    "success": True,
                    "execution_id": execution_result["execution_id"],
                    "workflow_id": workflow_id,
                    "status": execution_result["status"],
                    "started_at": execution_result["started_at"],
                    "estimated_duration": execution_result["estimated_duration"],
                    "monitoring_url": f"https://consulting.sa/workflows/{workflow_id}/executions/{execution_result['execution_id']}"
                }
            else:
                return execution_result
                
        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_workflow_status(self, 
                                workflow_id: str,
                                customer_id: str) -> Dict[str, Any]:
        """
        Get workflow status and execution history
        
        Args:
            workflow_id: Workflow identifier
            customer_id: Customer identifier
            
        Returns:
            Workflow status information
        """
        try:
            # Verify customer has access to this workflow
            access_check = await self._verify_workflow_access(workflow_id, customer_id)
            if not access_check.get("has_access", False):
                return {
                    "success": False,
                    "error": "Access denied to workflow",
                    "workflow_id": workflow_id
                }
            
            # Get status via MCP service
            status_result = await self.mcp_service.get_workflow_status(workflow_id)
            
            if status_result.get("success"):
                # Enhance with AI-generated insights
                insights = await self._generate_workflow_insights(status_result)
                
                return {
                    "success": True,
                    "workflow": status_result["workflow"],
                    "recent_executions": status_result["recent_executions"],
                    "insights": insights,
                    "recommendations": await self._get_workflow_recommendations(workflow_id, status_result)
                }
            else:
                return status_result
                
        except Exception as e:
            logger.error(f"Error getting workflow status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def setup_oauth_for_workflow(self, 
                                     customer_id: str,
                                     app_name: str,
                                     redirect_url: str = None) -> Dict[str, Any]:
        """
        Setup OAuth connection for workflow integration
        
        Args:
            customer_id: Customer identifier
            app_name: OAuth provider name (google, slack, etc.)
            redirect_url: Optional redirect URL
            
        Returns:
            OAuth setup result with authorization URL
        """
        try:
            # Initiate OAuth flow via Composio
            oauth_result = await self.composio_service.initiate_oauth_flow(
                app_name=app_name,
                customer_id=customer_id,
                redirect_url=redirect_url
            )
            
            if oauth_result.get("success"):
                logger.info(f"OAuth flow initiated for {app_name} - customer {customer_id}")
                
                return {
                    "success": True,
                    "auth_url": oauth_result["auth_url"],
                    "app_name": app_name,
                    "connection_id": oauth_result.get("connection_id"),
                    "expires_in": oauth_result.get("expires_in", 3600),
                    "instructions": f"Please visit the authorization URL to connect your {app_name} account. This connection will be used for workflow automation."
                }
            else:
                return oauth_result
                
        except Exception as e:
            logger.error(f"Error setting up OAuth: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_customer_workflows(self, customer_id: str) -> Dict[str, Any]:
        """
        Get all workflows for a customer
        
        Args:
            customer_id: Customer identifier
            
        Returns:
            List of customer workflows
        """
        try:
            # This would typically query a database
            # For now, return mock data
            workflows = [
                {
                    "workflow_id": f"wf_{customer_id}_001",
                    "name": "Email Automation",
                    "template": "email_automation",
                    "status": "active",
                    "created_at": "2025-08-10T10:00:00Z",
                    "last_execution": "2025-08-11T09:30:00Z",
                    "execution_count": 15,
                    "success_rate": 0.93
                },
                {
                    "workflow_id": f"wf_{customer_id}_002", 
                    "name": "Data Processing",
                    "template": "data_processing",
                    "status": "paused",
                    "created_at": "2025-08-09T14:20:00Z",
                    "last_execution": "2025-08-11T08:15:00Z",
                    "execution_count": 8,
                    "success_rate": 1.0
                }
            ]
            
            return {
                "success": True,
                "workflows": workflows,
                "total_count": len(workflows),
                "active_count": sum(1 for w in workflows if w["status"] == "active"),
                "customer_id": customer_id
            }
            
        except Exception as e:
            logger.error(f"Error getting customer workflows: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _check_oauth_requirements(self, customer_id: str, required_apps: List[str]) -> Dict[str, Any]:
        """Check if customer has required OAuth connections"""
        try:
            connections_result = await self.composio_service.get_connection_status(customer_id)
            
            if not connections_result.get("success"):
                return {
                    "all_connected": False,
                    "missing_connections": required_apps,
                    "error": connections_result.get("error")
                }
            
            connected_apps = [conn["app_name"] for conn in connections_result.get("connections", [])]
            missing_apps = [app for app in required_apps if app not in connected_apps]
            
            # Generate OAuth URLs for missing connections
            auth_urls = {}
            for app in missing_apps:
                oauth_result = await self.composio_service.initiate_oauth_flow(app, customer_id)
                if oauth_result.get("success"):
                    auth_urls[app] = oauth_result["auth_url"]
            
            return {
                "all_connected": len(missing_apps) == 0,
                "connected_apps": connected_apps,
                "missing_connections": missing_apps,
                "auth_urls": auth_urls
            }
            
        except Exception as e:
            logger.error(f"Error checking OAuth requirements: {e}")
            return {
                "all_connected": False,
                "missing_connections": required_apps,
                "error": str(e)
            }
    
    async def _verify_workflow_access(self, workflow_id: str, customer_id: str) -> Dict[str, Any]:
        """Verify customer has access to workflow"""
        # This would typically check database permissions
        # For now, assume access is granted if workflow_id contains customer_id
        has_access = customer_id in workflow_id or workflow_id.startswith(f"wf_{customer_id}")
        
        return {
            "has_access": has_access,
            "workflow_id": workflow_id,
            "customer_id": customer_id
        }
    
    async def _generate_workflow_insights(self, status_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered workflow insights"""
        try:
            workflow_summary = json.dumps(status_data, indent=2)
            
            system_prompt = """You are a workflow analysis expert. Analyze the workflow status data and provide insights about:
            1. Performance trends
            2. Potential issues
            3. Optimization opportunities
            4. Success patterns
            
            Respond in JSON format with insights, trends, and recommendations."""
            
            insights_result = await self.openrouter_service.generate_response(
                prompt=f"Analyze this workflow data and provide insights: {workflow_summary}",
                system_prompt=system_prompt,
                model="meta-llama/llama-3.1-8b-instruct:free",
                max_tokens=800,
                temperature=0.4
            )
            
            if insights_result.get("success"):
                try:
                    return json.loads(insights_result["response"])
                except json.JSONDecodeError:
                    return {"summary": insights_result["response"]}
            else:
                return {"error": "Failed to generate insights"}
                
        except Exception as e:
            logger.error(f"Error generating workflow insights: {e}")
            return {"error": str(e)}
    
    async def _get_workflow_recommendations(self, workflow_id: str, status_data: Dict[str, Any]) -> List[str]:
        """Get AI-generated workflow recommendations"""
        try:
            recommendations = [
                "Monitor execution frequency and adjust scheduling",
                "Review error patterns and implement better error handling",
                "Consider adding data validation steps",
                "Optimize node connections for better performance"
            ]
            
            # Add dynamic recommendations based on status
            workflow = status_data.get("workflow", {})
            executions = status_data.get("recent_executions", [])
            
            if len(executions) == 0:
                recommendations.append("Execute the workflow to establish baseline performance")
            elif len([e for e in executions if e.get("status") == "success"]) < len(executions) * 0.8:
                recommendations.append("Investigate and fix recurring execution failures")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting workflow recommendations: {e}")
            return ["Review workflow configuration and performance"]
    
    async def close(self):
        """Close all service connections"""
        await self.mcp_service.close()
        await self.composio_service.close()
        await self.openrouter_service.close()