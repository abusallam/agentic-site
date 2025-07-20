import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // In production, fetch real agent data from your database
    const agents = [
      {
        id: 'agent-1',
        name: 'Customer Journey Agent',
        status: 'active' as const,
        conversations: 89,
        lastActivity: '2 minutes ago'
      },
      {
        id: 'agent-2',
        name: 'N8n MCP Agent',
        status: 'active' as const,
        conversations: 45,
        lastActivity: '5 minutes ago'
      },
      {
        id: 'agent-3',
        name: 'Accountant Agent',
        status: 'idle' as const,
        conversations: 23,
        lastActivity: '1 hour ago'
      },
      {
        id: 'agent-4',
        name: 'Support Agent',
        status: 'active' as const,
        conversations: 67,
        lastActivity: '30 seconds ago'
      }
    ]

    return NextResponse.json(agents)
  } catch (error) {
    console.error('Error fetching agents:', error)
    return NextResponse.json(
      { error: 'Failed to fetch agents' },
      { status: 500 }
    )
  }
}