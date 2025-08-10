"""
Initial Authentication Agent - First contact for new customers
Handles Arabic/English communication and Saudi WhatsApp authentication
"""
from typing import Dict, Any, Optional
from .base_agent import BaseAgent, AgentResponse, AgentConfig
from dataclasses import dataclass
import logging
import re
import random
import string
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class AuthenticationSession:
    """Authentication session data"""
    session_id: str
    phone_number: str
    verification_code: str
    email: Optional[str] = None
    name: Optional[str] = None
    language: str = "ar"  # Default Arabic
    initial_request: str = ""
    service_interest: str = ""
    status: str = "pending"  # pending, verified, completed
    created_at: datetime = None
    expires_at: datetime = None


class InitialAuthAgent(BaseAgent):
    """Initial authentication agent for new customers"""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.auth_sessions = {}  # In production, use Redis/Database
        self.composio_api_key = "ak_MQM5jiai1Vjkwel-lL7N"
        self.current_language = "ar"  # Default Arabic
        
    def get_system_prompt(self) -> str:
        """System prompt for initial authentication agent"""
        return """
        أنت وكيل المصادقة الأولي لمنصة الاستشارات الذكية. مهمتك:

        1. الترحيب بالعملاء الجدد باللغة العربية (افتراضي)
        2. التحقق من هوية العملاء عبر رقم الواتساب السعودي
        3. جمع المعلومات الأساسية (الاسم، الإيميل، نوع الخدمة المطلوبة)
        4. توجيه العملاء للخدمة المناسبة

        قواعد مهمة:
        - ابدأ دائماً بـ "السلام عليكم ورحمة الله وبركاته"
        - تحدث فقط عن خدماتنا الثلاث: الحلول السريعة، التطوير المخصص، الاستشارات
        - لا تذكر الأدوات التقنية التي نستخدمها
        - كن مختصراً ولا تتوسع في الإجابات
        - إذا طلب العميل الإنجليزية، انتقل للإنجليزية
        - تأكد من أن رقم الواتساب سعودي (يبدأ بـ 009665)

        خدماتنا:
        1. الحلول السريعة: أتمتة سريعة وشات بوت جاهز
        2. التطوير المخصص: تطوير برمجي متخصص حسب الطلب  
        3. الاستشارات: استشارات تقنية وتخطيط مشاريع

        You are the Initial Authentication Agent for our AI consulting platform. Your mission:

        1. Welcome new customers in Arabic (default)
        2. Verify customer identity via Saudi WhatsApp number
        3. Collect basic information (name, email, service type needed)
        4. Route customers to appropriate service

        Important rules:
        - Always start with "السلام عليكم ورحمة الله وبركاته" (Peace be upon you)
        - Only talk about our three services: Fast Solutions, Custom Development, Consulting
        - Don't mention technical tools we use
        - Be concise and don't elaborate unnecessarily
        - If customer requests English, switch to English
        - Ensure WhatsApp number is Saudi (starts with 009665)

        Our services:
        1. Fast Solutions: Quick automation and ready chatbots
        2. Custom Development: Specialized software development on demand
        3. Consulting: Technical consulting and project planning
        """
    
    def process_message(self, message: str, context: Dict[str, Any] = None) -> AgentResponse:
        """Process customer message with authentication flow"""
        self.add_to_history("user", message)
        
        session_id = context.get("session_id") if context else None
        session = self.auth_sessions.get(session_id) if session_id else None
        
        # Detect language preference
        if self._is_english_request(message):
            self.current_language = "en"
        elif self._is_arabic_request(message):
            self.current_language = "ar"
        
        # Handle different authentication stages
        if not session:
            response = self._handle_initial_contact(message, session_id)
        elif session.status == "pending" and not session.phone_number:
            response = self._handle_phone_collection(message, session)
        elif session.status == "pending" and session.phone_number and not session.verification_code:
            response = self._handle_verification_code(message, session)
        elif session.status == "verified" and not session.name:
            response = self._handle_name_collection(message, session)
        elif session.status == "verified" and not session.email:
            response = self._handle_email_collection(message, session)
        elif session.status == "verified" and not session.service_interest:
            response = self._handle_service_selection(message, session)
        else:
            response = self._handle_completion(session)
        
        self.add_to_history("assistant", response.message)
        return response
    
    def _handle_initial_contact(self, message: str, session_id: str) -> AgentResponse:
        """Handle initial customer contact"""
        # Create new session
        session = AuthenticationSession(
            session_id=session_id or f"auth_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            phone_number="",
            verification_code="",
            language=self.current_language,
            initial_request=message,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(minutes=30)
        )
        
        self.auth_sessions[session.session_id] = session
        
        if self.current_language == "ar":
            welcome_message = (
                "السلام عليكم ورحمة الله وبركاته 🌟\n\n"
                "أهلاً وسهلاً بك في منصة الاستشارات الذكية!\n\n"
                "نحن نقدم ثلاث خدمات رئيسية:\n"
                "🚀 الحلول السريعة - أتمتة وشات بوت جاهز\n"
                "⚡ التطوير المخصص - برمجة متخصصة حسب طلبك\n"
                "📋 الاستشارات - استشارات تقنية وتخطيط مشاريع\n\n"
                "للمتابعة، أحتاج رقم الواتساب السعودي الخاص بك للتحقق من الهوية.\n"
                "مثال: 009665xxxxxxxx\n\n"
                "💬 إذا كنت تفضل الإنجليزية، اكتب 'English'"
            )
        else:
            welcome_message = (
                "Peace be upon you! 🌟\n\n"
                "Welcome to our AI Consulting Platform!\n\n"
                "We offer three main services:\n"
                "🚀 Fast Solutions - Quick automation and ready chatbots\n"
                "⚡ Custom Development - Specialized software development\n"
                "📋 Consulting - Technical consulting and project planning\n\n"
                "To proceed, I need your Saudi WhatsApp number for identity verification.\n"
                "Example: 009665xxxxxxxx\n\n"
                "💬 للعربية، اكتب 'عربي'"
            )
        
        return AgentResponse(
            message=welcome_message,
            confidence=1.0,
            next_action="collect_phone",
            context={
                "session_id": session.session_id,
                "language": self.current_language,
                "stage": "phone_collection"
            }
        )
    
    def _handle_phone_collection(self, message: str, session: AuthenticationSession) -> AgentResponse:
        """Handle phone number collection and validation"""
        phone_number = self._extract_saudi_phone(message)
        
        if not phone_number:
            error_message = (
                "يرجى إدخال رقم واتساب سعودي صحيح يبدأ بـ 009665\n"
                "مثال: 009665xxxxxxxx"
                if self.current_language == "ar" else
                "Please enter a valid Saudi WhatsApp number starting with 009665\n"
                "Example: 009665xxxxxxxx"
            )
            
            return AgentResponse(
                message=error_message,
                confidence=0.8,
                next_action="retry_phone",
                context={"session_id": session.session_id, "stage": "phone_collection"}
            )
        
        # Generate verification code
        verification_code = self._generate_verification_code()
        
        # Update session
        session.phone_number = phone_number
        session.verification_code = verification_code
        
        # Send WhatsApp verification code
        whatsapp_sent = self._send_whatsapp_verification(phone_number, verification_code)
        
        if whatsapp_sent:
            success_message = (
                f"تم إرسال رمز التحقق إلى {phone_number} عبر الواتساب ✅\n\n"
                "يرجى إدخال الرمز المكون من 6 أرقام:"
                if self.current_language == "ar" else
                f"Verification code sent to {phone_number} via WhatsApp ✅\n\n"
                "Please enter the 6-digit code:"
            )
        else:
            error_message = (
                "عذراً، لم نتمكن من إرسال رمز التحقق. يرجى المحاولة مرة أخرى."
                if self.current_language == "ar" else
                "Sorry, we couldn't send the verification code. Please try again."
            )
            return AgentResponse(
                message=error_message,
                confidence=0.7,
                next_action="retry_phone",
                context={"session_id": session.session_id, "stage": "phone_collection"}
            )
        
        return AgentResponse(
            message=success_message,
            confidence=0.9,
            next_action="verify_code",
            context={
                "session_id": session.session_id,
                "stage": "code_verification",
                "phone_number": phone_number
            }
        )
    
    def _handle_verification_code(self, message: str, session: AuthenticationSession) -> AgentResponse:
        """Handle verification code validation"""
        entered_code = re.sub(r'\D', '', message)  # Extract only digits
        
        if entered_code == session.verification_code:
            session.status = "verified"
            
            success_message = (
                "تم التحقق بنجاح! ✅\n\n"
                "الآن، ما اسمك الكريم؟"
                if self.current_language == "ar" else
                "Verification successful! ✅\n\n"
                "Now, what's your name?"
            )
            
            return AgentResponse(
                message=success_message,
                confidence=1.0,
                next_action="collect_name",
                context={
                    "session_id": session.session_id,
                    "stage": "name_collection",
                    "verified": True
                }
            )
        else:
            error_message = (
                "رمز التحقق غير صحيح. يرجى المحاولة مرة أخرى.\n"
                "أو اكتب 'إعادة إرسال' لإرسال رمز جديد."
                if self.current_language == "ar" else
                "Incorrect verification code. Please try again.\n"
                "Or type 'resend' for a new code."
            )
            
            return AgentResponse(
                message=error_message,
                confidence=0.7,
                next_action="retry_verification",
                context={"session_id": session.session_id, "stage": "code_verification"}
            )
    
    def _handle_name_collection(self, message: str, session: AuthenticationSession) -> AgentResponse:
        """Handle name collection"""
        name = message.strip()
        if len(name) < 2:
            error_message = (
                "يرجى إدخال اسم صحيح"
                if self.current_language == "ar" else
                "Please enter a valid name"
            )
            return AgentResponse(
                message=error_message,
                confidence=0.7,
                next_action="retry_name",
                context={"session_id": session.session_id, "stage": "name_collection"}
            )
        
        session.name = name
        
        email_request = (
            f"أهلاً {name}! 👋\n\n"
            "يرجى إدخال بريدك الإلكتروني:"
            if self.current_language == "ar" else
            f"Hello {name}! 👋\n\n"
            "Please enter your email address:"
        )
        
        return AgentResponse(
            message=email_request,
            confidence=0.9,
            next_action="collect_email",
            context={
                "session_id": session.session_id,
                "stage": "email_collection",
                "name": name
            }
        )
    
    def _handle_email_collection(self, message: str, session: AuthenticationSession) -> AgentResponse:
        """Handle email collection and validation"""
        email = self._extract_email(message)
        
        if not email:
            error_message = (
                "يرجى إدخال بريد إلكتروني صحيح\n"
                "مثال: example@gmail.com"
                if self.current_language == "ar" else
                "Please enter a valid email address\n"
                "Example: example@gmail.com"
            )
            return AgentResponse(
                message=error_message,
                confidence=0.7,
                next_action="retry_email",
                context={"session_id": session.session_id, "stage": "email_collection"}
            )
        
        session.email = email
        
        service_selection = (
            "ممتاز! الآن أخبرني، أي من خدماتنا تهمك؟\n\n"
            "🚀 الحلول السريعة - أتمتة وشات بوت جاهز\n"
            "⚡ التطوير المخصص - برمجة متخصصة حسب طلبك\n"
            "📋 الاستشارات - استشارات تقنية وتخطيط مشاريع\n\n"
            "اكتب رقم الخدمة أو اسمها:"
            if self.current_language == "ar" else
            "Excellent! Now tell me, which of our services interests you?\n\n"
            "🚀 Fast Solutions - Quick automation and ready chatbots\n"
            "⚡ Custom Development - Specialized software development\n"
            "📋 Consulting - Technical consulting and project planning\n\n"
            "Type the service number or name:"
        )
        
        return AgentResponse(
            message=service_selection,
            confidence=0.9,
            next_action="select_service",
            context={
                "session_id": session.session_id,
                "stage": "service_selection",
                "email": email
            }
        )
    
    def _handle_service_selection(self, message: str, session: AuthenticationSession) -> AgentResponse:
        """Handle service selection"""
        service_type = self._determine_service_type(message)
        
        if not service_type:
            error_message = (
                "يرجى اختيار إحدى الخدمات:\n"
                "1 - الحلول السريعة\n"
                "2 - التطوير المخصص\n"
                "3 - الاستشارات"
                if self.current_language == "ar" else
                "Please choose one of the services:\n"
                "1 - Fast Solutions\n"
                "2 - Custom Development\n"
                "3 - Consulting"
            )
            return AgentResponse(
                message=error_message,
                confidence=0.7,
                next_action="retry_service",
                context={"session_id": session.session_id, "stage": "service_selection"}
            )
        
        session.service_interest = service_type
        session.status = "completed"
        
        return self._handle_completion(session)
    
    def _handle_completion(self, session: AuthenticationSession) -> AgentResponse:
        """Handle authentication completion and routing"""
        # Save customer to database
        customer_data = {
            "name": session.name,
            "phone": session.phone_number,
            "email": session.email,
            "service_interest": session.service_interest,
            "language": session.language,
            "initial_request": session.initial_request,
            "created_at": session.created_at
        }
        
        # Create customer record (mock - implement with actual database)
        customer_id = self._create_customer_record(customer_data)
        
        service_names = {
            "fast_solution": "الحلول السريعة" if self.current_language == "ar" else "Fast Solutions",
            "custom_development": "التطوير المخصص" if self.current_language == "ar" else "Custom Development",
            "consulting": "الاستشارات" if self.current_language == "ar" else "Consulting"
        }
        
        completion_message = (
            f"مرحباً بك {session.name}! 🎉\n\n"
            f"تم تسجيلك بنجاح في خدمة {service_names.get(session.service_interest, 'غير محدد')}\n\n"
            f"سيتم توجيهك الآن إلى الوكيل المختص الذي سيساعدك في:\n"
            f"• فهم احتياجاتك بالتفصيل\n"
            f"• تقديم الحلول المناسبة\n"
            f"• متابعة مشروعك خطوة بخطوة\n\n"
            f"شكراً لثقتك بنا! 🙏"
            if self.current_language == "ar" else
            f"Welcome {session.name}! 🎉\n\n"
            f"You've been successfully registered for {service_names.get(session.service_interest, 'Unknown')}\n\n"
            f"You'll now be directed to the specialist agent who will help you with:\n"
            f"• Understanding your needs in detail\n"
            f"• Providing suitable solutions\n"
            f"• Following up on your project step by step\n\n"
            f"Thank you for trusting us! 🙏"
        )
        
        return AgentResponse(
            message=completion_message,
            confidence=1.0,
            next_action="route_to_specialist",
            context={
                "customer_id": customer_id,
                "service_type": session.service_interest,
                "language": session.language,
                "authenticated": True,
                "routing_target": self._get_routing_target(session.service_interest)
            }
        )
    
    def _is_english_request(self, message: str) -> bool:
        """Check if message requests English language"""
        english_indicators = ["english", "en", "انجليزي", "انكليزي"]
        return any(indicator in message.lower() for indicator in english_indicators)
    
    def _is_arabic_request(self, message: str) -> bool:
        """Check if message requests Arabic language"""
        arabic_indicators = ["arabic", "ar", "عربي", "عربية"]
        return any(indicator in message.lower() for indicator in arabic_indicators)
    
    def _extract_saudi_phone(self, message: str) -> Optional[str]:
        """Extract and validate Saudi phone number"""
        # Remove all non-digits
        digits = re.sub(r'\D', '', message)
        
        # Check for Saudi number patterns
        patterns = [
            r'^009665\d{8}$',  # 009665xxxxxxxx
            r'^9665\d{8}$',    # 9665xxxxxxxx
            r'^05\d{8}$'       # 05xxxxxxxx (local format)
        ]
        
        for pattern in patterns:
            if re.match(pattern, digits):
                # Normalize to international format
                if digits.startswith('009665'):
                    return digits
                elif digits.startswith('9665'):
                    return '00' + digits
                elif digits.startswith('05'):
                    return '009665' + digits[2:]
        
        return None
    
    def _extract_email(self, message: str) -> Optional[str]:
        """Extract and validate email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, message)
        return match.group(0) if match else None
    
    def _generate_verification_code(self) -> str:
        """Generate 6-digit verification code"""
        return ''.join(random.choices(string.digits, k=6))
    
    def _send_whatsapp_verification(self, phone_number: str, code: str) -> bool:
        """Send verification code via WhatsApp using Composio"""
        try:
            # Use Composio WhatsApp integration
            headers = {
                'Authorization': f'Bearer {self.composio_api_key}',
                'Content-Type': 'application/json'
            }
            
            message_text = (
                f"رمز التحقق الخاص بك: {code}\n"
                f"صالح لمدة 10 دقائق\n"
                f"منصة الاستشارات الذكية"
                if self.current_language == "ar" else
                f"Your verification code: {code}\n"
                f"Valid for 10 minutes\n"
                f"AI Consulting Platform"
            )
            
            payload = {
                'app': 'whatsapp',
                'action': 'send_message',
                'params': {
                    'to': phone_number,
                    'message': message_text
                }
            }
            
            # Mock successful send - implement actual Composio API call
            logger.info(f"Sending WhatsApp verification to {phone_number}: {code}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send WhatsApp verification: {e}")
            return False
    
    def _determine_service_type(self, message: str) -> Optional[str]:
        """Determine service type from user message"""
        message_lower = message.lower()
        
        # Arabic keywords
        if any(word in message_lower for word in ["1", "سريع", "أتمتة", "شات بوت", "جاهز"]):
            return "fast_solution"
        elif any(word in message_lower for word in ["2", "مخصص", "تطوير", "برمجة", "تصميم"]):
            return "custom_development"
        elif any(word in message_lower for word in ["3", "استشار", "تخطيط", "مشاريع"]):
            return "consulting"
        
        # English keywords
        elif any(word in message_lower for word in ["fast", "quick", "automation", "chatbot", "ready"]):
            return "fast_solution"
        elif any(word in message_lower for word in ["custom", "development", "programming", "coding"]):
            return "custom_development"
        elif any(word in message_lower for word in ["consulting", "consultation", "planning", "strategy"]):
            return "consulting"
        
        return None
    
    def _create_customer_record(self, customer_data: Dict[str, Any]) -> str:
        """Create customer record in database"""
        # Mock implementation - replace with actual database integration
        customer_id = f"cust_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Created customer record: {customer_id} - {customer_data}")
        return customer_id
    
    def _get_routing_target(self, service_type: str) -> str:
        """Get routing target based on service type"""
        routing_map = {
            "fast_solution": "workflow_agent",
            "custom_development": "professional_agent",
            "consulting": "consulting_agent"
        }
        return routing_map.get(service_type, "welcoming_agent")