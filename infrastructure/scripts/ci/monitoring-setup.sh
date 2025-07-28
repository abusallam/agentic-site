#!/bin/bash
set -e

# Monitoring Setup Script
# Sets up monitoring stack with Prometheus, Grafana, and alerting

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

ENVIRONMENT=${1:-staging}
MONITORING_DIR="monitoring"

echo -e "${BLUE}🔍 Setting up monitoring stack for environment: $ENVIRONMENT${NC}"

# Create monitoring directory structure
mkdir -p "$MONITORING_DIR"/{grafana,prometheus,alertmanager}
mkdir -p "$MONITORING_DIR"/grafana/{dashboards,provisioning/{dashboards,datasources}}

echo -e "${YELLOW}Creating Grafana configuration...${NC}"

# Grafana datasource configuration
cat > "$MONITORING_DIR/grafana/provisioning/datasources/prometheus.yml" << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF

# Grafana dashboard provisioning
cat > "$MONITORING_DIR/grafana/provisioning/dashboards/dashboards.yml" << 'EOF'
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
EOF

# Create Agentic AI dashboard
cat > "$MONITORING_DIR/grafana/dashboards/agentic-dashboard.json" << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "Agentic AI Platform",
    "tags": ["agentic", "ai", "platform"],
    "style": "dark",
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Service Health Status",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=~\"agentic-.*\"}",
            "legendFormat": "{{job}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "green", "value": 1}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "HTTP Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{job}} - {{method}} {{status}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      },
      {
        "id": 3,
        "title": "Response Time (95th percentile)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "{{job}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
      },
      {
        "id": 4,
        "title": "Agent Workflow Metrics",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(agent_workflow_executions_total[5m])",
            "legendFormat": "Executions/sec"
          },
          {
            "expr": "rate(agent_workflow_failures_total[5m])",
            "legendFormat": "Failures/sec"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
      },
      {
        "id": 5,
        "title": "System Resources",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg by(instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "CPU Usage %"
          },
          {
            "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
            "legendFormat": "Memory Usage %"
          }
        ],
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 16}
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
EOF

echo -e "${YELLOW}Creating Alertmanager configuration...${NC}"

# Alertmanager configuration
cat > "$MONITORING_DIR/alertmanager/alertmanager.yml" << 'EOF'
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@consulting.sa'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://localhost:5001/'
        send_resolved: true

  - name: 'slack'
    slack_configs:
      - api_url: '${SLACK_WEBHOOK_URL}'
        channel: '#alerts'
        title: 'Agentic AI Alert'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']
EOF

echo -e "${YELLOW}Creating Docker Compose monitoring stack...${NC}"

# Docker Compose for monitoring stack
cat > "$MONITORING_DIR/docker-compose.monitoring.yml" << 'EOF'
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: agentic-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./alert_rules.yml:/etc/prometheus/alert_rules.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
      - '--web.enable-admin-api'
    restart: unless-stopped
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    container_name: agentic-grafana
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-admin}
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
    restart: unless-stopped
    networks:
      - monitoring

  alertmanager:
    image: prom/alertmanager:latest
    container_name: agentic-alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro
      - alertmanager_data:/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
      - '--web.external-url=http://localhost:9093'
    restart: unless-stopped
    networks:
      - monitoring

  node-exporter:
    image: prom/node-exporter:latest
    container_name: agentic-node-exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    restart: unless-stopped
    networks:
      - monitoring

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: agentic-cadvisor
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    privileged: true
    devices:
      - /dev/kmsg
    restart: unless-stopped
    networks:
      - monitoring

networks:
  monitoring:
    driver: bridge

volumes:
  prometheus_data:
  grafana_data:
  alertmanager_data:
EOF

echo -e "${YELLOW}Creating monitoring startup script...${NC}"

# Monitoring startup script
cat > "$MONITORING_DIR/start-monitoring.sh" << 'EOF'
#!/bin/bash
set -e

echo "Starting Agentic AI monitoring stack..."

# Set default Grafana password if not provided
export GRAFANA_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-admin}

# Start monitoring services
docker-compose -f docker-compose.monitoring.yml up -d

echo "Monitoring stack started successfully!"
echo ""
echo "Access URLs:"
echo "- Prometheus: http://localhost:9090"
echo "- Grafana: http://localhost:3001 (admin/admin)"
echo "- Alertmanager: http://localhost:9093"
echo ""
echo "Grafana default credentials:"
echo "Username: admin"
echo "Password: $GRAFANA_ADMIN_PASSWORD"
EOF

chmod +x "$MONITORING_DIR/start-monitoring.sh"

echo -e "${YELLOW}Creating monitoring health check script...${NC}"

# Monitoring health check script
cat > "$MONITORING_DIR/check-monitoring.sh" << 'EOF'
#!/bin/bash
set -e

echo "Checking monitoring stack health..."

# Check Prometheus
if curl -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo "✓ Prometheus is healthy"
else
    echo "✗ Prometheus is not responding"
fi

# Check Grafana
if curl -f http://localhost:3001/api/health > /dev/null 2>&1; then
    echo "✓ Grafana is healthy"
else
    echo "✗ Grafana is not responding"
fi

# Check Alertmanager
if curl -f http://localhost:9093/-/healthy > /dev/null 2>&1; then
    echo "✓ Alertmanager is healthy"
else
    echo "✗ Alertmanager is not responding"
fi

# Check Node Exporter
if curl -f http://localhost:9100/metrics > /dev/null 2>&1; then
    echo "✓ Node Exporter is healthy"
else
    echo "✗ Node Exporter is not responding"
fi

echo "Monitoring health check completed"
EOF

chmod +x "$MONITORING_DIR/check-monitoring.sh"

echo -e "${YELLOW}Creating alert webhook server...${NC}"

# Simple alert webhook server
cat > "$MONITORING_DIR/alert-webhook.py" << 'EOF'
#!/usr/bin/env python3
"""Simple webhook server for receiving Prometheus alerts."""

import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/', methods=['POST'])
def webhook():
    """Receive webhook alerts."""
    try:
        data = request.get_json()
        
        for alert in data.get('alerts', []):
            alert_name = alert.get('labels', {}).get('alertname', 'Unknown')
            status = alert.get('status', 'unknown')
            summary = alert.get('annotations', {}).get('summary', 'No summary')
            
            logger.info(f"Alert: {alert_name} - Status: {status} - {summary}")
            
            # Here you could integrate with Slack, email, etc.
            # For now, just log the alert
            
        return jsonify({"status": "ok"})
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
EOF

chmod +x "$MONITORING_DIR/alert-webhook.py"

echo -e "${YELLOW}Creating monitoring integration script...${NC}"

# Script to integrate monitoring with existing application
cat > "scripts/ci/integrate-monitoring.sh" << 'EOF'
#!/bin/bash
set -e

# Integrate monitoring with existing Docker Compose setup

ENVIRONMENT=${1:-staging}
COMPOSE_FILE="docker-compose.${ENVIRONMENT}.yml"

echo "Integrating monitoring with $COMPOSE_FILE..."

# Add monitoring network to existing compose file
if ! grep -q "monitoring:" "$COMPOSE_FILE"; then
    echo "Adding monitoring network to $COMPOSE_FILE..."
    
    # Add monitoring network
    cat >> "$COMPOSE_FILE" << 'EONET'

  # Monitoring network integration
networks:
  monitoring:
    external: true
    name: monitoring_monitoring
EONET

    # Update services to use monitoring network
    sed -i '/networks:/a\      - monitoring' "$COMPOSE_FILE"
fi

echo "Monitoring integration completed!"
echo ""
echo "To start monitoring:"
echo "1. cd monitoring && ./start-monitoring.sh"
echo "2. docker-compose -f $COMPOSE_FILE up -d"
echo ""
echo "Access monitoring at:"
echo "- Grafana: http://localhost:3001"
echo "- Prometheus: http://localhost:9090"
EOF

chmod +x "scripts/ci/integrate-monitoring.sh"

echo -e "${GREEN}✅ Monitoring setup completed!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Start monitoring stack: cd $MONITORING_DIR && ./start-monitoring.sh"
echo "2. Integrate with application: ./scripts/ci/integrate-monitoring.sh $ENVIRONMENT"
echo "3. Access Grafana at http://localhost:3001 (admin/admin)"
echo "4. Configure alert webhooks and notifications"
echo ""
echo -e "${YELLOW}Files created:${NC}"
echo "- $MONITORING_DIR/docker-compose.monitoring.yml"
echo "- $MONITORING_DIR/grafana/dashboards/agentic-dashboard.json"
echo "- $MONITORING_DIR/alertmanager/alertmanager.yml"
echo "- $MONITORING_DIR/start-monitoring.sh"
echo "- $MONITORING_DIR/check-monitoring.sh"
echo "- $MONITORING_DIR/alert-webhook.py"
echo "- scripts/ci/integrate-monitoring.sh"