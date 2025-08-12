"""
Consultation data models for the consulting agent
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class Consultation(BaseModel):
    """Consultation model"""
    id: str
    customer_id: str
    consultation_type: str = Field(description="Type of consultation")
    business_domain: str = Field(description="Customer's business domain")
    challenges: List[str] = Field(default_factory=list, description="Current challenges")
    desired_outcomes: List[str] = Field(default_factory=list, description="Desired outcomes")
    budget_range: Optional[str] = None
    timeline: Optional[str] = None
    technical_requirements: List[str] = Field(default_factory=list)
    language: str = Field(default="ar", description="Consultation language")
    status: str = Field(default="requested", description="Consultation status")
    scheduled_time: Optional[datetime] = None
    ai_recommendations: List[str] = Field(default_factory=list)
    proposed_solutions: List[Dict[str, Any]] = Field(default_factory=list)
    estimated_cost: Optional[str] = None
    estimated_timeline: Optional[str] = None
    requires_human_consultant: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ConsultationSession(BaseModel):
    """Consultation session model for LiveKit integration"""
    id: str
    consultation_id: str
    customer_id: str
    room_name: str = Field(description="LiveKit room name")
    room_url: str = Field(description="LiveKit room URL")
    status: str = Field(default="scheduled", description="Session status")
    language: str = Field(default="ar")
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    participants: List[str] = Field(default_factory=list)
    recording_url: Optional[str] = None
    transcript: Optional[str] = None
    notes: Optional[str] = None
    follow_up_required: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)