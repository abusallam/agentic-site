"""
BMAD Service - Integration with BMAD Method for consulting agent
Implements BMAD methodology for strategic consulting and brainstorming
"""

import asyncio
import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from .gemini_service import GeminiService

logger = logging.getLogger(__name__)

class BMADService:
    """
    Service for integrating BMAD (Breakthrough Method of Agile AI-Driven Development)
    Provides strategic consulting capabilities using BMAD methodology
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.gemini_service = GeminiService(config)
        self.bmad_path = os.path.join(os.path.dirname(__file__), "../../../BMAD-METHOD")
        
        # BMAD agent roles and capabilities
        self.bmad_agents = {
            "analyst": {
                "name": "Mary",
                "role": "Business Analyst",
                "icon": "📊",
                "capabilities": [
                    "Market research and competitive analysis",
                    "Project briefing and discovery",
                    "Strategic brainstorming facilitation",
                    "Requirements elicitation",
                    "Business case development"
                ],
                "commands": [
                    "create-project-brief",
                    "perform-market-research", 
                    "create-competitor-analysis",
                    "brainstorm",
                    "research-prompt"
                ]
            },
            "architect": {
                "name": "Winston",
                "role": "System Architect",
                "icon": "🏗️",
                "capabilities": [
                    "Full-stack system architecture",
                    "Technology selection and evaluation",
                    "API design and infrastructure planning",
                    "Security architecture",
                    "Performance optimization"
                ],
                "commands": [
                    "create-full-stack-architecture",
                    "create-backend-architecture",
                    "create-front-end-architecture",
                    "document-project"
                ]
            },
            "orchestrator": {
                "name": "BMad Orchestrator",
                "role": "Master Orchestrator",
                "icon": "🎭",
                "capabilities": [
                    "Workflow coordination",
                    "Multi-agent task management",
                    "Role switching guidance",
                    "Process optimization"
                ],
                "commands": [
                    "workflow-guidance",
                    "plan",
                    "status",
                    "agent-coordination"
                ]
            }
        }
        
        # BMAD methodology phases
        self.bmad_phases = {
            "brainstorm": {
                "name": "Brainstorming & Ideation",
                "description": "Generate and explore ideas using structured brainstorming techniques",
                "duration": "30-60 minutes",
                "deliverables": ["Ideas list", "Concept prioritization", "Initial feasibility assessment"]
            },
            "analyze": {
                "name": "Analysis & Research",
                "description": "Deep dive analysis of market, competition, and technical requirements",
                "duration": "1-2 hours",
                "deliverables": ["Market research", "Competitive analysis", "Technical requirements"]
            },
            "architect": {
                "name": "Architecture & Design",
                "description": "System design and technical architecture planning",
                "duration": "2-4 hours", 
                "deliverables": ["System architecture", "Technology stack", "Implementation roadmap"]
            },
            "develop": {
                "name": "Development Planning",
                "description": "Detailed development planning and story creation",
                "duration": "1-2 hours",
                "deliverables": ["Development stories", "Sprint planning", "Resource allocation"]
            }
        }
    
    async def start_bmad_session(self, 
                                customer_id: str,
                                session_type: str = "strategic_consulting",
                                language: str = "en") -> Dict[str, Any]:
        """
        Start a BMAD methodology session
        
        Args:
            customer_id: Customer identifier
            session_type: Type of session (strategic_consulting, project_planning, etc.)
            language: Session language (en/ar)
            
        Returns:
            Session initialization result
        """
        try:
            session_id = f"bmad_{customer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Initialize session context
            session_context = {
                "session_id": session_id,
                "customer_id": customer_id,
                "session_type": session_type,
                "language": language,
                "current_phase": "brainstorm",
                "active_agent": "analyst",
                "created_at": datetime.now().isoformat(),
                "deliverables": {},
                "progress": {
                    "brainstorm": {"status": "active", "completion": 0},
                    "analyze": {"status": "pending", "completion": 0},
                    "architect": {"status": "pending", "completion": 0},
                    "develop": {"status": "pending", "completion": 0}
                }
            }
            
            # Generate welcome message using Gemini
            welcome_prompt = f"""As a BMAD methodology consultant, welcome the customer to a {session_type} session.

Explain:
1. The BMAD methodology phases (Brainstorm, Analyze, Architect, Develop)
2. What we'll accomplish in this session
3. How the process works with AI agents
4. Expected outcomes and deliverables

Language: {language}
Keep it professional, engaging, and culturally appropriate."""
            
            welcome_result = await self.gemini_service.generate_response(
                prompt=welcome_prompt,
                agent_type="consulting_agent",
                context=session_context,
                temperature=0.7,
                max_tokens=800
            )
            
            if welcome_result.get("success"):
                return {
                    "success": True,
                    "session_id": session_id,
                    "session_context": session_context,
                    "welcome_message": welcome_result["response"],
                    "current_phase": "brainstorm",
                    "active_agent": self.bmad_agents["analyst"],
                    "available_commands": self.bmad_agents["analyst"]["commands"],
                    "next_steps": [
                        "Share your project idea or business challenge",
                        "We'll start with structured brainstorming",
                        "Then move through analysis and architecture phases"
                    ]
                }
            else:
                return welcome_result
                
        except Exception as e:
            logger.error(f"Error starting BMAD session: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_bmad_command(self,
                                  session_id: str,
                                  command: str,
                                  parameters: Dict[str, Any] = None,
                                  user_input: str = None) -> Dict[str, Any]:
        """
        Execute a BMAD methodology command
        
        Args:
            session_id: BMAD session identifier
            command: Command to execute
            parameters: Command parameters
            user_input: User input for the command
            
        Returns:
            Command execution result
        """
        try:
            # Map commands to BMAD methodology
            command_mapping = {
                "brainstorm": self._execute_brainstorming,
                "analyze": self._execute_analysis,
                "research": self._execute_research,
                "architect": self._execute_architecture,
                "create-brief": self._create_project_brief,
                "market-research": self._perform_market_research,
                "competitor-analysis": self._create_competitor_analysis,
                "feasibility-study": self._conduct_feasibility_study
            }
            
            if command not in command_mapping:
                return {
                    "success": False,
                    "error": f"Unknown BMAD command: {command}",
                    "available_commands": list(command_mapping.keys())
                }
            
            # Execute the command
            result = await command_mapping[command](session_id, parameters or {}, user_input)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing BMAD command: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_brainstorming(self, session_id: str, parameters: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Execute structured brainstorming session"""
        try:
            topic = parameters.get("topic") or user_input
            if not topic:
                return {
                    "success": False,
                    "error": "Topic required for brainstorming session"
                }
            
            brainstorm_prompt = f"""As Mary, the Business Analyst using BMAD methodology, facilitate a structured brainstorming session.

TOPIC: {topic}

BRAINSTORMING FRAMEWORK:
1. **Divergent Thinking Phase**
   - Generate multiple ideas without judgment
   - Use techniques: Mind mapping, SCAMPER, What-if scenarios
   - Encourage creative and unconventional thinking

2. **Convergent Thinking Phase**
   - Evaluate and prioritize ideas
   - Apply feasibility and impact criteria
   - Select top 3-5 concepts for further development

3. **Action Planning**
   - Define next steps for selected ideas
   - Identify resources and requirements
   - Set priorities and timelines

OUTPUT FORMAT:
- Generated Ideas (10-15 ideas)
- Evaluation Criteria
- Top Priority Ideas (3-5)
- Recommended Next Steps
- Resource Requirements

Be creative, analytical, and actionable. Ask follow-up questions to deepen the exploration."""
            
            result = await self.gemini_service.generate_response(
                prompt=brainstorm_prompt,
                agent_type="consulting_agent",
                context={"session_id": session_id, "phase": "brainstorm", "topic": topic},
                temperature=0.8,
                max_tokens=2000
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "phase": "brainstorm",
                    "deliverable": "brainstorming_output",
                    "content": result["response"],
                    "next_phase": "analyze",
                    "recommendations": [
                        "Review and refine the generated ideas",
                        "Conduct market research on top concepts",
                        "Perform competitive analysis",
                        "Move to analysis phase when ready"
                    ]
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error in brainstorming execution: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_analysis(self, session_id: str, parameters: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Execute analysis phase"""
        try:
            analysis_type = parameters.get("type", "comprehensive")
            subject = parameters.get("subject") or user_input
            
            analysis_prompt = f"""As Mary, the Business Analyst, conduct a comprehensive analysis using BMAD methodology.

ANALYSIS SUBJECT: {subject}
ANALYSIS TYPE: {analysis_type}

ANALYSIS FRAMEWORK:
1. **Market Analysis**
   - Market size and growth potential
   - Target audience and segments
   - Market trends and drivers
   - Barriers to entry

2. **Competitive Landscape**
   - Direct and indirect competitors
   - Competitive advantages and weaknesses
   - Market positioning opportunities
   - Differentiation strategies

3. **Technical Feasibility**
   - Technical requirements and complexity
   - Available technologies and tools
   - Resource requirements
   - Implementation challenges

4. **Business Viability**
   - Revenue potential and models
   - Cost structure and investment needs
   - Risk assessment
   - Success metrics and KPIs

5. **Strategic Recommendations**
   - Go/No-go recommendation
   - Implementation approach
   - Resource allocation
   - Timeline and milestones

Provide detailed, data-informed analysis with actionable insights."""
            
            result = await self.gemini_service.generate_response(
                prompt=analysis_prompt,
                agent_type="consulting_agent",
                context={"session_id": session_id, "phase": "analyze", "subject": subject},
                temperature=0.6,
                max_tokens=2500
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "phase": "analyze",
                    "deliverable": "analysis_report",
                    "content": result["response"],
                    "next_phase": "architect",
                    "recommendations": [
                        "Review analysis findings with stakeholders",
                        "Validate assumptions with market data",
                        "Proceed to architecture phase if viable",
                        "Consider pilot or MVP approach"
                    ]
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error in analysis execution: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_research(self, session_id: str, parameters: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Execute research task"""
        try:
            research_topic = parameters.get("topic") or user_input
            research_depth = parameters.get("depth", "comprehensive")
            
            research_prompt = f"""As Mary, the Business Analyst, conduct deep research using BMAD methodology.

RESEARCH TOPIC: {research_topic}
RESEARCH DEPTH: {research_depth}

RESEARCH FRAMEWORK:
1. **Primary Research Areas**
   - Industry trends and developments
   - Market data and statistics
   - Technology landscape
   - Regulatory environment

2. **Secondary Research Sources**
   - Industry reports and whitepapers
   - Academic research and studies
   - Expert opinions and interviews
   - Case studies and best practices

3. **Research Questions**
   - What are the key trends affecting this area?
   - Who are the major players and what are they doing?
   - What technologies are emerging or maturing?
   - What are the opportunities and threats?

4. **Research Synthesis**
   - Key findings and insights
   - Implications for the project
   - Recommendations for action
   - Areas requiring further investigation

Provide comprehensive research with credible sources and actionable insights."""
            
            result = await self.gemini_service.generate_response(
                prompt=research_prompt,
                agent_type="consulting_agent",
                context={"session_id": session_id, "task": "research", "topic": research_topic},
                temperature=0.5,
                max_tokens=2000
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "deliverable": "research_report",
                    "content": result["response"],
                    "research_topic": research_topic,
                    "recommendations": [
                        "Validate findings with additional sources",
                        "Conduct stakeholder interviews if needed",
                        "Update analysis based on research insights",
                        "Document assumptions and limitations"
                    ]
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error in research execution: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_architecture(self, session_id: str, parameters: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Execute architecture phase - this will interact with code generation agent"""
        try:
            project_scope = parameters.get("scope") or user_input
            architecture_type = parameters.get("type", "full-stack")
            
            # This is where we'll interact with the code generation agent
            architecture_prompt = f"""As Winston, the System Architect, design a comprehensive architecture using BMAD methodology.

PROJECT SCOPE: {project_scope}
ARCHITECTURE TYPE: {architecture_type}

ARCHITECTURE FRAMEWORK:
1. **System Overview**
   - High-level architecture diagram
   - Core components and services
   - Data flow and interactions
   - Integration points

2. **Technology Stack**
   - Frontend technologies and frameworks
   - Backend services and APIs
   - Database and storage solutions
   - Infrastructure and deployment

3. **Security Architecture**
   - Authentication and authorization
   - Data protection and encryption
   - API security and rate limiting
   - Compliance requirements

4. **Performance & Scalability**
   - Performance requirements
   - Scalability considerations
   - Caching strategies
   - Load balancing and distribution

5. **Implementation Roadmap**
   - Development phases and milestones
   - Resource requirements
   - Risk mitigation strategies
   - Success criteria

Note: This architecture will be used by the Code Generation Agent for implementation."""
            
            result = await self.gemini_service.generate_response(
                prompt=architecture_prompt,
                agent_type="consulting_agent",
                context={"session_id": session_id, "phase": "architect", "scope": project_scope},
                temperature=0.6,
                max_tokens=2500
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "phase": "architect",
                    "deliverable": "architecture_document",
                    "content": result["response"],
                    "next_phase": "develop",
                    "handoff_to_code_agent": True,
                    "recommendations": [
                        "Review architecture with technical team",
                        "Validate technology choices",
                        "Hand off to Code Generation Agent for implementation",
                        "Begin development planning"
                    ]
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error in architecture execution: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _create_project_brief(self, session_id: str, parameters: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Create comprehensive project brief"""
        try:
            project_description = user_input or parameters.get("description", "")
            
            brief_prompt = f"""As Mary, the Business Analyst, create a comprehensive project brief using BMAD methodology.

PROJECT DESCRIPTION: {project_description}

PROJECT BRIEF TEMPLATE:
1. **Executive Summary**
   - Project overview and objectives
   - Key stakeholders and beneficiaries
   - Expected outcomes and success metrics

2. **Business Context**
   - Problem statement and opportunity
   - Market context and competitive landscape
   - Strategic alignment and business case

3. **Project Scope**
   - In-scope deliverables and features
   - Out-of-scope items and constraints
   - Assumptions and dependencies

4. **Requirements Overview**
   - Functional requirements (high-level)
   - Non-functional requirements
   - Technical constraints and preferences

5. **Success Criteria**
   - Key performance indicators (KPIs)
   - Acceptance criteria
   - Definition of done

6. **Resource Requirements**
   - Team composition and skills needed
   - Budget estimates and timeline
   - Technology and infrastructure needs

7. **Risk Assessment**
   - Identified risks and mitigation strategies
   - Critical success factors
   - Contingency planning

Create a professional, comprehensive project brief that can guide the entire development process."""
            
            result = await self.gemini_service.generate_response(
                prompt=brief_prompt,
                agent_type="consulting_agent",
                context={"session_id": session_id, "deliverable": "project_brief"},
                temperature=0.6,
                max_tokens=2500
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "deliverable": "project_brief",
                    "content": result["response"],
                    "recommendations": [
                        "Review brief with all stakeholders",
                        "Validate assumptions and requirements",
                        "Use as foundation for detailed planning",
                        "Update as project evolves"
                    ]
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error creating project brief: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _perform_market_research(self, session_id: str, parameters: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Perform comprehensive market research"""
        # Implementation similar to other methods
        # This would conduct detailed market research using BMAD methodology
        pass
    
    async def _create_competitor_analysis(self, session_id: str, parameters: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Create detailed competitor analysis"""
        # Implementation similar to other methods
        # This would analyze competitors using BMAD framework
        pass
    
    async def _conduct_feasibility_study(self, session_id: str, parameters: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Conduct comprehensive feasibility study"""
        # Implementation similar to other methods
        # This would assess technical and business feasibility
        pass
    
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get BMAD session status and progress"""
        try:
            # This would typically retrieve from database
            # For now, return mock status
            return {
                "success": True,
                "session_id": session_id,
                "current_phase": "brainstorm",
                "active_agent": "analyst",
                "progress": {
                    "brainstorm": {"status": "active", "completion": 60},
                    "analyze": {"status": "pending", "completion": 0},
                    "architect": {"status": "pending", "completion": 0},
                    "develop": {"status": "pending", "completion": 0}
                },
                "deliverables": {
                    "brainstorming_output": "completed",
                    "project_brief": "in_progress"
                },
                "next_steps": [
                    "Complete brainstorming session",
                    "Move to analysis phase",
                    "Conduct market research"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting session status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def close(self):
        """Close service connections"""
        await self.gemini_service.close()