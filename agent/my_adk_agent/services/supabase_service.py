"""
Supabase Service - Database operations for the multi-agent system
Handles all database interactions for customers, workflows, projects, and consultations
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from supabase import create_client, Client
import logging

from ..models.customer import Customer, CustomerInquiry
from ..models.workflow import Workflow, WorkflowExecution
from ..models.project import Project, CodeGeneration
from ..models.consultation import Consultation, ConsultationSession

logger = logging.getLogger(__name__)

class SupabaseService:
    """
    Service for all database operations using Supabase
    Provides CRUD operations for all data models
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.supabase_url = config.get("SUPABASE_URL")
        self.supabase_key = config.get("SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
    
    # Customer operations
    async def create_customer(self, customer_data: Dict[str, Any]) -> Customer:
        """Create a new customer"""
        try:
            result = self.client.table("customers").insert(customer_data).execute()
            
            if result.data:
                logger.info(f"Customer created: {result.data[0]['id']}")
                return Customer(**result.data[0])
            else:
                raise Exception("Failed to create customer")
                
        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            raise
    
    async def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get customer by ID"""
        try:
            result = self.client.table("customers").select("*").eq("id", customer_id).execute()
            
            if result.data:
                return Customer(**result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting customer: {e}")
            return None
    
    async def update_customer_status(self, customer_id: str, status: str, notes: str = None) -> bool:
        """Update customer status"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.now().isoformat()
            }
            if notes:
                update_data["notes"] = notes
            
            result = self.client.table("customers").update(update_data).eq("id", customer_id).execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error updating customer status: {e}")
            return False
    
    # Workflow operations
    async def create_workflow(self, workflow_data: Dict[str, Any]) -> Workflow:
        """Create a new workflow"""
        try:
            result = self.client.table("workflows").insert(workflow_data).execute()
            
            if result.data:
                logger.info(f"Workflow created: {result.data[0]['id']}")
                return Workflow(**result.data[0])
            else:
                raise Exception("Failed to create workflow")
                
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            raise
    
    async def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID"""
        try:
            result = self.client.table("workflows").select("*").eq("id", workflow_id).execute()
            
            if result.data:
                return Workflow(**result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting workflow: {e}")
            return None
    
    async def get_customer_workflows(self, customer_id: str) -> List[Workflow]:
        """Get all workflows for a customer"""
        try:
            result = self.client.table("workflows").select("*").eq("customer_id", customer_id).execute()
            
            return [Workflow(**workflow) for workflow in result.data]
            
        except Exception as e:
            logger.error(f"Error getting customer workflows: {e}")
            return []
    
    async def create_workflow_execution(self, execution_data: Dict[str, Any]) -> WorkflowExecution:
        """Create a workflow execution record"""
        try:
            result = self.client.table("workflow_executions").insert(execution_data).execute()
            
            if result.data:
                logger.info(f"Workflow execution created: {result.data[0]['id']}")
                return WorkflowExecution(**result.data[0])
            else:
                raise Exception("Failed to create workflow execution")
                
        except Exception as e:
            logger.error(f"Error creating workflow execution: {e}")
            raise
    
    async def get_workflow_executions(self, workflow_id: str, limit: int = 10) -> List[WorkflowExecution]:
        """Get recent workflow executions"""
        try:
            result = (self.client.table("workflow_executions")
                     .select("*")
                     .eq("workflow_id", workflow_id)
                     .order("started_at", desc=True)
                     .limit(limit)
                     .execute())
            
            return [WorkflowExecution(**execution) for execution in result.data]
            
        except Exception as e:
            logger.error(f"Error getting workflow executions: {e}")
            return []
    
    async def get_last_workflow_execution(self, workflow_id: str) -> Optional[WorkflowExecution]:
        """Get the last execution for a workflow"""
        try:
            result = (self.client.table("workflow_executions")
                     .select("*")
                     .eq("workflow_id", workflow_id)
                     .order("started_at", desc=True)
                     .limit(1)
                     .execute())
            
            if result.data:
                return WorkflowExecution(**result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting last workflow execution: {e}")
            return None
    
    async def get_workflow_metrics(self, workflow_id: str, days: int = 7) -> Dict[str, Any]:
        """Get workflow performance metrics"""
        try:
            # Get executions from the last N days
            from_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            result = (self.client.table("workflow_executions")
                     .select("*")
                     .eq("workflow_id", workflow_id)
                     .gte("started_at", from_date)
                     .execute())
            
            executions = result.data
            total_executions = len(executions)
            
            if total_executions == 0:
                return {
                    "total_executions": 0,
                    "successful_executions": 0,
                    "failed_executions": 0,
                    "success_rate": 0,
                    "average_duration": 0,
                    "total_runtime": 0,
                    "error_rate": 0
                }
            
            successful_executions = sum(1 for exec in executions if exec.get("success"))
            failed_executions = total_executions - successful_executions
            
            # Calculate average duration
            durations = [exec.get("duration_seconds", 0) for exec in executions if exec.get("duration_seconds")]
            average_duration = sum(durations) / len(durations) if durations else 0
            total_runtime = sum(durations)
            
            return {
                "total_executions": total_executions,
                "successful_executions": successful_executions,
                "failed_executions": failed_executions,
                "success_rate": successful_executions / total_executions,
                "average_duration": average_duration,
                "total_runtime": total_runtime,
                "error_rate": failed_executions / total_executions
            }
            
        except Exception as e:
            logger.error(f"Error getting workflow metrics: {e}")
            return {}
    
    # Project operations
    async def create_project(self, project_data: Dict[str, Any]) -> Project:
        """Create a new project"""
        try:
            result = self.client.table("projects").insert(project_data).execute()
            
            if result.data:
                logger.info(f"Project created: {result.data[0]['id']}")
                return Project(**result.data[0])
            else:
                raise Exception("Failed to create project")
                
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            raise
    
    async def get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        try:
            result = self.client.table("projects").select("*").eq("id", project_id).execute()
            
            if result.data:
                return Project(**result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting project: {e}")
            return None
    
    async def create_code_file(self, code_data: Dict[str, Any]) -> CodeGeneration:
        """Create a code file record"""
        try:
            result = self.client.table("code_generations").insert(code_data).execute()
            
            if result.data:
                logger.info(f"Code file created: {result.data[0]['id']}")
                return CodeGeneration(**result.data[0])
            else:
                raise Exception("Failed to create code file")
                
        except Exception as e:
            logger.error(f"Error creating code file: {e}")
            raise
    
    # Consultation operations
    async def create_consultation(self, consultation_data: Dict[str, Any]) -> Consultation:
        """Create a new consultation"""
        try:
            result = self.client.table("consultations").insert(consultation_data).execute()
            
            if result.data:
                logger.info(f"Consultation created: {result.data[0]['id']}")
                return Consultation(**result.data[0])
            else:
                raise Exception("Failed to create consultation")
                
        except Exception as e:
            logger.error(f"Error creating consultation: {e}")
            raise
    
    async def get_consultation(self, consultation_id: str) -> Optional[Consultation]:
        """Get consultation by ID"""
        try:
            result = self.client.table("consultations").select("*").eq("id", consultation_id).execute()
            
            if result.data:
                return Consultation(**result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting consultation: {e}")
            return None
    
    async def update_consultation(self, consultation_id: str, update_data: Dict[str, Any]) -> bool:
        """Update consultation"""
        try:
            update_data["updated_at"] = datetime.now().isoformat()
            
            result = self.client.table("consultations").update(update_data).eq("id", consultation_id).execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error updating consultation: {e}")
            return False
    
    async def create_consultation_session(self, session_data: Dict[str, Any]) -> ConsultationSession:
        """Create a consultation session"""
        try:
            result = self.client.table("consultation_sessions").insert(session_data).execute()
            
            if result.data:
                logger.info(f"Consultation session created: {result.data[0]['id']}")
                return ConsultationSession(**result.data[0])
            else:
                raise Exception("Failed to create consultation session")
                
        except Exception as e:
            logger.error(f"Error creating consultation session: {e}")
            raise
    
    async def get_consultation_session_by_consultation(self, consultation_id: str) -> Optional[ConsultationSession]:
        """Get consultation session by consultation ID"""
        try:
            result = (self.client.table("consultation_sessions")
                     .select("*")
                     .eq("consultation_id", consultation_id)
                     .execute())
            
            if result.data:
                return ConsultationSession(**result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting consultation session: {e}")
            return None
    
    # Analytics and reporting
    async def get_customer_analytics(self, customer_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for a customer"""
        try:
            # Get customer info
            customer = await self.get_customer(customer_id)
            if not customer:
                return {}
            
            # Get workflows count
            workflows = await self.get_customer_workflows(customer_id)
            
            # Get projects
            projects_result = self.client.table("projects").select("*").eq("customer_id", customer_id).execute()
            projects = projects_result.data
            
            # Get consultations
            consultations_result = self.client.table("consultations").select("*").eq("customer_id", customer_id).execute()
            consultations = consultations_result.data
            
            return {
                "customer": customer.dict(),
                "workflows": {
                    "total": len(workflows),
                    "active": len([w for w in workflows if w.status == "active"]),
                    "completed": len([w for w in workflows if w.status == "completed"])
                },
                "projects": {
                    "total": len(projects),
                    "in_progress": len([p for p in projects if p.get("status") == "in_progress"]),
                    "completed": len([p for p in projects if p.get("status") == "completed"])
                },
                "consultations": {
                    "total": len(consultations),
                    "scheduled": len([c for c in consultations if c.get("status") == "scheduled"]),
                    "completed": len([c for c in consultations if c.get("status") == "completed"])
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting customer analytics: {e}")
            return {}
    
    async def get_system_analytics(self) -> Dict[str, Any]:
        """Get system-wide analytics"""
        try:
            # Get counts for all entities
            customers_result = self.client.table("customers").select("id", count="exact").execute()
            workflows_result = self.client.table("workflows").select("id", count="exact").execute()
            projects_result = self.client.table("projects").select("id", count="exact").execute()
            consultations_result = self.client.table("consultations").select("id", count="exact").execute()
            
            return {
                "customers": {
                    "total": customers_result.count,
                    "new_this_month": 0  # Would need date filtering
                },
                "workflows": {
                    "total": workflows_result.count,
                    "active": 0  # Would need status filtering
                },
                "projects": {
                    "total": projects_result.count,
                    "in_progress": 0  # Would need status filtering
                },
                "consultations": {
                    "total": consultations_result.count,
                    "scheduled": 0  # Would need status filtering
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting system analytics: {e}")
            return {}
    
    # Utility methods
    async def health_check(self) -> Dict[str, Any]:
        """Check database connectivity and health"""
        try:
            # Simple query to test connection
            result = self.client.table("customers").select("id").limit(1).execute()
            
            return {
                "status": "healthy",
                "database": "connected",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }