"""
Professional Agent - Custom coding and professional solutions
Handles requirement gathering, technical feasibility, and negotiation
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResponse, AgentConfig
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class RequirementSpec:
    """Detailed requirement specification"""
    functional_requirements: List[str]
    technical_requirements: List[str]
    constraints: List[str]
    integrations: List[str]
    timeline: str
    budget_range: str
    complexity_level: str


@dataclass
class FeasibilityReport:
    """Technical feasibility assessment"""
    feasible: bool
    complexity_score: float
    estimated_timeline: str
    recommended_approach: str
    potential_challenges: List[str]
    technology_stack: List[str]


class ProfessionalAgent(BaseAgent):
    """Agent for custom coding and professional solutions"""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.requirement_analyzer = RequirementAnalyzer()
        self.technical_assessor = TechnicalAssessor()
        self.negotiation_engine = NegotiationEngine()
        self.conversation_stage = "initial"  # initial, requirements, feasibility, negotiation, proposal
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the professional agent"""
        return """
        You are a Professional Agent specializing in custom development and technical solutions.
        
        Your expertise includes:
        1. Requirement gathering and analysis
        2. Technical feasibility assessment
        3. Solution architecture and design
        4. Technology stack recommendations
        5. Project timeline and budget estimation
        6. Client negotiation and proposal development
        
        Your approach:
        - Ask detailed technical questions
        - Provide professional assessments
        - Offer multiple solution options
        - Be transparent about complexity and costs
        - Guide clients through decision-making process
        
        Always maintain a professional, consultative tone while being thorough and accurate.
        """
    
    def process_message(self, message: str, context: Dict[str, Any] = None) -> AgentResponse:
        """Process professional service request"""
        self.add_to_history("user", message)
        
        # Determine conversation stage and process accordingly
        if self.conversation_stage == "initial":
            response = self._handle_initial_inquiry(message, context)
        elif self.conversation_stage == "requirements":
            response = self._handle_requirements_gathering(message)
        elif self.conversation_stage == "feasibility":
            response = self._handle_feasibility_discussion(message)
        elif self.conversation_stage == "negotiation":
            response = self._handle_negotiation(message)
        else:
            response = self._handle_general_inquiry(message)
        
        self.add_to_history("assistant", response.message)
        return response
    
    def _handle_initial_inquiry(self, message: str, context: Dict[str, Any] = None) -> AgentResponse:
        """Handle initial professional service inquiry"""
        # Analyze the initial request
        initial_analysis = self._analyze_initial_request(message)
        
        # Generate response based on analysis
        if initial_analysis["complexity"] == "high":
            response_message = self._generate_complex_project_response(initial_analysis)
        elif initial_analysis["complexity"] == "medium":
            response_message = self._generate_medium_project_response(initial_analysis)
        else:
            response_message = self._generate_simple_project_response(initial_analysis)
        
        # Move to requirements gathering stage
        self.conversation_stage = "requirements"
        
        return AgentResponse(
            message=response_message,
            confidence=0.8,
            next_action="gather_requirements",
            context={
                "stage": "requirements_gathering",
                "initial_analysis": initial_analysis,
                "project_type": initial_analysis.get("type", "custom_development")
            }
        )
    
    def _handle_requirements_gathering(self, message: str) -> AgentResponse:
        """Handle requirements gathering conversation"""
        # Extract requirements from message
        requirements = self.gather_requirements(message)
        
        # Check if we have enough information
        completeness = self._assess_requirements_completeness(requirements)
        
        if completeness["complete"]:
            # Move to feasibility assessment
            self.conversation_stage = "feasibility"
            feasibility = self.assess_technical_feasibility(requirements)
            response_message = self._generate_feasibility_response(feasibility)
            next_action = "present_feasibility"
        else:
            # Continue gathering requirements
            missing_areas = completeness["missing"]
            response_message = self._generate_requirements_followup(missing_areas)
            next_action = "continue_requirements"
        
        return AgentResponse(
            message=response_message,
            confidence=0.9,
            next_action=next_action,
            context={
                "requirements": requirements,
                "completeness": completeness
            }
        )
    
    def _handle_feasibility_discussion(self, message: str) -> AgentResponse:
        """Handle feasibility discussion and solution options"""
        # Analyze client response to feasibility
        client_feedback = self._analyze_client_feedback(message)
        
        if client_feedback["proceed"]:
            # Move to negotiation stage
            self.conversation_stage = "negotiation"
            response_message = self._generate_negotiation_start()
            next_action = "start_negotiation"
        elif client_feedback["concerns"]:
            # Address concerns and provide alternatives
            response_message = self._address_feasibility_concerns(client_feedback["concerns"])
            next_action = "address_concerns"
        else:
            # Provide more details or alternatives
            response_message = self._provide_alternative_solutions()
            next_action = "present_alternatives"
        
        return AgentResponse(
            message=response_message,
            confidence=0.85,
            next_action=next_action,
            context={"client_feedback": client_feedback}
        )
    
    def _handle_negotiation(self, message: str) -> AgentResponse:
        """Handle negotiation and proposal development"""
        negotiation_points = self._extract_negotiation_points(message)
        
        # Generate counter-proposal or agreement
        if negotiation_points["agreement"]:
            response_message = self._generate_agreement_response()
            next_action = "create_proposal"
        else:
            response_message = self._generate_negotiation_response(negotiation_points)
            next_action = "continue_negotiation"
        
        return AgentResponse(
            message=response_message,
            confidence=0.9,
            next_action=next_action,
            context={"negotiation_points": negotiation_points}
        )
    
    def gather_requirements(self, conversation: str) -> RequirementSpec:
        """Extract detailed requirements from conversation"""
        return self.requirement_analyzer.analyze(conversation)
    
    def assess_technical_feasibility(self, requirements: RequirementSpec) -> FeasibilityReport:
        """Assess technical feasibility and provide recommendations"""
        return self.technical_assessor.assess(requirements)
    
    def _analyze_initial_request(self, message: str) -> Dict[str, Any]:
        """Analyze initial request to determine project characteristics"""
        message_lower = message.lower()
        
        analysis = {
            "type": "custom_development",
            "complexity": "medium",
            "technologies": [],
            "integrations": [],
            "urgency": "normal"
        }
        
        # Determine project type
        if any(word in message_lower for word in ["api", "integration", "connect"]):
            analysis["type"] = "api_integration"
        elif any(word in message_lower for word in ["website", "web", "frontend"]):
            analysis["type"] = "web_development"
        elif any(word in message_lower for word in ["mobile", "app", "ios", "android"]):
            analysis["type"] = "mobile_development"
        elif any(word in message_lower for word in ["automation", "workflow", "process"]):
            analysis["type"] = "process_automation"
        
        # Assess complexity
        complexity_indicators = {
            "high": ["enterprise", "complex", "advanced", "machine learning", "ai", "blockchain"],
            "medium": ["custom", "integration", "database", "api", "professional"],
            "low": ["simple", "basic", "template", "quick"]
        }
        
        for level, indicators in complexity_indicators.items():
            if any(indicator in message_lower for indicator in indicators):
                analysis["complexity"] = level
                break
        
        return analysis
    
    def _generate_complex_project_response(self, analysis: Dict[str, Any]) -> str:
        """Generate response for complex projects"""
        return (
            f"I understand you're looking for a {analysis['type'].replace('_', ' ')} solution. "
            f"Based on your description, this appears to be a complex project that will require "
            f"careful planning and a robust technical approach.\n\n"
            f"To provide you with an accurate assessment and proposal, I'll need to gather "
            f"detailed requirements. Let me start with a few key questions:\n\n"
            f"1. What are the core functionalities you need?\n"
            f"2. Do you have any existing systems that need integration?\n"
            f"3. What's your target timeline for this project?\n"
            f"4. Are there any specific technical constraints or preferences?"
        )
    
    def _generate_medium_project_response(self, analysis: Dict[str, Any]) -> str:
        """Generate response for medium complexity projects"""
        return (
            f"Great! I can help you with your {analysis['type'].replace('_', ' ')} project. "
            f"This looks like a solid professional development opportunity.\n\n"
            f"To create the best solution for you, I'd like to understand your requirements better. "
            f"Could you tell me more about:\n\n"
            f"1. The specific features and functionality you need\n"
            f"2. Your preferred technology stack (if any)\n"
            f"3. Integration requirements with existing systems\n"
            f"4. Your timeline and budget considerations"
        )
    
    def _generate_simple_project_response(self, analysis: Dict[str, Any]) -> str:
        """Generate response for simple projects"""
        return (
            f"Perfect! Your {analysis['type'].replace('_', ' ')} project sounds straightforward. "
            f"I can definitely help you build this solution efficiently.\n\n"
            f"Let me gather a few details to provide you with an accurate quote and timeline:\n\n"
            f"1. What specific functionality do you need?\n"
            f"2. Do you have any design preferences or existing branding?\n"
            f"3. When would you like to have this completed?\n"
            f"4. What's your budget range for this project?"
        )


class RequirementAnalyzer:
    """Analyzes and extracts requirements from conversations"""
    
    def analyze(self, conversation: str) -> RequirementSpec:
        """Analyze conversation and extract structured requirements"""
        # This would use NLP and pattern matching to extract requirements
        # For now, returning a basic structure
        return RequirementSpec(
            functional_requirements=[],
            technical_requirements=[],
            constraints=[],
            integrations=[],
            timeline="TBD",
            budget_range="TBD",
            complexity_level="medium"
        )


class TechnicalAssessor:
    """Assesses technical feasibility of requirements"""
    
    def assess(self, requirements: RequirementSpec) -> FeasibilityReport:
        """Assess technical feasibility of requirements"""
        # This would perform detailed technical analysis
        # For now, returning a basic assessment
        return FeasibilityReport(
            feasible=True,
            complexity_score=0.7,
            estimated_timeline="4-6 weeks",
            recommended_approach="Agile development with iterative delivery",
            potential_challenges=[],
            technology_stack=[]
        )


class NegotiationEngine:
    """Handles negotiation and proposal development"""
    
    def negotiate(self, client_requirements: Dict[str, Any], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Handle negotiation between client requirements and project constraints"""
        # This would implement negotiation logic
        return {"status": "in_progress"}    def _
handle_general_inquiry(self, message: str) -> AgentResponse:
        """Handle general professional service inquiries"""
        return AgentResponse(
            message="I'm here to help with your custom development needs. Could you tell me more about your project requirements?",
            confidence=0.8,
            next_action="gather_requirements"
        )
    
    def _generate_requirements_followup(self, missing_areas: List[str]) -> str:
        """Generate follow-up questions for missing requirement areas"""
        questions = []
        
        if "technical_stack" in missing_areas:
            questions.append("What technology stack do you prefer or are you currently using?")
        
        if "timeline" in missing_areas:
            questions.append("What's your target timeline for this project?")
        
        if "budget" in missing_areas:
            questions.append("Do you have a budget range in mind for this development?")
        
        if "integrations" in missing_areas:
            questions.append("Do you need to integrate with any existing systems or third-party services?")
        
        if "scalability" in missing_areas:
            questions.append("How many users do you expect to support initially and at scale?")
        
        base_message = "To provide you with the best solution, I need a bit more information:\n\n"
        return base_message + "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions))
    
    def _assess_requirements_completeness(self, requirements: RequirementSpec) -> Dict[str, Any]:
        """Assess if requirements are complete enough for feasibility analysis"""
        missing_areas = []
        
        if not requirements.technical_requirements:
            missing_areas.append("technical_stack")
        
        if requirements.timeline == "TBD":
            missing_areas.append("timeline")
        
        if requirements.budget_range == "TBD":
            missing_areas.append("budget")
        
        if not requirements.integrations:
            missing_areas.append("integrations")
        
        completeness_score = 1.0 - (len(missing_areas) / 5.0)
        
        return {
            "complete": completeness_score >= 0.7,
            "score": completeness_score,
            "missing": missing_areas
        }
    
    def _generate_feasibility_response(self, feasibility: FeasibilityReport) -> str:
        """Generate response based on feasibility assessment"""
        if feasibility.feasible:
            return (
                f"Great news! Your project is definitely feasible. Based on my analysis:\n\n"
                f"**Complexity Level**: {feasibility.complexity_score:.1f}/1.0\n"
                f"**Estimated Timeline**: {feasibility.estimated_timeline}\n"
                f"**Recommended Approach**: {feasibility.recommended_approach}\n\n"
                f"**Technology Stack Recommendation**:\n"
                f"{', '.join(feasibility.technology_stack)}\n\n"
                f"Would you like me to proceed with creating a detailed project proposal?"
            )
        else:
            challenges_text = "\n".join(f"• {challenge}" for challenge in feasibility.potential_challenges)
            return (
                f"I've analyzed your requirements and identified some challenges that need addressing:\n\n"
                f"{challenges_text}\n\n"
                f"However, these challenges are manageable. I recommend we discuss alternative approaches "
                f"that can achieve your goals while working within these constraints. "
                f"Would you like to explore some modified solutions?"
            )
    
    def _analyze_client_feedback(self, message: str) -> Dict[str, Any]:
        """Analyze client feedback on feasibility assessment"""
        message_lower = message.lower()
        
        feedback = {
            "proceed": False,
            "concerns": [],
            "modifications_requested": []
        }
        
        # Check for positive signals
        if any(word in message_lower for word in ["yes", "proceed", "sounds good", "let's go", "approve"]):
            feedback["proceed"] = True
        
        # Check for concerns
        concern_indicators = ["concern", "worry", "issue", "problem", "but", "however"]
        if any(indicator in message_lower for indicator in concern_indicators):
            # Extract concerns (simplified)
            if "timeline" in message_lower:
                feedback["concerns"].append("timeline")
            if "budget" in message_lower or "cost" in message_lower:
                feedback["concerns"].append("budget")
            if "complex" in message_lower:
                feedback["concerns"].append("complexity")
        
        return feedback
    
    def _address_feasibility_concerns(self, concerns: List[str]) -> str:
        """Address specific feasibility concerns"""
        responses = {
            "timeline": "I understand timeline is a concern. We can break the project into phases to deliver value sooner, or adjust the scope for faster delivery.",
            "budget": "Budget considerations are important. We can explore different approaches - MVP first, phased development, or alternative technology choices to optimize costs.",
            "complexity": "Complexity can be managed through proper architecture and incremental development. We can start with core features and expand gradually."
        }
        
        concern_responses = [responses.get(concern, f"I'll address your {concern} concerns") for concern in concerns]
        
        return (
            "I understand your concerns. Let me address them:\n\n" +
            "\n\n".join(f"**{concern.title()}**: {response}" for concern, response in zip(concerns, concern_responses)) +
            "\n\nWould you like to discuss any of these points in more detail?"
        )
    
    def _provide_alternative_solutions(self) -> str:
        """Provide alternative solution approaches"""
        return (
            "Let me suggest some alternative approaches that might better fit your needs:\n\n"
            "**Option 1: MVP Approach**\n"
            "Start with core features, validate with users, then expand based on feedback.\n\n"
            "**Option 2: Phased Development**\n"
            "Break the project into independent phases, each delivering business value.\n\n"
            "**Option 3: Hybrid Solution**\n"
            "Combine existing tools/platforms with custom development where needed.\n\n"
            "Which approach interests you most, or would you like me to elaborate on any of these?"
        )
    
    def _generate_negotiation_start(self) -> str:
        """Generate message to start negotiation phase"""
        return (
            "Excellent! Now let's discuss the project details and create a proposal that works for both of us.\n\n"
            "Key areas we should align on:\n"
            "• Project scope and deliverables\n"
            "• Timeline and milestones\n"
            "• Budget and payment structure\n"
            "• Communication and collaboration approach\n"
            "• Success criteria and acceptance testing\n\n"
            "What aspect would you like to discuss first?"
        )
    
    def _extract_negotiation_points(self, message: str) -> Dict[str, Any]:
        """Extract negotiation points from client message"""
        message_lower = message.lower()
        
        negotiation_points = {
            "agreement": False,
            "scope_changes": [],
            "timeline_concerns": False,
            "budget_discussions": False,
            "additional_requirements": []
        }
        
        # Check for agreement signals
        if any(word in message_lower for word in ["agree", "sounds good", "let's proceed", "accepted"]):
            negotiation_points["agreement"] = True
        
        # Check for scope discussions
        if "scope" in message_lower or "features" in message_lower:
            negotiation_points["scope_changes"].append("scope_modification_requested")
        
        # Check for timeline discussions
        if "timeline" in message_lower or "deadline" in message_lower:
            negotiation_points["timeline_concerns"] = True
        
        # Check for budget discussions
        if "budget" in message_lower or "cost" in message_lower or "price" in message_lower:
            negotiation_points["budget_discussions"] = True
        
        return negotiation_points
    
    def _generate_negotiation_response(self, negotiation_points: Dict[str, Any]) -> str:
        """Generate response based on negotiation points"""
        responses = []
        
        if negotiation_points["scope_changes"]:
            responses.append("I understand you'd like to discuss scope modifications. Let's review what changes you have in mind.")
        
        if negotiation_points["timeline_concerns"]:
            responses.append("Regarding timeline, I'm flexible and can work with your deadlines. What timeline works best for you?")
        
        if negotiation_points["budget_discussions"]:
            responses.append("For budget considerations, I can provide different options based on scope and timeline preferences.")
        
        if not responses:
            responses.append("I'm here to work with you on finding the best solution. What specific aspects would you like to adjust?")
        
        return "\n\n".join(responses) + "\n\nWhat would you like to focus on next?"
    
    def _generate_agreement_response(self) -> str:
        """Generate response when client agrees to proceed"""
        return (
            "Fantastic! I'm excited to work on this project with you.\n\n"
            "Next steps:\n"
            "1. I'll prepare a detailed project proposal with timeline and deliverables\n"
            "2. Set up a development environment and testing infrastructure\n"
            "3. Create a project repository and collaboration workspace\n"
            "4. Schedule regular check-ins and progress reviews\n\n"
            "I'll have the detailed proposal ready within 24 hours. "
            "Is there anything specific you'd like me to include or emphasize in the proposal?"
        )
    
    def create_deployment_environment(self, project_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create test deployment environment for custom development"""
        project_name = project_requirements.get("name", "custom_project")
        tech_stack = project_requirements.get("tech_stack", ["node", "react"])
        
        deployment_config = {
            "project_name": project_name,
            "environment": "test",
            "tech_stack": tech_stack,
            "infrastructure": self._generate_infrastructure_config(tech_stack),
            "deployment_url": f"https://test-{project_name.lower().replace(' ', '-')}.dev.consulting.sa",
            "repository_url": f"https://github.com/consulting-sa/{project_name.lower().replace(' ', '-')}",
            "ci_cd_pipeline": self._setup_ci_cd_pipeline(project_name, tech_stack),
            "monitoring": self._setup_monitoring(project_name)
        }
        
        return deployment_config
    
    def _generate_infrastructure_config(self, tech_stack: List[str]) -> Dict[str, Any]:
        """Generate infrastructure configuration based on tech stack"""
        config = {
            "containers": [],
            "databases": [],
            "services": []
        }
        
        if "node" in tech_stack or "react" in tech_stack:
            config["containers"].append({
                "name": "frontend",
                "image": "node:18-alpine",
                "ports": ["3000:3000"],
                "environment": ["NODE_ENV=development"]
            })
        
        if "python" in tech_stack:
            config["containers"].append({
                "name": "backend",
                "image": "python:3.11-slim",
                "ports": ["8000:8000"],
                "environment": ["PYTHONPATH=/app"]
            })
        
        if "database" in tech_stack:
            config["databases"].append({
                "type": "postgresql",
                "version": "15",
                "name": "app_db"
            })
        
        return config
    
    def _setup_ci_cd_pipeline(self, project_name: str, tech_stack: List[str]) -> Dict[str, Any]:
        """Set up CI/CD pipeline configuration"""
        return {
            "platform": "github_actions",
            "stages": ["test", "build", "deploy"],
            "test_commands": self._generate_test_commands(tech_stack),
            "build_commands": self._generate_build_commands(tech_stack),
            "deploy_target": f"test-{project_name.lower().replace(' ', '-')}.dev.consulting.sa"
        }
    
    def _generate_test_commands(self, tech_stack: List[str]) -> List[str]:
        """Generate test commands based on tech stack"""
        commands = []
        
        if "node" in tech_stack:
            commands.extend(["npm install", "npm test", "npm run lint"])
        
        if "python" in tech_stack:
            commands.extend(["pip install -r requirements.txt", "pytest", "flake8"])
        
        return commands
    
    def _generate_build_commands(self, tech_stack: List[str]) -> List[str]:
        """Generate build commands based on tech stack"""
        commands = []
        
        if "react" in tech_stack:
            commands.extend(["npm run build"])
        
        if "python" in tech_stack:
            commands.extend(["python -m build"])
        
        return commands
    
    def _setup_monitoring(self, project_name: str) -> Dict[str, Any]:
        """Set up monitoring configuration"""
        return {
            "health_checks": [
                f"https://test-{project_name.lower().replace(' ', '-')}.dev.consulting.sa/health"
            ],
            "metrics": ["response_time", "error_rate", "uptime"],
            "alerts": {
                "email": "alerts@consulting.sa",
                "thresholds": {
                    "response_time": 2000,  # ms
                    "error_rate": 5,  # %
                    "uptime": 99  # %
                }
            }
        }


class RequirementAnalyzer:
    """Enhanced requirement analyzer for professional development"""
    
    def analyze(self, conversation: str) -> RequirementSpec:
        """Analyze conversation and extract structured requirements"""
        # Enhanced requirement extraction logic
        functional_reqs = self._extract_functional_requirements(conversation)
        technical_reqs = self._extract_technical_requirements(conversation)
        constraints = self._extract_constraints(conversation)
        integrations = self._extract_integrations(conversation)
        timeline = self._extract_timeline(conversation)
        budget = self._extract_budget_range(conversation)
        complexity = self._assess_complexity(conversation)
        
        return RequirementSpec(
            functional_requirements=functional_reqs,
            technical_requirements=technical_reqs,
            constraints=constraints,
            integrations=integrations,
            timeline=timeline,
            budget_range=budget,
            complexity_level=complexity
        )
    
    def _extract_functional_requirements(self, conversation: str) -> List[str]:
        """Extract functional requirements from conversation"""
        # Simplified extraction - in production, use NLP
        requirements = []
        
        if "user management" in conversation.lower():
            requirements.append("User registration and authentication system")
        
        if "dashboard" in conversation.lower():
            requirements.append("Administrative dashboard interface")
        
        if "api" in conversation.lower():
            requirements.append("RESTful API endpoints")
        
        if "mobile" in conversation.lower():
            requirements.append("Mobile-responsive design")
        
        return requirements
    
    def _extract_technical_requirements(self, conversation: str) -> List[str]:
        """Extract technical requirements"""
        tech_reqs = []
        
        if "react" in conversation.lower():
            tech_reqs.append("React.js frontend framework")
        
        if "python" in conversation.lower():
            tech_reqs.append("Python backend development")
        
        if "database" in conversation.lower():
            tech_reqs.append("Database integration")
        
        return tech_reqs
    
    def _extract_constraints(self, conversation: str) -> List[str]:
        """Extract project constraints"""
        constraints = []
        
        if "budget" in conversation.lower():
            constraints.append("Budget limitations")
        
        if "deadline" in conversation.lower() or "urgent" in conversation.lower():
            constraints.append("Time constraints")
        
        return constraints
    
    def _extract_integrations(self, conversation: str) -> List[str]:
        """Extract required integrations"""
        integrations = []
        
        integration_keywords = {
            "payment": "Payment processing (Stripe/PayPal)",
            "email": "Email service integration",
            "social": "Social media integration",
            "analytics": "Analytics integration"
        }
        
        for keyword, integration in integration_keywords.items():
            if keyword in conversation.lower():
                integrations.append(integration)
        
        return integrations
    
    def _extract_timeline(self, conversation: str) -> str:
        """Extract project timeline"""
        if "week" in conversation.lower():
            return "1-4 weeks"
        elif "month" in conversation.lower():
            return "1-3 months"
        elif "urgent" in conversation.lower():
            return "Rush delivery"
        else:
            return "TBD"
    
    def _extract_budget_range(self, conversation: str) -> str:
        """Extract budget range"""
        if any(word in conversation.lower() for word in ["cheap", "budget", "affordable"]):
            return "Budget-friendly"
        elif any(word in conversation.lower() for word in ["enterprise", "premium", "high-end"]):
            return "Premium"
        else:
            return "TBD"
    
    def _assess_complexity(self, conversation: str) -> str:
        """Assess project complexity"""
        complexity_indicators = {
            "high": ["enterprise", "complex", "advanced", "machine learning", "ai", "blockchain"],
            "medium": ["custom", "integration", "database", "api", "professional"],
            "low": ["simple", "basic", "template", "quick"]
        }
        
        conversation_lower = conversation.lower()
        
        for level, indicators in complexity_indicators.items():
            if any(indicator in conversation_lower for indicator in indicators):
                return level
        
        return "medium"


class TechnicalAssessor:
    """Enhanced technical feasibility assessor"""
    
    def assess(self, requirements: RequirementSpec) -> FeasibilityReport:
        """Assess technical feasibility with detailed analysis"""
        complexity_score = self._calculate_complexity_score(requirements)
        timeline = self._estimate_timeline(requirements, complexity_score)
        tech_stack = self._recommend_tech_stack(requirements)
        challenges = self._identify_challenges(requirements)
        approach = self._recommend_approach(requirements, complexity_score)
        
        return FeasibilityReport(
            feasible=True,  # Most projects are feasible with proper planning
            complexity_score=complexity_score,
            estimated_timeline=timeline,
            recommended_approach=approach,
            potential_challenges=challenges,
            technology_stack=tech_stack
        )
    
    def _calculate_complexity_score(self, requirements: RequirementSpec) -> float:
        """Calculate complexity score based on requirements"""
        base_score = 0.3
        
        # Add complexity based on functional requirements
        base_score += len(requirements.functional_requirements) * 0.1
        
        # Add complexity based on integrations
        base_score += len(requirements.integrations) * 0.15
        
        # Add complexity based on constraints
        if "Time constraints" in requirements.constraints:
            base_score += 0.2
        
        # Complexity level modifier
        complexity_modifiers = {"low": 0.0, "medium": 0.2, "high": 0.4}
        base_score += complexity_modifiers.get(requirements.complexity_level, 0.2)
        
        return min(base_score, 1.0)
    
    def _estimate_timeline(self, requirements: RequirementSpec, complexity_score: float) -> str:
        """Estimate project timeline"""
        base_weeks = 2
        complexity_weeks = complexity_score * 8
        integration_weeks = len(requirements.integrations) * 0.5
        
        total_weeks = base_weeks + complexity_weeks + integration_weeks
        
        if total_weeks <= 2:
            return "1-2 weeks"
        elif total_weeks <= 4:
            return "2-4 weeks"
        elif total_weeks <= 8:
            return "1-2 months"
        else:
            return "2-3 months"
    
    def _recommend_tech_stack(self, requirements: RequirementSpec) -> List[str]:
        """Recommend technology stack"""
        tech_stack = []
        
        # Frontend recommendations
        if any("dashboard" in req.lower() for req in requirements.functional_requirements):
            tech_stack.extend(["React.js", "TypeScript", "Tailwind CSS"])
        
        # Backend recommendations
        if any("api" in req.lower() for req in requirements.functional_requirements):
            tech_stack.extend(["FastAPI", "Python", "PostgreSQL"])
        
        # Integration recommendations
        if "Payment processing" in requirements.integrations:
            tech_stack.append("Stripe API")
        
        if "Email service" in requirements.integrations:
            tech_stack.append("SendGrid")
        
        return tech_stack or ["React.js", "FastAPI", "PostgreSQL"]
    
    def _identify_challenges(self, requirements: RequirementSpec) -> List[str]:
        """Identify potential project challenges"""
        challenges = []
        
        if "Time constraints" in requirements.constraints:
            challenges.append("Tight timeline may require scope prioritization")
        
        if len(requirements.integrations) > 3:
            challenges.append("Multiple integrations may increase complexity")
        
        if requirements.complexity_level == "high":
            challenges.append("High complexity requires careful architecture planning")
        
        return challenges
    
    def _recommend_approach(self, requirements: RequirementSpec, complexity_score: float) -> str:
        """Recommend development approach"""
        if complexity_score > 0.7:
            return "Agile development with iterative delivery and regular client feedback"
        elif complexity_score > 0.4:
            return "Phased development with milestone-based delivery"
        else:
            return "Rapid prototyping with quick iteration cycles"


class NegotiationEngine:
    """Enhanced negotiation engine for project proposals"""
    
    def negotiate(self, client_requirements: Dict[str, Any], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Handle negotiation between client requirements and project constraints"""
        negotiation_result = {
            "status": "in_progress",
            "agreed_scope": [],
            "timeline_adjustments": [],
            "budget_considerations": [],
            "next_steps": []
        }
        
        # Analyze requirements vs constraints
        if constraints.get("timeline_tight") and client_requirements.get("scope_large"):
            negotiation_result["timeline_adjustments"].append(
                "Consider MVP approach to meet timeline while delivering core value"
            )
        
        if constraints.get("budget_limited") and client_requirements.get("features_extensive"):
            negotiation_result["budget_considerations"].append(
                "Prioritize features by business impact to optimize budget allocation"
            )
        
        negotiation_result["next_steps"] = [
            "Review and approve adjusted scope",
            "Finalize timeline and milestones",
            "Sign development agreement",
            "Set up project infrastructure"
        ]
        
        return negotiation_result