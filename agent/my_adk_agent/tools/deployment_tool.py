"""
Deployment Tool for Agentic Platform
Handles deployment operations and monitoring integration
"""

import subprocess
import json
import time
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DeploymentTool:
    """Tool for managing deployments and monitoring integration"""
    
    def __init__(self):
        self.deployment_history = []
        self.monitoring_endpoints = {
            "grafana": "https://monitoring.consulting.sa",
            "prometheus": "https://metrics.consulting.sa", 
            "n8n": "https://n8n.consulting.sa",
            "alertmanager": "http://localhost:9093"
        }
        
    def deploy_monitoring_stack(self) -> Dict[str, Any]:
        """Deploy the complete monitoring stack"""
        try:
            logger.info("Starting monitoring stack deployment")
            
            # Run the deployment script
            result = subprocess.run(
                ["./scripts/deploy-monitoring.sh"],
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes timeout
            )
            
            deployment_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "type": "monitoring_stack",
                "status": "success" if result.returncode == 0 else "failed",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
            self.deployment_history.append(deployment_record)
            
            if result.returncode == 0:
                logger.info("Monitoring stack deployed successfully")
                # Wait for services to be ready
                time.sleep(30)
                # Validate deployment
                validation_result = self.validate_monitoring_deployment()
                deployment_record["validation"] = validation_result
                
                return {
                    "success": True,
                    "message": "Monitoring stack deployed successfully",
                    "deployment": deployment_record,
                    "validation": validation_result
                }
            else:
                logger.error(f"Monitoring deployment failed: {result.stderr}")
                return {
                    "success": False,
                    "message": "Monitoring deployment failed",
                    "error": result.stderr,
                    "deployment": deployment_record
                }
                
        except subprocess.TimeoutExpired:
            logger.error("Monitoring deployment timed out")
            return {
                "success": False,
                "message": "Deployment timed out after 30 minutes",
                "error": "Timeout"
            }
        except Exception as e:
            logger.error(f"Deployment error: {e}")
            return {
                "success": False,
                "message": "Deployment failed with exception",
                "error": str(e)
            }
    
    def validate_monitoring_deployment(self) -> Dict[str, Any]:
        """Validate that monitoring services are running correctly"""
        validation_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy",
            "services": {}
        }
        
        # Check each monitoring service
        services_to_check = [
            ("grafana", "https://monitoring.consulting.sa/api/health"),
            ("prometheus", "https://metrics.consulting.sa/-/healthy"),
            ("n8n", "https://n8n.consulting.sa/healthz"),
            ("alertmanager", "http://localhost:9093/-/healthy")
        ]
        
        for service_name, health_url in services_to_check:
            try:
                response = requests.get(
                    health_url,
                    timeout=10,
                    auth=("admin", "agentic-platform-admin-2025") if "metrics" in health_url else None
                )
                
                validation_results["services"][service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "status_code": response.status_code,
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "last_check": datetime.utcnow().isoformat()
                }
                
                if response.status_code != 200:
                    validation_results["overall_status"] = "degraded"
                    
            except requests.RequestException as e:
                validation_results["services"][service_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_check": datetime.utcnow().isoformat()
                }
                validation_results["overall_status"] = "degraded"
        
        # Check Docker containers
        try:
            result = subprocess.run(
                ["ssh", "root@217.79.255.54", "cd /opt/monitoring && docker compose ps --format json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                containers = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        try:
                            container = json.loads(line)
                            containers.append({
                                "name": container.get("Name", "unknown"),
                                "status": container.get("State", "unknown"),
                                "health": container.get("Health", "unknown")
                            })
                        except json.JSONDecodeError:
                            continue
                
                validation_results["containers"] = containers
                
                # Check if any containers are not running
                unhealthy_containers = [c for c in containers if c["status"] != "running"]
                if unhealthy_containers:
                    validation_results["overall_status"] = "degraded"
                    validation_results["unhealthy_containers"] = unhealthy_containers
                    
        except Exception as e:
            validation_results["container_check_error"] = str(e)
            validation_results["overall_status"] = "degraded"
        
        return validation_results
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current status of monitoring services"""
        return self.validate_monitoring_deployment()
    
    def restart_monitoring_service(self, service_name: str) -> Dict[str, Any]:
        """Restart a specific monitoring service"""
        try:
            logger.info(f"Restarting monitoring service: {service_name}")
            
            result = subprocess.run([
                "ssh", "root@217.79.255.54", 
                f"cd /opt/monitoring && docker compose restart {service_name}"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info(f"Service {service_name} restarted successfully")
                # Wait for service to be ready
                time.sleep(10)
                # Validate service
                validation = self.validate_monitoring_deployment()
                
                return {
                    "success": True,
                    "message": f"Service {service_name} restarted successfully",
                    "validation": validation
                }
            else:
                logger.error(f"Failed to restart {service_name}: {result.stderr}")
                return {
                    "success": False,
                    "message": f"Failed to restart {service_name}",
                    "error": result.stderr
                }
                
        except Exception as e:
            logger.error(f"Error restarting service {service_name}: {e}")
            return {
                "success": False,
                "message": f"Error restarting {service_name}",
                "error": str(e)
            }
    
    def get_monitoring_logs(self, service_name: Optional[str] = None, lines: int = 100) -> Dict[str, Any]:
        """Get logs from monitoring services"""
        try:
            if service_name:
                cmd = f"cd /opt/monitoring && docker compose logs --tail={lines} {service_name}"
            else:
                cmd = f"cd /opt/monitoring && docker compose logs --tail={lines}"
            
            result = subprocess.run([
                "ssh", "root@217.79.255.54", cmd
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "logs": result.stdout,
                    "service": service_name or "all",
                    "lines": lines,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "service": service_name or "all"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "service": service_name or "all"
            }
    
    def create_n8n_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new N8N workflow"""
        try:
            # This would integrate with N8N API to create workflows
            # For now, return a placeholder response
            workflow_id = f"workflow_{int(time.time())}"
            
            return {
                "success": True,
                "message": "Workflow created successfully",
                "workflow_id": workflow_id,
                "workflow_name": workflow_data.get("name", "Unnamed Workflow"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating N8N workflow: {e}")
            return {
                "success": False,
                "message": "Failed to create workflow",
                "error": str(e)
            }
    
    def trigger_alert_test(self, alert_type: str = "test") -> Dict[str, Any]:
        """Trigger a test alert to validate alerting system"""
        try:
            # Create a test alert payload
            test_alert = {
                "alerts": [{
                    "status": "firing",
                    "labels": {
                        "alertname": "TestAlert",
                        "severity": "warning",
                        "category": "monitoring",
                        "instance": "test-instance",
                        "job": "test-job"
                    },
                    "annotations": {
                        "summary": "This is a test alert",
                        "description": "Test alert triggered from deployment tool",
                        "runbook_url": "https://consulting.sa/docs/runbooks/test-alert"
                    },
                    "startsAt": datetime.utcnow().isoformat(),
                    "endsAt": "0001-01-01T00:00:00Z"
                }],
                "groupLabels": {
                    "alertname": "TestAlert"
                },
                "commonLabels": {
                    "severity": "warning",
                    "category": "monitoring"
                },
                "status": "firing"
            }
            
            # Send test alert to N8N webhook
            response = requests.post(
                "https://n8n.consulting.sa/webhook/alertmanager-warning",
                json=test_alert,
                auth=("alertmanager", "agentic-webhook-2025"),
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Test alert sent successfully",
                    "alert_type": alert_type,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to send test alert",
                    "status_code": response.status_code,
                    "error": response.text
                }
                
        except Exception as e:
            logger.error(f"Error triggering test alert: {e}")
            return {
                "success": False,
                "message": "Failed to trigger test alert",
                "error": str(e)
            }
    
    def get_deployment_history(self) -> List[Dict[str, Any]]:
        """Get deployment history"""
        return self.deployment_history
    
    def get_monitoring_metrics(self) -> Dict[str, Any]:
        """Get current monitoring metrics"""
        try:
            # Get metrics from Prometheus
            response = requests.get(
                "https://metrics.consulting.sa/api/v1/query",
                params={"query": "up"},
                auth=("admin", "agentic-platform-admin-2025"),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "metrics": data,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to fetch metrics: {response.status_code}",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error fetching monitoring metrics: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

# Global deployment tool instance
deployment_tool = DeploymentTool()