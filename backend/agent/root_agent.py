"""Root Agent - Master orchestrator for all specialized agents."""

import json
import logging
from typing import Dict, Any, Optional, List
from google.adk.agents.base_agent import BaseAgent

# Import specialized agents
from my_adk_agent.agent import AccountantAgent
from my_adk_agent.calendar_agent import CalendarAgent
from n8n_mcp_agent.agent import N8nMCPAgent
from specialized_agents.sales_agent import SalesAgent

from my_adk_agent.services import (
    SupabaseService,
    LivekitService,
    MCPService,
)

logger = logging.getLogger(__name__)


class RootAgent(BaseAgent):
    """
    Root Agent - Master orchestrator that coordinates all specialized agents
    and manages the complete customer journey from initial contact to delivery.
    """
    
    def __init__(self):
        """Initialize the root agent with all specialized agents."""
        super().__init__(
            name="root_agent",
            description="Master orchestrator agent that coordinates all specialized agents and manages customer projects"
        )
        
        # Initialize core services
        object.__setattr__(self, 'supabase_service', SupabaseService())
        object.__setattr__(self, 'livekit_service', LivekitService())
        object.__setattr__(self, 'mcp_service', MCPService())
        
        # Initialize specialized agents
        object.__setattr__(self, 'accountant_agent', AccountantAgent())
        object.__setattr__(self, 'calendar_agent', CalendarAgent())
        object.__setattr__(self, 'n8n_agent', N8nMCPAgent())
        object.__setattr__(self, 'sales_agent', SalesAgent())
        
        # Project state management
        object.__setattr__(self, 'active_projects', {})
        object.__setattr__(self, 'agent_assignments', {})
        
        logger.info("RootAgent initialized with all specialized agents")
    
    async def initiate_customer_journey(self, customer_email: str, initial_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiate the complete customer journey from chatbot handoff.
        This is called when the chatbot transfers to live session.
        """
        try:
            logger.info(f"Initiating customer journey for: {customer_email}")
            
            # Create project record
            project_id = f"proj_{customer_email}_{int(datetime.now().timestamp())}"
            
            project_data = {
                "project_id": project_id,
                "customer_email": customer_email,
                "status": "requirements_gathering",
                "initial_requirements": initial_requirements,
                "created_at": datetime.now().isoformat(),
                "agents_assigned": [],
                "tasks": [],
                "phase": "discovery"
            }
            
            # Store project in active projects
            self.active_projects[project_id] = project_data
            
            # Schedule requirements gathering session
            session_result = await self._schedule_requirements_session(customer_email, project_id)
            
            # Assign initial agents
            assigned_agents = await self._assign_initial_agents(project_id, initial_requirements)
            
            return {
                "status": "success",
                "project_id": project_id,
                "phase": "discovery",
                "session": session_result,
                "assigned_agents": assigned_agents,
                "next_steps": [
                    "Live requirements gathering session scheduled",
                    "Root agent will monitor session",
                    "Detailed project plan will be created",
                    "Specialized agents will be assigned tasks"
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to initiate customer journey: {e}")
            return {"status": "error", "error": str(e)}
    
    async def join_live_session(self, session_id: str, project_id: str) -> Dict[str, Any]:
        """
        Join live Livekit session to monitor requirements gathering.
        Root agent listens and extracts detailed requirements.
        """
        try:
            logger.info(f"Root agent joining live session: {session_id}")
            
            # Join Livekit session as silent participant
            session_token = await self.livekit_service.generate_access_token(
                session_id, "root_agent", is_agent=True, permissions={"canPublish": False}
            )
            
            # Start monitoring session
            monitoring_result = await self.livekit_service.monitor_session_with_ai(
                session_id, self._process_live_conversation
            )
            
            # Update project status
            if project_id in self.active_projects:
                self.active_projects[project_id]["status"] = "live_session_active"
                self.active_projects[project_id]["session_id"] = session_id
            
            return {
                "status": "success",
                "session_id": session_id,
                "monitoring_active": True,
                "agent_role": "silent_observer",
                "capabilities": [
                    "Real-time requirements extraction",
                    "Technical feasibility analysis",
                    "Resource estimation",
                    "Agent assignment planning"
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to join live session: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _process_live_conversation(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process live conversation to extract detailed requirements.
        This is called in real-time during the Livekit session.
        """
        try:
            speaker = conversation_data.get("speaker")
            message = conversation_data.get("message")
            timestamp = conversation_data.get("timestamp")
            
            logger.info(f"Processing conversation: {speaker} - {message[:100]}...")
            
            # Extract requirements from conversation
            extracted_requirements = await self._extract_requirements_from_conversation(message, speaker)
            
            # Update project with new requirements
            project_id = conversation_data.get("project_id")
            if project_id and project_id in self.active_projects:
                project = self.active_projects[project_id]
                
                # Merge new requirements
                if "detailed_requirements" not in project:
                    project["detailed_requirements"] = {}
                
                project["detailed_requirements"].update(extracted_requirements)
                project["last_updated"] = timestamp
                
                # Check if we have enough information to proceed
                completeness_score = await self._assess_requirements_completeness(project["detailed_requirements"])
                
                if completeness_score >= 0.8:  # 80% complete
                    # Trigger project planning phase
                    await self._trigger_project_planning(project_id)
            
            return {
                "status": "processed",
                "extracted_requirements": extracted_requirements,
                "timestamp": timestamp
            }
            
        except Exception as e:
            logger.error(f"Failed to process conversation: {e}")
            return {"status": "error", "error": str(e)}
    
    async def orchestrate_project(self, project_id: str) -> Dict[str, Any]:
        """
        Orchestrate the complete project by assigning tasks to specialized agents.
        """
        try:
            logger.info(f"Orchestrating project: {project_id}")
            
            if project_id not in self.active_projects:
                return {"status": "error", "error": "Project not found"}
            
            project = self.active_projects[project_id]
            requirements = project.get("detailed_requirements", {})
            
            # Create project plan
            project_plan = await self._create_project_plan(requirements)
            
            # Assign tasks to specialized agents
            task_assignments = await self._assign_tasks_to_agents(project_plan)
            
            # Update project status
            project["status"] = "in_progress"
            project["phase"] = "execution"
            project["project_plan"] = project_plan
            project["task_assignments"] = task_assignments
            
            # Start task execution
            execution_results = await self._execute_project_tasks(project_id, task_assignments)
            
            return {
                "status": "success",
                "project_id": project_id,
                "phase": "execution",
                "project_plan": project_plan,
                "task_assignments": task_assignments,
                "execution_status": execution_results
            }
            
        except Exception as e:
            logger.error(f"Failed to orchestrate project: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _create_project_plan(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed project plan based on requirements."""
        try:
            service_type = requirements.get("service_type", "unknown")
            complexity = requirements.get("complexity", "medium")
            timeline = requirements.get("timeline", "flexible")
            
            # Define project phases
            phases = []
            
            # Phase 1: Setup & Configuration
            phases.append({
                "phase": "setup",
                "tasks": [
                    {"task": "create_customer_account", "agent": "accountant", "priority": "high"},
                    {"task": "setup_billing", "agent": "accountant", "priority": "high"},
                    {"task": "schedule_kickoff", "agent": "calendar", "priority": "medium"}
                ],
                "estimated_duration": "1-2 days"
            })
            
            # Phase 2: Development
            if service_type in ["chatbot", "ai_agent"]:
                phases.append({
                    "phase": "development",
                    "tasks": [
                        {"task": "create_n8n_workflow", "agent": "n8n", "priority": "high"},
                        {"task": "configure_ai_model", "agent": "n8n", "priority": "high"},
                        {"task": "setup_integrations", "agent": "n8n", "priority": "medium"}
                    ],
                    "estimated_duration": "3-7 days"
                })
            
            # Phase 3: Testing & Deployment
            phases.append({
                "phase": "testing",
                "tasks": [
                    {"task": "run_integration_tests", "agent": "n8n", "priority": "high"},
                    {"task": "user_acceptance_testing", "agent": "sales", "priority": "medium"},
                    {"task": "deploy_to_production", "agent": "n8n", "priority": "high"}
                ],
                "estimated_duration": "2-3 days"
            })
            
            # Phase 4: Delivery & Support
            phases.append({
                "phase": "delivery",
                "tasks": [
                    {"task": "generate_invoice", "agent": "accountant", "priority": "high"},
                    {"task": "schedule_handover", "agent": "calendar", "priority": "medium"},
                    {"task": "setup_support", "agent": "sales", "priority": "low"}
                ],
                "estimated_duration": "1 day"
            })
            
            return {
                "service_type": service_type,
                "complexity": complexity,
                "timeline": timeline,
                "phases": phases,
                "total_estimated_duration": "7-13 days",
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to create project plan: {e}")
            return {}
    
    async def _assign_tasks_to_agents(self, project_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Assign specific tasks to specialized agents."""
        try:
            assignments = {
                "accountant": [],
                "calendar": [],
                "n8n": [],
                "sales": []
            }
            
            # Process each phase and assign tasks
            for phase in project_plan.get("phases", []):
                for task in phase.get("tasks", []):
                    agent_type = task.get("agent")
                    if agent_type in assignments:
                        assignments[agent_type].append({
                            "task_id": f"{phase['phase']}_{task['task']}",
                            "task_name": task["task"],
                            "phase": phase["phase"],
                            "priority": task.get("priority", "medium"),
                            "status": "assigned",
                            "assigned_at": datetime.now().isoformat()
                        })
            
            return assignments
            
        except Exception as e:
            logger.error(f"Failed to assign tasks: {e}")
            return {}
    
    async def _execute_project_tasks(self, project_id: str, task_assignments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tasks by delegating to specialized agents."""
        try:
            execution_results = {}
            
            # Execute tasks for each agent type
            for agent_type, tasks in task_assignments.items():
                agent_results = []
                
                for task in tasks:
                    result = await self._execute_single_task(agent_type, task, project_id)
                    agent_results.append(result)
                
                execution_results[agent_type] = {
                    "total_tasks": len(tasks),
                    "completed_tasks": len([r for r in agent_results if r.get("status") == "success"]),
                    "failed_tasks": len([r for r in agent_results if r.get("status") == "error"]),
                    "results": agent_results
                }
            
            return execution_results
            
        except Exception as e:
            logger.error(f"Failed to execute project tasks: {e}")
            return {}
    
    async def _execute_single_task(self, agent_type: str, task: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """Execute a single task using the appropriate specialized agent."""
        try:
            task_name = task.get("task_name")
            logger.info(f"Executing task: {task_name} with {agent_type} agent")
            
            # Get project context
            project = self.active_projects.get(project_id, {})
            customer_email = project.get("customer_email")
            requirements = project.get("detailed_requirements", {})
            
            # Route to appropriate agent
            if agent_type == "accountant":
                result = await self._execute_accountant_task(task_name, customer_email, requirements)
            elif agent_type == "calendar":
                result = await self._execute_calendar_task(task_name, customer_email, requirements)
            elif agent_type == "n8n":
                result = await self._execute_n8n_task(task_name, customer_email, requirements)
            elif agent_type == "sales":
                result = await self._execute_sales_task(task_name, customer_email, requirements)
            else:
                result = {"status": "error", "error": f"Unknown agent type: {agent_type}"}
            
            # Update task status
            task["status"] = result.get("status", "error")
            task["completed_at"] = datetime.now().isoformat()
            task["result"] = result
            
            return {
                "task_id": task.get("task_id"),
                "task_name": task_name,
                "agent_type": agent_type,
                "status": result.get("status", "error"),
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Failed to execute single task: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _execute_accountant_task(self, task_name: str, customer_email: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Execute accountant-specific tasks."""
        if task_name == "create_customer_account":
            return await self.accountant_agent.create_customer_record(customer_email, requirements.get("customer_name"))
        elif task_name == "setup_billing":
            return await self.accountant_agent.setup_billing_profile(customer_email, requirements)
        elif task_name == "generate_invoice":
            return await self.accountant_agent.generate_invoice(customer_email, requirements)
        else:
            return {"status": "error", "error": f"Unknown accountant task: {task_name}"}
    
    async def _execute_calendar_task(self, task_name: str, customer_email: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Execute calendar-specific tasks."""
        if task_name == "schedule_kickoff":
            return await self.calendar_agent.schedule_appointment(
                customer_email, "project_kickoff", 
                requirements.get("preferred_start_date", ""), 
                requirements.get("preferred_time", "10:00")
            )
        elif task_name == "schedule_handover":
            return await self.calendar_agent.schedule_appointment(
                customer_email, "project_handover", 
                "", "14:00"  # Default afternoon handover
            )
        else:
            return {"status": "error", "error": f"Unknown calendar task: {task_name}"}
    
    async def _execute_n8n_task(self, task_name: str, customer_email: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Execute n8n workflow tasks."""
        if task_name == "create_n8n_workflow":
            return await self.n8n_agent.create_workflow_for_customer(customer_email, requirements)
        elif task_name == "configure_ai_model":
            return await self.n8n_agent.configure_ai_model(customer_email, requirements)
        elif task_name == "setup_integrations":
            return await self.n8n_agent.setup_integrations(customer_email, requirements)
        elif task_name == "run_integration_tests":
            return await self.n8n_agent.run_integration_tests(customer_email)
        elif task_name == "deploy_to_production":
            return await self.n8n_agent.deploy_to_production(customer_email)
        else:
            return {"status": "error", "error": f"Unknown n8n task: {task_name}"}
    
    async def _execute_sales_task(self, task_name: str, customer_email: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Execute sales-specific tasks."""
        if task_name == "user_acceptance_testing":
            return await self.sales_agent.coordinate_user_testing(customer_email, requirements)
        elif task_name == "setup_support":
            return await self.sales_agent.setup_ongoing_support(customer_email, requirements)
        else:
            return {"status": "error", "error": f"Unknown sales task: {task_name}"}
    
    async def test_project_delivery(self, project_id: str) -> Dict[str, Any]:
        """Test the complete project delivery before final handover."""
        try:
            logger.info(f"Testing project delivery: {project_id}")
            
            if project_id not in self.active_projects:
                return {"status": "error", "error": "Project not found"}
            
            project = self.active_projects[project_id]
            customer_email = project.get("customer_email")
            
            # Run comprehensive tests
            test_results = {
                "functional_tests": await self._run_functional_tests(project_id),
                "integration_tests": await self._run_integration_tests(project_id),
                "performance_tests": await self._run_performance_tests(project_id),
                "user_acceptance_tests": await self._run_user_acceptance_tests(project_id)
            }
            
            # Calculate overall success rate
            total_tests = sum(len(tests.get("results", [])) for tests in test_results.values())
            passed_tests = sum(len([t for t in tests.get("results", []) if t.get("status") == "passed"]) 
                             for tests in test_results.values())
            
            success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            
            # Update project status
            project["test_results"] = test_results
            project["success_rate"] = success_rate
            
            if success_rate >= 90:  # 90% success rate required
                project["status"] = "ready_for_delivery"
                project["phase"] = "delivery"
            else:
                project["status"] = "needs_fixes"
                project["phase"] = "testing"
            
            return {
                "status": "success",
                "project_id": project_id,
                "test_results": test_results,
                "success_rate": success_rate,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "ready_for_delivery": success_rate >= 90
            }
            
        except Exception as e:
            logger.error(f"Failed to test project delivery: {e}")
            return {"status": "error", "error": str(e)}
    
    async def deliver_project(self, project_id: str) -> Dict[str, Any]:
        """Final project delivery and handover to customer."""
        try:
            logger.info(f"Delivering project: {project_id}")
            
            if project_id not in self.active_projects:
                return {"status": "error", "error": "Project not found"}
            
            project = self.active_projects[project_id]
            
            # Ensure project is ready for delivery
            if project.get("status") != "ready_for_delivery":
                return {"status": "error", "error": "Project not ready for delivery"}
            
            customer_email = project.get("customer_email")
            
            # Final delivery tasks
            delivery_tasks = [
                await self.accountant_agent.generate_final_invoice(customer_email, project),
                await self.calendar_agent.schedule_handover_meeting(customer_email),
                await self.n8n_agent.finalize_deployment(customer_email),
                await self.sales_agent.setup_ongoing_support(customer_email, project)
            ]
            
            # Update project status
            project["status"] = "delivered"
            project["phase"] = "completed"
            project["delivered_at"] = datetime.now().isoformat()
            project["delivery_tasks"] = delivery_tasks
            
            # Archive project
            await self._archive_project(project_id)
            
            return {
                "status": "success",
                "project_id": project_id,
                "delivered_at": project["delivered_at"],
                "delivery_tasks": delivery_tasks,
                "customer_email": customer_email,
                "message": "Project successfully delivered to customer"
            }
            
        except Exception as e:
            logger.error(f"Failed to deliver project: {e}")
            return {"status": "error", "error": str(e)}
    
    # Helper methods for testing
    async def _run_functional_tests(self, project_id: str) -> Dict[str, Any]:
        """Run functional tests on the project."""
        # Mock implementation
        return {
            "status": "completed",
            "results": [
                {"test": "basic_functionality", "status": "passed"},
                {"test": "error_handling", "status": "passed"},
                {"test": "input_validation", "status": "passed"}
            ]
        }
    
    async def _run_integration_tests(self, project_id: str) -> Dict[str, Any]:
        """Run integration tests."""
        # Mock implementation
        return {
            "status": "completed",
            "results": [
                {"test": "api_integration", "status": "passed"},
                {"test": "database_connection", "status": "passed"},
                {"test": "external_services", "status": "passed"}
            ]
        }
    
    async def _run_performance_tests(self, project_id: str) -> Dict[str, Any]:
        """Run performance tests."""
        # Mock implementation
        return {
            "status": "completed",
            "results": [
                {"test": "response_time", "status": "passed", "value": "< 2s"},
                {"test": "throughput", "status": "passed", "value": "100 req/min"},
                {"test": "resource_usage", "status": "passed", "value": "< 512MB"}
            ]
        }
    
    async def _run_user_acceptance_tests(self, project_id: str) -> Dict[str, Any]:
        """Run user acceptance tests."""
        # Mock implementation
        return {
            "status": "completed",
            "results": [
                {"test": "user_interface", "status": "passed"},
                {"test": "user_experience", "status": "passed"},
                {"test": "business_requirements", "status": "passed"}
            ]
        }
    
    async def run(self, user_input: str) -> str:
        """Main entry point for root agent execution."""
        try:
            logger.info(f"Root agent processing: {user_input[:100]}...")
            
            # Try to parse as JSON command first
            try:
                command = json.loads(user_input)
                if isinstance(command, dict) and "action" in command:
                    return await self._handle_command(command)
            except json.JSONDecodeError:
                pass
            
            # Handle as natural language input
            return await self._handle_natural_language(user_input)
            
        except Exception as e:
            logger.error(f"Error in root agent run: {e}")
            return f"I encountered an error: {str(e)}. Please try again or contact support."
    
    async def _handle_command(self, command: Dict[str, Any]) -> str:
        """Handle structured JSON commands."""
        action = command.get("action")
        params = command.get("params", {})
        
        if action == "initiate_journey":
            result = await self.initiate_customer_journey(
                customer_email=params.get("email"),
                initial_requirements=params.get("requirements", {})
            )
        elif action == "join_session":
            result = await self.join_live_session(
                session_id=params.get("session_id"),
                project_id=params.get("project_id")
            )
        elif action == "orchestrate_project":
            result = await self.orchestrate_project(
                project_id=params.get("project_id")
            )
        elif action == "test_delivery":
            result = await self.test_project_delivery(
                project_id=params.get("project_id")
            )
        elif action == "deliver_project":
            result = await self.deliver_project(
                project_id=params.get("project_id")
            )
        else:
            return f"Unknown root agent action: {action}"
        
        return json.dumps(result, indent=2)
    
    async def _handle_natural_language(self, user_input: str) -> str:
        """Handle natural language input for root agent operations."""
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ["orchestrate", "manage", "coordinate"]):
            return """🎯 **Root Agent** - Master Project Orchestrator

I coordinate all specialized agents and manage complete customer projects:

**🚀 Customer Journey Management:**
• Initiate customer journey from chatbot handoff
• Join live sessions to extract requirements
• Create detailed project plans
• Assign tasks to specialized agents

**🤖 Agent Coordination:**
• **Accountant Agent** - Billing, invoicing, payments
• **Calendar Agent** - Scheduling, appointments
• **N8N Agent** - Workflow automation, AI deployment
• **Sales Agent** - Customer relations, support

**📋 Project Phases:**
1. **Discovery** - Requirements gathering via live session
2. **Planning** - Create project plan and assign tasks
3. **Execution** - Coordinate specialized agents
4. **Testing** - Comprehensive testing and validation
5. **Delivery** - Final handover to customer

**Commands:**
```json
{
  "action": "initiate_journey",
  "params": {
    "email": "customer@example.com",
    "requirements": {...}
  }
}
```

What project would you like me to orchestrate?"""
        
        elif any(word in input_lower for word in ["status", "project", "active"]):
            active_count = len(self.active_projects)
            return f"""📊 **Root Agent Status**

**Active Projects:** {active_count}
**Specialized Agents:** 4 (Accountant, Calendar, N8N, Sales)
**System Status:** ✅ All agents operational

**Recent Activity:**
{chr(10).join([f"• Project {pid}: {proj.get('status', 'unknown')}" for pid, proj in list(self.active_projects.items())[-5:]])}

Use commands to manage projects or ask about specific functionality."""
        
        else:
            return """🎯 **Root Agent** - Master Project Orchestrator

I'm the central coordinator that manages your complete customer journey:

**🔄 Workflow:**
1. **Chatbot** → Initial customer contact
2. **Live Session** → Detailed requirements (I monitor & extract)
3. **Project Planning** → I create comprehensive plans
4. **Task Assignment** → I coordinate specialized agents
5. **Testing & Delivery** → I ensure quality and completion

**🤖 My Specialized Agents:**
• **Accountant** - Financial operations
• **Calendar** - Scheduling & appointments  
• **N8N** - Workflow automation & AI
• **Sales** - Customer relations & support

**💡 I can help you:**
• Start new customer projects
• Monitor live requirement sessions
• Coordinate multi-agent workflows
• Test and validate deliverables
• Manage project delivery

What would you like me to orchestrate today?"""


# Import datetime at the top
from datetime import datetime