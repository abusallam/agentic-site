"""
Agent-specific Celery tasks for distributed processing
"""
from celery import Task
from typing import Dict, Any, Optional
import logging
from .celery_app import celery_app
from ..agents import WelcomingAgent, N8NWorkflowAgent, ProfessionalAgent, ConsultingAgent
from ..agents.base_agent import AgentConfig, AgentType

logger = logging.getLogger(__name__)


class AgentTask(Task):
    """Base class for agent tasks with error handling"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        logger.error(f"Agent task {task_id} failed: {exc}")
        logger.error(f"Error info: {einfo}")
    
    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success"""
        logger.info(f"Agent task {task_id} completed successfully")


@celery_app.task(base=AgentTask, bind=True)
def process_customer_message(self, message: str, agent_type: str, context: Optional[Dict[str, Any]] = None):
    """Process customer message with specified agent"""
    try:
        # Create agent configuration
        config = AgentConfig(
            agent_type=AgentType(agent_type),
            framework="ADK",  # Default to ADK
            model_name="gemini-pro",
            temperature=0.7
        )
        
        # Initialize appropriate agent
        agent = _create_agent(agent_type, config)
        
        # Process message
        response = agent.process_message(message, context or {})
        
        # Store result in context for potential chaining
        self.update_state(
            state="SUCCESS",
            meta={
                "response": response.__dict__,
                "agent_type": agent_type,
                "processed_at": "2024-01-01T00:00:00Z"
            }
        )
        
        return {
            "status": "success",
            "response": response.__dict__,
            "agent_type": agent_type
        }
        
    except Exception as exc:
        logger.error(f"Error processing message with {agent_type}: {exc}")
        self.update_state(
            state="FAILURE",
            meta={
                "error": str(exc),
                "agent_type": agent_type
            }
        )
        raise


@celery_app.task(base=AgentTask, bind=True)
def route_to_agent(self, customer_intent: Dict[str, Any], context: Optional[Dict[str, Any]] = None):
    """Route customer to appropriate specialist agent"""
    try:
        service_type = customer_intent.get("service_type")
        
        # Determine target agent based on service type
        agent_mapping = {
            "fast_solution": "workflow",
            "custom_solution": "professional", 
            "consultation": "consulting"
        }
        
        target_agent = agent_mapping.get(service_type, "welcoming")
        
        # Create handoff data
        handoff_data = {
            "source_agent": "welcoming",
            "target_agent": target_agent,
            "customer_intent": customer_intent,
            "context": context or {},
            "handoff_timestamp": "2024-01-01T00:00:00Z"
        }
        
        # Chain to target agent processing
        next_task = process_customer_message.delay(
            message=customer_intent.get("original_message", ""),
            agent_type=target_agent,
            context=handoff_data
        )
        
        return {
            "status": "routed",
            "target_agent": target_agent,
            "next_task_id": next_task.id,
            "handoff_data": handoff_data
        }
        
    except Exception as exc:
        logger.error(f"Error routing to agent: {exc}")
        raise


@celery_app.task(base=AgentTask, bind=True)
def execute_agent_workflow(self, workflow_definition: Dict[str, Any], agent_type: str):
    """Execute complex agent workflow with multiple steps"""
    try:
        workflow_id = workflow_definition.get("id", "unknown")
        steps = workflow_definition.get("steps", [])
        
        results = []
        
        for step_idx, step in enumerate(steps):
            step_type = step.get("type")
            step_data = step.get("data", {})
            
            if step_type == "agent_processing":
                # Process with specified agent
                result = process_customer_message.delay(
                    message=step_data.get("message", ""),
                    agent_type=step_data.get("agent_type", agent_type),
                    context=step_data.get("context", {})
                )
                results.append({
                    "step": step_idx,
                    "type": step_type,
                    "task_id": result.id,
                    "status": "submitted"
                })
                
            elif step_type == "workflow_creation":
                # Create workflow (delegate to workflow tasks)
                from .workflow_tasks import create_n8n_workflow
                result = create_n8n_workflow.delay(step_data)
                results.append({
                    "step": step_idx,
                    "type": step_type,
                    "task_id": result.id,
                    "status": "submitted"
                })
                
            elif step_type == "research":
                # Conduct research
                result = conduct_research.delay(step_data.get("topics", []))
                results.append({
                    "step": step_idx,
                    "type": step_type,
                    "task_id": result.id,
                    "status": "submitted"
                })
        
        return {
            "status": "workflow_executing",
            "workflow_id": workflow_id,
            "steps_submitted": len(results),
            "step_results": results
        }
        
    except Exception as exc:
        logger.error(f"Error executing agent workflow: {exc}")
        raise


@celery_app.task(base=AgentTask)
def conduct_research(topics: list):
    """Conduct research on specified topics"""
    try:
        # Mock research implementation
        # In production, this would integrate with actual research tools
        research_results = {
            "topics": topics,
            "findings": [f"Research finding for {topic}" for topic in topics],
            "sources": [f"Source for {topic}" for topic in topics],
            "summary": f"Research completed for {len(topics)} topics",
            "completed_at": "2024-01-01T00:00:00Z"
        }
        
        return {
            "status": "research_completed",
            "results": research_results
        }
        
    except Exception as exc:
        logger.error(f"Error conducting research: {exc}")
        raise


@celery_app.task(base=AgentTask)
def schedule_consultation(customer_info: Dict[str, Any]):
    """Schedule consultation appointment"""
    try:
        # Mock scheduling implementation
        # In production, this would integrate with actual calendar system
        appointment = {
            "customer": customer_info.get("name", "Unknown"),
            "email": customer_info.get("email"),
            "scheduled_time": "2024-01-15T10:00:00Z",
            "duration": customer_info.get("duration", 60),
            "type": "consultation",
            "status": "scheduled"
        }
        
        return {
            "status": "consultation_scheduled",
            "appointment": appointment
        }
        
    except Exception as exc:
        logger.error(f"Error scheduling consultation: {exc}")
        raise


def _create_agent(agent_type: str, config: AgentConfig):
    """Factory function to create appropriate agent"""
    agent_classes = {
        "welcoming": WelcomingAgent,
        "workflow": N8NWorkflowAgent,
        "professional": ProfessionalAgent,
        "consulting": ConsultingAgent
    }
    
    agent_class = agent_classes.get(agent_type)
    if not agent_class:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    return agent_class(config)