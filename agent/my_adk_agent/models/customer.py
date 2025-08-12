"""
Customer data models for the initial customer agent
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr

class Customer(BaseModel):
    """Customer model"""
    id: str
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    language: str = Field(default="ar", description="Preferred language (ar/en)")
    source: str = Field(default="chat", description="How customer found us")
    status: str = Field(default="new", description="Customer status")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    notes: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CustomerInquiry(BaseModel):
    """Customer inquiry model"""
    id: str
    customer_id: str
    inquiry_type: str = Field(description="Type of inquiry")
    message: str = Field(description="Customer message")
    language: str = Field(default="ar")
    agent_type: str = Field(description="Which agent handled the inquiry")
    status: str = Field(default="open")
    priority: str = Field(default="medium")
    created_at: datetime = Field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    resolution: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)