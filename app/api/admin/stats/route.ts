import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // In production, fetch real data from your database
    const stats = {
      totalCustomers: 127,
      activeAgents: 8,
      totalConversations: 1456,
      systemHealth: 'healthy' as const
    }

    return NextResponse.json(stats)
  } catch (error) {
    console.error('Error fetching admin stats:', error)
    return NextResponse.json(
      { error: 'Failed to fetch stats' },
      { status: 500 }
    )
  }
}