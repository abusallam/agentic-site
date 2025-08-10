"""
Base Agent Framework Interface
Abstract classes for multi-framework agent support
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Agent type enumeration"""
    WELCOMING = "welcoming"
    WORKFLOW = "workflow"
    PROFESSIONAL = "professional"
    CONSULTING = "consulting"


class ServiceType(Enum):
    """Service type enumeration"""
    FAST_SOLUTION = "fast_solution"
    CUSTOM_SOLUTION = "custom_solution"
    CONSULTATION = "consultation"


@dataclass
class AgentConfig:
    """Agent configuration data class"""
    agent_type: AgentType
    framework: str  # ADK, LangGraph, CrewAI, Swarm
    model_name: str
    temperature: float = 0.7
    max_tokens: int = 1000
    system_prompt: str = ""
    capabilities: List[str] = None


@dataclass
class AgentResponse:
    """Agent response data class"""
    message: str
    confidence: float
    next_action: Optional[str] = None
    context: Dict[str, Any] = None
    metadata: Dict[str, Any] = None


@dataclass
class CustomerIntent:
    """Customer intent analysis result"""
    service_type: ServiceType
    confidence: float
    requirements: Dict[str, Any]
    urgency: str = "normal"  # low, normal, high, urgent


class AgentFrameworkInterface(ABC):
    """Abstract interface for different agentic frameworks"""
    
    @abstractmethod
    def initialize_agent(self, config: AgentConfig) -> 'BaseAgent':
        """Initialize agent with framework-specific configuration"""
        pass
    
    @abstractmethod
    def process_message(self, message: str, context: dict) -> AgentResponse:
        """Process incoming message with context"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        pass


class BaseAgent(ABC):
    """Base agent class with common functionality"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.agent_type = config.agent_type
        self.framework = config.framework
        self.conversation_history = []
        self.context = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def process_message(self, message: str, context: Dict[str, Any] = None) -> AgentResponse:
        """Process incoming message and return response"""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        pass
    
    def update_context(self, key: str, value: Any):
        """Update agent context"""
        self.context[key] = value
        self.logger.debug(f"Updated context: {key} = {value}")
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get value from agent context"""
        return self.context.get(key, default)
    
    def add_to_history(self, role: str, message: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "message": message,
            "timestamp": self._get_timestamp()
        })
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.logger.info("Conversation history cleared")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return getattr(self.config, 'capabilities', [])