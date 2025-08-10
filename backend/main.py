"""
Agentic Platform FastAPI Application
Enhanced backend with FastAPI, Celery, Redis, and Flower integration
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

import redis
import structlog
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from agentic_core.config import settings
from agentic_core.agents import InitialAuthAgent, WelcomingAgent, N8NWorkflowAgent, ProfessionalAgent, ConsultingAgent
from agentic_core.agents.base_agent import AgentConfig, AgentType
from agentic_core.services.customer_dashboard_service import CustomerDashboardService
from agentic_core.services.task_calendar_service import TaskCalendarService
from agentic_core.tasks.agent_tasks import process_customer_message, health_check_agent


# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Get configuration
config = settings

# Prometheus metrics
REQUEST_COUNT = Counter('agentic_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('agentic_request_duration_seconds', 'Request duration')
AGENT_INTERACTIONS = Counter('agentic_agent_interactions_total', 'Agent interactions', ['agent_type'])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Agentic Platform API")
    
    # Initialize Redis connection
    try:
        redis_client = redis.from_url(config.redis_url)
        redis_client.ping()
        app.state.redis = redis_client
        logger.info("Redis connection established")
    except Exception as e:
        logger.error("Failed to connect to Redis", error=str(e))
        raise
    
    # Initialize agents
    app.state.agents = {
        'welcoming': WelcomingAgent(),
        'workflow': WorkflowAgent(),
        'professional': ProfessionalAgent(),
        'consulting': ConsultingAgent()
    }
    
    # Start agents
    for agent_name, agent in app.state.agents.items():
        await agent.start()
        logger.info("Agent started", agent_name=agent_name)
    
    yield
    
    # Cleanup
    logger.info("Shutting down Agentic Platform API")
    
    # Stop agents
    for agent_name, agent in app.state.agents.items():
        await agent.stop()
        logger.info("Agent stopped", agent_name=agent_name)


# Create FastAPI app
app = FastAPI(
    title="Agentic Platform API",
    description="Advanced AI Agent Platform with FastAPI, Celery, and Redis",
    version=config.app_version,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def metrics_middleware(request, call_next):
    """Middleware to collect metrics"""
    with REQUEST_DURATION.time():
        REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
        response = await call_next(request)
    return response


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Agentic Platform API",
        "version": config.app_version,
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Redis connection
        app.state.redis.ping()
        
        # Check agents
        agent_status = {}
        for agent_name, agent in app.state.agents.items():
            health_data = await agent.health_check()
            agent_status[agent_name] = health_data
        
        return {
            "status": "healthy",
            "timestamp": "now",
            "services": {
                "redis": "connected",
                "agents": agent_status
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/v1/chat")
async def chat_endpoint(
    agent_type: str,
    message: str,
    session_id: str,
    user_id: str = None,
    context: Dict[str, Any] = None
):
    """
    Main chat endpoint for agent interactions
    
    Args:
        agent_type: Type of agent to use
        message: User message
        session_id: Session identifier
        user_id: Optional user identifier
        context: Optional additional context
    """
    try:
        AGENT_INTERACTIONS.labels(agent_type=agent_type).inc()
        
        # Validate agent type
        if agent_type not in app.state.agents:
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")
        
        # Create message and context objects
        agent_message = AgentMessage(
            sender_id=user_id or "anonymous",
            content=message
        )
        
        agent_context = AgentContext(
            session_id=session_id,
            user_id=user_id,
            workflow_state=context or {}
        )
        
        # Process message through agent
        agent = app.state.agents[agent_type]
        response = await agent.process_message(agent_message, agent_context)
        
        return {
            "success": response.success,
            "message": response.message,
            "data": response.data,
            "next_action": response.next_action,
            "transfer_to": response.transfer_to,
            "metadata": response.metadata,
            "agent_type": agent_type,
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error("Chat endpoint error", error=str(e), agent_type=agent_type)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/v1/chat/async")
async def chat_async_endpoint(
    agent_type: str,
    message: str,
    session_id: str,
    user_id: str = None,
    context: Dict[str, Any] = None
):
    """
    Asynchronous chat endpoint using Celery
    
    Args:
        agent_type: Type of agent to use
        message: User message
        session_id: Session identifier
        user_id: Optional user identifier
        context: Optional additional context
    """
    try:
        # Validate agent type
        if agent_type not in ['welcoming', 'workflow', 'professional', 'consulting']:
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")
        
        # Prepare message and context data
        message_data = {
            'sender_id': user_id or "anonymous",
            'content': message
        }
        
        context_data = {
            'session_id': session_id,
            'user_id': user_id,
            'workflow_state': context or {}
        }
        
        # Submit task to Celery
        task = process_agent_message.delay(agent_type, message_data, context_data)
        
        return {
            "task_id": task.id,
            "status": "submitted",
            "agent_type": agent_type,
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error("Async chat endpoint error", error=str(e), agent_type=agent_type)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v1/task/{task_id}")
async def get_task_result(task_id: str):
    """
    Get Celery task result
    
    Args:
        task_id: Celery task ID
    """
    try:
        from agentic_core.tasks.celery_app import celery_app
        
        result = celery_app.AsyncResult(task_id)
        
        if result.ready():
            return {
                "task_id": task_id,
                "status": "completed",
                "result": result.result
            }
        else:
            return {
                "task_id": task_id,
                "status": "pending",
                "result": None
            }
            
    except Exception as e:
        logger.error("Task result error", error=str(e), task_id=task_id)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v1/agents")
async def list_agents():
    """List all available agents"""
    agents_info = {}
    
    for agent_name, agent in app.state.agents.items():
        health_data = await agent.health_check()
        agents_info[agent_name] = {
            "name": agent.name,
            "role": agent.role.value,
            "capabilities": [cap.value for cap in agent.capabilities],
            "description": agent.description,
            "health": health_data
        }
    
    return {
        "agents": agents_info,
        "total_agents": len(agents_info)
    }


@app.get("/api/v1/agents/{agent_type}/health")
async def agent_health_check(agent_type: str):
    """Get health status of specific agent"""
    if agent_type not in app.state.agents:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_type}")
    
    agent = app.state.agents[agent_type]
    health_data = await agent.health_check()
    
    return health_data


@app.post("/api/v1/workflows/execute")
async def execute_workflow(
    workflow_id: str,
    input_data: Dict[str, Any],
    webhook_url: str = None
):
    """
    Execute N8N workflow
    
    Args:
        workflow_id: N8N workflow ID
        input_data: Input data for workflow
        webhook_url: Optional webhook URL
    """
    try:
        from agentic_core.tasks.workflow_tasks import execute_n8n_workflow
        
        task = execute_n8n_workflow.delay(workflow_id, input_data, webhook_url)
        
        return {
            "task_id": task.id,
            "workflow_id": workflow_id,
            "status": "submitted"
        }
        
    except Exception as e:
        logger.error("Workflow execution error", error=str(e), workflow_id=workflow_id)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v1/system/stats")
async def system_stats():
    """Get system statistics"""
    try:
        # Redis stats
        redis_info = app.state.redis.info()
        
        # Agent stats
        agent_stats = {}
        for agent_name, agent in app.state.agents.items():
            health_data = await agent.health_check()
            agent_stats[agent_name] = health_data
        
        return {
            "redis": {
                "connected_clients": redis_info.get("connected_clients", 0),
                "used_memory_human": redis_info.get("used_memory_human", "0B"),
                "uptime_in_seconds": redis_info.get("uptime_in_seconds", 0)
            },
            "agents": agent_stats,
            "system": {
                "version": config.app_version,
                "debug": config.debug
            }
        }
        
    except Exception as e:
        logger.error("System stats error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=config.api_host,
        port=config.api_port,
        reload=config.debug,
        log_level=config.log_level.lower()
    )