"""FastAPI server for the ADK Agent to handle HTTP requests from the frontend."""

import asyncio
import logging
import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from my_adk_agent.agent import AccountantAgent

# Load environment variables
load_dotenv(dotenv_path="../.env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ADK Agent API",
    description="HTTP API for the ADK Agent",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://consulting.sa"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent: Optional[AccountantAgent] = None

class ChatRequest(BaseModel):
    message: str
    conversation_id: str = "default"
    agent_type: str = "root_agent"

class ChatResponse(BaseModel):
    response: str
    type: str = "general"
    service_type: Optional[str] = None
    handoff_required: bool = False

@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup."""
    global agent
    try:
        logger.info("Initializing ADK Agent...")
        agent = AccountantAgent()
        logger.info("ADK Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ADK Agent API is running",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/chat": "Send a message to the agent",
            "GET /api/health": "Health check",
            "GET /api/status": "Agent status"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agent_initialized": agent is not None,
        "timestamp": "2025-07-20T13:00:00Z"
    }

@app.get("/api/status")
async def agent_status():
    """Get agent status."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return {
        "status": "running",
        "agent_type": "AccountantAgent",
        "services": {
            "supabase": "connected",
            "n8n_mcp": "available",
            "stripe": "configured",
            "livekit": "mock_mode"
        }
    }

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """Handle chat messages from the frontend."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info(f"Processing chat message: {request.message[:50]}...")
        
        # Process the message through the agent
        response = await agent.run(request.message)
        
        # Analyze the response to determine type and handoff requirements
        response_type = "general"
        service_type = None
        handoff_required = False
        
        message_lower = request.message.lower()
        
        # Detect service types
        if any(word in message_lower for word in ['chatbot', 'chat bot']):
            service_type = "chatbot"
            response_type = "service_info"
        elif any(word in message_lower for word in ['ai agent', 'artificial intelligence']):
            service_type = "ai_agent"
            response_type = "service_info"
        elif any(word in message_lower for word in ['workflow', 'automation']):
            service_type = "workflow_automation"
            response_type = "service_info"
        elif any(word in message_lower for word in ['price', 'cost', 'pricing']):
            response_type = "pricing_info"
            handoff_required = True
        
        # Detect handoff requirements
        if any(word in message_lower for word in ['demo', 'call', 'speak', 'human', 'specialist']):
            handoff_required = True
            response_type = "handoff"
        
        return ChatResponse(
            response=response,
            type=response_type,
            service_type=service_type,
            handoff_required=handoff_required
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process message: {str(e)}"
        )

@app.post("/api/requirements")
async def gather_requirements(request: Dict[str, Any]):
    """Gather customer requirements."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        email = request.get("email")
        input_text = request.get("input", "")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        
        result = await agent.gather_requirements(email, input_text)
        return result
        
    except Exception as e:
        logger.error(f"Error gathering requirements: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to gather requirements: {str(e)}"
        )

@app.post("/api/deploy")
async def deploy_service(request: Dict[str, Any]):
    """Deploy a service for a customer."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        email = request.get("email")
        service_type = request.get("service_type")
        config = request.get("config", {})
        
        if not email or not service_type:
            raise HTTPException(status_code=400, detail="Email and service_type are required")
        
        result = await agent.deploy_ai_service(email, service_type, config)
        return result
        
    except Exception as e:
        logger.error(f"Error deploying service: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to deploy service: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("ADK_AGENT_PORT", 8080))
    host = os.getenv("ADK_WEB_HOST", "localhost")
    
    logger.info(f"Starting ADK Agent API server on {host}:{port}")
    
    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )