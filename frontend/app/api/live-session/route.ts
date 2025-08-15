import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const { user_id, agent_type, session_type } = await request.json()

    if (!user_id || !agent_type) {
      return NextResponse.json(
        { error: 'Missing required parameters' },
        { status: 400 }
      )
    }

    // Generate session ID
    const sessionId = `live_${agent_type}_${user_id}_${Date.now()}`
    
    // In production, you would integrate with LiveKit or similar service
    // For now, we'll simulate the session creation
    const mockSessionData = {
      session_id: sessionId,
      join_url: `https://meet.consulting.sa/room/${sessionId}`,
      agent_type: agent_type,
      session_type: session_type || 'video_consultation',
      status: 'created',
      created_at: new Date().toISOString(),
      expires_at: new Date(Date.now() + 60 * 60 * 1000).toISOString(), // 1 hour
      participant_token: generateParticipantToken(user_id, sessionId),
      room_config: {
        max_participants: agent_type === 'consulting' ? 2 : 5,
        recording_enabled: true,
        screen_share_enabled: true,
        chat_enabled: true
      }
    }

    // Store session data (in production, use database)
    // For now, we'll just return the session info
    
    return NextResponse.json({
      success: true,
      ...mockSessionData
    })

  } catch (error) {
    console.error('Live session creation error:', error)
    return NextResponse.json(
      { error: 'Failed to create live session' },
      { status: 500 }
    )
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const sessionId = searchParams.get('session_id')

    if (!sessionId) {
      return NextResponse.json(
        { error: 'Session ID required' },
        { status: 400 }
      )
    }

    // In production, fetch from database
    const mockSessionStatus = {
      session_id: sessionId,
      status: 'active',
      participants: [
        {
          id: 'user_123',
          name: 'Customer',
          role: 'customer',
          joined_at: new Date().toISOString()
        },
        {
          id: 'agent_456',
          name: 'AI Consultant',
          role: 'agent',
          joined_at: new Date().toISOString()
        }
      ],
      duration: Math.floor(Math.random() * 1800), // Random duration up to 30 minutes
      recording_url: `https://recordings.consulting.sa/${sessionId}.mp4`
    }

    return NextResponse.json({
      success: true,
      session: mockSessionStatus
    })

  } catch (error) {
    console.error('Live session status error:', error)
    return NextResponse.json(
      { error: 'Failed to get session status' },
      { status: 500 }
    )
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const sessionId = searchParams.get('session_id')

    if (!sessionId) {
      return NextResponse.json(
        { error: 'Session ID required' },
        { status: 400 }
      )
    }

    // In production, end the LiveKit session and cleanup
    
    return NextResponse.json({
      success: true,
      message: 'Session ended successfully',
      session_id: sessionId,
      ended_at: new Date().toISOString()
    })

  } catch (error) {
    console.error('Live session end error:', error)
    return NextResponse.json(
      { error: 'Failed to end session' },
      { status: 500 }
    )
  }
}

function generateParticipantToken(userId: string, sessionId: string): string {
  // In production, generate proper JWT token for LiveKit
  const tokenData = {
    user_id: userId,
    session_id: sessionId,
    permissions: ['join', 'publish', 'subscribe'],
    expires_at: Date.now() + 60 * 60 * 1000 // 1 hour
  }
  
  // Simple base64 encoding for demo (use proper JWT in production)
  return Buffer.from(JSON.stringify(tokenData)).toString('base64')
}