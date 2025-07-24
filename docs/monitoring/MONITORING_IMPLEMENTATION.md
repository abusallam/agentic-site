# 📊 Agentic Platform - Monitoring Implementation Guide

## Overview

This document describes the comprehensive monitoring and alerting system implemented for the Agentic AI Platform. The system provides real-time monitoring, intelligent alerting, and automated incident response using N8N workflows, Grafana dashboards, and Prometheus metrics.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Monitoring Stack                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │     N8N     │    │   Grafana   │    │ Prometheus  │     │
│  │  Workflows  │    │ Dashboards  │    │   Metrics   │     │
│  │ & Alerting  │    │ & Visualization │ │ Collection  │     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘     │
│         │                  │                  │            │
│         └──────────────────┼──────────────────┘            │
│                            │                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │Alertmanager │    │ Blackbox    │    │ Node        │     │
│  │   Routing   │    │ Exporter    │    │ Exporter    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agentic Platform                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  Frontend   │    │   Backend   │    │    Redis    │     │
│  │  (Next.js)  │    │ (Python ADK)│    │   Cache     │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. N8N Workflow Automation
- **Purpose**: Intelligent alert processing and notification routing
- **Access**: https://n8n.consulting.sa
- **Features**:
  - Multi-channel notifications (Slack, Email, Telegram)
  - Smart alert routing based on severity and category
  - Automated incident response workflows
  - Performance monitoring automation

### 2. Grafana Dashboards
- **Purpose**: Real-time visualization and monitoring dashboards
- **Access**: https://monitoring.consulting.sa
- **Credentials**: admin / agentic-platform-admin-2025
- **Features**:
  - System overview dashboard
  - Application performance metrics
  - Infrastructure monitoring
  - Custom alerting rules

### 3. Prometheus Metrics
- **Purpose**: Metrics collection and storage
- **Access**: https://metrics.consulting.sa (protected)
- **Credentials**: admin / agentic-platform-admin-2025
- **Features**:
  - Application metrics collection
  - System resource monitoring
  - Custom business metrics
  - Alert rule evaluation

### 4. Alertmanager
- **Purpose**: Alert routing and notification management
- **Features**:
  - Intelligent alert grouping
  - Notification deduplication
  - Multi-channel routing
  - Escalation policies

## Deployment

### Prerequisites
- Production Agentic Platform running
- SSH access to VPS (217.79.255.54)
- Environment variables configured

### Quick Deployment
```bash
# Deploy the complete monitoring stack
./scripts/deploy-monitoring.sh
```

### Manual Deployment Steps

1. **Validate Prerequisites**
   ```bash
   # Check VPS connection
   ssh root@217.79.255.54 'docker ps'
   
   # Verify production system
   curl -f https://consulting.sa/api/health
   ```

2. **Deploy Configuration Files**
   ```bash
   # Copy monitoring configurations
   scp -r monitoring/ root@217.79.255.54:/opt/monitoring/
   ```

3. **Start Monitoring Services**
   ```bash
   # On VPS
   cd /opt/monitoring
   docker compose up -d
   ```

4. **Configure Nginx**
   ```bash
   # Enable monitoring sites
   ln -sf /etc/nginx/sites-available/monitoring /etc/nginx/sites-enabled/
   nginx -t && systemctl reload nginx
   ```

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Notification Channels
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
ALERT_EMAIL=admin@consulting.sa
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password

# Monitoring Configuration
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=agentic-platform-admin-2025
N8N_ENCRYPTION_KEY=agentic-platform-encryption-key-2025
```

### Alert Routing Configuration

Alerts are routed based on:
- **Severity**: critical, warning, info
- **Category**: infrastructure, application, security, performance, network, database, monitoring

#### Critical Alerts
- **Channels**: Email + Slack + Telegram
- **Response Time**: Immediate (10s group wait)
- **Escalation**: 1 hour repeat interval

#### Warning Alerts
- **Channels**: Slack
- **Response Time**: 2 minutes group wait
- **Escalation**: 6 hour repeat interval

#### Performance Alerts
- **Channels**: Slack (#performance)
- **Response Time**: 2 minutes group wait
- **Escalation**: 2 hour repeat interval

## Monitoring Metrics

### System Metrics
- **CPU Usage**: Threshold 80% (warning), 95% (critical)
- **Memory Usage**: Threshold 85% (warning), 95% (critical)
- **Disk Usage**: Threshold 85% (warning), 95% (critical)
- **Load Average**: Monitored for system performance

### Application Metrics
- **HTTP Request Rate**: Requests per second
- **Response Time**: P95 latency monitoring
- **Error Rate**: 5xx errors threshold 5%
- **Active Users**: Real-time user count

### Infrastructure Metrics
- **Container Health**: Docker container status
- **Service Uptime**: Service availability monitoring
- **Network Connectivity**: Endpoint health checks
- **SSL Certificate**: Expiration monitoring

### Business Metrics
- **User Engagement**: Active sessions
- **API Usage**: Endpoint utilization
- **Feature Adoption**: Usage analytics
- **Performance KPIs**: Business-specific metrics

## Alert Rules

### Infrastructure Alerts
```yaml
# Instance Down
- alert: InstanceDown
  expr: up == 0
  for: 1m
  severity: critical

# High CPU Usage
- alert: HighCPUUsage
  expr: cpu_usage > 80
  for: 5m
  severity: warning

# Critical CPU Usage
- alert: CriticalCPUUsage
  expr: cpu_usage > 95
  for: 2m
  severity: critical
```

### Application Alerts
```yaml
# High Error Rate
- alert: HighErrorRate
  expr: error_rate > 0.05
  for: 5m
  severity: critical

# High Request Latency
- alert: HighRequestLatency
  expr: p95_latency > 2s
  for: 5m
  severity: warning

# Service Down
- alert: ServiceDown
  expr: service_up == 0
  for: 1m
  severity: critical
```

### Security Alerts
```yaml
# SSL Certificate Expiring
- alert: SSLCertificateExpiring
  expr: ssl_expiry < 7d
  for: 1h
  severity: warning

# SSL Certificate Expired
- alert: SSLCertificateExpired
  expr: ssl_expiry < 0
  for: 1m
  severity: critical
```

## N8N Workflows

### 1. System Alerts Workflow
- **Trigger**: Alertmanager webhooks
- **Function**: Process and route alerts
- **Notifications**: Multi-channel based on severity
- **Features**: Smart routing, deduplication, resolution tracking

### 2. Performance Monitoring Workflow
- **Trigger**: Scheduled every 5 minutes
- **Function**: Health checks and performance monitoring
- **Metrics**: Response time, availability, performance
- **Alerts**: Automated performance issue detection

### 3. Incident Response Workflow
- **Trigger**: Critical alerts
- **Function**: Automated incident response
- **Actions**: Create tickets, notify on-call, escalate
- **Integration**: ServiceNow, PagerDuty, Jira

## Grafana Dashboards

### 1. Platform Overview Dashboard
- **Panels**: Service status, system metrics, performance
- **Refresh**: 30 seconds
- **Features**: Real-time monitoring, drill-down capabilities

### 2. Application Performance Dashboard
- **Panels**: Request rates, latency, errors, throughput
- **Refresh**: 15 seconds
- **Features**: Performance trending, SLA monitoring

### 3. Infrastructure Dashboard
- **Panels**: System resources, container metrics, network
- **Refresh**: 1 minute
- **Features**: Capacity planning, resource optimization

### 4. Business Metrics Dashboard
- **Panels**: User analytics, feature usage, KPIs
- **Refresh**: 5 minutes
- **Features**: Business intelligence, growth tracking

## Maintenance

### Daily Operations
```bash
# Check monitoring system health
ssh root@217.79.255.54 'cd /opt/monitoring && docker compose ps'

# View monitoring logs
ssh root@217.79.255.54 'cd /opt/monitoring && docker compose logs -f'

# Restart monitoring services
ssh root@217.79.255.54 'cd /opt/monitoring && docker compose restart'
```

### Weekly Maintenance
- Review alert noise and tune thresholds
- Update dashboards based on new requirements
- Check disk usage for metrics storage
- Validate backup procedures

### Monthly Maintenance
- Review and update alert rules
- Analyze monitoring performance
- Update monitoring stack versions
- Conduct disaster recovery tests

## Troubleshooting

### Common Issues

#### N8N Not Starting
```bash
# Check logs
docker compose logs n8n

# Common fixes
docker compose restart n8n
docker compose down && docker compose up -d
```

#### Grafana Dashboard Issues
```bash
# Reset Grafana data
docker compose down
docker volume rm monitoring_grafana_data
docker compose up -d
```

#### Prometheus Metrics Missing
```bash
# Check Prometheus config
docker compose exec prometheus promtool check config /etc/prometheus/prometheus.yml

# Reload configuration
curl -X POST http://localhost:9090/-/reload
```

#### Alert Not Firing
```bash
# Check alert rules
curl http://localhost:9090/api/v1/rules

# Check Alertmanager
curl http://localhost:9093/api/v1/alerts
```

### Performance Optimization

#### Prometheus Storage
```bash
# Monitor storage usage
df -h /opt/monitoring/prometheus_data

# Configure retention
--storage.tsdb.retention.time=30d
```

#### Grafana Performance
```bash
# Optimize queries
- Use recording rules for complex queries
- Limit time ranges for heavy dashboards
- Use appropriate refresh intervals
```

## Security

### Access Control
- **Grafana**: Admin authentication required
- **Prometheus**: Basic auth protection
- **N8N**: Webhook authentication
- **Alertmanager**: Internal network only

### Network Security
- **SSL/TLS**: All external access encrypted
- **Firewall**: UFW rules for monitoring ports
- **VPN**: Consider VPN access for sensitive metrics
- **API Keys**: Secure storage of notification tokens

### Data Protection
- **Metrics Retention**: 30-day default retention
- **Log Rotation**: Automated log cleanup
- **Backup**: Regular configuration backups
- **Encryption**: Data encryption at rest

## Integration

### Existing Systems
- **Supabase**: Database metrics integration
- **Redis**: Cache performance monitoring
- **Nginx**: Web server metrics
- **Docker**: Container monitoring

### External Services
- **Slack**: Team notifications
- **Email**: Critical alert notifications
- **Telegram**: Mobile notifications
- **PagerDuty**: Incident management (optional)

### API Integration
```javascript
// Custom metrics endpoint
app.get('/metrics', (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(register.metrics());
});

// Health check with metrics
app.get('/health', (req, res) => {
  const health = {
    status: 'ok',
    timestamp: new Date().toISOString(),
    metrics: {
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      cpu: process.cpuUsage()
    }
  };
  res.json(health);
});
```

## Best Practices

### Alert Management
1. **Meaningful Alerts**: Only alert on actionable issues
2. **Proper Severity**: Use appropriate severity levels
3. **Context**: Include runbook links and context
4. **Deduplication**: Avoid alert storms
5. **Resolution**: Track alert resolution

### Dashboard Design
1. **User-Focused**: Design for the audience
2. **Performance**: Optimize query performance
3. **Clarity**: Clear visualizations and labels
4. **Consistency**: Consistent design patterns
5. **Actionability**: Include links to remediation

### Monitoring Strategy
1. **SLI/SLO**: Define service level indicators
2. **Four Golden Signals**: Latency, traffic, errors, saturation
3. **Business Metrics**: Monitor business KPIs
4. **Proactive**: Predict issues before they occur
5. **Documentation**: Maintain runbooks and procedures

## Support

### Documentation
- **Runbooks**: https://consulting.sa/docs/runbooks/
- **API Reference**: https://consulting.sa/docs/api/
- **Troubleshooting**: https://consulting.sa/docs/troubleshooting/

### Contacts
- **Primary**: admin@consulting.sa
- **Emergency**: Use Slack #alerts channel
- **Escalation**: Follow incident response procedures

### Resources
- **Grafana Docs**: https://grafana.com/docs/
- **Prometheus Docs**: https://prometheus.io/docs/
- **N8N Docs**: https://docs.n8n.io/
- **Alertmanager Docs**: https://prometheus.io/docs/alerting/latest/alertmanager/

---

**Last Updated**: January 2025  
**Version**: 1.0  
**Status**: Production Ready  
**Next Review**: February 2025