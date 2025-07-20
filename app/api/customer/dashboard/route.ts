import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const email = searchParams.get('email')

    if (!email) {
      return NextResponse.json(
        { error: 'Email parameter required' },
        { status: 400 }
      )
    }

    // In production, fetch real customer data from database
    const customerData = {
      agents: [
        {
          id: 'customer-agent-1',
          name: 'Customer Support Bot',
          type: 'chatbot' as const,
          status: 'active' as const,
          conversations: 156,
          lastActivity: '2 minutes ago',
          performance: 94
        },
        {
          id: 'customer-agent-2',
          name: 'Order Processing Agent',
          type: 'ai_agent' as const,
          status: 'active' as const,
          conversations: 89,
          lastActivity: '1 hour ago',
          performance: 87
        }
      ],
      stats: {
        totalAgents: 2,
        activeConversations: 12,
        totalInteractions: 245,
        satisfaction: 4.6
      }
    }

    return NextResponse.json(customerData)
  } catch (error) {
    console.error('Error fetching customer dashboard data:', error)
    return NextResponse.json(
      { error: 'Failed to fetch customer data' },
      { status: 500 }
    )
  }
}