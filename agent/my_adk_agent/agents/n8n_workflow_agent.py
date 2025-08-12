"""
N8N Workflow Agent - Google ADK Framework with MCP Integration
Handles authenticated customers who need quick workflow automation
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
import logging

# Import mock Google ADK for development
try:
    from google.adk import Agent, tool
    from google.generativeai import GenerativeModel
except ImportError:
    from ..mock_google_adk import Agent, tool, MockGenerativeModel as GenerativeModel

from ..services.supabase_service import SupabaseService
from ..services.mcp_service import MCPService
from ..models.workflow import Workflow, WorkflowExecution

logger = logging.getLogger(__name__)

class N8nWorkflowAgent(Agent):
    """
    N8N Workflow automation agent using Google ADK + MCP
    - Creates and manages n8n workflows
    - Executes workflows for authenticated customers
    - Monitors workflow performance
    - Provides ready-to-use workflow templates
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            name="N8nWorkflowAgent",
            description="Handles n8n workflow automation for authenticated customers",
            model=GenerativeModel("gemini-2.0-flash-exp"),
            system_prompt=self._get_system_prompt()
        )
        
        self.config = config
        self.supabase = SupabaseService(config)
        self.mcp = MCPService(config)
        self.workflow_templates = self._load_workflow_templates()
        
    def _get_system_prompt(self) -> str:
        return """
        أنت وكيل أتمتة سير العمل المتخصص في n8n لشركة consulting.sa
        You are a specialized n8n workflow automation agent for consulting.sa
        
        مهامك الأساسية / Your main tasks:
        1. إنشاء وإدارة سير العمل في n8n / Create and manage n8n workflows
        2. تنفيذ سير العمل للعملاء المصرح لهم / Execute workflows for authenticated customers
        3. مراقبة أداء سير العمل / Monitor workflow performance
        4. تقديم قوالب جاهزة للاستخدام / Provide ready-to-use templates
        
        قوالب سير العمل المتاحة / Available Workflow Templates:
        1. أتمتة البريد الإلكتروني / Email Automation
        2. معالجة البيانات / Data Processing
        3. تكامل الأنظمة / System Integration
        4. إشعارات تلقائية / Automated Notifications
        5. تحليل المشاعر / Sentiment Analysis
        6. إدارة المهام / Task Management
        7. تقارير تلقائية / Automated Reports
        8. نسخ احتياطية / Backup Automation
        
        قواعد مهمة / Important Rules:
        1. تأكد من صحة بيانات العميل / Verify customer authentication
        2. اختبر سير العمل قبل التنفيذ / Test workflows before execution
        3. راقب الأداء والأخطاء / Monitor performance and errors
        4. قدم تقارير مفصلة / Provide detailed reports
        5. احترم حدود الموارد / Respect resource limits
        """
    
    def _load_workflow_templates(self) -> Dict[str, Any]:
        """Load predefined workflow templates"""
        return {
            "email_automation": {
                "name": "Email Automation",
                "name_ar": "أتمتة البريد الإلكتروني",
                "description": "Automated email campaigns and responses",
                "description_ar": "حملات بريد إلكتروني تلقائية وردود آلية",
                "nodes": ["Email Trigger", "Condition", "Send Email", "Database Update"],
                "estimated_time": "15 minutes",
                "complexity": "medium"
            },
            "data_processing": {
                "name": "Data Processing",
                "name_ar": "معالجة البيانات",
                "description": "Automated data cleaning and transformation",
                "description_ar": "تنظيف وتحويل البيانات تلقائياً",
                "nodes": ["HTTP Request", "Data Transform", "Filter", "Database Insert"],
                "estimated_time": "20 minutes",
                "complexity": "high"
            },
            "system_integration": {
                "name": "System Integration",
                "name_ar": "تكامل الأنظمة",
                "description": "Connect different systems and APIs",
                "description_ar": "ربط الأنظمة المختلفة وواجهات البرمجة",
                "nodes": ["Webhook", "API Call", "Data Mapping", "Response Handler"],
                "estimated_time": "30 minutes",
                "complexity": "high"
            },
            "notifications": {
                "name": "Automated Notifications",
                "name_ar": "إشعارات تلقائية",
                "description": "Send notifications based on triggers",
                "description_ar": "إرسال إشعارات بناءً على المحفزات",
                "nodes": ["Schedule Trigger", "Condition Check", "Slack/Teams", "SMS"],
                "estimated_time": "10 minutes",
                "complexity": "low"
            },
            "sentiment_analysis": {
                "name": "Sentiment Analysis",
                "name_ar": "تحليل المشاعر",
                "description": "Analyze customer feedback sentiment",
                "description_ar": "تحليل مشاعر تعليقات العملاء",
                "nodes": ["Text Input", "AI Analysis", "Classification", "Report Generation"],
                "estimated_time": "25 minutes",
                "complexity": "medium"
            }
        }
    
    @tool
    async def list_workflow_templates(self, language: str = "ar") -> Dict[str, Any]:
        """
        List available workflow templates
        
        Args:
            language: Response language (ar/en)
        """
        try:
            templates = []
            
            for template_id, template in self.workflow_templates.items():
                template_info = {
                    "id": template_id,
                    "name": template["name_ar"] if language == "ar" else template["name"],
                    "description": template["description_ar"] if language == "ar" else template["description"],
                    "estimated_time": template["estimated_time"],
                    "complexity": template["complexity"],
                    "nodes_count": len(template["nodes"])
                }
                templates.append(template_info)
            
            return {
                "success": True,
                "templates": templates,
                "total_count": len(templates)
            }
            
        except Exception as e:
            logger.error(f"Error listing workflow templates: {e}")
            return {
                "success": False,
                "error": "خطأ في جلب قوالب سير العمل" if language == "ar" else "Error fetching workflow templates"
            }
    
    @tool
    async def create_workflow(self, customer_id: str, template_id: str, custom_config: Dict[str, Any] = None, language: str = "ar") -> Dict[str, Any]:
        """
        Create a new n8n workflow from template
        
        Args:
            customer_id: Authenticated customer ID
            template_id: Template identifier
            custom_config: Custom configuration parameters
            language: Response language
        """
        try:
            # Verify customer authentication
            customer = await self.supabase.get_customer(customer_id)
            if not customer or customer.status != "authenticated":
                return {
                    "success": False,
                    "error": "العميل غير مصرح له" if language == "ar" else "Customer not authenticated"
                }
            
            # Get template
            if template_id not in self.workflow_templates:
                return {
                    "success": False,
                    "error": "قالب غير موجود" if language == "ar" else "Template not found"
                }
            
            template = self.workflow_templates[template_id]
            
            # Create workflow via MCP
            workflow_data = {
                "name": f"{template['name']}_{customer_id}_{asyncio.get_event_loop().time()}",
                "template_id": template_id,
                "customer_id": customer_id,
                "nodes": template["nodes"],
                "custom_config": custom_config or {}
            }
            
            workflow_result = await self.mcp.create_workflow(workflow_data)
            
            if workflow_result["success"]:
                # Store workflow in database
                workflow = await self.supabase.create_workflow({
                    "customer_id": customer_id,
                    "n8n_workflow_id": workflow_result["workflow_id"],
                    "template_id": template_id,
                    "name": workflow_data["name"],
                    "status": "created",
                    "config": workflow_data
                })
                
                logger.info(f"Workflow created: {workflow.id} for customer {customer_id}")
                
                return {
                    "success": True,
                    "workflow_id": workflow.id,
                    "n8n_workflow_id": workflow_result["workflow_id"],
                    "name": workflow_data["name"],
                    "status": "created",
                    "message": "تم إنشاء سير العمل بنجاح" if language == "ar" else "Workflow created successfully",
                    "next_steps": "يمكنك الآن تنفيذ سير العمل" if language == "ar" else "You can now execute the workflow"
                }
            else:
                return {
                    "success": False,
                    "error": workflow_result.get("error", "خطأ في إنشاء سير العمل" if language == "ar" else "Error creating workflow")
                }
                
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            return {
                "success": False,
                "error": "خطأ في إنشاء سير العمل" if language == "ar" else "Error creating workflow"
            }
    
    @tool
    async def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any] = None, language: str = "ar") -> Dict[str, Any]:
        """
        Execute an existing workflow
        
        Args:
            workflow_id: Workflow identifier
            input_data: Input data for workflow execution
            language: Response language
        """
        try:
            # Get workflow from database
            workflow = await self.supabase.get_workflow(workflow_id)
            if not workflow:
                return {
                    "success": False,
                    "error": "سير العمل غير موجود" if language == "ar" else "Workflow not found"
                }
            
            # Execute via MCP
            execution_result = await self.mcp.execute_workflow(
                workflow.n8n_workflow_id,
                input_data or {}
            )
            
            if execution_result["success"]:
                # Store execution record
                execution = await self.supabase.create_workflow_execution({
                    "workflow_id": workflow_id,
                    "n8n_execution_id": execution_result["execution_id"],
                    "input_data": input_data,
                    "status": "running",
                    "started_at": execution_result["started_at"]
                })
                
                logger.info(f"Workflow execution started: {execution.id}")
                
                return {
                    "success": True,
                    "execution_id": execution.id,
                    "n8n_execution_id": execution_result["execution_id"],
                    "status": "running",
                    "message": "تم بدء تنفيذ سير العمل" if language == "ar" else "Workflow execution started",
                    "estimated_duration": execution_result.get("estimated_duration", "غير محدد" if language == "ar" else "Unknown")
                }
            else:
                return {
                    "success": False,
                    "error": execution_result.get("error", "خطأ في تنفيذ سير العمل" if language == "ar" else "Error executing workflow")
                }
                
        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            return {
                "success": False,
                "error": "خطأ في تنفيذ سير العمل" if language == "ar" else "Error executing workflow"
            }
    
    @tool
    async def get_workflow_status(self, workflow_id: str, language: str = "ar") -> Dict[str, Any]:
        """
        Get workflow execution status and results
        
        Args:
            workflow_id: Workflow identifier
            language: Response language
        """
        try:
            # Get workflow and recent executions
            workflow = await self.supabase.get_workflow(workflow_id)
            if not workflow:
                return {
                    "success": False,
                    "error": "سير العمل غير موجود" if language == "ar" else "Workflow not found"
                }
            
            executions = await self.supabase.get_workflow_executions(workflow_id, limit=5)
            
            # Get status from n8n via MCP
            n8n_status = await self.mcp.get_workflow_status(workflow.n8n_workflow_id)
            
            return {
                "success": True,
                "workflow": {
                    "id": workflow.id,
                    "name": workflow.name,
                    "status": workflow.status,
                    "created_at": workflow.created_at.isoformat(),
                    "template_id": workflow.template_id
                },
                "n8n_status": n8n_status,
                "recent_executions": [
                    {
                        "id": exec.id,
                        "status": exec.status,
                        "started_at": exec.started_at.isoformat() if exec.started_at else None,
                        "completed_at": exec.completed_at.isoformat() if exec.completed_at else None,
                        "success": exec.success
                    }
                    for exec in executions
                ],
                "total_executions": len(executions)
            }
            
        except Exception as e:
            logger.error(f"Error getting workflow status: {e}")
            return {
                "success": False,
                "error": "خطأ في جلب حالة سير العمل" if language == "ar" else "Error getting workflow status"
            }
    
    @tool
    async def list_customer_workflows(self, customer_id: str, language: str = "ar") -> Dict[str, Any]:
        """
        List all workflows for a customer
        
        Args:
            customer_id: Customer identifier
            language: Response language
        """
        try:
            workflows = await self.supabase.get_customer_workflows(customer_id)
            
            workflow_list = []
            for workflow in workflows:
                workflow_info = {
                    "id": workflow.id,
                    "name": workflow.name,
                    "template_id": workflow.template_id,
                    "status": workflow.status,
                    "created_at": workflow.created_at.isoformat(),
                    "last_execution": None
                }
                
                # Get last execution
                last_execution = await self.supabase.get_last_workflow_execution(workflow.id)
                if last_execution:
                    workflow_info["last_execution"] = {
                        "status": last_execution.status,
                        "started_at": last_execution.started_at.isoformat() if last_execution.started_at else None,
                        "success": last_execution.success
                    }
                
                workflow_list.append(workflow_info)
            
            return {
                "success": True,
                "workflows": workflow_list,
                "total_count": len(workflow_list)
            }
            
        except Exception as e:
            logger.error(f"Error listing customer workflows: {e}")
            return {
                "success": False,
                "error": "خطأ في جلب سير العمل" if language == "ar" else "Error fetching workflows"
            }
    
    @tool
    async def monitor_workflow_performance(self, workflow_id: str, days: int = 7, language: str = "ar") -> Dict[str, Any]:
        """
        Monitor workflow performance metrics
        
        Args:
            workflow_id: Workflow identifier
            days: Number of days to analyze
            language: Response language
        """
        try:
            # Get performance metrics from database
            metrics = await self.supabase.get_workflow_metrics(workflow_id, days)
            
            # Get n8n metrics via MCP
            n8n_metrics = await self.mcp.get_workflow_metrics(workflow_id, days)
            
            return {
                "success": True,
                "metrics": {
                    "total_executions": metrics.get("total_executions", 0),
                    "successful_executions": metrics.get("successful_executions", 0),
                    "failed_executions": metrics.get("failed_executions", 0),
                    "success_rate": metrics.get("success_rate", 0),
                    "average_duration": metrics.get("average_duration", 0),
                    "total_runtime": metrics.get("total_runtime", 0),
                    "error_rate": metrics.get("error_rate", 0)
                },
                "n8n_metrics": n8n_metrics,
                "period": f"{days} {'أيام' if language == 'ar' else 'days'}",
                "recommendations": self._generate_performance_recommendations(metrics, language)
            }
            
        except Exception as e:
            logger.error(f"Error monitoring workflow performance: {e}")
            return {
                "success": False,
                "error": "خطأ في مراقبة الأداء" if language == "ar" else "Error monitoring performance"
            }
    
    def _generate_performance_recommendations(self, metrics: Dict[str, Any], language: str) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        success_rate = metrics.get("success_rate", 0)
        error_rate = metrics.get("error_rate", 0)
        avg_duration = metrics.get("average_duration", 0)
        
        if language == "ar":
            if success_rate < 0.8:
                recommendations.append("معدل النجاح منخفض - يُنصح بمراجعة إعدادات سير العمل")
            if error_rate > 0.2:
                recommendations.append("معدل الأخطاء مرتفع - تحقق من اتصالات الأنظمة الخارجية")
            if avg_duration > 300:  # 5 minutes
                recommendations.append("مدة التنفيذ طويلة - فكر في تحسين العمليات")
            if not recommendations:
                recommendations.append("الأداء جيد - استمر في المراقبة المنتظمة")
        else:
            if success_rate < 0.8:
                recommendations.append("Low success rate - consider reviewing workflow configuration")
            if error_rate > 0.2:
                recommendations.append("High error rate - check external system connections")
            if avg_duration > 300:  # 5 minutes
                recommendations.append("Long execution time - consider optimizing processes")
            if not recommendations:
                recommendations.append("Performance is good - continue regular monitoring")
        
        return recommendations
    
    async def process_workflow_request(self, message: str, customer_id: str, language: str = "ar") -> Dict[str, Any]:
        """
        Process workflow-related customer requests
        
        Args:
            message: Customer message
            customer_id: Customer identifier
            language: Customer language
            
        Returns:
            Response dictionary
        """
        try:
            # Generate response using Gemini with workflow context
            context = f"""
            Customer ID: {customer_id}
            Language: {language}
            Available Templates: {list(self.workflow_templates.keys())}
            Message: {message}
            """
            
            response = await self.model.generate_content_async(
                f"{self.system_prompt}\n\nContext: {context}\n\nRespond with workflow assistance:"
            )
            
            # Determine if specific actions are needed
            actions = self._determine_workflow_actions(message, language)
            
            return {
                "content": response.text,
                "language": language,
                "actions": actions,
                "agent_type": "n8n_workflow"
            }
            
        except Exception as e:
            logger.error(f"Error processing workflow request: {e}")
            return {
                "content": "عذراً، حدث خطأ في معالجة طلبك" if language == "ar" else "Sorry, an error occurred processing your request",
                "language": language,
                "actions": [],
                "agent_type": "n8n_workflow"
            }
    
    def _determine_workflow_actions(self, message: str, language: str) -> List[Dict[str, Any]]:
        """Determine workflow-specific actions based on message"""
        actions = []
        message_lower = message.lower()
        
        # Check for template requests
        template_keywords_ar = ["قالب", "نموذج", "مثال", "جاهز"]
        template_keywords_en = ["template", "example", "ready", "sample"]
        
        if any(keyword in message_lower for keyword in template_keywords_ar + template_keywords_en):
            actions.append({
                "type": "show_templates",
                "priority": "high"
            })
        
        # Check for execution requests
        execute_keywords_ar = ["تنفيذ", "تشغيل", "بدء", "تفعيل"]
        execute_keywords_en = ["execute", "run", "start", "trigger"]
        
        if any(keyword in message_lower for keyword in execute_keywords_ar + execute_keywords_en):
            actions.append({
                "type": "execute_workflow",
                "priority": "high"
            })
        
        # Check for status requests
        status_keywords_ar = ["حالة", "وضع", "تقرير", "نتيجة"]
        status_keywords_en = ["status", "state", "report", "result"]
        
        if any(keyword in message_lower for keyword in status_keywords_ar + status_keywords_en):
            actions.append({
                "type": "check_status",
                "priority": "medium"
            })
        
        return actions