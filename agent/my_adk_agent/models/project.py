"""
Project data models for the code generation agent
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class Project(BaseModel):
    """Project model for code generation"""
    id: str
    customer_id: str
    name: str = Field(description="Project name")
    description: Optional[str] = None
    framework: str = Field(description="Framework used (google_adk, langgraph, pydantic)")
    complexity: str = Field(description="Project complexity (low, medium, high)")
    requirements: Dict[str, Any] = Field(default_factory=dict, description="Project requirements")
    architecture: Dict[str, Any] = Field(default_factory=dict, description="System architecture")
    status: str = Field(default="created", description="Project status")
    estimated_timeline: Optional[str] = None
    actual_timeline: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CodeGeneration(BaseModel):
    """Code generation model"""
    id: str
    project_id: str
    file_path: str = Field(description="File path in project")
    content: str = Field(description="Generated code content")
    file_type: str = Field(description="Type of file (source, test, documentation)")
    language: str = Field(default="python", description="Programming language")
    framework_specific: bool = Field(default=False, description="Framework-specific code")
    generated_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: int = Field(default=1, description="Code version")
    metadata: Dict[str, Any] = Field(default_factory=dict)