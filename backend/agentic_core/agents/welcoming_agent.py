"""
Welcoming Agent - Initial customer interaction and routing
Routes customers to appropriate specialist agents based on their needs
"""
from typing import Dict, Any
from .base_agent import BaseAgent, AgentResponse, CustomerIntent, ServiceType, AgentConfig
import re
import logging

logger = logging.getLogger(__name__)


class WelcomingAgent(BaseAgent):
    """Initial customer interaction and routing agent"""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.routing_rules = {
            ServiceType.FAST_SOLUTION: self._route_to_n8n_agent,
            ServiceType.CUSTOM_SOLUTION: self._route_to_professional_agent,
            ServiceType.CONSULTATION: self._route_to_consulting_agent
        }
        self.intent_keywords = {
            ServiceType.FAST_SOLUTION: [
                "quick", "fast", "simple", "chatbot", "automation", "workflow",
                "n8n", "template", "ready-made", "immediate", "basic"
            ],
            ServiceType.CUSTOM_SOLUTION: [
                "custom", "development", "coding", "integration", "complex",
                "specific", "tailored", "professional", "enterprise", "api"
            ],
            ServiceType.CONSULTATION: [
                "consultation", "meeting", "discuss", "advice", "strategy",
                "planning", "research", "analysis", "calendar", "appointment"
            ]
        }
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the welcoming agent"""
        return """
        You are a Welcoming Agent for an AI consulting platform. Your role is to:
        
        1. Warmly greet customers and understand their needs
        2. Analyze their requirements to determine the best service type
        3. Route them to the appropriate specialist agent
        
        Service Types Available:
        - FAST_SOLUTION: N8N-based chatbots and workflows (quick, template-based)
        - CUSTOM_SOLUTION: Professional development and coding services
        - CONSULTATION: Strategic consulting with calendar scheduling
        
        Always be professional, helpful, and efficient in your routing decisions.
        Gather enough information to make an accurate routing decision.
        """
    
    def process_message(self, message: str, context: Dict[str, Any] = None) -> AgentResponse:
        """Process customer message and determine routing"""
        self.add_to_history("user", message)
        
        # Analyze customer intent
        intent = self.analyze_customer_intent(message)
        
        # Generate appropriate response
        response_message = self._generate_welcome_response(intent)
        
        # Determine next action based on intent
        next_action = self._determine_next_action(intent)
        
        response = AgentResponse(
            message=response_message,
            confidence=intent.confidence,
            next_action=next_action,
            context={
                "intent": intent,
                "service_type": intent.service_type.value,
                "requirements": intent.requirements
            }
        )
        
        self.add_to_history("assistant", response_message)
        return response
    
    def analyze_customer_intent(self, message: str) -> CustomerIntent:
        """Analyze customer message to determine service type"""
        message_lower = message.lower()
        scores = {service_type: 0 for service_type in ServiceType}
        
        # Keyword-based scoring
        for service_type, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    scores[service_type] += 1
        
        # Pattern-based scoring
        scores.update(self._pattern_based_scoring(message_lower))
        
        # Determine best match
        best_service = max(scores, key=scores.get)
        max_score = scores[best_service]
        total_keywords = sum(len(keywords) for keywords in self.intent_keywords.values())
        confidence = min(max_score / 3.0, 1.0)  # Normalize confidence
        
        # Extract requirements
        requirements = self._extract_requirements(message)
        
        return CustomerIntent(
            service_type=best_service,
            confidence=confidence,
            requirements=requirements,
            urgency=self._determine_urgency(message_lower)
        )
    
    def _pattern_based_scoring(self, message: str) -> Dict[ServiceType, int]:
        """Additional pattern-based scoring for better accuracy"""
        scores = {service_type: 0 for service_type in ServiceType}
        
        # Fast solution patterns
        if re.search(r'\b(need.*(quick|fast|simple)|simple.*(bot|automation))\b', message):
            scores[ServiceType.FAST_SOLUTION] += 2
        
        # Custom solution patterns
        if re.search(r'\b(custom.*(development|solution)|need.*(coding|programming))\b', message):
            scores[ServiceType.CUSTOM_SOLUTION] += 2
        
        # Consultation patterns
        if re.search(r'\b(want.*(meeting|consultation)|schedule.*(call|meeting))\b', message):
            scores[ServiceType.CONSULTATION] += 2
        
        return scores
    
    def _extract_requirements(self, message: str) -> Dict[str, Any]:
        """Extract basic requirements from customer message"""
        requirements = {
            "original_message": message,
            "extracted_features": []
        }
        
        # Extract mentioned technologies
        tech_patterns = {
            "platforms": r'\b(website|app|mobile|web|platform)\b',
            "integrations": r'\b(api|integration|connect|sync)\b',
            "automation": r'\b(automate|workflow|process|trigger)\b'
        }
        
        for category, pattern in tech_patterns.items():
            matches = re.findall(pattern, message.lower())
            if matches:
                requirements["extracted_features"].extend(matches)
        
        return requirements
    
    def _determine_urgency(self, message: str) -> str:
        """Determine urgency level from message"""
        urgent_keywords = ["urgent", "asap", "immediately", "emergency"]
        high_keywords = ["soon", "quickly", "fast", "rush"]
        
        if any(keyword in message for keyword in urgent_keywords):
            return "urgent"
        elif any(keyword in message for keyword in high_keywords):
            return "high"
        else:
            return "normal"
    
    def _generate_welcome_response(self, intent: CustomerIntent) -> str:
        """Generate appropriate welcome response based on intent"""
        base_greeting = "Hello! Welcome to our AI consulting platform. "
        
        if intent.service_type == ServiceType.FAST_SOLUTION:
            return (base_greeting + 
                   "I can see you're looking for a quick automation solution. "
                   "I'll connect you with our N8N Workflow Agent who can help you "
                   "set up chatbots and automated workflows quickly using our templates.")
        
        elif intent.service_type == ServiceType.CUSTOM_SOLUTION:
            return (base_greeting + 
                   "I understand you need a custom solution. "
                   "I'll connect you with our Professional Agent who specializes in "
                   "custom development, coding, and platform integrations.")
        
        elif intent.service_type == ServiceType.CONSULTATION:
            return (base_greeting + 
                   "I see you're interested in consultation services. "
                   "I'll connect you with our Consulting Agent who can schedule "
                   "a meeting and prepare research based on your requirements.")
        
        else:
            return (base_greeting + 
                   "I'd be happy to help you find the right solution. "
                   "Could you tell me more about what you're looking for?")
    
    def _determine_next_action(self, intent: CustomerIntent) -> str:
        """Determine the next action based on customer intent"""
        if intent.confidence > 0.7:
            return f"route_to_{intent.service_type.value}_agent"
        else:
            return "request_clarification"
    
    def _route_to_n8n_agent(self, intent: CustomerIntent) -> Dict[str, Any]:
        """Route to N8N Workflow Agent"""
        return {
            "agent": "n8n_workflow",
            "handoff_data": {
                "intent": intent,
                "context": "fast_solution_routing"
            }
        }
    
    def _route_to_professional_agent(self, intent: CustomerIntent) -> Dict[str, Any]:
        """Route to Professional Agent"""
        return {
            "agent": "professional",
            "handoff_data": {
                "intent": intent,
                "context": "custom_solution_routing"
            }
        }
    
    def _route_to_consulting_agent(self, intent: CustomerIntent) -> Dict[str, Any]:
        """Route to Consulting Agent"""
        return {
            "agent": "consulting",
            "handoff_data": {
                "intent": intent,
                "context": "consultation_routing"
            }
        }