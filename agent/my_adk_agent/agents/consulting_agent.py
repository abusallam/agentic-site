"""
Consulting Agent - Pydantic AI Framework
Handles high-level consulting requests with LiveKit integration for human handoff
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import logging

# Import Pydantic AI with fallback
try:
    from pydantic_ai import Agent, RunContext
    from pydantic_ai.models import KnownModelName
except ImportError:
    # Mock implementations for development
    class Agent:
        def __init__(self, **kwargs): pass
        async def run(self, prompt, deps=None): 
            return type('MockResult', (), {
                'data': type('MockData', (), {
                    'consultation_id': 'mock_id',
                    'recommendations': ['Mock recommendation'],
                    'proposed_solutions': [{'solution': 'Mock solution'}],
                    'estimated_cost': 'Mock cost',
                    'estimated_timeline': 'Mock timeline',
                    'next_steps': ['Mock step'],
                    'requires_human_consultant': False,
                    'livekit_session_url': None
                })()
            })()
    
    RunContext = object
    KnownModelName = type('MockKnownModelName', (), {
        'gemini_2_0_flash_exp': 'gemini-2.0-flash-exp'
    })()

from ..services.supabase_service import SupabaseService
from ..services.livekit_service import LiveKitService
from ..models.consultation import Consultation, ConsultationSession

logger = logging.getLogger(__name__)

class ConsultationRequest(BaseModel):
    """Model for consultation requests"""
    customer_id: str
    consultation_type: str = Field(description="Type of consultation needed")
    business_domain: str = Field(description="Customer's business domain")
    current_challenges: List[str] = Field(description="Current business challenges")
    desired_outcomes: List[str] = Field(description="Desired outcomes from AI implementation")
    budget_range: Optional[str] = Field(description="Budget range for the project")
    timeline: Optional[str] = Field(description="Expected timeline")
    technical_requirements: List[str] = Field(description="Technical requirements")
    language: str = Field(default="ar", description="Preferred language")

class ConsultationResponse(BaseModel):
    """Model for consultation responses"""
    consultation_id: str
    recommendations: List[str]
    proposed_solutions: List[Dict[str, Any]]
    estimated_cost: Optional[str]
    estimated_timeline: Optional[str]
    next_steps: List[str]
    requires_human_consultant: bool
    livekit_session_url: Optional[str] = None

class ConsultingAgentDeps(BaseModel):
    """Dependencies for the consulting agent"""
    supabase: SupabaseService
    livekit: LiveKitService
    config: Dict[str, Any]

class ConsultingAgent:
    """
    Consulting agent using Pydantic AI framework
    - Provides strategic AI consulting advice
    - Analyzes business requirements and challenges
    - Recommends AI solutions and implementation strategies
    - Handles LiveKit integration for human consultant handoff
    - Manages consultation sessions and follow-ups
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.supabase = SupabaseService(config)
        self.livekit = LiveKitService(config)
        
        # Initialize Pydantic AI agent
        self.agent = Agent(
            model=KnownModelName.gemini_2_0_flash_exp,
            deps_type=ConsultingAgentDeps,
            result_type=ConsultationResponse,
            system_prompt=self._get_system_prompt()
        )
        
        # Consultation types and their characteristics
        self.consultation_types = {
            "ai_strategy": {
                "name": "AI Strategy Consultation",
                "name_ar": "استشارة استراتيجية الذكاء الاصطناعي",
                "description": "Comprehensive AI strategy development for your business",
                "description_ar": "تطوير استراتيجية شاملة للذكاء الاصطناعي لأعمالك",
                "duration": "2-3 hours",
                "price_range": "2000-5000 SAR",
                "deliverables": ["AI Roadmap", "Implementation Plan", "ROI Analysis"],
                "requires_human": True
            },
            "feasibility_study": {
                "name": "AI Feasibility Study",
                "name_ar": "دراسة جدوى الذكاء الاصطناعي",
                "description": "Technical and business feasibility analysis for AI projects",
                "description_ar": "تحليل الجدوى الفنية والتجارية لمشاريع الذكاء الاصطناعي",
                "duration": "1-2 weeks",
                "price_range": "3000-8000 SAR",
                "deliverables": ["Feasibility Report", "Technical Architecture", "Cost Analysis"],
                "requires_human": True
            },
            "implementation_support": {
                "name": "Implementation Support",
                "name_ar": "دعم التنفيذ",
                "description": "Hands-on support during AI solution implementation",
                "description_ar": "دعم عملي أثناء تنفيذ حلول الذكاء الاصطناعي",
                "duration": "Ongoing",
                "price_range": "1500-3000 SAR/month",
                "deliverables": ["Implementation Guidance", "Code Reviews", "Training"],
                "requires_human": True
            },
            "ai_audit": {
                "name": "AI Systems Audit",
                "name_ar": "مراجعة أنظمة الذكاء الاصطناعي",
                "description": "Comprehensive audit of existing AI systems and processes",
                "description_ar": "مراجعة شاملة لأنظمة وعمليات الذكاء الاصطناعي الحالية",
                "duration": "1-2 weeks",
                "price_range": "2500-6000 SAR",
                "deliverables": ["Audit Report", "Recommendations", "Improvement Plan"],
                "requires_human": False
            },
            "quick_consultation": {
                "name": "Quick Consultation",
                "name_ar": "استشارة سريعة",
                "description": "Brief consultation for specific AI questions",
                "description_ar": "استشارة مختصرة لأسئلة محددة حول الذكاء الاصطناعي",
                "duration": "30-60 minutes",
                "price_range": "500-1000 SAR",
                "deliverables": ["Consultation Summary", "Action Items"],
                "requires_human": False
            }
        }
    
    def _get_system_prompt(self) -> str:
        return """
        أنت مستشار ذكاء اصطناعي خبير في شركة consulting.sa
        You are an expert AI consultant at consulting.sa
        
        خبرتك تشمل / Your expertise includes:
        - استراتيجية الذكاء الاصطناعي / AI Strategy
        - دراسات الجدوى / Feasibility Studies  
        - تحليل الأعمال / Business Analysis
        - التحول الرقمي / Digital Transformation
        - إدارة المشاريع التقنية / Technical Project Management
        - أخلاقيات الذكاء الاصطناعي / AI Ethics
        
        أنواع الاستشارات المتاحة / Available Consultation Types:
        1. استشارة استراتيجية الذكاء الاصطناعي / AI Strategy Consultation
        2. دراسة جدوى الذكاء الاصطناعي / AI Feasibility Study
        3. دعم التنفيذ / Implementation Support
        4. مراجعة أنظمة الذكاء الاصطناعي / AI Systems Audit
        5. استشارة سريعة / Quick Consultation
        
        مبادئ الاستشارة / Consulting Principles:
        1. فهم احتياجات العميل بعمق / Deeply understand client needs
        2. تقديم حلول عملية وقابلة للتطبيق / Provide practical, actionable solutions
        3. مراعاة الميزانية والجدول الزمني / Consider budget and timeline constraints
        4. التركيز على عائد الاستثمار / Focus on ROI
        5. ضمان الامتثال والأخلاقيات / Ensure compliance and ethics
        6. التواصل الواضح والمفهوم / Clear and understandable communication
        
        عند تقديم الاستشارة / When providing consultation:
        - اطرح أسئلة مفصلة لفهم السياق / Ask detailed questions to understand context
        - قدم توصيات محددة وعملية / Provide specific, actionable recommendations
        - اشرح الفوائد والمخاطر / Explain benefits and risks
        - اقترح خطة تنفيذ واضحة / Suggest clear implementation plan
        - حدد ما إذا كانت هناك حاجة لمستشار بشري / Determine if human consultant is needed
        """
    
    async def analyze_consultation_request(self, request: ConsultationRequest) -> ConsultationResponse:
        """
        Analyze consultation request and provide recommendations
        
        Args:
            request: Consultation request details
            
        Returns:
            Consultation response with recommendations
        """
        try:
            # Create dependencies
            deps = ConsultingAgentDeps(
                supabase=self.supabase,
                livekit=self.livekit,
                config=self.config
            )
            
            # Prepare context for the agent
            context = f"""
            نوع الاستشارة / Consultation Type: {request.consultation_type}
            مجال الأعمال / Business Domain: {request.business_domain}
            التحديات الحالية / Current Challenges: {', '.join(request.current_challenges)}
            النتائج المرغوبة / Desired Outcomes: {', '.join(request.desired_outcomes)}
            نطاق الميزانية / Budget Range: {request.budget_range or 'غير محدد / Not specified'}
            الجدول الزمني / Timeline: {request.timeline or 'غير محدد / Not specified'}
            المتطلبات التقنية / Technical Requirements: {', '.join(request.technical_requirements)}
            اللغة المفضلة / Preferred Language: {request.language}
            
            يرجى تحليل هذا الطلب وتقديم استشارة شاملة
            Please analyze this request and provide comprehensive consultation
            """
            
            # Run the agent
            result = await self.agent.run(context, deps=deps)
            
            # Store consultation in database
            consultation_data = {
                "customer_id": request.customer_id,
                "consultation_type": request.consultation_type,
                "business_domain": request.business_domain,
                "challenges": request.current_challenges,
                "desired_outcomes": request.desired_outcomes,
                "budget_range": request.budget_range,
                "timeline": request.timeline,
                "technical_requirements": request.technical_requirements,
                "language": request.language,
                "status": "analyzed",
                "ai_recommendations": result.data.recommendations,
                "proposed_solutions": result.data.proposed_solutions,
                "estimated_cost": result.data.estimated_cost,
                "estimated_timeline": result.data.estimated_timeline,
                "requires_human_consultant": result.data.requires_human_consultant
            }
            
            consultation = await self.supabase.create_consultation(consultation_data)
            
            # Update result with consultation ID
            result.data.consultation_id = consultation.id
            
            # If human consultant is required, create LiveKit session
            if result.data.requires_human_consultant:
                livekit_session = await self._create_livekit_session(
                    consultation.id,
                    request.customer_id,
                    request.language
                )
                result.data.livekit_session_url = livekit_session.get("room_url")
            
            logger.info(f"Consultation analyzed: {consultation.id} for customer {request.customer_id}")
            
            return result.data
            
        except Exception as e:
            logger.error(f"Error analyzing consultation request: {e}")
            raise
    
    async def _create_livekit_session(self, consultation_id: str, customer_id: str, language: str) -> Dict[str, Any]:
        """Create LiveKit session for human consultant handoff"""
        try:
            room_info = await self.livekit.create_room(
                room_name=f"consultation_{consultation_id}",
                customer_id=customer_id,
                agent_type="human_consultant",
                metadata={
                    "consultation_id": consultation_id,
                    "language": language,
                    "type": "consulting_session"
                }
            )
            
            # Store session info
            session_data = {
                "consultation_id": consultation_id,
                "customer_id": customer_id,
                "room_name": room_info["room_name"],
                "room_url": room_info["room_url"],
                "status": "scheduled",
                "language": language
            }
            
            session = await self.supabase.create_consultation_session(session_data)
            
            logger.info(f"LiveKit session created: {session.id} for consultation {consultation_id}")
            
            return room_info
            
        except Exception as e:
            logger.error(f"Error creating LiveKit session: {e}")
            return {}
    
    async def get_consultation_types(self, language: str = "ar") -> List[Dict[str, Any]]:
        """
        Get available consultation types
        
        Args:
            language: Response language
            
        Returns:
            List of consultation types
        """
        consultation_list = []
        
        for type_id, consultation_type in self.consultation_types.items():
            type_info = {
                "id": type_id,
                "name": consultation_type["name_ar"] if language == "ar" else consultation_type["name"],
                "description": consultation_type["description_ar"] if language == "ar" else consultation_type["description"],
                "duration": consultation_type["duration"],
                "price_range": consultation_type["price_range"],
                "deliverables": consultation_type["deliverables"],
                "requires_human": consultation_type["requires_human"]
            }
            consultation_list.append(type_info)
        
        return consultation_list
    
    async def schedule_consultation(self, consultation_id: str, preferred_time: str, language: str = "ar") -> Dict[str, Any]:
        """
        Schedule a consultation session
        
        Args:
            consultation_id: Consultation identifier
            preferred_time: Customer's preferred time
            language: Response language
            
        Returns:
            Scheduling result
        """
        try:
            # Get consultation details
            consultation = await self.supabase.get_consultation(consultation_id)
            if not consultation:
                return {
                    "success": False,
                    "error": "الاستشارة غير موجودة" if language == "ar" else "Consultation not found"
                }
            
            # Parse preferred time
            try:
                scheduled_time = datetime.fromisoformat(preferred_time)
            except ValueError:
                return {
                    "success": False,
                    "error": "تنسيق الوقت غير صحيح" if language == "ar" else "Invalid time format"
                }
            
            # Check if time is in the future
            if scheduled_time <= datetime.now():
                return {
                    "success": False,
                    "error": "يجب أن يكون الوقت في المستقبل" if language == "ar" else "Time must be in the future"
                }
            
            # Update consultation with scheduled time
            await self.supabase.update_consultation(
                consultation_id,
                {
                    "scheduled_time": scheduled_time,
                    "status": "scheduled"
                }
            )
            
            # Create calendar event (if integration available)
            # await self._create_calendar_event(consultation, scheduled_time)
            
            # Send confirmation (if notification service available)
            # await self._send_confirmation(consultation, scheduled_time, language)
            
            logger.info(f"Consultation scheduled: {consultation_id} for {scheduled_time}")
            
            return {
                "success": True,
                "consultation_id": consultation_id,
                "scheduled_time": scheduled_time.isoformat(),
                "message": "تم جدولة الاستشارة بنجاح" if language == "ar" else "Consultation scheduled successfully",
                "next_steps": "سيتم إرسال رابط الجلسة قبل الموعد بـ 15 دقيقة" if language == "ar" else "Session link will be sent 15 minutes before the appointment"
            }
            
        except Exception as e:
            logger.error(f"Error scheduling consultation: {e}")
            return {
                "success": False,
                "error": "خطأ في جدولة الاستشارة" if language == "ar" else "Error scheduling consultation"
            }
    
    async def get_consultation_status(self, consultation_id: str, language: str = "ar") -> Dict[str, Any]:
        """
        Get consultation status and details
        
        Args:
            consultation_id: Consultation identifier
            language: Response language
            
        Returns:
            Consultation status and details
        """
        try:
            consultation = await self.supabase.get_consultation(consultation_id)
            if not consultation:
                return {
                    "success": False,
                    "error": "الاستشارة غير موجودة" if language == "ar" else "Consultation not found"
                }
            
            # Get associated session if exists
            session = await self.supabase.get_consultation_session_by_consultation(consultation_id)
            
            consultation_info = {
                "id": consultation.id,
                "type": consultation.consultation_type,
                "status": consultation.status,
                "created_at": consultation.created_at.isoformat(),
                "scheduled_time": consultation.scheduled_time.isoformat() if consultation.scheduled_time else None,
                "business_domain": consultation.business_domain,
                "estimated_cost": consultation.estimated_cost,
                "estimated_timeline": consultation.estimated_timeline,
                "requires_human_consultant": consultation.requires_human_consultant
            }
            
            if session:
                consultation_info["session"] = {
                    "id": session.id,
                    "room_url": session.room_url,
                    "status": session.status,
                    "language": session.language
                }
            
            return {
                "success": True,
                "consultation": consultation_info
            }
            
        except Exception as e:
            logger.error(f"Error getting consultation status: {e}")
            return {
                "success": False,
                "error": "خطأ في جلب حالة الاستشارة" if language == "ar" else "Error getting consultation status"
            }
    
    async def process_consultation_message(self, message: str, customer_id: str, language: str = "ar") -> Dict[str, Any]:
        """
        Process consultation-related customer messages
        
        Args:
            message: Customer message
            customer_id: Customer identifier
            language: Customer language
            
        Returns:
            Response dictionary
        """
        try:
            # Analyze message to determine consultation needs
            analysis_prompt = f"""
            تحليل رسالة العميل لتحديد نوع الاستشارة المطلوبة
            Analyze customer message to determine consultation needs
            
            الرسالة / Message: {message}
            اللغة / Language: {language}
            
            حدد / Determine:
            1. نوع الاستشارة المناسب / Appropriate consultation type
            2. مستوى الإلحاح / Urgency level
            3. هل يحتاج مستشار بشري فوراً / Needs immediate human consultant
            4. المعلومات الإضافية المطلوبة / Additional information needed
            
            أجب بصيغة JSON / Respond in JSON format
            """
            
            # Use the agent to analyze the message
            deps = ConsultingAgentDeps(
                supabase=self.supabase,
                livekit=self.livekit,
                config=self.config
            )
            
            # Generate contextual response
            response_prompt = f"""
            رد على العميل بناءً على رسالته حول الاستشارة
            Respond to customer based on their consultation message
            
            الرسالة / Message: {message}
            معرف العميل / Customer ID: {customer_id}
            اللغة / Language: {language}
            
            قدم رداً مفيداً يتضمن / Provide helpful response including:
            1. فهم احتياجاته / Understanding of their needs
            2. اقتراح نوع الاستشارة المناسب / Suggest appropriate consultation type
            3. الخطوات التالية / Next steps
            4. معلومات عن الأسعار والمدة / Information about pricing and duration
            """
            
            result = await self.agent.run(response_prompt, deps=deps)
            
            # Determine actions based on message content
            actions = self._determine_consultation_actions(message, language)
            
            return {
                "content": result.data if hasattr(result, 'data') else str(result),
                "language": language,
                "actions": actions,
                "agent_type": "consulting",
                "consultation_types": await self.get_consultation_types(language)
            }
            
        except Exception as e:
            logger.error(f"Error processing consultation message: {e}")
            return {
                "content": "عذراً، حدث خطأ في معالجة طلب الاستشارة" if language == "ar" else "Sorry, an error occurred processing your consultation request",
                "language": language,
                "actions": [],
                "agent_type": "consulting"
            }
    
    def _determine_consultation_actions(self, message: str, language: str) -> List[Dict[str, Any]]:
        """Determine consultation-specific actions based on message"""
        actions = []
        message_lower = message.lower()
        
        # Check for immediate consultation requests
        urgent_keywords_ar = ["عاجل", "فوري", "سريع", "الآن", "اليوم"]
        urgent_keywords_en = ["urgent", "immediate", "quick", "now", "today"]
        
        if any(keyword in message_lower for keyword in urgent_keywords_ar + urgent_keywords_en):
            actions.append({
                "type": "offer_immediate_consultation",
                "priority": "high"
            })
        
        # Check for specific consultation type mentions
        for type_id, consultation_type in self.consultation_types.items():
            type_keywords = [consultation_type["name"].lower(), consultation_type["name_ar"]]
            if any(keyword in message_lower for keyword in type_keywords):
                actions.append({
                    "type": "suggest_consultation_type",
                    "consultation_type": type_id,
                    "priority": "medium"
                })
                break
        
        # Check for scheduling requests
        schedule_keywords_ar = ["موعد", "جدولة", "حجز", "وقت"]
        schedule_keywords_en = ["appointment", "schedule", "book", "time"]
        
        if any(keyword in message_lower for keyword in schedule_keywords_ar + schedule_keywords_en):
            actions.append({
                "type": "offer_scheduling",
                "priority": "high"
            })
        
        # Check for human consultant requests
        human_keywords_ar = ["مستشار", "خبير", "شخص", "إنسان"]
        human_keywords_en = ["consultant", "expert", "person", "human"]
        
        if any(keyword in message_lower for keyword in human_keywords_ar + human_keywords_en):
            actions.append({
                "type": "offer_human_consultant",
                "priority": "high"
            })
        
        return actions