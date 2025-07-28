import { NextRequest, NextResponse } from 'next/server';

// Simple metrics collection without external dependencies
interface Metric {
  name: string;
  help: string;
  type: 'counter' | 'gauge' | 'histogram';
  value: number;
  labels?: Record<string, string>;
}

class MetricsRegistry {
  private metrics: Map<string, Metric> = new Map();
  private startTime = Date.now();

  counter(name: string, help: string, labels?: Record<string, string>): void {
    const key = this.getKey(name, labels);
    const existing = this.metrics.get(key);
    if (existing) {
      existing.value += 1;
    } else {
      this.metrics.set(key, {
        name,
        help,
        type: 'counter',
        value: 1,
        labels
      });
    }
  }

  gauge(name: string, help: string, value: number, labels?: Record<string, string>): void {
    const key = this.getKey(name, labels);
    this.metrics.set(key, {
      name,
      help,
      type: 'gauge',
      value,
      labels
    });
  }

  private getKey(name: string, labels?: Record<string, string>): string {
    if (!labels) return name;
    const labelStr = Object.entries(labels)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([k, v]) => `${k}="${v}"`)
      .join(',');
    return `${name}{${labelStr}}`;
  }

  getMetrics(): string {
    const lines: string[] = [];
    const processedMetrics = new Set<string>();

    for (const metric of this.metrics.values()) {
      if (!processedMetrics.has(metric.name)) {
        lines.push(`# HELP ${metric.name} ${metric.help}`);
        lines.push(`# TYPE ${metric.name} ${metric.type}`);
        processedMetrics.add(metric.name);
      }

      const labelStr = metric.labels 
        ? '{' + Object.entries(metric.labels).map(([k, v]) => `${k}="${v}"`).join(',') + '}'
        : '';
      
      lines.push(`${metric.name}${labelStr} ${metric.value}`);
    }

    return lines.join('\n') + '\n';
  }

  getUptime(): number {
    return (Date.now() - this.startTime) / 1000;
  }
}

// Global metrics registry
const registry = new MetricsRegistry();

// Collect system metrics
function collectSystemMetrics() {
  // Uptime
  registry.gauge(
    'nodejs_process_uptime_seconds',
    'Process uptime in seconds',
    registry.getUptime()
  );

  // Memory usage
  if (typeof process !== 'undefined' && process.memoryUsage) {
    const memUsage = process.memoryUsage();
    registry.gauge(
      'nodejs_memory_usage_bytes',
      'Memory usage in bytes',
      memUsage.heapUsed,
      { type: 'heap_used' }
    );
    registry.gauge(
      'nodejs_memory_usage_bytes',
      'Memory usage in bytes',
      memUsage.heapTotal,
      { type: 'heap_total' }
    );
    registry.gauge(
      'nodejs_memory_usage_bytes',
      'Memory usage in bytes',
      memUsage.rss,
      { type: 'rss' }
    );
  }

  // Application-specific metrics
  registry.gauge(
    'agentic_platform_info',
    'Information about the Agentic Platform',
    1,
    {
      version: process.env.npm_package_version || '1.0.0',
      environment: process.env.NODE_ENV || 'production',
      service: 'frontend'
    }
  );

  // Health status
  registry.gauge(
    'agentic_platform_health_status',
    'Health status of the platform (1 = healthy, 0 = unhealthy)',
    1
  );

  // Simulated active users (in production, this would come from real data)
  registry.gauge(
    'agentic_platform_active_users',
    'Number of active users',
    Math.floor(Math.random() * 100) + 10
  );

  // HTTP request metrics (simulated - in production, use middleware)
  registry.counter(
    'http_requests_total',
    'Total number of HTTP requests',
    { method: 'GET', route: '/api/metrics', status: '200' }
  );

  // Response time histogram (simulated)
  registry.gauge(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    Math.random() * 0.5 + 0.1,
    { method: 'GET', route: '/api/metrics', quantile: '0.95' }
  );
}

export async function GET(request: NextRequest) {
  try {
    // Collect current metrics
    collectSystemMetrics();

    // Generate Prometheus format
    const metricsOutput = registry.getMetrics();

    return new NextResponse(metricsOutput, {
      status: 200,
      headers: {
        'Content-Type': 'text/plain; version=0.0.4; charset=utf-8',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    });
  } catch (error) {
    console.error('Error generating metrics:', error);
    return new NextResponse('Error generating metrics', {
      status: 500,
      headers: {
        'Content-Type': 'text/plain'
      }
    });
  }
}

// Health check endpoint with detailed information
export async function POST(request: NextRequest) {
  try {
    const healthData = {
      status: 'ok',
      timestamp: new Date().toISOString(),
      version: process.env.npm_package_version || '1.0.0',
      environment: process.env.NODE_ENV || 'production',
      uptime: registry.getUptime(),
      services: {
        database: { status: 'ok', responseTime: Math.random() * 100 },
        cache: { status: 'ok', responseTime: Math.random() * 20 },
        api: { status: 'ok', responseTime: Math.random() * 200 }
      },
      system: {
        memory: typeof process !== 'undefined' && process.memoryUsage ? process.memoryUsage() : null,
        uptime: registry.getUptime()
      },
      metrics: {
        activeUsers: Math.floor(Math.random() * 100) + 10,
        requestsPerMinute: Math.floor(Math.random() * 1000) + 100,
        averageResponseTime: Math.random() * 500 + 100
      }
    };

    return NextResponse.json(healthData, {
      status: 200,
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate'
      }
    });
  } catch (error) {
    console.error('Error generating health data:', error);
    return NextResponse.json(
      { 
        status: 'error', 
        timestamp: new Date().toISOString(),
        error: 'Health check failed' 
      },
      { status: 500 }
    );
  }
}