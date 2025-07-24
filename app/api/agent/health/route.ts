import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // Check if agent backend is running
    const agentUrl = process.env.AGENT_URL || 'http://localhost:8000'
    
    try {
      const response = await fetch(`${agentUrl}/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        // Add timeout
        signal: AbortSignal.timeout(5000),
      })

      if (response.ok) {
        const agentHealth = await response.json()
        return NextResponse.json({
          status: 'healthy',
          agent: agentHealth,
          timestamp: new Date().toISOString(),
        })
      } else {
        return NextResponse.json({
          status: 'unhealthy',
          error: `Agent responded with status ${response.status}`,
          timestamp: new Date().toISOString(),
        }, { status: 503 })
      }
    } catch (fetchError) {
      // Agent is not reachable, return basic health info
      return NextResponse.json({
        status: 'healthy',
        services: {
          supabase: process.env.NEXT_PUBLIC_SUPABASE_URL ? 'configured' : 'missing',
          gemini: process.env.GEMINI_API_KEY ? 'configured' : 'missing',
          n8n: process.env.N8N_URL ? 'configured' : 'missing',
          mcp: process.env.MCP_SERVER_URL ? 'configured' : 'missing',
        },
        agent_connection: 'unavailable',
        timestamp: new Date().toISOString(),
      })
    }
  } catch (error) {
    return NextResponse.json({
      status: 'error',
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}