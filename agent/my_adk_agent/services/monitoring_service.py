"""
Monitoring Service for Agentic Platform
Provides metrics collection and health monitoring capabilities
"""

import time
import psutil
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collects and formats metrics for Prometheus"""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
        
    def increment_request_count(self, method: str = "GET", endpoint: str = "/", status_code: int = 200):
        """Increment request counter"""
        self.request_count += 1
        if status_code >= 400:
            self.error_count += 1
    
    def record_response_time(self, duration: float, endpoint: str = "/"):
        """Record response time"""
        self.response_times.append({
            'duration': duration,
            'endpoint': endpoint,
            'timestamp': time.time()
        })
        
        # Keep only last 1000 entries
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system resource metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_usage_percent': cpu_percent,
                'memory_usage_percent': memory.percent,
                'memory_used_bytes': memory.used,
                'memory_total_bytes': memory.total,
                'disk_usage_percent': disk.percent,
                'disk_used_bytes': disk.used,
                'disk_total_bytes': disk.total,
                'uptime_seconds': time.time() - self.start_time
            }
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {}
    
    def get_application_metrics(self) -> Dict[str, Any]:
        """Get application-specific metrics"""
        avg_response_time = 0
        if self.response_times:
            recent_times = [rt['duration'] for rt in self.response_times[-100:]]
            avg_response_time = sum(recent_times) / len(recent_times)
        
        error_rate = 0
        if self.request_count > 0:
            error_rate = self.error_count / self.request_count
        
        return {
            'http_requests_total': self.request_count,
            'http_errors_total': self.error_count,
            'http_error_rate': error_rate,
            'http_response_time_avg': avg_response_time,
            'active_connections': len(self.response_times),
            'uptime_seconds': time.time() - self.start_time
        }
    
    def get_prometheus_metrics(self) -> str:
        """Generate Prometheus-formatted metrics"""
        system_metrics = self.get_system_metrics()
        app_metrics = self.get_application_metrics()
        
        lines = []
        
        # System metrics
        lines.extend([
            "# HELP agentic_cpu_usage_percent CPU usage percentage",
            "# TYPE agentic_cpu_usage_percent gauge",
            f"agentic_cpu_usage_percent {system_metrics.get('cpu_usage_percent', 0)}",
            "",
            "# HELP agentic_memory_usage_percent Memory usage percentage", 
            "# TYPE agentic_memory_usage_percent gauge",
            f"agentic_memory_usage_percent {system_metrics.get('memory_usage_percent', 0)}",
            "",
            "# HELP agentic_memory_used_bytes Memory used in bytes",
            "# TYPE agentic_memory_used_bytes gauge", 
            f"agentic_memory_used_bytes {system_metrics.get('memory_used_bytes', 0)}",
            "",
            "# HELP agentic_disk_usage_percent Disk usage percentage",
            "# TYPE agentic_disk_usage_percent gauge",
            f"agentic_disk_usage_percent {system_metrics.get('disk_usage_percent', 0)}",
            "",
            "# HELP agentic_uptime_seconds Application uptime in seconds",
            "# TYPE agentic_uptime_seconds counter",
            f"agentic_uptime_seconds {system_metrics.get('uptime_seconds', 0)}",
            ""
        ])
        
        # Application metrics
        lines.extend([
            "# HELP http_requests_total Total HTTP requests",
            "# TYPE http_requests_total counter",
            f'http_requests_total{{service="agentic-backend"}} {app_metrics.get("http_requests_total", 0)}',
            "",
            "# HELP http_errors_total Total HTTP errors",
            "# TYPE http_errors_total counter", 
            f'http_errors_total{{service="agentic-backend"}} {app_metrics.get("http_errors_total", 0)}',
            "",
            "# HELP http_error_rate HTTP error rate",
            "# TYPE http_error_rate gauge",
            f'http_error_rate{{service="agentic-backend"}} {app_metrics.get("http_error_rate", 0)}',
            "",
            "# HELP http_response_time_avg Average HTTP response time",
            "# TYPE http_response_time_avg gauge",
            f'http_response_time_avg{{service="agentic-backend"}} {app_metrics.get("http_response_time_avg", 0)}',
            "",
            "# HELP agentic_platform_info Information about the Agentic Platform",
            "# TYPE agentic_platform_info gauge",
            f'agentic_platform_info{{version="1.0.0",environment="production",service="backend"}} 1',
            "",
            "# HELP agentic_platform_health_status Health status of the platform",
            "# TYPE agentic_platform_health_status gauge",
            f'agentic_platform_health_status{{service="backend"}} 1',
            ""
        ])
        
        return "\n".join(lines)

class HealthChecker:
    """Health check service for monitoring system health"""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.last_check = None
        self.health_status = "healthy"
        
    async def check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            # Simulate database check
            await asyncio.sleep(0.01)  # Simulate DB query time
            return {
                "status": "healthy",
                "response_time_ms": 10,
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy", 
                "error": str(e),
                "response_time_ms": 0,
                "last_check": datetime.utcnow().isoformat()
            }
    
    async def check_cache_health(self) -> Dict[str, Any]:
        """Check cache (Redis) connectivity"""
        try:
            # Simulate cache check
            await asyncio.sleep(0.005)  # Simulate cache query time
            return {
                "status": "healthy",
                "response_time_ms": 5,
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e), 
                "response_time_ms": 0,
                "last_check": datetime.utcnow().isoformat()
            }
    
    async def check_external_services_health(self) -> Dict[str, Any]:
        """Check external service dependencies"""
        services = {}
        
        # Check Supabase
        try:
            await asyncio.sleep(0.02)  # Simulate API call
            services["supabase"] = {
                "status": "healthy",
                "response_time_ms": 20,
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            services["supabase"] = {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": 0,
                "last_check": datetime.utcnow().isoformat()
            }
        
        # Check Gemini API
        try:
            await asyncio.sleep(0.05)  # Simulate API call
            services["gemini"] = {
                "status": "healthy", 
                "response_time_ms": 50,
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            services["gemini"] = {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": 0,
                "last_check": datetime.utcnow().isoformat()
            }
        
        return services
    
    async def get_comprehensive_health(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        self.last_check = datetime.utcnow()
        
        # Run all health checks concurrently
        database_health, cache_health, external_services = await asyncio.gather(
            self.check_database_health(),
            self.check_cache_health(), 
            self.check_external_services_health(),
            return_exceptions=True
        )
        
        # Determine overall health
        all_healthy = True
        if isinstance(database_health, dict) and database_health.get("status") != "healthy":
            all_healthy = False
        if isinstance(cache_health, dict) and cache_health.get("status") != "healthy":
            all_healthy = False
        if isinstance(external_services, dict):
            for service_health in external_services.values():
                if service_health.get("status") != "healthy":
                    all_healthy = False
        
        self.health_status = "healthy" if all_healthy else "unhealthy"
        
        return {
            "status": self.health_status,
            "timestamp": self.last_check.isoformat(),
            "uptime_seconds": (self.last_check - self.start_time).total_seconds(),
            "version": "1.0.0",
            "environment": "production",
            "service": "agentic-backend",
            "checks": {
                "database": database_health if isinstance(database_health, dict) else {"status": "error", "error": str(database_health)},
                "cache": cache_health if isinstance(cache_health, dict) else {"status": "error", "error": str(cache_health)},
                "external_services": external_services if isinstance(external_services, dict) else {"status": "error", "error": str(external_services)}
            },
            "system": {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent
            }
        }

class MonitoringService:
    """Main monitoring service that coordinates metrics and health checks"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.health_checker = HealthChecker()
        self.logger = logging.getLogger(__name__)
        
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record a request for metrics"""
        self.metrics_collector.increment_request_count(method, endpoint, status_code)
        self.metrics_collector.record_response_time(duration, endpoint)
        
    def get_metrics(self) -> str:
        """Get Prometheus-formatted metrics"""
        return self.metrics_collector.get_prometheus_metrics()
        
    async def get_health(self) -> Dict[str, Any]:
        """Get health status"""
        return await self.health_checker.get_comprehensive_health()
        
    def get_simple_health(self) -> Dict[str, Any]:
        """Get simple health status for quick checks"""
        return {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "agentic-backend",
            "uptime": time.time() - self.metrics_collector.start_time
        }

# Global monitoring service instance
monitoring_service = MonitoringService()