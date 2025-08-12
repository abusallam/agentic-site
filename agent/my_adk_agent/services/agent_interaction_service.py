"""
Agent Interaction Service - Enables collaboration between different agents
Handles handoffs between consulting agent (BMAD) and code generation agent
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from .gemini_service import GeminiService
from .bmad_service import BMADService

logger = logging.getLogger(__name__)

class AgentInteractionService:
    """
    Service for managing interactions and handoffs between different agents
    Enables collaborative workflows between consulting and code generation agents
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.gemini_service = GeminiService(config)
        self.bmad_service = BMADService(config)
        
        # Agent interaction patterns
        self.interaction_patterns = {
            "consulting_to_code": {
                "trigger": "architecture_complete",
                "handoff_data": ["architecture_document", "technical_requirements", "project_scope"],
                "target_agent": "code_generation_agent",
                "expected_deliverables": ["implementation_plan", "code_structure", "development_roadmap"]
            },
            "code_to_consulting": {
                "trigger": "implementation_questions",
                "handoff_data": ["technical_challenges", "architecture_questions", "feasibility_concerns"],
                "target_agent": "consulting_agent",
                "expected_deliverables": ["strategic_guidance", "requirement_clarification", "solution_alternatives"]
            },
            "consulting_to_workflow": {
                "trigger": "automation_requirements",
                "handoff_data": ["process_definition", "integration_requirements", "automation_scope"],
                "target_agent": "n8n_workflow_agent",
                "expected_deliverables": ["workflow_templates", "integration_plan", "automation_roadmap"]
            }
        }
        
        # Active collaborations tracking
        self.active_collaborations = {}
    
    async def initiate_agent_handoff(self,
                                   source_agent: str,
                                   target_agent: str,
                                   handoff_context: Dict[str, Any],
                                   customer_id: str) -> Dict[str, Any]:
        """
        Initiate handoff between agents
        
        Args:
            source_agent: Agent initiating the handoff
            target_agent: Agent receiving the handoff
            handoff_context: Context and data for handoff
            customer_id: Customer identifier
            
        Returns:
            Handoff initiation result
        """
        try:
            collaboration_id = f"collab_{customer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Validate handoff pattern
            pattern_key = f"{source_agent}_to_{target_agent.replace('_agent', '')}"
            if pattern_key not in self.interaction_patterns:
                return {
                    "success": False,
                    "error": f"No interaction pattern defined for {source_agent} -> {target_agent}",
                    "available_patterns": list(self.interaction_patterns.keys())
                }
            
            pattern = self.interaction_patterns[pattern_key]
            
            # Prepare handoff package
            handoff_package = {
                "collaboration_id": collaboration_id,
                "source_agent": source_agent,
                "target_agent": target_agent,
                "handoff_context": handoff_context,
                "customer_id": customer_id,
                "initiated_at": datetime.now().isoformat(),
                "pattern": pattern,
                "status": "initiated"
            }
            
            # Generate handoff message for target agent
            handoff_prompt = f"""You are receiving a handoff from the {source_agent} agent.

HANDOFF CONTEXT:
{json.dumps(handoff_context, indent=2)}

COLLABORATION DETAILS:
- Collaboration ID: {collaboration_id}
- Source Agent: {source_agent}
- Expected Deliverables: {', '.join(pattern['expected_deliverables'])}

INSTRUCTIONS:
1. Review the provided context and deliverables
2. Acknowledge receipt of the handoff
3. Identify any questions or clarifications needed
4. Outline your approach to fulfill the expected deliverables
5. Provide an estimated timeline for completion

Please respond professionally and indicate your readiness to proceed with this collaboration."""
            
            handoff_result = await self.gemini_service.generate_response(
                prompt=handoff_prompt,
                agent_type=target_agent,
                context=handoff_package,
                temperature=0.6,
                max_tokens=1000
            )
            
            if handoff_result.get("success"):
                # Store active collaboration
                self.active_collaborations[collaboration_id] = handoff_package
                
                return {
                    "success": True,
                    "collaboration_id": collaboration_id,
                    "handoff_message": handoff_result["response"],
                    "target_agent_response": handoff_result["response"],
                    "expected_deliverables": pattern["expected_deliverables"],
                    "next_steps": [
                        "Review handoff context with target agent",
                        "Address any questions or clarifications",
                        "Begin collaborative work on deliverables",
                        "Monitor progress and provide updates"
                    ]
                }
            else:
                return handoff_result
                
        except Exception as e:
            logger.error(f"Error initiating agent handoff: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def facilitate_agent_collaboration(self,
                                           collaboration_id: str,
                                           message: str,
                                           sender_agent: str) -> Dict[str, Any]:
        """
        Facilitate ongoing collaboration between agents
        
        Args:
            collaboration_id: Collaboration identifier
            message: Message from one agent to another
            sender_agent: Agent sending the message
            
        Returns:
            Collaboration facilitation result
        """
        try:
            if collaboration_id not in self.active_collaborations:
                return {
                    "success": False,
                    "error": f"Collaboration {collaboration_id} not found",
                    "active_collaborations": list(self.active_collaborations.keys())
                }
            
            collaboration = self.active_collaborations[collaboration_id]
            
            # Determine recipient agent
            if sender_agent == collaboration["source_agent"]:
                recipient_agent = collaboration["target_agent"]
            elif sender_agent == collaboration["target_agent"]:
                recipient_agent = collaboration["source_agent"]
            else:
                return {
                    "success": False,
                    "error": f"Agent {sender_agent} not part of collaboration {collaboration_id}"
                }
            
            # Generate response from recipient agent
            collaboration_prompt = f"""You are participating in an ongoing collaboration (ID: {collaboration_id}).

COLLABORATION CONTEXT:
- You are the {recipient_agent}
- Collaborating with: {sender_agent}
- Project: {collaboration['handoff_context'].get('project_name', 'Unnamed Project')}

MESSAGE FROM {sender_agent.upper()}:
{message}

INSTRUCTIONS:
1. Respond to the message professionally and constructively
2. Provide any requested information or clarification
3. Ask follow-up questions if needed
4. Suggest next steps or actions
5. Maintain focus on the collaboration objectives

Please respond as the {recipient_agent} would, staying in character and providing value to the collaboration."""
            
            response_result = await self.gemini_service.generate_response(
                prompt=collaboration_prompt,
                agent_type=recipient_agent,
                context=collaboration,
                temperature=0.7,
                max_tokens=1200
            )
            
            if response_result.get("success"):
                # Update collaboration log
                if "conversation_log" not in collaboration:
                    collaboration["conversation_log"] = []
                
                collaboration["conversation_log"].append({
                    "timestamp": datetime.now().isoformat(),
                    "sender": sender_agent,
                    "recipient": recipient_agent,
                    "message": message,
                    "response": response_result["response"]
                })
                
                return {
                    "success": True,
                    "collaboration_id": collaboration_id,
                    "sender": sender_agent,
                    "recipient": recipient_agent,
                    "response": response_result["response"],
                    "conversation_length": len(collaboration["conversation_log"])
                }
            else:
                return response_result
                
        except Exception as e:
            logger.error(f"Error facilitating agent collaboration: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_bmad_to_code_handoff(self,
                                         bmad_session_id: str,
                                         architecture_document: str,
                                         customer_id: str) -> Dict[str, Any]:
        """
        Execute specific handoff from BMAD consulting to code generation
        
        Args:
            bmad_session_id: BMAD session identifier
            architecture_document: Architecture document from BMAD
            customer_id: Customer identifier
            
        Returns:
            Handoff execution result
        """
        try:
            # Prepare handoff context
            handoff_context = {
                "bmad_session_id": bmad_session_id,
                "architecture_document": architecture_document,
                "project_name": f"Project for Customer {customer_id}",
                "handoff_type": "architecture_to_implementation",
                "deliverables_needed": [
                    "Implementation plan with timeline",
                    "Code structure and organization",
                    "Technology stack validation",
                    "Development roadmap with milestones"
                ]
            }
            
            # Initiate handoff
            handoff_result = await self.initiate_agent_handoff(
                source_agent="consulting_agent",
                target_agent="code_generation_agent", 
                handoff_context=handoff_context,
                customer_id=customer_id
            )
            
            if handoff_result.get("success"):
                # Generate implementation plan using code generation agent
                implementation_prompt = f"""As the Code Generation Agent, you've received an architecture document from the Consulting Agent.

ARCHITECTURE DOCUMENT:
{architecture_document}

TASK: Create a comprehensive implementation plan that includes:

1. **Code Structure Analysis**
   - Recommended project structure
   - Key modules and components
   - Framework selection rationale

2. **Implementation Roadmap**
   - Development phases (MVP, Beta, Production)
   - Sprint planning with 2-week iterations
   - Milestone definitions and success criteria

3. **Technology Stack Validation**
   - Validate proposed technologies
   - Suggest alternatives if needed
   - Identify potential technical risks

4. **Development Approach**
   - Recommended development methodology
   - Testing strategy and quality assurance
   - Deployment and DevOps considerations

5. **Resource Requirements**
   - Team composition and skills needed
   - Development timeline estimates
   - Infrastructure and tooling requirements

Provide a detailed, actionable implementation plan that the development team can follow."""
                
                implementation_result = await self.gemini_service.generate_response(
                    prompt=implementation_prompt,
                    agent_type="code_generation_agent",
                    context=handoff_context,
                    temperature=0.6,
                    max_tokens=2500
                )
                
                if implementation_result.get("success"):
                    return {
                        "success": True,
                        "collaboration_id": handoff_result["collaboration_id"],
                        "handoff_completed": True,
                        "implementation_plan": implementation_result["response"],
                        "deliverables": {
                            "architecture_document": "received",
                            "implementation_plan": "completed",
                            "code_structure": "outlined",
                            "development_roadmap": "created"
                        },
                        "next_steps": [
                            "Review implementation plan with stakeholders",
                            "Begin development team formation",
                            "Set up development environment",
                            "Start MVP development phase"
                        ]
                    }
                else:
                    return implementation_result
            else:
                return handoff_result
                
        except Exception as e:
            logger.error(f"Error executing BMAD to code handoff: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_collaboration_status(self, collaboration_id: str) -> Dict[str, Any]:
        """
        Get status of ongoing collaboration
        
        Args:
            collaboration_id: Collaboration identifier
            
        Returns:
            Collaboration status information
        """
        try:
            if collaboration_id not in self.active_collaborations:
                return {
                    "success": False,
                    "error": f"Collaboration {collaboration_id} not found"
                }
            
            collaboration = self.active_collaborations[collaboration_id]
            
            return {
                "success": True,
                "collaboration_id": collaboration_id,
                "source_agent": collaboration["source_agent"],
                "target_agent": collaboration["target_agent"],
                "status": collaboration["status"],
                "initiated_at": collaboration["initiated_at"],
                "conversation_length": len(collaboration.get("conversation_log", [])),
                "expected_deliverables": collaboration["pattern"]["expected_deliverables"],
                "progress_summary": "Collaboration active and progressing"
            }
            
        except Exception as e:
            logger.error(f"Error getting collaboration status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def complete_collaboration(self, 
                                   collaboration_id: str,
                                   final_deliverables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete and close a collaboration
        
        Args:
            collaboration_id: Collaboration identifier
            final_deliverables: Final deliverables from the collaboration
            
        Returns:
            Collaboration completion result
        """
        try:
            if collaboration_id not in self.active_collaborations:
                return {
                    "success": False,
                    "error": f"Collaboration {collaboration_id} not found"
                }
            
            collaboration = self.active_collaborations[collaboration_id]
            
            # Update collaboration status
            collaboration["status"] = "completed"
            collaboration["completed_at"] = datetime.now().isoformat()
            collaboration["final_deliverables"] = final_deliverables
            
            # Generate completion summary
            summary_prompt = f"""Generate a collaboration completion summary.

COLLABORATION DETAILS:
- ID: {collaboration_id}
- Agents: {collaboration['source_agent']} -> {collaboration['target_agent']}
- Duration: {collaboration['initiated_at']} to {collaboration['completed_at']}

FINAL DELIVERABLES:
{json.dumps(final_deliverables, indent=2)}

CONVERSATION LOG:
{len(collaboration.get('conversation_log', []))} messages exchanged

Create a professional summary of what was accomplished, key outcomes, and recommendations for next steps."""
            
            summary_result = await self.gemini_service.generate_response(
                prompt=summary_prompt,
                agent_type="consulting_agent",
                context=collaboration,
                temperature=0.5,
                max_tokens=800
            )
            
            # Archive the collaboration
            archived_collaboration = collaboration.copy()
            del self.active_collaborations[collaboration_id]
            
            return {
                "success": True,
                "collaboration_id": collaboration_id,
                "status": "completed",
                "summary": summary_result.get("response", "Collaboration completed successfully"),
                "final_deliverables": final_deliverables,
                "archived": True
            }
            
        except Exception as e:
            logger.error(f"Error completing collaboration: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def close(self):
        """Close service connections"""
        await self.gemini_service.close()
        await self.bmad_service.close()