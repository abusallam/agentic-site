"""FastAPI server for agent health checks and API endpoints."""

import os
import logging
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agentic AI Backend",
    description="Backend API for the Agentic AI SaaS platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: str
    environment: str
    services: Dict[str, str]
    uptime: float


class ServiceStatus(BaseModel):
    """Service status model."""
    name: str
    status: str
    last_check: str
    details: Dict[str, Any] = {}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Check service configurations
        services = {
            "supabase": "configured" if os.getenv("SUPABASE_URL") else "missing",
            "gemini": "configured" if os.getenv("GEMINI_API_KEY") else "missing",
            "n8n": "configured" if os.getenv("N8N_URL") else "missing",
            "mcp": "configured" if os.getenv("MCP_SERVER_URL") else "missing",
            "livekit": "configured" if os.getenv("LIVEKIT_URL") else "missing",
            "stripe": "configured" if os.getenv("STRIPE_SECRET_KEY") else "missing",
        }
        
        # Determine overall status
        status = "healthy" if all(s == "configured" for s in services.values()) else "degraded"
        
        return HealthResponse(
            status=status,
            timestamp=datetime.utcnow().isoformat(),
            environment=os.getenv("ENVIRONMENT", "development"),
            services=services,
            uptime=0.0  # Would be calculated from startup time in real implementation
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with service connectivity tests."""
    try:
        service_checks = []
        
        # Test Supabase connection
        try:
            from my_adk_agent.services.supabase_service import SupabaseService
            supabase_service = SupabaseService()
            supabase_healthy = await supabase_service.health_check()
            service_checks.append(ServiceStatus(
                name="supabase",
                status="healthy" if supabase_healthy else "unhealthy",
                last_check=datetime.utcnow().isoformat()
            ))
        except Exception as e:
            service_checks.append(ServiceStatus(
                name="supabase",
                status="error",
                last_check=datetime.utcnow().isoformat(),
                details={"error": str(e)}
            ))
        
        # Test MCP connection
        try:
            from my_adk_agent.services.mcp_service import MCPService
            mcp_service = MCPService()
            mcp_tools = await mcp_service.list_available_tools()
            service_checks.append(ServiceStatus(
                name="mcp",
                status="healthy" if mcp_tools is not None else "unhealthy",
                last_check=datetime.utcnow().isoformat(),
                details={"tools_count": len(mcp_tools) if mcp_tools else 0}
            ))
        except Exception as e:
            service_checks.append(ServiceStatus(
                name="mcp",
                status="error",
                last_check=datetime.utcnow().isoformat(),
                details={"error": str(e)}
            ))
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": service_checks
        }
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(status_code=500, detail="Detailed health check failed")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Agentic AI Backend API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    try:
        from my_adk_agent.services.monitoring_service import MonitoringService
        monitoring_service = MonitoringService()
        
        # Generate Prometheus format metrics
        prometheus_metrics = await monitoring_service.generate_prometheus_metrics()
        
        return Response(
            content=prometheus_metrics,
            media_type="text/plain; charset=utf-8"
        )
    except Exception as e:
        logger.error(f"Error generating metrics: {e}")
        # Fallback to basic metrics
        basic_metrics = f"""# HELP app_info Application information
# TYPE app_info gauge
app_info{{version="1.0.0",environment="{os.getenv('ENVIRONMENT', 'development')}",job="agentic-backend"}} 1

# HELP app_up Application up status
# TYPE app_up gauge
app_up{{job="agentic-backend"}} 1
"""
        return Response(
            content=basic_metrics,
            media_type="text/plain; charset=utf-8"
        )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=os.getenv("ENVIRONMENT") == "development",
        log_level="info"
    )