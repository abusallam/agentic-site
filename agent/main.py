"""
Main FastAPI application for the agent backend
Provides REST API endpoints for agent routing and processing
"""

import os
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from my_adk_agent.agent_router import AgentRouter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Agentic Backend API",
    description="Multi-agent system with intelligent routing",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent router
config = {
    "supabase_url": os.getenv("SUPABASE_URL"),
    "supabase_key": os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
    "google_api_key": os.getenv("GOOGLE_API_KEY"),
    "openai_api_key": os.getenv("OPENAI_API_KEY"),
    "livekit_api_key": os.getenv("LIVEKIT_API_KEY"),
    "livekit_api_secret": os.getenv("LIVEKIT_API_SECRET"),
    "stripe_secret_key": os.getenv("STRIPE_SECRET_KEY"),
    "n8n_url": os.getenv("N8N_URL", "http://localhost:5678"),
    "n8n_api_key": os.getenv("N8N_API_KEY"),
}

router = AgentRouter(config)

# Request/Response models
class AgentRequest(BaseModel):
    message: str
    session_id: str
    agentType: Optional[str] = None
    language: Optional[str] = "ar"
    voiceData: Optional[Dict[str, Any]] = None
    fileData: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    content: str
    agent_type: str
    language: str
    confidence: float
    actions: list = []
    routing: Dict[str, Any] = {}
    capabilities: list = []

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "agentic-backend",
        "version": "1.0.0",
        "agents_available": len(router.agents),
        "routing_active": True
    }

@app.post("/agent/route", response_model=AgentResponse)
async def route_message(request: AgentRequest):
    """Route message to appropriate agent"""
    try:
        # Route message through agent router
        response = await router.route_message(
            message=request.message,
            session_id=request.session_id,
            context=request.context
        )
        
        return AgentResponse(
            content=response.get("content", ""),
            agent_type=response.get("agent_type", "unknown"),
            language=response.get("language", "ar"),
            confidence=response.get("routing", {}).get("confidence", 0.5),
            actions=response.get("actions", []),
            routing=response.get("routing", {}),
            capabilities=response.get("capabilities", [])
        )
        
    except Exception as e:
        logger.error(f"Error routing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/handoff")
async def handoff_agent(session_id: str, target_agent: str, reason: str = None):
    """Manually handoff to specific agent"""
    try:
        result = await router.handoff_to_agent(session_id, target_agent, reason)
        return result
    except Exception as e:
        logger.error(f"Error in agent handoff: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/status")
async def get_agent_status():
    """Get status of all agents"""
    try:
        status = await router.get_agent_status()
        return status
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/billing/track")
async def track_resource_usage(
    customer_id: str,
    resource_type: str,
    quantity: float,
    metadata: Dict[str, Any] = None
):
    """Track resource usage for billing"""
    try:
        billing_agent = router.agents.get("billing")
        if not billing_agent:
            raise HTTPException(status_code=404, detail="Billing agent not available")
        
        result = await billing_agent.track_resource_usage(
            customer_id=customer_id,
            resource_type=resource_type,
            quantity=quantity,
            metadata=metadata
        )
        
        return result
    except Exception as e:
        logger.error(f"Error tracking resource usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/billing/usage/{customer_id}")
async def get_usage_summary(customer_id: str, period_days: int = 30, language: str = "ar"):
    """Get usage summary for customer"""
    try:
        billing_agent = router.agents.get("billing")
        if not billing_agent:
            raise HTTPException(status_code=404, detail="Billing agent not available")
        
        result = await billing_agent.get_usage_summary(
            customer_id=customer_id,
            period_days=period_days,
            language=language
        )
        
        return result
    except Exception as e:
        logger.error(f"Error getting usage summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/workflow/create")
async def create_workflow(
    customer_id: str,
    template_id: str,
    custom_config: Dict[str, Any] = None,
    language: str = "ar"
):
    """Create n8n workflow"""
    try:
        workflow_agent = router.agents.get("n8n_workflow")
        if not workflow_agent:
            raise HTTPException(status_code=404, detail="Workflow agent not available")
        
        result = await workflow_agent.create_workflow(
            customer_id=customer_id,
            template_id=template_id,
            custom_config=custom_config,
            language=language
        )
        
        return result
    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/workflow/templates")
async def list_workflow_templates(language: str = "ar"):
    """List available workflow templates"""
    try:
        workflow_agent = router.agents.get("n8n_workflow")
        if not workflow_agent:
            raise HTTPException(status_code=404, detail="Workflow agent not available")
        
        result = await workflow_agent.list_workflow_templates(language=language)
        return result
    except Exception as e:
        logger.error(f"Error listing workflow templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False
    )