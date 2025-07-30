import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // In production, fetch real customer session data
    const sessions = [
      {
        id: 'session-1',
        email: 'customer1@example.com',
        status: 'active' as const,
        agent: 'Customer Journey Agent',
        startTime: '2025-07-20T10:30:00Z',
        duration: '15m 32s'
      },
      {
        id: 'session-2',
        email: 'customer2@example.com',
        status: 'waiting' as const,
        agent: 'Support Agent',
        startTime: '2025-07-20T11:15:00Z',
        duration: '3m 45s'
      },
      {
        id: 'session-3',
        email: 'customer3@example.com',
        status: 'completed' as const,
        agent: 'Accountant Agent',
        startTime: '2025-07-20T09:45:00Z',
        duration: '22m 18s'
      }
    ]

    return NextResponse.json(sessions)
  } catch (error) {
    console.error('Error fetching customer sessions:', error)
    return NextResponse.json(
      { error: 'Failed to fetch sessions' },
      { status: 500 }
    )
  }
}