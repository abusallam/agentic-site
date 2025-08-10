"""
Consulting Agent - Calendar scheduling and research coordination with BMad-Method integration
Handles consultation appointments, knowledge gathering, and comprehensive project planning
"""
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentResponse, AgentConfig
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import json
import subprocess
import os

logger = logging.getLogger(__name__)


@dataclass
class CalendarEvent:
    """Calendar event data structure"""
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    attendees: List[str]
    location: Optional[str] = None
    meeting_type: str = "consultation"  # consultation, follow_up, presentation


@dataclass
class ResearchReport:
    """Research report data structure"""
    topic: str
    summary: str
    key_findings: List[str]
    sources: List[str]
    recommendations: List[str]
    created_at: datetime


class ConsultingAgent(BaseAgent):
    """Agent for consultation scheduling and research with BMad-Method integration"""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.calendar_manager = CalendarManager()
        self.research_engine = ResearchEngine()
        self.document_generator = DocumentGenerator()
        self.bmad_engine = BMadMethodEngine()
        self.consultation_stage = "initial"  # initial, scheduling, research, preparation, bmad_planning
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the consulting agent"""
        return """
        You are a Consulting Agent specializing in strategic consultation and research services.
        
        Your capabilities include:
        1. Calendar management and appointment scheduling
        2. Web research and knowledge gathering
        3. Document preparation for consultations
        4. Client requirement analysis and preparation
        5. Meeting coordination and follow-up
        
        Your approach:
        - Professional and consultative communication
        - Thorough preparation for each consultation
        - Proactive research based on client needs
        - Clear scheduling and coordination
        - Comprehensive documentation
        
        Always ensure consultations are well-prepared with relevant research and documentation.
        """
    
    def process_message(self, message: str, context: Dict[str, Any] = None) -> AgentResponse:
        """Process consultation request"""
        self.add_to_history("user", message)
        
        # Determine consultation stage and process accordingly
        if self.consultation_stage == "initial":
            response = self._handle_initial_consultation_request(message, context)
        elif self.consultation_stage == "scheduling":
            response = self._handle_scheduling_request(message)
        elif self.consultation_stage == "research":
            response = self._handle_research_discussion(message)
        elif self.consultation_stage == "preparation":
            response = self._handle_preparation_confirmation(message)
        else:
            response = self._handle_general_consultation_inquiry(message)
        
        self.add_to_history("assistant", response.message)
        return response
    
    def _handle_initial_consultation_request(self, message: str, context: Dict[str, Any] = None) -> AgentResponse:
        """Handle initial consultation request"""
        # Analyze consultation requirements
        consultation_analysis = self._analyze_consultation_needs(message)
        
        # Generate appropriate response
        response_message = self._generate_consultation_response(consultation_analysis)
        
        # Move to scheduling stage
        self.consultation_stage = "scheduling"
        
        return AgentResponse(
            message=response_message,
            confidence=0.9,
            next_action="schedule_consultation",
            context={
                "consultation_type": consultation_analysis["type"],
                "requirements": consultation_analysis["requirements"],
                "urgency": consultation_analysis["urgency"]
            }
        )
    
    def _handle_scheduling_request(self, message: str) -> AgentResponse:
        """Handle scheduling and calendar coordination"""
        # Extract scheduling preferences
        scheduling_info = self._extract_scheduling_preferences(message)
        
        # Check availability and suggest times
        available_slots = self.calendar_manager.get_available_slots(
            scheduling_info.get("preferred_dates", []),
            scheduling_info.get("duration", 60)
        )
        
        if available_slots:
            # Move to research stage
            self.consultation_stage = "research"
            response_message = self._generate_scheduling_confirmation(available_slots)
            next_action = "confirm_appointment"
        else:
            response_message = self._generate_alternative_scheduling_options()
            next_action = "reschedule"
        
        return AgentResponse(
            message=response_message,
            confidence=0.85,
            next_action=next_action,
            context={
                "scheduling_info": scheduling_info,
                "available_slots": available_slots
            }
        )
    
    def _handle_research_discussion(self, message: str) -> AgentResponse:
        """Handle research requirements discussion"""
        # Extract research topics from message
        research_topics = self._extract_research_topics(message)
        
        # Initiate research process
        research_plan = self._create_research_plan(research_topics)
        
        # Generate response about research preparation
        response_message = self._generate_research_response(research_plan)
        
        # Move to preparation stage
        self.consultation_stage = "preparation"
        
        return AgentResponse(
            message=response_message,
            confidence=0.9,
            next_action="conduct_research",
            context={
                "research_topics": research_topics,
                "research_plan": research_plan
            }
        )
    
    def schedule_consultation(self, customer_info: Dict[str, Any]) -> CalendarEvent:
        """Schedule consultation appointment"""
        return self.calendar_manager.create_event(
            title=f"Consultation - {customer_info.get('name', 'Client')}",
            description=f"Strategic consultation for {customer_info.get('topic', 'business requirements')}",
            start_time=customer_info.get("preferred_time"),
            duration=customer_info.get("duration", 60),
            attendees=[customer_info.get("email")]
        )
    
    def conduct_research(self, customer_requirements: str) -> ResearchReport:
        """Conduct web research based on customer requirements"""
        research_topics = self._extract_research_topics(customer_requirements)
        return self.research_engine.research(research_topics)
    
    def _analyze_consultation_needs(self, message: str) -> Dict[str, Any]:
        """Analyze consultation requirements from message"""
        message_lower = message.lower()
        
        analysis = {
            "type": "general",
            "requirements": [],
            "urgency": "normal",
            "duration": 60,
            "preparation_needed": True
        }
        
        # Determine consultation type
        if any(word in message_lower for word in ["strategy", "strategic", "planning"]):
            analysis["type"] = "strategic_planning"
        elif any(word in message_lower for word in ["technical", "technology", "implementation"]):
            analysis["type"] = "technical_consultation"
        elif any(word in message_lower for word in ["business", "process", "workflow"]):
            analysis["type"] = "business_consultation"
        elif any(word in message_lower for word in ["research", "analysis", "market"]):
            analysis["type"] = "research_consultation"
        
        # Extract requirements
        requirement_keywords = [
            "need", "want", "require", "looking for", "help with", "advice on"
        ]
        
        for keyword in requirement_keywords:
            if keyword in message_lower:
                # Extract text after the keyword
                start_idx = message_lower.find(keyword)
                requirement_text = message[start_idx:start_idx + 100]  # Get next 100 chars
                analysis["requirements"].append(requirement_text)
        
        # Determine urgency
        if any(word in message_lower for word in ["urgent", "asap", "immediately"]):
            analysis["urgency"] = "urgent"
        elif any(word in message_lower for word in ["soon", "quickly", "fast"]):
            analysis["urgency"] = "high"
        
        return analysis
    
    def _generate_consultation_response(self, analysis: Dict[str, Any]) -> str:
        """Generate appropriate consultation response"""
        consultation_type = analysis["type"].replace("_", " ").title()
        
        base_response = (
            f"I'd be happy to help you with {consultation_type.lower()}. "
            f"Based on your message, I can see this is an important topic that would benefit "
            f"from a dedicated consultation session.\n\n"
        )
        
        if analysis["type"] == "strategic_planning":
            specific_response = (
                "For strategic planning consultations, I typically prepare comprehensive "
                "market research, competitive analysis, and strategic recommendations. "
            )
        elif analysis["type"] == "technical_consultation":
            specific_response = (
                "For technical consultations, I'll research the latest technologies, "
                "best practices, and implementation strategies relevant to your needs. "
            )
        else:
            specific_response = (
                "I'll conduct thorough research on your specific requirements and "
                "prepare detailed insights and recommendations. "
            )
        
        scheduling_prompt = (
            "\n\nTo schedule your consultation:\n"
            "1. What days/times work best for you?\n"
            "2. How long would you like the session to be? (typically 60-90 minutes)\n"
            "3. Would you prefer video call, phone, or in-person meeting?\n"
            "4. Are there any specific topics you'd like me to research beforehand?"
        )
        
        return base_response + specific_response + scheduling_prompt
    
    def _extract_scheduling_preferences(self, message: str) -> Dict[str, Any]:
        """Extract scheduling preferences from message"""
        preferences = {
            "preferred_dates": [],
            "preferred_times": [],
            "duration": 60,
            "meeting_type": "video_call"
        }
        
        # Extract time preferences (simplified)
        message_lower = message.lower()
        
        if "morning" in message_lower:
            preferences["preferred_times"].append("morning")
        if "afternoon" in message_lower:
            preferences["preferred_times"].append("afternoon")
        if "evening" in message_lower:
            preferences["preferred_times"].append("evening")
        
        # Extract duration
        if "90" in message or "hour and half" in message_lower:
            preferences["duration"] = 90
        elif "30" in message or "half hour" in message_lower:
            preferences["duration"] = 30
        elif "120" in message or "two hour" in message_lower:
            preferences["duration"] = 120
        
        return preferences
    
    def _extract_research_topics(self, message: str) -> List[str]:
        """Extract research topics from message"""
        # This would use NLP to extract topics
        # For now, using simple keyword extraction
        topics = []
        
        # Common research topic indicators
        topic_indicators = [
            "research", "analyze", "study", "investigate", "explore",
            "market", "competition", "trends", "best practices", "solutions"
        ]
        
        message_lower = message.lower()
        for indicator in topic_indicators:
            if indicator in message_lower:
                # Extract surrounding context as topic
                start_idx = message_lower.find(indicator)
                topic_context = message[max(0, start_idx-20):start_idx+50]
                topics.append(topic_context.strip())
        
        return topics if topics else ["general business consultation"]
    
    def _create_research_plan(self, topics: List[str]) -> Dict[str, Any]:
        """Create research plan based on topics"""
        return {
            "topics": topics,
            "research_areas": [
                "Market analysis",
                "Competitive landscape",
                "Best practices",
                "Technology trends",
                "Implementation strategies"
            ],
            "estimated_time": "2-3 hours",
            "deliverables": [
                "Research summary document",
                "Key findings presentation",
                "Recommendations report"
            ]
        }


class CalendarManager:
    """Manages calendar operations and scheduling"""
    
    def get_available_slots(self, preferred_dates: List[str], duration: int) -> List[Dict[str, Any]]:
        """Get available time slots"""
        # Mock implementation - would integrate with actual calendar system
        return [
            {
                "date": "2024-01-15",
                "time": "10:00 AM",
                "duration": duration,
                "timezone": "UTC"
            },
            {
                "date": "2024-01-15", 
                "time": "2:00 PM",
                "duration": duration,
                "timezone": "UTC"
            }
        ]
    
    def create_event(self, title: str, description: str, start_time: datetime, 
                    duration: int, attendees: List[str]) -> CalendarEvent:
        """Create calendar event"""
        end_time = start_time + timedelta(minutes=duration)
        
        return CalendarEvent(
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            attendees=attendees
        )


class ResearchEngine:
    """Handles web research and knowledge gathering"""
    
    def research(self, topics: List[str]) -> ResearchReport:
        """Conduct research on specified topics"""
        # Mock implementation - would integrate with actual research tools
        return ResearchReport(
            topic=", ".join(topics),
            summary="Research summary would be generated here",
            key_findings=["Finding 1", "Finding 2", "Finding 3"],
            sources=["Source 1", "Source 2", "Source 3"],
            recommendations=["Recommendation 1", "Recommendation 2"],
            created_at=datetime.utcnow()
        )


class DocumentGenerator:
    """Generates consultation documents and reports"""
    
    def generate_consultation_prep(self, research: ResearchReport, 
                                 customer_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate consultation preparation document"""
        return {
            "document_type": "consultation_prep",
            "customer": customer_info,
            "research": research,
            "agenda": self._create_agenda(research),
            "created_at": datetime.utcnow()
        }
    
    def _create_agenda(self, research: ResearchReport) -> List[str]:
        """Create consultation agenda based on research"""
        return [
            "Introduction and objectives",
            "Current situation analysis", 
            "Research findings presentation",
            "Recommendations discussion",
            "Next steps and action items"
        ]
    def 
get_system_prompt(self) -> str:
        """Enhanced system prompt for consulting agent with BMad-Method integration"""
        return """
        You are an advanced Consulting Agent specializing in strategic consultation, research, and comprehensive project planning using the BMad-Method framework.
        
        Your enhanced capabilities include:
        1. Calendar management and appointment scheduling
        2. Web research and knowledge gathering
        3. BMad-Method project planning and brainstorming
        4. Agile development consultation using BMad framework
        5. Comprehensive documentation and requirement analysis
        6. Long-term consultation project management
        
        BMad-Method Integration Powers:
        - Agentic Planning with Analyst, PM, and Architect agents
        - Context-Engineered Development workflows
        - PRD (Product Requirements Document) creation
        - Architecture document generation
        - Scrum Master and Development story creation
        - Full-stack agile AI team coordination
        
        Your consultation process:
        1. Initial consultation and requirement gathering
        2. Calendar scheduling and meeting coordination
        3. Research and knowledge gathering
        4. BMad-Method planning session (for development projects)
        5. Comprehensive documentation and deliverable preparation
        6. Long-term project support and follow-up
        
        You act as a secretary and brainstorming partner for consultants, providing all the tools and capabilities needed for successful project planning and execution.
        """
    
    def _handle_preparation_confirmation(self, message: str) -> AgentResponse:
        """Handle preparation confirmation and BMad-Method integration"""
        message_lower = message.lower()
        
        # Check if this is a development/technical project requiring BMad-Method
        if any(word in message_lower for word in ["development", "software", "app", "system", "technical", "coding"]):
            # Move to BMad planning stage
            self.consultation_stage = "bmad_planning"
            response_message = self._initiate_bmad_planning()
            next_action = "start_bmad_planning"
        else:
            # Standard consultation preparation
            response_message = self._generate_standard_preparation_response()
            next_action = "finalize_consultation_prep"
        
        return AgentResponse(
            message=response_message,
            confidence=0.9,
            next_action=next_action,
            context={
                "preparation_type": "bmad_planning" if "bmad_planning" in next_action else "standard",
                "consultation_ready": True
            }
        )
    
    def _initiate_bmad_planning(self) -> str:
        """Initiate BMad-Method planning process"""
        return (
            "Excellent! I can see this is a development project that would benefit from our comprehensive BMad-Method planning approach.\n\n"
            "BMad-Method provides a complete Agentic Agile framework with:\n"
            "• **Analyst Agent**: Requirements gathering and user story creation\n"
            "• **PM Agent**: Project management and timeline planning\n"
            "• **Architect Agent**: Technical architecture and system design\n"
            "• **Scrum Master**: Development workflow and story management\n"
            "• **Dev Agent**: Implementation with full context understanding\n\n"
            "I'll prepare a comprehensive planning session that includes:\n"
            "1. **PRD Creation**: Detailed Product Requirements Document\n"
            "2. **Architecture Planning**: Technical system design\n"
            "3. **Development Workflow**: Agile story-driven development\n"
            "4. **Implementation Roadmap**: Step-by-step development plan\n\n"
            "This approach ensures your project has solid foundations and clear implementation paths. "
            "Would you like me to start with the Analyst phase to gather detailed requirements, or do you have specific areas you'd like to focus on first?"
        )
    
    def _generate_standard_preparation_response(self) -> str:
        """Generate standard consultation preparation response"""
        return (
            "Perfect! I have everything I need to prepare for our consultation.\n\n"
            "**Consultation Preparation Includes:**\n"
            "• Comprehensive research on your specific requirements\n"
            "• Market analysis and competitive landscape review\n"
            "• Best practices and industry trends research\n"
            "• Customized recommendations and strategic insights\n"
            "• Detailed consultation agenda and materials\n\n"
            "I'll have all materials prepared 24 hours before our scheduled meeting. "
            "You'll receive a consultation preparation package that includes:\n"
            "1. Research summary document\n"
            "2. Key findings and insights\n"
            "3. Strategic recommendations\n"
            "4. Meeting agenda and discussion points\n\n"
            "Is there anything specific you'd like me to emphasize in my research and preparation?"
        )
    
    def start_bmad_planning_session(self, project_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Start BMad-Method planning session"""
        planning_session = {
            "session_id": f"bmad_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "project_name": project_requirements.get("name", "Consultation Project"),
            "client_info": project_requirements.get("client_info", {}),
            "planning_phases": [
                "analyst_phase",
                "pm_phase", 
                "architect_phase",
                "scrum_master_phase"
            ],
            "current_phase": "analyst_phase",
            "deliverables": {
                "prd": None,
                "architecture": None,
                "user_stories": [],
                "development_plan": None
            },
            "bmad_agents": self._initialize_bmad_agents()
        }
        
        return planning_session
    
    def _initialize_bmad_agents(self) -> Dict[str, Any]:
        """Initialize BMad-Method agents"""
        return {
            "analyst": {
                "role": "Requirements Analysis and User Story Creation",
                "capabilities": [
                    "Stakeholder interview simulation",
                    "User persona development",
                    "Feature prioritization",
                    "Acceptance criteria definition"
                ],
                "status": "ready"
            },
            "pm": {
                "role": "Project Management and Planning",
                "capabilities": [
                    "Timeline estimation",
                    "Resource planning",
                    "Risk assessment",
                    "Milestone definition"
                ],
                "status": "ready"
            },
            "architect": {
                "role": "Technical Architecture and System Design",
                "capabilities": [
                    "System architecture design",
                    "Technology stack recommendations",
                    "Database design",
                    "API specification"
                ],
                "status": "ready"
            },
            "scrum_master": {
                "role": "Agile Workflow and Story Management",
                "capabilities": [
                    "Sprint planning",
                    "Story breakdown",
                    "Development workflow design",
                    "Quality assurance planning"
                ],
                "status": "ready"
            }
        }
    
    def execute_bmad_analyst_phase(self, project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute BMad Analyst phase for requirements gathering"""
        analyst_output = {
            "phase": "analyst",
            "deliverables": {
                "user_personas": self._generate_user_personas(project_context),
                "user_stories": self._generate_user_stories(project_context),
                "feature_list": self._generate_feature_list(project_context),
                "acceptance_criteria": self._generate_acceptance_criteria(project_context)
            },
            "recommendations": [
                "Prioritize core user workflows for MVP",
                "Consider mobile-first approach for better user engagement",
                "Plan for scalability from the beginning"
            ],
            "next_phase": "pm_phase"
        }
        
        return analyst_output
    
    def execute_bmad_pm_phase(self, analyst_output: Dict[str, Any]) -> Dict[str, Any]:
        """Execute BMad PM phase for project management planning"""
        pm_output = {
            "phase": "pm",
            "deliverables": {
                "project_timeline": self._generate_project_timeline(analyst_output),
                "resource_plan": self._generate_resource_plan(analyst_output),
                "risk_assessment": self._generate_risk_assessment(analyst_output),
                "milestones": self._generate_milestones(analyst_output)
            },
            "recommendations": [
                "Use iterative development approach",
                "Plan for regular stakeholder reviews",
                "Implement continuous integration from start"
            ],
            "next_phase": "architect_phase"
        }
        
        return pm_output
    
    def execute_bmad_architect_phase(self, pm_output: Dict[str, Any]) -> Dict[str, Any]:
        """Execute BMad Architect phase for technical design"""
        architect_output = {
            "phase": "architect",
            "deliverables": {
                "system_architecture": self._generate_system_architecture(pm_output),
                "technology_stack": self._recommend_technology_stack(pm_output),
                "database_design": self._generate_database_design(pm_output),
                "api_specification": self._generate_api_specification(pm_output)
            },
            "recommendations": [
                "Use microservices architecture for scalability",
                "Implement proper authentication and authorization",
                "Plan for monitoring and logging from the start"
            ],
            "next_phase": "scrum_master_phase"
        }
        
        return architect_output
    
    def execute_bmad_scrum_master_phase(self, architect_output: Dict[str, Any]) -> Dict[str, Any]:
        """Execute BMad Scrum Master phase for development workflow"""
        scrum_master_output = {
            "phase": "scrum_master",
            "deliverables": {
                "sprint_plan": self._generate_sprint_plan(architect_output),
                "development_stories": self._generate_development_stories(architect_output),
                "workflow_design": self._generate_workflow_design(architect_output),
                "qa_strategy": self._generate_qa_strategy(architect_output)
            },
            "recommendations": [
                "Start with 2-week sprints for better feedback cycles",
                "Implement automated testing from the beginning",
                "Use story-driven development approach"
            ],
            "final_deliverables_ready": True
        }
        
        return scrum_master_output
    
    def _generate_user_personas(self, project_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate user personas based on project context"""
        return [
            {
                "name": "Primary User",
                "role": "End User",
                "goals": ["Achieve primary objective", "Easy to use interface"],
                "pain_points": ["Current solution limitations", "Time constraints"],
                "tech_comfort": "Medium"
            },
            {
                "name": "Administrator",
                "role": "System Admin",
                "goals": ["Manage system", "Monitor performance"],
                "pain_points": ["Complex configuration", "Limited visibility"],
                "tech_comfort": "High"
            }
        ]
    
    def _generate_user_stories(self, project_context: Dict[str, Any]) -> List[str]:
        """Generate user stories based on project context"""
        return [
            "As a user, I want to easily access the main features so that I can accomplish my goals quickly",
            "As an administrator, I want to manage user permissions so that I can control system access",
            "As a user, I want to receive notifications so that I stay informed about important updates"
        ]
    
    def _generate_feature_list(self, project_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate feature list with priorities"""
        return [
            {"name": "User Authentication", "priority": "High", "complexity": "Medium"},
            {"name": "Dashboard Interface", "priority": "High", "complexity": "High"},
            {"name": "Data Management", "priority": "Medium", "complexity": "Medium"},
            {"name": "Reporting System", "priority": "Low", "complexity": "High"}
        ]
    
    def _generate_acceptance_criteria(self, project_context: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate acceptance criteria for features"""
        return {
            "User Authentication": [
                "User can register with email and password",
                "User can login with valid credentials",
                "User receives password reset email",
                "Invalid login attempts are handled gracefully"
            ],
            "Dashboard Interface": [
                "Dashboard loads within 2 seconds",
                "All key metrics are visible without scrolling",
                "Interface is responsive on mobile devices",
                "User can customize dashboard layout"
            ]
        }
    
    def _generate_project_timeline(self, analyst_output: Dict[str, Any]) -> Dict[str, Any]:
        """Generate project timeline based on analyst output"""
        return {
            "total_duration": "12 weeks",
            "phases": [
                {"name": "Setup & Planning", "duration": "1 week", "start_week": 1},
                {"name": "Core Development", "duration": "8 weeks", "start_week": 2},
                {"name": "Testing & QA", "duration": "2 weeks", "start_week": 10},
                {"name": "Deployment & Launch", "duration": "1 week", "start_week": 12}
            ]
        }
    
    def _generate_resource_plan(self, analyst_output: Dict[str, Any]) -> Dict[str, Any]:
        """Generate resource planning"""
        return {
            "team_size": "3-4 developers",
            "roles_needed": ["Frontend Developer", "Backend Developer", "DevOps Engineer", "QA Tester"],
            "estimated_hours": 480,
            "budget_estimate": "$50,000 - $75,000"
        }
    
    def _generate_risk_assessment(self, analyst_output: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate risk assessment"""
        return [
            {
                "risk": "Scope creep",
                "probability": "Medium",
                "impact": "High",
                "mitigation": "Clear requirements documentation and change control process"
            },
            {
                "risk": "Technical complexity",
                "probability": "Low",
                "impact": "Medium", 
                "mitigation": "Proof of concept for complex features"
            }
        ]
    
    def _generate_milestones(self, analyst_output: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate project milestones"""
        return [
            {"name": "MVP Release", "week": 6, "deliverables": ["Core features", "Basic UI"]},
            {"name": "Beta Release", "week": 10, "deliverables": ["Full feature set", "Testing complete"]},
            {"name": "Production Release", "week": 12, "deliverables": ["Deployed system", "Documentation"]}
        ]
    
    def _generate_system_architecture(self, pm_output: Dict[str, Any]) -> Dict[str, Any]:
        """Generate system architecture design"""
        return {
            "architecture_type": "Microservices",
            "components": [
                {"name": "Frontend", "technology": "React.js", "responsibility": "User Interface"},
                {"name": "API Gateway", "technology": "FastAPI", "responsibility": "Request routing"},
                {"name": "Auth Service", "technology": "Python", "responsibility": "Authentication"},
                {"name": "Database", "technology": "PostgreSQL", "responsibility": "Data storage"}
            ],
            "communication": "REST APIs with JWT authentication"
        }
    
    def _recommend_technology_stack(self, pm_output: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend technology stack"""
        return {
            "frontend": ["React.js", "TypeScript", "Tailwind CSS"],
            "backend": ["FastAPI", "Python", "SQLAlchemy"],
            "database": ["PostgreSQL", "Redis"],
            "infrastructure": ["Docker", "Nginx", "GitHub Actions"],
            "monitoring": ["Prometheus", "Grafana"]
        }
    
    def _generate_database_design(self, pm_output: Dict[str, Any]) -> Dict[str, Any]:
        """Generate database design"""
        return {
            "tables": [
                {
                    "name": "users",
                    "columns": ["id", "email", "password_hash", "created_at", "updated_at"],
                    "relationships": ["one-to-many with user_sessions"]
                },
                {
                    "name": "user_sessions", 
                    "columns": ["id", "user_id", "token", "expires_at"],
                    "relationships": ["many-to-one with users"]
                }
            ],
            "indexes": ["users.email", "user_sessions.token"],
            "constraints": ["users.email UNIQUE", "user_sessions.expires_at NOT NULL"]
        }
    
    def _generate_api_specification(self, pm_output: Dict[str, Any]) -> Dict[str, Any]:
        """Generate API specification"""
        return {
            "base_url": "/api/v1",
            "endpoints": [
                {
                    "path": "/auth/login",
                    "method": "POST",
                    "description": "User authentication",
                    "request": {"email": "string", "password": "string"},
                    "response": {"token": "string", "user": "object"}
                },
                {
                    "path": "/users/profile",
                    "method": "GET", 
                    "description": "Get user profile",
                    "auth_required": True,
                    "response": {"user": "object"}
                }
            ]
        }
    
    def _generate_sprint_plan(self, architect_output: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sprint planning"""
        return {
            "sprint_duration": "2 weeks",
            "total_sprints": 6,
            "sprints": [
                {
                    "number": 1,
                    "goal": "Project setup and authentication",
                    "stories": ["Setup development environment", "Implement user authentication"]
                },
                {
                    "number": 2,
                    "goal": "Core dashboard functionality",
                    "stories": ["Create dashboard layout", "Implement data visualization"]
                }
            ]
        }
    
    def _generate_development_stories(self, architect_output: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate development stories with full context"""
        return [
            {
                "id": "DEV-001",
                "title": "Implement User Authentication System",
                "description": "Create secure user authentication with JWT tokens",
                "acceptance_criteria": [
                    "User can register with email/password",
                    "User can login and receive JWT token",
                    "Protected routes require valid token"
                ],
                "technical_details": {
                    "framework": "FastAPI",
                    "database": "PostgreSQL",
                    "libraries": ["bcrypt", "python-jose"]
                },
                "estimated_hours": 16
            },
            {
                "id": "DEV-002", 
                "title": "Create Dashboard Interface",
                "description": "Build responsive dashboard with key metrics",
                "acceptance_criteria": [
                    "Dashboard loads within 2 seconds",
                    "Responsive design for mobile/desktop",
                    "Real-time data updates"
                ],
                "technical_details": {
                    "framework": "React.js",
                    "styling": "Tailwind CSS",
                    "state_management": "React hooks"
                },
                "estimated_hours": 24
            }
        ]
    
    def _generate_workflow_design(self, architect_output: Dict[str, Any]) -> Dict[str, Any]:
        """Generate development workflow design"""
        return {
            "methodology": "Agile Scrum with BMad-Method",
            "workflow_steps": [
                "Story selection from backlog",
                "Development with full context",
                "Code review and testing",
                "Integration and deployment"
            ],
            "tools": {
                "version_control": "Git with GitHub",
                "project_management": "GitHub Projects",
                "ci_cd": "GitHub Actions",
                "testing": "Pytest + Jest"
            }
        }
    
    def _generate_qa_strategy(self, architect_output: Dict[str, Any]) -> Dict[str, Any]:
        """Generate QA strategy"""
        return {
            "testing_levels": [
                "Unit testing (70% coverage minimum)",
                "Integration testing",
                "End-to-end testing",
                "User acceptance testing"
            ],
            "automation": {
                "unit_tests": "Automated in CI/CD",
                "integration_tests": "Automated in CI/CD", 
                "e2e_tests": "Automated with Playwright"
            },
            "quality_gates": [
                "All tests must pass",
                "Code coverage > 70%",
                "No critical security vulnerabilities"
            ]
        }
    
    def _generate_scheduling_confirmation(self, available_slots: List[Dict[str, Any]]) -> str:
        """Generate scheduling confirmation message"""
        slots_text = "\n".join([
            f"• {slot['date']} at {slot['time']} ({slot['duration']} minutes)"
            for slot in available_slots[:3]  # Show top 3 slots
        ])
        
        return (
            f"Perfect! I have several available time slots for your consultation:\n\n"
            f"{slots_text}\n\n"
            f"Please let me know which time works best for you, and I'll send you a calendar invitation. "
            f"In the meantime, I'll begin preparing research materials based on our discussion.\n\n"
            f"What specific topics would you like me to focus on in my preparation?"
        )
    
    def _generate_alternative_scheduling_options(self) -> str:
        """Generate alternative scheduling options"""
        return (
            "I apologize, but I don't have availability during your preferred times. "
            "Let me suggest some alternative options:\n\n"
            "• **This week**: Tuesday 2-4 PM, Thursday 10 AM-12 PM\n"
            "• **Next week**: Monday 9-11 AM, Wednesday 1-3 PM, Friday 3-5 PM\n\n"
            "Would any of these times work for you? I'm also happy to accommodate "
            "early morning or evening slots if needed for your schedule."
        )
    
    def _generate_research_response(self, research_plan: Dict[str, Any]) -> str:
        """Generate research preparation response"""
        topics_text = ", ".join(research_plan["topics"])
        deliverables_text = "\n".join([f"• {deliverable}" for deliverable in research_plan["deliverables"]])
        
        return (
            f"Excellent! I'll conduct comprehensive research on: {topics_text}\n\n"
            f"**Research Plan Overview:**\n"
            f"• **Estimated Time**: {research_plan['estimated_time']}\n"
            f"• **Research Areas**: {', '.join(research_plan['research_areas'])}\n\n"
            f"**Deliverables for Your Consultation:**\n"
            f"{deliverables_text}\n\n"
            f"I'll have all research materials prepared and sent to you 24 hours before our meeting. "
            f"This will give you time to review the findings and prepare any additional questions.\n\n"
            f"Is there anything specific you'd like me to emphasize in my research?"
        )
    
    def _handle_general_consultation_inquiry(self, message: str) -> AgentResponse:
        """Handle general consultation inquiries"""
        return AgentResponse(
            message=(
                "I'm here to help with your consultation needs. I can assist with:\n\n"
                "• **Strategic Planning**: Business strategy and market analysis\n"
                "• **Technical Consultation**: Technology recommendations and implementation\n"
                "• **Project Planning**: Comprehensive BMad-Method planning for development projects\n"
                "• **Research Services**: Market research and competitive analysis\n\n"
                "What type of consultation are you looking for?"
            ),
            confidence=0.8,
            next_action="clarify_consultation_type"
        )


class BMadMethodEngine:
    """BMad-Method integration engine for comprehensive project planning"""
    
    def __init__(self):
        self.bmad_repo_path = "/tmp/bmad-method"
        self.agents = {
            "analyst": "Requirements analysis and user story creation",
            "pm": "Project management and timeline planning", 
            "architect": "Technical architecture and system design",
            "scrum_master": "Agile workflow and development stories"
        }
    
    def initialize_bmad_project(self, project_name: str, project_type: str = "web_app") -> Dict[str, Any]:
        """Initialize BMad-Method project structure"""
        try:
            # Clone BMad-Method repository if not exists
            if not os.path.exists(self.bmad_repo_path):
                subprocess.run([
                    "git", "clone", 
                    "https://github.com/abusallam/BMAD-METHOD.git",
                    self.bmad_repo_path
                ], check=True)
            
            # Initialize project with BMad
            project_path = f"/tmp/bmad_projects/{project_name}"
            os.makedirs(project_path, exist_ok=True)
            
            # Copy BMad templates
            subprocess.run([
                "cp", "-r", 
                f"{self.bmad_repo_path}/templates/*",
                project_path
            ], check=True)
            
            return {
                "project_path": project_path,
                "bmad_initialized": True,
                "available_agents": list(self.agents.keys()),
                "project_type": project_type
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to initialize BMad project: {e}")
            return {
                "project_path": None,
                "bmad_initialized": False,
                "error": str(e)
            }
    
    def run_bmad_agent(self, agent_type: str, project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Run specific BMad agent with project context"""
        if agent_type not in self.agents:
            return {"error": f"Unknown agent type: {agent_type}"}
        
        # Mock BMad agent execution - in production, this would run actual BMad agents
        agent_results = {
            "analyst": self._run_analyst_agent(project_context),
            "pm": self._run_pm_agent(project_context),
            "architect": self._run_architect_agent(project_context),
            "scrum_master": self._run_scrum_master_agent(project_context)
        }
        
        return agent_results.get(agent_type, {"error": "Agent execution failed"})
    
    def _run_analyst_agent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run BMad Analyst agent"""
        return {
            "agent": "analyst",
            "deliverables": {
                "prd_draft": "Product Requirements Document created",
                "user_stories": ["Story 1", "Story 2", "Story 3"],
                "personas": ["User Persona 1", "Admin Persona"],
                "feature_matrix": "Feature prioritization matrix"
            },
            "status": "completed"
        }
    
    def _run_pm_agent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run BMad PM agent"""
        return {
            "agent": "pm",
            "deliverables": {
                "project_timeline": "12-week development timeline",
                "resource_allocation": "Team structure and roles",
                "risk_matrix": "Risk assessment and mitigation",
                "milestone_plan": "Key project milestones"
            },
            "status": "completed"
        }
    
    def _run_architect_agent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run BMad Architect agent"""
        return {
            "agent": "architect",
            "deliverables": {
                "system_architecture": "Technical architecture document",
                "tech_stack": "Recommended technology stack",
                "database_schema": "Database design and relationships",
                "api_design": "API specification and endpoints"
            },
            "status": "completed"
        }
    
    def _run_scrum_master_agent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run BMad Scrum Master agent"""
        return {
            "agent": "scrum_master",
            "deliverables": {
                "sprint_backlog": "Organized development stories",
                "workflow_design": "Development process and workflow",
                "story_templates": "Story templates with full context",
                "qa_strategy": "Testing and quality assurance plan"
            },
            "status": "completed"
        }
    
    def generate_comprehensive_plan(self, project_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive project plan using all BMad agents"""
        project_name = project_requirements.get("name", "bmad_project")
        
        # Initialize project
        init_result = self.initialize_bmad_project(project_name)
        if not init_result["bmad_initialized"]:
            return {"error": "Failed to initialize BMad project"}
        
        # Run all agents in sequence
        comprehensive_plan = {
            "project_name": project_name,
            "bmad_version": "4.0",
            "planning_phases": {}
        }
        
        for agent_type in ["analyst", "pm", "architect", "scrum_master"]:
            agent_result = self.run_bmad_agent(agent_type, project_requirements)
            comprehensive_plan["planning_phases"][agent_type] = agent_result
        
        # Generate final deliverables
        comprehensive_plan["final_deliverables"] = {
            "prd_document": "Complete Product Requirements Document",
            "architecture_document": "Technical Architecture Specification", 
            "development_stories": "Context-rich development stories",
            "implementation_roadmap": "Step-by-step implementation plan"
        }
        
        return comprehensive_plan