import { NextResponse } from 'next/server'

export async function GET() {
  const healthData = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'ai-saas-platform',
    version: '2.0.0',
    environment: process.env.NODE_ENV || 'development',
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    services: {
      frontend: {
        status: 'healthy',
        port: process.env.PORT || 3000
      },
      backend: {
        status: 'checking',
        port: process.env.BACKEND_PORT || 8080
      }
    }
  }

  // Check backend health if available
  try {
    const backendPort = process.env.BACKEND_PORT || 8080
    const backendResponse = await fetch(`http://localhost:${backendPort}/api/health`, {
      signal: AbortSignal.timeout(5000)
    })
    
    if (backendResponse.ok) {
      healthData.services.backend.status = 'healthy'
    } else {
      healthData.services.backend.status = 'unhealthy'
    }
  } catch (error) {
    healthData.services.backend.status = 'unavailable'
  }

  // Determine overall status
  const allServicesHealthy = Object.values(healthData.services).every(
    service => service.status === 'healthy'
  )
  
  if (!allServicesHealthy) {
    healthData.status = 'degraded'
  }

  return NextResponse.json(healthData, {
    status: healthData.status === 'healthy' ? 200 : 503,
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    }
  })
}