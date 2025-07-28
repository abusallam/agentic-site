"""
n8n MCP Agent - Dedicated agent for managing n8n MCP server integration.

This agent handles:
- n8n MCP server lifecycle management
- Workflow creation and management via MCP
- Real-time monitoring and updates
- Integration with the main customer journey agent
"""

from .agent import N8nMCPAgent

__version__ = "0.1.0"
__all__ = ["N8nMCPAgent"]