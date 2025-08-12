"""
Workflow data models for the n8n workflow agent
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class Workflow(BaseModel):
    """Workflow model"""
    id: str
    customer_id: str
    n8n_workflow_id: str = Field(description="N8N workflow identifier")
    template_id: str = Field(description="Template used to create workflow")
    name: str = Field(description="Workflow name")
    description: Optional[str] = None
    status: str = Field(default="created", description="Workflow status")
    config: Dict[str, Any] = Field(default_factory=dict, description="Workflow configuration")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_executed_at: Optional[datetime] = None
    execution_count: int = Field(default=0)
    success_count: int = Field(default=0)
    failure_count: int = Field(default=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class WorkflowExecution(BaseModel):
    """Workflow execution model"""
    id: str
    workflow_id: str
    n8n_execution_id: str = Field(description="N8N execution identifier")
    status: str = Field(default="running", description="Execution status")
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    success: Optional[bool] = None
    error_message: Optional[str] = None
    logs: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)