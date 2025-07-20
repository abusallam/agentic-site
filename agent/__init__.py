"""ADK Agent package for customer journey orchestration."""

from my_adk_agent.agent import CustomerJourneyAgent

# This is required for ADK agent discovery
agent = CustomerJourneyAgent()

__version__ = "0.1.0"
__all__ = ["CustomerJourneyAgent", "agent"]