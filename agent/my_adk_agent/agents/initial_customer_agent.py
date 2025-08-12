"""
Initial Customer Agent - Google ADK Framework
Handles new customer interactions, information gathering, and LiveKit handoff
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
from ..services.livekit_service import LiveKitService
from ..models.customer import Customer, CustomerInquiry

logger = logging.getLogger(__name__)

class InitialCustomerAgent(Agent):
    """
    Initial customer interaction agent using Google ADK
    - Collects customer information (name, email, phone)
    - Detects language (Arabic/English)
    - Provides basic information about services
    - Handles LiveKit handoff to human agents
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            name="InitialCustomerAgent",
            description="Handles initial customer interactions and information gathering",
            model=GenerativeModel("gemini-2.0-flash-exp"),
            system_prompt=self._get_system_prompt()
        )
        
        self.config = config
        self.supabase = SupabaseService(config)
        self.livekit = LiveKitService(config)
        self.conversation_state = {}
        
    def _get_system_prompt(self) -> str:
        return """
        أنت مساعد ذكي لشركة consulting.sa المتخصصة في حلول الذكاء الاصطناعي.
        You are an AI assistant for consulting.sa, specializing in AI solutions.
        
        مهامك الأساسية / Your main tasks:
        1. جمع معلومات العميل (الاسم، البريد الإلكتروني، رقم الهاتف) / Collect customer information (name, email, phone)
        2. تحديد لغة العميل (عربي/إنجليزي) / Detect customer language (Arabic/English)
        3. تقديم معلومات أساسية عن خدماتنا / Provide basic information about our services
        4. تحويل العميل إلى وكيل بشري عند الحاجة / Transfer to human agent when needed
        
        خدماتنا / Our services:
        - وكلاء الذكاء الاصطناعي / AI Agents
        - روبوتات المحادثة / Chatbots  
        - استشارات الذكاء الاصطناعي / AI Consulting
        - أتمتة سير العمل / Workflow Automation
        
        معلومات الاتصال / Contact Information:
        - البريد الإلكتروني / Email: cto@consulting.sa
        - الهاتف / Phone: 00966542331876
        - الموقع / Website: consulting.sa
        
        قواعد مهمة / Important Rules:
        1. كن مهذباً ومفيداً / Be polite and helpful
        2. اجمع المعلومات تدريجياً / Collect information gradually
        3. لا تطلب معلومات حساسة / Don't ask for sensitive information
        4. استخدم نفس لغة العميل / Use the same language as the customer
        5. اعرض التحويل للوكيل البشري عند الحاجة / Offer human agent transfer when needed
        """
    
    @tool
    async def collect_customer_info(self, name: str = None, email: str = None, phone: str = None, language: str = "ar") -> Dict[str, Any]:
        """
        Collect and store customer information
        
        Args:
            name: Customer name
            email: Customer email
            phone: Customer phone number
            language: Preferred language (ar/en)
        """
        try:
            customer_data = {
                "name": name,
                "email": email, 
                "phone": phone,
                "language": language,
                "source": "initial_chat",
                "status": "new_inquiry"
            }
            
            # Store in Supabase
            customer = await self.supabase.create_customer(customer_data)
            
            logger.info(f"Customer information collected: {customer.id}")
            
            return {
                "success": True,
                "customer_id": customer.id,
                "message": "تم حفظ معلوماتك بنجاح" if language == "ar" else "Your information has been saved successfully",
                "next_steps": "سيتم التواصل معك قريباً" if language == "ar" else "We will contact you soon"
            }
            
        except Exception as e:
            logger.error(f"Error collecting customer info: {e}")
            return {
                "success": False,
                "error": "حدث خطأ في حفظ المعلومات" if language == "ar" else "Error saving information"
            }
    
    @tool
    async def get_service_info(self, service_type: str, language: str = "ar") -> Dict[str, Any]:
        """
        Provide information about our services
        
        Args:
            service_type: Type of service (ai_agents, chatbots, consulting, workflows)
            language: Response language (ar/en)
        """
        services_ar = {
            "ai_agents": {
                "title": "وكلاء الذكاء الاصطناعي",
                "description": "حلول أتمتة ذكية تساعد في تحسين كفاءة العمل وتقليل التكاليف",
                "features": ["أتمتة المهام المتكررة", "تحليل البيانات", "اتخاذ القرارات الذكية"],
                "price_range": "يبدأ من 500 ريال شهرياً"
            },
            "chatbots": {
                "title": "روبوتات المحادثة",
                "description": "واجهات ذكية للتفاعل مع العملاء على مدار الساعة",
                "features": ["دعم متعدد اللغات", "تكامل مع الأنظمة", "تحليل المشاعر"],
                "price_range": "يبدأ من 300 ريال شهرياً"
            },
            "consulting": {
                "title": "استشارات الذكاء الاصطناعي",
                "description": "خدمات استشارية متخصصة لتطبيق الذكاء الاصطناعي في أعمالك",
                "features": ["تحليل الاحتياجات", "وضع الاستراتيجيات", "التنفيذ والمتابعة"],
                "price_range": "يبدأ من 1000 ريال للجلسة"
            },
            "workflows": {
                "title": "أتمتة سير العمل",
                "description": "حلول أتمتة شاملة لتحسين العمليات التجارية",
                "features": ["تصميم سير العمل", "تكامل الأنظمة", "مراقبة الأداء"],
                "price_range": "يبدأ من 800 ريال شهرياً"
            }
        }
        
        services_en = {
            "ai_agents": {
                "title": "AI Agents",
                "description": "Intelligent automation solutions that improve work efficiency and reduce costs",
                "features": ["Automate repetitive tasks", "Data analysis", "Smart decision making"],
                "price_range": "Starting from 500 SAR/month"
            },
            "chatbots": {
                "title": "Chatbots",
                "description": "Smart interfaces for 24/7 customer interaction",
                "features": ["Multi-language support", "System integration", "Sentiment analysis"],
                "price_range": "Starting from 300 SAR/month"
            },
            "consulting": {
                "title": "AI Consulting",
                "description": "Specialized consulting services for implementing AI in your business",
                "features": ["Needs analysis", "Strategy development", "Implementation and follow-up"],
                "price_range": "Starting from 1000 SAR/session"
            },
            "workflows": {
                "title": "Workflow Automation",
                "description": "Comprehensive automation solutions to improve business processes",
                "features": ["Workflow design", "System integration", "Performance monitoring"],
                "price_range": "Starting from 800 SAR/month"
            }
        }
        
        services = services_ar if language == "ar" else services_en
        
        if service_type in services:
            return {
                "success": True,
                "service": services[service_type]
            }
        else:
            return {
                "success": False,
                "error": "نوع الخدمة غير متوفر" if language == "ar" else "Service type not available"
            }
    
    @tool
    async def initiate_human_handoff(self, customer_id: str, reason: str, language: str = "ar") -> Dict[str, Any]:
        """
        Initiate handoff to human agent via LiveKit
        
        Args:
            customer_id: Customer ID
            reason: Reason for handoff
            language: Customer language
        """
        try:
            # Create LiveKit room for customer
            room_info = await self.livekit.create_room(
                room_name=f"customer_{customer_id}",
                customer_id=customer_id,
                agent_type="human_consultant"
            )
            
            # Update customer status
            await self.supabase.update_customer_status(
                customer_id=customer_id,
                status="human_handoff",
                notes=f"Handoff reason: {reason}"
            )
            
            logger.info(f"Human handoff initiated for customer {customer_id}")
            
            return {
                "success": True,
                "room_url": room_info["room_url"],
                "room_token": room_info["token"],
                "message": "جاري تحويلك إلى أحد المختصين" if language == "ar" else "Connecting you to a specialist",
                "estimated_wait": "2-3 دقائق" if language == "ar" else "2-3 minutes"
            }
            
        except Exception as e:
            logger.error(f"Error initiating human handoff: {e}")
            return {
                "success": False,
                "error": "خطأ في التحويل للمختص" if language == "ar" else "Error connecting to specialist"
            }
    
    @tool
    async def detect_language(self, message: str) -> str:
        """
        Detect the language of customer message
        
        Args:
            message: Customer message
            
        Returns:
            Language code (ar/en)
        """
        # Simple language detection based on Arabic characters
        arabic_chars = sum(1 for char in message if '\u0600' <= char <= '\u06FF')
        total_chars = len([char for char in message if char.isalpha()])
        
        if total_chars == 0:
            return "en"  # Default to English if no letters
            
        arabic_ratio = arabic_chars / total_chars
        
        return "ar" if arabic_ratio > 0.3 else "en"
    
    async def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """
        Process incoming customer message
        
        Args:
            message: Customer message
            session_id: Session identifier
            
        Returns:
            Response dictionary
        """
        try:
            # Detect language
            language = await self.detect_language(message)
            
            # Get or create conversation state
            if session_id not in self.conversation_state:
                self.conversation_state[session_id] = {
                    "language": language,
                    "stage": "greeting",
                    "customer_info": {},
                    "messages": []
                }
            
            state = self.conversation_state[session_id]
            state["messages"].append({"role": "user", "content": message})
            
            # Generate response using Gemini
            response = await self._generate_response(message, state)
            
            state["messages"].append({"role": "assistant", "content": response["content"]})
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "content": "عذراً، حدث خطأ. يرجى المحاولة مرة أخرى." if language == "ar" else "Sorry, an error occurred. Please try again.",
                "language": language,
                "actions": []
            }
    
    async def _generate_response(self, message: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate contextual response based on conversation state"""
        
        language = state["language"]
        stage = state["stage"]
        customer_info = state["customer_info"]
        
        # Build context for Gemini
        context = f"""
        Language: {language}
        Stage: {stage}
        Customer Info: {json.dumps(customer_info, ensure_ascii=False)}
        Message: {message}
        """
        
        # Generate response using the model
        response = await self.model.generate_content_async(
            f"{self.system_prompt}\n\nContext: {context}\n\nRespond appropriately:"
        )
        
        # Parse response and determine next actions
        content = response.text
        actions = self._determine_actions(message, state)
        
        return {
            "content": content,
            "language": language,
            "actions": actions,
            "stage": stage
        }
    
    def _determine_actions(self, message: str, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Determine what actions to take based on the message"""
        actions = []
        
        # Check if customer wants to talk to human
        human_keywords_ar = ["إنسان", "شخص", "موظف", "مختص", "استشاري"]
        human_keywords_en = ["human", "person", "agent", "specialist", "consultant"]
        
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in human_keywords_ar + human_keywords_en):
            actions.append({
                "type": "offer_human_handoff",
                "priority": "high"
            })
        
        # Check if customer provided contact information
        if "@" in message and "." in message:
            actions.append({
                "type": "collect_email",
                "value": self._extract_email(message)
            })
        
        # Check for phone number patterns
        phone_pattern = r'(\+966|0966|966)?[\s-]?5[0-9]{8}'
        import re
        if re.search(phone_pattern, message):
            actions.append({
                "type": "collect_phone",
                "value": re.search(phone_pattern, message).group()
            })
        
        return actions
    
    def _extract_email(self, message: str) -> Optional[str]:
        """Extract email from message"""
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, message)
        return match.group() if match else None