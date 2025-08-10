"""
Customer Dashboard Service - Personalized screens and integrated chatbots
Handles customer-specific interfaces with project context and notifications
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class CustomerProfile:
    """Customer profile with service context"""
    customer_id: str
    name: str
    email: str
    phone: str
    service_type: str  # fast_solution, custom_development, consulting
    language: str
    project_details: Dict[str, Any]
    billing_info: Dict[str, Any]
    notification_preferences: Dict[str, Any]
    created_at: datetime
    last_active: datetime


@dataclass
class ProjectContext:
    """Project context for customer dashboard"""
    project_id: str
    customer_id: str
    service_type: str
    status: str  # planning, development, testing, deployed, completed
    requirements: Dict[str, Any]
    progress: Dict[str, Any]
    next_steps: List[str]
    deliverables: List[Dict[str, Any]]
    timeline: Dict[str, Any]
    billing_summary: Dict[str, Any]


@dataclass
class NotificationChannel:
    """Notification channel configuration"""
    channel_type: str  # whatsapp, telegram, instagram, email
    channel_id: str
    is_active: bool
    preferences: Dict[str, Any]


class CustomerDashboardService:
    """Service for managing customer dashboards and interactions"""
    
    def __init__(self):
        self.customers = {}  # In production, use database
        self.projects = {}
        self.notification_service = NotificationService()
        self.chatbot_service = CustomerChatbotService()
    
    def create_customer_dashboard(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create personalized dashboard for customer"""
        customer_id = customer_data["customer_id"]
        service_type = customer_data["service_type"]
        
        # Create customer profile
        profile = CustomerProfile(
            customer_id=customer_id,
            name=customer_data["name"],
            email=customer_data["email"],
            phone=customer_data["phone"],
            service_type=service_type,
            language=customer_data.get("language", "ar"),
            project_details={},
            billing_info={"status": "active", "balance": 0},
            notification_preferences=self._get_default_notification_preferences(),
            created_at=datetime.now(),
            last_active=datetime.now()
        )
        
        self.customers[customer_id] = profile
        
        # Create dashboard configuration
        dashboard_config = {
            "customer_id": customer_id,
            "service_type": service_type,
            "dashboard_sections": self._get_dashboard_sections(service_type),
            "chatbot_config": self._get_chatbot_config(customer_id, service_type),
            "notification_channels": self._setup_notification_channels(customer_data),
            "project_overview": self._get_project_overview(customer_id),
            "billing_widget": self._get_billing_widget(customer_id),
            "next_actions": self._get_next_actions(service_type)
        }
        
        return dashboard_config
    
    def get_customer_dashboard(self, customer_id: str) -> Dict[str, Any]:
        """Get customer dashboard with current context"""
        profile = self.customers.get(customer_id)
        if not profile:
            return {"error": "Customer not found"}
        
        # Update last active
        profile.last_active = datetime.now()
        
        # Get current project context
        project_context = self._get_current_project_context(customer_id)
        
        dashboard = {
            "customer_info": {
                "name": profile.name,
                "service_type": profile.service_type,
                "language": profile.language,
                "member_since": profile.created_at.strftime("%Y-%m-%d")
            },
            "project_status": project_context,
            "chatbot_interface": self._get_chatbot_interface(customer_id),
            "notifications": self._get_recent_notifications(customer_id),
            "billing_summary": self._get_billing_summary(customer_id),
            "support_options": self._get_support_options(profile.service_type),
            "quick_actions": self._get_quick_actions(customer_id, profile.service_type)
        }
        
        return dashboard
    
    def _get_dashboard_sections(self, service_type: str) -> List[Dict[str, Any]]:
        """Get dashboard sections based on service type"""
        common_sections = [
            {"id": "overview", "title": "نظرة عامة", "title_en": "Overview", "order": 1},
            {"id": "chatbot", "title": "المساعد الذكي", "title_en": "AI Assistant", "order": 2},
            {"id": "notifications", "title": "الإشعارات", "title_en": "Notifications", "order": 3},
            {"id": "billing", "title": "الفواتير", "title_en": "Billing", "order": 4},
            {"id": "support", "title": "الدعم", "title_en": "Support", "order": 5}
        ]
        
        service_specific_sections = {
            "fast_solution": [
                {"id": "workflows", "title": "سير العمل", "title_en": "Workflows", "order": 2.5},
                {"id": "automation", "title": "الأتمتة", "title_en": "Automation", "order": 2.7}
            ],
            "custom_development": [
                {"id": "development", "title": "التطوير", "title_en": "Development", "order": 2.5},
                {"id": "testing", "title": "الاختبار", "title_en": "Testing", "order": 2.7},
                {"id": "deployment", "title": "النشر", "title_en": "Deployment", "order": 2.9}
            ],
            "consulting": [
                {"id": "planning", "title": "التخطيط", "title_en": "Planning", "order": 2.5},
                {"id": "research", "title": "البحث", "title_en": "Research", "order": 2.7},
                {"id": "documentation", "title": "التوثيق", "title_en": "Documentation", "order": 2.9}
            ]
        }
        
        sections = common_sections + service_specific_sections.get(service_type, [])
        return sorted(sections, key=lambda x: x["order"])
    
    def _get_chatbot_config(self, customer_id: str, service_type: str) -> Dict[str, Any]:
        """Get chatbot configuration for customer"""
        return {
            "customer_id": customer_id,
            "service_context": service_type,
            "capabilities": self._get_chatbot_capabilities(service_type),
            "knowledge_base": f"{service_type}_knowledge",
            "personality": "professional_arabic" if self.customers[customer_id].language == "ar" else "professional_english",
            "integration_tools": self._get_integration_tools(service_type)
        }
    
    def _get_chatbot_capabilities(self, service_type: str) -> List[str]:
        """Get chatbot capabilities based on service type"""
        common_capabilities = [
            "project_status_inquiry",
            "billing_questions",
            "support_requests",
            "appointment_scheduling",
            "notification_management"
        ]
        
        service_capabilities = {
            "fast_solution": [
                "workflow_monitoring",
                "automation_status",
                "n8n_integration",
                "oauth_management",
                "sub_agent_control"
            ],
            "custom_development": [
                "development_progress",
                "testing_results",
                "deployment_status",
                "feature_requests",
                "technical_support"
            ],
            "consulting": [
                "meeting_scheduling",
                "research_requests",
                "document_access",
                "bmad_planning",
                "project_roadmap"
            ]
        }
        
        return common_capabilities + service_capabilities.get(service_type, [])
    
    def _get_integration_tools(self, service_type: str) -> List[str]:
        """Get integration tools available to chatbot"""
        common_tools = ["calendar", "notifications", "billing", "support_tickets"]
        
        service_tools = {
            "fast_solution": ["n8n_api", "composio_oauth", "workflow_monitor"],
            "custom_development": ["github_api", "deployment_tools", "testing_framework"],
            "consulting": ["bmad_method", "research_tools", "document_generator"]
        }
        
        return common_tools + service_tools.get(service_type, [])
    
    def _setup_notification_channels(self, customer_data: Dict[str, Any]) -> List[NotificationChannel]:
        """Setup notification channels for customer"""
        channels = []
        
        # WhatsApp (primary for Saudi customers)
        if customer_data.get("phone"):
            channels.append(NotificationChannel(
                channel_type="whatsapp",
                channel_id=customer_data["phone"],
                is_active=True,
                preferences={"priority": "high", "types": ["all"]}
            ))
        
        # Email
        if customer_data.get("email"):
            channels.append(NotificationChannel(
                channel_type="email",
                channel_id=customer_data["email"],
                is_active=True,
                preferences={"priority": "medium", "types": ["updates", "billing"]}
            ))
        
        return channels
    
    def _get_current_project_context(self, customer_id: str) -> Dict[str, Any]:
        """Get current project context for customer"""
        # Mock project context - implement with actual database
        profile = self.customers.get(customer_id)
        if not profile:
            return {}
        
        service_type = profile.service_type
        
        project_contexts = {
            "fast_solution": {
                "status": "active",
                "current_phase": "workflow_setup",
                "progress": 65,
                "next_milestone": "OAuth integration completion",
                "active_workflows": 2,
                "last_update": "2024-01-15 14:30"
            },
            "custom_development": {
                "status": "development",
                "current_phase": "backend_development",
                "progress": 40,
                "next_milestone": "API endpoints completion",
                "features_completed": 8,
                "features_remaining": 12,
                "last_update": "2024-01-15 16:45"
            },
            "consulting": {
                "status": "planning",
                "current_phase": "bmad_analysis",
                "progress": 25,
                "next_milestone": "Architecture document",
                "meetings_completed": 3,
                "deliverables_ready": 2,
                "last_update": "2024-01-15 11:20"
            }
        }
        
        return project_contexts.get(service_type, {})
    
    def _get_chatbot_interface(self, customer_id: str) -> Dict[str, Any]:
        """Get chatbot interface configuration"""
        profile = self.customers.get(customer_id)
        if not profile:
            return {}
        
        return {
            "widget_id": f"chatbot_{customer_id}",
            "language": profile.language,
            "welcome_message": self._get_welcome_message(profile),
            "quick_actions": self._get_chatbot_quick_actions(profile.service_type),
            "context_aware": True,
            "project_integration": True,
            "notification_enabled": True
        }
    
    def _get_welcome_message(self, profile: CustomerProfile) -> str:
        """Get personalized welcome message for chatbot"""
        if profile.language == "ar":
            return f"مرحباً {profile.name}! كيف يمكنني مساعدتك اليوم؟"
        else:
            return f"Hello {profile.name}! How can I help you today?"
    
    def _get_chatbot_quick_actions(self, service_type: str) -> List[Dict[str, str]]:
        """Get quick action buttons for chatbot"""
        common_actions = [
            {"id": "project_status", "label_ar": "حالة المشروع", "label_en": "Project Status"},
            {"id": "billing_info", "label_ar": "معلومات الفواتير", "label_en": "Billing Info"},
            {"id": "schedule_meeting", "label_ar": "جدولة اجتماع", "label_en": "Schedule Meeting"}
        ]
        
        service_actions = {
            "fast_solution": [
                {"id": "workflow_status", "label_ar": "حالة سير العمل", "label_en": "Workflow Status"},
                {"id": "add_integration", "label_ar": "إضافة تكامل", "label_en": "Add Integration"}
            ],
            "custom_development": [
                {"id": "development_progress", "label_ar": "تقدم التطوير", "label_en": "Development Progress"},
                {"id": "request_feature", "label_ar": "طلب ميزة", "label_en": "Request Feature"}
            ],
            "consulting": [
                {"id": "view_documents", "label_ar": "عرض الوثائق", "label_en": "View Documents"},
                {"id": "research_request", "label_ar": "طلب بحث", "label_en": "Research Request"}
            ]
        }
        
        return common_actions + service_actions.get(service_type, [])
    
    def _get_recent_notifications(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get recent notifications for customer"""
        # Mock notifications - implement with actual notification system
        return [
            {
                "id": "notif_001",
                "type": "project_update",
                "title": "تحديث المشروع",
                "title_en": "Project Update",
                "message": "تم إكمال المرحلة الأولى من التطوير",
                "message_en": "First development phase completed",
                "timestamp": "2024-01-15 14:30",
                "read": False
            },
            {
                "id": "notif_002",
                "type": "billing",
                "title": "فاتورة جديدة",
                "title_en": "New Invoice",
                "message": "فاتورة جديدة متاحة للعرض",
                "message_en": "New invoice available for review",
                "timestamp": "2024-01-14 09:15",
                "read": True
            }
        ]
    
    def _get_billing_summary(self, customer_id: str) -> Dict[str, Any]:
        """Get billing summary for customer"""
        # Mock billing data - implement with actual billing system
        return {
            "current_balance": 0,
            "next_payment_due": "2024-02-01",
            "payment_method": "credit_card",
            "billing_cycle": "monthly",
            "recent_invoices": [
                {"id": "inv_001", "amount": 500, "date": "2024-01-01", "status": "paid"},
                {"id": "inv_002", "amount": 750, "date": "2024-01-15", "status": "pending"}
            ]
        }
    
    def _get_support_options(self, service_type: str) -> List[Dict[str, Any]]:
        """Get support options based on service type"""
        return [
            {
                "type": "chat",
                "title": "دردشة مباشرة",
                "title_en": "Live Chat",
                "available": True,
                "response_time": "فوري"
            },
            {
                "type": "whatsapp",
                "title": "واتساب",
                "title_en": "WhatsApp",
                "available": True,
                "response_time": "خلال ساعة"
            },
            {
                "type": "email",
                "title": "بريد إلكتروني",
                "title_en": "Email",
                "available": True,
                "response_time": "خلال 24 ساعة"
            }
        ]
    
    def _get_quick_actions(self, customer_id: str, service_type: str) -> List[Dict[str, Any]]:
        """Get quick actions for customer dashboard"""
        common_actions = [
            {"id": "contact_support", "title": "اتصل بالدعم", "title_en": "Contact Support"},
            {"id": "view_billing", "title": "عرض الفواتير", "title_en": "View Billing"},
            {"id": "update_profile", "title": "تحديث الملف الشخصي", "title_en": "Update Profile"}
        ]
        
        service_actions = {
            "fast_solution": [
                {"id": "create_workflow", "title": "إنشاء سير عمل", "title_en": "Create Workflow"},
                {"id": "manage_integrations", "title": "إدارة التكاملات", "title_en": "Manage Integrations"}
            ],
            "custom_development": [
                {"id": "request_changes", "title": "طلب تعديلات", "title_en": "Request Changes"},
                {"id": "view_progress", "title": "عرض التقدم", "title_en": "View Progress"}
            ],
            "consulting": [
                {"id": "schedule_consultation", "title": "جدولة استشارة", "title_en": "Schedule Consultation"},
                {"id": "access_documents", "title": "الوصول للوثائق", "title_en": "Access Documents"}
            ]
        }
        
        return common_actions + service_actions.get(service_type, [])
    
    def _get_default_notification_preferences(self) -> Dict[str, Any]:
        """Get default notification preferences"""
        return {
            "project_updates": {"whatsapp": True, "email": True, "telegram": False},
            "billing_alerts": {"whatsapp": True, "email": True, "telegram": False},
            "system_notifications": {"whatsapp": False, "email": True, "telegram": False},
            "marketing": {"whatsapp": False, "email": False, "telegram": False}
        }
    
    def _get_project_overview(self, customer_id: str) -> Dict[str, Any]:
        """Get project overview for dashboard"""
        return {
            "total_projects": 1,
            "active_projects": 1,
            "completed_projects": 0,
            "upcoming_milestones": 2,
            "last_activity": "2024-01-15 14:30"
        }
    
    def _get_billing_widget(self, customer_id: str) -> Dict[str, Any]:
        """Get billing widget data"""
        return {
            "current_balance": 0,
            "next_payment": "2024-02-01",
            "payment_status": "current",
            "quick_pay_enabled": True
        }
    
    def _get_next_actions(self, service_type: str) -> List[str]:
        """Get next recommended actions"""
        actions_map = {
            "fast_solution": [
                "Complete OAuth setup for integrations",
                "Test your first workflow",
                "Configure notification preferences"
            ],
            "custom_development": [
                "Review development requirements",
                "Approve technical specifications",
                "Schedule progress review meeting"
            ],
            "consulting": [
                "Complete BMad-Method planning session",
                "Review research documents",
                "Schedule implementation discussion"
            ]
        }
        
        return actions_map.get(service_type, ["Contact support for next steps"])


class NotificationService:
    """Service for managing customer notifications"""
    
    def __init__(self):
        self.composio_api_key = "ak_MQM5jiai1Vjkwel-lL7N"
    
    def send_notification(self, customer_id: str, channel: str, message: str) -> bool:
        """Send notification via specified channel"""
        try:
            if channel == "whatsapp":
                return self._send_whatsapp_notification(customer_id, message)
            elif channel == "telegram":
                return self._send_telegram_notification(customer_id, message)
            elif channel == "instagram":
                return self._send_instagram_notification(customer_id, message)
            elif channel == "email":
                return self._send_email_notification(customer_id, message)
            else:
                logger.warning(f"Unknown notification channel: {channel}")
                return False
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False
    
    def _send_whatsapp_notification(self, customer_id: str, message: str) -> bool:
        """Send WhatsApp notification using Composio"""
        # Implement Composio WhatsApp API call
        logger.info(f"Sending WhatsApp notification to {customer_id}: {message}")
        return True
    
    def _send_telegram_notification(self, customer_id: str, message: str) -> bool:
        """Send Telegram notification using Composio"""
        # Implement Composio Telegram API call
        logger.info(f"Sending Telegram notification to {customer_id}: {message}")
        return True
    
    def _send_instagram_notification(self, customer_id: str, message: str) -> bool:
        """Send Instagram notification using Composio"""
        # Implement Composio Instagram API call
        logger.info(f"Sending Instagram notification to {customer_id}: {message}")
        return True
    
    def _send_email_notification(self, customer_id: str, message: str) -> bool:
        """Send email notification"""
        # Implement email sending
        logger.info(f"Sending email notification to {customer_id}: {message}")
        return True


class CustomerChatbotService:
    """Service for customer-specific chatbots"""
    
    def __init__(self):
        self.customer_contexts = {}
    
    def get_chatbot_response(self, customer_id: str, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get chatbot response with customer context"""
        # This would integrate with the appropriate agent based on customer's service type
        service_type = context.get("service_type")
        
        # Route to appropriate agent with customer context
        agent_response = self._route_to_customer_agent(customer_id, service_type, message, context)
        
        return {
            "response": agent_response,
            "customer_id": customer_id,
            "context_updated": True,
            "notifications_triggered": self._check_notification_triggers(agent_response)
        }
    
    def _route_to_customer_agent(self, customer_id: str, service_type: str, message: str, context: Dict[str, Any]) -> str:
        """Route message to appropriate customer agent"""
        # This would call the actual agent with customer context
        # For now, return a mock response
        return f"Customer-specific response for {service_type} service"
    
    def _check_notification_triggers(self, response: str) -> List[str]:
        """Check if response should trigger notifications"""
        # Implement notification trigger logic
        return []